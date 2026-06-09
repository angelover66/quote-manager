# CDMO Quotation Management Platform — Design Specification

**Version**: v1.0  
**Date**: 2026-06-09  
**Author**: Lulu  
**Status**: Design Approved → Ready for Implementation

---

## 1. Product Overview

### 1.1 Product Positioning

A CDMO (Contract Development and Manufacturing Organization) quotation management platform that enables sales teams to manage product catalogs and create structured quotations. Built as a portfolio project demonstrating B2B SaaS product thinking.

### 1.2 Target Users

| Role | Capabilities |
|------|-------------|
| **Salesperson** | Manage products, create/edit quotations, submit for review |
| **Reviewer** | View quotations (review workflow reserved for v2) |

### 1.3 Core Value

- Centralize CDMO product pricing in a structured catalog with clear pricing units
- Streamline quotation creation with auto-filled guide prices and automatic calculations
- Enforce pricing logic: project-based items lock quantity, batch/study-based items allow manual quantity input

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Streamlit (Python) | Rapid development, Lulu's preferred stack for portfolio demos |
| Database | SQLite | Zero-config local storage, sufficient for single-user demo |
| Auth | Custom username/password + session state | Simple role-based access without external auth services |
| Deployment | Local `streamlit run` | Personal demo and interview showcase |

### 2.1 Streamlit Multi-Page Structure

```
quote-manager/
├── Home.py                 # Login page + auth routing
├── pages/
│   ├── 1_Product_Management.py   # Product list + create
│   ├── 2_Quotation_Management.py # Quotation list + create + detail
├── src/
│   ├── database.py          # SQLite connection + CRUD
│   ├── models.py            # Data models (dataclass/typed dict)
│   ├── auth.py              # Authentication helpers
│   └── components.py        # Reusable UI components
├── data/
│   └── app.db               # SQLite database file
├── docs/
│   └── superpowers/
│       └── specs/           # Design documents
├── 产品介绍.md
├── 产品更新日志.md
└── docs/designs/
    └── 产品设计文档.md
```

---

## 3. Data Model

### 3.1 ER Diagram

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   users     │    │    products      │    │   quotations    │
├─────────────┤    ├──────────────────┤    ├─────────────────┤
│ id (PK)     │    │ id (PK)          │    │ id (PK)         │
│ username    │    │ product_code     │    │ quote_no        │
│ password    │    │ product_type     │    │ customer        │
│ role        │    │ guide_price      │    │ requirement     │
│ created_at  │    │ unit             │    │ budget          │
└─────────────┘    │ status           │    │ status          │
                   │ created_at       │    │ created_by (FK) │
                   └──────────────────┘    │ created_at      │
                                           │ updated_at      │
       ┌─────────────────────┐             └────────┬────────┘
       │  quotation_items    │                      │
       ├─────────────────────┤                      │
       │ id (PK)             │                      │
       │ quotation_id (FK)   │──────────────────────┘
       │ product_id (FK)     │──→ products
       │ guide_price (带入)   │
       │ quoted_price (人工)  │
       │ quantity (人工/锁定) │
       │ line_total (计算)    │
       └─────────────────────┘
