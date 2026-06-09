"""
CDMO Quotation Platform — Quotation Management
"""

import streamlit as st
import pandas as pd
from src.database import (
    init_db, get_all_quotations, get_quotation_detail,
    get_active_products, create_quotation,
)
from src.components import inject_css, format_price

st.set_page_config(page_title="Quotation Management", page_icon="📋", layout="wide")
init_db()
inject_css()

# Default user for quotations (no auth)
DEFAULT_USER_ID = 1
DEFAULT_USER_NAME = "sales"

if "view" not in st.session_state:
    st.session_state.view = "list"
if "detail_quote_id" not in st.session_state:
    st.session_state.detail_quote_id = None
if "line_items" not in st.session_state:
    st.session_state.line_items = []

# =====================================================================
# VIEW: LIST
# =====================================================================
if st.session_state.view == "list":
    st.markdown("## 📋 Quotation Management")
    st.caption("View and manage all quotation documents")

    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("➕ Create Quotation", type="primary", use_container_width=True):
            st.session_state.view = "create"
            st.session_state.line_items = []
            st.rerun()

    quotations = get_all_quotations()
    with c1:
        st.caption(f"**{len(quotations)}** quotations")

    if not quotations:
        st.info("No quotations yet. Click 'Create Quotation' to get started.")
    else:
        rows = []
        for q in quotations:
            td = format_price(q["total_quoted"]) if q["total_quoted"] and q["total_quoted"] > 0 else "—"
            rows.append({
                "Quote No.": q["quote_no"],
                "Client": q["customer"],
                "Budget": format_price(q["budget"]),
                "Total Quoted": td,
                "Status": q["status"].capitalize(),
                "Prepared By": q["created_by_name"],
                "Date": q["created_at"],
            })

        df = pd.DataFrame(rows)

        def color_status(val):
            if val == "Submitted":
                return "background-color: #eef2ff; color: #4338ca; font-weight: 500"
            return "background-color: #fef3c7; color: #92400e; font-weight: 500"

        styled = df.style.applymap(color_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=300)

        st.markdown("##### View Details")
        btn_cols = st.columns(min(len(quotations), 5))
        for i, q in enumerate(quotations):
            with btn_cols[i % 5]:
                if st.button(f"📋 {q['quote_no']}", key=f"v_{q['id']}",
                             use_container_width=True, type="secondary"):
                    st.session_state.view = "detail"
                    st.session_state.detail_quote_id = q["id"]
                    st.rerun()

