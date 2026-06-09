"""
CDMO Quotation Platform — Database Layer
SQLite connection, schema creation, seed data, CRUD operations.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

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
    """Insert 10 CDMO products with real pharmaceutical CDMO pricing."""
    products = [
        # 8 core CDMO products
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
    """Insert 3 sample quotations with line items for demonstration."""
    # Quotation 1: Submitted — PharmaBio Therapeutics
    conn.execute(
        """INSERT INTO quotations (quote_no, customer, requirement, budget, total_quoted, status, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("Q20260609-001", "PharmaBio Therapeutics",
         "End-to-end CDMO services for Phase II oncology candidate — API process dev, 3-batch GMP mfg, formulation dev, stability study, CTD Module 3 for IND.",
         5000000, 4350000, "Submitted", 1),
    )
    q1_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Quotation 2: Submitted — NovoGen Biopharma
    conn.execute(
        """INSERT INTO quotations (quote_no, customer, requirement, budget, total_quoted, status, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("Q20260608-002", "NovoGen Biopharma",
         "API GMP manufacturing support for Phase III — 5 batches API, release testing, stability study for registration.",
         3000000, 2780000, "Submitted", 1),
    )
    q2_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Quotation 3: Draft — GenTech Pharmaceuticals
    conn.execute(
        """INSERT INTO quotations (quote_no, customer, requirement, budget, status, created_by)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("Q20260607-003", "GenTech Pharmaceuticals",
         "Early-phase analytical method development and formulation screening for small molecule candidate.",
         2000000, "Draft", 1),
    )

    # Line items for Q1 (4 items)
    items_q1 = [
        (q1_id, 1, 1200000, 1150000, 1),   # API Process Dev
        (q1_id, 2, 800000, 750000, 3),       # API GMP Mfg × 3 batches
        (q1_id, 3, 900000, 850000, 1),        # Formulation Dev
        (q1_id, 6, 200000, 100000, 1),        # Stability Study
    ]
    conn.executemany(
        "INSERT INTO quotation_items (quotation_id, product_id, guide_price, quoted_price, quantity) "
        "VALUES (?, ?, ?, ?, ?)",
        items_q1,
    )

    # Line items for Q2 (3 items)
    items_q2 = [
        (q2_id, 2, 800000, 780000, 5),        # API GMP Mfg × 5 batches
        (q2_id, 7, 50000, 48000, 5),            # Release Testing × 5
        (q2_id, 6, 200000, 180000, 1),           # Stability Study
    ]
    conn.executemany(
        "INSERT INTO quotation_items (quotation_id, product_id, guide_price, quoted_price, quantity) "
        "VALUES (?, ?, ?, ?, ?)",
        items_q2,
    )

    conn.commit()


# ═══════════════════════════════════════════════════════════════
# CRUD Helpers
# ═══════════════════════════════════════════════════════════════

def get_all_products() -> list:
    """Return all products ordered by product_code."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products ORDER BY product_code"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_products() -> list:
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


def get_all_quotations() -> list:
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


def get_quotation_detail(quote_id: int) -> Optional[dict]:
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
                     created_by: int, items: list, status: str = "Draft") -> dict:
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

    # Calculate total_quoted from line items
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


def verify_user(username: str, password: str) -> Optional[dict]:
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
