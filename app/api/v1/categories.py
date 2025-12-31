"""Vendor category management API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.vendor import (
    VendorCategoryCreate,
    VendorCategoryUpdate,
    VendorCategoryResponse,
)
from app.services.vendor import VendorService

router = APIRouter()


@router.post(
    "",
    response_model=VendorCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create vendor category",
    description="Create a new vendor category.",
)
async def create_category(
    data: VendorCategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> VendorCategoryResponse:
    """Create a new vendor category."""
    service = VendorService(db)
    category = await service.create_category(data)
    return VendorCategoryResponse.model_validate(category)


@router.get(
    "",
    response_model=List[VendorCategoryResponse],
    summary="List vendor categories",
    description="Get all vendor categories.",
)
async def list_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: AsyncSession = Depends(get_db),
) -> List[VendorCategoryResponse]:
    """List all vendor categories."""
    service = VendorService(db)
    categories = await service.list_categories(include_inactive)
    return [VendorCategoryResponse.model_validate(c) for c in categories]


@router.get(
    "/{category_id}",
    response_model=VendorCategoryResponse,
    summary="Get vendor category",
    description="Get a specific vendor category by ID.",
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> VendorCategoryResponse:
    """Get a vendor category by ID."""
    service = VendorService(db)
    category = await service.get_category(category_id)
    if not category:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("VendorCategory", category_id)
    return VendorCategoryResponse.model_validate(category)


@router.put(
    "/{category_id}",
    response_model=VendorCategoryResponse,
    summary="Update vendor category",
    description="Update a vendor category.",
)
async def update_category(
    category_id: int,
    data: VendorCategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> VendorCategoryResponse:
    """Update a vendor category."""
    service = VendorService(db)
    category = await service.update_category(category_id, data)
    return VendorCategoryResponse.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vendor category",
    description="Delete a vendor category. Cannot delete if vendors are assigned.",
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vendor category."""
    service = VendorService(db)
    await service.delete_category(category_id)
