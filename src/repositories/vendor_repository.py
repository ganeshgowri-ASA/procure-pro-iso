"""Vendor repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.vendor import VendorDB, VendorCreate, VendorUpdate, VendorStatus


class VendorRepository:
    """Repository for vendor database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, vendor_data: VendorCreate) -> VendorDB:
        """Create a new vendor."""
        vendor = VendorDB(
            name=vendor_data.name,
            code=vendor_data.code,
            email=vendor_data.email,
            phone=vendor_data.phone,
            address=vendor_data.address,
            country=vendor_data.country,
            industry=vendor_data.industry,
            status=vendor_data.status,
            certifications=vendor_data.certifications,
            iso_standards=vendor_data.iso_standards,
            quality_rating=vendor_data.quality_rating,
            delivery_rating=vendor_data.delivery_rating,
            price_competitiveness=vendor_data.price_competitiveness,
        )
        self.session.add(vendor)
        await self.session.flush()
        await self.session.refresh(vendor)
        return vendor

    async def get_by_id(self, vendor_id: str) -> Optional[VendorDB]:
        """Get vendor by ID."""
        result = await self.session.execute(
            select(VendorDB).where(VendorDB.id == vendor_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[VendorDB]:
        """Get vendor by code."""
        result = await self.session.execute(
            select(VendorDB).where(VendorDB.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: Optional[VendorStatus] = None,
        industry: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[VendorDB]:
        """Get all vendors with optional filtering."""
        query = select(VendorDB)

        if status:
            query = query.where(VendorDB.status == status)

        if industry:
            query = query.where(VendorDB.industry.ilike(f"%{industry}%"))

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, vendor_id: str, vendor_data: VendorUpdate) -> Optional[VendorDB]:
        """Update a vendor."""
        vendor = await self.get_by_id(vendor_id)
        if not vendor:
            return None

        update_data = vendor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)

        await self.session.flush()
        await self.session.refresh(vendor)
        return vendor

    async def delete(self, vendor_id: str) -> bool:
        """Delete a vendor."""
        result = await self.session.execute(
            delete(VendorDB).where(VendorDB.id == vendor_id)
        )
        return result.rowcount > 0

    async def update_status(self, vendor_id: str, status: VendorStatus) -> Optional[VendorDB]:
        """Update vendor status."""
        vendor = await self.get_by_id(vendor_id)
        if not vendor:
            return None

        vendor.status = status
        await self.session.flush()
        await self.session.refresh(vendor)
        return vendor

    async def get_vendors_dict(self) -> dict[str, VendorDB]:
        """Get all vendors as a dictionary keyed by ID."""
        result = await self.session.execute(select(VendorDB))
        vendors = result.scalars().all()
        return {v.id: v for v in vendors}
