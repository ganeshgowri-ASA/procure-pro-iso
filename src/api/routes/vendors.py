"""Vendor management API endpoints."""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query

from src.models.vendor import (
    Vendor,
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorStatus,
)

router = APIRouter()

# In-memory storage for demo (replace with database in production)
vendors_db: dict[UUID, Vendor] = {}


@router.get("/", response_model=list[VendorResponse])
async def list_vendors(
    status: Optional[VendorStatus] = Query(None, description="Filter by vendor status"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
) -> list[VendorResponse]:
    """
    List all vendors with optional filtering.

    - **status**: Filter by vendor status (active, inactive, pending, etc.)
    - **industry**: Filter by industry sector
    - **skip**: Pagination offset
    - **limit**: Maximum number of vendors to return
    """
    vendors = list(vendors_db.values())

    if status:
        vendors = [v for v in vendors if v.status == status]

    if industry:
        vendors = [v for v in vendors if v.industry and industry.lower() in v.industry.lower()]

    return vendors[skip : skip + limit]


@router.post("/", response_model=VendorResponse, status_code=201)
async def create_vendor(vendor_data: VendorCreate) -> VendorResponse:
    """
    Create a new vendor.

    Provide vendor details including:
    - Name and code (required)
    - Contact information
    - Certifications and ISO standards
    - Quality/delivery/price ratings
    """
    # Check for duplicate code
    existing = next((v for v in vendors_db.values() if v.code == vendor_data.code), None)
    if existing:
        raise HTTPException(status_code=400, detail=f"Vendor with code '{vendor_data.code}' already exists")

    vendor = Vendor(
        id=uuid4(),
        **vendor_data.model_dump(),
    )
    vendors_db[vendor.id] = vendor

    return vendor


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: UUID) -> VendorResponse:
    """Get a specific vendor by ID."""
    vendor = vendors_db.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(vendor_id: UUID, vendor_data: VendorUpdate) -> VendorResponse:
    """Update an existing vendor."""
    vendor = vendors_db.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    update_data = vendor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    vendors_db[vendor_id] = vendor
    return vendor


@router.delete("/{vendor_id}", status_code=204)
async def delete_vendor(vendor_id: UUID):
    """Delete a vendor."""
    if vendor_id not in vendors_db:
        raise HTTPException(status_code=404, detail="Vendor not found")
    del vendors_db[vendor_id]


@router.get("/{vendor_id}/certifications", response_model=dict)
async def get_vendor_certifications(vendor_id: UUID) -> dict:
    """Get vendor's certifications and ISO standards."""
    vendor = vendors_db.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return {
        "vendor_id": str(vendor_id),
        "vendor_name": vendor.name,
        "certifications": vendor.certifications,
        "iso_standards": vendor.iso_standards,
    }


@router.put("/{vendor_id}/status", response_model=VendorResponse)
async def update_vendor_status(
    vendor_id: UUID,
    status: VendorStatus = Query(..., description="New vendor status"),
) -> VendorResponse:
    """Update vendor status (active, inactive, suspended, etc.)."""
    vendor = vendors_db.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor.status = status
    vendors_db[vendor_id] = vendor
    return vendor


# Utility function for other modules
def get_vendors_dict() -> dict[UUID, Vendor]:
    """Get the vendors dictionary (for internal use by TBE module)."""
    return vendors_db


def add_vendor_internal(vendor: Vendor) -> Vendor:
    """Add a vendor internally (for testing/setup)."""
    vendors_db[vendor.id] = vendor
    return vendor
