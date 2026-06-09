"""
CDMO Quotation Platform — Product Management
"""

import streamlit as st
import pandas as pd
from src.database import init_db, get_all_products, create_product
from src.auth import require_auth
from src.components import inject_css, render_sidebar, format_price

require_auth()
st.set_page_config(page_title="Product Management", page_icon="📦", layout="wide")
init_db()
inject_css()
render_sidebar()

# ─── Page Header ────────────────────────────────────────────
st.markdown("## 📦 Product Management")
st.caption("Manage CDMO product catalog and guide prices")

# ─── Tabs ───────────────────────────────────────────────────
tab_list, tab_new = st.tabs(["Product List", "New Product"])

with tab_list:
    products = get_all_products()
    if not products:
        st.info("No products yet. Switch to 'New Product' tab to create one.")
    else:
        st.caption(f"**{len(products)}** products in catalog")

        df = pd.DataFrame(products)
        df["Guide Price"] = df["guide_price"].apply(format_price)
        df["Unit"] = df["unit"].apply(lambda u: f"/{u}")
        df["Status"] = df["status"]
        df["Created"] = df["created_at"]

        df_display = df[["product_code", "product_type", "Guide Price", "Unit", "Status", "Created"]]
        df_display.columns = ["Product ID", "Product Type", "Guide Price", "Unit", "Status", "Created"]

        def color_status(val):
            if val == "Active":
                return "background-color: #eef2ff; color: #4338ca; font-weight: 500"
            return "background-color: #fef3c7; color: #92400e; font-weight: 500"

        styled = df_display.style.applymap(color_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=420)

with tab_new:
    st.markdown("#### Create New Product")
    with st.container(border=True):
        with st.form("new_product_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                product_type = st.text_input("Product Type *", placeholder="e.g. API Process Development")
            with c2:
                guide_price = st.number_input("Guide Price (¥) *", min_value=0.01, value=100000.0,
                                              step=10000.0, format="%.0f")
            with c3:
                unit = st.selectbox("Pricing Unit *", options=["project", "batch", "study"])

            if st.form_submit_button("Create Product", type="primary", use_container_width=True):
                if not product_type.strip():
                    st.error("Product Type is required.")
                elif guide_price <= 0:
                    st.error("Guide Price must be greater than 0.")
                else:
                    new_p = create_product(product_type.strip(), guide_price, unit)
                    st.success(f"Created **{new_p['product_code']}** — {product_type.strip()}")
                    st.rerun()