```

### 3.2 Table Definitions

#### users

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | User ID |
| username | TEXT | NOT NULL UNIQUE | Login username |
| password_hash | TEXT | NOT NULL | Hashed password |
| role | TEXT | NOT NULL | 'salesperson' or 'reviewer' |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | Creation time |

#### products

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal ID |
| product_code | TEXT | NOT NULL UNIQUE | e.g., P20260601-001 |
| product_type | TEXT | NOT NULL | One of 8 CDMO product types |
| guide_price | REAL | NOT NULL | Sales guide price in CNY |
| unit | TEXT | NOT NULL | Pricing unit: project/batch/study |
| status | TEXT | DEFAULT 'Active' | Active / Inactive |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |

#### quotations

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal ID |
| quote_no | TEXT | NOT NULL UNIQUE | e.g., Q20260609-001 |
| customer | TEXT | NOT NULL | Client company name |
| requirement | TEXT | NOT NULL | Requirement details |
| budget | REAL | NOT NULL | Client budget in CNY |
| total_quoted | REAL | | Computed sum of line totals |
| status | TEXT | DEFAULT 'Draft' | Draft / Submitted |
| created_by | INTEGER | FK → users.id | |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |
| updated_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |

#### quotation_items

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| quotation_id | INTEGER | FK → quotations.id | Parent quotation |
| product_id | INTEGER | FK → products.id | Selected product |
| guide_price | REAL | NOT NULL | Auto-filled from product |
| quoted_price | REAL | NOT NULL | Manual entry by sales |
| quantity | INTEGER | NOT NULL | 1 if unit=project; editable otherwise |
| line_total | REAL | GENERATED | quoted_price × quantity |

### 3.3 CDMO Product Catalog (8 predefined)

| # | Product Type | English Name | Guide Price | Unit |
|---|-------------|-------------|------------|------|
| 1 | API Process Development | API Process Development | ¥1,200,000 | project |
| 2 | API GMP Manufacturing | API GMP Manufacturing | ¥800,000 | batch |
| 3 | Formulation & Process Dev | Formulation & Process Development | ¥900,000 | project |
| 4 | Drug Product GMP Mfg | Drug Product GMP Manufacturing | ¥2,000,000 | batch |
| 5 | Analytical Method Dev & Val | Analytical Method Development & Validation | ¥350,000 | project |
| 6 | Stability Study | Stability Study | ¥200,000 | study |
| 7 | Release Testing | Release Testing | ¥50,000 | batch |
| 8 | CTD Dossier Preparation | CTD Dossier Preparation | ¥400,000 | project |

---

## 4. Page Flow & Navigation

### 4.1 Navigation Structure

```
Login (Home.py)
  │
  └── Sidebar Navigation (2 items only)
        ├── 📦 Product Management
        └── 📋 Quotation Management
              ├── List View (default)
              ├── Create Quotation (button → inline form)
              └── Detail View (click row → expand)
```

### 4.2 Page Details

#### Page 1: Login (`Home.py`)
- Centered login card
- Username + password fields
- Role-based routing after login
- Demo credentials displayed

#### Page 2: Product Management (`pages/1_Product_Management.py`)
- Product table with columns: Product ID, Product Type, Guide Price, Unit, Status, Created
- "+ New Product" button → inline form (product type dropdown + guide price + unit selector)
- Product code auto-generated (P + date + sequence)

#### Page 3: Quotation Management (`pages/2_Quotation_Management.py`)

Three sub-views managed via session state:

**3a. List View** (default):
- Quotation table: Quote No., Client, Budget, Total Quoted, Status, Prepared By, Date
- "+ Create Quotation" button
- Click row → Detail View

**3b. Create Quotation** (single page, two sections):
- Section 1 — Basic Information: Client Name, Budget Amount, Requirement Details
- Section 2 — Line Items:
  - Product dropdown selector + "Add" button
  - Line items table with editable fields
  - Guide price auto-filled (read-only), Quoted Price (editable), Quantity (conditional)
  - Quantity logic: unit = "project" → locked at 1 (disabled); unit = "batch"/"study" → editable
  - Line Total = Quoted Price × Quantity (auto-calculated)
  - Delete row button (✕)
- Bottom total: sum of all Line Totals (by quoted price, NOT guide price)
- Two buttons: "Save as Draft" / "Submit for Review"

**3c. Detail View** (click from list):
- "← Back to List" navigation
- Basic Information card (client, budget, prepared by, requirements)
- Line Items table (read-only)
- Quoted Total summary

### 4.3 State Machine

```
Quotation Status:
  Draft ──→ Submitted
    │           │
    └── Edit ───┘ (v2: with reviewer comments)

Product Status:
  Active ←→ Inactive
