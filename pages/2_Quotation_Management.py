"""
CDMO Quotation Platform — Quotation Management Page
Three sub-views via session_state: list, create, detail.
"""

import streamlit as st
import pandas as pd
from src.database import (
    init_db, get_all_quotations, get_quotation_detail,
    get_active_products, create_quotation,
)
from src.auth import require_auth, get_current_user
from src.components import inject_css, render_sidebar, status_badge, format_price

require_auth()
st.set_page_config(page_title="Quotation Management", page_icon="📋", layout="wide")
init_db()
inject_css()
render_sidebar()

# ─── Session state ──────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "list"
if "detail_quote_id" not in st.session_state:
    st.session_state.detail_quote_id = None
if "line_items" not in st.session_state:
    st.session_state.line_items = []

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
        # Build DataFrame
        rows = []
        for q in quotations:
            total_display = format_price(q["total_quoted"]) if q["total_quoted"] and q["total_quoted"] > 0 else "—"
            rows.append({
                "Quote No.": q["quote_no"],
                "Client": q["customer"],
                "Budget": format_price(q["budget"]),
                "Total Quoted": total_display,
                "Status": q["status"].capitalize(),
                "Prepared By": q["created_by_name"],
                "Date": q["created_at"],
                "_id": q["id"],
            })

        df = pd.DataFrame(rows)
        display_cols = ["Quote No.", "Client", "Budget", "Total Quoted", "Status", "Prepared By", "Date"]

        def highlight_status(val):
            if val == "Submitted":
                return "background-color: #e0e7ff; color: #4338ca; font-weight: 500;"
            return "background-color: #fef3c7; color: #92400e; font-weight: 500;"

        styled = df[display_cols].style.applymap(highlight_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=350)

        # View buttons below table
        selected_id = None
        cols = st.columns(len(quotations) if len(quotations) <= 5 else 5)
        for i, q in enumerate(quotations):
            with cols[i % 5]:
                if st.button(f"📋 {q['quote_no']}", key=f"detail_{q['id']}", type="secondary", use_container_width=True):
                    st.session_state.view = "detail"
                    st.session_state.detail_quote_id = q["id"]
                    st.rerun()

