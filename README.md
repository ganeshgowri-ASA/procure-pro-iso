# Procure-Pro-ISO

Comprehensive ISO-compliant procurement lifecycle management system - From RFQ to Asset Management. Covers technical specs, vendor evaluation, TBE analysis, PO tracking, FAT-SAT testing, and equipment history per ISO 17025, ISO 9001, IATF 16949 standards.

## Features

### Vendor Management
- **CRUD Operations**: Create, read, update, and delete vendors
- **Registration System**: Self-service vendor registration with approval workflow
- **Certification Tracking**: Track ISO certifications (9001, 14001, 17025, 45001, IATF 16949, etc.)
- **Performance Ratings**: Periodic vendor performance evaluation and scoring
- **Category Management**: Organize vendors by categories and subcategories
- **Contact Management**: Multiple contacts per vendor with primary designation

### RFQ Workflow
- **RFQ Creation**: Create detailed requests for quotation with line items
- **Status Workflow**: Draft → Published → Under Review → Awarded → Closed
- **Vendor Invitations**: Invite specific vendors to participate
- **Item Management**: Manage equipment specifications and requirements
- **Quotation Submission**: Vendors can submit detailed quotations
- **Quote Comparison**: Side-by-side comparison of all received quotes
- **Email Notifications**: Automated notifications for invitations, submissions, and decisions

### API Features
- RESTful API design
- Pagination for list endpoints
- Search and filter capabilities
- Comprehensive error handling
- OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Authentication**: JWT tokens
- **Email**: aiosmtplib with Jinja2 templates
- **Testing**: pytest with pytest-asyncio

## Installation

### Prerequisites

- Python 3.10+
- pip or poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/procure-pro-iso.git
cd procure-pro-iso
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Vendor Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/vendors` | Create a new vendor |
| POST | `/api/v1/vendors/register` | Register vendor (pending approval) |
| GET | `/api/v1/vendors` | List vendors (paginated) |
| GET | `/api/v1/vendors/{id}` | Get vendor details |
| PUT | `/api/v1/vendors/{id}` | Update vendor |
| DELETE | `/api/v1/vendors/{id}` | Delete vendor |
| POST | `/api/v1/vendors/{id}/activate` | Activate vendor |

### Vendor Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/categories` | Create category |
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/{id}` | Get category |
| PUT | `/api/v1/categories/{id}` | Update category |
| DELETE | `/api/v1/categories/{id}` | Delete category |

### Vendor Certifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/vendors/{id}/certifications` | Add certification |
| GET | `/api/v1/vendors/{id}/certifications` | List certifications |
| PUT | `/api/v1/vendors/certifications/{id}` | Update certification |
| POST | `/api/v1/vendors/certifications/{id}/verify` | Verify certification |
| DELETE | `/api/v1/vendors/certifications/{id}` | Delete certification |

### Vendor Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/vendors/{id}/contacts` | Add contact |
| GET | `/api/v1/vendors/{id}/contacts` | List contacts |
| PUT | `/api/v1/vendors/contacts/{id}` | Update contact |
| DELETE | `/api/v1/vendors/contacts/{id}` | Delete contact |

### Vendor Ratings

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/vendors/{id}/ratings` | Add rating |
| GET | `/api/v1/vendors/{id}/ratings` | List ratings |
| GET | `/api/v1/vendors/{id}/performance` | Get performance summary |
| PUT | `/api/v1/vendors/ratings/{id}` | Update rating |
| DELETE | `/api/v1/vendors/ratings/{id}` | Delete rating |

### RFQ Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rfq` | Create RFQ |
| GET | `/api/v1/rfq` | List RFQs (paginated) |
| GET | `/api/v1/rfq/{id}` | Get RFQ details |
| PUT | `/api/v1/rfq/{id}` | Update RFQ |
| PATCH | `/api/v1/rfq/{id}/status` | Update RFQ status |
| DELETE | `/api/v1/rfq/{id}` | Delete RFQ |
| GET | `/api/v1/rfq/{id}/compare` | Compare quotes |

### RFQ Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rfq/{id}/items` | Add item |
| GET | `/api/v1/rfq/{id}/items` | List items |
| PUT | `/api/v1/rfq/items/{id}` | Update item |
| DELETE | `/api/v1/rfq/items/{id}` | Delete item |

### Vendor Invitations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rfq/{id}/invitations` | Invite vendor |
| GET | `/api/v1/rfq/{id}/invitations` | List invitations |
| POST | `/api/v1/rfq/invitations/{id}/accept` | Accept invitation |
| POST | `/api/v1/rfq/invitations/{id}/decline` | Decline invitation |
| DELETE | `/api/v1/rfq/invitations/{id}` | Remove invitation |

### Quotations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/quotations/rfq/{id}` | Create quotation |
| GET | `/api/v1/quotations/rfq/{id}` | List RFQ quotations |
| GET | `/api/v1/quotations/{id}` | Get quotation |
| PUT | `/api/v1/quotations/{id}` | Update quotation |
| POST | `/api/v1/quotations/{id}/submit` | Submit quotation |
| POST | `/api/v1/quotations/{id}/evaluate` | Evaluate quotation |
| POST | `/api/v1/quotations/{id}/accept` | Accept quotation |
| POST | `/api/v1/quotations/{id}/reject` | Reject quotation |

### Quotation Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/quotations/{id}/items` | Add item |
| PUT | `/api/v1/quotations/items/{id}` | Update item |
| DELETE | `/api/v1/quotations/items/{id}` | Delete item |

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Project Structure

```
procure-pro-iso/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── vendors.py   # Vendor endpoints
│   │       ├── categories.py # Category endpoints
│   │       ├── rfq.py       # RFQ endpoints
│   │       └── quotations.py # Quotation endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database configuration
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── pagination.py    # Pagination utilities
│   │   └── security.py      # Security utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vendor.py        # Vendor models
│   │   ├── rfq.py           # RFQ models
│   │   └── user.py          # User model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── vendor.py        # Vendor schemas
│   │   └── rfq.py           # RFQ schemas
│   └── services/
│       ├── __init__.py
│       ├── vendor.py        # Vendor service
│       ├── rfq.py           # RFQ service
│       └── email.py         # Email service
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_vendors.py      # Vendor tests
│   ├── test_rfq.py          # RFQ tests
│   └── test_health.py       # Health check tests
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── pytest.ini
└── requirements.txt
```

## ISO Standards Support

The system supports tracking compliance with:

- **ISO 9001**: Quality Management Systems
- **ISO 14001**: Environmental Management Systems
- **ISO 17025**: Laboratory Competence
- **ISO 45001**: Occupational Health and Safety
- **IATF 16949**: Automotive Quality Management
- **ISO 22000**: Food Safety Management
- **ISO 27001**: Information Security Management

## RFQ Status Workflow

```
┌─────────┐     ┌───────────┐     ┌──────────────┐     ┌─────────┐     ┌────────┐
│  Draft  │────►│ Published │────►│ Under Review │────►│ Awarded │────►│ Closed │
└─────────┘     └───────────┘     └──────────────┘     └─────────┘     └────────┘
     │               │                   │
     │               │                   │
     ▼               ▼                   ▼
┌───────────┐   ┌───────────┐       ┌───────────┐
│ Cancelled │   │ Cancelled │       │ Cancelled │
└───────────┘   └───────────┘       └───────────┘
```

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
