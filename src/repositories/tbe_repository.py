"""TBE repository for database operations."""

from datetime import datetime
from typing import Optional, Any
from uuid import uuid4
import json

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tbe import (
    EvaluationCriteriaDB,
    VendorBidDB,
    TBEEvaluationDB,
    TBEScoreDB,
    EvaluationCriteriaCreate,
    VendorBidCreate,
    TBEEvaluationCreate,
    EvaluationStatus,
)


class TBERepository:
    """Repository for TBE database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================================
    # Evaluation Criteria
    # ========================================================================

    async def create_criteria(self, criteria_data: EvaluationCriteriaCreate) -> EvaluationCriteriaDB:
        """Create evaluation criteria."""
        criteria = EvaluationCriteriaDB(
            id=str(uuid4()),
            name=criteria_data.name,
            code=criteria_data.code,
            category=criteria_data.category.value,
            description=criteria_data.description,
            weight=criteria_data.weight,
            max_score=criteria_data.max_score,
            is_mandatory=criteria_data.is_mandatory,
            scoring_guidance=criteria_data.scoring_guidance,
        )
        self.session.add(criteria)
        await self.session.flush()
        await self.session.refresh(criteria)
        return criteria

    async def get_criteria_by_id(self, criteria_id: str) -> Optional[EvaluationCriteriaDB]:
        """Get criteria by ID."""
        result = await self.session.execute(
            select(EvaluationCriteriaDB).where(EvaluationCriteriaDB.id == criteria_id)
        )
        return result.scalar_one_or_none()

    async def get_criteria_by_code(self, code: str) -> Optional[EvaluationCriteriaDB]:
        """Get criteria by code."""
        result = await self.session.execute(
            select(EvaluationCriteriaDB).where(EvaluationCriteriaDB.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all_criteria(self) -> list[EvaluationCriteriaDB]:
        """Get all evaluation criteria."""
        result = await self.session.execute(select(EvaluationCriteriaDB))
        return list(result.scalars().all())

    async def delete_criteria(self, criteria_id: str) -> bool:
        """Delete evaluation criteria."""
        result = await self.session.execute(
            delete(EvaluationCriteriaDB).where(EvaluationCriteriaDB.id == criteria_id)
        )
        return result.rowcount > 0

    # ========================================================================
    # Vendor Bids
    # ========================================================================

    async def create_bid(self, bid_data: VendorBidCreate) -> VendorBidDB:
        """Create a vendor bid."""
        bid = VendorBidDB(
            id=str(uuid4()),
            vendor_id=str(bid_data.vendor_id),
            bid_reference=bid_data.bid_reference,
            unit_price=bid_data.unit_price,
            quantity=bid_data.quantity,
            total_price=bid_data.unit_price * bid_data.quantity,
            currency=bid_data.currency,
            shipping_cost=bid_data.shipping_cost,
            installation_cost=bid_data.installation_cost,
            training_cost=bid_data.training_cost,
            maintenance_cost_annual=bid_data.maintenance_cost_annual,
            warranty_years=bid_data.warranty_years,
            expected_lifespan_years=bid_data.expected_lifespan_years,
            delivery_days=bid_data.delivery_days,
            delivery_terms=bid_data.delivery_terms,
            technical_specs=bid_data.technical_specs,
            certifications=bid_data.certifications,
            iso_compliance=bid_data.iso_compliance,
            quality_score=bid_data.quality_score,
            past_performance_score=bid_data.past_performance_score,
        )
        self.session.add(bid)
        await self.session.flush()
        await self.session.refresh(bid)
        return bid

    async def get_bid_by_id(self, bid_id: str) -> Optional[VendorBidDB]:
        """Get bid by ID."""
        result = await self.session.execute(
            select(VendorBidDB).where(VendorBidDB.id == bid_id)
        )
        return result.scalar_one_or_none()

    async def get_bids_by_vendor(self, vendor_id: str) -> list[VendorBidDB]:
        """Get all bids for a vendor."""
        result = await self.session.execute(
            select(VendorBidDB).where(VendorBidDB.vendor_id == vendor_id)
        )
        return list(result.scalars().all())

    async def get_bids_by_evaluation(self, evaluation_id: str) -> list[VendorBidDB]:
        """Get all bids for an evaluation."""
        result = await self.session.execute(
            select(VendorBidDB).where(VendorBidDB.evaluation_id == evaluation_id)
        )
        return list(result.scalars().all())

    async def get_all_bids(
        self,
        vendor_id: Optional[str] = None,
        evaluation_id: Optional[str] = None,
    ) -> list[VendorBidDB]:
        """Get all bids with optional filtering."""
        query = select(VendorBidDB)

        if vendor_id:
            query = query.where(VendorBidDB.vendor_id == vendor_id)

        if evaluation_id:
            query = query.where(VendorBidDB.evaluation_id == evaluation_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_bid_to_evaluation(self, bid_id: str, evaluation_id: str) -> Optional[VendorBidDB]:
        """Add a bid to an evaluation."""
        bid = await self.get_bid_by_id(bid_id)
        if not bid:
            return None

        bid.evaluation_id = evaluation_id
        await self.session.flush()
        await self.session.refresh(bid)
        return bid

    async def delete_bid(self, bid_id: str) -> bool:
        """Delete a bid."""
        result = await self.session.execute(
            delete(VendorBidDB).where(VendorBidDB.id == bid_id)
        )
        return result.rowcount > 0

    # ========================================================================
    # TBE Evaluations
    # ========================================================================

    async def create_evaluation(self, eval_data: TBEEvaluationCreate) -> TBEEvaluationDB:
        """Create a TBE evaluation."""
        # Convert criteria weights to dict
        weights_dict = eval_data.criteria_weights.model_dump()

        # Convert ISO standards to strings
        iso_standards = [std.value for std in eval_data.required_iso_standards]

        evaluation = TBEEvaluationDB(
            id=str(uuid4()),
            name=eval_data.name,
            description=eval_data.description,
            project_reference=eval_data.project_reference,
            criteria_weights=weights_dict,
            required_iso_standards=iso_standards,
            required_certifications=eval_data.required_certifications,
        )
        self.session.add(evaluation)
        await self.session.flush()
        await self.session.refresh(evaluation)
        return evaluation

    async def get_evaluation_by_id(self, evaluation_id: str) -> Optional[TBEEvaluationDB]:
        """Get evaluation by ID."""
        result = await self.session.execute(
            select(TBEEvaluationDB).where(TBEEvaluationDB.id == evaluation_id)
        )
        return result.scalar_one_or_none()

    async def get_all_evaluations(
        self,
        status: Optional[EvaluationStatus] = None,
    ) -> list[TBEEvaluationDB]:
        """Get all evaluations with optional filtering."""
        query = select(TBEEvaluationDB)

        if status:
            query = query.where(TBEEvaluationDB.status == status.value)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_evaluation_results(
        self,
        evaluation_id: str,
        status: EvaluationStatus,
        results: list[dict],
        ranking: list[str],
        recommended_vendor_id: Optional[str],
        evaluated_by: Optional[str],
    ) -> Optional[TBEEvaluationDB]:
        """Update evaluation with results."""
        evaluation = await self.get_evaluation_by_id(evaluation_id)
        if not evaluation:
            return None

        evaluation.status = status.value
        evaluation.evaluation_results = results
        evaluation.ranking = ranking
        evaluation.recommended_vendor_id = recommended_vendor_id
        evaluation.evaluated_by = evaluated_by
        evaluation.evaluated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(evaluation)
        return evaluation

    async def delete_evaluation(self, evaluation_id: str) -> bool:
        """Delete an evaluation."""
        result = await self.session.execute(
            delete(TBEEvaluationDB).where(TBEEvaluationDB.id == evaluation_id)
        )
        return result.rowcount > 0

    # ========================================================================
    # TBE Scores
    # ========================================================================

    async def save_score(
        self,
        evaluation_id: str,
        vendor_id: str,
        bid_id: str,
        criteria_id: str,
        raw_score: float,
        weighted_score: float,
        max_possible: float,
        comments: Optional[str] = None,
        scored_by: Optional[str] = None,
    ) -> TBEScoreDB:
        """Save an individual TBE score."""
        score = TBEScoreDB(
            id=str(uuid4()),
            evaluation_id=evaluation_id,
            vendor_id=vendor_id,
            bid_id=bid_id,
            criteria_id=criteria_id,
            raw_score=raw_score,
            weighted_score=weighted_score,
            max_possible=max_possible,
            comments=comments,
            scored_by=scored_by,
        )
        self.session.add(score)
        await self.session.flush()
        await self.session.refresh(score)
        return score

    async def get_scores_by_evaluation(self, evaluation_id: str) -> list[TBEScoreDB]:
        """Get all scores for an evaluation."""
        result = await self.session.execute(
            select(TBEScoreDB).where(TBEScoreDB.evaluation_id == evaluation_id)
        )
        return list(result.scalars().all())

    async def get_scores_by_vendor(self, evaluation_id: str, vendor_id: str) -> list[TBEScoreDB]:
        """Get scores for a specific vendor in an evaluation."""
        result = await self.session.execute(
            select(TBEScoreDB).where(
                TBEScoreDB.evaluation_id == evaluation_id,
                TBEScoreDB.vendor_id == vendor_id,
            )
        )
        return list(result.scalars().all())