# ═══════════════════════════════════════════════════════════════
# VIEW: CREATE
# ═══════════════════════════════════════════════════════════════
elif st.session_state.view == "create":
    st.markdown('<h2 style="color:#1a1a2e;">Create Quotation</h2>', unsafe_allow_html=True)
    st.caption("Fill in basic info and add line items below")

    # ── Basic Information ────────────────────────────────────
    st.markdown("### Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("Client Name *", key="cust_name", placeholder="Enter client company name")
    with col2:
        budget = st.number_input("Budget Amount (¥) *", min_value=0.01, value=1000000.0,
                                 step=100000.0, format="%.0f", key="budget_val")
    requirement = st.text_area("Requirement Details *", key="req_detail",
                               placeholder="Describe client requirements, project scope, timeline...", height=80)

    st.markdown("---")

    # ── Line Items ───────────────────────────────────────────
    st.markdown("### Line Items")

    products = get_active_products()
    product_options = {
        f"{p['product_type']} — {format_price(p['guide_price'])}/{p['unit']}": p for p in products
    }

    col_sel, col_add = st.columns([3, 1])
    with col_sel:
        selected = st.selectbox("Add Product", options=list(product_options.keys()),
                                key="product_selector", label_visibility="collapsed")
    with col_add:
        if st.button("➕ Add", type="primary", use_container_width=True):
            p = product_options[selected]
            existing_ids = [li.get("product_id") for li in st.session_state.line_items]
            if p["id"] not in existing_ids:
                st.session_state.line_items.append({
                    "product_id": p["id"],
                    "product_type": p["product_type"],
                    "product_code": p["product_code"],
                    "guide_price": p["guide_price"],
                    "unit": p["unit"],
                    "quoted_price": p["guide_price"],
                    "quantity": 1,
                })
                st.rerun()
            else:
                st.warning(f"'{p['product_type']}' is already in the list.")

    if not st.session_state.line_items:
        st.info("No line items yet. Select a product above and click 'Add'.")
    else:
        total = 0
        # Header row
        hdr_cols = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
        for col, label in zip(hdr_cols, ["#", "Product", "Guide Price", "Quoted Price", "Qty", "Line Total", ""]):
            with col:
                st.markdown(f"<div style='font-size:11px; color:#6b7280; font-weight:600;'>{label}</div>",
                            unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.line_items):
            is_project = item["unit"] == "project"
            cols = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
            with cols[0]:
                st.markdown(f"<div style='padding-top:8px; font-size:13px; color:#9ca3af;'>{i+1}</div>",
                            unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<div style='padding-top:8px; font-size:13px; color:#1a1a2e; font-weight:500;'>{item['product_type']}</div>",
                            unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div style='padding-top:8px; font-size:12px; color:#9ca3af;'>{format_price(item['guide_price'])}/{item['unit']}</div>",
                            unsafe_allow_html=True)
            with cols[3]:
                item["quoted_price"] = st.number_input(
                    "qp", value=float(item["quoted_price"]), min_value=1.0, step=1000.0,
                    key=f"qp_{i}", label_visibility="collapsed")
            with cols[4]:
                if is_project:
                    item["quantity"] = 1
                    st.number_input("qty", value=1, disabled=True, key=f"qty_{i}", label_visibility="collapsed")
                else:
                    item["quantity"] = st.number_input(
                        "qty", value=int(item["quantity"]), min_value=1, step=1,
                        key=f"qty_{i}", label_visibility="collapsed")
            with cols[5]:
                line_total = item["quoted_price"] * item["quantity"]
                st.markdown(f"<div style='padding-top:8px; font-size:14px; color:#6366f1; font-weight:700;'>{format_price(line_total)}</div>",
                            unsafe_allow_html=True)
            with cols[6]:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.line_items.pop(i)
                    st.rerun()
            total += item["quoted_price"] * item["quantity"]

        # Total
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; align-items:center;
                    margin-top:12px; padding:12px 16px; background:#f5f3ff; border-radius:8px;">
            <span style="font-size:14px; color:#6b7280; margin-right:16px;">Quoted Total (by quoted price)</span>
            <span style="font-size:24px; font-weight:800; color:#6366f1;">{format_price(total)}</span>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
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
                    items = [{"product_id": li["product_id"], "guide_price": li["guide_price"],
                              "quoted_price": li["quoted_price"], "quantity": li["quantity"]}
                             for li in st.session_state.line_items]
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
                    items = [{"product_id": li["product_id"], "guide_price": li["guide_price"],
                              "quoted_price": li["quoted_price"], "quantity": li["quantity"]}
                             for li in st.session_state.line_items]
                    create_quotation(customer, requirement, budget, user["id"], items, status="Submitted")
                    st.session_state.view = "list"
                    st.session_state.line_items = []
                    st.success("Quotation submitted for review!")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════
# VIEW: DETAIL
# ═══════════════════════════════════════════════════════════════
elif st.session_state.view == "detail" and st.session_state.detail_quote_id:
    q = get_quotation_detail(st.session_state.detail_quote_id)
    if not q:
        st.error("Quotation not found.")
        st.session_state.view = "list"
        st.rerun()

    if st.button("← Back to List", type="secondary"):
        st.session_state.view = "list"
        st.session_state.detail_quote_id = None
        st.rerun()

    st.markdown(f"## {q['quote_no']}")
    st.caption(f"Status: **{q['status']}**")

    # Basic info
    st.markdown("### Basic Information")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Client", q["customer"])
    with col_b:
        st.metric("Budget", format_price(q["budget"]))
    with col_c:
        st.metric("Prepared by", q["created_by_name"])

    st.markdown(f"**Requirements:** {q['requirement']}")

    # Line items
    if q["items"]:
        st.markdown("### Line Items")
        item_rows = []
        for it in q["items"]:
            item_rows.append({
                "#": it["id"],
                "Product": it["product_type"],
                "Guide Price": f"{format_price(it['guide_price'])}/{it['unit']}",
                "Quoted Price": format_price(it['quoted_price']),
                "Qty": it["quantity"],
                "Line Total": format_price(it["quoted_price"] * it["quantity"]),
            })

        df_items = pd.DataFrame(item_rows)
        st.dataframe(df_items, use_container_width=True, hide_index=True)

        # Total
        total = sum(it["quoted_price"] * it["quantity"] for it in q["items"])
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; margin-top:16px;">
            <div style="background:#f5f3ff; border-radius:10px; padding:16px 24px; text-align:right;">
                <div style="font-size:12px; color:#9ca3af;">Quoted Total (by quoted price)</div>
                <div style="font-size:26px; font-weight:800; color:#6366f1;">{format_price(total)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No line items in this quotation.")
