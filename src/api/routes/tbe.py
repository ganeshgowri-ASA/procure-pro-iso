"""TBE (Technical Bid Evaluation) API endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_async_session
from src.models.tbe import (
    DefaultCriteriaWeights,
    EvaluationCriteria,
    EvaluationCriteriaCreate,
    EvaluationStatus,
    ISOStandard,
    TBEEvaluation,
    TBEEvaluationCreate,
    TBEResult,
    VendorBid,
    VendorBidCreate,
    CriteriaCategory,
)
from src.models.vendor import Vendor
from src.services.tbe_scoring import create_scoring_engine
from src.services.comparison_matrix import ComparisonMatrixEngine
from src.services.ranking_engine import RankingEngine
from src.services.tco_calculator import TCOCalculator
from src.services.compliance_scorer import ComplianceScorer
from src.repositories.tbe_repository import TBERepository
from src.repositories.vendor_repository import VendorRepository

router = APIRouter()


# In-memory cache for evaluation results (not persisted fully to DB yet)
evaluation_results_cache: dict[str, TBEEvaluation] = {}


def db_bid_to_model(bid_db) -> VendorBid:
    """Convert database bid to Pydantic model."""
    return VendorBid(
        id=UUID(bid_db.id),
        vendor_id=UUID(bid_db.vendor_id),
        evaluation_id=UUID(bid_db.evaluation_id) if bid_db.evaluation_id else None,
        bid_reference=bid_db.bid_reference,
        unit_price=bid_db.unit_price,
        quantity=bid_db.quantity,
        total_price=bid_db.total_price,
        currency=bid_db.currency,
        shipping_cost=bid_db.shipping_cost or 0.0,
        installation_cost=bid_db.installation_cost or 0.0,
        training_cost=bid_db.training_cost or 0.0,
        maintenance_cost_annual=bid_db.maintenance_cost_annual or 0.0,
        warranty_years=bid_db.warranty_years or 1,
        expected_lifespan_years=bid_db.expected_lifespan_years or 5,
        delivery_days=bid_db.delivery_days,
        delivery_terms=bid_db.delivery_terms,
        technical_specs=bid_db.technical_specs or {},
        certifications=bid_db.certifications or [],
        iso_compliance=bid_db.iso_compliance or [],
        quality_score=bid_db.quality_score or 0.0,
        past_performance_score=bid_db.past_performance_score or 0.0,
        submitted_at=bid_db.submitted_at,
        created_at=bid_db.created_at,
        updated_at=bid_db.updated_at,
    )


def db_criteria_to_model(criteria_db) -> EvaluationCriteria:
    """Convert database criteria to Pydantic model."""
    return EvaluationCriteria(
        id=UUID(criteria_db.id),
        name=criteria_db.name,
        code=criteria_db.code,
        category=CriteriaCategory(criteria_db.category),
        description=criteria_db.description,
        weight=criteria_db.weight,
        max_score=criteria_db.max_score,
        is_mandatory=criteria_db.is_mandatory,
        scoring_guidance=criteria_db.scoring_guidance or {},
    )


def db_eval_to_model(eval_db) -> TBEEvaluation:
    """Convert database evaluation to Pydantic model."""
    weights = eval_db.criteria_weights or {}
    criteria_weights = DefaultCriteriaWeights(
        price=weights.get("price", 0.40),
        quality=weights.get("quality", 0.25),
        delivery=weights.get("delivery", 0.20),
        compliance=weights.get("compliance", 0.15),
    )

    iso_standards = []
    for std in (eval_db.required_iso_standards or []):
        try:
            iso_standards.append(ISOStandard(std))
        except ValueError:
            pass

    return TBEEvaluation(
        id=UUID(eval_db.id),
        name=eval_db.name,
        description=eval_db.description,
        project_reference=eval_db.project_reference,
        status=EvaluationStatus(eval_db.status) if eval_db.status else EvaluationStatus.DRAFT,
        criteria_weights=criteria_weights,
        required_iso_standards=iso_standards,
        required_certifications=eval_db.required_certifications or [],
        evaluated_by=eval_db.evaluated_by,
        evaluated_at=eval_db.evaluated_at,
        created_at=eval_db.created_at,
        updated_at=eval_db.updated_at,
    )


def db_vendor_to_model(vendor_db) -> Vendor:
    """Convert database vendor to Pydantic model."""
    return Vendor(
        id=UUID(vendor_db.id),
        name=vendor_db.name,
        code=vendor_db.code,
        email=vendor_db.email,
        phone=vendor_db.phone,
        address=vendor_db.address,
        country=vendor_db.country,
        industry=vendor_db.industry,
        status=vendor_db.status,
        certifications=vendor_db.certifications or [],
        iso_standards=vendor_db.iso_standards or [],
        quality_rating=vendor_db.quality_rating or 0.0,
        delivery_rating=vendor_db.delivery_rating or 0.0,
        price_competitiveness=vendor_db.price_competitiveness or 0.0,
        created_at=vendor_db.created_at,
        updated_at=vendor_db.updated_at,
    )


# ============================================================================
# Evaluation Criteria Endpoints
# ============================================================================


@router.get("/criteria", response_model=list[EvaluationCriteria])
async def list_criteria(
    session: AsyncSession = Depends(get_async_session),
) -> list[EvaluationCriteria]:
    """List all evaluation criteria."""
    repo = TBERepository(session)
    criteria_list = await repo.get_all_criteria()
    return [db_criteria_to_model(c) for c in criteria_list]


@router.post("/criteria", response_model=EvaluationCriteria, status_code=201)
async def create_criteria(
    criteria_data: EvaluationCriteriaCreate,
    session: AsyncSession = Depends(get_async_session),
) -> EvaluationCriteria:
    """
    Create a new evaluation criteria.

    Custom criteria allow extending the standard evaluation framework with
    organization-specific requirements.
    """
    repo = TBERepository(session)

    # Check for duplicate code
    existing = await repo.get_criteria_by_code(criteria_data.code)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Criteria with code '{criteria_data.code}' already exists"
        )

    criteria = await repo.create_criteria(criteria_data)
    return db_criteria_to_model(criteria)


@router.get("/criteria/{criteria_id}", response_model=EvaluationCriteria)
async def get_criteria(
    criteria_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> EvaluationCriteria:
    """Get a specific evaluation criteria."""
    repo = TBERepository(session)
    criteria = await repo.get_criteria_by_id(str(criteria_id))
    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return db_criteria_to_model(criteria)


@router.delete("/criteria/{criteria_id}", status_code=204)
async def delete_criteria(
    criteria_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Delete an evaluation criteria."""
    repo = TBERepository(session)
    deleted = await repo.delete_criteria(str(criteria_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Criteria not found")


# ============================================================================
# Vendor Bid Endpoints
# ============================================================================


@router.get("/bids", response_model=list[VendorBid])
async def list_bids(
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor"),
    evaluation_id: Optional[UUID] = Query(None, description="Filter by evaluation"),
    session: AsyncSession = Depends(get_async_session),
) -> list[VendorBid]:
    """List all vendor bids with optional filtering."""
    repo = TBERepository(session)
    bids = await repo.get_all_bids(
        vendor_id=str(vendor_id) if vendor_id else None,
        evaluation_id=str(evaluation_id) if evaluation_id else None,
    )
    return [db_bid_to_model(b) for b in bids]


@router.post("/bids", response_model=VendorBid, status_code=201)
async def create_bid(
    bid_data: VendorBidCreate,
    session: AsyncSession = Depends(get_async_session),
) -> VendorBid:
    """
    Submit a vendor bid for evaluation.

    Include:
    - Pricing details (unit price, quantity, additional costs)
    - Delivery information
    - Technical specifications
    - Certifications and ISO compliance
    """
    # Verify vendor exists
    vendor_repo = VendorRepository(session)
    vendor = await vendor_repo.get_by_id(str(bid_data.vendor_id))
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    tbe_repo = TBERepository(session)
    bid = await tbe_repo.create_bid(bid_data)
    return db_bid_to_model(bid)


@router.get("/bids/{bid_id}", response_model=VendorBid)
async def get_bid(
    bid_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> VendorBid:
    """Get a specific vendor bid."""
    repo = TBERepository(session)
    bid = await repo.get_bid_by_id(str(bid_id))
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    return db_bid_to_model(bid)


@router.delete("/bids/{bid_id}", status_code=204)
async def delete_bid(
    bid_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a vendor bid."""
    repo = TBERepository(session)
    deleted = await repo.delete_bid(str(bid_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Bid not found")


# ============================================================================
# TBE Evaluation Endpoints
# ============================================================================


@router.get("/evaluations", response_model=list[TBEEvaluation])
async def list_evaluations(
    status: Optional[EvaluationStatus] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_async_session),
) -> list[TBEEvaluation]:
    """List all TBE evaluations."""
    repo = TBERepository(session)
    evaluations = await repo.get_all_evaluations(status=status)
    result = []
    for e in evaluations:
        eval_model = db_eval_to_model(e)
        # Attach cached results if available
        if e.id in evaluation_results_cache:
            cached = evaluation_results_cache[e.id]
            eval_model.results = cached.results
            eval_model.ranking = cached.ranking
            eval_model.comparison_matrix = cached.comparison_matrix
        result.append(eval_model)
    return result


@router.post("/evaluations", response_model=TBEEvaluation, status_code=201)
async def create_evaluation(
    evaluation_data: TBEEvaluationCreate,
    session: AsyncSession = Depends(get_async_session),
) -> TBEEvaluation:
    """
    Create a new TBE evaluation.

    Configure:
    - Criteria weights (price, quality, delivery, compliance)
    - Required ISO standards
    - Required certifications
    """
    repo = TBERepository(session)
    evaluation = await repo.create_evaluation(evaluation_data)
    return db_eval_to_model(evaluation)


@router.get("/evaluations/{evaluation_id}", response_model=TBEEvaluation)
async def get_evaluation(
    evaluation_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> TBEEvaluation:
    """Get a specific TBE evaluation."""
    repo = TBERepository(session)
    evaluation = await repo.get_evaluation_by_id(str(evaluation_id))
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    eval_model = db_eval_to_model(evaluation)

    # Attach cached results if available
    if str(evaluation_id) in evaluation_results_cache:
        cached = evaluation_results_cache[str(evaluation_id)]
        eval_model.results = cached.results
        eval_model.ranking = cached.ranking
        eval_model.comparison_matrix = cached.comparison_matrix
        eval_model.recommended_vendor_id = cached.recommended_vendor_id

    return eval_model


@router.post("/evaluations/{evaluation_id}/bids/{bid_id}")
async def add_bid_to_evaluation(
    evaluation_id: UUID,
    bid_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Add a vendor bid to an evaluation."""
    repo = TBERepository(session)

    evaluation = await repo.get_evaluation_by_id(str(evaluation_id))
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    bid = await repo.add_bid_to_evaluation(str(bid_id), str(evaluation_id))
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    return {"message": f"Bid {bid_id} added to evaluation {evaluation_id}"}


@router.post("/evaluations/{evaluation_id}/execute", response_model=TBEEvaluation)
async def execute_evaluation(
    evaluation_id: UUID,
    evaluated_by: Optional[str] = Query(None, description="Evaluator name"),
    session: AsyncSession = Depends(get_async_session),
) -> TBEEvaluation:
    """
    Execute TBE evaluation for all associated bids.

    This will:
    1. Score all vendor bids using weighted criteria
    2. Calculate TCO for each vendor
    3. Check compliance with ISO standards
    4. Rank vendors and generate recommendations
    5. Create comparison matrix
    """
    tbe_repo = TBERepository(session)
    vendor_repo = VendorRepository(session)

    evaluation_db = await tbe_repo.get_evaluation_by_id(str(evaluation_id))
    if not evaluation_db:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    evaluation = db_eval_to_model(evaluation_db)

    # Get bids for this evaluation
    bids_db = await tbe_repo.get_bids_by_evaluation(str(evaluation_id))
    if not bids_db:
        raise HTTPException(status_code=400, detail="No bids associated with this evaluation")

    eval_bids = [db_bid_to_model(b) for b in bids_db]

    # Get vendors
    vendors_db = await vendor_repo.get_vendors_dict()
    vendors = {UUID(k): db_vendor_to_model(v) for k, v in vendors_db.items()}

    # Initialize scoring engine with evaluation weights
    weights = evaluation.criteria_weights
    scoring_engine = create_scoring_engine(
        price_weight=weights.price,
        quality_weight=weights.quality,
        delivery_weight=weights.delivery,
        compliance_weight=weights.compliance,
    )

    # Score all bids
    required_standards = [std.value for std in evaluation.required_iso_standards]
    results = scoring_engine.evaluate_all_bids(
        bids=eval_bids,
        vendors=vendors,
        required_standards=required_standards,
        required_certs=evaluation.required_certifications,
    )

    # Calculate TCO
    tco_calculator = TCOCalculator()
    tco_calculations = tco_calculator.calculate_all_tco(eval_bids, vendors)

    # Check compliance
    compliance_scorer = ComplianceScorer()
    compliance_checks = compliance_scorer.check_all_vendors(
        bids=eval_bids,
        vendors=vendors,
        required_standards=evaluation.required_iso_standards,
        required_certifications=evaluation.required_certifications,
    )

    # Attach TCO and compliance to results
    tco_map = {t.vendor_id: t for t in tco_calculations}
    compliance_map = {c.vendor_id: c for c in compliance_checks}

    for result in results:
        result.tco_calculation = tco_map.get(result.vendor_id)
        result.compliance_check = compliance_map.get(result.vendor_id)

    # Rank vendors
    ranking_engine = RankingEngine()
    ranked_results = ranking_engine.rank_vendors(
        results=results,
        tco_calculations=tco_calculations,
        compliance_checks=compliance_checks,
    )

    # Generate comparison matrix
    matrix_engine = ComparisonMatrixEngine()
    comparison_matrix = matrix_engine.generate_matrix(
        evaluation_id=evaluation_id,
        evaluation_name=evaluation.name,
        results=ranked_results,
    )

    # Update evaluation
    evaluation.status = EvaluationStatus.COMPLETED
    evaluation.results = ranked_results
    evaluation.ranking = [r.vendor_id for r in ranked_results]
    evaluation.comparison_matrix = comparison_matrix
    evaluation.evaluated_by = evaluated_by
    evaluation.evaluated_at = datetime.utcnow()

    if ranked_results:
        evaluation.recommended_vendor_id = ranked_results[0].vendor_id

    # Update database
    results_dict = [r.model_dump(mode="json") for r in ranked_results]
    ranking_list = [str(r.vendor_id) for r in ranked_results]
    await tbe_repo.update_evaluation_results(
        evaluation_id=str(evaluation_id),
        status=EvaluationStatus.COMPLETED,
        results=results_dict,
        ranking=ranking_list,
        recommended_vendor_id=str(evaluation.recommended_vendor_id) if evaluation.recommended_vendor_id else None,
        evaluated_by=evaluated_by,
    )

    # Cache results
    evaluation_results_cache[str(evaluation_id)] = evaluation

    return evaluation


@router.get("/evaluations/{evaluation_id}/results", response_model=list[TBEResult])
async def get_evaluation_results(
    evaluation_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> list[TBEResult]:
    """Get scored results for an evaluation."""
    if str(evaluation_id) not in evaluation_results_cache:
        repo = TBERepository(session)
        evaluation = await repo.get_evaluation_by_id(str(evaluation_id))
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        if evaluation.status != EvaluationStatus.COMPLETED.value:
            raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")
        raise HTTPException(status_code=400, detail="Evaluation results not in cache. Please re-execute.")

    return evaluation_results_cache[str(evaluation_id)].results


@router.get("/evaluations/{evaluation_id}/matrix", response_model=dict)
async def get_comparison_matrix(
    evaluation_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Get comparison matrix for an evaluation."""
    if str(evaluation_id) not in evaluation_results_cache:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet or not in cache")

    evaluation = evaluation_results_cache[str(evaluation_id)]
    if not evaluation.comparison_matrix:
        raise HTTPException(status_code=400, detail="Comparison matrix not available")

    matrix_engine = ComparisonMatrixEngine()
    return matrix_engine.matrix_to_dict(evaluation.comparison_matrix)


@router.get("/evaluations/{evaluation_id}/ranking", response_model=dict)
async def get_ranking_summary(
    evaluation_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Get ranking summary for an evaluation."""
    if str(evaluation_id) not in evaluation_results_cache:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet or not in cache")

    evaluation = evaluation_results_cache[str(evaluation_id)]
    ranking_engine = RankingEngine()
    return ranking_engine.generate_ranking_summary(evaluation.results)


@router.get("/evaluations/{evaluation_id}/tco", response_model=dict)
async def get_tco_analysis(
    evaluation_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Get TCO analysis for an evaluation."""
    if str(evaluation_id) not in evaluation_results_cache:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet or not in cache")

    evaluation = evaluation_results_cache[str(evaluation_id)]
    tco_calculations = [
        r.tco_calculation for r in evaluation.results if r.tco_calculation
    ]

    if not tco_calculations:
        raise HTTPException(status_code=400, detail="No TCO data available")

    tco_calculator = TCOCalculator()
    return tco_calculator.get_tco_summary(tco_calculations)


@router.get("/evaluations/{evaluation_id}/compliance", response_model=dict)
async def get_compliance_summary(
    evaluation_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Get compliance summary for an evaluation."""
    if str(evaluation_id) not in evaluation_results_cache:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet or not in cache")

    evaluation = evaluation_results_cache[str(evaluation_id)]
    compliance_checks = [
        r.compliance_check for r in evaluation.results if r.compliance_check
    ]

    if not compliance_checks:
        raise HTTPException(status_code=400, detail="No compliance data available")

    compliance_scorer = ComplianceScorer()
    return compliance_scorer.get_compliance_summary(compliance_checks)


# ============================================================================
# Utility Endpoints
# ============================================================================


@router.get("/iso-standards", response_model=list[dict])
async def list_iso_standards() -> list[dict]:
    """List all supported ISO standards."""
    return [
        {"code": std.name, "name": std.value, "description": _get_iso_description(std)}
        for std in ISOStandard
    ]


@router.post("/calculate-score", response_model=dict)
async def calculate_score_preview(
    weights: DefaultCriteriaWeights = Body(...),
    price_score: float = Body(..., ge=0, le=100),
    quality_score: float = Body(..., ge=0, le=100),
    delivery_score: float = Body(..., ge=0, le=100),
    compliance_score: float = Body(..., ge=0, le=100),
) -> dict:
    """
    Preview weighted score calculation without creating an evaluation.

    Useful for testing weight configurations before running full evaluations.
    """
    if not weights.is_valid():
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to 1.0, got {weights.total_weight():.4f}",
        )

    weighted_price = price_score * weights.price
    weighted_quality = quality_score * weights.quality
    weighted_delivery = delivery_score * weights.delivery
    weighted_compliance = compliance_score * weights.compliance

    total = weighted_price + weighted_quality + weighted_delivery + weighted_compliance

    return {
        "input_scores": {
            "price": price_score,
            "quality": quality_score,
            "delivery": delivery_score,
            "compliance": compliance_score,
        },
        "weights": {
            "price": weights.price,
            "quality": weights.quality,
            "delivery": weights.delivery,
            "compliance": weights.compliance,
        },
        "weighted_scores": {
            "price": round(weighted_price, 2),
            "quality": round(weighted_quality, 2),
            "delivery": round(weighted_delivery, 2),
            "compliance": round(weighted_compliance, 2),
        },
        "total_weighted_score": round(total, 2),
        "max_possible": 100.0,
        "percentage": round(total, 2),
    }


def _get_iso_description(standard: ISOStandard) -> str:
    """Get description for ISO standard."""
    descriptions = {
        ISOStandard.ISO_9001: "Quality Management Systems",
        ISOStandard.ISO_14001: "Environmental Management Systems",
        ISOStandard.ISO_17025: "Testing and Calibration Laboratories",
        ISOStandard.ISO_27001: "Information Security Management",
        ISOStandard.ISO_45001: "Occupational Health and Safety",
        ISOStandard.IATF_16949: "Automotive Quality Management",
        ISOStandard.ISO_13485: "Medical Devices Quality Management",
        ISOStandard.ISO_22000: "Food Safety Management",
        ISOStandard.AS_9100: "Aerospace Quality Management",
    }
    return descriptions.get(standard, "")


# Utility functions for other modules
def get_evaluation_from_cache(evaluation_id: str) -> Optional[TBEEvaluation]:
    """Get evaluation from cache."""
    return evaluation_results_cache.get(evaluation_id)
