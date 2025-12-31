"""Tests for Vendor Management API endpoints."""

import pytest
from httpx import AsyncClient


class TestVendorCategories:
    """Tests for vendor category endpoints."""

    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient, category_data):
        """Test creating a vendor category."""
        response = await client.post("/api/v1/categories", json=category_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert data["is_active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_categories(self, client: AsyncClient, category_data):
        """Test listing vendor categories."""
        # Create a category first
        await client.post("/api/v1/categories", json=category_data)

        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_category(self, client: AsyncClient, category_data):
        """Test getting a specific category."""
        # Create a category first
        create_response = await client.post("/api/v1/categories", json=category_data)
        category_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == category_data["name"]

    @pytest.mark.asyncio
    async def test_update_category(self, client: AsyncClient, category_data):
        """Test updating a category."""
        # Create a category first
        create_response = await client.post("/api/v1/categories", json=category_data)
        category_id = create_response.json()["id"]

        update_data = {"name": "Updated Electronics", "description": "Updated description"}
        response = await client.put(f"/api/v1/categories/{category_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_delete_category(self, client: AsyncClient, category_data):
        """Test deleting a category."""
        # Create a category first
        create_response = await client.post("/api/v1/categories", json=category_data)
        category_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/categories/{category_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/categories/{category_id}")
        assert get_response.status_code == 404


class TestVendorCRUD:
    """Tests for vendor CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_vendor(self, client: AsyncClient, vendor_data):
        """Test creating a vendor."""
        response = await client.post("/api/v1/vendors", json=vendor_data)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == vendor_data["code"]
        assert data["name"] == vendor_data["name"]
        assert data["email"] == vendor_data["email"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_vendor(self, client: AsyncClient, vendor_data):
        """Test vendor registration."""
        vendor_data["code"] = "VND002"  # Use different code
        response = await client.post("/api/v1/vendors/register", json=vendor_data)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_vendors(self, client: AsyncClient, vendor_data):
        """Test listing vendors with pagination."""
        # Create a vendor first
        await client.post("/api/v1/vendors", json=vendor_data)

        response = await client.get("/api/v1/vendors")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_vendors_with_filters(self, client: AsyncClient, vendor_data):
        """Test listing vendors with filters."""
        # Create a vendor first
        await client.post("/api/v1/vendors", json=vendor_data)

        response = await client.get("/api/v1/vendors", params={"status": "pending"})
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_vendors_with_search(self, client: AsyncClient, vendor_data):
        """Test listing vendors with search."""
        # Create a vendor first
        await client.post("/api/v1/vendors", json=vendor_data)

        response = await client.get("/api/v1/vendors", params={"search": "Test Vendor"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_get_vendor(self, client: AsyncClient, vendor_data):
        """Test getting a specific vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/vendors/{vendor_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == vendor_id
        assert data["code"] == vendor_data["code"]

    @pytest.mark.asyncio
    async def test_update_vendor(self, client: AsyncClient, vendor_data):
        """Test updating a vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        update_data = {"name": "Updated Vendor Inc.", "phone": "+1-555-0200"}
        response = await client.put(f"/api/v1/vendors/{vendor_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["phone"] == update_data["phone"]

    @pytest.mark.asyncio
    async def test_activate_vendor(self, client: AsyncClient, vendor_data):
        """Test activating a vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await client.post(f"/api/v1/vendors/{vendor_id}/activate")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_delete_vendor(self, client: AsyncClient, vendor_data):
        """Test deleting a vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/vendors/{vendor_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/vendors/{vendor_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_duplicate_vendor_code(self, client: AsyncClient, vendor_data):
        """Test that duplicate vendor codes are rejected."""
        # Create a vendor first
        await client.post("/api/v1/vendors", json=vendor_data)

        # Try to create another vendor with the same code
        response = await client.post("/api/v1/vendors", json=vendor_data)
        assert response.status_code == 409


class TestVendorCertifications:
    """Tests for vendor certification endpoints."""

    @pytest.mark.asyncio
    async def test_add_certification(
        self, client: AsyncClient, vendor_data, certification_data
    ):
        """Test adding a certification to a vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await client.post(
            f"/api/v1/vendors/{vendor_id}/certifications",
            json=certification_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["certification_type"] == certification_data["certification_type"]
        assert data["is_verified"] is False

    @pytest.mark.asyncio
    async def test_list_certifications(
        self, client: AsyncClient, vendor_data, certification_data
    ):
        """Test listing vendor certifications."""
        # Create a vendor and add certification
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]
        await client.post(
            f"/api/v1/vendors/{vendor_id}/certifications",
            json=certification_data,
        )

        response = await client.get(f"/api/v1/vendors/{vendor_id}/certifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_verify_certification(
        self, client: AsyncClient, vendor_data, certification_data
    ):
        """Test verifying a certification."""
        # Create a vendor and add certification
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]
        cert_response = await client.post(
            f"/api/v1/vendors/{vendor_id}/certifications",
            json=certification_data,
        )
        cert_id = cert_response.json()["id"]

        response = await client.post(
            f"/api/v1/vendors/certifications/{cert_id}/verify",
            params={"verified_by": "Quality Team"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_verified"] is True
        assert data["verified_by"] == "Quality Team"


class TestVendorContacts:
    """Tests for vendor contact endpoints."""

    @pytest.mark.asyncio
    async def test_add_contact(self, client: AsyncClient, vendor_data, contact_data):
        """Test adding a contact to a vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await client.post(
            f"/api/v1/vendors/{vendor_id}/contacts",
            json=contact_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == contact_data["name"]
        assert data["is_primary"] == contact_data["is_primary"]

    @pytest.mark.asyncio
    async def test_list_contacts(self, client: AsyncClient, vendor_data, contact_data):
        """Test listing vendor contacts."""
        # Create a vendor and add contact
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]
        await client.post(
            f"/api/v1/vendors/{vendor_id}/contacts",
            json=contact_data,
        )

        response = await client.get(f"/api/v1/vendors/{vendor_id}/contacts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestVendorRatings:
    """Tests for vendor rating endpoints."""

    @pytest.mark.asyncio
    async def test_add_rating(self, client: AsyncClient, vendor_data, rating_data):
        """Test adding a rating to a vendor."""
        # Create a vendor first
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]

        response = await client.post(
            f"/api/v1/vendors/{vendor_id}/ratings",
            json=rating_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["rating_period"] == rating_data["rating_period"]
        assert data["quality_rating"] == rating_data["quality_rating"]
        assert "overall_rating" in data

    @pytest.mark.asyncio
    async def test_get_performance_summary(
        self, client: AsyncClient, vendor_data, rating_data
    ):
        """Test getting vendor performance summary."""
        # Create a vendor and add rating
        create_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = create_response.json()["id"]
        await client.post(
            f"/api/v1/vendors/{vendor_id}/ratings",
            json=rating_data,
        )

        response = await client.get(f"/api/v1/vendors/{vendor_id}/performance")
        assert response.status_code == 200
        data = response.json()
        assert "average_overall_rating" in data
        assert "total_orders_placed" in data
        assert "on_time_delivery_rate" in data
