"""Report generation API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from src.models.tbe import TBEReport
from src.services.report_generator import TBEReportGenerator
from src.api.routes.tbe import get_evaluations_dict

router = APIRouter()

# Report generator instance
report_generator = TBEReportGenerator()


@router.get("/evaluations/{evaluation_id}", response_model=dict)
async def generate_evaluation_report(
    evaluation_id: UUID,
    include_charts: bool = Query(True, description="Include chart images"),
    generated_by: Optional[str] = Query(None, description="Report generator name"),
) -> dict:
    """
    Generate a comprehensive TBE report for an evaluation.

    The report includes:
    - Executive summary
    - Score comparisons
    - TCO analysis
    - Compliance summary
    - Recommendations
    - Visual charts (optional)
    """
    evaluations = get_evaluations_dict()
    evaluation = evaluations.get(evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    if not evaluation.comparison_matrix:
        raise HTTPException(status_code=400, detail="Comparison matrix not available")

    # Extract TCO and compliance data
    tco_calculations = [r.tco_calculation for r in evaluation.results if r.tco_calculation]
    compliance_checks = [r.compliance_check for r in evaluation.results if r.compliance_check]

    # Generate report
    report = report_generator.generate_report(
        evaluation=evaluation,
        results=evaluation.results,
        matrix=evaluation.comparison_matrix,
        tco_calculations=tco_calculations,
        compliance_checks=compliance_checks,
        generated_by=generated_by,
    )

    # Build response
    response = {
        "evaluation_id": str(evaluation_id),
        "evaluation_name": evaluation.name,
        "generated_at": report.generated_at.isoformat(),
        "generated_by": report.generated_by,
        "executive_summary": report.executive_summary,
        "recommendations": report.recommendations,
        "results_summary": [
            {
                "rank": r.rank,
                "vendor_id": str(r.vendor_id),
                "vendor_name": r.vendor_name,
                "total_score": round(r.total_weighted_score, 2),
                "recommendation": r.recommendation.value,
                "scores": {
                    "price": round(r.price_score, 2),
                    "quality": round(r.quality_score, 2),
                    "delivery": round(r.delivery_score, 2),
                    "compliance": round(r.compliance_score, 2),
                },
            }
            for r in evaluation.results
        ],
        "tco_summary": [
            {
                "vendor_name": t.vendor_name,
                "total_tco": round(t.total_cost_of_ownership, 2),
                "tco_rank": t.tco_rank,
                "acquisition_cost": round(t.acquisition_cost, 2),
                "operational_cost": round(t.operational_cost, 2),
            }
            for t in tco_calculations
        ],
        "compliance_summary": [
            {
                "vendor_name": c.vendor_name,
                "is_compliant": c.is_compliant,
                "overall_score": round(c.overall_compliance_score, 2),
                "missing_standards": c.missing_iso_standards,
            }
            for c in compliance_checks
        ],
    }

    if include_charts:
        response["charts"] = {
            "score_chart": report.score_chart,
            "tco_chart": report.tco_chart,
            "radar_chart": report.radar_chart,
        }

    return response


@router.get("/evaluations/{evaluation_id}/charts/scores")
async def get_score_chart(evaluation_id: UUID) -> dict:
    """Get score comparison chart for an evaluation."""
    evaluations = get_evaluations_dict()
    evaluation = evaluations.get(evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    chart_base64 = report_generator._generate_score_chart(evaluation.results)

    return {
        "evaluation_id": str(evaluation_id),
        "chart_type": "score_comparison",
        "image": chart_base64,
        "format": "png",
    }


@router.get("/evaluations/{evaluation_id}/charts/tco")
async def get_tco_chart(evaluation_id: UUID) -> dict:
    """Get TCO comparison chart for an evaluation."""
    evaluations = get_evaluations_dict()
    evaluation = evaluations.get(evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    tco_calculations = [r.tco_calculation for r in evaluation.results if r.tco_calculation]

    if not tco_calculations:
        raise HTTPException(status_code=400, detail="No TCO data available")

    chart_base64 = report_generator._generate_tco_chart(tco_calculations)

    return {
        "evaluation_id": str(evaluation_id),
        "chart_type": "tco_comparison",
        "image": chart_base64,
        "format": "png",
    }


@router.get("/evaluations/{evaluation_id}/charts/radar")
async def get_radar_chart(evaluation_id: UUID) -> dict:
    """Get radar chart for multi-criteria comparison."""
    evaluations = get_evaluations_dict()
    evaluation = evaluations.get(evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    chart_base64 = report_generator._generate_radar_chart(evaluation.results)

    return {
        "evaluation_id": str(evaluation_id),
        "chart_type": "radar_comparison",
        "image": chart_base64,
        "format": "png",
    }


@router.get("/evaluations/{evaluation_id}/charts/compliance")
async def get_compliance_heatmap(evaluation_id: UUID) -> dict:
    """Get compliance heatmap for an evaluation."""
    evaluations = get_evaluations_dict()
    evaluation = evaluations.get(evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    compliance_checks = [r.compliance_check for r in evaluation.results if r.compliance_check]

    if not compliance_checks:
        raise HTTPException(status_code=400, detail="No compliance data available")

    chart_base64 = report_generator.generate_compliance_heatmap(compliance_checks)

    return {
        "evaluation_id": str(evaluation_id),
        "chart_type": "compliance_heatmap",
        "image": chart_base64,
        "format": "png",
    }


@router.post("/evaluations/{evaluation_id}/export")
async def export_report(
    evaluation_id: UUID,
    format: str = Query("json", enum=["json"], description="Export format"),
    generated_by: Optional[str] = Query(None),
) -> dict:
    """
    Export evaluation report to file.

    Currently supports JSON format. PDF export coming soon.
    """
    evaluations = get_evaluations_dict()
    evaluation = evaluations.get(evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    if not evaluation.results:
        raise HTTPException(status_code=400, detail="Evaluation has not been executed yet")

    if not evaluation.comparison_matrix:
        raise HTTPException(status_code=400, detail="Comparison matrix not available")

    tco_calculations = [r.tco_calculation for r in evaluation.results if r.tco_calculation]
    compliance_checks = [r.compliance_check for r in evaluation.results if r.compliance_check]

    report = report_generator.generate_report(
        evaluation=evaluation,
        results=evaluation.results,
        matrix=evaluation.comparison_matrix,
        tco_calculations=tco_calculations,
        compliance_checks=compliance_checks,
        generated_by=generated_by,
    )

    if format == "json":
        filename = f"tbe_report_{evaluation_id}.json"
        filepath = report_generator.export_report_json(report, filename)
        return {
            "message": "Report exported successfully",
            "format": format,
            "filepath": filepath,
        }

    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.get("/templates/weights")
async def get_weight_templates() -> dict:
    """Get predefined weight templates for common evaluation scenarios."""
    return {
        "balanced": {
            "description": "Balanced evaluation across all criteria",
            "weights": {
                "price": 0.25,
                "quality": 0.25,
                "delivery": 0.25,
                "compliance": 0.25,
            },
        },
        "cost_focused": {
            "description": "Cost-driven evaluation prioritizing price",
            "weights": {
                "price": 0.50,
                "quality": 0.20,
                "delivery": 0.15,
                "compliance": 0.15,
            },
        },
        "quality_focused": {
            "description": "Quality-driven evaluation for critical applications",
            "weights": {
                "price": 0.20,
                "quality": 0.45,
                "delivery": 0.15,
                "compliance": 0.20,
            },
        },
        "time_critical": {
            "description": "Time-sensitive evaluation prioritizing delivery",
            "weights": {
                "price": 0.25,
                "quality": 0.20,
                "delivery": 0.40,
                "compliance": 0.15,
            },
        },
        "compliance_focused": {
            "description": "Regulatory-driven evaluation for strict compliance needs",
            "weights": {
                "price": 0.20,
                "quality": 0.25,
                "delivery": 0.15,
                "compliance": 0.40,
            },
        },
        "iso_default": {
            "description": "Default ISO procurement weights (Price 40%, Quality 25%, Delivery 20%, Compliance 15%)",
            "weights": {
                "price": 0.40,
                "quality": 0.25,
                "delivery": 0.20,
                "compliance": 0.15,
            },
        },
    }
