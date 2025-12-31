"""Vendor management service."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.core.pagination import PaginationParams
from app.models.vendor import (
    Vendor,
    VendorCategory,
    VendorCertification,
    VendorContact,
    VendorRating,
    VendorStatus,
)
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorCategoryCreate,
    VendorCategoryUpdate,
    VendorCertificationCreate,
    VendorCertificationUpdate,
    VendorContactCreate,
    VendorContactUpdate,
    VendorRatingCreate,
    VendorRatingUpdate,
    VendorFilterParams,
)


class VendorService:
    """Service for vendor management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Vendor Category Operations ====================

    async def create_category(self, data: VendorCategoryCreate) -> VendorCategory:
        """Create a new vendor category."""
        # Check for duplicate name
        existing = await self.db.execute(
            select(VendorCategory).where(VendorCategory.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise DuplicateException("VendorCategory", "name", data.name)

        # Validate parent if provided
        if data.parent_id:
            parent = await self.get_category(data.parent_id)
            if not parent:
                raise NotFoundException("VendorCategory", data.parent_id)

        category = VendorCategory(**data.model_dump())
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def get_category(self, category_id: int) -> Optional[VendorCategory]:
        """Get a vendor category by ID."""
        result = await self.db.execute(
            select(VendorCategory).where(VendorCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        include_inactive: bool = False,
    ) -> List[VendorCategory]:
        """List all vendor categories."""
        query = select(VendorCategory)
        if not include_inactive:
            query = query.where(VendorCategory.is_active == True)  # noqa: E712
        query = query.order_by(VendorCategory.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_category(
        self,
        category_id: int,
        data: VendorCategoryUpdate,
    ) -> VendorCategory:
        """Update a vendor category."""
        category = await self.get_category(category_id)
        if not category:
            raise NotFoundException("VendorCategory", category_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete_category(self, category_id: int) -> None:
        """Delete a vendor category."""
        category = await self.get_category(category_id)
        if not category:
            raise NotFoundException("VendorCategory", category_id)

        # Check if category has vendors
        result = await self.db.execute(
            select(func.count(Vendor.id)).where(Vendor.category_id == category_id)
        )
        vendor_count = result.scalar()
        if vendor_count and vendor_count > 0:
            raise ValidationException(
                f"Cannot delete category with {vendor_count} associated vendors"
            )

        await self.db.delete(category)
        await self.db.flush()

    # ==================== Vendor CRUD Operations ====================

    async def create_vendor(self, data: VendorCreate) -> Vendor:
        """Create a new vendor."""
        # Check for duplicate code
        existing = await self.db.execute(
            select(Vendor).where(Vendor.code == data.code)
        )
        if existing.scalar_one_or_none():
            raise DuplicateException("Vendor", "code", data.code)

        # Validate category if provided
        if data.category_id:
            category = await self.get_category(data.category_id)
            if not category:
                raise NotFoundException("VendorCategory", data.category_id)

        vendor = Vendor(**data.model_dump())
        self.db.add(vendor)
        await self.db.flush()
        await self.db.refresh(vendor)
        return vendor

    async def get_vendor(
        self,
        vendor_id: int,
        include_relations: bool = True,
    ) -> Optional[Vendor]:
        """Get a vendor by ID with optional relations."""
        query = select(Vendor).where(Vendor.id == vendor_id)

        if include_relations:
            query = query.options(
                selectinload(Vendor.category),
                selectinload(Vendor.certifications),
                selectinload(Vendor.contacts),
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_vendor_by_code(self, code: str) -> Optional[Vendor]:
        """Get a vendor by code."""
        result = await self.db.execute(
            select(Vendor).where(Vendor.code == code)
        )
        return result.scalar_one_or_none()

    async def list_vendors(
        self,
        pagination: PaginationParams,
        filters: Optional[VendorFilterParams] = None,
    ) -> Tuple[List[Vendor], int]:
        """List vendors with pagination and filtering."""
        query = select(Vendor)
        count_query = select(func.count(Vendor.id))

        # Apply filters
        if filters:
            conditions = []

            if filters.search:
                search_term = f"%{filters.search}%"
                conditions.append(
                    or_(
                        Vendor.name.ilike(search_term),
                        Vendor.code.ilike(search_term),
                        Vendor.email.ilike(search_term),
                    )
                )

            if filters.status:
                conditions.append(Vendor.status == filters.status.value)

            if filters.category_id:
                conditions.append(Vendor.category_id == filters.category_id)

            if filters.country:
                conditions.append(Vendor.country == filters.country)

            if filters.min_rating:
                conditions.append(Vendor.average_rating >= filters.min_rating)

            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))

            # Apply sorting
            if filters.sort_by:
                sort_column = getattr(Vendor, filters.sort_by, Vendor.created_at)
                if filters.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(Vendor.created_at.desc())
        else:
            query = query.order_by(Vendor.created_at.desc())

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.db.execute(query)
        vendors = list(result.scalars().all())

        return vendors, total

    async def update_vendor(
        self,
        vendor_id: int,
        data: VendorUpdate,
    ) -> Vendor:
        """Update a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        update_data = data.model_dump(exclude_unset=True)

        # Check for duplicate code if being updated
        if "code" in update_data and update_data["code"] != vendor.code:
            existing = await self.get_vendor_by_code(update_data["code"])
            if existing:
                raise DuplicateException("Vendor", "code", update_data["code"])

        # Validate category if provided
        if "category_id" in update_data and update_data["category_id"]:
            category = await self.get_category(update_data["category_id"])
            if not category:
                raise NotFoundException("VendorCategory", update_data["category_id"])

        for field, value in update_data.items():
            setattr(vendor, field, value)

        await self.db.flush()
        await self.db.refresh(vendor)
        return vendor

    async def delete_vendor(self, vendor_id: int) -> None:
        """Delete a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        await self.db.delete(vendor)
        await self.db.flush()

    async def register_vendor(self, data: VendorCreate) -> Vendor:
        """Register a new vendor (sets status to pending)."""
        data.status = VendorStatus.PENDING
        vendor = await self.create_vendor(data)
        vendor.registered_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(vendor)
        return vendor

    async def activate_vendor(self, vendor_id: int) -> Vendor:
        """Activate a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        vendor.status = VendorStatus.ACTIVE.value
        await self.db.flush()
        await self.db.refresh(vendor)
        return vendor

    # ==================== Vendor Certification Operations ====================

    async def add_certification(
        self,
        vendor_id: int,
        data: VendorCertificationCreate,
    ) -> VendorCertification:
        """Add a certification to a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        # Check for duplicate certification type
        existing = await self.db.execute(
            select(VendorCertification).where(
                and_(
                    VendorCertification.vendor_id == vendor_id,
                    VendorCertification.certification_type == data.certification_type.value,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateException(
                "VendorCertification",
                "certification_type",
                data.certification_type.value,
            )

        certification = VendorCertification(
            vendor_id=vendor_id,
            **data.model_dump(),
        )
        self.db.add(certification)
        await self.db.flush()
        await self.db.refresh(certification)
        return certification

    async def get_certification(
        self,
        certification_id: int,
    ) -> Optional[VendorCertification]:
        """Get a certification by ID."""
        result = await self.db.execute(
            select(VendorCertification).where(
                VendorCertification.id == certification_id
            )
        )
        return result.scalar_one_or_none()

    async def list_vendor_certifications(
        self,
        vendor_id: int,
    ) -> List[VendorCertification]:
        """List all certifications for a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        result = await self.db.execute(
            select(VendorCertification)
            .where(VendorCertification.vendor_id == vendor_id)
            .order_by(VendorCertification.certification_type)
        )
        return list(result.scalars().all())

    async def update_certification(
        self,
        certification_id: int,
        data: VendorCertificationUpdate,
    ) -> VendorCertification:
        """Update a vendor certification."""
        certification = await self.get_certification(certification_id)
        if not certification:
            raise NotFoundException("VendorCertification", certification_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(certification, field, value)

        await self.db.flush()
        await self.db.refresh(certification)
        return certification

    async def verify_certification(
        self,
        certification_id: int,
        verified_by: str,
    ) -> VendorCertification:
        """Mark a certification as verified."""
        certification = await self.get_certification(certification_id)
        if not certification:
            raise NotFoundException("VendorCertification", certification_id)

        certification.is_verified = True
        certification.verification_date = datetime.now(timezone.utc)
        certification.verified_by = verified_by

        await self.db.flush()
        await self.db.refresh(certification)
        return certification

    async def delete_certification(self, certification_id: int) -> None:
        """Delete a vendor certification."""
        certification = await self.get_certification(certification_id)
        if not certification:
            raise NotFoundException("VendorCertification", certification_id)

        await self.db.delete(certification)
        await self.db.flush()

    # ==================== Vendor Contact Operations ====================

    async def add_contact(
        self,
        vendor_id: int,
        data: VendorContactCreate,
    ) -> VendorContact:
        """Add a contact to a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        # If this contact is primary, unset other primary contacts
        if data.is_primary:
            await self._unset_primary_contacts(vendor_id)

        contact = VendorContact(
            vendor_id=vendor_id,
            **data.model_dump(),
        )
        self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def _unset_primary_contacts(self, vendor_id: int) -> None:
        """Unset primary flag for all contacts of a vendor."""
        result = await self.db.execute(
            select(VendorContact).where(
                and_(
                    VendorContact.vendor_id == vendor_id,
                    VendorContact.is_primary == True,  # noqa: E712
                )
            )
        )
        for contact in result.scalars().all():
            contact.is_primary = False

    async def get_contact(self, contact_id: int) -> Optional[VendorContact]:
        """Get a contact by ID."""
        result = await self.db.execute(
            select(VendorContact).where(VendorContact.id == contact_id)
        )
        return result.scalar_one_or_none()

    async def list_vendor_contacts(
        self,
        vendor_id: int,
        active_only: bool = True,
    ) -> List[VendorContact]:
        """List all contacts for a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        query = select(VendorContact).where(VendorContact.vendor_id == vendor_id)
        if active_only:
            query = query.where(VendorContact.is_active == True)  # noqa: E712
        query = query.order_by(
            VendorContact.is_primary.desc(),
            VendorContact.name,
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_contact(
        self,
        contact_id: int,
        data: VendorContactUpdate,
    ) -> VendorContact:
        """Update a vendor contact."""
        contact = await self.get_contact(contact_id)
        if not contact:
            raise NotFoundException("VendorContact", contact_id)

        update_data = data.model_dump(exclude_unset=True)

        # If setting as primary, unset other primary contacts
        if update_data.get("is_primary"):
            await self._unset_primary_contacts(contact.vendor_id)

        for field, value in update_data.items():
            setattr(contact, field, value)

        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int) -> None:
        """Delete a vendor contact."""
        contact = await self.get_contact(contact_id)
        if not contact:
            raise NotFoundException("VendorContact", contact_id)

        await self.db.delete(contact)
        await self.db.flush()

    # ==================== Vendor Rating Operations ====================

    async def add_rating(
        self,
        vendor_id: int,
        data: VendorRatingCreate,
    ) -> VendorRating:
        """Add a performance rating for a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        # Check for duplicate rating period
        existing = await self.db.execute(
            select(VendorRating).where(
                and_(
                    VendorRating.vendor_id == vendor_id,
                    VendorRating.rating_period == data.rating_period,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateException(
                "VendorRating",
                "rating_period",
                data.rating_period,
            )

        # Calculate overall rating
        ratings = [
            data.quality_rating,
            data.delivery_rating,
            data.price_rating,
            data.service_rating,
            data.communication_rating,
        ]
        non_zero_ratings = [r for r in ratings if r > 0]
        overall_rating = (
            sum(non_zero_ratings) / len(non_zero_ratings)
            if non_zero_ratings
            else 0.0
        )

        rating = VendorRating(
            vendor_id=vendor_id,
            overall_rating=overall_rating,
            evaluation_date=datetime.now(timezone.utc),
            **data.model_dump(),
        )
        self.db.add(rating)
        await self.db.flush()
        await self.db.refresh(rating)

        # Update vendor average rating
        await self._update_vendor_average_rating(vendor_id)

        return rating

    async def _update_vendor_average_rating(self, vendor_id: int) -> None:
        """Update the average rating for a vendor."""
        result = await self.db.execute(
            select(func.avg(VendorRating.overall_rating)).where(
                VendorRating.vendor_id == vendor_id
            )
        )
        avg_rating = result.scalar() or 0.0

        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if vendor:
            vendor.average_rating = round(avg_rating, 2)

    async def get_rating(self, rating_id: int) -> Optional[VendorRating]:
        """Get a rating by ID."""
        result = await self.db.execute(
            select(VendorRating).where(VendorRating.id == rating_id)
        )
        return result.scalar_one_or_none()

    async def list_vendor_ratings(
        self,
        vendor_id: int,
    ) -> List[VendorRating]:
        """List all ratings for a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        result = await self.db.execute(
            select(VendorRating)
            .where(VendorRating.vendor_id == vendor_id)
            .order_by(VendorRating.rating_period.desc())
        )
        return list(result.scalars().all())

    async def get_vendor_performance_summary(
        self,
        vendor_id: int,
    ) -> dict:
        """Get performance summary for a vendor."""
        vendor = await self.get_vendor(vendor_id, include_relations=False)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)

        ratings = await self.list_vendor_ratings(vendor_id)

        if not ratings:
            return {
                "vendor_id": vendor_id,
                "total_ratings": 0,
                "average_overall_rating": 0.0,
                "average_quality_rating": 0.0,
                "average_delivery_rating": 0.0,
                "average_price_rating": 0.0,
                "average_service_rating": 0.0,
                "average_communication_rating": 0.0,
                "total_orders_placed": 0,
                "total_orders_completed": 0,
                "total_orders_on_time": 0,
                "on_time_delivery_rate": 0.0,
                "total_defects": 0,
                "total_value": 0.0,
            }

        total_ratings = len(ratings)
        total_orders_placed = sum(r.orders_placed for r in ratings)
        total_orders_completed = sum(r.orders_completed for r in ratings)
        total_orders_on_time = sum(r.orders_on_time for r in ratings)
        on_time_rate = (
            (total_orders_on_time / total_orders_completed * 100)
            if total_orders_completed > 0
            else 0.0
        )

        return {
            "vendor_id": vendor_id,
            "total_ratings": total_ratings,
            "average_overall_rating": round(
                sum(r.overall_rating for r in ratings) / total_ratings, 2
            ),
            "average_quality_rating": round(
                sum(r.quality_rating for r in ratings) / total_ratings, 2
            ),
            "average_delivery_rating": round(
                sum(r.delivery_rating for r in ratings) / total_ratings, 2
            ),
            "average_price_rating": round(
                sum(r.price_rating for r in ratings) / total_ratings, 2
            ),
            "average_service_rating": round(
                sum(r.service_rating for r in ratings) / total_ratings, 2
            ),
            "average_communication_rating": round(
                sum(r.communication_rating for r in ratings) / total_ratings, 2
            ),
            "total_orders_placed": total_orders_placed,
            "total_orders_completed": total_orders_completed,
            "total_orders_on_time": total_orders_on_time,
            "on_time_delivery_rate": round(on_time_rate, 2),
            "total_defects": sum(r.defect_count for r in ratings),
            "total_value": sum(r.total_value for r in ratings),
        }

    async def update_rating(
        self,
        rating_id: int,
        data: VendorRatingUpdate,
    ) -> VendorRating:
        """Update a vendor rating."""
        rating = await self.get_rating(rating_id)
        if not rating:
            raise NotFoundException("VendorRating", rating_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rating, field, value)

        # Recalculate overall rating
        ratings = [
            rating.quality_rating,
            rating.delivery_rating,
            rating.price_rating,
            rating.service_rating,
            rating.communication_rating,
        ]
        non_zero_ratings = [r for r in ratings if r > 0]
        rating.overall_rating = (
            sum(non_zero_ratings) / len(non_zero_ratings)
            if non_zero_ratings
            else 0.0
        )

        await self.db.flush()
        await self.db.refresh(rating)

        # Update vendor average rating
        await self._update_vendor_average_rating(rating.vendor_id)

        return rating

    async def delete_rating(self, rating_id: int) -> None:
        """Delete a vendor rating."""
        rating = await self.get_rating(rating_id)
        if not rating:
            raise NotFoundException("VendorRating", rating_id)

        vendor_id = rating.vendor_id
        await self.db.delete(rating)
        await self.db.flush()

        # Update vendor average rating
        await self._update_vendor_average_rating(vendor_id)
