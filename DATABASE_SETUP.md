# Database Setup Guide for Railway

This guide explains how to set up the Procure-Pro-ISO database on Railway.

## Connection Types

Railway provides two ways to connect to PostgreSQL:

### 1. Internal Connection (Within Railway)
```
postgresql://postgres:password@postgres.railway.internal:5432/railway
```
- Used when running inside Railway (e.g., from your deployed application)
- Lower latency, no data transfer costs
- This is the recommended connection for production

### 2. Public Proxy Connection (External Access)
```
postgresql://postgres:password@<public-host>.railway.app:5432/railway
```
- Used for local development or external tools
- Find this URL in Railway Dashboard → PostgreSQL service → Connect tab

## Automatic Setup (Recommended)

When you deploy to Railway, the application automatically:
1. Runs database migrations to create all 30 tables
2. Inserts seed data (sample vendors, categories, products)
3. Starts the FastAPI server

This is configured in `Procfile` and `railway.json`.

## Manual Setup

### From Within Railway (Railway Shell)
```bash
# Run migrations
python -m database.migration_runner migrate

# Insert seed data
python -m database.migration_runner seed

# Check status
python -m database.migration_runner status
```

### From Local Machine
1. Get the **public proxy** connection URL from Railway Dashboard
2. Set it in your `.env` file:
   ```
   DATABASE_URL=postgresql://postgres:password@<public-host>.railway.app:5432/railway
   ```
3. Run the migration:
   ```bash
   python -m database.migration_runner setup --with-seeds
   ```

## Verifying the Setup

### Check via API (after deployment)
```bash
# Health check
curl https://your-app.railway.app/health

# Database health
curl https://your-app.railway.app/health/db

# List tables
curl https://your-app.railway.app/api/v1/db/tables

# Schema version
curl https://your-app.railway.app/api/v1/db/schema-version
```

### Check via Railway CLI
```bash
railway run python -m database.migration_runner status
```

## Database Schema

The migration creates 30 tables:

| Category | Tables |
|----------|--------|
| Organization | organizations, users, user_permissions |
| Vendor | vendors, vendor_evaluations, vendor_documents |
| Product | categories, products, technical_specifications |
| RFQ | rfqs, rfq_items, rfq_invitations |
| Quotation | quotations, quotation_items, technical_bid_evaluations |
| Purchase | purchase_orders, purchase_order_items |
| Receipt | goods_receipts, goods_receipt_items |
| Testing | acceptance_tests, acceptance_test_results |
| Asset | assets, asset_calibrations, asset_maintenance |
| Compliance | audit_trail, document_control, non_conformance_reports |
| Workflow | notifications, approval_workflows, approval_steps |
| System | schema_version |

## Seed Data

The seed data includes:
- 3 sample organizations
- 5 users with different roles
- 15 categories (hierarchical)
- 6 vendors with evaluations
- 6 products with specifications
- Sample RFQs and documents

## Troubleshooting

### "could not translate host name" Error
This means you're trying to use the internal Railway URL from outside Railway.
Use the public proxy URL instead.

### Connection Timeout
- Check if Railway PostgreSQL service is running
- Verify credentials in DATABASE_URL
- Check Railway service logs for errors

### Tables Not Created
```bash
# Re-run migration
python -m database.migration_runner migrate

# Or reset and recreate (DELETES ALL DATA)
python -m database.migration_runner reset
python -m database.migration_runner setup --with-seeds
```
