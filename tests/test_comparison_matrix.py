"""
Tests for Comparison Matrix Engine.

Tests multi-criteria vendor comparison matrix generation.
"""

from uuid import UUID, uuid4

import pytest

from src.models.vendor import Vendor
from src.models.tbe import VendorBid, TBEResult, CriteriaCategory
from src.services.tbe_scoring import create_scoring_engine
from src.services.comparison_matrix import ComparisonMatrixEngine


class TestComparisonMatrixEngine:
    """Test suite for Comparison Matrix Engine."""

    @pytest.fixture
    def matrix_engine(self) -> ComparisonMatrixEngine:
        """Create comparison matrix engine."""
        return ComparisonMatrixEngine()

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

    def test_generate_matrix(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test basic matrix generation."""
        evaluation_id = uuid4()

        matrix = matrix_engine.generate_matrix(
            evaluation_id=evaluation_id,
            evaluation_name="Test Evaluation",
            results=scored_results,
        )

        assert matrix.evaluation_id == evaluation_id
        assert matrix.evaluation_name == "Test Evaluation"
        assert matrix.vendor_count == len(scored_results)
        assert len(matrix.vendor_names) == len(scored_results)
        assert len(matrix.vendor_ids) == len(scored_results)
        assert len(matrix.rows) > 0  # Should have criteria rows
        assert len(matrix.total_scores) == len(scored_results)

    def test_matrix_identifies_best_vendor(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test that matrix correctly identifies best vendor."""
        matrix = matrix_engine.generate_matrix(
            evaluation_id=uuid4(),
            evaluation_name="Test",
            results=scored_results,
        )

        # Matrix should identify best and worst
        assert matrix.best_vendor_id is not None
        assert matrix.best_vendor_name is not None

        # Best vendor should have highest score
        best_score = max(r.total_weighted_score for r in scored_results)
        best_vendor = next(r for r in scored_results if r.total_weighted_score == best_score)
        assert matrix.best_vendor_id == best_vendor.vendor_id

    def test_matrix_rows_have_rankings(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test that matrix rows include rankings."""
        matrix = matrix_engine.generate_matrix(
            evaluation_id=uuid4(),
            evaluation_name="Test",
            results=scored_results,
        )

        for row in matrix.rows:
            assert len(row.cells) == len(scored_results)
            for cell in row.cells:
                assert cell.rank >= 1
                assert cell.rank <= len(scored_results)

    def test_matrix_to_dict(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test matrix serialization to dictionary."""
        matrix = matrix_engine.generate_matrix(
            evaluation_id=uuid4(),
            evaluation_name="Test",
            results=scored_results,
        )

        matrix_dict = matrix_engine.matrix_to_dict(matrix)

        assert "evaluation_id" in matrix_dict
        assert "vendors" in matrix_dict
        assert "criteria_scores" in matrix_dict
        assert "total_scores" in matrix_dict
        assert "best_vendor" in matrix_dict

        # Verify vendors list
        assert len(matrix_dict["vendors"]) == len(scored_results)

    def test_criteria_summary(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test criteria summary generation."""
        matrix = matrix_engine.generate_matrix(
            evaluation_id=uuid4(),
            evaluation_name="Test",
            results=scored_results,
        )

        summary = matrix_engine.get_criteria_summary(matrix)

        assert "criteria_count" in summary
        assert "categories" in summary
        assert summary["criteria_count"] == len(matrix.rows)

    def test_criteria_summary_by_category(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test criteria summary filtered by category."""
        matrix = matrix_engine.generate_matrix(
            evaluation_id=uuid4(),
            evaluation_name="Test",
            results=scored_results,
        )

        summary = matrix_engine.get_criteria_summary(matrix, category=CriteriaCategory.PRICE)

        # Should only include price criteria
        for cat_name in summary["categories"]:
            assert cat_name == CriteriaCategory.PRICE.value

    def test_empty_results_raises_error(self, matrix_engine: ComparisonMatrixEngine):
        """Test that empty results raise an error."""
        with pytest.raises(ValueError, match="Cannot generate matrix without results"):
            matrix_engine.generate_matrix(
                evaluation_id=uuid4(),
                evaluation_name="Test",
                results=[],
            )

    def test_matrix_total_scores_ranking(
        self,
        matrix_engine: ComparisonMatrixEngine,
        scored_results: list[TBEResult],
    ):
        """Test that total scores are properly ranked."""
        matrix = matrix_engine.generate_matrix(
            evaluation_id=uuid4(),
            evaluation_name="Test",
            results=scored_results,
        )

        # Total scores should have is_best and is_worst markers
        best_count = sum(1 for cell in matrix.total_scores if cell.is_best)
        worst_count = sum(1 for cell in matrix.total_scores if cell.is_worst)

        assert best_count == 1  # Only one best
        if len(scored_results) > 1:
            assert worst_count == 1  # Only one worst (if more than 1 vendor)
