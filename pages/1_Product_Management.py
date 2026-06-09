"""
CDMO Quotation Platform — Product Management Page
Display all products in a table, create new product with auto-generated code.
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
st.markdown('<h2 style="color:#1a1a2e;">Product Management</h2>', unsafe_allow_html=True)

# ─── Tabs: Product List | + New Product ─────────────────────
tab_list, tab_new = st.tabs(["📋 Product List", "➕ New Product"])

with tab_list:
    products = get_all_products()
    if not products:
        st.info("No products yet. Switch to 'New Product' tab to create one.")
    else:
        st.caption(f"Total **{len(products)}** product entries")

        # Build table as HTML for clean styling
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
            guide_price = st.number_input("Guide Price (¥) *", min_value=0.01, value=100000.0,
                                          step=10000.0, format="%.0f")
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
