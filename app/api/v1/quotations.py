"""Quotation management API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.vendor import Vendor
from app.schemas.rfq import (
    QuotationCreate,
    QuotationUpdate,
    QuotationResponse,
    QuotationItemCreate,
    QuotationItemUpdate,
    QuotationItemResponse,
    QuotationEvaluate,
)
from app.services.rfq import RFQService
from app.services.email import email_service

router = APIRouter()


# ==================== Quotation CRUD Endpoints ====================


@router.post(
    "/rfq/{rfq_id}",
    response_model=QuotationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create quotation",
    description="Create a new quotation for an RFQ.",
)
async def create_quotation(
    rfq_id: int,
    data: QuotationCreate,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Create a new quotation for an RFQ."""
    service = RFQService(db)
    quotation = await service.create_quotation(rfq_id, data)
    return await _build_quotation_response(quotation, db)


@router.get(
    "/rfq/{rfq_id}",
    response_model=List[QuotationResponse],
    summary="List RFQ quotations",
    description="Get all quotations for an RFQ.",
)
async def list_rfq_quotations(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[QuotationResponse]:
    """List all quotations for an RFQ."""
    service = RFQService(db)
    quotations = await service.list_rfq_quotations(rfq_id)
    return [await _build_quotation_response(q, db) for q in quotations]


@router.get(
    "/{quotation_id}",
    response_model=QuotationResponse,
    summary="Get quotation",
    description="Get a specific quotation by ID.",
)
async def get_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Get a quotation by ID."""
    service = RFQService(db)
    quotation = await service.get_quotation(quotation_id)
    if not quotation:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Quotation", quotation_id)
    return await _build_quotation_response(quotation, db)


@router.put(
    "/{quotation_id}",
    response_model=QuotationResponse,
    summary="Update quotation",
    description="Update a quotation. Only draft quotations can be updated.",
)
async def update_quotation(
    quotation_id: int,
    data: QuotationUpdate,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Update a quotation."""
    service = RFQService(db)
    quotation = await service.update_quotation(quotation_id, data)
    return await _build_quotation_response(quotation, db)


@router.post(
    "/{quotation_id}/submit",
    response_model=QuotationResponse,
    summary="Submit quotation",
    description="Submit a quotation for evaluation.",
)
async def submit_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Submit a quotation for evaluation."""
    service = RFQService(db)
    quotation = await service.submit_quotation(quotation_id)

    # Get RFQ and vendor for email notification
    rfq = await service.get_rfq(quotation.rfq_id, include_relations=False)
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.id == quotation.vendor_id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if rfq and vendor:
        await email_service.send_quotation_received_confirmation(
            vendor_email=vendor.email,
            vendor_name=vendor.name,
            rfq_number=rfq.rfq_number,
            quotation_number=quotation.quotation_number,
            total_amount=quotation.total_amount,
            currency=quotation.currency,
        )

    return await _build_quotation_response(quotation, db)


@router.post(
    "/{quotation_id}/evaluate",
    response_model=QuotationResponse,
    summary="Evaluate quotation",
    description="Evaluate a submitted quotation.",
)
async def evaluate_quotation(
    quotation_id: int,
    data: QuotationEvaluate,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Evaluate a quotation."""
    service = RFQService(db)
    quotation = await service.evaluate_quotation(quotation_id, data)
    return await _build_quotation_response(quotation, db)


@router.post(
    "/{quotation_id}/accept",
    response_model=QuotationResponse,
    summary="Accept quotation",
    description="Accept a quotation. This will reject all other quotations for the RFQ.",
)
async def accept_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Accept a quotation."""
    service = RFQService(db)
    quotation = await service.accept_quotation(quotation_id)

    # Get RFQ and vendor for email notification
    rfq = await service.get_rfq(quotation.rfq_id, include_relations=False)
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.id == quotation.vendor_id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if rfq and vendor:
        await email_service.send_quotation_accepted_notification(
            vendor_email=vendor.email,
            vendor_name=vendor.name,
            rfq_number=rfq.rfq_number,
            rfq_title=rfq.title,
            quotation_number=quotation.quotation_number,
        )

    return await _build_quotation_response(quotation, db)


@router.post(
    "/{quotation_id}/reject",
    response_model=QuotationResponse,
    summary="Reject quotation",
    description="Reject a quotation.",
)
async def reject_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuotationResponse:
    """Reject a quotation."""
    service = RFQService(db)
    quotation = await service.reject_quotation(quotation_id)

    # Get RFQ and vendor for email notification
    rfq = await service.get_rfq(quotation.rfq_id, include_relations=False)
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.id == quotation.vendor_id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if rfq and vendor:
        await email_service.send_quotation_rejected_notification(
            vendor_email=vendor.email,
            vendor_name=vendor.name,
            rfq_number=rfq.rfq_number,
            rfq_title=rfq.title,
            quotation_number=quotation.quotation_number,
        )

    return await _build_quotation_response(quotation, db)


# ==================== Quotation Item Endpoints ====================


@router.post(
    "/{quotation_id}/items",
    response_model=QuotationItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add quotation item",
    description="Add an item to a quotation.",
)
async def add_quotation_item(
    quotation_id: int,
    data: QuotationItemCreate,
    db: AsyncSession = Depends(get_db),
) -> QuotationItemResponse:
    """Add an item to a quotation."""
    service = RFQService(db)
    item = await service.add_quotation_item(quotation_id, data)
    rfq_item = await service.get_rfq_item(item.rfq_item_id)
    return _build_quotation_item_response(item, rfq_item)


@router.put(
    "/items/{item_id}",
    response_model=QuotationItemResponse,
    summary="Update quotation item",
    description="Update a quotation item.",
)
async def update_quotation_item(
    item_id: int,
    data: QuotationItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> QuotationItemResponse:
    """Update a quotation item."""
    service = RFQService(db)
    item = await service.update_quotation_item(item_id, data)
    rfq_item = await service.get_rfq_item(item.rfq_item_id)
    return _build_quotation_item_response(item, rfq_item)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete quotation item",
    description="Delete a quotation item.",
)
async def delete_quotation_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a quotation item."""
    service = RFQService(db)
    await service.delete_quotation_item(item_id)


# ==================== Helper Functions ====================


async def _build_quotation_response(quotation, db: AsyncSession) -> QuotationResponse:
    """Build quotation response from model."""
    # Get vendor name
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.id == quotation.vendor_id)
    )
    vendor = vendor_result.scalar_one_or_none()

    # Build item responses
    service = RFQService(db)
    item_responses = []
    for item in quotation.items:
        rfq_item = await service.get_rfq_item(item.rfq_item_id)
        item_responses.append(_build_quotation_item_response(item, rfq_item))

    return QuotationResponse(
        id=quotation.id,
        rfq_id=quotation.rfq_id,
        vendor_id=quotation.vendor_id,
        quotation_number=quotation.quotation_number,
        status=quotation.status,
        subtotal=quotation.subtotal,
        discount_percentage=quotation.discount_percentage,
        discount_amount=quotation.discount_amount,
        tax_percentage=quotation.tax_percentage,
        tax_amount=quotation.tax_amount,
        shipping_cost=quotation.shipping_cost,
        total_amount=quotation.total_amount,
        currency=quotation.currency,
        validity_days=quotation.validity_days,
        delivery_days=quotation.delivery_days,
        payment_terms=quotation.payment_terms,
        warranty_terms=quotation.warranty_terms,
        document_url=quotation.document_url,
        notes=quotation.notes,
        technical_score=quotation.technical_score,
        commercial_score=quotation.commercial_score,
        overall_score=quotation.overall_score,
        evaluation_notes=quotation.evaluation_notes,
        evaluated_by=quotation.evaluated_by,
        evaluated_at=quotation.evaluated_at,
        submitted_at=quotation.submitted_at,
        created_at=quotation.created_at,
        updated_at=quotation.updated_at,
        items=item_responses,
        vendor_name=vendor.name if vendor else None,
    )


def _build_quotation_item_response(item, rfq_item) -> QuotationItemResponse:
    """Build quotation item response from model."""
    return QuotationItemResponse(
        id=item.id,
        quotation_id=item.quotation_id,
        rfq_item_id=item.rfq_item_id,
        unit_price=item.unit_price,
        quantity=item.quantity,
        total_price=item.total_price,
        offered_brand=item.offered_brand,
        offered_model=item.offered_model,
        offered_part_number=item.offered_part_number,
        is_alternative=item.is_alternative,
        lead_time_days=item.lead_time_days,
        availability=item.availability,
        specifications=item.specifications,
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
        rfq_item_name=rfq_item.name if rfq_item else None,
        rfq_item_number=rfq_item.item_number if rfq_item else None,
    )
