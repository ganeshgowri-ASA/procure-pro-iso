# Procure-Pro-ISO Frontend

A modern, production-ready React + TypeScript web application for ISO-compliant procurement lifecycle management.

## Features

- **Dashboard** - KPI cards, budget trends, RFQ status charts, and activity feeds
- **Equipment Master** - Equipment inventory with search, filters, and file uploads
- **RFQ Management** - Request for quotation workflow with vendor tracking
- **Vendor Management** - Supplier directory with performance metrics and ratings
- **Technical Evaluation** - CTQ comparison matrix with vendor scoring
- **Commercial Evaluation** - TCO calculator and price comparison

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Recharts** - Charts and visualizations
- **Lucide React** - Icons

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Output will be in the `dist` directory.

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/
│   │   ├── layout/      # Sidebar, Header, Layout
│   │   └── ui/          # Reusable UI components
│   ├── data/            # Sample data
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── EquipmentMaster.tsx
│   │   ├── RFQManagement.tsx
│   │   ├── VendorManagement.tsx
│   │   ├── TechnicalEvaluation.tsx
│   │   └── CommercialEvaluation.tsx
│   ├── types/           # TypeScript types
│   ├── App.tsx          # Root component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── vercel.json          # Vercel deployment config
```

## Design System

### Colors

- **Primary Gradient**: `rgba(88, 86, 214, 1)` to `rgba(103, 58, 183, 1)`
- **KPI Blue**: `#3b82f6`
- **KPI Green**: `#22c55e`
- **KPI Orange**: `#f97316`
- **KPI Purple**: `#8b5cf6`

### Components

- **Card** - Container with shadow and hover effects
- **KPICard** - Metric display with color-coded borders
- **Badge** - Status indicators (success, warning, danger, info)
- **Button** - Primary, secondary, outline, ghost variants
- **Table** - Data tables with headers and sorting
- **StarRating** - 5-star rating display
- **FileUpload** - Drag & drop file upload

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set the root directory to `frontend`
3. Vercel will auto-detect Vite and configure the build

Or use the CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Manual Deployment

1. Build the project: `npm run build`
2. Deploy the `dist` folder to any static hosting service

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_URL=http://localhost:8000/api
VITE_API_VERSION=v1
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## License

MIT License - see [LICENSE](../LICENSE) for details.
