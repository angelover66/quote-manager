# CDMO Quotation Management Platform — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit-based CDMO quotation management platform with product catalog, multi-step quotation creation, pricing unit logic, and role-based auth.

**Architecture:** Streamlit multi-page app (Home.py login + 2 pages), SQLite database with 4 tables, session-state-driven wizard. Auth gates all pages. Database auto-seeds 10 CDMO products, 2 demo users, and sample quotations on first launch.

**Tech Stack:** Python 3.11+, Streamlit, SQLite (sqlite3 stdlib), hashlib (password hashing), datetime

---

## File Structure

```
quote-manager/
├── requirements.txt              # streamlit
├── Home.py                       # Login page + auth gate
├── pages/
│   ├── 1_Product_Management.py   # Product list + create form
│   └── 2_Quotation_Management.py # List + Create + Detail (session_state)
├── src/
│   ├── __init__.py
│   ├── database.py               # Connection, schema, CRUD, seed
│   ├── auth.py                   # Login/logout, session helpers
│   └── components.py             # Reusable UI: sidebar, styles, cards
├── data/                         # SQLite auto-created here
├── docs/
│   ├── superpowers/
│   │   ├── specs/2026-06-09-cdmo-quotation-platform-design.md
│   │   └── plans/2026-06-09-cdmo-quotation-platform-plan.md
│   └── designs/
│       └── 产品设计文档.md
├── 产品介绍.md
└── 产品更新日志.md
```

---

