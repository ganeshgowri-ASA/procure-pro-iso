"""
Tests for TCO Calculator.

Tests Total Cost of Ownership calculations and analysis.
"""

from uuid import UUID

import pytest

from src.models.vendor import Vendor
from src.models.tbe import VendorBid
from src.services.tco_calculator import TCOCalculator, TCOConfig


class TestTCOCalculator:
    """Test suite for TCO Calculator."""

    @pytest.fixture
    def tco_calculator(self) -> TCOCalculator:
        """Create TCO calculator with default config."""
        return TCOCalculator()

    def test_calculate_tco_single_vendor(
        self,
        tco_calculator: TCOCalculator,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test TCO calculation for a single vendor."""
        bid = sample_bids[0]
        vendor = sample_vendors[bid.vendor_id]

        tco = tco_calculator.calculate_tco(bid, vendor)

        # Verify basic structure
        assert tco.bid_id == bid.id
        assert tco.vendor_id == bid.vendor_id
        assert tco.vendor_name == vendor.name

        # Verify cost calculations
        assert tco.base_cost == bid.unit_price * bid.quantity
        assert tco.acquisition_cost > 0
        assert tco.total_cost_of_ownership > 0
        assert tco.tco_per_year > 0
        assert tco.tco_per_unit > 0

        # Acquisition cost should include all one-time costs
        expected_acquisition = (
            tco.base_cost
            + bid.shipping_cost
            + bid.installation_cost
            + bid.training_cost
        )
        assert tco.acquisition_cost == expected_acquisition

    def test_calculate_all_tco(
        self,
        tco_calculator: TCOCalculator,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test TCO calculation for all vendors."""
        calculations = tco_calculator.calculate_all_tco(sample_bids, sample_vendors)

        assert len(calculations) == len(sample_bids)

        # All should have normalized scores
        for calc in calculations:
            assert 0 <= calc.tco_score <= 100
            assert calc.tco_rank >= 1
            assert calc.tco_rank <= len(sample_bids)

    def test_tco_ranking_lowest_is_best(
        self,
        tco_calculator: TCOCalculator,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test that lowest TCO gets rank 1 and highest score."""
        calculations = tco_calculator.calculate_all_tco(sample_bids, sample_vendors)

        # Find rank 1
        rank_1 = next(c for c in calculations if c.tco_rank == 1)

        # Rank 1 should have lowest TCO
        for calc in calculations:
            assert calc.total_cost_of_ownership >= rank_1.total_cost_of_ownership

        # Lowest TCO should have highest score (100)
        assert rank_1.tco_score == 100.0

    def test_maintenance_cost_calculation(self, sample_vendors: dict[UUID, Vendor]):
        """Test maintenance cost with inflation and discounting."""
        calculator = TCOCalculator()
        vendor = list(sample_vendors.values())[0]

        # Create bid with specific maintenance costs
        from uuid import uuid4

        bid = VendorBid(
            id=uuid4(),
            vendor_id=vendor.id,
            bid_reference="TEST-001",
            unit_price=10000.0,
            quantity=1,
            total_price=10000.0,
            delivery_days=30,
            maintenance_cost_annual=1000.0,
            warranty_years=1,
            expected_lifespan_years=5,
        )

        tco = calculator.calculate_tco(bid, vendor)

        # Should have maintenance for 4 years (5 - 1 warranty)
        assert tco.total_maintenance_cost > 0
        # Maintenance should be less than simple multiplication due to discounting
        assert tco.total_maintenance_cost < 1000.0 * 4

    def test_warranty_reduces_maintenance(self, sample_vendors: dict[UUID, Vendor]):
        """Test that longer warranty reduces maintenance costs."""
        calculator = TCOCalculator()
        vendor = list(sample_vendors.values())[0]

        from uuid import uuid4

        # Short warranty
        bid_short = VendorBid(
            id=uuid4(),
            vendor_id=vendor.id,
            bid_reference="TEST-SHORT",
            unit_price=10000.0,
            quantity=1,
            total_price=10000.0,
            delivery_days=30,
            maintenance_cost_annual=1000.0,
            warranty_years=1,
            expected_lifespan_years=5,
        )

        # Long warranty
        bid_long = VendorBid(
            id=uuid4(),
            vendor_id=vendor.id,
            bid_reference="TEST-LONG",
            unit_price=10000.0,
            quantity=1,
            total_price=10000.0,
            delivery_days=30,
            maintenance_cost_annual=1000.0,
            warranty_years=4,
            expected_lifespan_years=5,
        )

        tco_short = calculator.calculate_tco(bid_short, vendor)
        tco_long = calculator.calculate_tco(bid_long, vendor)

        # Longer warranty = less maintenance cost
        assert tco_long.total_maintenance_cost < tco_short.total_maintenance_cost

    def test_tco_summary(
        self,
        tco_calculator: TCOCalculator,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test TCO summary generation."""
        calculations = tco_calculator.calculate_all_tco(sample_bids, sample_vendors)

        summary = tco_calculator.get_tco_summary(calculations)

        assert "vendor_count" in summary
        assert "tco_statistics" in summary
        assert "acquisition_statistics" in summary
        assert "operational_statistics" in summary
        assert "best_value" in summary
        assert "worst_value" in summary
        assert "savings_analysis" in summary

        assert summary["vendor_count"] == len(sample_bids)
        assert summary["savings_analysis"]["potential_savings"] >= 0

    def test_compare_tco(
        self,
        tco_calculator: TCOCalculator,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test TCO comparison between two vendors."""
        calculations = tco_calculator.calculate_all_tco(sample_bids, sample_vendors)

        if len(calculations) >= 2:
            comparison = tco_calculator.compare_tco(calculations[0], calculations[1])

            assert "vendor_1" in comparison
            assert "vendor_2" in comparison
            assert "comparison" in comparison
            assert "breakdown_comparison" in comparison

            assert "tco_difference" in comparison["comparison"]
            assert "better_value_vendor" in comparison["comparison"]

    def test_custom_discount_rate(self, sample_bids: list[VendorBid], sample_vendors: dict[UUID, Vendor]):
        """Test TCO with custom discount rate."""
        config_high = TCOConfig(discount_rate=0.10)  # 10%
        config_low = TCOConfig(discount_rate=0.02)  # 2%

        calc_high = TCOCalculator(config=config_high)
        calc_low = TCOCalculator(config=config_low)

        bid = sample_bids[0]
        vendor = sample_vendors[bid.vendor_id]

        tco_high = calc_high.calculate_tco(bid, vendor)
        tco_low = calc_low.calculate_tco(bid, vendor)

        # Higher discount rate = lower present value of future costs
        assert tco_high.total_maintenance_cost < tco_low.total_maintenance_cost

    def test_empty_calculations(self, tco_calculator: TCOCalculator):
        """Test summary with no calculations."""
        summary = tco_calculator.get_tco_summary([])
        assert "message" in summary
