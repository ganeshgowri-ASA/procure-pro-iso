#!/usr/bin/env python3
"""
Example script demonstrating RFQ document parsing and database storage.

Usage:
    python scripts/parse_rfq_example.py <file_path>
    python scripts/parse_rfq_example.py tests/fixtures/sample_rfq.csv
"""

import json
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Parse an RFQ document and save to database."""
    if len(sys.argv) < 2:
        print("Usage: python parse_rfq_example.py <file_path>")
        print("\nExample:")
        print("  python scripts/parse_rfq_example.py tests/fixtures/sample_rfq.csv")
        return 1

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    print("=" * 60)
    print("RFQ Document Parser - Procure-Pro-ISO")
    print("=" * 60)
    print(f"\nParsing: {file_path}")

    try:
        from procure_pro_iso.services.rfq_service import RFQService

        # Create service
        service = RFQService()

        # Parse and save
        result = service.parse_and_save(file_path)

        print("\n" + "-" * 40)
        print("PARSING RESULT")
        print("-" * 40)
        print(f"Success: {result['success']}")
        print(f"Source Type: {result['source_type']}")
        print(f"Processing Time: {result['processing_time_ms']}ms")
        print(f"Parse Result ID: {result['parse_result_id']}")
        print(f"RFQ Document ID: {result['rfq_document_id']}")

        if result.get("errors"):
            print(f"\nErrors: {len(result['errors'])}")
            for err in result["errors"]:
                print(f"  - [{err['type']}] {err['message']}")

        if result.get("summary"):
            summary = result["summary"]
            print("\n" + "-" * 40)
            print("DOCUMENT SUMMARY")
            print("-" * 40)
            print(f"RFQ Number: {summary.get('rfq_number', 'N/A')}")
            print(f"RFQ Title: {summary.get('rfq_title', 'N/A')}")
            print(f"Vendor Count: {summary.get('vendor_count', 0)}")
            print(f"Total Items: {summary.get('total_items', 0)}")

        # If we have an RFQ ID, show vendor comparison
        if result["rfq_document_id"]:
            print("\n" + "-" * 40)
            print("VENDOR COMPARISON")
            print("-" * 40)

            comparison = service.compare_vendors(result["rfq_document_id"])

            for vendor in comparison.get("vendors", []):
                print(f"\n{vendor['vendor_name']}:")
                print(f"  Total Amount: ${vendor['total_amount']:,.2f}")
                print(f"  Items: {vendor['item_count']}")

                for item in vendor.get("items", [])[:3]:  # Show first 3 items
                    unit_price = item.get("unit_price", 0)
                    print(f"    - {item['name']}: ${unit_price:,.2f}")

            if comparison.get("lowest_bidder"):
                print(f"\n>>> Lowest Bidder: {comparison['lowest_bidder']}")
                print(f">>> Lowest Amount: ${comparison['lowest_amount']:,.2f}")

        # Show database statistics
        print("\n" + "-" * 40)
        print("DATABASE STATISTICS")
        print("-" * 40)
        stats = service.get_statistics()
        print(f"Total RFQs: {stats['total_rfqs']}")
        print(f"Total Vendors: {stats['total_vendors']}")
        print(f"Total Items: {stats['total_items']}")
        print(f"Total Value: ${stats['total_value']:,.2f}")

        print("\n" + "=" * 60)
        print("Parsing completed successfully!")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
