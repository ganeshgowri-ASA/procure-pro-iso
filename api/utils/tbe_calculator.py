"""
TBE (Technical Bid Evaluation) Calculator Module
Handles scoring and ranking of vendor quotations
"""

import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum

from database.connection import get_db_session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class ScoreCategory(Enum):
    """Score category types for TBE evaluation."""
    PRICE = 'price'
    QUALITY = 'quality'
    DELIVERY = 'delivery'
    COMPLIANCE = 'compliance'


@dataclass
class QuotationScore:
    """Represents scores for a single quotation."""
    quotation_id: str
    vendor_id: str
    vendor_name: str
    price_score: Decimal
    quality_score: Decimal
    delivery_score: Decimal
    compliance_score: Decimal
    total_weighted_score: Decimal
    rank: int
    is_recommended: bool
    remarks: str = ""


@dataclass
class TBEResult:
    """Complete TBE calculation result."""
    evaluation_id: str
    rfq_id: str
    scores: List[QuotationScore]
    weights: Dict[str, Decimal]
    recommended_vendor_id: Optional[str]
    summary: str


class TBECalculator:
    """
    Calculator for Technical Bid Evaluation scoring.

    Implements weighted scoring methodology for comparing vendor quotations
    based on multiple criteria including price, quality, delivery, and compliance.
    """

    DEFAULT_WEIGHTS = {
        'price': Decimal('0.40'),
        'quality': Decimal('0.25'),
        'delivery': Decimal('0.20'),
        'compliance': Decimal('0.15')
    }

    MAX_SCORE = Decimal('100')

    def __init__(self, weights: Optional[Dict[str, Decimal]] = None):
        """
        Initialize TBE Calculator.

        Args:
            weights: Optional custom weights for each category
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Validate that weights sum to 1.0."""
        total = sum(self.weights.values())
        if not (Decimal('0.99') <= total <= Decimal('1.01')):
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def calculate_scores(self, evaluation_id: str) -> TBEResult:
        """
        Calculate TBE scores for all quotations in an evaluation.

        Args:
            evaluation_id: UUID of the TBE evaluation

        Returns:
            TBEResult with all calculated scores
        """
        with get_db_session() as session:
            # Get evaluation details
            eval_result = session.execute(text("""
                SELECT rfq_id, weight_price, weight_quality,
                       weight_delivery, weight_compliance
                FROM tbe_evaluations
                WHERE id = :eval_id
            """), {'eval_id': evaluation_id})

            eval_row = eval_result.fetchone()
            if not eval_row:
                raise ValueError(f"Evaluation not found: {evaluation_id}")

            rfq_id = str(eval_row[0])
            self.weights = {
                'price': Decimal(str(eval_row[1])),
                'quality': Decimal(str(eval_row[2])),
                'delivery': Decimal(str(eval_row[3])),
                'compliance': Decimal(str(eval_row[4]))
            }

            # Get all quotations for this RFQ
            quot_result = session.execute(text("""
                SELECT q.id, q.vendor_id, v.company_name,
                       q.total_amount, q.delivery_days,
                       q.is_technically_compliant
                FROM quotations q
                JOIN vendors v ON q.vendor_id = v.id
                WHERE q.rfq_id = :rfq_id
                AND q.status = 'submitted'
            """), {'rfq_id': rfq_id})

            quotations = []
            for row in quot_result:
                quotations.append({
                    'id': str(row[0]),
                    'vendor_id': str(row[1]),
                    'vendor_name': row[2],
                    'total_amount': Decimal(str(row[3])) if row[3] else None,
                    'delivery_days': row[4],
                    'is_compliant': row[5]
                })

            if not quotations:
                return TBEResult(
                    evaluation_id=evaluation_id,
                    rfq_id=rfq_id,
                    scores=[],
                    weights=self.weights,
                    recommended_vendor_id=None,
                    summary="No quotations available for evaluation"
                )

            # Calculate scores
            scores = self._calculate_all_scores(quotations, session, evaluation_id)

            # Rank quotations
            ranked_scores = self._rank_quotations(scores)

            # Update database with scores
            self._save_scores(session, evaluation_id, ranked_scores)

            # Determine recommendation
            recommended = ranked_scores[0] if ranked_scores else None

            return TBEResult(
                evaluation_id=evaluation_id,
                rfq_id=rfq_id,
                scores=ranked_scores,
                weights=self.weights,
                recommended_vendor_id=recommended.vendor_id if recommended else None,
                summary=self._generate_summary(ranked_scores)
            )

    def _calculate_all_scores(
        self,
        quotations: List[Dict],
        session,
        evaluation_id: str
    ) -> List[QuotationScore]:
        """Calculate scores for all quotations."""
        scores = []

        # Extract values for normalization
        prices = [q['total_amount'] for q in quotations if q['total_amount']]
        delivery_days = [q['delivery_days'] for q in quotations if q['delivery_days']]

        min_price = min(prices) if prices else Decimal('0')
        max_price = max(prices) if prices else Decimal('1')
        min_delivery = min(delivery_days) if delivery_days else 0
        max_delivery = max(delivery_days) if delivery_days else 1

        for quot in quotations:
            # Calculate price score (lower is better)
            price_score = self._calculate_price_score(
                quot['total_amount'], min_price, max_price
            )

            # Calculate delivery score (faster is better)
            delivery_score = self._calculate_delivery_score(
                quot['delivery_days'], min_delivery, max_delivery
            )

            # Get quality scores from criteria evaluations
            quality_score = self._get_criteria_score(
                session, evaluation_id, quot['id'], 'quality'
            )

            # Get compliance score
            compliance_score = self._calculate_compliance_score(
                quot['is_compliant'],
                session, evaluation_id, quot['id']
            )

            # Calculate weighted total
            total = (
                price_score * self.weights['price'] +
                quality_score * self.weights['quality'] +
                delivery_score * self.weights['delivery'] +
                compliance_score * self.weights['compliance']
            )

            scores.append(QuotationScore(
                quotation_id=quot['id'],
                vendor_id=quot['vendor_id'],
                vendor_name=quot['vendor_name'],
                price_score=price_score,
                quality_score=quality_score,
                delivery_score=delivery_score,
                compliance_score=compliance_score,
                total_weighted_score=total.quantize(Decimal('0.01'), ROUND_HALF_UP),
                rank=0,  # Will be set during ranking
                is_recommended=False
            ))

        return scores

    def _calculate_price_score(
        self,
        price: Optional[Decimal],
        min_price: Decimal,
        max_price: Decimal
    ) -> Decimal:
        """
        Calculate price score using inverse linear normalization.
        Lower price = higher score.
        """
        if price is None or max_price == min_price:
            return Decimal('50')  # Default middle score

        # Inverse normalization: lowest price gets 100, highest gets minimum
        price_range = max_price - min_price
        if price_range == 0:
            return self.MAX_SCORE

        normalized = (max_price - price) / price_range
        score = Decimal('20') + (normalized * Decimal('80'))  # Score range 20-100

        return score.quantize(Decimal('0.01'), ROUND_HALF_UP)

    def _calculate_delivery_score(
        self,
        days: Optional[int],
        min_days: int,
        max_days: int
    ) -> Decimal:
        """
        Calculate delivery score based on lead time.
        Faster delivery = higher score.
        """
        if days is None:
            return Decimal('50')

        if max_days == min_days:
            return self.MAX_SCORE

        day_range = max_days - min_days
        if day_range == 0:
            return self.MAX_SCORE

        normalized = Decimal(str((max_days - days) / day_range))
        score = Decimal('20') + (normalized * Decimal('80'))

        return score.quantize(Decimal('0.01'), ROUND_HALF_UP)

    def _get_criteria_score(
        self,
        session,
        evaluation_id: str,
        quotation_id: str,
        category: str
    ) -> Decimal:
        """Get average score for a category from individual criteria scores."""
        result = session.execute(text("""
            SELECT AVG(s.weighted_score)
            FROM tbe_scores s
            JOIN tbe_criteria c ON s.criteria_id = c.id
            WHERE s.tbe_id = :eval_id
            AND s.quotation_id = :quot_id
            AND c.category = :category
        """), {
            'eval_id': evaluation_id,
            'quot_id': quotation_id,
            'category': category
        })

        avg_score = result.scalar()
        if avg_score is None:
            return Decimal('70')  # Default score if no criteria evaluated

        return Decimal(str(avg_score)).quantize(Decimal('0.01'), ROUND_HALF_UP)

    def _calculate_compliance_score(
        self,
        is_compliant: Optional[bool],
        session,
        evaluation_id: str,
        quotation_id: str
    ) -> Decimal:
        """Calculate compliance score based on technical compliance and criteria."""
        base_score = Decimal('100') if is_compliant else Decimal('0')

        # Check for compliance criteria scores
        criteria_score = self._get_criteria_score(
            session, evaluation_id, quotation_id, 'compliance'
        )

        # Weight: 60% technical compliance, 40% criteria evaluation
        if is_compliant is None:
            return criteria_score

        weighted = (base_score * Decimal('0.6')) + (criteria_score * Decimal('0.4'))
        return weighted.quantize(Decimal('0.01'), ROUND_HALF_UP)

    def _rank_quotations(self, scores: List[QuotationScore]) -> List[QuotationScore]:
        """Rank quotations by total weighted score (descending)."""
        # Sort by total score descending
        sorted_scores = sorted(
            scores,
            key=lambda s: s.total_weighted_score,
            reverse=True
        )

        # Assign ranks
        for i, score in enumerate(sorted_scores, start=1):
            score.rank = i
            if i == 1:
                score.is_recommended = True
                score.remarks = "Highest overall score - Recommended"
            elif i == 2:
                score.remarks = "Second highest score - Alternative"
            elif i == 3:
                score.remarks = "Third highest score"

        return sorted_scores

    def _save_scores(
        self,
        session,
        evaluation_id: str,
        scores: List[QuotationScore]
    ) -> None:
        """Save calculated scores to database."""
        for score in scores:
            # Update or insert TBE summary
            session.execute(text("""
                INSERT INTO tbe_summary (
                    tbe_id, quotation_id, vendor_id,
                    price_score, quality_score, delivery_score, compliance_score,
                    total_weighted_score, rank, is_recommended, remarks
                )
                VALUES (
                    :tbe_id, :quot_id, :vendor_id,
                    :price_score, :quality_score, :delivery_score, :compliance_score,
                    :total_score, :rank, :is_recommended, :remarks
                )
                ON CONFLICT (tbe_id, quotation_id)
                DO UPDATE SET
                    price_score = :price_score,
                    quality_score = :quality_score,
                    delivery_score = :delivery_score,
                    compliance_score = :compliance_score,
                    total_weighted_score = :total_score,
                    rank = :rank,
                    is_recommended = :is_recommended,
                    remarks = :remarks
            """), {
                'tbe_id': evaluation_id,
                'quot_id': score.quotation_id,
                'vendor_id': score.vendor_id,
                'price_score': float(score.price_score),
                'quality_score': float(score.quality_score),
                'delivery_score': float(score.delivery_score),
                'compliance_score': float(score.compliance_score),
                'total_score': float(score.total_weighted_score),
                'rank': score.rank,
                'is_recommended': score.is_recommended,
                'remarks': score.remarks
            })

            # Update quotation with scores
            session.execute(text("""
                UPDATE quotations
                SET overall_score = :score, rank = :rank
                WHERE id = :quot_id
            """), {
                'score': float(score.total_weighted_score),
                'rank': score.rank,
                'quot_id': score.quotation_id
            })

        # Update evaluation status
        if scores:
            session.execute(text("""
                UPDATE tbe_evaluations
                SET status = 'evaluated',
                    selected_vendor_id = :vendor_id,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :eval_id
            """), {
                'vendor_id': scores[0].vendor_id,
                'eval_id': evaluation_id
            })

    def _generate_summary(self, scores: List[QuotationScore]) -> str:
        """Generate a text summary of the evaluation results."""
        if not scores:
            return "No quotations evaluated."

        top_score = scores[0]
        summary_parts = [
            f"TBE Evaluation Complete - {len(scores)} quotations evaluated.",
            f"",
            f"Recommended Vendor: {top_score.vendor_name}",
            f"Total Weighted Score: {top_score.total_weighted_score}",
            f"",
            f"Score Breakdown:",
            f"  - Price Score: {top_score.price_score}",
            f"  - Quality Score: {top_score.quality_score}",
            f"  - Delivery Score: {top_score.delivery_score}",
            f"  - Compliance Score: {top_score.compliance_score}",
        ]

        if len(scores) > 1:
            summary_parts.extend([
                f"",
                f"Alternative: {scores[1].vendor_name} (Score: {scores[1].total_weighted_score})"
            ])

        return "\n".join(summary_parts)

    def compare_quotations(
        self,
        quotation_ids: List[str],
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comparison matrix for selected quotations.

        Args:
            quotation_ids: List of quotation UUIDs to compare
            criteria: Optional list of specific criteria to compare

        Returns:
            Comparison matrix with scores and differences
        """
        with get_db_session() as session:
            result = session.execute(text("""
                SELECT q.id, v.company_name, q.total_amount,
                       q.delivery_days, q.overall_score, q.rank
                FROM quotations q
                JOIN vendors v ON q.vendor_id = v.id
                WHERE q.id = ANY(:ids)
            """), {'ids': quotation_ids})

            comparison = {
                'quotations': [],
                'price_comparison': {},
                'delivery_comparison': {},
                'score_comparison': {}
            }

            prices = []
            for row in result:
                quot_data = {
                    'id': str(row[0]),
                    'vendor': row[1],
                    'total_amount': float(row[2]) if row[2] else None,
                    'delivery_days': row[3],
                    'score': float(row[4]) if row[4] else None,
                    'rank': row[5]
                }
                comparison['quotations'].append(quot_data)
                if row[2]:
                    prices.append(float(row[2]))

            if prices:
                min_price = min(prices)
                comparison['price_comparison'] = {
                    'lowest': min_price,
                    'savings_potential': {
                        q['vendor']: round((q['total_amount'] - min_price), 2)
                        for q in comparison['quotations']
                        if q['total_amount']
                    }
                }

            return comparison
