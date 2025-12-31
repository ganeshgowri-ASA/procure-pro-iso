"""Vendor management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_async_session
from src.models.vendor import (
    Vendor,
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorStatus,
    VendorDB,
)
from src.repositories.vendor_repository import VendorRepository

router = APIRouter()


def db_to_response(vendor_db: VendorDB) -> VendorResponse:
    """Convert database model to response model."""
    return VendorResponse(
        id=UUID(vendor_db.id),
        name=vendor_db.name,
        code=vendor_db.code,
        email=vendor_db.email,
        phone=vendor_db.phone,
        address=vendor_db.address,
        country=vendor_db.country,
        industry=vendor_db.industry,
        status=vendor_db.status,
        certifications=vendor_db.certifications or [],
        iso_standards=vendor_db.iso_standards or [],
        quality_rating=vendor_db.quality_rating or 0.0,
        delivery_rating=vendor_db.delivery_rating or 0.0,
        price_competitiveness=vendor_db.price_competitiveness or 0.0,
        created_at=vendor_db.created_at,
        updated_at=vendor_db.updated_at,
    )


def db_to_vendor(vendor_db: VendorDB) -> Vendor:
    """Convert database model to Vendor model for internal use."""
    return Vendor(
        id=UUID(vendor_db.id),
        name=vendor_db.name,
        code=vendor_db.code,
        email=vendor_db.email,
        phone=vendor_db.phone,
        address=vendor_db.address,
        country=vendor_db.country,
        industry=vendor_db.industry,
        status=vendor_db.status,
        certifications=vendor_db.certifications or [],
        iso_standards=vendor_db.iso_standards or [],
        quality_rating=vendor_db.quality_rating or 0.0,
        delivery_rating=vendor_db.delivery_rating or 0.0,
        price_competitiveness=vendor_db.price_competitiveness or 0.0,
        created_at=vendor_db.created_at,
        updated_at=vendor_db.updated_at,
    )


@router.get("/", response_model=list[VendorResponse])
async def list_vendors(
    status: Optional[VendorStatus] = Query(None, description="Filter by vendor status"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    session: AsyncSession = Depends(get_async_session),
) -> list[VendorResponse]:
    """
    List all vendors with optional filtering.

    - **status**: Filter by vendor status (active, inactive, pending, etc.)
    - **industry**: Filter by industry sector
    - **skip**: Pagination offset
    - **limit**: Maximum number of vendors to return
    """
    repo = VendorRepository(session)
    vendors = await repo.get_all(status=status, industry=industry, skip=skip, limit=limit)
    return [db_to_response(v) for v in vendors]


@router.post("/", response_model=VendorResponse, status_code=201)
async def create_vendor(
    vendor_data: VendorCreate,
    session: AsyncSession = Depends(get_async_session),
) -> VendorResponse:
    """
    Create a new vendor.

    Provide vendor details including:
    - Name and code (required)
    - Contact information
    - Certifications and ISO standards
    - Quality/delivery/price ratings
    """
    repo = VendorRepository(session)

    # Check for duplicate code
    existing = await repo.get_by_code(vendor_data.code)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Vendor with code '{vendor_data.code}' already exists"
        )

    vendor = await repo.create(vendor_data)
    return db_to_response(vendor)


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> VendorResponse:
    """Get a specific vendor by ID."""
    repo = VendorRepository(session)
    vendor = await repo.get_by_id(str(vendor_id))
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_to_response(vendor)


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: UUID,
    vendor_data: VendorUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> VendorResponse:
    """Update an existing vendor."""
    repo = VendorRepository(session)
    vendor = await repo.update(str(vendor_id), vendor_data)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_to_response(vendor)


@router.delete("/{vendor_id}", status_code=204)
async def delete_vendor(
    vendor_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a vendor."""
    repo = VendorRepository(session)
    deleted = await repo.delete(str(vendor_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Vendor not found")


@router.get("/{vendor_id}/certifications", response_model=dict)
async def get_vendor_certifications(
    vendor_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Get vendor's certifications and ISO standards."""
    repo = VendorRepository(session)
    vendor = await repo.get_by_id(str(vendor_id))
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return {
        "vendor_id": str(vendor_id),
        "vendor_name": vendor.name,
        "certifications": vendor.certifications or [],
        "iso_standards": vendor.iso_standards or [],
    }


@router.put("/{vendor_id}/status", response_model=VendorResponse)
async def update_vendor_status(
    vendor_id: UUID,
    status: VendorStatus = Query(..., description="New vendor status"),
    session: AsyncSession = Depends(get_async_session),
) -> VendorResponse:
    """Update vendor status (active, inactive, suspended, etc.)."""
    repo = VendorRepository(session)
    vendor = await repo.update_status(str(vendor_id), status)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_to_response(vendor)


# Utility function for other modules
async def get_vendors_dict_from_db(session: AsyncSession) -> dict[UUID, Vendor]:
    """Get all vendors as dictionary from database."""
    repo = VendorRepository(session)
    vendors_db = await repo.get_vendors_dict()
    return {UUID(k): db_to_vendor(v) for k, v in vendors_db.items()}
