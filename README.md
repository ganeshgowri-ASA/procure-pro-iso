# Procure-Pro-ISO

Comprehensive ISO-compliant procurement lifecycle management system - From RFQ to Asset Management. Covers technical specs, vendor evaluation, TBE analysis, PO tracking, FAT-SAT testing, and equipment history per ISO 17025, ISO 9001, IATF 16949 standards.

## Project Structure

```
procure-pro-iso/
├── api/                    # FastAPI backend
│   ├── models.py          # SQLAlchemy ORM models
│   ├── routes.py          # REST API endpoints
│   ├── schemas.py         # Pydantic validation schemas
│   └── utils/             # Utility modules
├── config/                # Configuration settings
├── database/              # Database schemas and connection
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   ├── hooks/         # Custom React hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── package.json
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Frontend

Modern React frontend for procurement analysis and dashboard.

### Features

- **Dashboard**: Overview with RFQ cards, quick stats, and activity feed
- **Equipment Analysis**: Data table with parsed Excel data from SharePoint
- **Vendor Comparison**: Side-by-side comparison with charts (bar chart, radar chart)
- **Timeline View**: Gantt-style timeline for equipment delivery tracking

### Tech Stack

- React 18 with TypeScript
- Tailwind CSS for styling
- Recharts for data visualization
- Axios for API calls
- React Router for navigation
- Vite for build tooling

### Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Backend API

Flask-based REST API with SQLAlchemy ORM.

### Endpoints

- `GET /api/v1/rfqs` - List RFQs
- `GET /api/v1/vendors` - List vendors
- `GET /api/v1/quotations` - List quotations
- `GET /api/v1/tbe-evaluations` - List TBE evaluations
- `GET /api/v1/purchase-orders` - List purchase orders
- `GET /api/v1/reports/dashboard` - Dashboard statistics

### Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the development server
python app.py
```

## ISO Compliance

This system supports compliance with:

- **ISO 17025** - Testing and calibration laboratories
- **ISO 9001** - Quality management systems
- **IATF 16949** - Automotive quality management

## License

MIT License - See [LICENSE](LICENSE) for details.
