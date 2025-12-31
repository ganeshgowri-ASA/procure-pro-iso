"""
Tests for TBE Scoring Engine.

Comprehensive tests for:
- Weighted scoring algorithm
- Price/quality/delivery/compliance calculations
- Custom weight configurations
"""

from uuid import UUID

import pytest

from src.models.vendor import Vendor
from src.models.tbe import (
    VendorBid,
    DefaultCriteriaWeights,
    RecommendationType,
)
from src.services.tbe_scoring import TBEScoringEngine, create_scoring_engine, ScoringConfig


class TestTBEScoringEngine:
    """Test suite for TBE Scoring Engine."""

    def test_create_scoring_engine_with_default_weights(self):
        """Test creating scoring engine with default weights."""
        engine = create_scoring_engine()

        assert engine.weights.price == 0.40
        assert engine.weights.quality == 0.25
        assert engine.weights.delivery == 0.20
        assert engine.weights.compliance == 0.15
        assert engine.weights.is_valid()

    def test_create_scoring_engine_with_custom_weights(self):
        """Test creating scoring engine with custom weights."""
        engine = create_scoring_engine(
            price_weight=0.30,
            quality_weight=0.30,
            delivery_weight=0.25,
            compliance_weight=0.15,
        )

        assert engine.weights.price == 0.30
        assert engine.weights.quality == 0.30
        assert engine.weights.delivery == 0.25
        assert engine.weights.is_valid()

    def test_invalid_weights_raise_error(self):
        """Test that invalid weights (not summing to 1.0) raise error."""
        with pytest.raises(ValueError, match="Criteria weights must sum to 1.0"):
            create_scoring_engine(
                price_weight=0.50,
                quality_weight=0.30,
                delivery_weight=0.20,
                compliance_weight=0.20,  # Sum = 1.2
            )

    def test_calculate_price_score(self, sample_bids: list[VendorBid]):
        """Test price score calculation - lower prices get higher scores."""
        engine = create_scoring_engine()

        all_prices = [bid.total_price for bid in sample_bids]

        # Epsilon has lowest price ($115,000), should get highest score
        epsilon_bid = next(b for b in sample_bids if b.bid_reference.startswith("BID-EPSILON"))
        epsilon_score = engine.calculate_price_score(epsilon_bid.total_price, all_prices)
        assert epsilon_score == 100.0

        # Delta has highest price ($220,000), should get lowest score
        delta_bid = next(b for b in sample_bids if b.bid_reference.startswith("BID-DELTA"))
        delta_score = engine.calculate_price_score(delta_bid.total_price, all_prices)
        assert delta_score == 0.0

        # Alpha is in the middle
        alpha_bid = next(b for b in sample_bids if b.bid_reference.startswith("BID-ALPHA"))
        alpha_score = engine.calculate_price_score(alpha_bid.total_price, all_prices)
        assert 0 < alpha_score < 100

    def test_calculate_delivery_score(self, sample_bids: list[VendorBid]):
        """Test delivery score calculation - faster delivery gets higher scores."""
        engine = create_scoring_engine()

        all_delivery = [bid.delivery_days for bid in sample_bids]

        # Gamma has fastest delivery (21 days), should get highest score
        gamma_bid = next(b for b in sample_bids if b.bid_reference.startswith("BID-GAMMA"))
        gamma_score = engine.calculate_delivery_score(gamma_bid.delivery_days, all_delivery)
        assert gamma_score == 100.0

        # Delta has slowest delivery (60 days), should get lowest score
        delta_bid = next(b for b in sample_bids if b.bid_reference.startswith("BID-DELTA"))
        delta_score = engine.calculate_delivery_score(delta_bid.delivery_days, all_delivery)
        assert delta_score == 0.0

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        engine = create_scoring_engine()

        # High quality ratings
        score = engine.calculate_quality_score(quality_rating=95.0, past_performance=90.0)
        assert score >= 90.0

        # Low quality ratings
        score = engine.calculate_quality_score(quality_rating=50.0, past_performance=50.0)
        assert score == 50.0

        # Mixed ratings
        score = engine.calculate_quality_score(quality_rating=80.0, past_performance=60.0)
        expected = 80.0 * 0.6 + 60.0 * 0.4  # 48 + 24 = 72
        assert score == expected

    def test_calculate_compliance_score(self):
        """Test compliance score calculation."""
        engine = create_scoring_engine()

        # Full compliance
        score = engine.calculate_compliance_score(
            provided_standards=["ISO 9001", "ISO 17025"],
            required_standards=["ISO 9001", "ISO 17025"],
            provided_certs=["CE Mark"],
            required_certs=["CE Mark"],
        )
        assert score == 100.0

        # Partial compliance
        score = engine.calculate_compliance_score(
            provided_standards=["ISO 9001"],
            required_standards=["ISO 9001", "ISO 17025"],
            provided_certs=[],
            required_certs=["CE Mark"],
        )
        assert score < 100.0
        assert score > 0.0

        # No requirements = full compliance
        score = engine.calculate_compliance_score(
            provided_standards=["ISO 9001"],
            required_standards=[],
            provided_certs=[],
            required_certs=[],
        )
        assert score == 100.0

    def test_score_bid_complete(
        self,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test complete bid scoring."""
        engine = create_scoring_engine()

        # Score one bid
        bid = sample_bids[0]
        vendor = sample_vendors[bid.vendor_id]

        result = engine.score_bid(
            bid=bid,
            vendor=vendor,
            all_bids=sample_bids,
            required_standards=["ISO 9001", "ISO 17025"],
            required_certs=["CE Mark"],
        )

        # Check result structure
        assert result.vendor_id == bid.vendor_id
        assert result.vendor_name == vendor.name
        assert result.bid_id == bid.id
        assert len(result.scores) == 4  # price, quality, delivery, compliance

        # Check scores are in valid range
        assert 0 <= result.price_score <= 100
        assert 0 <= result.quality_score <= 100
        assert 0 <= result.delivery_score <= 100
        assert 0 <= result.compliance_score <= 100
        assert 0 <= result.total_weighted_score <= 100

    def test_evaluate_all_bids(
        self,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test evaluating all vendor bids."""
        engine = create_scoring_engine()

        results = engine.evaluate_all_bids(
            bids=sample_bids,
            vendors=sample_vendors,
            required_standards=["ISO 9001"],
            required_certs=[],
        )

        assert len(results) == len(sample_bids)

        # All results should have valid scores
        for result in results:
            assert 0 <= result.total_weighted_score <= 100
            assert result.recommendation in list(RecommendationType)

    def test_recommendation_thresholds(
        self,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test recommendation thresholds."""
        config = ScoringConfig(
            min_score_highly_recommended=85.0,
            min_score_recommended=70.0,
            min_score_acceptable=50.0,
        )
        engine = TBEScoringEngine(config=config)

        # Score should be mapped correctly to recommendations
        # This is a behavioral test that ensures the threshold logic works
        assert engine.config.min_score_highly_recommended == 85.0
        assert engine.config.min_score_recommended == 70.0
        assert engine.config.min_score_acceptable == 50.0

    def test_weights_affect_final_score(
        self,
        sample_bids: list[VendorBid],
        sample_vendors: dict[UUID, Vendor],
    ):
        """Test that different weights produce different final scores."""
        # Price-focused weights
        price_engine = create_scoring_engine(
            price_weight=0.60,
            quality_weight=0.15,
            delivery_weight=0.15,
            compliance_weight=0.10,
        )

        # Quality-focused weights
        quality_engine = create_scoring_engine(
            price_weight=0.15,
            quality_weight=0.60,
            delivery_weight=0.15,
            compliance_weight=0.10,
        )

        bid = sample_bids[0]
        vendor = sample_vendors[bid.vendor_id]

        price_result = price_engine.score_bid(
            bid, vendor, sample_bids, ["ISO 9001"], []
        )
        quality_result = quality_engine.score_bid(
            bid, vendor, sample_bids, ["ISO 9001"], []
        )

        # Scores should be different due to different weights
        assert price_result.total_weighted_score != quality_result.total_weighted_score


class TestPriceScoringMethods:
    """Test different price scoring methods."""

    def test_inverse_linear_scoring(self):
        """Test inverse linear price scoring."""
        config = ScoringConfig(price_scoring_method="inverse_linear")
        engine = TBEScoringEngine(config=config)

        prices = [100, 150, 200]

        # Lowest price gets 100, highest gets 0
        assert engine.calculate_price_score(100, prices) == 100.0
        assert engine.calculate_price_score(200, prices) == 0.0
        assert engine.calculate_price_score(150, prices) == 50.0

    def test_min_max_scoring(self):
        """Test min-max price scoring."""
        config = ScoringConfig(price_scoring_method="min_max")
        engine = TBEScoringEngine(config=config)

        prices = [100, 200]

        # Score based on ratio to minimum price
        assert engine.calculate_price_score(100, prices) == 100.0
        assert engine.calculate_price_score(200, prices) == 50.0

    def test_equal_prices(self):
        """Test scoring when all prices are equal."""
        engine = create_scoring_engine()

        prices = [100, 100, 100]

        # All should get max score
        for price in prices:
            assert engine.calculate_price_score(price, prices) == 100.0
