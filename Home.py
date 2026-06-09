"""
CDMO Quotation Management Platform
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

# ─── Minimal CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #ffffff; }
    input, textarea, .stTextInput input, .stNumberInput input {
        background: #fff !important; color: #111 !important;
        border: 1px solid #d1d5db !important; border-radius: 6px !important;
    }
    .stButton > button {
        background: #4f46e5 !important; color: #fff !important;
        border: none !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    .stDataFrame [data-testid="stTable"] table,
    .stDataFrame [data-testid="stTable"] td { background: #fff !important; color: #111 !important; }
    .stDataFrame [data-testid="stTable"] th { background: #f9fafb !important; color: #374151 !important; }
    .stTextInput label, .stNumberInput label, .stTextArea label {
        font-size: 12px !important; color: #374151 !important; font-weight: 500 !important;
    }
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
if "items" not in st.session_state: st.session_state.items = []
if "show_create" not in st.session_state: st.session_state.show_create = False

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📋 CDMO")
    st.caption("Quotation Platform")
    st.divider()
    page = st.radio("Navigation", ["📦 Product Management", "📋 Quotation Management"],
                    index=0 if st.session_state.nav == "products" else 1,
                    label_visibility="collapsed")
    # Map radio value back to session state
    if "Product" in page:
        st.session_state.nav = "products"
    else:
        st.session_state.nav = "quotations"

# ═══════════════════════════════════════════════════════════════
# PRODUCT MANAGEMENT
# ═══════════════════════════════════════════════════════════════
if st.session_state.nav == "products":
    c1, c2 = st.columns([5, 2])
    with c1:
        st.header("📦 Product Management")
    with c2:
        if st.button("➕ Create Product", use_container_width=True):
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
        st.dataframe(disp.style.applymap(cs, subset=["Status"]),
                     use_container_width=True, hide_index=True, height=420)

# ═══════════════════════════════════════════════════════════════
# QUOTATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════
else:
    if st.session_state.view == "list":
        c1, c2 = st.columns([2, 5])
        with c1:
            if st.button("➕ Create Quotation", use_container_width=True):
                st.session_state.view = "create"
                st.session_state.items = []
                st.rerun()
        with c2:
            st.header("📋 Quotation Management")

        quotes = get_all_quotations()
        st.caption(f"**{len(quotes)}** quotations")

        if not quotes:
            st.info("No quotations yet. Click Create Quotation.")
        else:
            rows = []
            for q in quotes:
                td = fmt(q["total_quoted"]) if q["total_quoted"] and q["total_quoted"] > 0 else "—"
                rows.append({
                    "Quote No.": q["quote_no"], "Client": q["customer"],
                    "Budget": fmt(q["budget"]), "Total Quoted": td,
                    "Status": q["status"].capitalize(),
                    "Prepared By": q["created_by_name"], "Date": q["created_at"],
                })
            df = pd.DataFrame(rows)
            def cs(v):
                if v == "Submitted": return "background:#eef2ff;color:#4338ca;font-weight:500"
                return "background:#fef3c7;color:#92400e;font-weight:500"
            st.dataframe(df.style.applymap(cs, subset=["Status"]),
                         use_container_width=True, hide_index=True, height=350)

            st.caption("View detail:")
            bcs = st.columns(len(quotes))
            for i, q in enumerate(quotes):
                with bcs[i]:
                    if st.button(f"View {q['quote_no']}", key=f"vd_{q['id']}", use_container_width=True):
                        st.session_state.view = "detail"
                        st.session_state.detail_id = q["id"]
                        st.rerun()

    elif st.session_state.view == "create":
        st.header("➕ Create Quotation")

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

        st.subheader("Line Items")
        prods = get_active_products()
        popts = {f"{p['product_type']} — {fmt(p['guide_price'])}/{p['unit']}": p for p in prods}
        s1, s2 = st.columns([3, 1])
        with s1:
            sel = st.selectbox("Select product to add", list(popts.keys()), key="ps", label_visibility="collapsed")
        with s2:
            if st.button("➕ Add", use_container_width=True):
                p = popts[sel]
                ids = [li["product_id"] for li in st.session_state.items]
                if p["id"] not in ids:
                    st.session_state.items.append({
                        "product_id": p["id"], "product_type": p["product_type"],
                        "guide_price": p["guide_price"], "unit": p["unit"],
                        "quoted_price": p["guide_price"], "quantity": 1,
                    }); st.rerun()
                else: st.warning("Already in list.")

        if not st.session_state.items:
            st.info("No line items yet. Select a product and click Add.")
        else:
            total = 0
            hc = st.columns([0.4, 2.2, 1.2, 1.2, 0.7, 1.2, 0.5])
            for c, l in zip(hc, ["#","Product","Guide Price","Quoted Price","Qty","Line Total",""]):
                with c:
                    st.caption(l)

            for i, item in enumerate(st.session_state.items):
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
                        st.session_state.items.pop(i); st.rerun()
                total += item["quoted_price"] * item["quantity"]

            st.info(f"**Quoted Total (by quoted price): {fmt(total)}**")

            bc, bd, bs = st.columns([1, 1, 1.5])
            with bc:
                if st.button("← Cancel", use_container_width=True):
                    st.session_state.view = "list"; st.session_state.items = []; st.rerun()
            with bd:
                if st.button("💾 Save as Draft", use_container_width=True):
                    if not customer or not req or budget <= 0: st.error("Fill all fields.")
                    elif len(st.session_state.items) == 0: st.error("Add at least one line item.")
                    else:
                        its = [{"product_id":li["product_id"],"guide_price":li["guide_price"],
                                "quoted_price":li["quoted_price"],"quantity":li["quantity"]}
                               for li in st.session_state.items]
                        create_quotation(customer, req, budget, 1, its, "Draft")
                        st.session_state.view = "list"; st.session_state.items = []
                        st.success("Saved as Draft!"); st.rerun()
            with bs:
                if st.button("✅ Submit for Review", use_container_width=True):
                    if not customer or not req or budget <= 0: st.error("Fill all fields.")
                    elif len(st.session_state.items) == 0: st.error("Add at least one line item.")
                    else:
                        its = [{"product_id":li["product_id"],"guide_price":li["guide_price"],
                                "quoted_price":li["quoted_price"],"quantity":li["quantity"]}
                               for li in st.session_state.items]
                        create_quotation(customer, req, budget, 1, its, "Submitted")
                        st.session_state.view = "list"; st.session_state.items = []
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
            st.subheader("Line Items")
            ir = [{"#":i+1,"Product":it["product_type"],
                   "Guide Price":f"{fmt(it['guide_price'])}/{it['unit']}",
                   "Quoted Price":fmt(it["quoted_price"]),
                   "Qty":it["quantity"],
                   "Line Total":fmt(it["quoted_price"]*it["quantity"])}
                  for i,it in enumerate(q["items"])]
            st.dataframe(pd.DataFrame(ir), use_container_width=True, hide_index=True)
            tot = sum(it["quoted_price"]*it["quantity"] for it in q["items"])
            st.info(f"**Quoted Total (by quoted price): {fmt(tot)}**")
