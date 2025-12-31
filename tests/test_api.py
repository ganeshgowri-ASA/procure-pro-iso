"""
Tests for API endpoints.

Comprehensive API testing for TBE scoring engine endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health and root endpoints."""

    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "Procure-Pro-ISO"

    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
class TestVendorEndpoints:
    """Test vendor management endpoints."""

    async def test_create_vendor(self, async_client: AsyncClient):
        """Test creating a vendor."""
        vendor_data = {
            "name": "Test Vendor Inc.",
            "code": "TEST-001",
            "email": "test@vendor.com",
            "country": "USA",
            "industry": "Manufacturing",
            "certifications": ["ISO 9001:2015"],
            "iso_standards": ["ISO 9001"],
        }

        response = await async_client.post("/api/v1/vendors/", json=vendor_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == vendor_data["name"]
        assert data["code"] == vendor_data["code"]
        assert "id" in data

    async def test_list_vendors(self, async_client: AsyncClient):
        """Test listing vendors."""
        # First create a vendor
        vendor_data = {
            "name": "List Test Vendor",
            "code": "LIST-001",
        }
        await async_client.post("/api/v1/vendors/", json=vendor_data)

        response = await async_client.get("/api/v1/vendors/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_vendor(self, async_client: AsyncClient):
        """Test getting a specific vendor."""
        # Create vendor first
        vendor_data = {
            "name": "Get Test Vendor",
            "code": "GET-001",
        }
        create_response = await async_client.post("/api/v1/vendors/", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await async_client.get(f"/api/v1/vendors/{vendor_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == vendor_id

    async def test_get_nonexistent_vendor(self, async_client: AsyncClient):
        """Test getting a vendor that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(f"/api/v1/vendors/{fake_id}")

        assert response.status_code == 404

    async def test_duplicate_vendor_code(self, async_client: AsyncClient):
        """Test that duplicate vendor codes are rejected."""
        vendor_data = {
            "name": "Duplicate Test",
            "code": "DUP-001",
        }

        # Create first vendor
        await async_client.post("/api/v1/vendors/", json=vendor_data)

        # Try to create duplicate
        response = await async_client.post("/api/v1/vendors/", json=vendor_data)

        assert response.status_code == 400


@pytest.mark.asyncio
class TestTBEEndpoints:
    """Test TBE evaluation endpoints."""

    async def test_list_iso_standards(self, async_client: AsyncClient):
        """Test listing supported ISO standards."""
        response = await async_client.get("/api/v1/tbe/iso-standards")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all("code" in item and "name" in item for item in data)

    async def test_create_evaluation(self, async_client: AsyncClient):
        """Test creating a TBE evaluation."""
        eval_data = {
            "name": "Test Evaluation 2024",
            "description": "Test evaluation for API testing",
            "project_reference": "TEST-PROJ-001",
            "criteria_weights": {
                "price": 0.40,
                "quality": 0.25,
                "delivery": 0.20,
                "compliance": 0.15,
            },
            "required_iso_standards": ["ISO_9001"],
            "required_certifications": [],
        }

        response = await async_client.post("/api/v1/tbe/evaluations", json=eval_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == eval_data["name"]
        assert "id" in data

    async def test_calculate_score_preview(self, async_client: AsyncClient):
        """Test score calculation preview."""
        request_data = {
            "weights": {
                "price": 0.40,
                "quality": 0.25,
                "delivery": 0.20,
                "compliance": 0.15,
            },
            "price_score": 80.0,
            "quality_score": 90.0,
            "delivery_score": 85.0,
            "compliance_score": 100.0,
        }

        response = await async_client.post("/api/v1/tbe/calculate-score", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "total_weighted_score" in data
        assert "weighted_scores" in data

        # Verify calculation
        expected = (80 * 0.40) + (90 * 0.25) + (85 * 0.20) + (100 * 0.15)
        assert data["total_weighted_score"] == pytest.approx(expected, 0.01)

    async def test_invalid_weights_rejected(self, async_client: AsyncClient):
        """Test that invalid weights are rejected."""
        request_data = {
            "weights": {
                "price": 0.50,
                "quality": 0.30,
                "delivery": 0.20,
                "compliance": 0.20,  # Sum = 1.2
            },
            "price_score": 80.0,
            "quality_score": 90.0,
            "delivery_score": 85.0,
            "compliance_score": 100.0,
        }

        response = await async_client.post("/api/v1/tbe/calculate-score", json=request_data)

        assert response.status_code == 400

    async def test_create_bid(self, async_client: AsyncClient):
        """Test creating a vendor bid."""
        # First create a vendor
        vendor_data = {"name": "Bid Test Vendor", "code": "BID-TEST-001"}
        vendor_response = await async_client.post("/api/v1/vendors/", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        bid_data = {
            "vendor_id": vendor_id,
            "bid_reference": "BID-2024-001",
            "unit_price": 10000.00,
            "quantity": 5,
            "currency": "USD",
            "shipping_cost": 500.00,
            "installation_cost": 1000.00,
            "training_cost": 500.00,
            "maintenance_cost_annual": 1200.00,
            "warranty_years": 2,
            "expected_lifespan_years": 7,
            "delivery_days": 30,
            "certifications": ["ISO 9001:2015"],
            "iso_compliance": ["ISO 9001"],
            "quality_score": 85.0,
            "past_performance_score": 80.0,
        }

        response = await async_client.post("/api/v1/tbe/bids", json=bid_data)

        assert response.status_code == 201
        data = response.json()
        assert data["bid_reference"] == bid_data["bid_reference"]
        assert data["total_price"] == bid_data["unit_price"] * bid_data["quantity"]


@pytest.mark.asyncio
class TestReportEndpoints:
    """Test report generation endpoints."""

    async def test_get_weight_templates(self, async_client: AsyncClient):
        """Test getting weight templates."""
        response = await async_client.get("/api/v1/reports/templates/weights")

        assert response.status_code == 200
        data = response.json()

        # Should have predefined templates
        assert "balanced" in data
        assert "cost_focused" in data
        assert "quality_focused" in data
        assert "iso_default" in data

        # Verify template structure
        for template_name, template in data.items():
            assert "description" in template
            assert "weights" in template
            weights = template["weights"]
            # Weights should sum to 1.0
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.0001

    async def test_report_requires_evaluation(self, async_client: AsyncClient):
        """Test that report requires a valid evaluation."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(f"/api/v1/reports/evaluations/{fake_id}")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestCriteriaEndpoints:
    """Test evaluation criteria endpoints."""

    async def test_create_custom_criteria(self, async_client: AsyncClient):
        """Test creating custom evaluation criteria."""
        criteria_data = {
            "name": "Technical Support Quality",
            "code": "TECH-SUPPORT",
            "category": "support",
            "description": "Evaluates vendor technical support capabilities",
            "weight": 0.10,
            "max_score": 100.0,
            "is_mandatory": False,
        }

        response = await async_client.post("/api/v1/tbe/criteria", json=criteria_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == criteria_data["name"]
        assert data["code"] == criteria_data["code"]

    async def test_list_criteria(self, async_client: AsyncClient):
        """Test listing evaluation criteria."""
        response = await async_client.get("/api/v1/tbe/criteria")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