```

---

## 5. Business Logic Rules

### 5.1 Pricing Unit Rules

| Unit | Quantity Behavior | Example |
|------|------------------|---------|
| project | Locked at 1, disabled input | API Process Development |
| batch | Editable, integer ≥ 1 | API GMP Manufacturing × 3 batches |
| study | Editable, integer ≥ 1 | Stability Study × 2 studies |

### 5.2 Calculation Rules

- **Line Total** = `quoted_price` × `quantity`
- **Quotation Total** = Σ(all line totals) — aggregated by quoted price
- Guide price is for reference only; does NOT participate in total calculation

### 5.3 Validation Rules

| Field | Rule |
|-------|------|
| Product Type | Required, must match predefined list of 8 |
| Guide Price | Required, numeric > 0 |
| Unit | Required, one of: project / batch / study |
| Client Name | Required, non-empty |
| Budget | Required, numeric > 0 |
| Requirement | Required, non-empty |
| Line Items | At least 1 line item required before submit |
| Quoted Price | Required, numeric > 0 |
| Quantity | Required, integer ≥ 1 |

---

## 6. UI Design System

### 6.1 Visual Style

**Option B: Clean Light + Indigo Accent**

- Background: `#f5f7fa`
- Card: white, `border: 1px solid #e5e7eb`, `border-radius: 8-10px`
- Primary color: `#6366f1` (Indigo)
- Text primary: `#1a1a2e`
- Text secondary: `#6b7280`
- Text tertiary: `#9ca3af`
- Success/Active: `#e0e7ff` bg, `#4338ca` text
- Warning/Draft: `#fef3c7` bg, `#92400e` text
- Delete/Danger: `#ef4444`

### 6.2 Components

- Sidebar: 200px fixed width, white background, right border
- Table: clean lines, zebra-free, hover highlight on clickable rows
- Form inputs: `border-radius: 6-8px`, `border: 1px solid #e5e7eb`
- Primary button: Indigo bg, white text, 8px radius
- Secondary button: white bg, gray border
- Status badges: pill-shaped, 10px radius

---

## 7. Error Handling & Edge Cases

| Scenario | Handling |
|----------|---------|
| Empty product catalog | Show "No products yet" empty state with CTA |
| Product in use by quotation | Prevent deletion, show warning |
| Submit with 0 line items | Validation error, highlight Line Items section |
| Submit with empty client name | Validation error, highlight field |
| Quantity ≤ 0 | Validation error, inline message |
| Concurrent session conflict | SQLite handles with write-ahead logging |
| Database not found | Auto-create tables on first run |

---

## 8. Seed Data

On first launch, auto-populate:
- 2 demo users: `sales` (salesperson) / `reviewer` (reviewer), password `123456`
- 8 CDMO products as defined in §3.3
- 3 sample quotations for demonstration

---

## 9. Out of Scope (v2+)

- Reviewer approval/rejection workflow
- Quotation version history
- PDF export
- Email notification
- Multi-currency support
- Discount/coupon logic
- Audit trail

---

## 10. Test Strategy

### P0 Test Cases

| # | Scenario | Steps | Expected Result |
|---|---------|-------|-----------------|
| T1 | Login with valid credentials | Enter username/password → click Login | Redirect to sidebar, show role-appropriate nav |
| T2 | Login with invalid credentials | Enter wrong password → click Login | Show error message |
| T3 | View product list | Navigate to Product Management | Display 8 CDMO products in table |
| T4 | Create new product | Click "+ New Product" → fill form → confirm | Product appears in table |
| T5 | View quotation list | Navigate to Quotation Management | Display quotations in table |
| T6 | Create quotation — add project-type product | Select "API Process Development" → add | Guide price auto-filled, quantity locked at 1 |
| T7 | Create quotation — add batch-type product | Select "API GMP Manufacturing" → add | Guide price auto-filled, quantity editable |
| T8 | Line total auto-calculation | Enter quoted price + quantity | Line total updates correctly |
| T9 | Quotation total aggregation | Add multiple line items | Bottom total = sum of all line totals |
| T10 | Submit quotation | Fill all fields → "Submit for Review" | Status changes to "Submitted" |
| T11 | View quotation detail | Click row in list | Detail view with basic info + line items |
| T12 | Save as draft | Partial fill → "Save as Draft" | Status = "Draft", can edit later |

---

## 11. Document Tracking

| Document | Path | Status |
|----------|------|--------|
| Product Introduction | `/产品介绍.md` | To be created |
| Product Changelog | `/产品更新日志.md` | To be created |
| Technical Design | `/docs/designs/产品设计文档.md` | To be created |
