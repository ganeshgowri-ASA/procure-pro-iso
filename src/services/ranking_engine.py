"""
Ranking Engine - Automatic vendor ranking and recommendations.

Provides intelligent ranking based on weighted scores with recommendation generation.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.models.tbe import (
    RecommendationType,
    TBEResult,
    ComplianceCheck,
    TCOCalculation,
)


@dataclass
class RankingConfig:
    """Configuration for ranking behavior."""

    # Score thresholds for recommendations
    highly_recommended_threshold: float = 85.0
    recommended_threshold: float = 70.0
    acceptable_threshold: float = 50.0

    # Weight adjustments for ranking
    tco_ranking_weight: float = 0.3  # How much TCO affects final ranking
    compliance_ranking_weight: float = 0.2  # How much compliance affects ranking

    # Disqualification rules
    disqualify_below_compliance: float = 50.0
    disqualify_missing_mandatory: bool = True


class RankingEngine:
    """
    Automatic ranking and recommendation engine.

    Ranks vendors based on:
    - Weighted TBE scores
    - TCO calculations
    - Compliance assessments
    - Custom ranking rules
    """

    def __init__(self, config: Optional[RankingConfig] = None):
        """Initialize ranking engine with configuration."""
        self.config = config or RankingConfig()

    def rank_vendors(
        self,
        results: list[TBEResult],
        tco_calculations: Optional[list[TCOCalculation]] = None,
        compliance_checks: Optional[list[ComplianceCheck]] = None,
    ) -> list[TBEResult]:
        """
        Rank vendors and assign rankings to results.

        Args:
            results: TBE results to rank
            tco_calculations: Optional TCO calculations for ranking adjustment
            compliance_checks: Optional compliance checks for ranking adjustment

        Returns:
            Ranked list of TBE results with rank assignments
        """
        if not results:
            return []

        # Calculate composite scores for ranking
        ranking_scores = self._calculate_ranking_scores(
            results, tco_calculations, compliance_checks
        )

        # Sort by composite ranking score
        sorted_indices = sorted(
            range(len(results)),
            key=lambda i: ranking_scores[i],
            reverse=True,
        )

        # Assign ranks and update results
        ranked_results = []
        for rank, idx in enumerate(sorted_indices, 1):
            result = results[idx]
            result.rank = rank

            # Update recommendation based on ranking
            result.recommendation = self._determine_recommendation(
                result,
                ranking_scores[idx],
                compliance_checks[idx] if compliance_checks and idx < len(compliance_checks) else None,
            )

            # Add recommendation notes
            result.recommendation_notes = self._generate_recommendation_notes(
                result, rank, len(results)
            )

            ranked_results.append(result)

        return ranked_results

    def _calculate_ranking_scores(
        self,
        results: list[TBEResult],
        tco_calculations: Optional[list[TCOCalculation]],
        compliance_checks: Optional[list[ComplianceCheck]],
    ) -> list[float]:
        """Calculate composite ranking scores."""
        scores = []

        # Create lookup maps
        tco_map = {}
        if tco_calculations:
            tco_map = {calc.vendor_id: calc for calc in tco_calculations}

        compliance_map = {}
        if compliance_checks:
            compliance_map = {check.vendor_id: check for check in compliance_checks}

        for result in results:
            base_score = result.total_weighted_score

            # Adjust for TCO if available
            tco_adjustment = 0.0
            if result.vendor_id in tco_map:
                tco = tco_map[result.vendor_id]
                tco_adjustment = tco.tco_score * self.config.tco_ranking_weight

            # Adjust for compliance if available
            compliance_adjustment = 0.0
            if result.vendor_id in compliance_map:
                compliance = compliance_map[result.vendor_id]
                compliance_adjustment = (
                    compliance.overall_compliance_score * self.config.compliance_ranking_weight
                )

            # Calculate composite score
            composite = (
                base_score * (1 - self.config.tco_ranking_weight - self.config.compliance_ranking_weight)
                + tco_adjustment
                + compliance_adjustment
            )

            scores.append(composite)

        return scores

    def _determine_recommendation(
        self,
        result: TBEResult,
        composite_score: float,
        compliance_check: Optional[ComplianceCheck],
    ) -> RecommendationType:
        """Determine recommendation type based on scores and rules."""
        # Check for disqualification
        if compliance_check:
            if compliance_check.overall_compliance_score < self.config.disqualify_below_compliance:
                return RecommendationType.DISQUALIFIED

            if self.config.disqualify_missing_mandatory and not compliance_check.is_compliant:
                return RecommendationType.NOT_RECOMMENDED

        # Score-based recommendations
        if composite_score >= self.config.highly_recommended_threshold:
            return RecommendationType.HIGHLY_RECOMMENDED
        elif composite_score >= self.config.recommended_threshold:
            return RecommendationType.RECOMMENDED
        elif composite_score >= self.config.acceptable_threshold:
            return RecommendationType.ACCEPTABLE
        else:
            return RecommendationType.NOT_RECOMMENDED

    def _generate_recommendation_notes(
        self,
        result: TBEResult,
        rank: int,
        total_vendors: int,
    ) -> str:
        """Generate recommendation notes for a vendor."""
        notes_parts = []

        # Rank information
        if rank == 1:
            notes_parts.append("Top-ranked vendor based on overall evaluation.")
        elif rank <= 3:
            notes_parts.append(f"Ranked #{rank} of {total_vendors} vendors.")
        else:
            notes_parts.append(f"Ranked #{rank} of {total_vendors} vendors.")

        # Score commentary
        if result.total_weighted_score >= 90:
            notes_parts.append("Exceptional overall score.")
        elif result.total_weighted_score >= 80:
            notes_parts.append("Strong overall performance.")
        elif result.total_weighted_score >= 70:
            notes_parts.append("Good overall performance with room for improvement.")
        elif result.total_weighted_score >= 60:
            notes_parts.append("Acceptable but below average performance.")
        else:
            notes_parts.append("Below expectations in multiple criteria.")

        # Category-specific notes
        if result.price_score >= 90:
            notes_parts.append("Excellent price competitiveness.")
        elif result.price_score <= 50:
            notes_parts.append("Price is significantly higher than competitors.")

        if result.quality_score >= 90:
            notes_parts.append("Outstanding quality indicators.")
        elif result.quality_score <= 50:
            notes_parts.append("Quality concerns require attention.")

        if result.delivery_score >= 90:
            notes_parts.append("Best-in-class delivery performance.")
        elif result.delivery_score <= 50:
            notes_parts.append("Delivery timeline may be a concern.")

        if result.compliance_score >= 90:
            notes_parts.append("Full compliance with requirements.")
        elif result.compliance_score <= 50:
            notes_parts.append("Compliance gaps identified.")

        return " ".join(notes_parts)

    def get_top_recommendations(
        self,
        ranked_results: list[TBEResult],
        count: int = 3,
    ) -> list[TBEResult]:
        """
        Get top recommended vendors.

        Args:
            ranked_results: Ranked TBE results
            count: Number of top recommendations to return

        Returns:
            Top recommended vendors
        """
        # Filter out disqualified vendors
        qualified = [
            r for r in ranked_results
            if r.recommendation != RecommendationType.DISQUALIFIED
        ]

        # Sort by rank
        sorted_results = sorted(qualified, key=lambda r: r.rank)

        return sorted_results[:count]

    def generate_ranking_summary(
        self,
        ranked_results: list[TBEResult],
    ) -> dict:
        """
        Generate a summary of the ranking.

        Args:
            ranked_results: Ranked TBE results

        Returns:
            Summary dictionary
        """
        if not ranked_results:
            return {"message": "No vendors to rank"}

        # Count by recommendation
        recommendation_counts = {}
        for result in ranked_results:
            rec = result.recommendation.value
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

        # Statistics
        scores = [r.total_weighted_score for r in ranked_results]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        score_spread = max_score - min_score

        # Top vendor
        top_vendor = min(ranked_results, key=lambda r: r.rank)

        return {
            "total_vendors": len(ranked_results),
            "recommendation_breakdown": recommendation_counts,
            "score_statistics": {
                "average": round(avg_score, 2),
                "maximum": round(max_score, 2),
                "minimum": round(min_score, 2),
                "spread": round(score_spread, 2),
            },
            "top_recommendation": {
                "vendor_id": str(top_vendor.vendor_id),
                "vendor_name": top_vendor.vendor_name,
                "score": round(top_vendor.total_weighted_score, 2),
                "recommendation": top_vendor.recommendation.value,
            },
            "qualified_vendors": len([
                r for r in ranked_results
                if r.recommendation != RecommendationType.DISQUALIFIED
            ]),
            "disqualified_vendors": len([
                r for r in ranked_results
                if r.recommendation == RecommendationType.DISQUALIFIED
            ]),
        }

    def compare_top_vendors(
        self,
        ranked_results: list[TBEResult],
        count: int = 2,
    ) -> dict:
        """
        Compare top vendors head-to-head.

        Args:
            ranked_results: Ranked TBE results
            count: Number of top vendors to compare

        Returns:
            Comparison dictionary
        """
        top = self.get_top_recommendations(ranked_results, count)

        if len(top) < 2:
            return {"message": "Not enough vendors for comparison"}

        comparison = {
            "vendors": [],
            "criteria_comparison": {
                "price": [],
                "quality": [],
                "delivery": [],
                "compliance": [],
            },
            "winner_by_criteria": {},
        }

        # Build vendor data
        for result in top:
            comparison["vendors"].append({
                "rank": result.rank,
                "vendor_id": str(result.vendor_id),
                "vendor_name": result.vendor_name,
                "total_score": round(result.total_weighted_score, 2),
                "recommendation": result.recommendation.value,
            })

            comparison["criteria_comparison"]["price"].append({
                "vendor": result.vendor_name,
                "score": round(result.price_score, 2),
            })
            comparison["criteria_comparison"]["quality"].append({
                "vendor": result.vendor_name,
                "score": round(result.quality_score, 2),
            })
            comparison["criteria_comparison"]["delivery"].append({
                "vendor": result.vendor_name,
                "score": round(result.delivery_score, 2),
            })
            comparison["criteria_comparison"]["compliance"].append({
                "vendor": result.vendor_name,
                "score": round(result.compliance_score, 2),
            })

        # Determine winners by criteria
        for criteria in ["price", "quality", "delivery", "compliance"]:
            scores = comparison["criteria_comparison"][criteria]
            winner = max(scores, key=lambda x: x["score"])
            comparison["winner_by_criteria"][criteria] = winner["vendor"]

        return comparison
