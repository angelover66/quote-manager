"""
CDMO Quotation Platform — Quotation Management Page
Three sub-views via session_state: list, create, detail.
Rendered by Home.py navigation — does NOT call set_page_config or require_auth.
"""

import streamlit as st
from src.database import (
    init_db, get_all_quotations, get_quotation_detail,
    get_active_products, create_quotation,
)
from src.auth import get_current_user
from src.components import status_badge, format_price

init_db()

# ─── Session state initialization ───────────────────────────
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

        for q in quotations:
            if st.button("View", key=f"detail_{q['id']}", type="secondary"):
                st.session_state.view = "detail"
                st.session_state.detail_quote_id = q["id"]
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# VIEW: CREATE
# ═══════════════════════════════════════════════════════════════
elif st.session_state.view == "create":
    st.markdown('<h2 style="color:#1a1a2e;">Create Quotation</h2>', unsafe_allow_html=True)
    st.caption("Fill in basic info and add line items below")

    st.markdown("""
    <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; padding:20px; margin-bottom:20px;">
    <h4 style="margin:0 0 16px 0; color:#1a1a2e;">Basic Information</h4>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("Client Name *", key="cust_name", placeholder="Enter client company name")
    with col2:
        budget = st.number_input("Budget Amount (¥) *", min_value=0.01, value=1000000.0,
                                 step=100000.0, format="%.0f", key="budget_val")
    requirement = st.text_area("Requirement Details *", key="req_detail",
                               placeholder="Describe client requirements, project scope, timeline...", height=80)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Section 2: Line Items ─────────────────────────────────
    st.markdown("""
    <div style="background:white; border-radius:10px; border:1px solid #e5e7eb; padding:20px;">
    <h4 style="margin:0 0 16px 0; color:#1a1a2e;">Line Items</h4>
    """, unsafe_allow_html=True)

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

    st.markdown("<hr style='margin:12px 0; border-color:#f0f0f0;'>", unsafe_allow_html=True)

    if not st.session_state.line_items:
        st.info("No line items yet. Select a product above and click 'Add'.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.line_items):
            is_project = item["unit"] == "project"
            cols = st.columns([0.5, 2.5, 1.3, 1.3, 0.8, 1.3, 0.6])
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
                    st.number_input("Qty", value=1, disabled=True,
                                    key=f"qty_{i}", label_visibility="collapsed")
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

        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; align-items:center;
                    margin-top:12px; padding:12px 16px; background:#f5f3ff; border-radius:8px;">
            <span style="font-size:13px; color:#6b7280; margin-right:16px;">Quoted Total (by quoted price)</span>
            <span style="font-size:22px; font-weight:800; color:#6366f1;">{format_price(total)}</span>
        </div>
        """, unsafe_allow_html=True)

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

    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin:12px 0 20px 0;">
        <h2 style="margin:0; color:#1a1a2e;">{q['quote_no']}</h2>
        {status_badge(q['status'])}
    </div>
    """, unsafe_allow_html=True)

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

    if q["items"]:
        rows = ""
        for i, it in enumerate(q["items"]):
            lt = it["quoted_price"] * it["quantity"]
            rows += f"""
            <tr style="border-bottom:1px solid #f5f5f5;">
                <td style="padding:10px 14px; font-size:12px; color:#9ca3af;">{i+1}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e; font-weight:500;">{it['product_type']}</td>
                <td style="padding:10px 14px; font-size:12px; color:#9ca3af;">{format_price(it['guide_price'])}/{it['unit']}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e;">{format_price(it['quoted_price'])}</td>
                <td style="padding:10px 14px; font-size:13px; color:#1a1a2e;">{it['quantity']}</td>
                <td style="padding:10px 14px; font-size:13px; color:#6366f1; font-weight:600;">{format_price(lt)}</td>
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

        total = sum(it["quoted_price"] * it["quantity"] for it in q["items"])
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end;">
            <div style="background:#f5f3ff; border-radius:10px; padding:16px 24px; text-align:right;">
                <div style="font-size:11px; color:#9ca3af;">Quoted Total (by quoted price)</div>
                <div style="font-size:24px; font-weight:800; color:#6366f1;">{format_price(total)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No line items in this quotation.")
