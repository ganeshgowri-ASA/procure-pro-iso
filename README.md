# Procure-Pro-ISO

Comprehensive ISO-compliant procurement lifecycle management system - From RFQ to Asset Management. Covers technical specs, vendor evaluation, TBE analysis, PO tracking, FAT-SAT testing, and equipment history per ISO 17025, ISO 9001, IATF 16949 standards.

## Features

- **Vendor Management**: Registration, evaluation, and qualification per ISO standards
- **RFQ Management**: Request for quotation creation and distribution
- **Technical Bid Evaluation (TBE)**: Structured evaluation matrix with scoring
- **Purchase Order Tracking**: Full PO lifecycle management
- **Goods Receipt & Inspection**: Quality inspection with accept/reject workflow
- **FAT/SAT Testing**: Factory and Site Acceptance Test management
- **Asset Management**: Equipment tracking, calibration, and maintenance
- **Document Control**: ISO-compliant document management
- **Audit Trail**: Complete traceability of all changes
- **Non-Conformance Reports**: NCR tracking and corrective actions

## Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL (Railway)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic + Custom migration runner
- **Testing**: pytest

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database (Railway or local)

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/procure-pro-iso.git
cd procure-pro-iso

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup

#### Configure Environment Variables

For Railway PostgreSQL, set one of these in your `.env`:

```bash
# Option 1: Full DATABASE_URL (recommended for Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# Option 2: Individual variables
PGHOST=your-railway-host.railway.app
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=your-password
```

#### Run Database Setup

```bash
# Test database connection
make db-test
# or
python scripts/test_connection.py

# Run full setup (schema + seed data)
make setup
# or
python scripts/setup.py
```

#### Manual Migration Steps

```bash
# Run schema migration only
python -m database.migration_runner migrate

# Insert seed data
python -m database.migration_runner seed

# Check status
python -m database.migration_runner status
```

### Start the API Server

```bash
# Development mode with auto-reload
make run
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Database Schema

The system includes **30 tables** organized into modules:

| Module | Tables | Description |
|--------|--------|-------------|
| Organizations | 3 | Organizations, users, permissions |
| Vendors | 3 | Vendor master, evaluations, documents |
| Products | 3 | Categories, products, specifications |
| RFQ | 3 | RFQs, line items, invitations |
| Quotations | 3 | Quotations, items, TBE evaluations |
| Purchase Orders | 2 | POs, line items |
| Goods Receipt | 2 | Receipts, inspection items |
| Acceptance Testing | 2 | FAT/SAT tests, results |
| Assets | 3 | Assets, calibrations, maintenance |
| Compliance | 3 | Audit trail, documents, NCRs |
| Workflows | 3 | Notifications, workflows, approvals |

## API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Overall system health |
| `/health/db` | GET | Database health check |
| `/health/ready` | GET | Kubernetes readiness probe |
| `/health/live` | GET | Kubernetes liveness probe |

### Database Info

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/db/tables` | GET | List all database tables |
| `/api/v1/db/schema-version` | GET | Current schema version |
| `/api/v1/stats` | GET | Database statistics |

## Alembic Migrations

For future schema changes, use Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column to vendors"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show history
alembic history
```

## Project Structure

```
procure-pro-iso/
├── alembic/                  # Alembic migrations
│   ├── versions/             # Migration scripts
│   ├── env.py                # Migration environment
│   └── script.py.mako        # Migration template
├── app/                      # FastAPI application
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── database.py           # Database connection
│   └── main.py               # API endpoints
├── database/                 # Database management
│   ├── migrations/           # Custom migrations
│   ├── seeds/                # Seed data
│   │   └── seed_data.sql     # Initial seed data
│   ├── migration_runner.py   # Migration CLI tool
│   └── schema.sql            # Main database schema
├── scripts/                  # Utility scripts
│   ├── setup.py              # Full setup script
│   └── test_connection.py    # Connection test script
├── .env.example              # Environment template
├── alembic.ini               # Alembic configuration
├── Makefile                  # Common commands
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Make Commands

```bash
make help           # Show all available commands
make install        # Install dependencies
make setup          # Full database setup
make migrate        # Run schema migration
make seed           # Insert seed data
make db-test        # Test database connection
make db-status      # Show database status
make run            # Start development server
make test           # Run tests
make clean          # Remove cached files
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

ganeshgowri-ASA