# =====================================================================
# VIEW: CREATE
# =====================================================================
elif st.session_state.view == "create":
    st.markdown("## ➕ Create Quotation")
    st.caption("Step 1: Basic Info  |  Step 2: Line Items")

    st.markdown("#### Basic Information")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.text_input("Client Name *", key="cust_name", placeholder="Enter client company name")
        with c2:
            budget = st.number_input("Budget Amount (¥) *", min_value=0.01, value=1000000.0,
                                     step=100000.0, format="%.0f", key="budget_val")
        requirement = st.text_area("Requirement Details *", key="req_detail",
                                   placeholder="Describe client requirements, project scope, timeline...",
                                   height=80)

    st.markdown("#### Line Items")

    products = get_active_products()
    product_opts = {f"{p['product_type']} — {format_price(p['guide_price'])}/{p['unit']}": p
                     for p in products}

    s1, s2 = st.columns([3, 1])
    with s1:
        selected = st.selectbox("Add a product to this quotation",
                                options=list(product_opts.keys()), key="psel", label_visibility="collapsed")
    with s2:
        if st.button("➕ Add", type="primary", use_container_width=True):
            p = product_opts[selected]
            ids = [li["product_id"] for li in st.session_state.line_items]
            if p["id"] not in ids:
                st.session_state.line_items.append({
                    "product_id": p["id"], "product_type": p["product_type"],
                    "product_code": p["product_code"], "guide_price": p["guide_price"],
                    "unit": p["unit"], "quoted_price": p["guide_price"], "quantity": 1,
                })
                st.rerun()
            else:
                st.warning(f"'{p['product_type']}' is already in the list.")

    if not st.session_state.line_items:
        st.info("No line items yet. Select a product and click Add.")
    else:
        total = 0
        hc = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
        for c, l in zip(hc, ["#", "Product", "Guide Price", "Quoted Price", "Qty", "Line Total", ""]):
            with c:
                st.markdown(f"<div style='font-size:11px;color:#6b7280;font-weight:600'>{l}</div>",
                            unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.line_items):
            is_proj = item["unit"] == "project"
            cols = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
            with cols[0]:
                st.write(f"<span style='color:#9ca3af'>{i+1}</span>", unsafe_allow_html=True)
            with cols[1]:
                st.write(f"<b>{item['product_type']}</b>", unsafe_allow_html=True)
            with cols[2]:
                st.write(f"<span style='color:#6b7280;font-size:12px'>{format_price(item['guide_price'])}/{item['unit']}</span>",
                         unsafe_allow_html=True)
            with cols[3]:
                item["quoted_price"] = st.number_input(
                    "price", value=float(item["quoted_price"]), min_value=1.0, step=1000.0,
                    key=f"qp_{i}", label_visibility="collapsed")
            with cols[4]:
                if is_proj:
                    item["quantity"] = 1
                    st.number_input("qty", value=1, disabled=True, key=f"qt_{i}", label_visibility="collapsed")
                else:
                    item["quantity"] = st.number_input(
                        "qty", value=int(item["quantity"]), min_value=1, step=1,
                        key=f"qt_{i}", label_visibility="collapsed")
            with cols[5]:
                lt = item["quoted_price"] * item["quantity"]
                st.write(f"<span style='color:#4f46e5;font-weight:700;font-size:15px'>{format_price(lt)}</span>",
                         unsafe_allow_html=True)
            with cols[6]:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.line_items.pop(i)
                    st.rerun()
            total += item["quoted_price"] * item["quantity"]

        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;align-items:center;
                    padding:14px 20px;background:#eef2ff;border-radius:10px;margin-top:8px;">
            <span style="font-size:14px;color:#6b7280;margin-right:16px">Quoted Total (by quoted price)</span>
            <span style="font-size:26px;font-weight:800;color:#4f46e5">{format_price(total)}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        bc, bd, bs = st.columns([1, 1, 1.5])
        with bc:
            if st.button("← Cancel", use_container_width=True, type="secondary"):
                st.session_state.view = "list"; st.session_state.line_items = []; st.rerun()
        with bd:
            if st.button("💾 Save as Draft", use_container_width=True, type="secondary"):
                if not customer or not requirement or budget <= 0:
                    st.error("Fill in all Basic Information fields first.")
                elif len(st.session_state.line_items) == 0:
                    st.error("Add at least one line item.")
                else:
                    its = [{"product_id": li["product_id"], "guide_price": li["guide_price"],
                            "quoted_price": li["quoted_price"], "quantity": li["quantity"]}
                           for li in st.session_state.line_items]
                    create_quotation(customer, requirement, budget, DEFAULT_USER_ID, its, "Draft")
                    st.session_state.view = "list"; st.session_state.line_items = []
                    st.success("Saved as Draft!"); st.rerun()
        with bs:
            if st.button("✅ Submit for Review", use_container_width=True, type="primary"):
                if not customer or not requirement or budget <= 0:
                    st.error("Fill in all Basic Information fields first.")
                elif len(st.session_state.line_items) == 0:
                    st.error("Add at least one line item.")
                else:
                    its = [{"product_id": li["product_id"], "guide_price": li["guide_price"],
                            "quoted_price": li["quoted_price"], "quantity": li["quantity"]}
                           for li in st.session_state.line_items]
                    create_quotation(customer, requirement, budget, DEFAULT_USER_ID, its, "Submitted")
                    st.session_state.view = "list"; st.session_state.line_items = []
                    st.success("Submitted for review!"); st.rerun()

# =====================================================================
# VIEW: DETAIL
# =====================================================================
elif st.session_state.view == "detail" and st.session_state.detail_quote_id:
    q = get_quotation_detail(st.session_state.detail_quote_id)
    if not q:
        st.error("Quotation not found.")
        st.session_state.view = "list"; st.rerun()

    if st.button("← Back to List", type="secondary"):
        st.session_state.view = "list"; st.session_state.detail_quote_id = None; st.rerun()

    status_color = "#4338ca" if q["status"] == "Submitted" else "#92400e"
    st.markdown(f"## 📋 {q['quote_no']} &nbsp; <span style='font-size:14px;color:{status_color}'>({q['status']})</span>",
                unsafe_allow_html=True)

    st.markdown("#### Basic Information")
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric("Client", q["customer"])
    with mc2:
        st.metric("Budget", format_price(q["budget"]))
    with mc3:
        st.metric("Prepared by", q["created_by_name"])
    st.write(f"**Requirements:** {q['requirement']}")

    if q["items"]:
        st.markdown("#### Line Items")
        rows = []
        for it in q["items"]:
            rows.append({
                "#": it["id"],
                "Product": it["product_type"],
                "Guide Price": f"{format_price(it['guide_price'])}/{it['unit']}",
                "Quoted Price": format_price(it["quoted_price"]),
                "Qty": it["quantity"],
                "Line Total": format_price(it["quoted_price"] * it["quantity"]),
            })
        dfi = pd.DataFrame(rows)
        st.dataframe(dfi, use_container_width=True, hide_index=True)

        total = sum(it["quoted_price"] * it["quantity"] for it in q["items"])
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <div style="background:#eef2ff;border-radius:10px;padding:16px 24px;text-align:right">
                <div style="font-size:12px;color:#9ca3af">Quoted Total (by quoted price)</div>
                <div style="font-size:28px;font-weight:800;color:#4f46e5">{format_price(total)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No line items.")
