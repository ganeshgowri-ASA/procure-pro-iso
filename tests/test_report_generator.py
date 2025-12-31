"""
Tests for TBE Report Generator.

Tests report generation including charts and summaries.
"""

from uuid import UUID

import pytest

from src.models.vendor import Vendor
from src.models.tbe import VendorBid, ISOStandard
from src.services.tbe_scoring import create_scoring_engine
from src.services.comparison_matrix import ComparisonMatrixEngine
from src.services.tco_calculator import TCOCalculator
from src.services.compliance_scorer import ComplianceScorer
from src.services.report_generator import TBEReportGenerator


class TestReportGenerator:
    """Test suite for TBE Report Generator."""

    @pytest.fixture
    def report_generator(self, tmp_path) -> TBEReportGenerator:
        """Create report generator with temp output directory."""
        return TBEReportGenerator(output_dir=str(tmp_path), dpi=72)  # Lower DPI for faster tests

    @pytest.fixture
    def full_evaluation_data(
        self,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
        sample_evaluation,
    ):
        """Create complete evaluation data for report generation."""
        # Score bids
        scoring_engine = create_scoring_engine()
        results = scoring_engine.evaluate_all_bids(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=["ISO 9001", "ISO 17025"],
            required_certs=["CE Mark"],
        )

        # Generate comparison matrix
        matrix_engine = ComparisonMatrixEngine()
        matrix = matrix_engine.generate_matrix(
            evaluation_id=sample_evaluation.id,
            evaluation_name=sample_evaluation.name,
            results=results,
        )

        # Calculate TCO
        tco_calculator = TCOCalculator()
        tco_calculations = tco_calculator.calculate_all_tco(sample_bids, sample_vendors)

        # Check compliance
        compliance_scorer = ComplianceScorer()
        compliance_checks = compliance_scorer.check_all_vendors(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=[ISOStandard.ISO_9001, ISOStandard.ISO_17025],
            required_certifications=["CE Mark"],
        )

        # Update evaluation with results
        sample_evaluation.results = results
        sample_evaluation.comparison_matrix = matrix

        return {
            "evaluation": sample_evaluation,
            "results": results,
            "matrix": matrix,
            "tco_calculations": tco_calculations,
            "compliance_checks": compliance_checks,
        }

    def test_generate_report(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test complete report generation."""
        report = report_generator.generate_report(
            evaluation=full_evaluation_data["evaluation"],
            results=full_evaluation_data["results"],
            matrix=full_evaluation_data["matrix"],
            tco_calculations=full_evaluation_data["tco_calculations"],
            compliance_checks=full_evaluation_data["compliance_checks"],
            generated_by="Test User",
        )

        assert report.evaluation is not None
        assert report.comparison_matrix is not None
        assert len(report.tco_summary) > 0
        assert len(report.compliance_summary) > 0
        assert report.executive_summary is not None
        assert len(report.recommendations) > 0
        assert report.generated_by == "Test User"

    def test_generate_score_chart(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test score chart generation."""
        chart_base64 = report_generator._generate_score_chart(
            full_evaluation_data["results"]
        )

        assert chart_base64 is not None
        assert chart_base64.startswith("data:image/png;base64,")
        assert len(chart_base64) > 100  # Should have actual image data

    def test_generate_tco_chart(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test TCO chart generation."""
        chart_base64 = report_generator._generate_tco_chart(
            full_evaluation_data["tco_calculations"]
        )

        assert chart_base64 is not None
        assert chart_base64.startswith("data:image/png;base64,")

    def test_generate_radar_chart(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test radar chart generation."""
        chart_base64 = report_generator._generate_radar_chart(
            full_evaluation_data["results"]
        )

        assert chart_base64 is not None
        assert chart_base64.startswith("data:image/png;base64,")

    def test_generate_compliance_heatmap(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test compliance heatmap generation."""
        chart_base64 = report_generator.generate_compliance_heatmap(
            full_evaluation_data["compliance_checks"]
        )

        assert chart_base64 is not None
        assert chart_base64.startswith("data:image/png;base64,")

    def test_executive_summary_content(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test executive summary contains key information."""
        summary = report_generator._generate_executive_summary(
            evaluation=full_evaluation_data["evaluation"],
            results=full_evaluation_data["results"],
            tco_calculations=full_evaluation_data["tco_calculations"],
            compliance_checks=full_evaluation_data["compliance_checks"],
        )

        assert "Executive Summary" in summary
        assert "Evaluation" in summary
        assert "Recommendation" in summary
        assert "Total Cost of Ownership" in summary
        assert "Compliance" in summary

    def test_recommendations_generated(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test recommendations are generated."""
        recommendations = report_generator._generate_recommendations(
            results=full_evaluation_data["results"],
            tco_calculations=full_evaluation_data["tco_calculations"],
        )

        assert len(recommendations) > 0
        assert any("RECOMMENDED" in r for r in recommendations)

    def test_save_chart_to_file(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
        tmp_path,
    ):
        """Test saving chart to file."""
        chart_base64 = report_generator._generate_score_chart(
            full_evaluation_data["results"]
        )

        filepath = report_generator.save_chart_to_file(chart_base64, "test_chart.png")

        assert filepath.endswith("test_chart.png")
        import os
        assert os.path.exists(filepath)

    def test_export_report_json(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
        tmp_path,
    ):
        """Test exporting report to JSON."""
        report = report_generator.generate_report(
            evaluation=full_evaluation_data["evaluation"],
            results=full_evaluation_data["results"],
            matrix=full_evaluation_data["matrix"],
            tco_calculations=full_evaluation_data["tco_calculations"],
            compliance_checks=full_evaluation_data["compliance_checks"],
        )

        filepath = report_generator.export_report_json(report, "test_report.json")

        import os
        import json

        assert os.path.exists(filepath)

        with open(filepath) as f:
            data = json.load(f)

        assert "evaluation_name" in data
        assert "executive_summary" in data
        assert "recommendations" in data
        assert "results" in data

    def test_empty_results_chart(self, report_generator: TBEReportGenerator):
        """Test chart generation with empty results."""
        chart = report_generator._generate_score_chart([])
        assert chart == ""

    def test_single_vendor_radar(
        self,
        report_generator: TBEReportGenerator,
        full_evaluation_data: dict,
    ):
        """Test radar chart with single vendor (needs at least 2)."""
        single_result = [full_evaluation_data["results"][0]]
        chart = report_generator._generate_radar_chart(single_result)
        assert chart == ""  # Should return empty for < 2 vendors
