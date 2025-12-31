"""
TBE Scoring Engine - Core weighted scoring algorithm.

Implements configurable weighted scoring for Technical Bid Evaluation with:
- Price scoring (lower is better, normalized)
- Quality scoring (higher is better)
- Delivery scoring (faster is better, normalized)
- Compliance scoring (based on ISO/certifications)
- Support for custom criteria with configurable weights
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.models.tbe import (
    CriteriaCategory,
    CriteriaWeight,
    DefaultCriteriaWeights,
    TBEScore,
    TBEResult,
    VendorBid,
    RecommendationType,
)
from src.models.vendor import Vendor


@dataclass
class ScoringConfig:
    """Configuration for scoring behavior."""

    # Price scoring: lower prices get higher scores
    price_scoring_method: str = "inverse_linear"  # inverse_linear, inverse_log, min_max

    # Delivery scoring: faster delivery gets higher scores
    delivery_scoring_method: str = "inverse_linear"

    # Minimum acceptable scores for recommendations
    min_score_highly_recommended: float = 85.0
    min_score_recommended: float = 70.0
    min_score_acceptable: float = 50.0

    # Mandatory compliance threshold
    mandatory_compliance_threshold: float = 100.0


class TBEScoringEngine:
    """
    Technical Bid Evaluation Scoring Engine.

    Calculates weighted scores for vendor bids across multiple criteria:
    - Price (40% default weight) - Lower prices score higher
    - Quality (25% default weight) - Based on quality indicators
    - Delivery (20% default weight) - Faster delivery scores higher
    - Compliance (15% default weight) - ISO/certification compliance
    """

    def __init__(
        self,
        weights: Optional[DefaultCriteriaWeights] = None,
        config: Optional[ScoringConfig] = None,
        custom_criteria: Optional[list[CriteriaWeight]] = None,
    ):
        """
        Initialize the scoring engine.

        Args:
            weights: Default criteria weights (price, quality, delivery, compliance)
            config: Scoring configuration options
            custom_criteria: Additional custom criteria with weights
        """
        self.weights = weights or DefaultCriteriaWeights()
        self.config = config or ScoringConfig()
        self.custom_criteria = custom_criteria or []

        # Validate weights sum to 1.0
        if not self.weights.is_valid():
            total = self.weights.total_weight()
            raise ValueError(
                f"Criteria weights must sum to 1.0, got {total:.4f}. "
                f"Weights: price={self.weights.price}, quality={self.weights.quality}, "
                f"delivery={self.weights.delivery}, compliance={self.weights.compliance}"
            )

    def calculate_price_score(
        self,
        bid_price: float,
        all_prices: list[float],
        max_score: float = 100.0,
    ) -> float:
        """
        Calculate price score - lower prices get higher scores.

        Uses inverse linear normalization: score = max_score * (1 - (price - min) / (max - min))
        The lowest price gets max_score, highest price gets 0.

        Args:
            bid_price: The bid price to score
            all_prices: All bid prices for comparison
            max_score: Maximum possible score

        Returns:
            Price score (0 to max_score)
        """
        if not all_prices:
            return 0.0

        min_price = min(all_prices)
        max_price = max(all_prices)

        if max_price == min_price:
            # All prices are equal
            return max_score

        if self.config.price_scoring_method == "inverse_linear":
            # Linear inverse: lowest price = max score
            normalized = (bid_price - min_price) / (max_price - min_price)
            return max_score * (1 - normalized)

        elif self.config.price_scoring_method == "inverse_log":
            # Logarithmic scaling for larger price differences
            import math

            log_range = math.log(max_price) - math.log(min_price)
            if log_range == 0:
                return max_score
            log_normalized = (math.log(bid_price) - math.log(min_price)) / log_range
            return max_score * (1 - log_normalized)

        elif self.config.price_scoring_method == "min_max":
            # Score relative to best price
            return max_score * (min_price / bid_price) if bid_price > 0 else 0.0

        return max_score * (1 - (bid_price - min_price) / (max_price - min_price))

    def calculate_delivery_score(
        self,
        delivery_days: int,
        all_delivery_days: list[int],
        max_score: float = 100.0,
    ) -> float:
        """
        Calculate delivery score - faster delivery gets higher scores.

        Args:
            delivery_days: Delivery time in days
            all_delivery_days: All delivery times for comparison
            max_score: Maximum possible score

        Returns:
            Delivery score (0 to max_score)
        """
        if not all_delivery_days:
            return 0.0

        min_days = min(all_delivery_days)
        max_days = max(all_delivery_days)

        if max_days == min_days:
            return max_score

        # Inverse linear: fastest delivery = max score
        normalized = (delivery_days - min_days) / (max_days - min_days)
        return max_score * (1 - normalized)

    def calculate_quality_score(
        self,
        quality_rating: float,
        past_performance: float,
        max_score: float = 100.0,
    ) -> float:
        """
        Calculate quality score based on quality indicators.

        Args:
            quality_rating: Quality rating (0-100)
            past_performance: Past performance score (0-100)
            max_score: Maximum possible score

        Returns:
            Quality score (0 to max_score)
        """
        # Weighted average of quality indicators
        quality_weight = 0.6
        performance_weight = 0.4

        raw_score = (quality_rating * quality_weight) + (past_performance * performance_weight)
        return min(raw_score, max_score)

    def calculate_compliance_score(
        self,
        provided_standards: list[str],
        required_standards: list[str],
        provided_certs: list[str],
        required_certs: list[str],
        max_score: float = 100.0,
    ) -> float:
        """
        Calculate compliance score based on ISO standards and certifications.

        Args:
            provided_standards: ISO standards the vendor has
            required_standards: Required ISO standards
            provided_certs: Certifications the vendor has
            required_certs: Required certifications
            max_score: Maximum possible score

        Returns:
            Compliance score (0 to max_score)
        """
        if not required_standards and not required_certs:
            # No requirements, full compliance
            return max_score

        total_required = len(required_standards) + len(required_certs)
        if total_required == 0:
            return max_score

        # Normalize provided lists for comparison
        provided_standards_normalized = [s.upper().strip() for s in provided_standards]
        provided_certs_normalized = [c.upper().strip() for c in provided_certs]

        # Count matches
        iso_matches = sum(
            1
            for req in required_standards
            if req.upper().strip() in provided_standards_normalized
            or any(req.upper() in std for std in provided_standards_normalized)
        )

        cert_matches = sum(
            1
            for req in required_certs
            if req.upper().strip() in provided_certs_normalized
            or any(req.upper() in cert for cert in provided_certs_normalized)
        )

        total_matches = iso_matches + cert_matches
        compliance_ratio = total_matches / total_required

        return max_score * compliance_ratio

    def score_bid(
        self,
        bid: VendorBid,
        vendor: Vendor,
        all_bids: list[VendorBid],
        required_standards: list[str],
        required_certs: list[str],
    ) -> TBEResult:
        """
        Calculate complete TBE score for a vendor bid.

        Args:
            bid: The vendor bid to score
            vendor: The vendor information
            all_bids: All bids for comparison (price/delivery normalization)
            required_standards: Required ISO standards
            required_certs: Required certifications

        Returns:
            Complete TBE result with all scores
        """
        scores: list[TBEScore] = []

        # Extract comparison data
        all_prices = [b.total_price for b in all_bids]
        all_delivery = [b.delivery_days for b in all_bids]

        # Calculate Price Score
        price_raw = self.calculate_price_score(bid.total_price, all_prices)
        price_weighted = price_raw * self.weights.price
        scores.append(
            TBEScore(
                criteria_id=UUID("00000000-0000-0000-0000-000000000001"),
                criteria_name="Price Competitiveness",
                criteria_category=CriteriaCategory.PRICE,
                raw_score=price_raw,
                weight=self.weights.price,
                weighted_score=price_weighted,
                max_possible=100.0 * self.weights.price,
                percentage=(price_raw / 100.0) * 100 if price_raw > 0 else 0,
                comments=f"Total price: {bid.total_price:,.2f} {bid.currency}",
            )
        )

        # Calculate Quality Score
        quality_raw = self.calculate_quality_score(bid.quality_score, bid.past_performance_score)
        quality_weighted = quality_raw * self.weights.quality
        scores.append(
            TBEScore(
                criteria_id=UUID("00000000-0000-0000-0000-000000000002"),
                criteria_name="Quality Assessment",
                criteria_category=CriteriaCategory.QUALITY,
                raw_score=quality_raw,
                weight=self.weights.quality,
                weighted_score=quality_weighted,
                max_possible=100.0 * self.weights.quality,
                percentage=(quality_raw / 100.0) * 100 if quality_raw > 0 else 0,
                comments=f"Quality: {bid.quality_score:.1f}, Past Performance: {bid.past_performance_score:.1f}",
            )
        )

        # Calculate Delivery Score
        delivery_raw = self.calculate_delivery_score(bid.delivery_days, all_delivery)
        delivery_weighted = delivery_raw * self.weights.delivery
        scores.append(
            TBEScore(
                criteria_id=UUID("00000000-0000-0000-0000-000000000003"),
                criteria_name="Delivery Performance",
                criteria_category=CriteriaCategory.DELIVERY,
                raw_score=delivery_raw,
                weight=self.weights.delivery,
                weighted_score=delivery_weighted,
                max_possible=100.0 * self.weights.delivery,
                percentage=(delivery_raw / 100.0) * 100 if delivery_raw > 0 else 0,
                comments=f"Delivery: {bid.delivery_days} days",
            )
        )

        # Calculate Compliance Score
        compliance_raw = self.calculate_compliance_score(
            bid.iso_compliance,
            required_standards,
            bid.certifications,
            required_certs,
        )
        compliance_weighted = compliance_raw * self.weights.compliance
        scores.append(
            TBEScore(
                criteria_id=UUID("00000000-0000-0000-0000-000000000004"),
                criteria_name="Compliance & Standards",
                criteria_category=CriteriaCategory.COMPLIANCE,
                raw_score=compliance_raw,
                weight=self.weights.compliance,
                weighted_score=compliance_weighted,
                max_possible=100.0 * self.weights.compliance,
                percentage=(compliance_raw / 100.0) * 100 if compliance_raw > 0 else 0,
                comments=f"ISO: {len(bid.iso_compliance)} standards, Certs: {len(bid.certifications)}",
            )
        )

        # Calculate totals
        total_weighted = sum(s.weighted_score for s in scores)
        total_raw = sum(s.raw_score for s in scores)

        # Determine recommendation
        recommendation = self._get_recommendation(total_weighted, compliance_raw)

        return TBEResult(
            vendor_id=bid.vendor_id,
            vendor_name=vendor.name,
            vendor_code=vendor.code,
            bid_id=bid.id,
            bid_reference=bid.bid_reference,
            scores=scores,
            price_score=price_raw,
            quality_score=quality_raw,
            delivery_score=delivery_raw,
            compliance_score=compliance_raw,
            total_weighted_score=total_weighted,
            total_raw_score=total_raw,
            max_possible_score=100.0,
            recommendation=recommendation,
        )

    def _get_recommendation(
        self,
        total_score: float,
        compliance_score: float,
    ) -> RecommendationType:
        """Determine recommendation based on scores."""
        # Check if disqualified due to compliance
        if compliance_score < self.config.mandatory_compliance_threshold * 0.5:
            return RecommendationType.DISQUALIFIED

        if total_score >= self.config.min_score_highly_recommended:
            return RecommendationType.HIGHLY_RECOMMENDED
        elif total_score >= self.config.min_score_recommended:
            return RecommendationType.RECOMMENDED
        elif total_score >= self.config.min_score_acceptable:
            return RecommendationType.ACCEPTABLE
        else:
            return RecommendationType.NOT_RECOMMENDED

    def evaluate_all_bids(
        self,
        bids: list[VendorBid],
        vendors: dict[UUID, Vendor],
        required_standards: list[str],
        required_certs: list[str],
    ) -> list[TBEResult]:
        """
        Evaluate all vendor bids and return scored results.

        Args:
            bids: List of vendor bids
            vendors: Dictionary mapping vendor IDs to Vendor objects
            required_standards: Required ISO standards
            required_certs: Required certifications

        Returns:
            List of TBE results for all vendors
        """
        results = []

        for bid in bids:
            vendor = vendors.get(bid.vendor_id)
            if not vendor:
                continue

            result = self.score_bid(
                bid=bid,
                vendor=vendor,
                all_bids=bids,
                required_standards=required_standards,
                required_certs=required_certs,
            )
            results.append(result)

        return results


def create_scoring_engine(
    price_weight: float = 0.40,
    quality_weight: float = 0.25,
    delivery_weight: float = 0.20,
    compliance_weight: float = 0.15,
    config: Optional[ScoringConfig] = None,
) -> TBEScoringEngine:
    """
    Factory function to create a TBE scoring engine with custom weights.

    Args:
        price_weight: Weight for price criteria (default 40%)
        quality_weight: Weight for quality criteria (default 25%)
        delivery_weight: Weight for delivery criteria (default 20%)
        compliance_weight: Weight for compliance criteria (default 15%)
        config: Optional scoring configuration

    Returns:
        Configured TBEScoringEngine instance
    """
    weights = DefaultCriteriaWeights(
        price=price_weight,
        quality=quality_weight,
        delivery=delivery_weight,
        compliance=compliance_weight,
    )

    return TBEScoringEngine(weights=weights, config=config)
