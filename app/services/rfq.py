"""RFQ (Request for Quotation) workflow service."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    DuplicateException,
    NotFoundException,
    ValidationException,
    WorkflowException,
)
from app.core.pagination import PaginationParams
from app.models.rfq import (
    RFQ,
    RFQItem,
    RFQVendorInvitation,
    Quotation,
    QuotationItem,
    RFQStatus,
    InvitationStatus,
    QuotationStatus,
)
from app.models.vendor import Vendor
from app.schemas.rfq import (
    RFQCreate,
    RFQUpdate,
    RFQItemCreate,
    RFQItemUpdate,
    RFQVendorInvitationCreate,
    QuotationCreate,
    QuotationUpdate,
    QuotationItemCreate,
    QuotationItemUpdate,
    QuotationEvaluate,
    RFQFilterParams,
    RFQStatusUpdate,
    QuoteComparisonResponse,
    QuoteItemComparison,
)


class RFQService:
    """Service for RFQ workflow operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== RFQ Number Generation ====================

    async def _generate_rfq_number(self) -> str:
        """Generate a unique RFQ number."""
        today = datetime.now(timezone.utc)
        prefix = f"RFQ-{today.strftime('%Y%m')}"

        # Get the highest number for this month
        result = await self.db.execute(
            select(func.max(RFQ.rfq_number)).where(
                RFQ.rfq_number.like(f"{prefix}%")
            )
        )
        last_number = result.scalar()

        if last_number:
            # Extract the sequence number and increment
            seq = int(last_number.split("-")[-1]) + 1
        else:
            seq = 1

        return f"{prefix}-{seq:04d}"

    async def _generate_quotation_number(self, rfq_number: str, vendor_code: str) -> str:
        """Generate a unique quotation number."""
        return f"Q-{rfq_number}-{vendor_code}"

    # ==================== RFQ CRUD Operations ====================

    async def create_rfq(self, data: RFQCreate, created_by: Optional[str] = None) -> RFQ:
        """Create a new RFQ."""
        rfq_number = await self._generate_rfq_number()

        # Create RFQ
        rfq_data = data.model_dump(exclude={"items", "vendor_ids"})
        rfq = RFQ(
            rfq_number=rfq_number,
            created_by=created_by,
            **rfq_data,
        )
        self.db.add(rfq)
        await self.db.flush()

        # Add items
        for item_data in data.items:
            item = RFQItem(
                rfq_id=rfq.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        # Create vendor invitations
        for vendor_id in data.vendor_ids:
            await self._create_invitation(rfq.id, vendor_id)

        await self.db.flush()
        await self.db.refresh(rfq)
        return rfq

    async def get_rfq(
        self,
        rfq_id: int,
        include_relations: bool = True,
    ) -> Optional[RFQ]:
        """Get an RFQ by ID with optional relations."""
        query = select(RFQ).where(RFQ.id == rfq_id)

        if include_relations:
            query = query.options(
                selectinload(RFQ.items),
                selectinload(RFQ.vendor_invitations),
                selectinload(RFQ.quotations).selectinload(Quotation.items),
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_rfq_by_number(self, rfq_number: str) -> Optional[RFQ]:
        """Get an RFQ by number."""
        result = await self.db.execute(
            select(RFQ).where(RFQ.rfq_number == rfq_number)
        )
        return result.scalar_one_or_none()

    async def list_rfqs(
        self,
        pagination: PaginationParams,
        filters: Optional[RFQFilterParams] = None,
    ) -> Tuple[List[RFQ], int]:
        """List RFQs with pagination and filtering."""
        query = select(RFQ).options(
            selectinload(RFQ.items),
            selectinload(RFQ.vendor_invitations),
            selectinload(RFQ.quotations),
        )
        count_query = select(func.count(RFQ.id))

        # Apply filters
        if filters:
            conditions = []

            if filters.search:
                search_term = f"%{filters.search}%"
                conditions.append(
                    or_(
                        RFQ.title.ilike(search_term),
                        RFQ.rfq_number.ilike(search_term),
                        RFQ.description.ilike(search_term),
                    )
                )

            if filters.status:
                conditions.append(RFQ.status == filters.status.value)

            if filters.priority:
                conditions.append(RFQ.priority == filters.priority)

            if filters.department:
                conditions.append(RFQ.department == filters.department)

            if filters.created_by:
                conditions.append(RFQ.created_by == filters.created_by)

            if filters.date_from:
                conditions.append(RFQ.created_at >= filters.date_from)

            if filters.date_to:
                conditions.append(RFQ.created_at <= filters.date_to)

            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))

            # Apply sorting
            if filters.sort_by:
                sort_column = getattr(RFQ, filters.sort_by, RFQ.created_at)
                if filters.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(RFQ.created_at.desc())
        else:
            query = query.order_by(RFQ.created_at.desc())

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.db.execute(query)
        rfqs = list(result.scalars().all())

        return rfqs, total

    async def update_rfq(
        self,
        rfq_id: int,
        data: RFQUpdate,
    ) -> RFQ:
        """Update an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        # Only allow updates if RFQ is in draft status
        if rfq.status != RFQStatus.DRAFT.value:
            raise ValidationException(
                f"Cannot update RFQ in '{rfq.status}' status. Only draft RFQs can be updated."
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rfq, field, value)

        await self.db.flush()
        await self.db.refresh(rfq)
        return rfq

    async def update_rfq_status(
        self,
        rfq_id: int,
        data: RFQStatusUpdate,
    ) -> RFQ:
        """Update RFQ status with workflow validation."""
        rfq = await self.get_rfq(rfq_id, include_relations=True)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        new_status = data.status

        # Validate status transition
        if not rfq.can_transition_to(new_status):
            raise WorkflowException(rfq.status, new_status.value)

        # Additional validations based on target status
        if new_status == RFQStatus.PUBLISHED:
            # Must have at least one item
            if not rfq.items:
                raise ValidationException("Cannot publish RFQ without items")
            # Must have at least one vendor invitation
            if not rfq.vendor_invitations:
                raise ValidationException(
                    "Cannot publish RFQ without vendor invitations"
                )
            # Set issue date and published_at
            rfq.issue_date = datetime.now(timezone.utc)
            rfq.published_at = datetime.now(timezone.utc)

        elif new_status == RFQStatus.CLOSED:
            rfq.closed_at = datetime.now(timezone.utc)

        rfq.status = new_status.value

        if data.notes:
            rfq.notes = (rfq.notes or "") + f"\n[{new_status.value}]: {data.notes}"

        await self.db.flush()
        await self.db.refresh(rfq)
        return rfq

    async def delete_rfq(self, rfq_id: int) -> None:
        """Delete an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        # Only allow deletion of draft RFQs
        if rfq.status != RFQStatus.DRAFT.value:
            raise ValidationException(
                f"Cannot delete RFQ in '{rfq.status}' status. Only draft RFQs can be deleted."
            )

        await self.db.delete(rfq)
        await self.db.flush()

    # ==================== RFQ Item Operations ====================

    async def add_rfq_item(
        self,
        rfq_id: int,
        data: RFQItemCreate,
    ) -> RFQItem:
        """Add an item to an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        if rfq.status != RFQStatus.DRAFT.value:
            raise ValidationException("Cannot add items to non-draft RFQ")

        # Check for duplicate item number
        existing = await self.db.execute(
            select(RFQItem).where(
                and_(
                    RFQItem.rfq_id == rfq_id,
                    RFQItem.item_number == data.item_number,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateException("RFQItem", "item_number", data.item_number)

        item = RFQItem(
            rfq_id=rfq_id,
            **data.model_dump(),
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def get_rfq_item(self, item_id: int) -> Optional[RFQItem]:
        """Get an RFQ item by ID."""
        result = await self.db.execute(
            select(RFQItem).where(RFQItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_rfq_items(self, rfq_id: int) -> List[RFQItem]:
        """List all items for an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        result = await self.db.execute(
            select(RFQItem)
            .where(RFQItem.rfq_id == rfq_id)
            .order_by(RFQItem.item_number)
        )
        return list(result.scalars().all())

    async def update_rfq_item(
        self,
        item_id: int,
        data: RFQItemUpdate,
    ) -> RFQItem:
        """Update an RFQ item."""
        item = await self.get_rfq_item(item_id)
        if not item:
            raise NotFoundException("RFQItem", item_id)

        # Get parent RFQ to check status
        rfq = await self.get_rfq(item.rfq_id, include_relations=False)
        if rfq and rfq.status != RFQStatus.DRAFT.value:
            raise ValidationException("Cannot update items in non-draft RFQ")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete_rfq_item(self, item_id: int) -> None:
        """Delete an RFQ item."""
        item = await self.get_rfq_item(item_id)
        if not item:
            raise NotFoundException("RFQItem", item_id)

        # Get parent RFQ to check status
        rfq = await self.get_rfq(item.rfq_id, include_relations=False)
        if rfq and rfq.status != RFQStatus.DRAFT.value:
            raise ValidationException("Cannot delete items from non-draft RFQ")

        await self.db.delete(item)
        await self.db.flush()

    # ==================== Vendor Invitation Operations ====================

    async def _create_invitation(
        self,
        rfq_id: int,
        vendor_id: int,
        notes: Optional[str] = None,
    ) -> RFQVendorInvitation:
        """Create a vendor invitation (internal method)."""
        # Verify vendor exists
        vendor = await self.db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        if not vendor.scalar_one_or_none():
            raise NotFoundException("Vendor", vendor_id)

        # Check for duplicate invitation
        existing = await self.db.execute(
            select(RFQVendorInvitation).where(
                and_(
                    RFQVendorInvitation.rfq_id == rfq_id,
                    RFQVendorInvitation.vendor_id == vendor_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateException(
                "RFQVendorInvitation",
                "vendor_id",
                vendor_id,
            )

        # Generate invitation token
        invitation_token = secrets.token_urlsafe(32)

        invitation = RFQVendorInvitation(
            rfq_id=rfq_id,
            vendor_id=vendor_id,
            invitation_token=invitation_token,
            invited_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            notes=notes,
        )
        self.db.add(invitation)
        await self.db.flush()
        await self.db.refresh(invitation)
        return invitation

    async def invite_vendor(
        self,
        rfq_id: int,
        data: RFQVendorInvitationCreate,
    ) -> RFQVendorInvitation:
        """Invite a vendor to participate in an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        # Allow invitations for draft and published RFQs
        if rfq.status not in [RFQStatus.DRAFT.value, RFQStatus.PUBLISHED.value]:
            raise ValidationException(
                f"Cannot invite vendors to RFQ in '{rfq.status}' status"
            )

        return await self._create_invitation(rfq_id, data.vendor_id, data.notes)

    async def get_invitation(
        self,
        invitation_id: int,
    ) -> Optional[RFQVendorInvitation]:
        """Get an invitation by ID."""
        result = await self.db.execute(
            select(RFQVendorInvitation).where(
                RFQVendorInvitation.id == invitation_id
            )
        )
        return result.scalar_one_or_none()

    async def get_invitation_by_token(
        self,
        token: str,
    ) -> Optional[RFQVendorInvitation]:
        """Get an invitation by token."""
        result = await self.db.execute(
            select(RFQVendorInvitation).where(
                RFQVendorInvitation.invitation_token == token
            )
        )
        return result.scalar_one_or_none()

    async def list_rfq_invitations(
        self,
        rfq_id: int,
    ) -> List[RFQVendorInvitation]:
        """List all vendor invitations for an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        result = await self.db.execute(
            select(RFQVendorInvitation)
            .where(RFQVendorInvitation.rfq_id == rfq_id)
            .options(selectinload(RFQVendorInvitation.vendor))
        )
        return list(result.scalars().all())

    async def mark_invitation_sent(
        self,
        invitation_id: int,
    ) -> RFQVendorInvitation:
        """Mark an invitation as sent."""
        invitation = await self.get_invitation(invitation_id)
        if not invitation:
            raise NotFoundException("RFQVendorInvitation", invitation_id)

        invitation.status = InvitationStatus.SENT.value
        invitation.sent_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(invitation)
        return invitation

    async def accept_invitation(
        self,
        invitation_id: int,
    ) -> RFQVendorInvitation:
        """Accept a vendor invitation."""
        invitation = await self.get_invitation(invitation_id)
        if not invitation:
            raise NotFoundException("RFQVendorInvitation", invitation_id)

        invitation.status = InvitationStatus.ACCEPTED.value
        invitation.responded_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(invitation)
        return invitation

    async def decline_invitation(
        self,
        invitation_id: int,
        reason: Optional[str] = None,
    ) -> RFQVendorInvitation:
        """Decline a vendor invitation."""
        invitation = await self.get_invitation(invitation_id)
        if not invitation:
            raise NotFoundException("RFQVendorInvitation", invitation_id)

        invitation.status = InvitationStatus.DECLINED.value
        invitation.responded_at = datetime.now(timezone.utc)
        invitation.decline_reason = reason

        await self.db.flush()
        await self.db.refresh(invitation)
        return invitation

    async def remove_invitation(self, invitation_id: int) -> None:
        """Remove a vendor invitation."""
        invitation = await self.get_invitation(invitation_id)
        if not invitation:
            raise NotFoundException("RFQVendorInvitation", invitation_id)

        # Get parent RFQ to check status
        rfq = await self.get_rfq(invitation.rfq_id, include_relations=False)
        if rfq and rfq.status not in [RFQStatus.DRAFT.value, RFQStatus.PUBLISHED.value]:
            raise ValidationException(
                f"Cannot remove invitations from RFQ in '{rfq.status}' status"
            )

        await self.db.delete(invitation)
        await self.db.flush()

    # ==================== Quotation Operations ====================

    async def create_quotation(
        self,
        rfq_id: int,
        data: QuotationCreate,
    ) -> Quotation:
        """Create a new quotation for an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=True)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        # Verify RFQ is accepting quotations
        if rfq.status != RFQStatus.PUBLISHED.value:
            raise ValidationException(
                f"Cannot submit quotations for RFQ in '{rfq.status}' status"
            )

        # Verify vendor is invited
        vendor_invited = any(
            inv.vendor_id == data.vendor_id for inv in rfq.vendor_invitations
        )
        if not vendor_invited:
            raise ValidationException("Vendor is not invited to this RFQ")

        # Check for existing quotation
        existing = await self.db.execute(
            select(Quotation).where(
                and_(
                    Quotation.rfq_id == rfq_id,
                    Quotation.vendor_id == data.vendor_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateException("Quotation", "vendor_id", data.vendor_id)

        # Get vendor for quotation number
        vendor = await self.db.execute(
            select(Vendor).where(Vendor.id == data.vendor_id)
        )
        vendor_obj = vendor.scalar_one_or_none()
        if not vendor_obj:
            raise NotFoundException("Vendor", data.vendor_id)

        quotation_number = await self._generate_quotation_number(
            rfq.rfq_number, vendor_obj.code
        )

        # Create quotation
        quotation_data = data.model_dump(exclude={"items"})
        quotation = Quotation(
            rfq_id=rfq_id,
            quotation_number=quotation_number,
            **quotation_data,
        )
        self.db.add(quotation)
        await self.db.flush()

        # Add items
        subtotal = 0.0
        for item_data in data.items:
            # Verify RFQ item exists
            rfq_item = await self.get_rfq_item(item_data.rfq_item_id)
            if not rfq_item or rfq_item.rfq_id != rfq_id:
                raise ValidationException(
                    f"Invalid RFQ item ID: {item_data.rfq_item_id}"
                )

            total_price = item_data.unit_price * item_data.quantity
            item = QuotationItem(
                quotation_id=quotation.id,
                total_price=total_price,
                **item_data.model_dump(),
            )
            self.db.add(item)
            subtotal += total_price

        # Calculate totals
        quotation.subtotal = subtotal
        quotation.discount_amount = subtotal * (quotation.discount_percentage / 100)
        after_discount = subtotal - quotation.discount_amount
        quotation.tax_amount = after_discount * (quotation.tax_percentage / 100)
        quotation.total_amount = (
            after_discount + quotation.tax_amount + quotation.shipping_cost
        )

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def get_quotation(
        self,
        quotation_id: int,
        include_items: bool = True,
    ) -> Optional[Quotation]:
        """Get a quotation by ID."""
        query = select(Quotation).where(Quotation.id == quotation_id)

        if include_items:
            query = query.options(selectinload(Quotation.items))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_rfq_quotations(
        self,
        rfq_id: int,
    ) -> List[Quotation]:
        """List all quotations for an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=False)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        result = await self.db.execute(
            select(Quotation)
            .where(Quotation.rfq_id == rfq_id)
            .options(selectinload(Quotation.items))
            .order_by(Quotation.created_at)
        )
        return list(result.scalars().all())

    async def update_quotation(
        self,
        quotation_id: int,
        data: QuotationUpdate,
    ) -> Quotation:
        """Update a quotation."""
        quotation = await self.get_quotation(quotation_id)
        if not quotation:
            raise NotFoundException("Quotation", quotation_id)

        # Only allow updates if quotation is in draft status
        if quotation.status != QuotationStatus.DRAFT.value:
            raise ValidationException(
                f"Cannot update quotation in '{quotation.status}' status"
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quotation, field, value)

        # Recalculate totals
        quotation.discount_amount = quotation.subtotal * (
            quotation.discount_percentage / 100
        )
        after_discount = quotation.subtotal - quotation.discount_amount
        quotation.tax_amount = after_discount * (quotation.tax_percentage / 100)
        quotation.total_amount = (
            after_discount + quotation.tax_amount + quotation.shipping_cost
        )

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def submit_quotation(self, quotation_id: int) -> Quotation:
        """Submit a quotation for evaluation."""
        quotation = await self.get_quotation(quotation_id)
        if not quotation:
            raise NotFoundException("Quotation", quotation_id)

        if quotation.status != QuotationStatus.DRAFT.value:
            raise ValidationException(
                f"Cannot submit quotation in '{quotation.status}' status"
            )

        # Verify quotation has items
        if not quotation.items:
            raise ValidationException("Cannot submit quotation without items")

        quotation.status = QuotationStatus.SUBMITTED.value
        quotation.submitted_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def evaluate_quotation(
        self,
        quotation_id: int,
        data: QuotationEvaluate,
    ) -> Quotation:
        """Evaluate a submitted quotation."""
        quotation = await self.get_quotation(quotation_id)
        if not quotation:
            raise NotFoundException("Quotation", quotation_id)

        if quotation.status not in [
            QuotationStatus.SUBMITTED.value,
            QuotationStatus.UNDER_EVALUATION.value,
        ]:
            raise ValidationException(
                f"Cannot evaluate quotation in '{quotation.status}' status"
            )

        quotation.status = QuotationStatus.UNDER_EVALUATION.value
        quotation.technical_score = data.technical_score
        quotation.commercial_score = data.commercial_score
        quotation.overall_score = (data.technical_score + data.commercial_score) / 2
        quotation.evaluation_notes = data.evaluation_notes
        quotation.evaluated_by = data.evaluated_by
        quotation.evaluated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def accept_quotation(self, quotation_id: int) -> Quotation:
        """Accept a quotation."""
        quotation = await self.get_quotation(quotation_id)
        if not quotation:
            raise NotFoundException("Quotation", quotation_id)

        if quotation.status != QuotationStatus.UNDER_EVALUATION.value:
            raise ValidationException(
                f"Cannot accept quotation in '{quotation.status}' status"
            )

        quotation.status = QuotationStatus.ACCEPTED.value

        # Reject all other quotations for this RFQ
        result = await self.db.execute(
            select(Quotation).where(
                and_(
                    Quotation.rfq_id == quotation.rfq_id,
                    Quotation.id != quotation_id,
                    Quotation.status == QuotationStatus.UNDER_EVALUATION.value,
                )
            )
        )
        for other_quotation in result.scalars().all():
            other_quotation.status = QuotationStatus.REJECTED.value

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    async def reject_quotation(self, quotation_id: int) -> Quotation:
        """Reject a quotation."""
        quotation = await self.get_quotation(quotation_id)
        if not quotation:
            raise NotFoundException("Quotation", quotation_id)

        if quotation.status != QuotationStatus.UNDER_EVALUATION.value:
            raise ValidationException(
                f"Cannot reject quotation in '{quotation.status}' status"
            )

        quotation.status = QuotationStatus.REJECTED.value

        await self.db.flush()
        await self.db.refresh(quotation)
        return quotation

    # ==================== Quotation Item Operations ====================

    async def add_quotation_item(
        self,
        quotation_id: int,
        data: QuotationItemCreate,
    ) -> QuotationItem:
        """Add an item to a quotation."""
        quotation = await self.get_quotation(quotation_id)
        if not quotation:
            raise NotFoundException("Quotation", quotation_id)

        if quotation.status != QuotationStatus.DRAFT.value:
            raise ValidationException("Cannot add items to non-draft quotation")

        # Verify RFQ item exists and belongs to the RFQ
        rfq_item = await self.get_rfq_item(data.rfq_item_id)
        if not rfq_item or rfq_item.rfq_id != quotation.rfq_id:
            raise ValidationException(f"Invalid RFQ item ID: {data.rfq_item_id}")

        # Check for duplicate
        existing = await self.db.execute(
            select(QuotationItem).where(
                and_(
                    QuotationItem.quotation_id == quotation_id,
                    QuotationItem.rfq_item_id == data.rfq_item_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateException("QuotationItem", "rfq_item_id", data.rfq_item_id)

        total_price = data.unit_price * data.quantity
        item = QuotationItem(
            quotation_id=quotation_id,
            total_price=total_price,
            **data.model_dump(),
        )
        self.db.add(item)

        # Update quotation totals
        quotation.subtotal += total_price
        self._recalculate_quotation_totals(quotation)

        await self.db.flush()
        await self.db.refresh(item)
        return item

    def _recalculate_quotation_totals(self, quotation: Quotation) -> None:
        """Recalculate quotation totals."""
        quotation.discount_amount = quotation.subtotal * (
            quotation.discount_percentage / 100
        )
        after_discount = quotation.subtotal - quotation.discount_amount
        quotation.tax_amount = after_discount * (quotation.tax_percentage / 100)
        quotation.total_amount = (
            after_discount + quotation.tax_amount + quotation.shipping_cost
        )

    async def update_quotation_item(
        self,
        item_id: int,
        data: QuotationItemUpdate,
    ) -> QuotationItem:
        """Update a quotation item."""
        result = await self.db.execute(
            select(QuotationItem).where(QuotationItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundException("QuotationItem", item_id)

        # Get quotation to check status
        quotation = await self.get_quotation(item.quotation_id)
        if quotation and quotation.status != QuotationStatus.DRAFT.value:
            raise ValidationException("Cannot update items in non-draft quotation")

        old_total = item.total_price
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        # Recalculate item total
        item.total_price = item.unit_price * item.quantity

        # Update quotation totals
        if quotation:
            quotation.subtotal = quotation.subtotal - old_total + item.total_price
            self._recalculate_quotation_totals(quotation)

        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete_quotation_item(self, item_id: int) -> None:
        """Delete a quotation item."""
        result = await self.db.execute(
            select(QuotationItem).where(QuotationItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundException("QuotationItem", item_id)

        # Get quotation to check status
        quotation = await self.get_quotation(item.quotation_id)
        if quotation and quotation.status != QuotationStatus.DRAFT.value:
            raise ValidationException("Cannot delete items from non-draft quotation")

        # Update quotation totals
        if quotation:
            quotation.subtotal -= item.total_price
            self._recalculate_quotation_totals(quotation)

        await self.db.delete(item)
        await self.db.flush()

    # ==================== Quote Comparison ====================

    async def compare_quotes(self, rfq_id: int) -> QuoteComparisonResponse:
        """Generate a comprehensive quote comparison for an RFQ."""
        rfq = await self.get_rfq(rfq_id, include_relations=True)
        if not rfq:
            raise NotFoundException("RFQ", rfq_id)

        quotations = await self.list_rfq_quotations(rfq_id)
        submitted_quotations = [
            q for q in quotations
            if q.status in [
                QuotationStatus.SUBMITTED.value,
                QuotationStatus.UNDER_EVALUATION.value,
                QuotationStatus.ACCEPTED.value,
            ]
        ]

        # Build item comparisons
        item_comparisons = []
        for rfq_item in rfq.items:
            item_quotes = []
            prices = []

            for quotation in submitted_quotations:
                # Get vendor info
                vendor_result = await self.db.execute(
                    select(Vendor).where(Vendor.id == quotation.vendor_id)
                )
                vendor = vendor_result.scalar_one_or_none()

                # Find quote item for this RFQ item
                quote_item = next(
                    (qi for qi in quotation.items if qi.rfq_item_id == rfq_item.id),
                    None,
                )

                if quote_item:
                    prices.append(quote_item.total_price)
                    item_quotes.append({
                        "vendor_id": quotation.vendor_id,
                        "vendor_name": vendor.name if vendor else "Unknown",
                        "quotation_id": quotation.id,
                        "unit_price": quote_item.unit_price,
                        "quantity": quote_item.quantity,
                        "total_price": quote_item.total_price,
                        "lead_time_days": quote_item.lead_time_days,
                        "offered_brand": quote_item.offered_brand,
                        "offered_model": quote_item.offered_model,
                        "is_alternative": quote_item.is_alternative,
                    })

            if prices:
                avg_price = sum(prices) / len(prices)
                variance = (
                    ((max(prices) - min(prices)) / avg_price * 100)
                    if avg_price > 0
                    else 0
                )
            else:
                avg_price = 0
                variance = 0

            item_comparisons.append(QuoteItemComparison(
                rfq_item_id=rfq_item.id,
                rfq_item_name=rfq_item.name,
                rfq_item_number=rfq_item.item_number,
                requested_quantity=rfq_item.quantity,
                unit=rfq_item.unit,
                estimated_price=rfq_item.estimated_unit_price,
                quotes=item_quotes,
                lowest_price=min(prices) if prices else 0,
                highest_price=max(prices) if prices else 0,
                average_price=round(avg_price, 2),
                price_variance_percentage=round(variance, 2),
            ))

        # Find best quotes
        lowest_total = None
        best_rated = None
        fastest_delivery = None

        if submitted_quotations:
            # Lowest total
            sorted_by_total = sorted(
                submitted_quotations, key=lambda q: q.total_amount
            )
            if sorted_by_total:
                q = sorted_by_total[0]
                vendor_result = await self.db.execute(
                    select(Vendor).where(Vendor.id == q.vendor_id)
                )
                vendor = vendor_result.scalar_one_or_none()
                lowest_total = {
                    "quotation_id": q.id,
                    "vendor_id": q.vendor_id,
                    "vendor_name": vendor.name if vendor else "Unknown",
                    "total_amount": q.total_amount,
                }

            # Best rated (by overall score)
            scored = [q for q in submitted_quotations if q.overall_score is not None]
            if scored:
                sorted_by_score = sorted(
                    scored, key=lambda q: q.overall_score or 0, reverse=True
                )
                q = sorted_by_score[0]
                vendor_result = await self.db.execute(
                    select(Vendor).where(Vendor.id == q.vendor_id)
                )
                vendor = vendor_result.scalar_one_or_none()
                best_rated = {
                    "quotation_id": q.id,
                    "vendor_id": q.vendor_id,
                    "vendor_name": vendor.name if vendor else "Unknown",
                    "overall_score": q.overall_score,
                }

            # Fastest delivery
            with_delivery = [
                q for q in submitted_quotations if q.delivery_days is not None
            ]
            if with_delivery:
                sorted_by_delivery = sorted(
                    with_delivery, key=lambda q: q.delivery_days or float("inf")
                )
                q = sorted_by_delivery[0]
                vendor_result = await self.db.execute(
                    select(Vendor).where(Vendor.id == q.vendor_id)
                )
                vendor = vendor_result.scalar_one_or_none()
                fastest_delivery = {
                    "quotation_id": q.id,
                    "vendor_id": q.vendor_id,
                    "vendor_name": vendor.name if vendor else "Unknown",
                    "delivery_days": q.delivery_days,
                }

        # Build quotation responses
        quotation_responses = []
        for q in submitted_quotations:
            vendor_result = await self.db.execute(
                select(Vendor).where(Vendor.id == q.vendor_id)
            )
            vendor = vendor_result.scalar_one_or_none()

            from app.schemas.rfq import QuotationResponse, QuotationItemResponse

            item_responses = []
            for qi in q.items:
                rfq_item = await self.get_rfq_item(qi.rfq_item_id)
                item_responses.append(QuotationItemResponse(
                    id=qi.id,
                    quotation_id=qi.quotation_id,
                    rfq_item_id=qi.rfq_item_id,
                    unit_price=qi.unit_price,
                    quantity=qi.quantity,
                    total_price=qi.total_price,
                    offered_brand=qi.offered_brand,
                    offered_model=qi.offered_model,
                    offered_part_number=qi.offered_part_number,
                    is_alternative=qi.is_alternative,
                    lead_time_days=qi.lead_time_days,
                    availability=qi.availability,
                    specifications=qi.specifications,
                    notes=qi.notes,
                    created_at=qi.created_at,
                    updated_at=qi.updated_at,
                    rfq_item_name=rfq_item.name if rfq_item else None,
                    rfq_item_number=rfq_item.item_number if rfq_item else None,
                ))

            quotation_responses.append(QuotationResponse(
                id=q.id,
                rfq_id=q.rfq_id,
                vendor_id=q.vendor_id,
                quotation_number=q.quotation_number,
                status=q.status,
                subtotal=q.subtotal,
                discount_percentage=q.discount_percentage,
                discount_amount=q.discount_amount,
                tax_percentage=q.tax_percentage,
                tax_amount=q.tax_amount,
                shipping_cost=q.shipping_cost,
                total_amount=q.total_amount,
                currency=q.currency,
                validity_days=q.validity_days,
                delivery_days=q.delivery_days,
                payment_terms=q.payment_terms,
                warranty_terms=q.warranty_terms,
                document_url=q.document_url,
                notes=q.notes,
                technical_score=q.technical_score,
                commercial_score=q.commercial_score,
                overall_score=q.overall_score,
                evaluation_notes=q.evaluation_notes,
                evaluated_by=q.evaluated_by,
                evaluated_at=q.evaluated_at,
                submitted_at=q.submitted_at,
                created_at=q.created_at,
                updated_at=q.updated_at,
                items=item_responses,
                vendor_name=vendor.name if vendor else None,
            ))

        return QuoteComparisonResponse(
            rfq_id=rfq.id,
            rfq_number=rfq.rfq_number,
            rfq_title=rfq.title,
            total_vendors_invited=len(rfq.vendor_invitations),
            total_quotations_received=len(submitted_quotations),
            quotations_under_evaluation=len([
                q for q in submitted_quotations
                if q.status == QuotationStatus.UNDER_EVALUATION.value
            ]),
            quotations=quotation_responses,
            item_comparisons=item_comparisons,
            lowest_total_quote=lowest_total,
            best_rated_vendor=best_rated,
            fastest_delivery=fastest_delivery,
        )
