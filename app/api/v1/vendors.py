"""Vendor management API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.vendor import CertificationType, VendorStatus
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
    VendorCertificationCreate,
    VendorCertificationUpdate,
    VendorCertificationResponse,
    VendorContactCreate,
    VendorContactUpdate,
    VendorContactResponse,
    VendorRatingCreate,
    VendorRatingUpdate,
    VendorRatingResponse,
    VendorFilterParams,
)
from app.services.vendor import VendorService
from app.services.email import email_service

router = APIRouter()


# ==================== Vendor CRUD Endpoints ====================


@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vendor",
    description="Create a new vendor with the provided information.",
)
async def create_vendor(
    data: VendorCreate,
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    """Create a new vendor."""
    service = VendorService(db)
    vendor = await service.create_vendor(data)
    return VendorResponse.model_validate(vendor)


@router.post(
    "/register",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new vendor",
    description="Register a new vendor. The vendor will be set to pending status until approved.",
)
async def register_vendor(
    data: VendorCreate,
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    """Register a new vendor with pending status."""
    service = VendorService(db)
    vendor = await service.register_vendor(data)

    # Send registration confirmation email
    await email_service.send_vendor_registration_confirmation(
        vendor_email=vendor.email,
        vendor_name=vendor.name,
        vendor_code=vendor.code,
    )

    return VendorResponse.model_validate(vendor)


@router.get(
    "",
    response_model=PaginatedResponse[VendorListResponse],
    summary="List vendors",
    description="Get a paginated list of vendors with optional filtering.",
)
async def list_vendors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in name, code, email"),
    status: Optional[VendorStatus] = Query(None, description="Filter by status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    country: Optional[str] = Query(None, description="Filter by country"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    has_certification: Optional[CertificationType] = Query(
        None, description="Filter by certification type"
    ),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VendorListResponse]:
    """List vendors with pagination and filtering."""
    service = VendorService(db)

    pagination = PaginationParams(page=page, page_size=page_size)
    filters = VendorFilterParams(
        search=search,
        status=status,
        category_id=category_id,
        country=country,
        min_rating=min_rating,
        has_certification=has_certification,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    vendors, total = await service.list_vendors(pagination, filters)

    items = [VendorListResponse.model_validate(v) for v in vendors]

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor details",
    description="Get detailed information about a specific vendor.",
)
async def get_vendor(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    """Get vendor by ID."""
    service = VendorService(db)
    vendor = await service.get_vendor(vendor_id)
    if not vendor:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Vendor", vendor_id)
    return VendorResponse.model_validate(vendor)


@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Update vendor",
    description="Update vendor information.",
)
async def update_vendor(
    vendor_id: int,
    data: VendorUpdate,
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    """Update a vendor."""
    service = VendorService(db)
    vendor = await service.update_vendor(vendor_id, data)
    return VendorResponse.model_validate(vendor)


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vendor",
    description="Delete a vendor. This will also delete all related data.",
)
async def delete_vendor(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vendor."""
    service = VendorService(db)
    await service.delete_vendor(vendor_id)


