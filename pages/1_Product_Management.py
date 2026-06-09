"""
CDMO Quotation Platform — Product Management Page
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

st.markdown('<h2 style="color:#1a1a2e;">Product Management</h2>', unsafe_allow_html=True)

tab_list, tab_new = st.tabs(["📋 Product List", "➕ New Product"])

with tab_list:
    products = get_all_products()
    if not products:
        st.info("No products yet. Switch to 'New Product' tab to create one.")
    else:
        st.caption(f"Total **{len(products)}** product entries")

        # Build DataFrame for proper Streamlit rendering
        df = pd.DataFrame(products)
        df = df.rename(columns={
            "product_code": "Product ID",
            "product_type": "Product Type",
            "guide_price": "Guide Price",
            "unit": "Unit",
            "status": "Status",
            "created_at": "Created",
        })
        df["Guide Price"] = df["Guide Price"].apply(format_price)
        df["Unit"] = df["Unit"].apply(lambda u: f"/{u}")
        display_cols = ["Product ID", "Product Type", "Guide Price", "Unit", "Status", "Created"]

        # Color-code status
        def highlight_status(val):
            if val == "Active":
                return "background-color: #e0e7ff; color: #4338ca; font-weight: 500; border-radius: 4px;"
            return "background-color: #fef3c7; color: #92400e; font-weight: 500; border-radius: 4px;"

        styled = df[display_cols].style.applymap(highlight_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=400)

with tab_new:
    st.markdown("### Create New Product")
    with st.form("new_product_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            product_type = st.text_input("Product Type *", placeholder="e.g. API Process Development")
        with col2:
            guide_price = st.number_input("Guide Price (¥) *", min_value=0.01, value=100000.0,
                                          step=10000.0, format="%.0f")
        with col3:
            unit = st.selectbox("Pricing Unit *", options=["project", "batch", "study"])

        if st.form_submit_button("Create Product", type="primary", use_container_width=True):
            if not product_type.strip():
                st.error("Product Type is required.")
            elif guide_price <= 0:
                st.error("Guide Price must be greater than 0.")
            else:
                create_product(product_type.strip(), guide_price, unit)
                st.success(f"Product created successfully!")
                st.rerun()
