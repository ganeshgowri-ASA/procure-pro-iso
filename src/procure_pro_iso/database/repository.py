"""
Repository layer for RFQ database operations.

Provides high-level data access methods for RFQ documents and related entities.
"""

import time
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from procure_pro_iso.database.models import (
    DeliveryTermsDB,
    EquipmentItemDB,
    ParseResultDB,
    PriceBreakdownDB,
    RFQDocumentDB,
    TechnicalSpecDB,
    VendorQuoteDB,
)
from procure_pro_iso.models.rfq import (
    DeliveryTerms,
    EquipmentItem,
    ParsedRFQResult,
    PriceBreakdown,
    RFQDocument,
    TechnicalSpecification,
    VendorQuote,
)


class RFQRepository:
    """
    Repository for RFQ document database operations.

    Provides CRUD operations and specialized queries for RFQ data.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self.session = session

    # ==================== CREATE OPERATIONS ====================

    def save_parsed_result(
        self,
        result: ParsedRFQResult,
        processing_time_ms: int | None = None,
    ) -> ParseResultDB:
        """
        Save a parsed RFQ result to the database.

        Args:
            result: ParsedRFQResult from parsing operation.
            processing_time_ms: Time taken to parse in milliseconds.

        Returns:
            ParseResultDB instance with generated ID.
        """
        # First save the RFQ document if parsing was successful
        rfq_doc_db = None
        if result.success and result.document:
            rfq_doc_db = self.save_rfq_document(result.document)

        # Create parse result record
        parse_result = ParseResultDB(
            source_file=result.source_file,
            source_type=result.source_type,
            success=result.success,
            error_message=(
                "; ".join(e.message for e in result.parsing_errors)
                if result.parsing_errors
                else None
            ),
            raw_data=result.raw_data,
            metadata=result.metadata,
            processing_time_ms=processing_time_ms,
            rfq_document_id=rfq_doc_db.id if rfq_doc_db else None,
        )

        self.session.add(parse_result)
        self.session.flush()  # Get the ID

        return parse_result

    def save_rfq_document(self, document: RFQDocument) -> RFQDocumentDB:
        """
        Save an RFQ document to the database.

        Args:
            document: RFQDocument Pydantic model.

        Returns:
            RFQDocumentDB instance with generated ID.
        """
        # Check if document with same RFQ number exists
        existing = None
        if document.rfq_number:
            existing = self.get_by_rfq_number(document.rfq_number)

        if existing:
            # Update existing document
            return self._update_rfq_document(existing, document)

        # Create new document
        rfq_db = RFQDocumentDB(
            rfq_number=document.rfq_number,
            rfq_title=document.rfq_title,
            project_name=document.project_name,
            issue_date=document.issue_date,
            due_date=document.due_date,
            buyer_name=document.buyer_name,
            buyer_organization=document.buyer_organization,
        )

        self.session.add(rfq_db)
        self.session.flush()

        # Save vendor quotes
        for quote in document.vendor_quotes:
            self._save_vendor_quote(rfq_db.id, quote)

        return rfq_db

    def _update_rfq_document(
        self, existing: RFQDocumentDB, document: RFQDocument
    ) -> RFQDocumentDB:
        """Update an existing RFQ document."""
        existing.rfq_title = document.rfq_title or existing.rfq_title
        existing.project_name = document.project_name or existing.project_name
        existing.issue_date = document.issue_date or existing.issue_date
        existing.due_date = document.due_date or existing.due_date
        existing.buyer_name = document.buyer_name or existing.buyer_name
        existing.buyer_organization = (
            document.buyer_organization or existing.buyer_organization
        )

        # Add new vendor quotes (don't replace existing ones)
        existing_vendors = {q.vendor_name.lower() for q in existing.vendor_quotes}
        for quote in document.vendor_quotes:
            if quote.vendor_name.lower() not in existing_vendors:
                self._save_vendor_quote(existing.id, quote)

        self.session.flush()
        return existing

    def _save_vendor_quote(
        self, rfq_document_id: UUID, quote: VendorQuote
    ) -> VendorQuoteDB:
        """Save a vendor quote to the database."""
        quote_db = VendorQuoteDB(
            rfq_document_id=rfq_document_id,
            vendor_name=quote.vendor_name,
            vendor_code=quote.vendor_code,
            contact_person=quote.contact_person,
            contact_email=quote.contact_email,
            contact_phone=quote.contact_phone,
            quote_reference=quote.quote_reference,
            quote_date=quote.quote_date,
            validity_date=quote.validity_date,
            status=quote.status.value if quote.status else "received",
            payment_terms=quote.payment_terms,
            total_amount=quote.total_amount,
            currency=quote.currency.value if quote.currency else "USD",
            country_of_origin=quote.country_of_origin,
            notes=quote.notes,
        )

        self.session.add(quote_db)
        self.session.flush()

        # Save delivery terms if present
        if quote.delivery:
            self._save_delivery_terms(quote_db.id, None, quote.delivery)

        # Save equipment items
        for item in quote.items:
            self._save_equipment_item(quote_db.id, item)

        return quote_db

    def _save_equipment_item(
        self, vendor_quote_id: UUID, item: EquipmentItem
    ) -> EquipmentItemDB:
        """Save an equipment item to the database."""
        item_db = EquipmentItemDB(
            vendor_quote_id=vendor_quote_id,
            name=item.name,
            description=item.description,
            model_number=item.model_number,
            manufacturer=item.manufacturer,
            country_of_origin=item.country_of_origin,
            warranty_period=item.warranty_period,
            certifications=item.certifications if item.certifications else None,
        )

        self.session.add(item_db)
        self.session.flush()

        # Save pricing
        if item.pricing:
            self._save_price_breakdown(item_db.id, item.pricing)

        # Save technical specs
        for spec in item.technical_specs:
            self._save_technical_spec(item_db.id, spec)

        # Save item-level delivery terms
        if item.delivery:
            self._save_delivery_terms(None, item_db.id, item.delivery)

        return item_db

    def _save_price_breakdown(
        self, equipment_item_id: UUID, pricing: PriceBreakdown
    ) -> PriceBreakdownDB:
        """Save price breakdown to the database."""
        price_db = PriceBreakdownDB(
            equipment_item_id=equipment_item_id,
            unit_price=pricing.unit_price,
            quantity=pricing.quantity,
            currency=pricing.currency.value if pricing.currency else "USD",
            total_price=pricing.total_price,
            discount_percent=pricing.discount_percent,
            tax_percent=pricing.tax_percent,
            shipping_cost=pricing.shipping_cost,
            installation_cost=pricing.installation_cost,
            warranty_cost=pricing.warranty_cost,
            grand_total=pricing.grand_total,
        )

        self.session.add(price_db)
        self.session.flush()
        return price_db

    def _save_technical_spec(
        self, equipment_item_id: UUID, spec: TechnicalSpecification
    ) -> TechnicalSpecDB:
        """Save technical specification to the database."""
        spec_db = TechnicalSpecDB(
            equipment_item_id=equipment_item_id,
            parameter=spec.parameter,
            value=spec.value,
            unit=spec.unit,
            is_compliant=spec.is_compliant,
            notes=spec.notes,
        )

        self.session.add(spec_db)
        self.session.flush()
        return spec_db

    def _save_delivery_terms(
        self,
        vendor_quote_id: UUID | None,
        equipment_item_id: UUID | None,
        delivery: DeliveryTerms,
    ) -> DeliveryTermsDB:
        """Save delivery terms to the database."""
        delivery_db = DeliveryTermsDB(
            vendor_quote_id=vendor_quote_id,
            equipment_item_id=equipment_item_id,
            incoterm=delivery.incoterm,
            delivery_time_days=delivery.delivery_time_days,
            delivery_time_text=delivery.delivery_time_text,
            delivery_location=delivery.delivery_location,
            shipping_method=delivery.shipping_method,
            partial_shipment_allowed=delivery.partial_shipment_allowed,
        )

        self.session.add(delivery_db)
        self.session.flush()
        return delivery_db

    # ==================== READ OPERATIONS ====================

    def get_by_id(self, rfq_id: UUID) -> RFQDocumentDB | None:
        """
        Get an RFQ document by ID.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            RFQDocumentDB or None if not found.
        """
        return self.session.get(RFQDocumentDB, rfq_id)

    def get_by_rfq_number(self, rfq_number: str) -> RFQDocumentDB | None:
        """
        Get an RFQ document by RFQ number.

        Args:
            rfq_number: RFQ reference number.

        Returns:
            RFQDocumentDB or None if not found.
        """
        stmt = select(RFQDocumentDB).where(RFQDocumentDB.rfq_number == rfq_number)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_with_quotes(self, rfq_id: UUID) -> RFQDocumentDB | None:
        """
        Get an RFQ document with all vendor quotes loaded.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            RFQDocumentDB with vendor_quotes loaded, or None.
        """
        stmt = (
            select(RFQDocumentDB)
            .where(RFQDocumentDB.id == rfq_id)
            .options(
                joinedload(RFQDocumentDB.vendor_quotes).joinedload(VendorQuoteDB.items)
            )
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[RFQDocumentDB]:
        """
        List all RFQ documents with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            status: Filter by status.

        Returns:
            List of RFQDocumentDB instances.
        """
        stmt = select(RFQDocumentDB).offset(skip).limit(limit)

        if status:
            stmt = stmt.where(RFQDocumentDB.status == status)

        stmt = stmt.order_by(RFQDocumentDB.created_at.desc())

        return list(self.session.execute(stmt).scalars().all())

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RFQDocumentDB]:
        """
        Search RFQ documents by keyword.

        Args:
            query: Search query string.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of matching RFQDocumentDB instances.
        """
        search_pattern = f"%{query}%"
        stmt = (
            select(RFQDocumentDB)
            .where(
                or_(
                    RFQDocumentDB.rfq_number.ilike(search_pattern),
                    RFQDocumentDB.rfq_title.ilike(search_pattern),
                    RFQDocumentDB.project_name.ilike(search_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(RFQDocumentDB.created_at.desc())
        )

        return list(self.session.execute(stmt).scalars().all())

    def get_vendor_quotes(self, rfq_id: UUID) -> list[VendorQuoteDB]:
        """
        Get all vendor quotes for an RFQ.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            List of VendorQuoteDB instances.
        """
        stmt = (
            select(VendorQuoteDB)
            .where(VendorQuoteDB.rfq_document_id == rfq_id)
            .options(joinedload(VendorQuoteDB.items))
        )
        return list(self.session.execute(stmt).unique().scalars().all())

    def get_quote_by_vendor(
        self, rfq_id: UUID, vendor_name: str
    ) -> VendorQuoteDB | None:
        """
        Get a specific vendor's quote for an RFQ.

        Args:
            rfq_id: UUID of the RFQ document.
            vendor_name: Name of the vendor.

        Returns:
            VendorQuoteDB or None if not found.
        """
        stmt = (
            select(VendorQuoteDB)
            .where(
                and_(
                    VendorQuoteDB.rfq_document_id == rfq_id,
                    VendorQuoteDB.vendor_name.ilike(vendor_name),
                )
            )
            .options(joinedload(VendorQuoteDB.items))
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    # ==================== STATISTICS ====================

    def get_statistics(self) -> dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics.
        """
        rfq_count = self.session.execute(
            select(func.count(RFQDocumentDB.id))
        ).scalar_one()

        vendor_count = self.session.execute(
            select(func.count(VendorQuoteDB.id))
        ).scalar_one()

        item_count = self.session.execute(
            select(func.count(EquipmentItemDB.id))
        ).scalar_one()

        total_value = self.session.execute(
            select(func.sum(VendorQuoteDB.total_amount))
        ).scalar_one() or Decimal("0")

        return {
            "total_rfqs": rfq_count,
            "total_vendors": vendor_count,
            "total_items": item_count,
            "total_value": float(total_value),
        }

    # ==================== DELETE OPERATIONS ====================

    def delete(self, rfq_id: UUID) -> bool:
        """
        Delete an RFQ document and all related data.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            True if deleted, False if not found.
        """
        rfq_doc = self.get_by_id(rfq_id)
        if rfq_doc:
            self.session.delete(rfq_doc)
            self.session.flush()
            return True
        return False

    def delete_vendor_quote(self, quote_id: UUID) -> bool:
        """
        Delete a vendor quote.

        Args:
            quote_id: UUID of the vendor quote.

        Returns:
            True if deleted, False if not found.
        """
        quote = self.session.get(VendorQuoteDB, quote_id)
        if quote:
            self.session.delete(quote)
            self.session.flush()
            return True
        return False

    # ==================== CONVERSION ====================

    def to_pydantic(self, rfq_db: RFQDocumentDB) -> RFQDocument:
        """
        Convert database model to Pydantic model.

        Args:
            rfq_db: RFQDocumentDB instance.

        Returns:
            RFQDocument Pydantic model.
        """
        vendor_quotes = []
        for quote_db in rfq_db.vendor_quotes:
            items = []
            for item_db in quote_db.items:
                # Convert pricing
                pricing = None
                if item_db.pricing:
                    from procure_pro_iso.models.rfq import Currency

                    pricing = PriceBreakdown(
                        unit_price=item_db.pricing.unit_price,
                        quantity=item_db.pricing.quantity,
                        currency=Currency(item_db.pricing.currency),
                        total_price=item_db.pricing.total_price,
                        discount_percent=item_db.pricing.discount_percent,
                        tax_percent=item_db.pricing.tax_percent,
                        shipping_cost=item_db.pricing.shipping_cost,
                        installation_cost=item_db.pricing.installation_cost,
                        warranty_cost=item_db.pricing.warranty_cost,
                        grand_total=item_db.pricing.grand_total,
                    )

                # Convert tech specs
                tech_specs = [
                    TechnicalSpecification(
                        parameter=spec.parameter,
                        value=spec.value,
                        unit=spec.unit,
                        is_compliant=spec.is_compliant,
                        notes=spec.notes,
                    )
                    for spec in item_db.technical_specs
                ]

                # Convert delivery
                delivery = None
                if item_db.delivery_terms:
                    delivery = DeliveryTerms(
                        incoterm=item_db.delivery_terms.incoterm,
                        delivery_time_days=item_db.delivery_terms.delivery_time_days,
                        delivery_time_text=item_db.delivery_terms.delivery_time_text,
                        delivery_location=item_db.delivery_terms.delivery_location,
                        shipping_method=item_db.delivery_terms.shipping_method,
                        partial_shipment_allowed=item_db.delivery_terms.partial_shipment_allowed,
                    )

                items.append(
                    EquipmentItem(
                        name=item_db.name,
                        description=item_db.description,
                        model_number=item_db.model_number,
                        manufacturer=item_db.manufacturer,
                        country_of_origin=item_db.country_of_origin,
                        pricing=pricing,
                        technical_specs=tech_specs,
                        delivery=delivery,
                        warranty_period=item_db.warranty_period,
                        certifications=item_db.certifications or [],
                    )
                )

            from procure_pro_iso.models.rfq import Currency, QuoteStatus

            vendor_quotes.append(
                VendorQuote(
                    vendor_name=quote_db.vendor_name,
                    vendor_code=quote_db.vendor_code,
                    contact_person=quote_db.contact_person,
                    contact_email=quote_db.contact_email,
                    contact_phone=quote_db.contact_phone,
                    quote_reference=quote_db.quote_reference,
                    quote_date=quote_db.quote_date,
                    validity_date=quote_db.validity_date,
                    status=QuoteStatus(quote_db.status),
                    items=items,
                    payment_terms=quote_db.payment_terms,
                    total_amount=quote_db.total_amount,
                    currency=Currency(quote_db.currency),
                    notes=quote_db.notes,
                    country_of_origin=quote_db.country_of_origin,
                )
            )

        return RFQDocument(
            rfq_number=rfq_db.rfq_number,
            rfq_title=rfq_db.rfq_title,
            project_name=rfq_db.project_name,
            issue_date=rfq_db.issue_date,
            due_date=rfq_db.due_date,
            buyer_name=rfq_db.buyer_name,
            buyer_organization=rfq_db.buyer_organization,
            vendor_quotes=vendor_quotes,
        )
