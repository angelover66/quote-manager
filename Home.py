"""
Quotation Management Platform
"""

import streamlit as st
import pandas as pd
from src.database import (
    init_db, get_all_products, create_product,
    get_all_quotations, get_quotation_detail,
    get_active_products, create_quotation, update_quotation,
)

st.set_page_config(page_title="Quotation Platform", page_icon="📋", layout="wide")
init_db()

# ─── CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #ffffff; }
    input, textarea, .stTextInput input, .stNumberInput input {
        background: #fff !important; color: #111 !important;
        border: 1px solid #d1d5db !important; border-radius: 6px !important;
    }
    .stButton > button {
        background: #4f46e5 !important; color: #fff !important;
        border: none !important; border-radius: 6px !important;
        font-weight: 500 !important; font-size: 13px !important;
        padding: 4px 14px !important;
    }
    /* Table borders */
    .stDataFrame [data-testid="stTable"] {
        border: 1px solid #d1d5db !important;
    }
    .stDataFrame [data-testid="stTable"] table,
    .stDataFrame [data-testid="stTable"] td {
        background: #fff !important; color: #111 !important;
    }
    .stDataFrame [data-testid="stTable"] td {
        border-bottom: 1px solid #d1d5db !important;
    }
    .stDataFrame [data-testid="stTable"] th {
        background: #f9fafb !important; color: #374151 !important;
        border-bottom: 2px solid #d1d5db !important;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label {
        font-size: 12px !important; color: #374151 !important; font-weight: 500 !important;
    }
    /* Keep sidebar radio on one line */
    [data-testid="stSidebar"] label { white-space: nowrap !important; font-size: 14px !important; }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Helper ─────────────────────────────────────────────────
def fmt(amount):
    if amount is None: return "—"
    if isinstance(amount, (int, float)): return f"¥{amount:,.0f}"
    return str(amount)

# ─── Session state ──────────────────────────────────────────
if "nav" not in st.session_state: st.session_state.nav = "products"
if "view" not in st.session_state: st.session_state.view = "list"
if "detail_id" not in st.session_state: st.session_state.detail_id = None
if "editing_id" not in st.session_state: st.session_state.editing_id = None
if "line_items" not in st.session_state: st.session_state.line_items = []
if "show_create" not in st.session_state: st.session_state.show_create = False

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-size:20px;font-weight:700;color:#111827;padding:4px 0;">
        📋 Quotation Platform
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigation", ["📦 Products", "📋 Quotations"],
                    index=0 if st.session_state.nav == "products" else 1,
                    label_visibility="collapsed")
    if "Products" in page:
        st.session_state.nav = "products"
    else:
        st.session_state.nav = "quotations"

# ═══════════════════════════════════════════════════════════════
# PRODUCT MANAGEMENT
# ═══════════════════════════════════════════════════════════════
if st.session_state.nav == "products":
    c1, c2 = st.columns([5, 1.5])
    with c1:
        st.header("📦 Product Management")
    with c2:
        st.write("")  # spacer
        if st.button("Create Product", use_container_width=True):
            st.session_state.show_create = True
            st.rerun()

    if st.session_state.show_create:
        with st.container(border=True):
            st.subheader("Create New Product")
            with st.form("create_product_form", clear_on_submit=True):
                pc1, pc2, pc3 = st.columns([2, 1, 1])
                with pc1:
                    ptype = st.text_input("Product Type *", placeholder="e.g. API Process Development")
                with pc2:
                    price = st.number_input("Guide Price (¥) *", min_value=1.0, value=100000.0,
                                            step=10000.0, format="%.0f")
                with pc3:
                    unit = st.selectbox("Pricing Unit *", ["project", "batch", "study"])
                cf1, cf2 = st.columns(2)
                with cf1:
                    sub = st.form_submit_button("Create", type="primary", use_container_width=True)
                with cf2:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                if sub:
                    if not ptype.strip(): st.error("Product Type required.")
                    elif price <= 0: st.error("Price must be > 0.")
                    else:
                        create_product(ptype.strip(), price, unit)
                        st.success(f"Created {ptype.strip()}")
                        st.session_state.show_create = False
                        st.rerun()
                if cancel:
                    st.session_state.show_create = False
                    st.rerun()

    products = get_all_products()
    st.caption(f"**{len(products)}** products in catalog")
    if products:
        df = pd.DataFrame(products)
        df["Guide Price"] = df["guide_price"].apply(fmt)
        df["Unit"] = df["unit"].apply(lambda u: f"/{u}")
        disp = df[["product_code","product_type","Guide Price","Unit","status","created_at"]]
        disp.columns = ["Product ID","Product Type","Guide Price","Unit","Status","Created"]
        def cs(v):
            if v == "Active": return "background:#eef2ff;color:#4338ca;font-weight:500"
            return "background:#fef3c7;color:#92400e;font-weight:500"
        st.dataframe(disp.style.map(cs, subset=["Status"]),
                     width="stretch", hide_index=True, height=420)

