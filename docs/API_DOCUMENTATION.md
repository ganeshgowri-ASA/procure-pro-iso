# Procure-Pro-ISO API Documentation

## Overview

The Procure-Pro-ISO API provides RESTful endpoints for managing procurement operations including projects, vendors, RFQs, quotations, purchase orders, and technical bid evaluations.

**Base URL:** `/api/v1`

**Content-Type:** `application/json`

---

## Authentication

*Coming Soon* - JWT-based authentication will be implemented.

---

## Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "procure-pro-iso",
  "version": "1.0.0"
}
```

---

### Projects

#### List Projects

```
GET /api/v1/projects
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page (max 100) |
| status | string | - | Filter by status |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "project_number": "PRJ-00001",
      "name": "Project Name",
      "client_name": "Client Corp",
      "status": "active",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "budget": 100000.00,
      "currency": "USD",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### Create Project

```
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description",
  "client_name": "Client Corp",
  "status": "active",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "budget": 100000.00,
  "currency": "USD"
}
```

#### Get Project

```
GET /api/v1/projects/{id}
```

#### Update Project

```
PUT /api/v1/projects/{id}
```

#### Delete Project

```
DELETE /api/v1/projects/{id}
```

---

### Vendors

#### List Vendors

```
GET /api/v1/vendors
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number |
| limit | integer | Items per page |
| is_approved | boolean | Filter by approval status |
| search | string | Search by name or code |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "vendor_code": "VND-00001",
      "company_name": "Vendor Corp",
      "contact_person": "John Doe",
      "email": "vendor@example.com",
      "phone": "+1234567890",
      "city": "Dubai",
      "country": "UAE",
      "is_approved": true,
      "rating": 4.5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### Create Vendor

```
POST /api/v1/vendors
```

**Request Body:**
```json
{
  "company_name": "Vendor Corp",
  "trade_name": "VC Trading",
  "contact_person": "John Doe",
  "email": "vendor@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "Dubai",
  "country": "UAE",
  "website": "https://vendor.com",
  "tax_id": "TAX123",
  "payment_terms": "Net 30",
  "vendor_type": "supplier"
}
```

---

### RFQs (Request for Quotation)

#### List RFQs

```
GET /api/v1/rfqs
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (draft, open, closed, cancelled) |
| project_id | uuid | Filter by project |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "rfq_number": "RFQ-000001",
      "title": "RFQ for Materials",
      "status": "open",
      "issue_date": "2024-01-01",
      "closing_date": "2024-01-15",
      "currency": "USD",
      "estimated_value": 50000.00,
      "project_number": "PRJ-00001",
      "project_name": "Main Project",
      "item_count": 10,
      "quotation_count": 3,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create RFQ

```
POST /api/v1/rfqs
```

**Request Body:**
```json
{
  "title": "RFQ for Construction Materials",
  "description": "Materials needed for Phase 1",
  "project_id": "uuid",
  "rfq_type": "standard",
  "priority": "high",
  "issue_date": "2024-01-01",
  "closing_date": "2024-01-15",
  "validity_days": 30,
  "delivery_location": "Project Site A",
  "currency": "USD",
  "estimated_value": 50000.00,
  "terms_and_conditions": "Standard T&C apply"
}
```

---

### Quotations

#### List Quotations

```
GET /api/v1/quotations
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| rfq_id | uuid | Filter by RFQ |
| vendor_id | uuid | Filter by vendor |

#### Create Quotation

```
POST /api/v1/quotations
```

**Request Body:**
```json
{
  "rfq_id": "uuid",
  "vendor_id": "uuid",
  "validity_date": "2024-02-15",
  "currency": "USD",
  "payment_terms": "Net 30",
  "delivery_terms": "FOB Destination",
  "delivery_days": 14,
  "items": [
    {
      "rfq_item_id": "uuid",
      "description": "Steel Pipes",
      "quantity": 100,
      "unit_price": 45.00,
      "brand_offered": "BrandX",
      "lead_time_days": 7
    }
  ]
}
```

---

### Purchase Orders

#### List Purchase Orders

```
GET /api/v1/purchase-orders
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status |
| vendor_id | uuid | Filter by vendor |

#### Create Purchase Order

```
POST /api/v1/purchase-orders
```

---

### TBE Evaluations

#### List TBE Evaluations

```
GET /api/v1/tbe-evaluations
```

#### Calculate TBE Scores

```
POST /api/v1/tbe-evaluations/{id}/calculate
```

Calculates weighted scores for all quotations in the evaluation.

**Response:**
```json
{
  "message": "TBE calculation completed",
  "data": {
    "evaluation_id": "uuid",
    "rfq_id": "uuid",
    "scores": [
      {
        "quotation_id": "uuid",
        "vendor_name": "Vendor A",
        "price_score": 85.50,
        "quality_score": 90.00,
        "delivery_score": 80.00,
        "compliance_score": 95.00,
        "total_weighted_score": 87.25,
        "rank": 1,
        "is_recommended": true
      }
    ],
    "recommended_vendor_id": "uuid"
  }
}
```

---

### Reports

#### Dashboard

```
GET /api/v1/reports/dashboard
```

**Response:**
```json
{
  "data": {
    "active_projects": 15,
    "open_rfqs": 8,
    "active_pos": 24,
    "approved_vendors": 120,
    "total_po_value": 2500000.00,
    "recent_quotations": 12
  }
}
```

#### Procurement Summary

```
GET /api/v1/reports/procurement-summary
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | date | Start of period |
| end_date | date | End of period |

---

### Utilities

#### List Units of Measure

```
GET /api/v1/units-of-measure
```

#### List Currencies

```
GET /api/v1/currencies
```

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

**HTTP Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Pagination

All list endpoints support pagination:

**Request:**
```
GET /api/v1/projects?page=2&limit=50
```

**Response includes:**
```json
{
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 150,
    "pages": 3
  }
}
```
