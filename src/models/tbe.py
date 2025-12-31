"""Technical Bid Evaluation (TBE) data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from src.config.database import Base


# ============================================================================
# Enums
# ============================================================================


class ISOStandard(str, Enum):
    """ISO standards for procurement compliance."""

    ISO_9001 = "ISO 9001"  # Quality Management
    ISO_14001 = "ISO 14001"  # Environmental Management
    ISO_17025 = "ISO 17025"  # Testing & Calibration Labs
    ISO_27001 = "ISO 27001"  # Information Security
    ISO_45001 = "ISO 45001"  # Occupational Health & Safety
    IATF_16949 = "IATF 16949"  # Automotive Quality
    ISO_13485 = "ISO 13485"  # Medical Devices
    ISO_22000 = "ISO 22000"  # Food Safety
    AS_9100 = "AS 9100"  # Aerospace Quality


class EvaluationStatus(str, Enum):
    """TBE evaluation status."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"


class CriteriaCategory(str, Enum):
    """Evaluation criteria categories."""

    PRICE = "price"
    QUALITY = "quality"
    DELIVERY = "delivery"
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"
    EXPERIENCE = "experience"
    SUPPORT = "support"
    CUSTOM = "custom"


class RecommendationType(str, Enum):
    """Vendor recommendation types."""

    HIGHLY_RECOMMENDED = "highly_recommended"
    RECOMMENDED = "recommended"
    ACCEPTABLE = "acceptable"
    NOT_RECOMMENDED = "not_recommended"
    DISQUALIFIED = "disqualified"


# ============================================================================
# SQLAlchemy Models (Database)
# ============================================================================


