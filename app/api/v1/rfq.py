"""RFQ (Request for Quotation) management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import PaginatedResponse, PaginationParams
from app.models.rfq import RFQStatus
from app.schemas.rfq import (
    RFQCreate,
    RFQUpdate,
    RFQResponse,
    RFQListResponse,
    RFQItemCreate,
    RFQItemUpdate,
    RFQItemResponse,
    RFQVendorInvitationCreate,
    RFQVendorInvitationResponse,
    RFQFilterParams,
    RFQStatusUpdate,
    QuoteComparisonResponse,
)
from app.services.rfq import RFQService
from app.services.email import email_service

router = APIRouter()


# ==================== RFQ CRUD Endpoints ====================


@router.post(
    "",
    response_model=RFQResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create RFQ",
    description="Create a new Request for Quotation.",
)
async def create_rfq(
    data: RFQCreate,
    created_by: Optional[str] = Query(None, description="Creator's name/email"),
    db: AsyncSession = Depends(get_db),
) -> RFQResponse:
    """Create a new RFQ."""
    service = RFQService(db)
    rfq = await service.create_rfq(data, created_by)
    return _build_rfq_response(rfq)


@router.get(
    "",
    response_model=PaginatedResponse[RFQListResponse],
    summary="List RFQs",
    description="Get a paginated list of RFQs with optional filtering.",
)
async def list_rfqs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in title, number, description"),
    status: Optional[RFQStatus] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(
        None, pattern="^(low|normal|high|urgent)$", description="Filter by priority"
    ),
    department: Optional[str] = Query(None, description="Filter by department"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[RFQListResponse]:
    """List RFQs with pagination and filtering."""
    service = RFQService(db)

    pagination = PaginationParams(page=page, page_size=page_size)
    filters = RFQFilterParams(
        search=search,
        status=status,
        priority=priority,
        department=department,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    rfqs, total = await service.list_rfqs(pagination, filters)

    items = []
    for rfq in rfqs:
        items.append(RFQListResponse(
            id=rfq.id,
            rfq_number=rfq.rfq_number,
            title=rfq.title,
            status=rfq.status,
            submission_deadline=rfq.submission_deadline,
            priority=rfq.priority,
            department=rfq.department,
            items_count=len(rfq.items),
            vendors_invited=len(rfq.vendor_invitations),
            quotations_received=len([
                q for q in rfq.quotations if q.status != "draft"
            ]),
            created_at=rfq.created_at,
        ))

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{rfq_id}",
    response_model=RFQResponse,
    summary="Get RFQ details",
    description="Get detailed information about a specific RFQ.",
)
async def get_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
) -> RFQResponse:
    """Get RFQ by ID."""
    service = RFQService(db)
    rfq = await service.get_rfq(rfq_id)
    if not rfq:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("RFQ", rfq_id)
    return _build_rfq_response(rfq)


@router.put(
    "/{rfq_id}",
    response_model=RFQResponse,
    summary="Update RFQ",
    description="Update RFQ information. Only draft RFQs can be updated.",
)
async def update_rfq(
    rfq_id: int,
    data: RFQUpdate,
    db: AsyncSession = Depends(get_db),
) -> RFQResponse:
    """Update an RFQ."""
    service = RFQService(db)
    rfq = await service.update_rfq(rfq_id, data)
    return _build_rfq_response(rfq)


@router.patch(
    "/{rfq_id}/status",
    response_model=RFQResponse,
    summary="Update RFQ status",
    description="Update RFQ status with workflow validation.",
)
async def update_rfq_status(
    rfq_id: int,
    data: RFQStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> RFQResponse:
    """Update RFQ status."""
    service = RFQService(db)
    rfq = await service.update_rfq_status(rfq_id, data)

    # Send notifications for status changes
    if data.status == RFQStatus.PUBLISHED:
        # Notify all invited vendors
        invitations = await service.list_rfq_invitations(rfq_id)
        for invitation in invitations:
            if invitation.vendor:
                deadline = (
                    rfq.submission_deadline.strftime("%Y-%m-%d %H:%M UTC")
                    if rfq.submission_deadline
                    else "No deadline set"
                )
                await email_service.send_rfq_invitation(
                    vendor_email=invitation.vendor.email,
                    vendor_name=invitation.vendor.name,
                    rfq_number=rfq.rfq_number,
                    rfq_title=rfq.title,
                    deadline=deadline,
                    invitation_link=f"/rfq/{rfq.id}/invitation/{invitation.invitation_token}",
                )
                # Mark invitation as sent
                await service.mark_invitation_sent(invitation.id)

    return _build_rfq_response(rfq)


@router.delete(
    "/{rfq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete RFQ",
    description="Delete an RFQ. Only draft RFQs can be deleted.",
)
async def delete_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an RFQ."""
    service = RFQService(db)
    await service.delete_rfq(rfq_id)


# ==================== RFQ Item Endpoints ====================


@router.post(
    "/{rfq_id}/items",
    response_model=RFQItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add RFQ item",
    description="Add a new item to an RFQ.",
)
async def add_rfq_item(
    rfq_id: int,
    data: RFQItemCreate,
    db: AsyncSession = Depends(get_db),
) -> RFQItemResponse:
    """Add an item to an RFQ."""
    service = RFQService(db)
    item = await service.add_rfq_item(rfq_id, data)
    return RFQItemResponse.model_validate(item)


