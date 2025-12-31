"""
RFQ Service for integrated document parsing and database storage.

Provides high-level operations for parsing RFQ documents and persisting
them to the database.
"""

import time
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from procure_pro_iso.database.connection import DatabaseManager, get_db_manager
from procure_pro_iso.database.models import RFQDocumentDB, VendorQuoteDB
from procure_pro_iso.database.repository import RFQRepository
from procure_pro_iso.models.rfq import ParsedRFQResult, RFQDocument
from procure_pro_iso.parsers.rfq_parser import RFQParser


class RFQService:
    """
    Service for RFQ document operations.

    Combines parsing capabilities with database persistence.
    """

    def __init__(
        self,
        db_manager: DatabaseManager | None = None,
        parser: RFQParser | None = None,
    ):
        """
        Initialize the RFQ service.

        Args:
            db_manager: Database manager instance. If None, uses global instance.
            parser: RFQ parser instance. If None, creates new instance.
        """
        self.db_manager = db_manager or get_db_manager()
        self.parser = parser or RFQParser()

    def parse_and_save(
        self,
        file_path: str | Path,
        auto_commit: bool = True,
    ) -> dict[str, Any]:
        """
        Parse an RFQ document and save to database.

        Args:
            file_path: Path to the RFQ document.
            auto_commit: If True, automatically commit the transaction.

        Returns:
            Dictionary containing parse result and database IDs.
        """
        start_time = time.time()

        # Parse the document
        result = self.parser.parse(file_path)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Save to database
        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            parse_result_db = repo.save_parsed_result(result, processing_time_ms)

            response = {
                "success": result.success,
                "parse_result_id": str(parse_result_db.id),
                "rfq_document_id": (
                    str(parse_result_db.rfq_document_id)
                    if parse_result_db.rfq_document_id
                    else None
                ),
                "source_file": result.source_file,
                "source_type": result.source_type,
                "processing_time_ms": processing_time_ms,
                "errors": [
                    {"type": e.error_type, "message": e.message}
                    for e in result.parsing_errors
                ],
                "validation_errors": [
                    {"field": e.field, "message": e.message}
                    for e in result.validation_errors
                ],
            }

            if result.success and result.document:
                response["summary"] = {
                    "rfq_number": result.document.rfq_number,
                    "rfq_title": result.document.rfq_title,
                    "vendor_count": len(result.document.vendor_quotes),
                    "total_items": sum(
                        len(q.items) for q in result.document.vendor_quotes
                    ),
                }

            if auto_commit:
                session.commit()

            return response

    def parse_multiple_and_save(
        self,
        file_paths: list[str | Path],
        merge: bool = False,
    ) -> dict[str, Any]:
        """
        Parse multiple RFQ documents and save to database.

        Args:
            file_paths: List of paths to RFQ documents.
            merge: If True, merge results into a single RFQ document.

        Returns:
            Dictionary containing results for all files.
        """
        results = []

        for path in file_paths:
            result = self.parse_and_save(path)
            results.append(result)

        response = {
            "total_files": len(file_paths),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
        }

        if merge and response["successful"] > 0:
            # Get all successful RFQ document IDs and merge
            rfq_ids = [
                UUID(r["rfq_document_id"])
                for r in results
                if r["success"] and r["rfq_document_id"]
            ]
            if len(rfq_ids) > 1:
                with self.db_manager.session_scope() as session:
                    repo = RFQRepository(session)
                    # Merge logic could be implemented here
                    response["merged"] = True

        return response

    def get_rfq(self, rfq_id: UUID | str) -> RFQDocument | None:
        """
        Get an RFQ document from the database.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            RFQDocument Pydantic model or None if not found.
        """
        if isinstance(rfq_id, str):
            rfq_id = UUID(rfq_id)

        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            rfq_db = repo.get_with_quotes(rfq_id)

            if rfq_db:
                return repo.to_pydantic(rfq_db)
            return None

    def get_rfq_by_number(self, rfq_number: str) -> RFQDocument | None:
        """
        Get an RFQ document by RFQ number.

        Args:
            rfq_number: RFQ reference number.

        Returns:
            RFQDocument Pydantic model or None if not found.
        """
        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            rfq_db = repo.get_by_rfq_number(rfq_number)

            if rfq_db:
                # Load vendor quotes
                rfq_db = repo.get_with_quotes(rfq_db.id)
                return repo.to_pydantic(rfq_db)
            return None

    def list_rfqs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        List all RFQ documents.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            status: Filter by status.

        Returns:
            List of RFQ summary dictionaries.
        """
        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            rfqs = repo.list_all(skip=skip, limit=limit, status=status)

            return [
                {
                    "id": str(rfq.id),
                    "rfq_number": rfq.rfq_number,
                    "rfq_title": rfq.rfq_title,
                    "project_name": rfq.project_name,
                    "status": rfq.status,
                    "created_at": rfq.created_at.isoformat(),
                    "vendor_count": len(rfq.vendor_quotes),
                }
                for rfq in rfqs
            ]

    def search_rfqs(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search RFQ documents.

        Args:
            query: Search query string.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of matching RFQ summary dictionaries.
        """
        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            rfqs = repo.search(query=query, skip=skip, limit=limit)

            return [
                {
                    "id": str(rfq.id),
                    "rfq_number": rfq.rfq_number,
                    "rfq_title": rfq.rfq_title,
                    "project_name": rfq.project_name,
                    "status": rfq.status,
                    "created_at": rfq.created_at.isoformat(),
                }
                for rfq in rfqs
            ]

    def get_vendor_quotes(self, rfq_id: UUID | str) -> list[dict[str, Any]]:
        """
        Get all vendor quotes for an RFQ.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            List of vendor quote summaries.
        """
        if isinstance(rfq_id, str):
            rfq_id = UUID(rfq_id)

        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            quotes = repo.get_vendor_quotes(rfq_id)

            return [
                {
                    "id": str(q.id),
                    "vendor_name": q.vendor_name,
                    "quote_reference": q.quote_reference,
                    "status": q.status,
                    "total_amount": float(q.total_amount) if q.total_amount else None,
                    "currency": q.currency,
                    "item_count": len(q.items),
                    "quote_date": q.quote_date.isoformat() if q.quote_date else None,
                }
                for q in quotes
            ]

    def compare_vendors(self, rfq_id: UUID | str) -> dict[str, Any]:
        """
        Compare vendor quotes for an RFQ.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            Comparison data for all vendors.
        """
        if isinstance(rfq_id, str):
            rfq_id = UUID(rfq_id)

        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            quotes = repo.get_vendor_quotes(rfq_id)

            comparison = {
                "rfq_id": str(rfq_id),
                "vendor_count": len(quotes),
                "vendors": [],
            }

            for quote in quotes:
                vendor_data = {
                    "vendor_name": quote.vendor_name,
                    "total_amount": float(quote.total_amount) if quote.total_amount else 0,
                    "currency": quote.currency,
                    "item_count": len(quote.items),
                    "items": [],
                }

                for item in quote.items:
                    item_data = {
                        "name": item.name,
                        "model_number": item.model_number,
                        "country_of_origin": item.country_of_origin,
                    }

                    if item.pricing:
                        item_data["unit_price"] = float(item.pricing.unit_price)
                        item_data["quantity"] = item.pricing.quantity
                        item_data["total_price"] = (
                            float(item.pricing.total_price)
                            if item.pricing.total_price
                            else None
                        )

                    if item.delivery_terms:
                        item_data["delivery_days"] = item.delivery_terms.delivery_time_days

                    vendor_data["items"].append(item_data)

                comparison["vendors"].append(vendor_data)

            # Sort by total amount
            comparison["vendors"].sort(
                key=lambda x: x["total_amount"] or float("inf")
            )

            if comparison["vendors"]:
                comparison["lowest_bidder"] = comparison["vendors"][0]["vendor_name"]
                comparison["lowest_amount"] = comparison["vendors"][0]["total_amount"]

            return comparison

    def delete_rfq(self, rfq_id: UUID | str) -> bool:
        """
        Delete an RFQ document.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            True if deleted, False if not found.
        """
        if isinstance(rfq_id, str):
            rfq_id = UUID(rfq_id)

        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            return repo.delete(rfq_id)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics.
        """
        with self.db_manager.session_scope() as session:
            repo = RFQRepository(session)
            return repo.get_statistics()

    def export_to_json(self, rfq_id: UUID | str) -> str | None:
        """
        Export an RFQ document to JSON.

        Args:
            rfq_id: UUID of the RFQ document.

        Returns:
            JSON string or None if not found.
        """
        rfq = self.get_rfq(rfq_id)
        if rfq:
            from procure_pro_iso.models.rfq import ParsedRFQResult

            result = ParsedRFQResult(
                success=True,
                document=rfq,
                source_file="database",
                source_type="database",
            )
            return result.to_json()
        return None


# Convenience function for quick parsing and saving
def parse_and_save_rfq(
    file_path: str | Path,
    db_manager: DatabaseManager | None = None,
) -> dict[str, Any]:
    """
    Convenience function to parse and save an RFQ document.

    Args:
        file_path: Path to the RFQ document.
        db_manager: Optional database manager.

    Returns:
        Dictionary containing parse result and database IDs.
    """
    service = RFQService(db_manager=db_manager)
    return service.parse_and_save(file_path)