class EvaluationCriteriaDB(Base):
    """SQLAlchemy model for evaluation criteria."""

    __tablename__ = "evaluation_criteria"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=0.0)
    max_score = Column(Float, default=100.0)
    is_mandatory = Column(Boolean, default=False)
    scoring_guidance = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VendorBidDB(Base):
    """SQLAlchemy model for vendor bids."""

    __tablename__ = "vendor_bids"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False)
    evaluation_id = Column(String(36), ForeignKey("tbe_evaluations.id"), nullable=True)
    bid_reference = Column(String(100), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Price components
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")

    # Additional costs for TCO
    shipping_cost = Column(Float, default=0.0)
    installation_cost = Column(Float, default=0.0)
    training_cost = Column(Float, default=0.0)
    maintenance_cost_annual = Column(Float, default=0.0)
    warranty_years = Column(Integer, default=1)
    expected_lifespan_years = Column(Integer, default=5)

    # Delivery
    delivery_days = Column(Integer, nullable=False)
    delivery_terms = Column(String(50), nullable=True)

    # Technical specifications
    technical_specs = Column(JSON, default=dict)
    certifications = Column(JSON, default=list)
    iso_compliance = Column(JSON, default=list)

    # Quality indicators
    quality_score = Column(Float, default=0.0)
    past_performance_score = Column(Float, default=0.0)

    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TBEEvaluationDB(Base):
    """SQLAlchemy model for TBE evaluations."""

    __tablename__ = "tbe_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_reference = Column(String(100), nullable=True)
    status = Column(String(50), default=EvaluationStatus.DRAFT.value)

    # Criteria weights
    criteria_weights = Column(JSON, default=dict)

    # Required compliance
    required_iso_standards = Column(JSON, default=list)
    required_certifications = Column(JSON, default=list)

    # Results
    evaluation_results = Column(JSON, default=dict)
    ranking = Column(JSON, default=list)
    recommended_vendor_id = Column(String(36), nullable=True)

    evaluated_by = Column(String(255), nullable=True)
    evaluated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bids = relationship("VendorBidDB", backref="evaluation", lazy="dynamic")


class TBEScoreDB(Base):
    """SQLAlchemy model for individual TBE scores."""

    __tablename__ = "tbe_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    evaluation_id = Column(String(36), ForeignKey("tbe_evaluations.id"), nullable=False)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False)
    bid_id = Column(String(36), ForeignKey("vendor_bids.id"), nullable=False)
    criteria_id = Column(String(36), ForeignKey("evaluation_criteria.id"), nullable=False)

    raw_score = Column(Float, nullable=False)
    weighted_score = Column(Float, nullable=False)
    max_possible = Column(Float, nullable=False)

    comments = Column(Text, nullable=True)
    scored_by = Column(String(255), nullable=True)
    scored_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# Pydantic Models (API)
# ============================================================================


class CriteriaWeight(BaseModel):
    """Weight configuration for evaluation criteria."""

    category: CriteriaCategory
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight as decimal (0.0-1.0)")
    max_score: float = Field(100.0, gt=0, description="Maximum possible score")

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        return round(v, 4)


class DefaultCriteriaWeights(BaseModel):
    """Default criteria weights configuration."""

    price: float = Field(0.40, ge=0.0, le=1.0)
    quality: float = Field(0.25, ge=0.0, le=1.0)
    delivery: float = Field(0.20, ge=0.0, le=1.0)
    compliance: float = Field(0.15, ge=0.0, le=1.0)

    @field_validator("price", "quality", "delivery", "compliance")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        return round(v, 4)

    def total_weight(self) -> float:
        return self.price + self.quality + self.delivery + self.compliance

    def is_valid(self) -> bool:
        return abs(self.total_weight() - 1.0) < 0.0001


class EvaluationCriteria(BaseModel):
    """Evaluation criteria model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    category: CriteriaCategory
    description: Optional[str] = None
    weight: float = Field(0.0, ge=0.0, le=1.0)
    max_score: float = Field(100.0, gt=0)
    is_mandatory: bool = False
    scoring_guidance: dict[str, Any] = Field(default_factory=dict)


class EvaluationCriteriaCreate(BaseModel):
    """Model for creating evaluation criteria."""

    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    category: CriteriaCategory
    description: Optional[str] = None
    weight: float = Field(0.0, ge=0.0, le=1.0)
    max_score: float = Field(100.0, gt=0)
    is_mandatory: bool = False
    scoring_guidance: dict[str, Any] = Field(default_factory=dict)


class VendorBidCreate(BaseModel):
    """Model for creating a vendor bid."""

    vendor_id: UUID
    bid_reference: str = Field(..., min_length=1, max_length=100)

    # Price
    unit_price: float = Field(..., gt=0)
    quantity: int = Field(1, gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)

    # Additional costs
    shipping_cost: float = Field(0.0, ge=0)
    installation_cost: float = Field(0.0, ge=0)
    training_cost: float = Field(0.0, ge=0)
    maintenance_cost_annual: float = Field(0.0, ge=0)
    warranty_years: int = Field(1, ge=0)
    expected_lifespan_years: int = Field(5, ge=1)

    # Delivery
    delivery_days: int = Field(..., gt=0)
    delivery_terms: Optional[str] = None

    # Technical
    technical_specs: dict[str, Any] = Field(default_factory=dict)
    certifications: list[str] = Field(default_factory=list)
    iso_compliance: list[str] = Field(default_factory=list)

    # Quality
    quality_score: float = Field(0.0, ge=0, le=100)
    past_performance_score: float = Field(0.0, ge=0, le=100)

    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity


class VendorBid(VendorBidCreate):
    """Complete vendor bid model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    evaluation_id: Optional[UUID] = None
    total_price: float = 0.0
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TBEScore(BaseModel):
    """Individual TBE score for a criteria."""

    model_config = ConfigDict(from_attributes=True)

    criteria_id: UUID
    criteria_name: str
    criteria_category: CriteriaCategory
    raw_score: float = Field(..., ge=0)
    weight: float = Field(..., ge=0, le=1)
    weighted_score: float = Field(..., ge=0)
    max_possible: float
    percentage: float = Field(..., ge=0, le=100)
    comments: Optional[str] = None


class TCOCalculation(BaseModel):
    """Total Cost of Ownership calculation."""

    bid_id: UUID
    vendor_id: UUID
    vendor_name: str

    # Direct costs
    unit_price: float
    quantity: int
    base_cost: float
    shipping_cost: float
    installation_cost: float
    training_cost: float

    # Recurring costs
    maintenance_cost_annual: float
    warranty_years: int
    expected_lifespan_years: int
    total_maintenance_cost: float

    # TCO components
    acquisition_cost: float
    operational_cost: float
    total_cost_of_ownership: float
    tco_per_year: float
    tco_per_unit: float

    # Comparison
    tco_score: float = Field(0.0, ge=0, le=100)
    tco_rank: int = 0


class ComplianceCheck(BaseModel):
    """ISO/Certification compliance check result."""

    vendor_id: UUID
    vendor_name: str

    # Required vs provided
    required_iso_standards: list[ISOStandard]
    provided_iso_standards: list[str]
    required_certifications: list[str]
    provided_certifications: list[str]

    # Compliance scores
    iso_compliance_score: float = Field(0.0, ge=0, le=100)
    certification_compliance_score: float = Field(0.0, ge=0, le=100)
    overall_compliance_score: float = Field(0.0, ge=0, le=100)

    # Details
    missing_iso_standards: list[str] = Field(default_factory=list)
    missing_certifications: list[str] = Field(default_factory=list)
    is_compliant: bool = False
    compliance_notes: Optional[str] = None


class TBEResult(BaseModel):
    """Complete TBE result for a vendor."""

    model_config = ConfigDict(from_attributes=True)

    vendor_id: UUID
    vendor_name: str
    vendor_code: str
    bid_id: UUID
    bid_reference: str

    # Scores by category
    scores: list[TBEScore]

    # Category summaries
    price_score: float = Field(0.0, ge=0, le=100)
    quality_score: float = Field(0.0, ge=0, le=100)
    delivery_score: float = Field(0.0, ge=0, le=100)
    compliance_score: float = Field(0.0, ge=0, le=100)

    # Overall
    total_weighted_score: float = Field(0.0, ge=0, le=100)
    total_raw_score: float = 0.0
    max_possible_score: float = 100.0

    # TCO
    tco_calculation: Optional[TCOCalculation] = None

    # Compliance
    compliance_check: Optional[ComplianceCheck] = None

    # Ranking
    rank: int = 0
    recommendation: RecommendationType = RecommendationType.ACCEPTABLE
    recommendation_notes: Optional[str] = None


class ComparisonMatrixCell(BaseModel):
    """Single cell in comparison matrix."""

    vendor_id: UUID
    vendor_name: str
    value: float
    display_value: str
    is_best: bool = False
    is_worst: bool = False
    rank: int = 0


class ComparisonMatrixRow(BaseModel):
    """Row in comparison matrix representing a criteria."""

    criteria_name: str
    criteria_category: CriteriaCategory
    weight: float
    cells: list[ComparisonMatrixCell]


class ComparisonMatrix(BaseModel):
    """Multi-criteria comparison matrix for vendors."""

    evaluation_id: UUID
    evaluation_name: str
    vendor_count: int
    criteria_count: int

    # Headers
    vendor_names: list[str]
    vendor_ids: list[UUID]

    # Matrix data
    rows: list[ComparisonMatrixRow]

    # Summary row
    total_scores: list[ComparisonMatrixCell]

    # Best/worst indicators
    best_vendor_id: Optional[UUID] = None
    best_vendor_name: Optional[str] = None
    worst_vendor_id: Optional[UUID] = None
    worst_vendor_name: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class TBEEvaluationCreate(BaseModel):
    """Model for creating a TBE evaluation."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_reference: Optional[str] = None

    # Weights
    criteria_weights: DefaultCriteriaWeights = Field(default_factory=DefaultCriteriaWeights)

    # Requirements
    required_iso_standards: list[ISOStandard] = Field(default_factory=list)
    required_certifications: list[str] = Field(default_factory=list)


class TBEEvaluation(TBEEvaluationCreate):
    """Complete TBE evaluation model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    status: EvaluationStatus = EvaluationStatus.DRAFT

    # Results
    results: list[TBEResult] = Field(default_factory=list)
    ranking: list[UUID] = Field(default_factory=list)
    recommended_vendor_id: Optional[UUID] = None
    comparison_matrix: Optional[ComparisonMatrix] = None

    evaluated_by: Optional[str] = None
    evaluated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TBEReport(BaseModel):
    """Complete TBE report model."""

    evaluation: TBEEvaluation
    comparison_matrix: ComparisonMatrix
    tco_summary: list[TCOCalculation]
    compliance_summary: list[ComplianceCheck]

    # Charts (base64 encoded)
    score_chart: Optional[str] = None
    tco_chart: Optional[str] = None
    radar_chart: Optional[str] = None

    # Summary
    executive_summary: str
    recommendations: list[str]

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: Optional[str] = None