### Task 1: Project Scaffolding & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `data/.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```txt
streamlit>=1.28.0
```

- [ ] **Step 2: Create src/__init__.py**

```python
# CDMO Quotation Management Platform — source package
```

- [ ] **Step 3: Create .gitignore**

```
data/*.db
__pycache__/
*.pyc
.env
.superpowers/
```

- [ ] **Step 4: Create data/.gitkeep** (empty file)

```bash
touch /Users/lulu/quote-manager/data/.gitkeep
```

- [ ] **Step 5: Install dependencies**

```bash
cd /Users/lulu/quote-manager && pip install -r requirements.txt
```

Expected: `Successfully installed streamlit-...`

---

### Task 2: Database Layer — Schema & Seed Data

**Files:**
- Create: `src/database.py`

This is the single most critical file. It handles connection, schema creation, 10-product seed, user seed, and all CRUD operations.

- [ ] **Step 1: Write database.py with schema + seed + CRUD**

```python
"""
CDMO Quotation Platform — Database Layer
SQLite connection, schema creation, seed data, CRUD operations.
"""

import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "app.db")


def get_connection() -> sqlite3.Connection:
    """Get SQLite connection with WAL mode and foreign keys enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist, then seed demo data if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- users table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('salesperson', 'reviewer')),
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # --- products table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT NOT NULL UNIQUE,
            product_type TEXT NOT NULL,
            guide_price REAL NOT NULL CHECK(guide_price > 0),
            unit TEXT NOT NULL CHECK(unit IN ('project', 'batch', 'study')),
            status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive')),
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # --- quotations table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_no TEXT NOT NULL UNIQUE,
            customer TEXT NOT NULL,
            requirement TEXT NOT NULL,
            budget REAL NOT NULL CHECK(budget > 0),
            total_quoted REAL DEFAULT 0,
            status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Submitted')),
            created_by INTEGER NOT NULL REFERENCES users(id),
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # --- quotation_items table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotation_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER NOT NULL REFERENCES quotations(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            guide_price REAL NOT NULL,
            quoted_price REAL NOT NULL CHECK(quoted_price > 0),
            quantity INTEGER NOT NULL CHECK(quantity >= 1),
            line_total REAL GENERATED ALWAYS AS (quoted_price * quantity) STORED
        )
    """)

    conn.commit()

    # --- Seed demo data if tables are empty ---
    if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed_users(conn)
    if cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        _seed_products(conn)
    if cursor.execute("SELECT COUNT(*) FROM quotations").fetchone()[0] == 0:
        _seed_quotations(conn)

    conn.close()


def _seed_users(conn):
    """Insert 2 demo users with hashed passwords."""
    import hashlib

    def _hash(pw: str) -> str:
        return hashlib.sha256(pw.encode()).hexdigest()

    users = [
        ("sales", _hash("123456"), "salesperson"),
        ("reviewer", _hash("123456"), "reviewer"),
    ]
    conn.executemany(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        users,
    )
    conn.commit()


def _seed_products(conn):
    """Insert 10 CDMO products."""
    products = [
        # 8 core products from design spec
        ("P20260601-001", "API Process Development", 1200000, "project"),
        ("P20260601-002", "API GMP Manufacturing", 800000, "batch"),
        ("P20260602-003", "Formulation & Process Development", 900000, "project"),
        ("P20260602-004", "Drug Product GMP Manufacturing", 2000000, "batch"),
        ("P20260603-005", "Analytical Method Development & Validation", 350000, "project"),
        ("P20260603-006", "Stability Study", 200000, "study"),
        ("P20260604-007", "Release Testing", 50000, "batch"),
        ("P20260604-008", "CTD Dossier Preparation", 400000, "project"),
        # 2 extended products
        ("P20260605-009", "Impurity Profiling & Characterization", 280000, "project"),
        ("P20260605-010", "Process Validation (PPQ)", 600000, "project"),
    ]
    conn.executemany(
        "INSERT INTO products (product_code, product_type, guide_price, unit) VALUES (?, ?, ?, ?)",
        products,
    )
    conn.commit()


def _seed_quotations(conn):
    """Insert 3 sample quotations with line items."""
    # Quotation 1: Submitted
    conn.execute(
        "INSERT INTO quotations (quote_no, customer, requirement, budget, total_quoted, status, created_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("Q20260609-001", "PharmaBio Therapeutics",
         "End-to-end CDMO services for Phase II oncology candidate — API process dev, 3-batch GMP mfg, formulation dev, stability study, CTD Module 3 for IND.",
         5000000, 4350000, "Submitted", 1),
    )
    q1_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Quotation 2: Submitted
    conn.execute(
        "INSERT INTO quotations (quote_no, customer, requirement, budget, total_quoted, status, created_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("Q20260608-002", "NovoGen Biopharma",
         "API GMP manufacturing support for Phase III — 5 batches API, release testing, stability study for registration.",
         3000000, 2780000, "Submitted", 1),
    )
    q2_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Quotation 3: Draft
    conn.execute(
        "INSERT INTO quotations (quote_no, customer, requirement, budget, status, created_by) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("Q20260607-003", "GenTech Pharmaceuticals",
         "Early-phase analytical method development and formulation screening for small molecule candidate.",
         2000000, "Draft", 1),
    )

    # Line items for Q1
    items_q1 = [
        (q1_id, 1, 1200000, 1150000, 1),
        (q1_id, 2, 800000, 750000, 3),
        (q1_id, 3, 900000, 850000, 1),
        (q1_id, 6, 200000, 100000, 1),
    ]
    conn.executemany(
        "INSERT INTO quotation_items (quotation_id, product_id, guide_price, quoted_price, quantity) "
        "VALUES (?, ?, ?, ?, ?)",
        items_q1,
    )

    # Line items for Q2
    items_q2 = [
        (q2_id, 2, 800000, 780000, 5),
        (q2_id, 7, 50000, 48000, 5),
        (q2_id, 6, 200000, 180000, 1),
    ]
    conn.executemany(
        "INSERT INTO quotation_items (quotation_id, product_id, guide_price, quoted_price, quantity) "
        "VALUES (?, ?, ?, ?, ?)",
        items_q2,
    )

    conn.commit()


# ─── CRUD Helpers ───────────────────────────────────────────

def get_all_products() -> list[dict]:
    """Return all products ordered by product_code."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products ORDER BY product_code"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_products() -> list[dict]:
    """Return active products for quotation dropdown."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE status = 'Active' ORDER BY product_code"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_product(product_type: str, guide_price: float, unit: str) -> dict:
    """Create a new product with auto-generated product_code. Returns the new product row."""
    conn = get_connection()
    today = datetime.now().strftime("%Y%m%d")
    # Get next sequence number for today
    existing = conn.execute(
        "SELECT COUNT(*) FROM products WHERE product_code LIKE ?",
        (f"P{today}-%",),
    ).fetchone()[0]
    seq = existing + 1
    product_code = f"P{today}-{seq:03d}"

    cursor = conn.execute(
        "INSERT INTO products (product_code, product_type, guide_price, unit) VALUES (?, ?, ?, ?)",
        (product_code, product_type, guide_price, unit),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


def get_all_quotations() -> list[dict]:
    """Return all quotations with creator username, ordered by created_at DESC."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT q.*, u.username as created_by_name
        FROM quotations q
        JOIN users u ON q.created_by = u.id
        ORDER BY q.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_quotation_detail(quote_id: int) -> dict | None:
    """Return quotation with basic info + line items."""
    conn = get_connection()
    q = conn.execute("""
        SELECT q.*, u.username as created_by_name
        FROM quotations q
        JOIN users u ON q.created_by = u.id
        WHERE q.id = ?
    """, (quote_id,)).fetchone()
    if not q:
        conn.close()
        return None

    items = conn.execute("""
        SELECT qi.*, p.product_type, p.product_code, p.unit
        FROM quotation_items qi
        JOIN products p ON qi.product_id = p.id
        WHERE qi.quotation_id = ?
        ORDER BY qi.id
    """, (quote_id,)).fetchall()

    conn.close()
    result = dict(q)
    result["items"] = [dict(i) for i in items]
    return result


def create_quotation(customer: str, requirement: str, budget: float,
                     created_by: int, items: list[dict], status: str = "Draft") -> dict:
    """
    Create a quotation with line items.
    items: list of dicts with keys: product_id, guide_price, quoted_price, quantity
    """
    conn = get_connection()
    today = datetime.now().strftime("%Y%m%d")
    existing = conn.execute(
        "SELECT COUNT(*) FROM quotations WHERE quote_no LIKE ?",
        (f"Q{today}-%",),
    ).fetchone()[0]
    seq = existing + 1
    quote_no = f"Q{today}-{seq:03d}"

    # Calculate total_quoted
    total_quoted = sum(it["quoted_price"] * it["quantity"] for it in items)

    cursor = conn.execute(
        """INSERT INTO quotations (quote_no, customer, requirement, budget, total_quoted, status, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (quote_no, customer, requirement, budget, total_quoted, status, created_by),
    )
    q_id = cursor.lastrowid

    for it in items:
        conn.execute(
            """INSERT INTO quotation_items (quotation_id, product_id, guide_price, quoted_price, quantity)
               VALUES (?, ?, ?, ?, ?)""",
            (q_id, it["product_id"], it["guide_price"], it["quoted_price"], it["quantity"]),
        )

    conn.commit()
    row = conn.execute("SELECT * FROM quotations WHERE id = ?", (q_id,)).fetchone()
    conn.close()
    return dict(row)


def verify_user(username: str, password: str) -> dict | None:
    """Verify credentials. Returns user dict or None."""
    import hashlib
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, pw_hash),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
```

- [ ] **Step 2: Verify database initialization**

```bash
cd /Users/lulu/quote-manager && python -c "
from src.database import init_db, get_all_products, get_all_quotations
init_db()
products = get_all_products()
print(f'Products: {len(products)}')
for p in products:
    print(f'  {p[\"product_code\"]} | {p[\"product_type\"]} | ¥{p[\"guide_price\"]:,.0f} | /{p[\"unit\"]}')
quotations = get_all_quotations()
print(f'Quotations: {len(quotations)}')
"
```

Expected:
```
Products: 10
  P20260601-001 | API Process Development | ¥1,200,000 | /project
  ...
  P20260605-010 | Process Validation (PPQ) | ¥600,000 | /project
Quotations: 3
```

---

### Task 3: Authentication Layer

**Files:**
- Create: `src/auth.py`

- [ ] **Step 1: Write auth.py**

```python
"""
CDMO Quotation Platform — Authentication
Login/logout helpers, session state management, auth gate decorator.
"""

import streamlit as st
from src.database import verify_user


def is_logged_in() -> bool:
    """Check if user is authenticated in current session."""
    return "user" in st.session_state and st.session_state.user is not None


def require_auth():
    """Gate: if not logged in, show login page and stop execution of calling page."""
    if not is_logged_in():
        st.switch_page("Home.py")


def login(username: str, password: str) -> bool:
    """Attempt login. Stores user in session_state on success."""
    user = verify_user(username, password)
    if user:
        st.session_state.user = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        }
        return True
    return False


def logout():
    """Clear session and return to login."""
    st.session_state.user = None
    st.session_state.pop("view", None)
    st.session_state.pop("line_items", None)
    st.session_state.pop("editing_quote", None)


def get_current_user() -> dict | None:
    """Get current user from session, or None if not logged in."""
    return st.session_state.get("user")
```

---

### Task 4: Login Page (Home.py)

**Files:**
- Create: `Home.py`

- [ ] **Step 1: Write Home.py**

```python
"""
CDMO Quotation Management Platform — Login Page
Role-based routing after authentication.
"""

import streamlit as st
from src.database import init_db
from src.auth import login, is_logged_in

st.set_page_config(
    page_title="CDMO Quotation Platform",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Initialize database on first run
init_db()

# Custom CSS for centered login card
st.markdown("""
<style>
    .stApp { background: #f5f7fa; }
    div[data-testid="stForm"] {
        background: white;
        padding: 40px 32px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# If already logged in, redirect to first page
if is_logged_in():
    st.switch_page("pages/1_Product_Management.py")

# Login form
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    st.markdown("""
    <div style="text-align:center; margin-bottom:28px; margin-top:80px;">
        <div style="width:48px; height:48px; background:#6366f1; border-radius:10px;
                    margin:0 auto 12px; display:flex; align-items:center; justify-content:center;
                    font-size:22px; color:white;">📋</div>
        <div style="font-size:20px; font-weight:700; color:#1a1a2e;">CDMO Quotation Platform</div>
        <div style="font-size:13px; color:#9ca3af; margin-top:4px;">Quotation Management System</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

        if submitted:
            if login(username, password):
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

    st.markdown("""
    <div style="text-align:center; margin-top:16px; font-size:11px; color:#9ca3af;">
        Demo: <b>sales</b> / <b>reviewer</b> &nbsp;|&nbsp; Password: <b>123456</b>
    </div>
    """, unsafe_allow_html=True)
```

- [ ] **Step 2: Verify login page loads**

```bash
cd /Users/lulu/quote-manager && streamlit run Home.py --server.headless true &
sleep 3 && curl -s http://localhost:8501 | head -20
```

Expected: HTML containing "CDMO Quotation Platform"

---

### Task 5: Reusable UI Components

**Files:**
- Create: `src/components.py`

- [ ] **Step 1: Write components.py**

```python
"""
CDMO Quotation Platform — Reusable UI Components
Sidebar navigation, CSS styling, display helpers.
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """Inject global CSS styles matching the Clean Light + Indigo design system."""
    st.markdown("""
    <style>
        /* Background */
        .stApp { background: #f5f7fa; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: white;
            border-right: 1px solid #f0f0f0;
        }
        section[data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
            background: white;
        }

        /* Cards */
        .css-card {
            background: white;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            padding: 20px;
            margin-bottom: 16px;
        }

        /* Primary button override */
        .stButton > button[kind="primary"] {
            background-color: #6366f1 !important;
            border: none !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        /* Secondary button */
        .stButton > button[kind="secondary"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            color: #6b7280 !important;
            background: white !important;
        }

        /* Table styling */
        table {
            font-size: 13px;
        }

        /* Input labels */
        .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #6b7280 !important;
            font-weight: 500 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with navigation and user info."""
    user = get_current_user()
    with st.sidebar:
        st.markdown("""
        <div style="padding: 4px 0 16px 0;">
            <div style="font-size:11px; color:#9ca3af; text-transform:uppercase;
                        letter-spacing:0.5px; font-weight:600;">NAVIGATION</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation — only 2 items
        pg = st.navigation([
            st.Page("pages/1_Product_Management.py", title="📦 Product Management", icon="📦"),
            st.Page("pages/2_Quotation_Management.py", title="📋 Quotation Management", icon="📋"),
        ])

        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

        # User info
        st.markdown(f"""
        <div style="border-top:1px solid #f0f0f0; padding-top:12px; margin-top:auto;">
            <div style="font-size:12px; color:#6b7280;">👤 {user['username']}</div>
            <div style="font-size:10px; color:#d1d5db; text-transform:capitalize;">{user['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True, type="secondary"):
            logout()
            st.switch_page("Home.py")


def status_badge(status: str) -> str:
    """Return HTML for a pill-shaped status badge."""
    if status.lower() == "active":
        return '<span style="background:#e0e7ff; color:#4338ca; padding:3px 8px; border-radius:10px; font-size:11px;">Active</span>'
    elif status.lower() == "inactive":
        return '<span style="background:#fef3c7; color:#92400e; padding:3px 8px; border-radius:10px; font-size:11px;">Inactive</span>'
    elif status.lower() == "submitted":
        return '<span style="background:#e0e7ff; color:#4338ca; padding:3px 8px; border-radius:10px; font-size:11px;">Submitted</span>'
    elif status.lower() == "draft":
        return '<span style="background:#fef3c7; color:#92400e; padding:3px 8px; border-radius:10px; font-size:11px;">Draft</span>'
    return status


def format_price(amount: float | int | None) -> str:
    """Format a number as CNY price string."""
    if amount is None:
        return "—"
    return f"¥{amount:,.0f}"
```

---

### Task 6: Product Management Page

**Files:**
- Create: `pages/1_Product_Management.py`

This page shows the product list table and a "New Product" inline form.

- [ ] **Step 1: Write 1_Product_Management.py**

```python
"""
CDMO Quotation Platform — Product Management Page
Display all products, create new product with auto-generated code.
"""

import streamlit as st
from src.database import init_db, get_all_products, create_product
from src.auth import require_auth
from src.components import inject_css, render_sidebar, status_badge, format_price

# ─── Auth gate ──────────────────────────────────────────────
require_auth()

st.set_page_config(
    page_title="Product Management — CDMO Quotation",
    page_icon="📦",
    layout="wide",
)

init_db()
inject_css()
render_sidebar()

# ─── Page header ────────────────────────────────────────────
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
    <div>
        <h2 style="margin:0; color:#1a1a2e;">Product Management</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs: Product List | + New Product ─────────────────────
tab_list, tab_new = st.tabs(["📋 Product List", "➕ New Product"])

with tab_list:
    products = get_all_products()
    if not products:
        st.info("No products yet. Switch to 'New Product' tab to create one.")
    else:
        st.caption(f"Total **{len(products)}** product entries")

        # Build table HTML
        rows_html = ""
        for p in products:
            rows_html += f"""
            <tr style="border-bottom:1px solid #f5f5f5;">
                <td style="padding:10px 14px; font-size:12px; color:#9ca3af;">{p['product_code']}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e; font-weight:500;">{p['product_type']}</td>
                <td style="padding:10px 14px; font-size:13px; color:#6366f1; font-weight:600;">{format_price(p['guide_price'])}</td>
                <td style="padding:10px 14px; font-size:12px; color:#6b7280;">/{p['unit']}</td>
                <td style="padding:10px 14px;">{status_badge(p['status'])}</td>
                <td style="padding:10px 14px; font-size:12px; color:#9ca3af;">{p['created_at']}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; overflow:hidden;">
            <table style="width:100%; border-collapse:collapse;">
                <tr style="background:#f9fafb; border-bottom:1px solid #e5e7eb;">
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Product ID</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Product Type</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Guide Price</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Unit</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Status</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Created</td>
                </tr>
                {rows_html}
            </table>
        </div>
        """, unsafe_allow_html=True)

with tab_new:
    st.markdown("""
    <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; padding:24px; max-width:600px;">
    <h4 style="margin:0 0 16px 0; color:#1a1a2e;">Create New Product</h4>
    """, unsafe_allow_html=True)

    with st.form("new_product_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            product_type = st.text_input("Product Type *", placeholder="e.g. API Process Development")
        with col2:
            guide_price = st.number_input("Guide Price (¥) *", min_value=0.01, value=100000.0, step=10000.0, format="%.0f")
        with col3:
            unit = st.selectbox("Pricing Unit *", options=["project", "batch", "study"])

        submitted = st.form_submit_button("Create Product", type="primary", use_container_width=True)

        if submitted:
            if not product_type.strip():
                st.error("Product Type is required.")
            elif guide_price <= 0:
                st.error("Guide Price must be greater than 0.")
            else:
                new_p = create_product(product_type.strip(), guide_price, unit)
                st.success(f"Product '{new_p['product_code']}' created successfully!")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
```

---

### Task 7: Quotation Management Page — List View

**Files:**
- Create: `pages/2_Quotation_Management.py`

This is the largest file. It handles three sub-views via `st.session_state.view`:
- `"list"` (default): Quotation table
- `"create"`: Create quotation form (basic info + line items in one page)
- `"detail"`: Click a row to see full detail

- [ ] **Step 1: Write 2_Quotation_Management.py — imports, auth, config, sidebar**

```python
"""
CDMO Quotation Platform — Quotation Management Page
List view, Create quotation (Step 1+2 merged), Detail view.
"""

import streamlit as st
from datetime import datetime
from src.database import (
    init_db, get_all_quotations, get_quotation_detail,
    get_active_products, create_quotation,
)
from src.auth import require_auth, get_current_user
from src.components import inject_css, render_sidebar, status_badge, format_price

# ─── Auth gate ──────────────────────────────────────────────
require_auth()

st.set_page_config(
    page_title="Quotation Management — CDMO Quotation",
    page_icon="📋",
    layout="wide",
)

init_db()
inject_css()
render_sidebar()

# ─── Session state initialization ───────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "list"        # list | create | detail
if "detail_quote_id" not in st.session_state:
    st.session_state.detail_quote_id = None
if "line_items" not in st.session_state:
    st.session_state.line_items = []      # [{product_id, product_type, guide_price, unit, quoted_price, quantity}]
```

- [ ] **Step 2: Add list view rendering**

```python
# ═══════════════════════════════════════════════════════════════
# VIEW: LIST
# ═══════════════════════════════════════════════════════════════
if st.session_state.view == "list":
    st.markdown('<h2 style="color:#1a1a2e;">Quotation Management</h2>', unsafe_allow_html=True)

    col_title, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("➕ Create Quotation", type="primary", use_container_width=True):
            st.session_state.view = "create"
            st.session_state.line_items = []
            st.rerun()

    quotations = get_all_quotations()
    with col_title:
        st.caption(f"Total **{len(quotations)}** quotations")

    if not quotations:
        st.info("No quotations yet. Click 'Create Quotation' to get started.")
    else:
        # Build table
        rows_html = ""
        for q in quotations:
            total_display = format_price(q["total_quoted"]) if q["total_quoted"] and q["total_quoted"] > 0 else "—"
            rows_html += f"""
            <tr style="border-bottom:1px solid #f5f5f5; cursor:pointer;"
                onclick="document.getElementById('detail_{q["id"]}').click();">
                <td style="padding:11px 14px; font-size:12px; color:#6366f1; font-weight:500;">{q['quote_no']}</td>
                <td style="padding:11px 14px; font-size:13px; color:#1a1a2e;">{q['customer']}</td>
                <td style="padding:11px 14px; font-size:13px; color:#1a1a2e;">{format_price(q['budget'])}</td>
                <td style="padding:11px 14px; font-size:13px; color:#6366f1; font-weight:600;">{total_display}</td>
                <td style="padding:11px 14px;">{status_badge(q['status'])}</td>
                <td style="padding:11px 14px; font-size:12px; color:#6b7280;">{q['created_by_name']}</td>
                <td style="padding:11px 14px; font-size:12px; color:#9ca3af;">{q['created_at']}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; overflow:hidden;">
            <table style="width:100%; border-collapse:collapse;">
                <tr style="background:#f9fafb; border-bottom:1px solid #e5e7eb;">
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Quote No.</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Client</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Budget</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Total Quoted</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Status</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Prepared By</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Date</td>
                </tr>
                {rows_html}
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Hidden buttons for row click handling
        for q in quotations:
            if st.button(f"View", key=f"detail_{q['id']}", type="secondary"):
                st.session_state.view = "detail"
                st.session_state.detail_quote_id = q["id"]
                st.rerun()
```

- [ ] **Step 3: Add create quotation view**

```python
# ═══════════════════════════════════════════════════════════════
# VIEW: CREATE
# ═══════════════════════════════════════════════════════════════
elif st.session_state.view == "create":
    st.markdown('<h2 style="color:#1a1a2e;">Create Quotation</h2>', unsafe_allow_html=True)
    st.caption("Fill in basic info and add line items below")

    # ── Section 1: Basic Information ──────────────────────────
    st.markdown("""
    <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; padding:20px; margin-bottom:20px;">
    <h4 style="margin:0 0 16px 0; color:#1a1a2e;">Basic Information</h4>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("Client Name *", key="cust_name", placeholder="Enter client company name")
    with col2:
        budget = st.number_input("Budget Amount (¥) *", min_value=0.01, value=1000000.0, step=100000.0, format="%.0f", key="budget_val")

    requirement = st.text_area("Requirement Details *", key="req_detail",
                               placeholder="Describe client requirements, project scope, timeline...",
                               height=80)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section 2: Line Items ─────────────────────────────────
    st.markdown("""
    <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; padding:20px;">
    <h4 style="margin:0 0 16px 0; color:#1a1a2e;">Line Items</h4>
    """, unsafe_allow_html=True)

    # Product selector + Add button
    products = get_active_products()
    product_options = {f"{p['product_type']} — {format_price(p['guide_price'])}/{p['unit']}": p for p in products}

    col_sel, col_add = st.columns([3, 1])
    with col_sel:
        selected = st.selectbox("Add Product", options=list(product_options.keys()),
                                key="product_selector", label_visibility="collapsed")
    with col_add:
        if st.button("➕ Add", type="primary", use_container_width=True):
            p = product_options[selected]
            # Check for duplicate
            existing_codes = [li.get("product_id") for li in st.session_state.line_items]
            if p["id"] not in existing_codes:
                st.session_state.line_items.append({
                    "product_id": p["id"],
                    "product_type": p["product_type"],
                    "product_code": p["product_code"],
                    "guide_price": p["guide_price"],
                    "unit": p["unit"],
                    "quoted_price": p["guide_price"],  # default = guide price
                    "quantity": 1,
                })
                st.rerun()
            else:
                st.warning(f"'{p['product_type']}' is already in the list.")

    st.markdown("<hr style='margin:12px 0; border-color:#f0f0f0;'>", unsafe_allow_html=True)

    # Line items table
    if not st.session_state.line_items:
        st.info("No line items yet. Select a product above and click 'Add'.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.line_items):
            is_project = item["unit"] == "project"

            cols = st.columns([1, 2.5, 1.3, 1.3, 0.8, 1.3, 0.6])
            with cols[0]:
                st.markdown(f"<div style='padding-top:28px; font-size:13px; color:#9ca3af;'>{i+1}</div>",
                            unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<div style='padding-top:28px; font-size:13px; color:#1a1a2e; font-weight:500;'>{item['product_type']}</div>",
                            unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div style='padding-top:28px; font-size:12px; color:#9ca3af;'>{format_price(item['guide_price'])}/{item['unit']}</div>",
                            unsafe_allow_html=True)
            with cols[3]:
                item["quoted_price"] = st.number_input(
                    "Quoted Price", value=float(item["quoted_price"]), min_value=1.0, step=1000.0,
                    key=f"qp_{i}", label_visibility="collapsed")
            with cols[4]:
                if is_project:
                    item["quantity"] = 1
                    st.number_input("Qty", value=1, disabled=True, key=f"qty_{i}", label_visibility="collapsed")
                else:
                    item["quantity"] = st.number_input(
                        "Qty", value=int(item["quantity"]), min_value=1, step=1,
                        key=f"qty_{i}", label_visibility="collapsed")
            with cols[5]:
                line_total = item["quoted_price"] * item["quantity"]
                st.markdown(f"<div style='padding-top:28px; font-size:14px; color:#6366f1; font-weight:700;'>{format_price(line_total)}</div>",
                            unsafe_allow_html=True)
            with cols[6]:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.line_items.pop(i)
                    st.rerun()

            total += item["quoted_price"] * item["quantity"]

        # Total row
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; align-items:center;
                    margin-top:12px; padding:12px 16px; background:#f5f3ff; border-radius:8px;">
            <span style="font-size:13px; color:#6b7280; margin-right:16px;">Quoted Total (by quoted price)</span>
            <span style="font-size:22px; font-weight:800; color:#6366f1;">{format_price(total)}</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Action buttons ───────────────────────────────────
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        col_back, col_draft, col_submit = st.columns([1, 1, 1.5])
        with col_back:
            if st.button("← Cancel", use_container_width=True, type="secondary"):
                st.session_state.view = "list"
                st.session_state.line_items = []
                st.rerun()
        with col_draft:
            if st.button("💾 Save as Draft", use_container_width=True, type="secondary"):
                if not customer or not requirement or budget <= 0:
                    st.error("Please fill in all Basic Information fields before saving.")
                elif len(st.session_state.line_items) == 0:
                    st.error("Please add at least one line item.")
                else:
                    user = get_current_user()
                    items = [{
                        "product_id": li["product_id"],
                        "guide_price": li["guide_price"],
                        "quoted_price": li["quoted_price"],
                        "quantity": li["quantity"],
                    } for li in st.session_state.line_items]
                    create_quotation(customer, requirement, budget, user["id"], items, status="Draft")
                    st.session_state.view = "list"
                    st.session_state.line_items = []
                    st.success("Quotation saved as Draft!")
                    st.rerun()
        with col_submit:
            if st.button("✅ Submit for Review", use_container_width=True, type="primary"):
                if not customer or not requirement or budget <= 0:
                    st.error("Please fill in all Basic Information fields before submitting.")
                elif len(st.session_state.line_items) == 0:
                    st.error("Please add at least one line item.")
                else:
                    user = get_current_user()
                    items = [{
                        "product_id": li["product_id"],
                        "guide_price": li["guide_price"],
                        "quoted_price": li["quoted_price"],
                        "quantity": li["quantity"],
                    } for li in st.session_state.line_items]
                    create_quotation(customer, requirement, budget, user["id"], items, status="Submitted")
                    st.session_state.view = "list"
                    st.session_state.line_items = []
                    st.success("Quotation submitted for review!")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
```

- [ ] **Step 4: Add detail view**

```python
# ═══════════════════════════════════════════════════════════════
# VIEW: DETAIL
# ═══════════════════════════════════════════════════════════════
elif st.session_state.view == "detail" and st.session_state.detail_quote_id:
    q = get_quotation_detail(st.session_state.detail_quote_id)

    if not q:
        st.error("Quotation not found.")
        st.session_state.view = "list"
        st.rerun()

    # Back button
    if st.button("← Back to List", type="secondary"):
        st.session_state.view = "list"
        st.session_state.detail_quote_id = None
        st.rerun()

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin:12px 0 20px 0;">
        <h2 style="margin:0; color:#1a1a2e;">{q['quote_no']}</h2>
        {status_badge(q['status'])}
    </div>
    """, unsafe_allow_html=True)

    # Basic info card
    st.markdown(f"""
    <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; padding:20px; margin-bottom:20px;">
        <div style="font-size:11px; color:#9ca3af; margin-bottom:12px; font-weight:600;">BASIC INFORMATION</div>
        <div style="display:flex; gap:40px; font-size:13px; color:#6b7280; flex-wrap:wrap;">
            <div><span style="color:#9ca3af;">Client:</span> <b style="color:#1a1a2e;">{q['customer']}</b></div>
            <div><span style="color:#9ca3af;">Budget:</span> <b style="color:#1a1a2e;">{format_price(q['budget'])}</b></div>
            <div><span style="color:#9ca3af;">Prepared by:</span> <b style="color:#1a1a2e;">{q['created_by_name']}</b></div>
        </div>
        <div style="margin-top:12px; font-size:13px; color:#6b7280;">
            <span style="color:#9ca3af;">Requirements:</span>
            <span style="color:#1a1a2e;">{q['requirement']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Line items
    if q["items"]:
        rows = ""
        for i, it in enumerate(q["items"]):
            rows += f"""
            <tr style="border-bottom:1px solid #f5f5f5;">
                <td style="padding:10px 14px; font-size:12px; color:#9ca3af;">{i+1}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e; font-weight:500;">{it['product_type']}</td>
                <td style="padding:10px 14px; font-size:12px; color:#9ca3af;">{format_price(it['guide_price'])}/{it['unit']}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e;">{format_price(it['quoted_price'])}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e;">{it['quantity']}</td>
                <td style="padding:10px 14px; font-size:13px; color:#6366f1; font-weight:600;">{format_price(it['quoted_price'] * it['quantity'])}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; overflow:hidden; margin-bottom:20px;">
            <div style="padding:14px 20px; border-bottom:1px solid #e5e7eb; font-size:11px; color:#9ca3af; font-weight:600;">LINE ITEMS</div>
            <table style="width:100%; border-collapse:collapse;">
                <tr style="background:#f9fafb; border-bottom:1px solid #e5e7eb;">
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">#</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Product</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Guide Price</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Quoted Price</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Qty</td>
                    <td style="padding:10px 14px; font-size:11px; color:#6b7280; font-weight:600;">Line Total</td>
                </tr>
                {rows}
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Total
        total = sum(it["quoted_price"] * it["quantity"] for it in q["items"])
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end;">
            <div style="background:#f5f3ff; border-radius:10px; padding:16px 24px; text-align:right;">
                <div style="font-size:11px; color:#9ca3af;">Quoted Total (by quoted price)</div>
                <div style="font-size:24px; font-weight:800; color:#6366f1;">{format_price(total)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
```

---

### Task 8: Integration Test — Verify Full Flow

- [ ] **Step 1: Run database verification**

```bash
cd /Users/lulu/quote-manager && python -c "
from src.database import init_db, get_all_products, get_all_quotations, get_quotation_detail
init_db()
products = get_all_products()
assert len(products) == 10, f'Expected 10 products, got {len(products)}'
quotations = get_all_quotations()
assert len(quotations) == 3, f'Expected 3 quotations, got {len(quotations)}'
q = get_quotation_detail(1)
assert q is not None, 'Quotation 1 detail should exist'
assert len(q['items']) == 4, f'Expected 4 line items, got {len(q[\"items\"])}'
print('✅ All database checks passed!')
print(f'   Products: {len(products)}')
print(f'   Quotations: {len(quotations)}')
print(f'   Q1 line items: {len(q[\"items\"])}')
for it in q['items']:
    print(f'     {it[\"product_type\"]}: {it[\"quoted_price\"]} x {it[\"quantity\"]} = {it[\"line_total\"]}')
"
```

Expected: `✅ All database checks passed!` with listing of 4 line items.

- [ ] **Step 2: Verify Streamlit app starts without errors**

```bash
cd /Users/lulu/quote-manager && timeout 5 streamlit run Home.py --server.headless true 2>&1 | tail -5 || true
```

Expected: No Python traceback errors.

---

### Task 9: Three Mandatory Documents — Product Introduction + Changelog + Technical Design

Per CLAUDE.md Section 2.1, every project must have three core documents.

- [ ] **Step 1: Create 产品介绍.md**

Full product introduction document covering all 10 sections as defined in CLAUDE.md Section 3.

- [ ] **Step 2: Create 产品更新日志.md**

v1.0.0 initial release entry with iteration details.

- [ ] **Step 3: Create docs/designs/产品设计文档.md**

Technical design document covering architecture, data model, algorithm details, error handling, test strategy.

---

### Task 10: QA Agent + Final Commit

- [ ] **Step 1: Run QA Agent L1 (static checks)**

Spawn QA Agent for L1 static analysis.

- [ ] **Step 2: Run QA Agent L2 (functional test)**

Verify key flows: login → product list → create product → quotation list → create quotation → view detail.

- [ ] **Step 3: Run QA Agent L3 (document verification)**

Verify three documents present, spec/plan consistency.

- [ ] **Step 4: Final commit**

```bash
cd /Users/lulu/quote-manager
git add -A
git commit -m "feat: CDMO Quotation Management Platform v1.0.0

- Multi-page Streamlit app with role-based auth
- Product Management: 10 CDMO products with pricing units
- Quotation Management: create (basic info + line items), list, detail
- Pricing logic: project-type locks qty=1, batch/study editable
- Auto-calculated line totals + quotation total by quoted price
- SQLite database with auto-seed on first launch"
```
