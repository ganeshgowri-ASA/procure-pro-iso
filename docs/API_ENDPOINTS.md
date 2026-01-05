# Procure-Pro-ISO API Endpoints

This document outlines the API endpoints for the Procure-Pro-ISO backend (to be implemented).

## Base URL

```
Production: https://api.procure-pro-iso.com/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication via JWT tokens.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Auth Endpoints

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "procurement_manager"
  }
}
```

### POST /auth/refresh

Refresh access token.

### POST /auth/logout

Invalidate current tokens.

---

## Equipment Endpoints

### GET /equipment

List all equipment with pagination and filters.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| limit | int | Items per page (default: 20) |
| search | string | Search by name, ID, or manufacturer |
| category | string | Filter by category |
| status | string | Filter by status |
| sort | string | Sort field (e.g., "name", "-created_at") |

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "equipment_id": "EQ-001",
      "name": "CNC Milling Machine",
      "category": "Manufacturing",
      "manufacturer": "HAAS",
      "model": "VF-2SS",
      "specifications": "5-axis, 12000 RPM",
      "quantity": 2,
      "unit_price": 89500,
      "total_price": 179000,
      "status": "Active",
      "rfq_status": "Completed",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

### GET /equipment/:id

Get single equipment by ID.

### POST /equipment

Create new equipment.

**Request:**
```json
{
  "name": "New Machine",
  "category": "Manufacturing",
  "manufacturer": "Brand",
  "model": "Model-X",
  "specifications": "Specs here",
  "quantity": 1,
  "unit_price": 50000
}
```

### PUT /equipment/:id

Update equipment.

### DELETE /equipment/:id

Delete equipment.

### POST /equipment/:id/attachments

Upload file attachment.

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| file | File | Document file (PDF, DOC, XLSX) |
| type | string | Document type (spec, manual, certificate) |

---

## RFQ Endpoints

### GET /rfqs

List all RFQs with filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (draft, open, closed, awarded) |
| priority | string | Filter by priority |
| date_from | date | Issue date from |
| date_to | date | Issue date to |

### GET /rfqs/:id

Get RFQ details including items and vendor invites.

### POST /rfqs

Create new RFQ.

**Request:**
```json
{
  "title": "CNC Machinery Procurement",
  "description": "Procurement of CNC machines for expansion",
  "priority": "high",
  "closing_date": "2024-02-15",
  "estimated_value": 450000,
  "delivery_location": "Main Plant, Building A",
  "items": [
    {
      "description": "CNC Milling Machine",
      "specifications": "5-axis, 12000+ RPM",
      "quantity": 2,
      "unit": "EA",
      "target_price": 90000
    }
  ],
  "vendor_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### PUT /rfqs/:id

Update RFQ.

### POST /rfqs/:id/publish

Publish draft RFQ and notify vendors.

### POST /rfqs/:id/close

Close RFQ for submissions.

---

## Vendor Endpoints

### GET /vendors

List all vendors.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (approved, pending, blacklisted) |
| category | string | Filter by category |
| min_rating | float | Minimum rating (1-5) |

### GET /vendors/:id

Get vendor details with performance history.

**Response:**
```json
{
  "id": "uuid",
  "vendor_code": "V-001",
  "company_name": "Precision Machinery Co.",
  "contact_person": "John Smith",
  "email": "john@precision.com",
  "phone": "+1-555-0101",
  "country": "USA",
  "category": "Manufacturing Equipment",
  "rating": 4.8,
  "status": "Approved",
  "certifications": ["ISO 9001", "ISO 14001"],
  "performance": {
    "total_orders": 24,
    "total_value": 1250000,
    "on_time_delivery": 96,
    "quality_score": 98,
    "response_rate": 100
  },
  "order_history": [...]
}
```

### POST /vendors

Create new vendor.

### PUT /vendors/:id

Update vendor.

### POST /vendors/:id/approve

Approve pending vendor.

### POST /vendors/:id/blacklist

Blacklist vendor with reason.

---

## Technical Evaluation Endpoints

### GET /evaluations/technical

List technical evaluations.

### GET /evaluations/technical/:id

Get technical evaluation with scores.

### POST /evaluations/technical

Create new technical evaluation.

**Request:**
```json
{
  "rfq_id": "uuid",
  "title": "TBE for CNC Procurement",
  "criteria": [
    {
      "name": "Spindle Speed",
      "category": "technical",
      "weight": 15,
      "requirement": "≥ 12,000 RPM"
    }
  ]
}
```

### POST /evaluations/technical/:id/scores

Submit vendor scores.

**Request:**
```json
{
  "quotation_id": "uuid",
  "scores": [
    {
      "criteria_id": "uuid",
      "score": 95,
      "comments": "Exceeds requirement"
    }
  ]
}
```

---

## Commercial Evaluation Endpoints

### GET /evaluations/commercial

List commercial evaluations.

### GET /evaluations/commercial/:id

Get commercial evaluation with TCO breakdown.

### POST /evaluations/commercial/:id/calculate-tco

Calculate/recalculate TCO.

**Request:**
```json
{
  "analysis_period_years": 5,
  "discount_rate": 8,
  "annual_maintenance_percent": 5
}
```

---

## Quotation Endpoints

### GET /quotations

List quotations for an RFQ.

### POST /quotations

Submit vendor quotation.

### PUT /quotations/:id

Update quotation.

### POST /quotations/:id/accept

Accept quotation and create PO.

---

## Reports Endpoints

### GET /reports/dashboard

Get dashboard KPIs and summary data.

**Response:**
```json
{
  "kpis": {
    "total_equipment": 12,
    "total_budget": 1800000,
    "active_rfqs": 3,
    "pending_approvals": 4
  },
  "budget_trend": [...],
  "rfq_status_distribution": [...],
  "recent_activity": [...]
}
```

### GET /reports/equipment

Equipment summary report.

### GET /reports/vendors

Vendor performance report.

### GET /reports/rfqs

RFQ analytics report.

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Invalid or expired token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 422 | Invalid input data |
| INTERNAL_ERROR | 500 | Server error |

---

## Rate Limiting

- **Authenticated**: 1000 requests/hour
- **Unauthenticated**: 100 requests/hour

Headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

---

## Webhooks (Future)

Webhook events for integrations:

- `rfq.created`
- `rfq.published`
- `rfq.closed`
- `quotation.received`
- `vendor.approved`
- `po.created`