@router.get(
    "/{rfq_id}/items",
    response_model=List[RFQItemResponse],
    summary="List RFQ items",
    description="Get all items for an RFQ.",
)
async def list_rfq_items(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[RFQItemResponse]:
    """List all items for an RFQ."""
    service = RFQService(db)
    items = await service.list_rfq_items(rfq_id)
    return [RFQItemResponse.model_validate(item) for item in items]


@router.put(
    "/items/{item_id}",
    response_model=RFQItemResponse,
    summary="Update RFQ item",
    description="Update an RFQ item.",
)
async def update_rfq_item(
    item_id: int,
    data: RFQItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> RFQItemResponse:
    """Update an RFQ item."""
    service = RFQService(db)
    item = await service.update_rfq_item(item_id, data)
    return RFQItemResponse.model_validate(item)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete RFQ item",
    description="Delete an RFQ item.",
)
async def delete_rfq_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an RFQ item."""
    service = RFQService(db)
    await service.delete_rfq_item(item_id)


# ==================== Vendor Invitation Endpoints ====================


@router.post(
    "/{rfq_id}/invitations",
    response_model=RFQVendorInvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite vendor",
    description="Invite a vendor to participate in an RFQ.",
)
async def invite_vendor(
    rfq_id: int,
    data: RFQVendorInvitationCreate,
    db: AsyncSession = Depends(get_db),
) -> RFQVendorInvitationResponse:
    """Invite a vendor to an RFQ."""
    service = RFQService(db)
    invitation = await service.invite_vendor(rfq_id, data)
    return _build_invitation_response(invitation)


@router.get(
    "/{rfq_id}/invitations",
    response_model=List[RFQVendorInvitationResponse],
    summary="List vendor invitations",
    description="Get all vendor invitations for an RFQ.",
)
async def list_rfq_invitations(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[RFQVendorInvitationResponse]:
    """List all vendor invitations for an RFQ."""
    service = RFQService(db)
    invitations = await service.list_rfq_invitations(rfq_id)
    return [_build_invitation_response(inv) for inv in invitations]


@router.post(
    "/invitations/{invitation_id}/accept",
    response_model=RFQVendorInvitationResponse,
    summary="Accept invitation",
    description="Accept an RFQ invitation.",
)
async def accept_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
) -> RFQVendorInvitationResponse:
    """Accept an RFQ invitation."""
    service = RFQService(db)
    invitation = await service.accept_invitation(invitation_id)
    return _build_invitation_response(invitation)


@router.post(
    "/invitations/{invitation_id}/decline",
    response_model=RFQVendorInvitationResponse,
    summary="Decline invitation",
    description="Decline an RFQ invitation.",
)
async def decline_invitation(
    invitation_id: int,
    reason: Optional[str] = Query(None, description="Reason for declining"),
    db: AsyncSession = Depends(get_db),
) -> RFQVendorInvitationResponse:
    """Decline an RFQ invitation."""
    service = RFQService(db)
    invitation = await service.decline_invitation(invitation_id, reason)
    return _build_invitation_response(invitation)


@router.delete(
    "/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove invitation",
    description="Remove a vendor invitation from an RFQ.",
)
async def remove_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a vendor invitation."""
    service = RFQService(db)
    await service.remove_invitation(invitation_id)


# ==================== Quote Comparison Endpoint ====================


@router.get(
    "/{rfq_id}/compare",
    response_model=QuoteComparisonResponse,
    summary="Compare quotes",
    description="Get a comprehensive comparison of all submitted quotations for an RFQ.",
)
async def compare_quotes(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuoteComparisonResponse:
    """Compare all quotes for an RFQ."""
    service = RFQService(db)
    return await service.compare_quotes(rfq_id)


# ==================== Helper Functions ====================


def _build_rfq_response(rfq) -> RFQResponse:
    """Build RFQ response from model."""
    from app.schemas.rfq import RFQItemResponse, RFQVendorInvitationResponse

    items = [RFQItemResponse.model_validate(item) for item in rfq.items]
    invitations = [_build_invitation_response(inv) for inv in rfq.vendor_invitations]

    quotations_count = len([q for q in rfq.quotations if q.status != "draft"])

    return RFQResponse(
        id=rfq.id,
        rfq_number=rfq.rfq_number,
        title=rfq.title,
        description=rfq.description,
        status=rfq.status,
        issue_date=rfq.issue_date,
        submission_deadline=rfq.submission_deadline,
        validity_period_days=rfq.validity_period_days,
        delivery_address=rfq.delivery_address,
        delivery_terms=rfq.delivery_terms,
        payment_terms=rfq.payment_terms,
        warranty_requirements=rfq.warranty_requirements,
        technical_requirements=rfq.technical_requirements,
        compliance_requirements=rfq.compliance_requirements,
        budget_min=rfq.budget_min,
        budget_max=rfq.budget_max,
        currency=rfq.currency,
        department=rfq.department,
        project_reference=rfq.project_reference,
        priority=rfq.priority,
        notes=rfq.notes,
        created_by=rfq.created_by,
        published_at=rfq.published_at,
        closed_at=rfq.closed_at,
        created_at=rfq.created_at,
        updated_at=rfq.updated_at,
        items=items,
        vendor_invitations=invitations,
        quotations_count=quotations_count,
    )


def _build_invitation_response(invitation) -> RFQVendorInvitationResponse:
    """Build invitation response from model."""
    return RFQVendorInvitationResponse(
        id=invitation.id,
        rfq_id=invitation.rfq_id,
        vendor_id=invitation.vendor_id,
        status=invitation.status,
        invited_at=invitation.invited_at,
        sent_at=invitation.sent_at,
        viewed_at=invitation.viewed_at,
        responded_at=invitation.responded_at,
        expires_at=invitation.expires_at,
        decline_reason=invitation.decline_reason,
        notes=invitation.notes,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
        vendor_name=invitation.vendor.name if invitation.vendor else None,
        vendor_email=invitation.vendor.email if invitation.vendor else None,
    )
