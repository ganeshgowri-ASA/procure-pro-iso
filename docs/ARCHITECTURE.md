# Procure-Pro-ISO Architecture

## System Overview

Procure-Pro-ISO is a comprehensive procurement management system designed for ISO compliance. The system follows a modular architecture with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                    (React/Vue - Future)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Layer (Flask)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Routes    │  │   Schemas    │  │  Middleware  │          │
│  │  (REST API)  │  │ (Validation) │  │  (Auth/CORS) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ RFQ Parser   │  │TBE Calculator│  │  Workflows   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Models     │  │  Connection  │  │    Cache     │          │
│  │ (SQLAlchemy) │  │   Pooling    │  │   (Redis)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
procure-pro-iso/
├── api/                      # API Layer
│   ├── __init__.py
│   ├── routes.py             # REST API endpoints
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic schemas for validation
│   └── utils/                # Utility modules
│       ├── rfq_parser.py     # RFQ document parser
│       └── tbe_calculator.py # TBE scoring calculator
│
├── database/                 # Database Layer
│   ├── __init__.py
│   ├── connection.py         # Database connection management
│   └── schema.sql            # Complete SQL schema
│
├── config/                   # Configuration
│   ├── __init__.py
│   └── settings.py           # Environment-based settings
│
├── docs/                     # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   └── ARCHITECTURE.md
│
├── tests/                    # Test Suite
│   └── __init__.py
│
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── .gitignore
```

---

## Component Details

### 1. Application Entry Point (`app.py`)

The main Flask application factory:

- Creates Flask app instance
- Configures CORS
- Initializes database connection
- Registers API blueprints
- Sets up error handlers
- Provides health check endpoint

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    init_db(app)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    return app
```

### 2. API Routes (`api/routes.py`)

RESTful endpoints organized by resource:

- **Projects**: CRUD operations for projects
- **Vendors**: Vendor management with approval workflow
- **RFQs**: Request for quotation lifecycle
- **Quotations**: Vendor bid submissions
- **TBE**: Technical bid evaluations
- **Purchase Orders**: PO creation and management
- **Reports**: Dashboard and analytics

Features:
- Pagination decorator for list endpoints
- Error handling decorator
- Consistent JSON response format

### 3. Database Models (`api/models.py`)

SQLAlchemy ORM models with:

- UUID primary keys
- Timestamp mixins for audit
- Relationship definitions
- JSON/JSONB support for metadata

Key Models:
- `User`, `UserRole`
- `Project`, `Department`, `Organization`
- `Vendor`
- `Item`, `ItemCategory`
- `RFQ`, `RFQItem`
- `Quotation`, `QuotationItem`
- `TBEEvaluation`
- `PurchaseOrder`, `PurchaseOrderItem`
- `AuditLog`

### 4. Validation Schemas (`api/schemas.py`)

Pydantic schemas for:

- Request validation
- Response serialization
- Data transformation

Features:
- Type validation
- Custom validators
- Nested schema support
- JSON encoder configuration

### 5. RFQ Parser (`api/utils/rfq_parser.py`)

Document parsing utility supporting:

- **PDF**: Using pdfplumber
- **Excel**: Using pandas/openpyxl
- **CSV**: Standard parsing

Capabilities:
- Table extraction
- Header detection
- Unit normalization
- Date parsing
- Error/warning collection

### 6. TBE Calculator (`api/utils/tbe_calculator.py`)

Technical Bid Evaluation engine:

**Scoring Categories:**
- Price (default 40%)
- Quality (default 25%)
- Delivery (default 20%)
- Compliance (default 15%)

**Features:**
- Weighted scoring
- Automatic ranking
- Recommendation generation
- Score persistence

**Algorithm:**
```
Total Score = (Price × W_price) + (Quality × W_quality) +
              (Delivery × W_delivery) + (Compliance × W_compliance)
```

### 7. Database Connection (`database/connection.py`)

Connection management with:

- Connection pooling (SQLAlchemy)
- Railway DATABASE_URL support
- Context managers for sessions
- Health check utilities

Configuration:
- Pool size: 5
- Max overflow: 10
- Pool timeout: 30s
- Connection recycling: 1800s

### 8. Configuration (`config/settings.py`)

Environment-based configuration:

- **DevelopmentConfig**: Debug enabled, SQL echo
- **ProductionConfig**: Secure settings
- **TestingConfig**: Test database, CSRF disabled

---

## Deployment Architecture

### Railway Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                         Railway                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │   Flask App          │  │   PostgreSQL         │            │
│  │   (Gunicorn)         │──│   (Managed)          │            │
│  │   Port: $PORT        │  │                      │            │
│  └──────────────────────┘  └──────────────────────┘            │
│           │                          │                          │
│           │                          │                          │
│  ┌────────┴──────────────────────────┴────────┐                │
│  │              Environment Variables          │                │
│  │  DATABASE_URL, SECRET_KEY, etc.            │                │
│  └────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

**Required Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `PORT` - Server port (Railway sets this)

---

## Data Flow

### RFQ to Purchase Order Flow

```
1. Create Project
       │
       ▼
2. Create RFQ ──────────────────────────────┐
       │                                     │
       ▼                                     │
3. Add Items to RFQ                          │
       │                                     │
       ▼                                     │
4. Invite Vendors                            │
       │                                     │
       ▼                                     │
5. Vendors Submit Quotations                 │
       │                                     │
       ▼                                     │
6. Create TBE Evaluation                     │
       │                                     │
       ▼                                     │
7. Calculate Scores & Rankings               │
       │                                     │
       ▼                                     │
8. Select Winning Vendor                     │
       │                                     │
       ▼                                     │
9. Create Purchase Order                     │
       │                                     │
       ▼                                     │
10. Receive Goods ◄──────────────────────────┘
       │
       ▼
11. Process Invoice & Payment
```

---

## Security Considerations

### Current Implementation

1. **CORS Configuration**
   - Configurable allowed origins
   - Restricted methods and headers

2. **Input Validation**
   - Pydantic schema validation
   - SQL parameterization (no injection)

3. **Error Handling**
   - Sanitized error messages
   - No stack traces in production

### Planned Enhancements

1. **Authentication**
   - JWT token-based auth
   - Role-based access control

2. **Rate Limiting**
   - Flask-Limiter integration
   - Per-endpoint limits

3. **Audit Logging**
   - All CRUD operations logged
   - User tracking

---

## Performance Considerations

### Database Optimization

1. **Indexes**
   - Status columns
   - Foreign keys
   - Frequently queried fields

2. **Connection Pooling**
   - SQLAlchemy pool management
   - Pre-ping for stale connections

3. **Query Optimization**
   - Eager loading for relationships
   - Pagination for large datasets

### Caching Strategy (Future)

1. **Redis Cache**
   - Session storage
   - Frequently accessed data
   - Report caching

---

## Testing Strategy

### Unit Tests
- Model validation
- Schema serialization
- Utility functions

### Integration Tests
- API endpoints
- Database operations
- TBE calculations

### End-to-End Tests
- Complete workflows
- Document parsing
- Report generation

---

## Future Enhancements

### Phase 1: Core Improvements
- [ ] JWT Authentication
- [ ] Role-based permissions
- [ ] Email notifications
- [ ] File upload handling

### Phase 2: Advanced Features
- [ ] Approval workflows
- [ ] Budget tracking
- [ ] Vendor portal
- [ ] Advanced reporting

### Phase 3: Integrations
- [ ] ERP integration
- [ ] Accounting systems
- [ ] Document management
- [ ] Mobile app API
