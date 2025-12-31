"""
Comparison Matrix Engine - Multi-criteria vendor comparison.

Creates comparison matrices for visual vendor evaluation across all criteria.
"""

from typing import Optional
from uuid import UUID

from src.models.tbe import (
    ComparisonMatrix,
    ComparisonMatrixCell,
    ComparisonMatrixRow,
    CriteriaCategory,
    TBEResult,
)


class ComparisonMatrixEngine:
    """
    Multi-criteria comparison matrix generator.

    Creates structured comparison matrices showing how vendors
    compare across all evaluation criteria.
    """

    def __init__(self):
        """Initialize the comparison matrix engine."""
        self._category_order = [
            CriteriaCategory.PRICE,
            CriteriaCategory.QUALITY,
            CriteriaCategory.DELIVERY,
            CriteriaCategory.COMPLIANCE,
            CriteriaCategory.TECHNICAL,
            CriteriaCategory.EXPERIENCE,
            CriteriaCategory.SUPPORT,
            CriteriaCategory.CUSTOM,
        ]

    def generate_matrix(
        self,
        evaluation_id: UUID,
        evaluation_name: str,
        results: list[TBEResult],
    ) -> ComparisonMatrix:
        """
        Generate a comparison matrix from TBE results.

        Args:
            evaluation_id: The evaluation ID
            evaluation_name: Name of the evaluation
            results: List of TBE results for all vendors

        Returns:
            ComparisonMatrix with vendor comparisons across all criteria
        """
        if not results:
            raise ValueError("Cannot generate matrix without results")

        # Extract vendor info
        vendor_names = [r.vendor_name for r in results]
        vendor_ids = [r.vendor_id for r in results]

        # Build matrix rows
        rows = self._build_criteria_rows(results)

        # Build total scores row
        total_scores = self._build_total_scores(results)

        # Identify best and worst
        sorted_by_score = sorted(results, key=lambda r: r.total_weighted_score, reverse=True)
        best = sorted_by_score[0] if sorted_by_score else None
        worst = sorted_by_score[-1] if len(sorted_by_score) > 1 else None

        return ComparisonMatrix(
            evaluation_id=evaluation_id,
            evaluation_name=evaluation_name,
            vendor_count=len(results),
            criteria_count=len(rows),
            vendor_names=vendor_names,
            vendor_ids=vendor_ids,
            rows=rows,
            total_scores=total_scores,
            best_vendor_id=best.vendor_id if best else None,
            best_vendor_name=best.vendor_name if best else None,
            worst_vendor_id=worst.vendor_id if worst and worst != best else None,
            worst_vendor_name=worst.vendor_name if worst and worst != best else None,
        )

    def _build_criteria_rows(self, results: list[TBEResult]) -> list[ComparisonMatrixRow]:
        """Build matrix rows for each criteria."""
        rows = []

        # Get all unique criteria from first result (assuming all have same criteria)
        if not results or not results[0].scores:
            return rows

        criteria_list = results[0].scores

        for criteria in criteria_list:
            # Get scores for this criteria across all vendors
            criteria_scores = []
            for result in results:
                score = next(
                    (s for s in result.scores if s.criteria_name == criteria.criteria_name),
                    None,
                )
                if score:
                    criteria_scores.append(
                        {
                            "vendor_id": result.vendor_id,
                            "vendor_name": result.vendor_name,
                            "raw_score": score.raw_score,
                            "weighted_score": score.weighted_score,
                        }
                    )

            # Determine best and worst for this criteria
            if criteria_scores:
                max_score = max(s["raw_score"] for s in criteria_scores)
                min_score = min(s["raw_score"] for s in criteria_scores)

                cells = []
                for idx, score_data in enumerate(criteria_scores):
                    is_best = score_data["raw_score"] == max_score
                    is_worst = score_data["raw_score"] == min_score and max_score != min_score

                    # Rank by score
                    sorted_scores = sorted(
                        criteria_scores, key=lambda x: x["raw_score"], reverse=True
                    )
                    rank = next(
                        i + 1
                        for i, s in enumerate(sorted_scores)
                        if s["vendor_id"] == score_data["vendor_id"]
                    )

                    cells.append(
                        ComparisonMatrixCell(
                            vendor_id=score_data["vendor_id"],
                            vendor_name=score_data["vendor_name"],
                            value=score_data["raw_score"],
                            display_value=f"{score_data['raw_score']:.1f}",
                            is_best=is_best,
                            is_worst=is_worst,
                            rank=rank,
                        )
                    )

                rows.append(
                    ComparisonMatrixRow(
                        criteria_name=criteria.criteria_name,
                        criteria_category=criteria.criteria_category,
                        weight=criteria.weight,
                        cells=cells,
                    )
                )

        return rows

    def _build_total_scores(self, results: list[TBEResult]) -> list[ComparisonMatrixCell]:
        """Build the total scores summary row."""
        if not results:
            return []

        # Get max and min total scores
        max_total = max(r.total_weighted_score for r in results)
        min_total = min(r.total_weighted_score for r in results)

        # Sort for ranking
        sorted_results = sorted(results, key=lambda r: r.total_weighted_score, reverse=True)

        cells = []
        for result in results:
            is_best = result.total_weighted_score == max_total
            is_worst = result.total_weighted_score == min_total and max_total != min_total

            rank = next(
                i + 1
                for i, r in enumerate(sorted_results)
                if r.vendor_id == result.vendor_id
            )

            cells.append(
                ComparisonMatrixCell(
                    vendor_id=result.vendor_id,
                    vendor_name=result.vendor_name,
                    value=result.total_weighted_score,
                    display_value=f"{result.total_weighted_score:.2f}",
                    is_best=is_best,
                    is_worst=is_worst,
                    rank=rank,
                )
            )

        return cells

    def matrix_to_dict(self, matrix: ComparisonMatrix) -> dict:
        """
        Convert comparison matrix to dictionary for JSON serialization.

        Args:
            matrix: The comparison matrix

        Returns:
            Dictionary representation
        """
        return {
            "evaluation_id": str(matrix.evaluation_id),
            "evaluation_name": matrix.evaluation_name,
            "vendor_count": matrix.vendor_count,
            "criteria_count": matrix.criteria_count,
            "vendors": [
                {"id": str(vid), "name": name}
                for vid, name in zip(matrix.vendor_ids, matrix.vendor_names)
            ],
            "criteria_scores": [
                {
                    "criteria": row.criteria_name,
                    "category": row.criteria_category.value,
                    "weight": row.weight,
                    "scores": [
                        {
                            "vendor_id": str(cell.vendor_id),
                            "vendor_name": cell.vendor_name,
                            "score": cell.value,
                            "display": cell.display_value,
                            "is_best": cell.is_best,
                            "is_worst": cell.is_worst,
                            "rank": cell.rank,
                        }
                        for cell in row.cells
                    ],
                }
                for row in matrix.rows
            ],
            "total_scores": [
                {
                    "vendor_id": str(cell.vendor_id),
                    "vendor_name": cell.vendor_name,
                    "total": cell.value,
                    "display": cell.display_value,
                    "is_best": cell.is_best,
                    "is_worst": cell.is_worst,
                    "rank": cell.rank,
                }
                for cell in matrix.total_scores
            ],
            "best_vendor": {
                "id": str(matrix.best_vendor_id) if matrix.best_vendor_id else None,
                "name": matrix.best_vendor_name,
            },
            "worst_vendor": {
                "id": str(matrix.worst_vendor_id) if matrix.worst_vendor_id else None,
                "name": matrix.worst_vendor_name,
            },
        }

    def get_criteria_summary(
        self,
        matrix: ComparisonMatrix,
        category: Optional[CriteriaCategory] = None,
    ) -> dict:
        """
        Get summary statistics for criteria.

        Args:
            matrix: The comparison matrix
            category: Optional category filter

        Returns:
            Summary statistics dictionary
        """
        rows = matrix.rows
        if category:
            rows = [r for r in rows if r.criteria_category == category]

        summary = {
            "criteria_count": len(rows),
            "categories": {},
        }

        for row in rows:
            cat = row.criteria_category.value
            if cat not in summary["categories"]:
                summary["categories"][cat] = {
                    "criteria": [],
                    "average_score": 0.0,
                    "max_score": 0.0,
                    "min_score": 0.0,
                }

            scores = [c.value for c in row.cells]
            summary["categories"][cat]["criteria"].append(
                {
                    "name": row.criteria_name,
                    "weight": row.weight,
                    "avg": sum(scores) / len(scores) if scores else 0,
                    "max": max(scores) if scores else 0,
                    "min": min(scores) if scores else 0,
                }
            )

        # Calculate category averages
        for cat_data in summary["categories"].values():
            criteria = cat_data["criteria"]
            if criteria:
                cat_data["average_score"] = sum(c["avg"] for c in criteria) / len(criteria)
                cat_data["max_score"] = max(c["max"] for c in criteria)
                cat_data["min_score"] = min(c["min"] for c in criteria)

        return summary
