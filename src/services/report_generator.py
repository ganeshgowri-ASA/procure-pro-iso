"""
TBE Report Generator - Comprehensive report generation with charts.

Generates detailed TBE reports including:
- Executive summary
- Score comparison charts
- TCO analysis charts
- Radar charts for multi-criteria comparison
- PDF/HTML report generation
"""

import base64
import io
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from src.config.settings import get_settings
from src.models.tbe import (
    ComparisonMatrix,
    ComplianceCheck,
    TCOCalculation,
    TBEEvaluation,
    TBEReport,
    TBEResult,
    RecommendationType,
)


class TBEReportGenerator:
    """
    TBE Report Generator.

    Creates comprehensive TBE reports with:
    - Score visualizations (bar charts, radar charts)
    - TCO comparison charts
    - Compliance heatmaps
    - Executive summaries
    - Detailed recommendations
    """

    def __init__(self, output_dir: Optional[str] = None, dpi: int = 150):
        """
        Initialize report generator.

        Args:
            output_dir: Directory for saving reports
            dpi: Resolution for chart images
        """
        settings = get_settings()
        self.output_dir = output_dir or settings.report_output_dir
        self.dpi = dpi or settings.chart_dpi

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Chart styling
        self.colors = {
            "primary": "#2563eb",
            "secondary": "#7c3aed",
            "success": "#059669",
            "warning": "#d97706",
            "danger": "#dc2626",
            "info": "#0891b2",
            "gray": "#6b7280",
        }

        self.vendor_colors = [
            "#2563eb",
            "#7c3aed",
            "#059669",
            "#d97706",
            "#dc2626",
            "#0891b2",
            "#84cc16",
            "#f43f5e",
            "#8b5cf6",
            "#14b8a6",
        ]

    def generate_report(
        self,
        evaluation: TBEEvaluation,
        results: list[TBEResult],
        matrix: ComparisonMatrix,
        tco_calculations: list[TCOCalculation],
        compliance_checks: list[ComplianceCheck],
        generated_by: Optional[str] = None,
    ) -> TBEReport:
        """
        Generate a complete TBE report.

        Args:
            evaluation: The TBE evaluation
            results: Scored TBE results
            matrix: Comparison matrix
            tco_calculations: TCO calculations
            compliance_checks: Compliance check results
            generated_by: Report generator name

        Returns:
            Complete TBE report
        """
        # Generate charts
        score_chart = self._generate_score_chart(results)
        tco_chart = self._generate_tco_chart(tco_calculations)
        radar_chart = self._generate_radar_chart(results)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            evaluation, results, tco_calculations, compliance_checks
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(results, tco_calculations)

        return TBEReport(
            evaluation=evaluation,
            comparison_matrix=matrix,
            tco_summary=tco_calculations,
            compliance_summary=compliance_checks,
            score_chart=score_chart,
            tco_chart=tco_chart,
            radar_chart=radar_chart,
            executive_summary=executive_summary,
            recommendations=recommendations,
            generated_at=datetime.utcnow(),
            generated_by=generated_by,
        )

    def _generate_score_chart(self, results: list[TBEResult]) -> str:
        """Generate bar chart comparing vendor scores."""
        if not results:
            return ""

        fig, ax = plt.subplots(figsize=(12, 6))

        vendors = [r.vendor_name for r in results]
        x = np.arange(len(vendors))
        width = 0.2

        # Score categories
        price_scores = [r.price_score for r in results]
        quality_scores = [r.quality_score for r in results]
        delivery_scores = [r.delivery_score for r in results]
        compliance_scores = [r.compliance_score for r in results]

        # Create grouped bars
        bars1 = ax.bar(x - 1.5 * width, price_scores, width, label="Price", color=self.colors["primary"])
        bars2 = ax.bar(x - 0.5 * width, quality_scores, width, label="Quality", color=self.colors["secondary"])
        bars3 = ax.bar(x + 0.5 * width, delivery_scores, width, label="Delivery", color=self.colors["success"])
        bars4 = ax.bar(x + 1.5 * width, compliance_scores, width, label="Compliance", color=self.colors["warning"])

        # Customize chart
        ax.set_xlabel("Vendors", fontsize=12)
        ax.set_ylabel("Score", fontsize=12)
        ax.set_title("Vendor Score Comparison by Criteria", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(vendors, rotation=45, ha="right")
        ax.legend(loc="upper right")
        ax.set_ylim(0, 110)
        ax.grid(axis="y", alpha=0.3)

        # Add score labels on bars
        for bars in [bars1, bars2, bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        plt.tight_layout()

        # Convert to base64
        return self._fig_to_base64(fig)

    def _generate_tco_chart(self, tco_calculations: list[TCOCalculation]) -> str:
        """Generate stacked bar chart for TCO comparison."""
        if not tco_calculations:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        vendors = [calc.vendor_name for calc in tco_calculations]
        x = np.arange(len(vendors))

        # Cost components
        acquisition = [calc.acquisition_cost for calc in tco_calculations]
        operational = [calc.operational_cost for calc in tco_calculations]

        # Create stacked bars
        bars1 = ax.bar(x, acquisition, label="Acquisition Cost", color=self.colors["primary"])
        bars2 = ax.bar(x, operational, bottom=acquisition, label="Operational Cost", color=self.colors["secondary"])

        # Customize chart
        ax.set_xlabel("Vendors", fontsize=12)
        ax.set_ylabel("Cost ($)", fontsize=12)
        ax.set_title("Total Cost of Ownership Comparison", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(vendors, rotation=45, ha="right")
        ax.legend(loc="upper right")
        ax.grid(axis="y", alpha=0.3)

        # Add total labels
        for i, calc in enumerate(tco_calculations):
            ax.annotate(
                f"${calc.total_cost_of_ownership:,.0f}",
                xy=(i, calc.total_cost_of_ownership),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _generate_radar_chart(self, results: list[TBEResult]) -> str:
        """Generate radar chart for multi-criteria comparison."""
        if not results or len(results) < 2:
            return ""

        # Limit to top 5 vendors for readability
        top_results = sorted(results, key=lambda r: r.total_weighted_score, reverse=True)[:5]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))

        # Categories
        categories = ["Price", "Quality", "Delivery", "Compliance"]
        N = len(categories)

        # Compute angles
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the loop

        # Plot each vendor
        for idx, result in enumerate(top_results):
            values = [
                result.price_score,
                result.quality_score,
                result.delivery_score,
                result.compliance_score,
            ]
            values += values[:1]  # Complete the loop

            color = self.vendor_colors[idx % len(self.vendor_colors)]
            ax.plot(angles, values, "o-", linewidth=2, label=result.vendor_name, color=color)
            ax.fill(angles, values, alpha=0.1, color=color)

        # Customize chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 100)
        ax.set_title(
            "Multi-Criteria Vendor Comparison",
            fontsize=14,
            fontweight="bold",
            y=1.08,
        )
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
        ax.grid(True)

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def generate_compliance_heatmap(
        self,
        compliance_checks: list[ComplianceCheck],
    ) -> str:
        """Generate heatmap for compliance visualization."""
        if not compliance_checks:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        vendors = [check.vendor_name for check in compliance_checks]
        categories = ["ISO Compliance", "Certification", "Overall"]

        data = np.array([
            [check.iso_compliance_score for check in compliance_checks],
            [check.certification_compliance_score for check in compliance_checks],
            [check.overall_compliance_score for check in compliance_checks],
        ])

        im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

        # Labels
        ax.set_xticks(np.arange(len(vendors)))
        ax.set_yticks(np.arange(len(categories)))
        ax.set_xticklabels(vendors, rotation=45, ha="right")
        ax.set_yticklabels(categories)

        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Compliance Score", rotation=-90, va="bottom")

        # Add text annotations
        for i in range(len(categories)):
            for j in range(len(vendors)):
                text = ax.text(
                    j, i, f"{data[i, j]:.0f}",
                    ha="center", va="center",
                    color="white" if data[i, j] < 50 else "black",
                    fontweight="bold",
                )

        ax.set_title("Vendor Compliance Heatmap", fontsize=14, fontweight="bold")
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 encoded string."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=self.dpi, bbox_inches="tight")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"

    def _generate_executive_summary(
        self,
        evaluation: TBEEvaluation,
        results: list[TBEResult],
        tco_calculations: list[TCOCalculation],
        compliance_checks: list[ComplianceCheck],
    ) -> str:
        """Generate executive summary for the report."""
        if not results:
            return "No vendor bids were evaluated."

        # Get top vendor
        ranked = sorted(results, key=lambda r: r.rank)
        top_vendor = ranked[0] if ranked else None

        # Count recommendations
        highly_rec = sum(1 for r in results if r.recommendation == RecommendationType.HIGHLY_RECOMMENDED)
        recommended = sum(1 for r in results if r.recommendation == RecommendationType.RECOMMENDED)
        acceptable = sum(1 for r in results if r.recommendation == RecommendationType.ACCEPTABLE)
        not_rec = sum(1 for r in results if r.recommendation == RecommendationType.NOT_RECOMMENDED)
        disqualified = sum(1 for r in results if r.recommendation == RecommendationType.DISQUALIFIED)

        # Get TCO info
        tco_sorted = sorted(tco_calculations, key=lambda t: t.total_cost_of_ownership)
        best_tco = tco_sorted[0] if tco_sorted else None

        # Get compliance info
        compliant_count = sum(1 for c in compliance_checks if c.is_compliant)

        summary_parts = [
            f"## Executive Summary\n",
            f"**Evaluation:** {evaluation.name}\n",
            f"**Total Vendors Evaluated:** {len(results)}\n\n",
        ]

        if top_vendor:
            summary_parts.append(
                f"### Top Recommendation\n"
                f"**{top_vendor.vendor_name}** is ranked #1 with a weighted score of "
                f"**{top_vendor.total_weighted_score:.2f}/100**.\n\n"
            )

        summary_parts.append(
            f"### Recommendation Breakdown\n"
            f"- Highly Recommended: {highly_rec}\n"
            f"- Recommended: {recommended}\n"
            f"- Acceptable: {acceptable}\n"
            f"- Not Recommended: {not_rec}\n"
            f"- Disqualified: {disqualified}\n\n"
        )

        if best_tco:
            summary_parts.append(
                f"### Total Cost of Ownership\n"
                f"**{best_tco.vendor_name}** offers the best TCO at "
                f"**${best_tco.total_cost_of_ownership:,.2f}** "
                f"(${best_tco.tco_per_year:,.2f}/year).\n\n"
            )

        summary_parts.append(
            f"### Compliance Status\n"
            f"**{compliant_count}/{len(compliance_checks)}** vendors meet all compliance requirements.\n"
        )

        return "".join(summary_parts)

    def _generate_recommendations(
        self,
        results: list[TBEResult],
        tco_calculations: list[TCOCalculation],
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if not results:
            return ["No recommendations available - no vendors evaluated."]

        # Sort by rank
        ranked = sorted(results, key=lambda r: r.rank)

        # Primary recommendation
        if ranked[0]:
            top = ranked[0]
            recommendations.append(
                f"RECOMMENDED: Award contract to {top.vendor_name} based on highest "
                f"weighted score ({top.total_weighted_score:.2f}/100)."
            )

        # Runner-up recommendation
        if len(ranked) >= 2:
            runner = ranked[1]
            recommendations.append(
                f"ALTERNATIVE: Consider {runner.vendor_name} as backup option "
                f"(score: {runner.total_weighted_score:.2f}/100)."
            )

        # TCO recommendation
        if tco_calculations:
            tco_sorted = sorted(tco_calculations, key=lambda t: t.total_cost_of_ownership)
            best_tco = tco_sorted[0]
            recommendations.append(
                f"COST ANALYSIS: {best_tco.vendor_name} offers the lowest Total Cost of Ownership "
                f"at ${best_tco.total_cost_of_ownership:,.2f}."
            )

        # Quality recommendation
        quality_sorted = sorted(results, key=lambda r: r.quality_score, reverse=True)
        if quality_sorted[0].quality_score >= 90:
            recommendations.append(
                f"QUALITY LEADER: {quality_sorted[0].vendor_name} demonstrates exceptional "
                f"quality performance ({quality_sorted[0].quality_score:.1f}/100)."
            )

        # Delivery recommendation
        delivery_sorted = sorted(results, key=lambda r: r.delivery_score, reverse=True)
        if delivery_sorted[0].delivery_score >= 90:
            recommendations.append(
                f"FASTEST DELIVERY: {delivery_sorted[0].vendor_name} offers the best "
                f"delivery performance ({delivery_sorted[0].delivery_score:.1f}/100)."
            )

        # Risk warnings
        disqualified = [r for r in results if r.recommendation == RecommendationType.DISQUALIFIED]
        if disqualified:
            names = ", ".join(r.vendor_name for r in disqualified)
            recommendations.append(
                f"WARNING: {len(disqualified)} vendor(s) disqualified due to compliance issues: {names}."
            )

        return recommendations

    def save_chart_to_file(
        self,
        chart_base64: str,
        filename: str,
    ) -> str:
        """
        Save a base64 encoded chart to a file.

        Args:
            chart_base64: Base64 encoded image
            filename: Output filename

        Returns:
            Full path to saved file
        """
        if not chart_base64:
            return ""

        # Remove data URL prefix
        if "base64," in chart_base64:
            chart_base64 = chart_base64.split("base64,")[1]

        img_data = base64.b64decode(chart_base64)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "wb") as f:
            f.write(img_data)

        return filepath

    def export_report_json(
        self,
        report: TBEReport,
        filename: str = "tbe_report.json",
    ) -> str:
        """
        Export report to JSON file.

        Args:
            report: The TBE report
            filename: Output filename

        Returns:
            Full path to saved file
        """
        import json

        filepath = os.path.join(self.output_dir, filename)

        # Convert to serializable dict (excluding base64 charts for smaller file)
        report_dict = {
            "evaluation_name": report.evaluation.name,
            "evaluation_id": str(report.evaluation.id),
            "generated_at": report.generated_at.isoformat(),
            "generated_by": report.generated_by,
            "executive_summary": report.executive_summary,
            "recommendations": report.recommendations,
            "results": [
                {
                    "vendor_name": r.vendor_name,
                    "rank": r.rank,
                    "total_score": r.total_weighted_score,
                    "recommendation": r.recommendation.value,
                    "price_score": r.price_score,
                    "quality_score": r.quality_score,
                    "delivery_score": r.delivery_score,
                    "compliance_score": r.compliance_score,
                }
                for r in report.evaluation.results
            ],
            "tco_summary": [
                {
                    "vendor_name": t.vendor_name,
                    "total_tco": t.total_cost_of_ownership,
                    "tco_rank": t.tco_rank,
                }
                for t in report.tco_summary
            ],
            "compliance_summary": [
                {
                    "vendor_name": c.vendor_name,
                    "is_compliant": c.is_compliant,
                    "overall_score": c.overall_compliance_score,
                }
                for c in report.compliance_summary
            ],
        }

        with open(filepath, "w") as f:
            json.dump(report_dict, f, indent=2)

        return filepath