# ═══════════════════════════════════════════════════════════════
# QUOTATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════
else:
    # Handle query param navigation (View/Edit text links in table)
    qp = st.query_params
    if "action" in qp and "id" in qp:
        qid = int(qp["id"])
        if qp["action"] == "edit":
            # Load existing quotation data into edit form
            eq = get_quotation_detail(qid)
            if eq:
                st.session_state.editing_id = qid
                st.session_state.line_items = [{
                    "product_id": it["product_id"],
                    "product_type": it["product_type"],
                    "product_code": it["product_code"],
                    "guide_price": it["guide_price"],
                    "unit": it["unit"],
                    "quoted_price": it["quoted_price"],
                    "quantity": it["quantity"],
                } for it in eq["items"]]
                # Store basic info for form pre-fill
                st.session_state.edit_customer = eq["customer"]
                st.session_state.edit_budget = eq["budget"]
                st.session_state.edit_requirement = eq["requirement"]
                st.session_state.view = "edit"
        else:
            st.session_state.view = "detail"
            st.session_state.detail_id = qid
        st.query_params.clear()
        st.rerun()

    if st.session_state.view == "list":
        c1, c2 = st.columns([5, 1.5])
        with c1:
            st.header("📋 Quotation Management")
        with c2:
            st.write("")  # spacer
            if st.button("Create Quotation", use_container_width=True):
                st.session_state.view = "create"
                st.session_state.line_items = []
                st.rerun()

        quotes = get_all_quotations()
        st.caption(f"**{len(quotes)}** quotations")

        if not quotes:
            st.info("No quotations yet. Click Create Quotation.")
        else:
            # Build HTML table as single string for st.html()
            rows_html = ""
            for q in quotes:
                td = fmt(q["total_quoted"]) if q["total_quoted"] and q["total_quoted"] > 0 else "—"
                sc = "#4338ca" if q["status"] == "Submitted" else "#92400e"
                rows_html += '<tr style="border-bottom:1px solid #d1d5db;">'
                rows_html += f'<td style="padding:10px 14px;font-size:13px;color:#4f46e5;font-weight:500">{q["quote_no"]}</td>'
                rows_html += f'<td style="padding:10px 14px;font-size:13px;color:#111827">{q["customer"]}</td>'
                rows_html += f'<td style="padding:10px 14px;font-size:13px;color:#111827">{fmt(q["budget"])}</td>'
                rows_html += f'<td style="padding:10px 14px;font-size:13px;color:#111827;font-weight:600">{td}</td>'
                rows_html += f'<td style="padding:10px 14px;font-size:12px;color:{sc};font-weight:500">{q["status"].capitalize()}</td>'
                rows_html += f'<td style="padding:10px 14px;font-size:12px;color:#6b7280">{q["created_by_name"]}</td>'
                rows_html += f'<td style="padding:10px 14px;font-size:12px;color:#9ca3af">{q["created_at"]}</td>'
                rows_html += '<td style="padding:10px 14px;font-size:13px">'
                rows_html += f'<a href="?action=view&id={q["id"]}" style="color:#4f46e5;text-decoration:none">View</a>'
                rows_html += '</td></tr>'

            table_html = '<div style="border:1px solid #d1d5db;border-radius:8px;overflow:hidden;">'
            table_html += '<table style="width:100%;border-collapse:collapse;">'
            table_html += '<thead><tr style="background:#f9fafb;border-bottom:2px solid #d1d5db;">'
            for col in ["Quote No.","Client","Budget","Total Quoted","Status","Prepared By","Date","Actions"]:
                table_html += f'<th style="padding:10px 14px;font-size:11px;color:#6b7280;font-weight:600;text-align:left">{col}</th>'
            table_html += '</tr></thead><tbody>'
            table_html += rows_html
            table_html += '</tbody></table></div>'

            st.html(table_html)


    elif st.session_state.view == "create":
        st.header("Create Quotation")

        st.subheader("Basic Information")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                customer = st.text_input("Client Name *", key="cn", placeholder="Enter client company name")
            with c2:
                budget = st.number_input("Budget Amount (¥) *", min_value=1.0, value=1000000.0,
                                         step=100000.0, format="%.0f", key="bg")
            req = st.text_area("Requirement Details *", key="rd",
                               placeholder="Describe scope, timeline...", height=80)

        st.subheader("Products Detail")
        prods = get_active_products()
        popts = {f"{p['product_type']} — {fmt(p['guide_price'])}/{p['unit']}": p for p in prods}
        s1, s2 = st.columns([3, 1])
        with s1:
            sel = st.selectbox("Select product to add", list(popts.keys()), key="ps", label_visibility="collapsed")
        with s2:
            if st.button("Add", key="add_create", use_container_width=True):
                p = popts[sel]
                ids = [li["product_id"] for li in st.session_state.line_items]
                if p["id"] not in ids:
                    st.session_state.line_items.append({
                        "product_id": p["id"], "product_type": p["product_type"],
                        "guide_price": p["guide_price"], "unit": p["unit"],
                        "quoted_price": p["guide_price"], "quantity": 1,
                    }); st.rerun()
                else: st.warning("Already in list.")

        if not st.session_state.line_items:
            st.info("No products yet. Select a product and click Add.")
        else:
            total = 0
            hc = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
            for c, l in zip(hc, ["#","Product","Guide Price","Quoted Price","Qty","Line Total",""]):
                with c:
                    st.markdown(f"<div style='font-size:11px;color:#6b7280;font-weight:600'>{l}</div>",
                                unsafe_allow_html=True)

            for i, item in enumerate(st.session_state.line_items):
                is_proj = item["unit"] == "project"
                cols = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
                with cols[0]: st.write(str(i+1))
                with cols[1]: st.write(f"**{item['product_type']}**")
                with cols[2]: st.write(f"{fmt(item['guide_price'])}/{item['unit']}")
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
                    st.write(f":blue[**{fmt(lt)}**]")
                with cols[6]:
                    if st.button("✕", key=f"del_{i}"):
                        st.session_state.line_items.pop(i); st.rerun()
                total += item["quoted_price"] * item["quantity"]

            st.info(f"**Quoted Total (by quoted price): {fmt(total)}**")

            bc, bd, bs = st.columns([1, 1, 1.5])
            with bc:
                if st.button("← Cancel", key="cancel_create", use_container_width=True):
                    st.session_state.view = "list"; st.session_state.line_items = []; st.rerun()
            with bd:
                if st.button("💾 Save as Draft", key="draft_create", use_container_width=True):
                    if not customer or not req or budget <= 0: st.error("Fill all fields.")
                    elif len(st.session_state.line_items) == 0: st.error("Add at least one line item.")
                    else:
                        its = [{"product_id":li["product_id"],"guide_price":li["guide_price"],
                                "quoted_price":li["quoted_price"],"quantity":li["quantity"]}
                               for li in st.session_state.line_items]
                        create_quotation(customer, req, budget, 1, its, "Draft")
                        st.session_state.view = "list"; st.session_state.line_items = []
                        st.success("Saved as Draft!"); st.rerun()
            with bs:
                if st.button("✅ Submit for Review", key="submit_create", use_container_width=True):
                    if not customer or not req or budget <= 0: st.error("Fill all fields.")
                    elif len(st.session_state.line_items) == 0: st.error("Add at least one line item.")
                    else:
                        its = [{"product_id":li["product_id"],"guide_price":li["guide_price"],
                                "quoted_price":li["quoted_price"],"quantity":li["quantity"]}
                               for li in st.session_state.line_items]
                        create_quotation(customer, req, budget, 1, its, "Submitted")
                        st.session_state.view = "list"; st.session_state.line_items = []
                        st.success("Submitted!"); st.rerun()

    elif st.session_state.view == "edit" and st.session_state.editing_id:
        st.header("Edit Quotation")

        # Pre-fill from stored edit data
        st.subheader("Basic Information")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                customer = st.text_input("Client Name *", key="ecn",
                                         value=st.session_state.get("edit_customer", ""))
            with c2:
                budget = st.number_input("Budget Amount (¥) *", min_value=1.0,
                                         value=float(st.session_state.get("edit_budget", 1000000)),
                                         step=100000.0, format="%.0f", key="ebg")
            req = st.text_area("Requirement Details *", key="erd",
                               value=st.session_state.get("edit_requirement", ""), height=80)

        st.subheader("Products Detail")
        prods = get_active_products()
        popts = {f"{p['product_type']} — {fmt(p['guide_price'])}/{p['unit']}": p for p in prods}
        s1, s2 = st.columns([3, 1])
        with s1:
            sel = st.selectbox("Add product", list(popts.keys()), key="eps", label_visibility="collapsed")
        with s2:
            if st.button("Add", key="eadd", use_container_width=True):
                p = popts[sel]
                ids = [li["product_id"] for li in st.session_state.line_items]
                if p["id"] not in ids:
                    st.session_state.line_items.append({
                        "product_id": p["id"], "product_type": p["product_type"],
                        "guide_price": p["guide_price"], "unit": p["unit"],
                        "quoted_price": p["guide_price"], "quantity": 1,
                    }); st.rerun()
                else: st.warning("Already in list.")

        if not st.session_state.line_items:
            st.info("No line items.")
        else:
            total = 0
            hc = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
            for c, l in zip(hc, ["#","Product","Guide Price","Quoted Price","Qty","Line Total",""]):
                with c:
                    st.markdown(f"<div style='font-size:11px;color:#6b7280;font-weight:600'>{l}</div>",
                                unsafe_allow_html=True)
            for i, item in enumerate(st.session_state.line_items):
                is_proj = item["unit"] == "project"
                cols = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
                with cols[0]: st.write(str(i+1))
                with cols[1]: st.write(f"**{item['product_type']}**")
                with cols[2]: st.write(f"{fmt(item['guide_price'])}/{item['unit']}")
                with cols[3]:
                    item["quoted_price"] = st.number_input(
                        "p", value=float(item["quoted_price"]), min_value=1.0, step=1000.0,
                        key=f"eqp_{i}", label_visibility="collapsed")
                with cols[4]:
                    if is_proj:
                        item["quantity"] = 1
                        st.number_input("q", value=1, disabled=True, key=f"eqt_{i}", label_visibility="collapsed")
                    else:
                        item["quantity"] = st.number_input(
                            "q", value=int(item["quantity"]), min_value=1, step=1,
                            key=f"eqt_{i}", label_visibility="collapsed")
                with cols[5]:
                    lt = item["quoted_price"] * item["quantity"]
                    st.write(f":blue[**{fmt(lt)}**]")
                with cols[6]:
                    if st.button("✕", key=f"edel_{i}"):
                        st.session_state.line_items.pop(i); st.rerun()
                total += item["quoted_price"] * item["quantity"]

            st.info(f"**Quoted Total: {fmt(total)}**")

            bc, bd, bs = st.columns([1, 1, 1.5])
            with bc:
                if st.button("← Cancel", key="ecancel", width="stretch"):
                    st.session_state.view = "list"; st.session_state.line_items = []
                    st.session_state.editing_id = None; st.rerun()
            with bd:
                if st.button("💾 Save as Draft", key="esave", width="stretch"):
                    if not customer or not req or budget <= 0: st.error("Fill all fields.")
                    elif len(st.session_state.line_items) == 0: st.error("Add at least one line item.")
                    else:
                        its = [{"product_id":li["product_id"],"guide_price":li["guide_price"],
                                "quoted_price":li["quoted_price"],"quantity":li["quantity"]}
                               for li in st.session_state.line_items]
                        update_quotation(st.session_state.editing_id, customer, req, budget, its, "Draft")
                        st.session_state.view = "list"; st.session_state.line_items = []
                        st.session_state.editing_id = None
                        st.success("Updated!"); st.rerun()
            with bs:
                if st.button("✅ Submit for Review", key="esubmit", width="stretch"):
                    if not customer or not req or budget <= 0: st.error("Fill all fields.")
                    elif len(st.session_state.line_items) == 0: st.error("Add at least one line item.")
                    else:
                        its = [{"product_id":li["product_id"],"guide_price":li["guide_price"],
                                "quoted_price":li["quoted_price"],"quantity":li["quantity"]}
                               for li in st.session_state.line_items]
                        update_quotation(st.session_state.editing_id, customer, req, budget, its, "Submitted")
                        st.session_state.view = "list"; st.session_state.line_items = []
                        st.session_state.editing_id = None
                        st.success("Submitted!"); st.rerun()

    elif st.session_state.view == "detail" and st.session_state.detail_id:
        q = get_quotation_detail(st.session_state.detail_id)
        if not q: st.error("Not found."); st.session_state.view = "list"; st.rerun()

        if st.button("← Back to List"):
            st.session_state.view = "list"; st.session_state.detail_id = None; st.rerun()

        sc = "#4338ca" if q["status"] == "Submitted" else "#92400e"
        st.header(f"📋 {q['quote_no']}")
        st.caption(f"Status: {q['status']}")

        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.metric("Client", q["customer"])
        with mc2: st.metric("Budget", fmt(q["budget"]))
        with mc3: st.metric("Prepared by", q["created_by_name"])
        st.write(f"**Requirements:** {q['requirement']}")

        if q["items"]:
            st.subheader("Products Detail")
            ir = [{"#":i+1,"Product":it["product_type"],
                   "Guide Price":f"{fmt(it['guide_price'])}/{it['unit']}",
                   "Quoted Price":fmt(it["quoted_price"]),
                   "Qty":it["quantity"],
                   "Line Total":fmt(it["quoted_price"]*it["quantity"])}
                  for i,it in enumerate(q["items"])]
            st.dataframe(pd.DataFrame(ir), width="stretch", hide_index=True)
            tot = sum(it["quoted_price"]*it["quantity"] for it in q["items"])
            st.info(f"**Quoted Total (by quoted price): {fmt(tot)}**")
