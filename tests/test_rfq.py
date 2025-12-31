"""Tests for RFQ Workflow API endpoints."""

import pytest
from httpx import AsyncClient


class TestRFQCRUD:
    """Tests for RFQ CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_rfq(self, client: AsyncClient, rfq_data):
        """Test creating an RFQ."""
        response = await client.post("/api/v1/rfq", json=rfq_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == rfq_data["title"]
        assert data["status"] == "draft"
        assert "rfq_number" in data
        assert data["rfq_number"].startswith("RFQ-")

    @pytest.mark.asyncio
    async def test_list_rfqs(self, client: AsyncClient, rfq_data):
        """Test listing RFQs with pagination."""
        # Create an RFQ first
        await client.post("/api/v1/rfq", json=rfq_data)

        response = await client.get("/api/v1/rfq")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_rfqs_with_filters(self, client: AsyncClient, rfq_data):
        """Test listing RFQs with filters."""
        # Create an RFQ first
        await client.post("/api/v1/rfq", json=rfq_data)

        response = await client.get("/api/v1/rfq", params={"status": "draft"})
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "draft"

    @pytest.mark.asyncio
    async def test_get_rfq(self, client: AsyncClient, rfq_data):
        """Test getting a specific RFQ."""
        # Create an RFQ first
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/rfq/{rfq_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rfq_id
        assert data["title"] == rfq_data["title"]

    @pytest.mark.asyncio
    async def test_update_rfq(self, client: AsyncClient, rfq_data):
        """Test updating an RFQ."""
        # Create an RFQ first
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        update_data = {"title": "Updated Office Equipment Procurement", "priority": "high"}
        response = await client.put(f"/api/v1/rfq/{rfq_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["priority"] == update_data["priority"]

    @pytest.mark.asyncio
    async def test_delete_rfq(self, client: AsyncClient, rfq_data):
        """Test deleting an RFQ."""
        # Create an RFQ first
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/rfq/{rfq_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/rfq/{rfq_id}")
        assert get_response.status_code == 404


class TestRFQItems:
    """Tests for RFQ item endpoints."""

    @pytest.mark.asyncio
    async def test_add_rfq_item(self, client: AsyncClient, rfq_data, rfq_item_data):
        """Test adding an item to an RFQ."""
        # Create an RFQ first
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        response = await client.post(f"/api/v1/rfq/{rfq_id}/items", json=rfq_item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == rfq_item_data["name"]
        assert data["quantity"] == rfq_item_data["quantity"]
        assert data["item_number"] == rfq_item_data["item_number"]

    @pytest.mark.asyncio
    async def test_list_rfq_items(self, client: AsyncClient, rfq_data, rfq_item_data):
        """Test listing RFQ items."""
        # Create an RFQ and add item
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        await client.post(f"/api/v1/rfq/{rfq_id}/items", json=rfq_item_data)

        response = await client.get(f"/api/v1/rfq/{rfq_id}/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_update_rfq_item(self, client: AsyncClient, rfq_data, rfq_item_data):
        """Test updating an RFQ item."""
        # Create an RFQ and add item
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        item_response = await client.post(f"/api/v1/rfq/{rfq_id}/items", json=rfq_item_data)
        item_id = item_response.json()["id"]

        update_data = {"quantity": 20, "estimated_unit_price": 1200.0}
        response = await client.put(f"/api/v1/rfq/items/{item_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == update_data["quantity"]
        assert data["estimated_unit_price"] == update_data["estimated_unit_price"]

    @pytest.mark.asyncio
    async def test_delete_rfq_item(self, client: AsyncClient, rfq_data, rfq_item_data):
        """Test deleting an RFQ item."""
        # Create an RFQ and add item
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        item_response = await client.post(f"/api/v1/rfq/{rfq_id}/items", json=rfq_item_data)
        item_id = item_response.json()["id"]

        response = await client.delete(f"/api/v1/rfq/items/{item_id}")
        assert response.status_code == 204


class TestRFQWorkflow:
    """Tests for RFQ status workflow."""

    @pytest.mark.asyncio
    async def test_publish_rfq(
        self, client: AsyncClient, rfq_data, rfq_item_data, vendor_data
    ):
        """Test publishing an RFQ."""
        # Create vendor first
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create an RFQ with item and vendor invitation
        rfq_data["items"] = [rfq_item_data]
        rfq_data["vendor_ids"] = [vendor_id]
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        # Publish the RFQ
        response = await client.patch(
            f"/api/v1/rfq/{rfq_id}/status",
            json={"status": "published"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert data["published_at"] is not None

    @pytest.mark.asyncio
    async def test_cannot_publish_empty_rfq(self, client: AsyncClient, rfq_data):
        """Test that empty RFQ cannot be published."""
        # Create an RFQ without items or vendors
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        # Try to publish
        response = await client.patch(
            f"/api/v1/rfq/{rfq_id}/status",
            json={"status": "published"},
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_invalid_status_transition(
        self, client: AsyncClient, rfq_data, rfq_item_data, vendor_data
    ):
        """Test invalid status transition."""
        # Create vendor first
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create an RFQ
        rfq_data["items"] = [rfq_item_data]
        rfq_data["vendor_ids"] = [vendor_id]
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        # Try invalid transition: draft -> under_review (should fail)
        response = await client.patch(
            f"/api/v1/rfq/{rfq_id}/status",
            json={"status": "under_review"},
        )
        assert response.status_code == 400


class TestVendorInvitations:
    """Tests for vendor invitation endpoints."""

    @pytest.mark.asyncio
    async def test_invite_vendor(self, client: AsyncClient, rfq_data, vendor_data):
        """Test inviting a vendor to an RFQ."""
        # Create vendor first
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create an RFQ
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        # Invite vendor
        response = await client.post(
            f"/api/v1/rfq/{rfq_id}/invitations",
            json={"vendor_id": vendor_id},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["vendor_id"] == vendor_id
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_invitations(self, client: AsyncClient, rfq_data, vendor_data):
        """Test listing vendor invitations."""
        # Create vendor and invite them
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        await client.post(
            f"/api/v1/rfq/{rfq_id}/invitations",
            json={"vendor_id": vendor_id},
        )

        response = await client.get(f"/api/v1/rfq/{rfq_id}/invitations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_accept_invitation(self, client: AsyncClient, rfq_data, vendor_data):
        """Test accepting an invitation."""
        # Create vendor and invite them
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        invite_response = await client.post(
            f"/api/v1/rfq/{rfq_id}/invitations",
            json={"vendor_id": vendor_id},
        )
        invitation_id = invite_response.json()["id"]

        response = await client.post(f"/api/v1/rfq/invitations/{invitation_id}/accept")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_decline_invitation(self, client: AsyncClient, rfq_data, vendor_data):
        """Test declining an invitation."""
        # Create vendor and invite them
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]

        invite_response = await client.post(
            f"/api/v1/rfq/{rfq_id}/invitations",
            json={"vendor_id": vendor_id},
        )
        invitation_id = invite_response.json()["id"]

        response = await client.post(
            f"/api/v1/rfq/invitations/{invitation_id}/decline",
            params={"reason": "Not interested"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "declined"
        assert data["decline_reason"] == "Not interested"


class TestQuotations:
    """Tests for quotation endpoints."""

    @pytest.mark.asyncio
    async def test_create_quotation(
        self,
        client: AsyncClient,
        rfq_data,
        rfq_item_data,
        vendor_data,
        quotation_item_data,
    ):
        """Test creating a quotation."""
        # Create vendor
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create RFQ with item and invite vendor
        rfq_data["items"] = [rfq_item_data]
        rfq_data["vendor_ids"] = [vendor_id]
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        rfq_item_id = create_response.json()["items"][0]["id"]

        # Publish RFQ
        await client.patch(f"/api/v1/rfq/{rfq_id}/status", json={"status": "published"})

        # Create quotation
        quotation_item_data["rfq_item_id"] = rfq_item_id
        quotation_data = {
            "vendor_id": vendor_id,
            "discount_percentage": 5.0,
            "tax_percentage": 10.0,
            "shipping_cost": 100.0,
            "validity_days": 30,
            "delivery_days": 14,
            "items": [quotation_item_data],
        }
        response = await client.post(f"/api/v1/quotations/rfq/{rfq_id}", json=quotation_data)
        assert response.status_code == 201
        data = response.json()
        assert data["vendor_id"] == vendor_id
        assert data["status"] == "draft"
        assert "quotation_number" in data

    @pytest.mark.asyncio
    async def test_submit_quotation(
        self,
        client: AsyncClient,
        rfq_data,
        rfq_item_data,
        vendor_data,
        quotation_item_data,
    ):
        """Test submitting a quotation."""
        # Create vendor
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create RFQ with item and invite vendor
        rfq_data["items"] = [rfq_item_data]
        rfq_data["vendor_ids"] = [vendor_id]
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        rfq_item_id = create_response.json()["items"][0]["id"]

        # Publish RFQ
        await client.patch(f"/api/v1/rfq/{rfq_id}/status", json={"status": "published"})

        # Create quotation
        quotation_item_data["rfq_item_id"] = rfq_item_id
        quotation_data = {
            "vendor_id": vendor_id,
            "discount_percentage": 5.0,
            "tax_percentage": 10.0,
            "shipping_cost": 100.0,
            "validity_days": 30,
            "delivery_days": 14,
            "items": [quotation_item_data],
        }
        quote_response = await client.post(
            f"/api/v1/quotations/rfq/{rfq_id}",
            json=quotation_data,
        )
        quotation_id = quote_response.json()["id"]

        # Submit quotation
        response = await client.post(f"/api/v1/quotations/{quotation_id}/submit")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"
        assert data["submitted_at"] is not None

    @pytest.mark.asyncio
    async def test_evaluate_quotation(
        self,
        client: AsyncClient,
        rfq_data,
        rfq_item_data,
        vendor_data,
        quotation_item_data,
    ):
        """Test evaluating a quotation."""
        # Create vendor
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create RFQ with item and invite vendor
        rfq_data["items"] = [rfq_item_data]
        rfq_data["vendor_ids"] = [vendor_id]
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        rfq_item_id = create_response.json()["items"][0]["id"]

        # Publish RFQ
        await client.patch(f"/api/v1/rfq/{rfq_id}/status", json={"status": "published"})

        # Create and submit quotation
        quotation_item_data["rfq_item_id"] = rfq_item_id
        quotation_data = {
            "vendor_id": vendor_id,
            "discount_percentage": 5.0,
            "tax_percentage": 10.0,
            "shipping_cost": 100.0,
            "validity_days": 30,
            "delivery_days": 14,
            "items": [quotation_item_data],
        }
        quote_response = await client.post(
            f"/api/v1/quotations/rfq/{rfq_id}",
            json=quotation_data,
        )
        quotation_id = quote_response.json()["id"]
        await client.post(f"/api/v1/quotations/{quotation_id}/submit")

        # Evaluate quotation
        evaluation_data = {
            "technical_score": 85.0,
            "commercial_score": 90.0,
            "evaluation_notes": "Good overall proposal",
            "evaluated_by": "Procurement Team",
        }
        response = await client.post(
            f"/api/v1/quotations/{quotation_id}/evaluate",
            json=evaluation_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "under_evaluation"
        assert data["technical_score"] == evaluation_data["technical_score"]
        assert data["commercial_score"] == evaluation_data["commercial_score"]
        assert data["overall_score"] == 87.5  # Average of technical and commercial


class TestQuoteComparison:
    """Tests for quote comparison endpoint."""

    @pytest.mark.asyncio
    async def test_compare_quotes(
        self,
        client: AsyncClient,
        rfq_data,
        rfq_item_data,
        vendor_data,
        quotation_item_data,
    ):
        """Test quote comparison endpoint."""
        # Create vendor
        vendor_response = await client.post("/api/v1/vendors", json=vendor_data)
        vendor_id = vendor_response.json()["id"]

        # Create RFQ with item and invite vendor
        rfq_data["items"] = [rfq_item_data]
        rfq_data["vendor_ids"] = [vendor_id]
        create_response = await client.post("/api/v1/rfq", json=rfq_data)
        rfq_id = create_response.json()["id"]
        rfq_item_id = create_response.json()["items"][0]["id"]

        # Publish RFQ
        await client.patch(f"/api/v1/rfq/{rfq_id}/status", json={"status": "published"})

        # Create and submit quotation
        quotation_item_data["rfq_item_id"] = rfq_item_id
        quotation_data = {
            "vendor_id": vendor_id,
            "discount_percentage": 5.0,
            "tax_percentage": 10.0,
            "shipping_cost": 100.0,
            "validity_days": 30,
            "delivery_days": 14,
            "items": [quotation_item_data],
        }
        quote_response = await client.post(
            f"/api/v1/quotations/rfq/{rfq_id}",
            json=quotation_data,
        )
        quotation_id = quote_response.json()["id"]
        await client.post(f"/api/v1/quotations/{quotation_id}/submit")

        # Compare quotes
        response = await client.get(f"/api/v1/rfq/{rfq_id}/compare")
        assert response.status_code == 200
        data = response.json()
        assert data["rfq_id"] == rfq_id
        assert "total_vendors_invited" in data
        assert "total_quotations_received" in data
        assert "item_comparisons" in data
        assert "quotations" in data
