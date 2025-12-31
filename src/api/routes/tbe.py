"""TBE (Technical Bid Evaluation) API endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, Body

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
    ComparisonMatrix,
    TCOCalculation,
    ComplianceCheck,
)
from src.services.tbe_scoring import TBEScoringEngine, create_scoring_engine
from src.services.comparison_matrix import ComparisonMatrixEngine
from src.services.ranking_engine import RankingEngine
from src.services.tco_calculator import TCOCalculator
from src.services.compliance_scorer import ComplianceScorer
from src.api.routes.vendors import get_vendors_dict

router = APIRouter()

# In-memory storage for demo
evaluations_db: dict[UUID, TBEEvaluation] = {}
bids_db: dict[UUID, VendorBid] = {}
criteria_db: dict[UUID, EvaluationCriteria] = {}


# ============================================================================
# Evaluation Criteria Endpoints
# ============================================================================


@router.get("/criteria", response_model=list[EvaluationCriteria])
async def list_criteria() -> list[EvaluationCriteria]:
    """List all evaluation criteria."""
    return list(criteria_db.values())


@router.post("/criteria", response_model=EvaluationCriteria, status_code=201)
async def create_criteria(criteria_data: EvaluationCriteriaCreate) -> EvaluationCriteria:
    """
    Create a new evaluation criteria.

    Custom criteria allow extending the standard evaluation framework with
    organization-specific requirements.
    """
    # Check for duplicate code
    existing = next((c for c in criteria_db.values() if c.code == criteria_data.code), None)
    if existing:
        raise HTTPException(status_code=400, detail=f"Criteria with code '{criteria_data.code}' already exists")

    criteria = EvaluationCriteria(
        id=uuid4(),
        **criteria_data.model_dump(),
    )
    criteria_db[criteria.id] = criteria

    return criteria


@router.get("/criteria/{criteria_id}", response_model=EvaluationCriteria)
async def get_criteria(criteria_id: UUID) -> EvaluationCriteria:
    """Get a specific evaluation criteria."""
    criteria = criteria_db.get(criteria_id)
    if not criteria:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return criteria


@router.delete("/criteria/{criteria_id}", status_code=204)
async def delete_criteria(criteria_id: UUID):
    """Delete an evaluation criteria."""
    if criteria_id not in criteria_db:
        raise HTTPException(status_code=404, detail="Criteria not found")
    del criteria_db[criteria_id]


# ============================================================================
# Vendor Bid Endpoints
# ============================================================================


@router.get("/bids", response_model=list[VendorBid])
async def list_bids(
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor"),
    evaluation_id: Optional[UUID] = Query(None, description="Filter by evaluation"),
) -> list[VendorBid]:
    """List all vendor bids with optional filtering."""
    bids = list(bids_db.values())

    if vendor_id:
        bids = [b for b in bids if b.vendor_id == vendor_id]

    if evaluation_id:
        bids = [b for b in bids if b.evaluation_id == evaluation_id]

    return bids


@router.post("/bids", response_model=VendorBid, status_code=201)
async def create_bid(bid_data: VendorBidCreate) -> VendorBid:
    """
    Submit a vendor bid for evaluation.

    Include:
    - Pricing details (unit price, quantity, additional costs)
    - Delivery information
    - Technical specifications
    - Certifications and ISO compliance
    """
    # Verify vendor exists
    vendors = get_vendors_dict()
    if bid_data.vendor_id not in vendors:
        raise HTTPException(status_code=404, detail="Vendor not found")

    bid = VendorBid(
        id=uuid4(),
        total_price=bid_data.unit_price * bid_data.quantity,
        **bid_data.model_dump(),
    )
    bids_db[bid.id] = bid

    return bid


@router.get("/bids/{bid_id}", response_model=VendorBid)
async def get_bid(bid_id: UUID) -> VendorBid:
    """Get a specific vendor bid."""
    bid = bids_db.get(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    return bid


@router.delete("/bids/{bid_id}", status_code=204)
async def delete_bid(bid_id: UUID):
    """Delete a vendor bid."""
    if bid_id not in bids_db:
        raise HTTPException(status_code=404, detail="Bid not found")
    del bids_db[bid_id]


# ============================================================================
# TBE Evaluation Endpoints
# ============================================================================


@router.get("/evaluations", response_model=list[TBEEvaluation])
async def list_evaluations(
    status: Optional[EvaluationStatus] = Query(None, description="Filter by status"),
) -> list[TBEEvaluation]:
    """List all TBE evaluations."""
    evaluations = list(evaluations_db.values())

    if status:
        evaluations = [e for e in evaluations if e.status == status]

    return evaluations


@router.post("/evaluations", response_model=TBEEvaluation, status_code=201)
async def create_evaluation(evaluation_data: TBEEvaluationCreate) -> TBEEvaluation:
    """
    Create a new TBE evaluation.

    Configure:
    - Criteria weights (price, quality, delivery, compliance)
    - Required ISO standards
    - Required certifications
    """
    evaluation = TBEEvaluation(
        id=uuid4(),
        **evaluation_data.model_dump(),
    )
    evaluations_db[evaluation.id] = evaluation

    return evaluation


@router.get("/evaluations/{evaluation_id}", response_model=TBEEvaluation)
async def get_evaluation(evaluation_id: UUID) -> TBEEvaluation:
    """Get a specific TBE evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@router.post("/evaluations/{evaluation_id}/bids/{bid_id}")
