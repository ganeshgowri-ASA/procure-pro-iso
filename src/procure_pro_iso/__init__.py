"""
Procure-Pro-ISO: Comprehensive ISO-compliant procurement lifecycle management system.

This module provides document parsing capabilities for RFQ (Request for Quote)
documents including Excel, PDF, and CSV formats, with PostgreSQL database integration.
"""

from procure_pro_iso.models.rfq import (
    RFQDocument,
    VendorQuote,
    TechnicalSpecification,
    PriceBreakdown,
    DeliveryTerms,
    ParsedRFQResult,
)
from procure_pro_iso.parsers import RFQParser
from procure_pro_iso.config import settings, get_settings
from procure_pro_iso.database import (
    DatabaseManager,
    get_db,
    get_db_manager,
    init_db,
    RFQRepository,
)
from procure_pro_iso.services import RFQService

__version__ = "0.1.0"
__all__ = [
    # Parser
    "RFQParser",
    # Models
    "RFQDocument",
    "VendorQuote",
    "TechnicalSpecification",
    "PriceBreakdown",
    "DeliveryTerms",
    "ParsedRFQResult",
    # Config
    "settings",
    "get_settings",
    # Database
    "DatabaseManager",
    "get_db",
    "get_db_manager",
    "init_db",
    "RFQRepository",
    # Services
    "RFQService",
]
