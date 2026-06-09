"""
CDMO Quotation Management Platform
Sidebar navigation + main content area.
"""

import streamlit as st
import pandas as pd
from src.database import (
    init_db, get_all_products, create_product,
    get_all_quotations, get_quotation_detail,
    get_active_products, create_quotation,
)

st.set_page_config(page_title="CDMO Quotation Platform", page_icon="📋", layout="wide")
init_db()

# ─── Global CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #ffffff; }
    p, span, div, label, h1, h2, h3, h4, h5, h6 { color: #111827; }

    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"],
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: #fff !important; color: #111827 !important;
        border: 1px solid #d1d5db !important; border-radius: 8px !important;
    }
    input::placeholder, textarea::placeholder { color: #9ca3af !important; }

    /* Blue primary buttons — blue bg, white text */
    .stButton > button[kind="primary"] {
        background: #4f46e5 !important; border: none !important;
        color: #ffffff !important; border-radius: 8px !important;
        font-weight: 600 !important; font-size: 14px !important;
    }
    .stButton > button[kind="secondary"] {
        background: #fff !important; border: 1px solid #d1d5db !important;
        border-radius: 8px !important; color: #374151 !important;
    }
    /* All buttons: blue bg, white text by default (override Streamlit) */
    .stButton > button {
        color: #ffffff !important;
        background: #4f46e5 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    /* Exception: secondary kind = white bg */
    .stButton > button[kind="secondary"] {
        color: #374151 !important;
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
    }

    .stDataFrame { border: 1px solid #e5e7eb !important; border-radius: 8px !important; }
    .stDataFrame [data-testid="stTable"] table,
    .stDataFrame [data-testid="stTable"] th,
    .stDataFrame [data-testid="stTable"] td {
        background: #fff !important; color: #111827 !important;
    }
    .stDataFrame [data-testid="stTable"] th {
        background: #f9fafb !important; color: #374151 !important; font-weight: 600 !important;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
        font-size: 12px !important; color: #374151 !important; font-weight: 500 !important;
    }
    #MainMenu, footer { visibility: hidden; }
    div[data-testid="stToolbar"], .stDeployButton { display: none; }
    header[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Helper ─────────────────────────────────────────────────
def fmt(amount):
    if amount is None: return "—"
    if isinstance(amount, (int, float)): return f"¥{amount:,.0f}"
    return str(amount)

DEFAULT_USER = 1

# Session state
if "nav" not in st.session_state: st.session_state.nav = "products"
if "view" not in st.session_state: st.session_state.view = "list"
if "detail_id" not in st.session_state: st.session_state.detail_id = None
if "items" not in st.session_state: st.session_state.items = []
if "show_create" not in st.session_state: st.session_state.show_create = False

# ═══════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 8px 0;">
        <div style="font-size:18px;font-weight:800;color:#111827;">📋 CDMO Quotation</div>
        <div style="font-size:11px;color:#9ca3af;margin-top:2px;">Management Platform</div>
    </div>
    <div style="border-bottom:2px solid #f3f4f6;margin-bottom:12px;"></div>
    """, unsafe_allow_html=True)

    # Nav buttons — full width
    if st.button("📦 Product Management", use_container_width=True,
                 type="primary" if st.session_state.nav == "products" else "secondary"):
        st.session_state.nav = "products"
        st.session_state.view = "list"
        st.session_state.show_create = False
        st.rerun()

    if st.button("📋 Quotation Management", use_container_width=True,
                 type="primary" if st.session_state.nav == "quotations" else "secondary"):
        st.session_state.nav = "quotations"
        st.session_state.view = "list"
        st.rerun()

# ═══════════════════════════════════════════════════════════════
# MAIN CONTENT — PRODUCT MANAGEMENT
# ═══════════════════════════════════════════════════════════════
if st.session_state.nav == "products":
    # Header row with title + Create button
    c1, c2 = st.columns([5, 2])
    with c1:
        st.markdown("## 📦 Product Management")
    with c2:
        if st.button("➕ Create Product", use_container_width=True, type="primary"):
            st.session_state.show_create = True
            st.rerun()

    # ── Create Product form (shown when button clicked) ──
    if st.session_state.show_create:
        with st.container(border=True):
            st.markdown("#### Create New Product")
            with st.form("create_product_form", clear_on_submit=True):
                pc1, pc2, pc3 = st.columns([2, 1, 1])
                with pc1:
                    ptype = st.text_input("Product Type *", placeholder="e.g. API Process Development")
                with pc2:
                    price = st.number_input("Guide Price (¥) *", min_value=0.01, value=100000.0,
                                            step=10000.0, format="%.0f")
                with pc3:
                    unit = st.selectbox("Pricing Unit *", ["project", "batch", "study"])
                cf1, cf2 = st.columns([2, 1])
                with cf1:
                    if st.form_submit_button("Create Product", type="primary", use_container_width=True):
                        if not ptype.strip():
                            st.error("Product Type is required.")
                        elif price <= 0:
                            st.error("Guide Price must be > 0.")
                        else:
                            create_product(ptype.strip(), price, unit)
                            st.success(f"Created **{ptype.strip()}**")
                            st.session_state.show_create = False
                            st.rerun()
                with cf2:
                    if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                        st.session_state.show_create = False
                        st.rerun()

    # ── Product list ─────────────────────────────────────
    products = get_all_products()
    st.caption(f"**{len(products)}** products in catalog")

    if not products:
        st.info("No products. Click 'Create Product' to add one.")
    else:
        df = pd.DataFrame(products)
        df["Guide Price"] = df["guide_price"].apply(fmt)
        df["Unit"] = df["unit"].apply(lambda u: f"/{u}")
        disp = df[["product_code", "product_type", "Guide Price", "Unit", "status", "created_at"]]
        disp.columns = ["Product ID", "Product Type", "Guide Price", "Unit", "Status", "Created"]

        def color_status(v):
            if v == "Active": return "background:#eef2ff;color:#4338ca;font-weight:500"
            return "background:#fef3c7;color:#92400e;font-weight:500"
        st.dataframe(disp.style.applymap(color_status, subset=["Status"]),
                     use_container_width=True, hide_index=True, height=420)

# ═══════════════════════════════════════════════════════════════
# MAIN CONTENT — QUOTATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════
elif st.session_state.nav == "quotations":
    # ── LIST VIEW ──────────────────────────────────────────
    if st.session_state.view == "list":
        c1, c2 = st.columns([5, 2])
        with c1:
            st.markdown("## 📋 Quotation Management")
        with c2:
            if st.button("➕ Create Quotation", use_container_width=True, type="primary"):
                st.session_state.view = "create"
                st.session_state.items = []
                st.rerun()

        quotes = get_all_quotations()
        st.caption(f"**{len(quotes)}** quotations")

        if not quotes:
            st.info("No quotations yet. Click 'Create Quotation' to start.")
        else:
            # Build table data — include an "Actions" column with View Detail
            rows = []
            for q in quotes:
                td = fmt(q["total_quoted"]) if q["total_quoted"] and q["total_quoted"] > 0 else "—"
                rows.append({
                    "Quote No.": q["quote_no"],
                    "Client": q["customer"],
                    "Budget": fmt(q["budget"]),
                    "Total Quoted": td,
                    "Status": q["status"].capitalize(),
                    "Prepared By": q["created_by_name"],
                    "Date": q["created_at"],
                    "Actions": f'<a href="#" onclick="return false;" style="color:#4f46e5;font-weight:600;text-decoration:none;">View Detail →</a>',
                    "_id": q["id"],
                })

            df = pd.DataFrame(rows)
            display_cols = ["Quote No.", "Client", "Budget", "Total Quoted", "Status", "Prepared By", "Date", "Actions"]

            def color_status(v):
                if v == "Submitted": return "background:#eef2ff;color:#4338ca;font-weight:500"
                return "background:#fef3c7;color:#92400e;font-weight:500"

            styled = df[display_cols].style.applymap(color_status, subset=["Status"])

            # Render table
            st.dataframe(styled, use_container_width=True, hide_index=True, height=350)

            # View Detail buttons as actual Streamlit buttons below the table
            st.markdown("")
            cols = st.columns(len(quotes))
            for i, q in enumerate(quotes):
                with cols[i]:
                    if st.button(f"View Detail →", key=f"vd_{q['id']}",
                                 use_container_width=True, type="secondary"):
                        st.session_state.view = "detail"
                        st.session_state.detail_id = q["id"]
                        st.rerun()

    # ── CREATE VIEW ───────────────────────────────────────
    elif st.session_state.view == "create":
        st.markdown("## ➕ Create Quotation")

        st.markdown("#### Basic Information")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                customer = st.text_input("Client Name *", key="cn", placeholder="Enter client company name")
            with c2:
                budget = st.number_input("Budget Amount (¥) *", min_value=1.0, value=1000000.0,
                                         step=100000.0, format="%.0f", key="bg")
            req = st.text_area("Requirement Details *", key="rd",
                               placeholder="Describe scope, timeline...", height=80)

        st.markdown("#### Line Items")
        prods = get_active_products()
        popts = {f"{p['product_type']} — {fmt(p['guide_price'])}/{p['unit']}": p for p in prods}
        s1, s2 = st.columns([3, 1])
        with s1:
            sel = st.selectbox("Add product", list(popts.keys()), key="ps", label_visibility="collapsed")
        with s2:
            if st.button("➕ Add", type="primary", use_container_width=True):
                p = popts[sel]
                ids = [li["product_id"] for li in st.session_state.items]
                if p["id"] not in ids:
                    st.session_state.items.append({
                        "product_id": p["id"], "product_type": p["product_type"],
                        "product_code": p["product_code"], "guide_price": p["guide_price"],
                        "unit": p["unit"], "quoted_price": p["guide_price"], "quantity": 1,
                    }); st.rerun()
                else:
                    st.warning(f"Already in list.")

        if not st.session_state.items:
            st.info("No line items yet. Select a product and click Add.")
        else:
            total = 0
            hc = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
            for c, l in zip(hc, ["#", "Product", "Guide Price", "Quoted Price", "Qty", "Line Total", ""]):
                with c:
                    st.markdown(f"<div style='font-size:11px;color:#6b7280;font-weight:600'>{l}</div>",
                                unsafe_allow_html=True)

            for i, item in enumerate(st.session_state.items):
                is_proj = item["unit"] == "project"
                cols = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
                with cols[0]:
                    st.write(f"<span style='color:#9ca3af'>{i+1}</span>", unsafe_allow_html=True)
                with cols[1]:
                    st.write(f"<b style='color:#111827'>{item['product_type']}</b>", unsafe_allow_html=True)
                with cols[2]:
                    st.write(f"<span style='color:#6b7280;font-size:12px'>{fmt(item['guide_price'])}/{item['unit']}</span>",
                             unsafe_allow_html=True)
                with cols[3]:
                    item["quoted_price"] = st.number_input(
                        "p", value=float(item["quoted_price"]), min_value=1.0, step=1000.0,
                        key=f"qp_{i}", label_visibility="collapsed")
                with cols[4]:
                    if is_proj:
                        item["quantity"] = 1
                        st.number_input("q", value=1, disabled=True, key=f"qt_{i}", label_visibility="collapsed")
                    else:
                        item["quantity"] = st.number_input(
                            "q", value=int(item["quantity"]), min_value=1, step=1,
                            key=f"qt_{i}", label_visibility="collapsed")
                with cols[5]:
                    lt = item["quoted_price"] * item["quantity"]
                    st.write(f"<span style='color:#4f46e5;font-weight:700;font-size:15px'>{fmt(lt)}</span>",
                             unsafe_allow_html=True)
                with cols[6]:
                    if st.button("✕", key=f"del_{i}"):
                        st.session_state.items.pop(i); st.rerun()
                total += item["quoted_price"] * item["quantity"]

            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;align-items:center;
                        padding:14px 20px;background:#eef2ff;border-radius:10px;margin-top:8px;">
                <span style="font-size:14px;color:#6b7280;margin-right:16px">Quoted Total (by quoted price)</span>
                <span style="font-size:26px;font-weight:800;color:#4f46e5">{fmt(total)}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")
            bc, bd, bs = st.columns([1, 1, 1.5])
            with bc:
                if st.button("← Cancel", use_container_width=True, type="secondary"):
                    st.session_state.view = "list"; st.session_state.items = []; st.rerun()
            with bd:
                if st.button("💾 Save as Draft", use_container_width=True, type="secondary"):
                    if not customer or not req or budget <= 0:
                        st.error("Fill in all Basic Information fields first.")
                    elif len(st.session_state.items) == 0:
                        st.error("Add at least one line item.")
                    else:
                        its = [{"product_id": li["product_id"], "guide_price": li["guide_price"],
                                "quoted_price": li["quoted_price"], "quantity": li["quantity"]}
                               for li in st.session_state.items]
                        create_quotation(customer, req, budget, DEFAULT_USER, its, "Draft")
                        st.session_state.view = "list"; st.session_state.items = []
                        st.success("Saved as Draft!"); st.rerun()
            with bs:
                if st.button("✅ Submit for Review", use_container_width=True, type="primary"):
                    if not customer or not req or budget <= 0:
                        st.error("Fill in all Basic Information fields first.")
                    elif len(st.session_state.items) == 0:
                        st.error("Add at least one line item.")
                    else:
                        its = [{"product_id": li["product_id"], "guide_price": li["guide_price"],
                                "quoted_price": li["quoted_price"], "quantity": li["quantity"]}
                               for li in st.session_state.items]
                        create_quotation(customer, req, budget, DEFAULT_USER, its, "Submitted")
                        st.session_state.view = "list"; st.session_state.items = []
                        st.success("Submitted!"); st.rerun()

    # ── DETAIL VIEW ───────────────────────────────────────
    elif st.session_state.view == "detail" and st.session_state.detail_id:
        q = get_quotation_detail(st.session_state.detail_id)
        if not q:
            st.error("Not found."); st.session_state.view = "list"; st.rerun()

        if st.button("← Back to List", type="secondary"):
            st.session_state.view = "list"; st.session_state.detail_id = None; st.rerun()

        sc = "#4338ca" if q["status"] == "Submitted" else "#92400e"
        st.markdown(f"## 📋 {q['quote_no']} &nbsp; <span style='font-size:14px;color:{sc}'>({q['status']})</span>",
                    unsafe_allow_html=True)

        st.markdown("#### Basic Information")
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.metric("Client", q["customer"])
        with mc2: st.metric("Budget", fmt(q["budget"]))
        with mc3: st.metric("Prepared by", q["created_by_name"])
        st.write(f"**Requirements:** {q['requirement']}")

        if q["items"]:
            st.markdown("#### Line Items")
            ir = [{
                "#": i + 1,
                "Product": it["product_type"],
                "Guide Price": f"{fmt(it['guide_price'])}/{it['unit']}",
                "Quoted Price": fmt(it["quoted_price"]),
                "Qty": it["quantity"],
                "Line Total": fmt(it["quoted_price"] * it["quantity"]),
            } for i, it in enumerate(q["items"])]
            st.dataframe(pd.DataFrame(ir), use_container_width=True, hide_index=True)

            tot = sum(it["quoted_price"] * it["quantity"] for it in q["items"])
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin-top:12px">
                <div style="background:#eef2ff;border-radius:10px;padding:16px 24px;text-align:right">
                    <div style="font-size:12px;color:#9ca3af">Quoted Total (by quoted price)</div>
                    <div style="font-size:28px;font-weight:800;color:#4f46e5">{fmt(tot)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No line items.")