async def add_bid_to_evaluation(evaluation_id: UUID, bid_id: UUID) -> dict:
    """Add a vendor bid to an evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    bid = bids_db.get(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    bid.evaluation_id = evaluation_id
    bids_db[bid_id] = bid

    return {"message": f"Bid {bid_id} added to evaluation {evaluation_id}"}


@router.post("/evaluations/{evaluation_id}/execute", response_model=TBEEvaluation)
async def execute_evaluation(
    evaluation_id: UUID,
    evaluated_by: Optional[str] = Query(None, description="Evaluator name"),
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
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Get bids for this evaluation
    eval_bids = [b for b in bids_db.values() if b.evaluation_id == evaluation_id]
    if not eval_bids:
        raise HTTPException(status_code=400, detail="No bids associated with this evaluation")

    vendors = get_vendors_dict()

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

    evaluations_db[evaluation_id] = evaluation

    return evaluation


@router.get("/evaluations/{evaluation_id}/results", response_model=list[TBEResult])
async def get_evaluation_results(evaluation_id: UUID) -> list[TBEResult]:
    """Get scored results for an evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    return evaluation.results


@router.get("/evaluations/{evaluation_id}/matrix", response_model=dict)
async def get_comparison_matrix(evaluation_id: UUID) -> dict:
    """Get comparison matrix for an evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.comparison_matrix:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    matrix_engine = ComparisonMatrixEngine()
    return matrix_engine.matrix_to_dict(evaluation.comparison_matrix)


@router.get("/evaluations/{evaluation_id}/ranking", response_model=dict)
async def get_ranking_summary(evaluation_id: UUID) -> dict:
    """Get ranking summary for an evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    ranking_engine = RankingEngine()
    return ranking_engine.generate_ranking_summary(evaluation.results)


@router.get("/evaluations/{evaluation_id}/tco", response_model=dict)
async def get_tco_analysis(evaluation_id: UUID) -> dict:
    """Get TCO analysis for an evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    # Extract TCO from results
    tco_calculations = [
        r.tco_calculation for r in evaluation.results if r.tco_calculation
    ]

    if not tco_calculations:
        raise HTTPException(status_code=400, detail="No TCO data available")

    tco_calculator = TCOCalculator()
    return tco_calculator.get_tco_summary(tco_calculations)


@router.get("/evaluations/{evaluation_id}/compliance", response_model=dict)
async def get_compliance_summary(evaluation_id: UUID) -> dict:
    """Get compliance summary for an evaluation."""
    evaluation = evaluations_db.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    # Extract compliance checks from results
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
def get_evaluations_dict() -> dict[UUID, TBEEvaluation]:
    """Get evaluations dictionary (for internal use)."""
    return evaluations_db


def get_bids_dict() -> dict[UUID, VendorBid]:
    """Get bids dictionary (for internal use)."""
    return bids_db