@router.post(
    "/{vendor_id}/activate",
    response_model=VendorResponse,
    summary="Activate vendor",
    description="Activate a vendor, changing their status to active.",
)
async def activate_vendor(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    """Activate a vendor."""
    service = VendorService(db)
    vendor = await service.activate_vendor(vendor_id)

    # Send activation notification email
    await email_service.send_vendor_activation_notification(
        vendor_email=vendor.email,
        vendor_name=vendor.name,
        vendor_code=vendor.code,
    )

    return VendorResponse.model_validate(vendor)


# ==================== Vendor Certification Endpoints ====================


@router.post(
    "/{vendor_id}/certifications",
    response_model=VendorCertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add vendor certification",
    description="Add a new certification to a vendor.",
)
async def add_vendor_certification(
    vendor_id: int,
    data: VendorCertificationCreate,
    db: AsyncSession = Depends(get_db),
) -> VendorCertificationResponse:
    """Add a certification to a vendor."""
    service = VendorService(db)
    certification = await service.add_certification(vendor_id, data)
    return VendorCertificationResponse.model_validate(certification)


@router.get(
    "/{vendor_id}/certifications",
    response_model=List[VendorCertificationResponse],
    summary="List vendor certifications",
    description="Get all certifications for a vendor.",
)
async def list_vendor_certifications(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[VendorCertificationResponse]:
    """List all certifications for a vendor."""
    service = VendorService(db)
    certifications = await service.list_vendor_certifications(vendor_id)
    return [VendorCertificationResponse.model_validate(c) for c in certifications]


@router.put(
    "/certifications/{certification_id}",
    response_model=VendorCertificationResponse,
    summary="Update certification",
    description="Update a vendor certification.",
)
async def update_certification(
    certification_id: int,
    data: VendorCertificationUpdate,
    db: AsyncSession = Depends(get_db),
) -> VendorCertificationResponse:
    """Update a vendor certification."""
    service = VendorService(db)
    certification = await service.update_certification(certification_id, data)
    return VendorCertificationResponse.model_validate(certification)


@router.post(
    "/certifications/{certification_id}/verify",
    response_model=VendorCertificationResponse,
    summary="Verify certification",
    description="Mark a certification as verified.",
)
async def verify_certification(
    certification_id: int,
    verified_by: str = Query(..., description="Name of the verifier"),
    db: AsyncSession = Depends(get_db),
) -> VendorCertificationResponse:
    """Verify a vendor certification."""
    service = VendorService(db)
    certification = await service.verify_certification(certification_id, verified_by)
    return VendorCertificationResponse.model_validate(certification)


@router.delete(
    "/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete certification",
    description="Delete a vendor certification.",
)
async def delete_certification(
    certification_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vendor certification."""
    service = VendorService(db)
    await service.delete_certification(certification_id)


# ==================== Vendor Contact Endpoints ====================


@router.post(
    "/{vendor_id}/contacts",
    response_model=VendorContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add vendor contact",
    description="Add a new contact to a vendor.",
)
async def add_vendor_contact(
    vendor_id: int,
    data: VendorContactCreate,
    db: AsyncSession = Depends(get_db),
) -> VendorContactResponse:
    """Add a contact to a vendor."""
    service = VendorService(db)
    contact = await service.add_contact(vendor_id, data)
    return VendorContactResponse.model_validate(contact)


@router.get(
    "/{vendor_id}/contacts",
    response_model=List[VendorContactResponse],
    summary="List vendor contacts",
    description="Get all contacts for a vendor.",
)
async def list_vendor_contacts(
    vendor_id: int,
    active_only: bool = Query(True, description="Only show active contacts"),
    db: AsyncSession = Depends(get_db),
) -> List[VendorContactResponse]:
    """List all contacts for a vendor."""
    service = VendorService(db)
    contacts = await service.list_vendor_contacts(vendor_id, active_only)
    return [VendorContactResponse.model_validate(c) for c in contacts]


@router.put(
    "/contacts/{contact_id}",
    response_model=VendorContactResponse,
    summary="Update contact",
    description="Update a vendor contact.",
)
async def update_contact(
    contact_id: int,
    data: VendorContactUpdate,
    db: AsyncSession = Depends(get_db),
) -> VendorContactResponse:
    """Update a vendor contact."""
    service = VendorService(db)
    contact = await service.update_contact(contact_id, data)
    return VendorContactResponse.model_validate(contact)


@router.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact",
    description="Delete a vendor contact.",
)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vendor contact."""
    service = VendorService(db)
    await service.delete_contact(contact_id)


# ==================== Vendor Rating Endpoints ====================


@router.post(
    "/{vendor_id}/ratings",
    response_model=VendorRatingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add vendor rating",
    description="Add a performance rating for a vendor.",
)
async def add_vendor_rating(
    vendor_id: int,
    data: VendorRatingCreate,
    db: AsyncSession = Depends(get_db),
) -> VendorRatingResponse:
    """Add a rating to a vendor."""
    service = VendorService(db)
    rating = await service.add_rating(vendor_id, data)
    return VendorRatingResponse.model_validate(rating)


@router.get(
    "/{vendor_id}/ratings",
    response_model=List[VendorRatingResponse],
    summary="List vendor ratings",
    description="Get all performance ratings for a vendor.",
)
async def list_vendor_ratings(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[VendorRatingResponse]:
    """List all ratings for a vendor."""
    service = VendorService(db)
    ratings = await service.list_vendor_ratings(vendor_id)
    return [VendorRatingResponse.model_validate(r) for r in ratings]


@router.get(
    "/{vendor_id}/performance",
    summary="Get vendor performance summary",
    description="Get a comprehensive performance summary for a vendor.",
)
async def get_vendor_performance(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get performance summary for a vendor."""
    service = VendorService(db)
    return await service.get_vendor_performance_summary(vendor_id)


@router.put(
    "/ratings/{rating_id}",
    response_model=VendorRatingResponse,
    summary="Update rating",
    description="Update a vendor rating.",
)
async def update_rating(
    rating_id: int,
    data: VendorRatingUpdate,
    db: AsyncSession = Depends(get_db),
) -> VendorRatingResponse:
    """Update a vendor rating."""
    service = VendorService(db)
    rating = await service.update_rating(rating_id, data)
    return VendorRatingResponse.model_validate(rating)


@router.delete(
    "/ratings/{rating_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete rating",
    description="Delete a vendor rating.",
)
async def delete_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vendor rating."""
    service = VendorService(db)
    await service.delete_rating(rating_id)
