# Procure-Pro-ISO

Comprehensive ISO-compliant procurement lifecycle management system with an advanced Technical Bid Evaluation (TBE) Scoring Engine.

## Features

### TBE Scoring Engine

- **Weighted Scoring Algorithm**: Configurable criteria weights (default: Price 40%, Quality 25%, Delivery 20%, Compliance 15%)
- **Multi-Criteria Comparison Matrix**: Visual vendor comparison across all evaluation criteria
- **Automatic Ranking & Recommendations**: Intelligent vendor ranking with recommendation categories
- **Cost-Benefit Analysis**: Total Cost of Ownership (TCO) calculations including acquisition and operational costs
- **Compliance Scoring**: ISO standards and certification compliance evaluation
- **Detailed Reports**: Comprehensive TBE reports with charts and visualizations
- **Custom Criteria Support**: Extend evaluations with organization-specific criteria

### ISO Standards Support

- ISO 9001 (Quality Management)
- ISO 14001 (Environmental Management)
- ISO 17025 (Testing & Calibration Labs)
- ISO 27001 (Information Security)
- ISO 45001 (Occupational Health & Safety)
- IATF 16949 (Automotive Quality)
- ISO 13485 (Medical Devices)
- ISO 22000 (Food Safety)
- AS 9100 (Aerospace Quality)

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/procure-pro-iso.git
cd procure-pro-iso

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -e ".[dev]"
```

## Quick Start

### Running the API Server

```bash
# Start the development server
uvicorn main:app --reload

# Or using Python directly
python main.py
```

The API will be available at:
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Basic Usage

```python
from src.services.tbe_scoring import create_scoring_engine
from src.models.tbe import DefaultCriteriaWeights

# Create scoring engine with custom weights
engine = create_scoring_engine(
    price_weight=0.40,
    quality_weight=0.25,
    delivery_weight=0.20,
    compliance_weight=0.15,
)

# Score vendor bids
results = engine.evaluate_all_bids(
    bids=vendor_bids,
    vendors=vendors_dict,
    required_standards=["ISO 9001", "ISO 17025"],
    required_certs=["CE Mark"],
)
```

## API Endpoints

### Vendors
- `GET /api/v1/vendors/` - List all vendors
- `POST /api/v1/vendors/` - Create a vendor
- `GET /api/v1/vendors/{id}` - Get vendor details
- `PUT /api/v1/vendors/{id}` - Update vendor
- `DELETE /api/v1/vendors/{id}` - Delete vendor

### TBE Evaluations
- `GET /api/v1/tbe/evaluations` - List evaluations
- `POST /api/v1/tbe/evaluations` - Create evaluation
- `POST /api/v1/tbe/evaluations/{id}/execute` - Execute evaluation
- `GET /api/v1/tbe/evaluations/{id}/results` - Get results
- `GET /api/v1/tbe/evaluations/{id}/matrix` - Get comparison matrix
- `GET /api/v1/tbe/evaluations/{id}/ranking` - Get ranking summary
- `GET /api/v1/tbe/evaluations/{id}/tco` - Get TCO analysis
- `GET /api/v1/tbe/evaluations/{id}/compliance` - Get compliance summary

### Vendor Bids
- `GET /api/v1/tbe/bids` - List bids
- `POST /api/v1/tbe/bids` - Submit a bid
- `GET /api/v1/tbe/bids/{id}` - Get bid details

### Reports
- `GET /api/v1/reports/evaluations/{id}` - Generate TBE report
- `GET /api/v1/reports/evaluations/{id}/charts/scores` - Score comparison chart
- `GET /api/v1/reports/evaluations/{id}/charts/tco` - TCO comparison chart
- `GET /api/v1/reports/evaluations/{id}/charts/radar` - Radar comparison chart
- `GET /api/v1/reports/templates/weights` - Get weight templates

### Utilities
- `GET /api/v1/tbe/iso-standards` - List supported ISO standards
- `POST /api/v1/tbe/calculate-score` - Preview score calculation

## Scoring Algorithm

### Price Scoring
Lower prices receive higher scores using inverse linear normalization:
```
score = max_score * (1 - (price - min_price) / (max_price - min_price))
```

### Quality Scoring
Weighted average of quality indicators:
```
score = (quality_rating * 0.6) + (past_performance * 0.4)
```

### Delivery Scoring
Faster delivery receives higher scores:
```
score = max_score * (1 - (days - min_days) / (max_days - min_days))
```

### Compliance Scoring
Based on ISO standards and certification matches:
```
score = (matches / total_required) * 100
```

### Final Weighted Score
```
total = (price_score * 0.40) + (quality_score * 0.25) +
        (delivery_score * 0.20) + (compliance_score * 0.15)
```

## TCO Calculation

Total Cost of Ownership includes:
- **Acquisition Cost**: Base price + shipping + installation + training
- **Operational Cost**: Maintenance over lifespan (with inflation and discounting)

```
TCO = Acquisition Cost + Σ(Maintenance[year] * (1 + inflation)^year / (1 + discount)^year)
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tbe_scoring.py

# Run with verbose output
pytest -v
```

## Project Structure

```
procure-pro-iso/
├── src/
│   ├── api/
│   │   ├── app.py              # FastAPI application
│   │   └── routes/
│   │       ├── vendors.py      # Vendor endpoints
│   │       ├── tbe.py          # TBE evaluation endpoints
│   │       └── reports.py      # Report endpoints
│   ├── config/
│   │   ├── settings.py         # Application settings
│   │   └── database.py         # Database configuration
│   ├── models/
│   │   ├── vendor.py           # Vendor models
│   │   └── tbe.py              # TBE models
│   └── services/
│       ├── tbe_scoring.py      # Weighted scoring algorithm
│       ├── comparison_matrix.py # Matrix generation
│       ├── ranking_engine.py   # Ranking & recommendations
│       ├── tco_calculator.py   # TCO calculations
│       ├── compliance_scorer.py # Compliance checking
│       └── report_generator.py # Report generation
├── tests/
│   ├── conftest.py             # Test fixtures
│   ├── test_tbe_scoring.py     # Scoring tests
│   ├── test_comparison_matrix.py
│   ├── test_ranking_engine.py
│   ├── test_tco_calculator.py
│   ├── test_compliance_scorer.py
│   ├── test_api.py
│   └── test_report_generator.py
├── main.py                     # Application entry point
├── pyproject.toml              # Project configuration
└── requirements.txt            # Dependencies
```

## Configuration

Environment variables (or `.env` file):

```env
# Application
APP_NAME=Procure-Pro-ISO
DEBUG=false
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite+aiosqlite:///./procure_pro.db

# API
API_PREFIX=/api/v1

# TBE Defaults
DEFAULT_PRICE_WEIGHT=0.40
DEFAULT_QUALITY_WEIGHT=0.25
DEFAULT_DELIVERY_WEIGHT=0.20
DEFAULT_COMPLIANCE_WEIGHT=0.15

# Reports
REPORT_OUTPUT_DIR=./reports
CHART_DPI=150
```

## License

MIT License - See [LICENSE](LICENSE) for details.
