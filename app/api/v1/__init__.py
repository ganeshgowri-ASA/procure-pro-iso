"""API v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.vendors import router as vendors_router
from app.api.v1.categories import router as categories_router
from app.api.v1.rfq import router as rfq_router
from app.api.v1.quotations import router as quotations_router

api_router = APIRouter()

api_router.include_router(vendors_router, prefix="/vendors", tags=["Vendors"])
api_router.include_router(categories_router, prefix="/categories", tags=["Vendor Categories"])
api_router.include_router(rfq_router, prefix="/rfq", tags=["RFQ"])
api_router.include_router(quotations_router, prefix="/quotations", tags=["Quotations"])
