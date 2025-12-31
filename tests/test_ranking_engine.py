"""
Tests for Ranking Engine.

Tests automatic vendor ranking and recommendation generation.
"""

from uuid import UUID

import pytest

from src.models.vendor import Vendor
from src.models.tbe import VendorBid, TBEResult, RecommendationType
from src.services.tbe_scoring import create_scoring_engine
from src.services.ranking_engine import RankingEngine, RankingConfig


class TestRankingEngine:
    """Test suite for Ranking Engine."""

    @pytest.fixture
    def ranking_engine(self) -> RankingEngine:
        """Create ranking engine with default config."""
        return RankingEngine()

    @pytest.fixture
    def scored_results(
        self,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ) -> list[TBEResult]:
        """Create scored TBE results."""
        engine = create_scoring_engine()

        return engine.evaluate_all_bids(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=["ISO 9001"],
            required_certs=[],
        )

    def test_rank_vendors(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test basic vendor ranking."""
        ranked_results = ranking_engine.rank_vendors(scored_results)

        assert len(ranked_results) == len(scored_results)

        # Check ranks are assigned correctly
        ranks = [r.rank for r in ranked_results]
        assert min(ranks) == 1
        assert max(ranks) == len(scored_results)

        # Verify ordering (rank 1 should have highest score)
        rank_1 = next(r for r in ranked_results if r.rank == 1)
        for result in ranked_results:
            if result.rank > 1:
                assert result.total_weighted_score <= rank_1.total_weighted_score

    def test_recommendations_assigned(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test that recommendations are assigned to all results."""
        ranked_results = ranking_engine.rank_vendors(scored_results)

        for result in ranked_results:
            assert result.recommendation in list(RecommendationType)
            assert result.recommendation_notes is not None
            assert len(result.recommendation_notes) > 0

    def test_get_top_recommendations(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test getting top recommendations."""
        ranked_results = ranking_engine.rank_vendors(scored_results)

        top_3 = ranking_engine.get_top_recommendations(ranked_results, count=3)

        assert len(top_3) <= 3
        assert all(r.rank <= 3 for r in top_3)

        # Should be sorted by rank
        for i in range(len(top_3) - 1):
            assert top_3[i].rank <= top_3[i + 1].rank

    def test_ranking_summary(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test ranking summary generation."""
        ranked_results = ranking_engine.rank_vendors(scored_results)

        summary = ranking_engine.generate_ranking_summary(ranked_results)

        assert "total_vendors" in summary
        assert "recommendation_breakdown" in summary
        assert "score_statistics" in summary
        assert "top_recommendation" in summary
        assert "qualified_vendors" in summary

        assert summary["total_vendors"] == len(scored_results)
        assert "average" in summary["score_statistics"]
        assert "maximum" in summary["score_statistics"]
        assert "minimum" in summary["score_statistics"]

    def test_compare_top_vendors(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test head-to-head comparison of top vendors."""
        ranked_results = ranking_engine.rank_vendors(scored_results)

        comparison = ranking_engine.compare_top_vendors(ranked_results, count=2)

        assert "vendors" in comparison
        assert "criteria_comparison" in comparison
        assert "winner_by_criteria" in comparison

        assert len(comparison["vendors"]) == 2
        assert "price" in comparison["criteria_comparison"]
        assert "quality" in comparison["criteria_comparison"]
        assert "delivery" in comparison["criteria_comparison"]
        assert "compliance" in comparison["criteria_comparison"]

    def test_custom_ranking_thresholds(self, scored_results: list[TBEResult]):
        """Test ranking with custom thresholds."""
        config = RankingConfig(
            highly_recommended_threshold=95.0,  # Very high bar
            recommended_threshold=80.0,
            acceptable_threshold=60.0,
        )
        engine = RankingEngine(config=config)

        ranked_results = engine.rank_vendors(scored_results)

        # With higher thresholds, fewer should be highly recommended
        highly_rec = [
            r for r in ranked_results
            if r.recommendation == RecommendationType.HIGHLY_RECOMMENDED
        ]
        # With 95% threshold, likely no one qualifies
        assert len(highly_rec) <= 1

    def test_empty_results(self, ranking_engine: RankingEngine):
        """Test ranking with empty results."""
        ranked = ranking_engine.rank_vendors([])
        assert ranked == []

        summary = ranking_engine.generate_ranking_summary([])
        assert "message" in summary

    def test_single_vendor_ranking(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test ranking with single vendor."""
        single_result = [scored_results[0]]
        ranked = ranking_engine.rank_vendors(single_result)

        assert len(ranked) == 1
        assert ranked[0].rank == 1

    def test_recommendation_notes_content(
        self,
        ranking_engine: RankingEngine,
        scored_results: list[TBEResult],
    ):
        """Test that recommendation notes contain useful information."""
        ranked_results = ranking_engine.rank_vendors(scored_results)

        for result in ranked_results:
            notes = result.recommendation_notes
            # Notes should mention ranking
            assert "Ranked" in notes or "Top-ranked" in notes
            # Notes should have some commentary about performance
            assert "performance" in notes.lower() or "score" in notes.lower()
