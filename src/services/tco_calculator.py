"""
TCO Calculator - Total Cost of Ownership analysis.

Provides comprehensive cost-benefit analysis including:
- Acquisition costs
- Operational costs over lifespan
- Maintenance and support costs
- TCO normalization for scoring
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.models.tbe import TCOCalculation, VendorBid
from src.models.vendor import Vendor


@dataclass
class TCOConfig:
    """Configuration for TCO calculations."""

    # Discount rate for NPV calculations
    discount_rate: float = 0.05  # 5% annual discount rate

    # Default assumptions
    default_lifespan_years: int = 5
    default_warranty_years: int = 1

    # Cost factors
    maintenance_inflation_rate: float = 0.03  # 3% annual increase

    # Scoring normalization
    normalize_to_100: bool = True


class TCOCalculator:
    """
    Total Cost of Ownership Calculator.

    Calculates TCO including:
    - Initial acquisition cost (purchase + shipping + installation + training)
    - Recurring operational costs (maintenance over lifespan)
    - Present value adjustments
    - Normalized TCO scoring for comparison
    """

    def __init__(self, config: Optional[TCOConfig] = None):
        """Initialize TCO calculator with configuration."""
        self.config = config or TCOConfig()

    def calculate_tco(
        self,
        bid: VendorBid,
        vendor: Vendor,
    ) -> TCOCalculation:
        """
        Calculate TCO for a vendor bid.

        Args:
            bid: The vendor bid with cost details
            vendor: The vendor information

        Returns:
            Complete TCO calculation
        """
        # Base cost
        base_cost = bid.unit_price * bid.quantity

        # Acquisition cost (one-time costs)
        acquisition_cost = (
            base_cost
            + bid.shipping_cost
            + bid.installation_cost
            + bid.training_cost
        )

        # Calculate maintenance costs over lifespan
        lifespan = bid.expected_lifespan_years or self.config.default_lifespan_years
        warranty = bid.warranty_years or self.config.default_warranty_years

        # Years requiring paid maintenance (after warranty)
        maintenance_years = max(0, lifespan - warranty)

        # Calculate maintenance with inflation
        total_maintenance = self._calculate_maintenance_cost(
            annual_cost=bid.maintenance_cost_annual,
            years=maintenance_years,
            start_year=warranty + 1,
        )

        # Operational cost (recurring)
        operational_cost = total_maintenance

        # Total Cost of Ownership
        total_tco = acquisition_cost + operational_cost

        # Per-year and per-unit calculations
        tco_per_year = total_tco / lifespan if lifespan > 0 else total_tco
        tco_per_unit = total_tco / bid.quantity if bid.quantity > 0 else total_tco

        return TCOCalculation(
            bid_id=bid.id,
            vendor_id=bid.vendor_id,
            vendor_name=vendor.name,
            unit_price=bid.unit_price,
            quantity=bid.quantity,
            base_cost=base_cost,
            shipping_cost=bid.shipping_cost,
            installation_cost=bid.installation_cost,
            training_cost=bid.training_cost,
            maintenance_cost_annual=bid.maintenance_cost_annual,
            warranty_years=warranty,
            expected_lifespan_years=lifespan,
            total_maintenance_cost=total_maintenance,
            acquisition_cost=acquisition_cost,
            operational_cost=operational_cost,
            total_cost_of_ownership=total_tco,
            tco_per_year=tco_per_year,
            tco_per_unit=tco_per_unit,
            tco_score=0.0,  # Will be set after normalization
            tco_rank=0,  # Will be set after ranking
        )

    def _calculate_maintenance_cost(
        self,
        annual_cost: float,
        years: int,
        start_year: int = 1,
    ) -> float:
        """
        Calculate total maintenance cost with inflation and discounting.

        Args:
            annual_cost: Base annual maintenance cost
            years: Number of years of maintenance
            start_year: First year of paid maintenance

        Returns:
            Total maintenance cost (present value)
        """
        if annual_cost <= 0 or years <= 0:
            return 0.0

        total = 0.0
        for year in range(start_year, start_year + years):
            # Apply inflation to annual cost
            inflated_cost = annual_cost * (
                (1 + self.config.maintenance_inflation_rate) ** (year - 1)
            )

            # Discount to present value
            present_value = inflated_cost / ((1 + self.config.discount_rate) ** year)

            total += present_value

        return total

    def calculate_all_tco(
        self,
        bids: list[VendorBid],
        vendors: dict[UUID, Vendor],
    ) -> list[TCOCalculation]:
        """
        Calculate TCO for all vendor bids.

        Args:
            bids: List of vendor bids
            vendors: Dictionary mapping vendor IDs to Vendor objects

        Returns:
            List of TCO calculations
        """
        calculations = []

        for bid in bids:
            vendor = vendors.get(bid.vendor_id)
            if not vendor:
                continue

            tco = self.calculate_tco(bid, vendor)
            calculations.append(tco)

        # Normalize scores after all calculations
        calculations = self._normalize_tco_scores(calculations)

        # Assign ranks
        calculations = self._assign_tco_ranks(calculations)

        return calculations

    def _normalize_tco_scores(
        self,
        calculations: list[TCOCalculation],
    ) -> list[TCOCalculation]:
        """
        Normalize TCO values to 0-100 score (lower TCO = higher score).

        Args:
            calculations: TCO calculations to normalize

        Returns:
            Calculations with normalized scores
        """
        if not calculations:
            return calculations

        tco_values = [c.total_cost_of_ownership for c in calculations]
        min_tco = min(tco_values)
        max_tco = max(tco_values)

        if max_tco == min_tco:
            # All TCOs are equal
            for calc in calculations:
                calc.tco_score = 100.0
            return calculations

        for calc in calculations:
            # Inverse normalization: lowest TCO = 100, highest = 0
            normalized = (calc.total_cost_of_ownership - min_tco) / (max_tco - min_tco)
            calc.tco_score = 100.0 * (1 - normalized)

        return calculations

    def _assign_tco_ranks(
        self,
        calculations: list[TCOCalculation],
    ) -> list[TCOCalculation]:
        """Assign TCO ranks (lower TCO = better rank)."""
        sorted_by_tco = sorted(calculations, key=lambda c: c.total_cost_of_ownership)

        for rank, calc in enumerate(sorted_by_tco, 1):
            calc.tco_rank = rank

        return calculations

    def get_tco_summary(
        self,
        calculations: list[TCOCalculation],
    ) -> dict:
        """
        Generate TCO summary statistics.

        Args:
            calculations: TCO calculations

        Returns:
            Summary dictionary
        """
        if not calculations:
            return {"message": "No TCO calculations available"}

        tco_values = [c.total_cost_of_ownership for c in calculations]
        acquisition_values = [c.acquisition_cost for c in calculations]
        operational_values = [c.operational_cost for c in calculations]

        # Find best and worst
        best = min(calculations, key=lambda c: c.total_cost_of_ownership)
        worst = max(calculations, key=lambda c: c.total_cost_of_ownership)

        savings_potential = worst.total_cost_of_ownership - best.total_cost_of_ownership
        savings_percentage = (savings_potential / worst.total_cost_of_ownership * 100) if worst.total_cost_of_ownership > 0 else 0

        return {
            "vendor_count": len(calculations),
            "tco_statistics": {
                "average": round(sum(tco_values) / len(tco_values), 2),
                "minimum": round(min(tco_values), 2),
                "maximum": round(max(tco_values), 2),
                "range": round(max(tco_values) - min(tco_values), 2),
            },
            "acquisition_statistics": {
                "average": round(sum(acquisition_values) / len(acquisition_values), 2),
                "minimum": round(min(acquisition_values), 2),
                "maximum": round(max(acquisition_values), 2),
            },
            "operational_statistics": {
                "average": round(sum(operational_values) / len(operational_values), 2),
                "minimum": round(min(operational_values), 2),
                "maximum": round(max(operational_values), 2),
            },
            "best_value": {
                "vendor_id": str(best.vendor_id),
                "vendor_name": best.vendor_name,
                "total_tco": round(best.total_cost_of_ownership, 2),
                "tco_per_year": round(best.tco_per_year, 2),
            },
            "worst_value": {
                "vendor_id": str(worst.vendor_id),
                "vendor_name": worst.vendor_name,
                "total_tco": round(worst.total_cost_of_ownership, 2),
                "tco_per_year": round(worst.tco_per_year, 2),
            },
            "savings_analysis": {
                "potential_savings": round(savings_potential, 2),
                "savings_percentage": round(savings_percentage, 2),
            },
        }

    def compare_tco(
        self,
        calc1: TCOCalculation,
        calc2: TCOCalculation,
    ) -> dict:
        """
        Compare TCO between two vendors.

        Args:
            calc1: First vendor's TCO calculation
            calc2: Second vendor's TCO calculation

        Returns:
            Comparison dictionary
        """
        tco_diff = calc1.total_cost_of_ownership - calc2.total_cost_of_ownership
        percentage_diff = (tco_diff / calc2.total_cost_of_ownership * 100) if calc2.total_cost_of_ownership > 0 else 0

        better = calc1 if calc1.total_cost_of_ownership < calc2.total_cost_of_ownership else calc2
        worse = calc2 if better == calc1 else calc1

        return {
            "vendor_1": {
                "vendor_id": str(calc1.vendor_id),
                "vendor_name": calc1.vendor_name,
                "total_tco": round(calc1.total_cost_of_ownership, 2),
                "acquisition_cost": round(calc1.acquisition_cost, 2),
                "operational_cost": round(calc1.operational_cost, 2),
            },
            "vendor_2": {
                "vendor_id": str(calc2.vendor_id),
                "vendor_name": calc2.vendor_name,
                "total_tco": round(calc2.total_cost_of_ownership, 2),
                "acquisition_cost": round(calc2.acquisition_cost, 2),
                "operational_cost": round(calc2.operational_cost, 2),
            },
            "comparison": {
                "tco_difference": round(abs(tco_diff), 2),
                "percentage_difference": round(abs(percentage_diff), 2),
                "better_value_vendor": better.vendor_name,
                "savings_amount": round(abs(tco_diff), 2),
            },
            "breakdown_comparison": {
                "acquisition_diff": round(abs(calc1.acquisition_cost - calc2.acquisition_cost), 2),
                "operational_diff": round(abs(calc1.operational_cost - calc2.operational_cost), 2),
                "maintenance_diff": round(abs(calc1.total_maintenance_cost - calc2.total_maintenance_cost), 2),
            },
        }
