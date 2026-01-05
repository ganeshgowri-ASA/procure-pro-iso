# Procure-Pro-ISO

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ganeshgowri-ASA/procure-pro-iso)

Comprehensive ISO-compliant procurement lifecycle management system. Covers technical specs, vendor evaluation, TBE analysis, PO tracking, FAT-SAT testing, and equipment history per ISO 17025, ISO 9001, and IATF 16949 standards.

## Features

### Frontend Application

- **Dashboard** - Real-time KPIs, budget trends, RFQ status, and activity feeds
- **Equipment Master** - Complete equipment inventory with search, filters, and document uploads
- **RFQ Management** - End-to-end request for quotation workflow
- **Vendor Management** - Supplier directory with performance tracking and star ratings
- **Technical Evaluation** - CTQ comparison matrix with vendor scoring (90.2, 88.7, 88.1)
- **Commercial Evaluation** - TCO calculator and price comparison tables

### Design Highlights

- Purple/blue gradient header (`rgba(88,86,214,1)` to `rgba(103,58,183,1)`)
- Responsive sidebar with hamburger menu
- Color-coded KPI cards with left border accents
- Professional charts using Recharts
- Clean white cards with shadows
- Status badges with semantic colors

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/procure-pro-iso.git
cd procure-pro-iso

# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
cd frontend
npm run build
```

## Project Structure

```
procure-pro-iso/
├── frontend/                 # React + TypeScript application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components (6 screens)
│   │   ├── data/             # Sample data
│   │   └── types/            # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── vercel.json           # Vercel deployment config
├── api/                      # Python backend (Flask)
├── database/                 # Database schema
├── docs/                     # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── API_ENDPOINTS.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   └── DEPLOYMENT_GUIDE.md
└── README.md
```

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS
- Recharts for visualizations
- React Router for navigation
- Lucide icons

### Backend (Planned)
- Python Flask REST API
- PostgreSQL database
- JWT authentication

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Deploy automatically

### Manual Deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

## Sample Data

The application includes realistic sample data:

| Metric | Value |
|--------|-------|
| Total Equipment | 12 |
| Total Budget | $1.8M |
| Active RFQs | 3 |
| Pending Approvals | 4 |
| Vendors | 7 |

## Screenshots

### Dashboard
- KPI cards with trend indicators
- Budget vs spending chart
- RFQ status pie chart
- Recent activity feed

### Technical Evaluation
- Vendor score cards (90.2, 88.7, 88.1)
- Radar chart comparison
- CTQ matrix with compliance indicators

### Commercial Evaluation
- Price comparison cards
- TCO breakdown chart
- 5-year cost analysis

## API Documentation

See [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) for the complete API reference.

## Database Schema

See [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for the full database design with 22+ tables.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues:
- Open a GitHub issue
- Check [documentation](docs/)
