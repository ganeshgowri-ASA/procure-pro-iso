"""
Compliance Scorer - ISO standards and certification compliance evaluation.

Evaluates vendor compliance with:
- ISO 9001, ISO 14001, ISO 17025, ISO 27001, ISO 45001
- IATF 16949, ISO 13485, ISO 22000, AS 9100
- Custom certifications
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.models.tbe import (
    ComplianceCheck,
    ISOStandard,
    VendorBid,
)
from src.models.vendor import Vendor


@dataclass
class ComplianceConfig:
    """Configuration for compliance scoring."""

    # Weight distribution between ISO and other certifications
    iso_weight: float = 0.7
    certification_weight: float = 0.3

    # Mandatory compliance threshold
    mandatory_threshold: float = 100.0

    # Partial credit for related standards
    allow_partial_credit: bool = True
    partial_credit_ratio: float = 0.5

    # Standard relationships (related standards that can provide partial credit)
    standard_relationships: dict = None

    def __post_init__(self):
        if self.standard_relationships is None:
            self.standard_relationships = {
                "ISO 9001": ["IATF 16949", "AS 9100", "ISO 13485"],
                "ISO 14001": ["ISO 45001"],
                "ISO 17025": ["ISO 9001"],
                "ISO 27001": [],
                "ISO 45001": ["ISO 14001"],
                "IATF 16949": ["ISO 9001"],
                "ISO 13485": ["ISO 9001"],
                "ISO 22000": ["ISO 9001"],
                "AS 9100": ["ISO 9001"],
            }


class ComplianceScorer:
    """
    ISO and Certification Compliance Scorer.

    Evaluates vendor compliance with required standards and certifications,
    providing detailed compliance checks and scoring.
    """

    def __init__(self, config: Optional[ComplianceConfig] = None):
        """Initialize compliance scorer with configuration."""
        self.config = config or ComplianceConfig()

    def check_compliance(
        self,
        bid: VendorBid,
        vendor: Vendor,
        required_standards: list[ISOStandard],
        required_certifications: list[str],
    ) -> ComplianceCheck:
        """
        Perform compliance check for a vendor bid.

        Args:
            bid: The vendor bid
            vendor: The vendor information
            required_standards: Required ISO standards
            required_certifications: Required certifications

        Returns:
            Complete compliance check result
        """
        # Normalize provided standards and certs
        provided_iso = self._normalize_standards(bid.iso_compliance + vendor.iso_standards)
        provided_certs = self._normalize_certs(bid.certifications + vendor.certifications)

        # Required standards as strings
        required_iso_strings = [std.value for std in required_standards]

        # Check ISO compliance
        iso_score, missing_iso = self._score_iso_compliance(
            provided=provided_iso,
            required=required_iso_strings,
        )

        # Check certification compliance
        cert_score, missing_certs = self._score_certification_compliance(
            provided=provided_certs,
            required=required_certifications,
        )

        # Calculate overall compliance score
        if required_standards and required_certifications:
            overall_score = (
                iso_score * self.config.iso_weight
                + cert_score * self.config.certification_weight
            )
        elif required_standards:
            overall_score = iso_score
        elif required_certifications:
            overall_score = cert_score
        else:
            overall_score = 100.0  # No requirements = full compliance

        # Determine if fully compliant
        is_compliant = len(missing_iso) == 0 and len(missing_certs) == 0

        # Generate compliance notes
        notes = self._generate_compliance_notes(
            iso_score, cert_score, missing_iso, missing_certs
        )

        return ComplianceCheck(
            vendor_id=bid.vendor_id,
            vendor_name=vendor.name,
            required_iso_standards=required_standards,
            provided_iso_standards=provided_iso,
            required_certifications=required_certifications,
            provided_certifications=provided_certs,
            iso_compliance_score=iso_score,
            certification_compliance_score=cert_score,
            overall_compliance_score=overall_score,
            missing_iso_standards=missing_iso,
            missing_certifications=missing_certs,
            is_compliant=is_compliant,
            compliance_notes=notes,
        )

    def _normalize_standards(self, standards: list[str]) -> list[str]:
        """Normalize ISO standard names for comparison."""
        normalized = []
        for std in standards:
            if not std:
                continue
            # Normalize format (e.g., "ISO9001" -> "ISO 9001")
            std_upper = std.upper().strip()
            std_upper = std_upper.replace("-", " ").replace("_", " ")

            # Handle common variations
            if std_upper.startswith("ISO") and not std_upper.startswith("ISO "):
                std_upper = "ISO " + std_upper[3:]

            normalized.append(std_upper)

        return list(set(normalized))

    def _normalize_certs(self, certs: list[str]) -> list[str]:
        """Normalize certification names for comparison."""
        return list(set(c.upper().strip() for c in certs if c))

    def _score_iso_compliance(
        self,
        provided: list[str],
        required: list[str],
    ) -> tuple[float, list[str]]:
        """
        Score ISO compliance.

        Returns:
            Tuple of (compliance score, missing standards)
        """
        if not required:
            return 100.0, []

        missing = []
        matches = 0

        for req in required:
            req_normalized = req.upper().strip()

            # Direct match
            if req_normalized in provided or any(
                req_normalized in p for p in provided
            ):
                matches += 1
                continue

            # Check for partial credit from related standards
            if self.config.allow_partial_credit:
                related = self.config.standard_relationships.get(req, [])
                related_normalized = [r.upper().strip() for r in related]

                if any(r in provided for r in related_normalized):
                    matches += self.config.partial_credit_ratio
                    continue

            missing.append(req)

        score = (matches / len(required)) * 100 if required else 100.0
        return round(score, 2), missing

    def _score_certification_compliance(
        self,
        provided: list[str],
        required: list[str],
    ) -> tuple[float, list[str]]:
        """
        Score certification compliance.

        Returns:
            Tuple of (compliance score, missing certifications)
        """
        if not required:
            return 100.0, []

        missing = []
        matches = 0

        for req in required:
            req_normalized = req.upper().strip()

            # Direct match or partial match
            if req_normalized in provided or any(
                req_normalized in p for p in provided
            ):
                matches += 1
            else:
                missing.append(req)

        score = (matches / len(required)) * 100 if required else 100.0
        return round(score, 2), missing

    def _generate_compliance_notes(
        self,
        iso_score: float,
        cert_score: float,
        missing_iso: list[str],
        missing_certs: list[str],
    ) -> str:
        """Generate descriptive compliance notes."""
        notes_parts = []

        if iso_score >= 100 and cert_score >= 100:
            notes_parts.append("Full compliance with all requirements.")
        else:
            if iso_score < 100:
                notes_parts.append(
                    f"ISO compliance: {iso_score:.1f}%. "
                    f"Missing: {', '.join(missing_iso) if missing_iso else 'None'}."
                )
            if cert_score < 100:
                notes_parts.append(
                    f"Certification compliance: {cert_score:.1f}%. "
                    f"Missing: {', '.join(missing_certs) if missing_certs else 'None'}."
                )

        if iso_score >= 80 and cert_score >= 80:
            notes_parts.append("Minor compliance gaps may be acceptable.")
        elif iso_score >= 50 or cert_score >= 50:
            notes_parts.append("Significant compliance gaps require attention.")
        elif iso_score < 50 or cert_score < 50:
            notes_parts.append("Critical compliance issues identified.")

        return " ".join(notes_parts)

    def check_all_vendors(
        self,
        bids: list[VendorBid],
        vendors: dict[UUID, Vendor],
        required_standards: list[ISOStandard],
        required_certifications: list[str],
    ) -> list[ComplianceCheck]:
        """
        Check compliance for all vendor bids.

        Args:
            bids: List of vendor bids
            vendors: Dictionary mapping vendor IDs to Vendor objects
            required_standards: Required ISO standards
            required_certifications: Required certifications

        Returns:
            List of compliance checks
        """
        checks = []

        for bid in bids:
            vendor = vendors.get(bid.vendor_id)
            if not vendor:
                continue

            check = self.check_compliance(
                bid=bid,
                vendor=vendor,
                required_standards=required_standards,
                required_certifications=required_certifications,
            )
            checks.append(check)

        return checks

    def get_compliance_summary(
        self,
        checks: list[ComplianceCheck],
    ) -> dict:
        """
        Generate compliance summary for all vendors.

        Args:
            checks: List of compliance checks

        Returns:
            Summary dictionary
        """
        if not checks:
            return {"message": "No compliance checks available"}

        compliant_count = sum(1 for c in checks if c.is_compliant)
        scores = [c.overall_compliance_score for c in checks]

        # Group by compliance level
        high_compliance = [c for c in checks if c.overall_compliance_score >= 80]
        medium_compliance = [c for c in checks if 50 <= c.overall_compliance_score < 80]
        low_compliance = [c for c in checks if c.overall_compliance_score < 50]

        # Find common missing standards
        all_missing_iso = []
        all_missing_certs = []
        for check in checks:
            all_missing_iso.extend(check.missing_iso_standards)
            all_missing_certs.extend(check.missing_certifications)

        from collections import Counter

        common_missing_iso = Counter(all_missing_iso).most_common(5)
        common_missing_certs = Counter(all_missing_certs).most_common(5)

        return {
            "vendor_count": len(checks),
            "compliance_statistics": {
                "fully_compliant": compliant_count,
                "partially_compliant": len(checks) - compliant_count,
                "compliance_rate": round(compliant_count / len(checks) * 100, 2),
            },
            "score_statistics": {
                "average": round(sum(scores) / len(scores), 2),
                "minimum": round(min(scores), 2),
                "maximum": round(max(scores), 2),
            },
            "compliance_levels": {
                "high_compliance_count": len(high_compliance),
                "medium_compliance_count": len(medium_compliance),
                "low_compliance_count": len(low_compliance),
            },
            "common_gaps": {
                "missing_iso_standards": [
                    {"standard": std, "count": count}
                    for std, count in common_missing_iso
                ],
                "missing_certifications": [
                    {"certification": cert, "count": count}
                    for cert, count in common_missing_certs
                ],
            },
        }

    def get_vendor_compliance_rank(
        self,
        checks: list[ComplianceCheck],
    ) -> list[dict]:
        """
        Rank vendors by compliance score.

        Args:
            checks: List of compliance checks

        Returns:
            Sorted list of vendor compliance ranks
        """
        sorted_checks = sorted(
            checks, key=lambda c: c.overall_compliance_score, reverse=True
        )

        return [
            {
                "rank": idx + 1,
                "vendor_id": str(check.vendor_id),
                "vendor_name": check.vendor_name,
                "overall_score": round(check.overall_compliance_score, 2),
                "iso_score": round(check.iso_compliance_score, 2),
                "certification_score": round(check.certification_compliance_score, 2),
                "is_compliant": check.is_compliant,
            }
            for idx, check in enumerate(sorted_checks)
        ]
