"""
Tests for Compliance Scorer.

Tests ISO standards and certification compliance evaluation.
"""

from uuid import UUID

import pytest

from src.models.vendor import Vendor
from src.models.tbe import VendorBid, ISOStandard
from src.services.compliance_scorer import ComplianceScorer, ComplianceConfig


class TestComplianceScorer:
    """Test suite for Compliance Scorer."""

    @pytest.fixture
    def compliance_scorer(self) -> ComplianceScorer:
        """Create compliance scorer with default config."""
        return ComplianceScorer()

    def test_full_compliance(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test vendor with full compliance."""
        # Find a bid that has the required standards
        bid = sample_bids[1]  # Beta has ISO 9001 and ISO 17025
        vendor = sample_vendors[bid.vendor_id]

        check = compliance_scorer.check_compliance(
            bid=bid,
            vendor=vendor,
            required_standards=[ISOStandard.ISO_9001, ISOStandard.ISO_17025],
            required_certifications=[],
        )

        assert check.is_compliant
        assert check.iso_compliance_score == 100.0
        assert check.overall_compliance_score == 100.0
        assert len(check.missing_iso_standards) == 0

    def test_partial_compliance(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test vendor with partial compliance."""
        # Epsilon only has ISO 9001
        bid = sample_bids[4]  # Epsilon
        vendor = sample_vendors[bid.vendor_id]

        check = compliance_scorer.check_compliance(
            bid=bid,
            vendor=vendor,
            required_standards=[ISOStandard.ISO_9001, ISOStandard.ISO_17025, ISOStandard.ISO_14001],
            required_certifications=["CE Mark", "UL Listed"],
        )

        assert not check.is_compliant
        assert check.iso_compliance_score < 100.0
        assert len(check.missing_iso_standards) > 0

    def test_no_requirements_full_compliance(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test that no requirements means full compliance."""
        bid = sample_bids[0]
        vendor = sample_vendors[bid.vendor_id]

        check = compliance_scorer.check_compliance(
            bid=bid,
            vendor=vendor,
            required_standards=[],
            required_certifications=[],
        )

        assert check.is_compliant
        assert check.overall_compliance_score == 100.0

    def test_standard_normalization(
        self,
        compliance_scorer: ComplianceScorer,
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test that standard names are normalized for comparison."""
        from uuid import uuid4

        vendor = list(sample_vendors.values())[0]

        # Create bid with different formatting
        bid = VendorBid(
            id=uuid4(),
            vendor_id=vendor.id,
            bid_reference="TEST-001",
            unit_price=1000.0,
            quantity=1,
            total_price=1000.0,
            delivery_days=30,
            iso_compliance=["ISO9001", "iso 17025", "ISO-14001"],  # Various formats
        )

        check = compliance_scorer.check_compliance(
            bid=bid,
            vendor=vendor,
            required_standards=[ISOStandard.ISO_9001, ISOStandard.ISO_17025],
            required_certifications=[],
        )

        # Should match despite formatting differences
        assert check.iso_compliance_score == 100.0

    def test_check_all_vendors(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test checking compliance for all vendors."""
        checks = compliance_scorer.check_all_vendors(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=[ISOStandard.ISO_9001],
            required_certifications=[],
        )

        assert len(checks) == len(sample_bids)

        # All vendors have ISO 9001
        for check in checks:
            assert check.iso_compliance_score == 100.0

    def test_compliance_summary(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test compliance summary generation."""
        checks = compliance_scorer.check_all_vendors(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=[ISOStandard.ISO_9001, ISOStandard.ISO_17025],
            required_certifications=["CE Mark"],
        )

        summary = compliance_scorer.get_compliance_summary(checks)

        assert "vendor_count" in summary
        assert "compliance_statistics" in summary
        assert "score_statistics" in summary
        assert "compliance_levels" in summary
        assert "common_gaps" in summary

        assert summary["vendor_count"] == len(sample_bids)

    def test_vendor_compliance_rank(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test vendor ranking by compliance score."""
        checks = compliance_scorer.check_all_vendors(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=[ISOStandard.ISO_9001, ISOStandard.ISO_17025],
            required_certifications=[],
        )

        ranking = compliance_scorer.get_vendor_compliance_rank(checks)

        assert len(ranking) == len(checks)

        # Verify ranking order (highest score first)
        for i in range(len(ranking) - 1):
            assert ranking[i]["overall_score"] >= ranking[i + 1]["overall_score"]
            assert ranking[i]["rank"] < ranking[i + 1]["rank"]

    def test_partial_credit_for_related_standards(self):
        """Test partial credit for related ISO standards."""
        config = ComplianceConfig(allow_partial_credit=True, partial_credit_ratio=0.5)
        scorer = ComplianceScorer(config=config)

        from uuid import uuid4
        from src.models.vendor import Vendor, VendorStatus

        vendor = Vendor(
            id=uuid4(),
            name="Test Vendor",
            code="TEST-001",
            status=VendorStatus.ACTIVE,
            iso_standards=["IATF 16949"],  # Related to ISO 9001
        )

        bid = VendorBid(
            id=uuid4(),
            vendor_id=vendor.id,
            bid_reference="TEST-001",
            unit_price=1000.0,
            quantity=1,
            total_price=1000.0,
            delivery_days=30,
            iso_compliance=["IATF 16949"],
        )

        check = scorer.check_compliance(
            bid=bid,
            vendor=vendor,
            required_standards=[ISOStandard.ISO_9001],  # IATF 16949 is related
            required_certifications=[],
        )

        # Should get partial credit (50%)
        assert check.iso_compliance_score == 50.0

    def test_compliance_notes_generation(
        self,
        compliance_scorer: ComplianceScorer,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test that compliance notes are generated."""
        bid = sample_bids[0]
        vendor = sample_vendors[bid.vendor_id]

        check = compliance_scorer.check_compliance(
            bid=bid,
            vendor=vendor,
            required_standards=[ISOStandard.ISO_9001],
            required_certifications=[],
        )

        assert check.compliance_notes is not None
        assert len(check.compliance_notes) > 0

    def test_empty_checks_summary(self, compliance_scorer: ComplianceScorer):
        """Test summary with no compliance checks."""
        summary = compliance_scorer.get_compliance_summary([])
        assert "message" in summary


class TestISOStandards:
    """Tests for ISO standard enumeration."""

    def test_all_standards_have_values(self):
        """Test all ISO standards have proper values."""
        for standard in ISOStandard:
            assert standard.value is not None
            assert len(standard.value) > 0

    def test_standard_values_format(self):
        """Test ISO standard values are properly formatted."""
        # All should start with 'ISO' or be specific standards like IATF/AS
        for standard in ISOStandard:
            assert (
                standard.value.startswith("ISO")
                or standard.value.startswith("IATF")
                or standard.value.startswith("AS")
            )
