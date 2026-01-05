"""
Vendor Management Page - Procure-Pro-ISO
Supplier directory with performance ratings
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import sys
sys.path.append('..')
from data.sample_data import get_vendor_data

st.set_page_config(page_title="Vendor Management | Procure-Pro-ISO", page_icon="👥", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">👥 Vendor Management</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Supplier directory & performance tracking</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'vendor_df' not in st.session_state:
    st.session_state.vendor_df = get_vendor_data()

vendor_df = st.session_state.vendor_df

# Quick Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Vendors", len(vendor_df))
with col2:
    st.metric("Approved", len(vendor_df[vendor_df['Status'] == 'Approved']))
with col3:
    avg_rating = vendor_df[vendor_df['Rating'] > 0]['Rating'].mean()
    st.metric("Avg Rating", f"{avg_rating:.1f} / 5.0")
with col4:
    total_value = vendor_df['Total Value'].sum()
    st.metric("Total Order Value", f"${total_value/1000000:.1f}M")

st.markdown("---")

# Performance Chart
st.subheader("📊 Vendor Performance Overview")

# Filter out vendors with no data
perf_df = vendor_df[vendor_df['On-Time Delivery %'] > 0].copy()

fig = go.Figure()

fig.add_trace(go.Bar(
    name='On-Time Delivery %',
    x=perf_df['Company Name'],
    y=perf_df['On-Time Delivery %'],
    marker_color='#3b82f6'
))

fig.add_trace(go.Bar(
    name='Quality Score %',
    x=perf_df['Company Name'],
    y=perf_df['Quality Score %'],
    marker_color='#22c55e'
))

fig.update_layout(
    barmode='group',
    height=400,
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis_title="Percentage (%)",
    yaxis=dict(range=[0, 105])
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("🔍 Search Vendors", placeholder="Search by name, code...")

with col2:
    status_filter = st.selectbox("Status", ['All', 'Approved', 'Pending', 'Blacklisted'])

with col3:
    category_filter = st.selectbox("Category", ['All'] + list(vendor_df['Category'].unique()))

# Apply filters
filtered_df = vendor_df.copy()

if search:
    mask = (
        filtered_df['Company Name'].str.contains(search, case=False, na=False) |
        filtered_df['Vendor Code'].str.contains(search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if status_filter != 'All':
    filtered_df = filtered_df[filtered_df['Status'] == status_filter]

if category_filter != 'All':
    filtered_df = filtered_df[filtered_df['Category'] == category_filter]

# Vendor Table with Star Ratings
st.subheader(f"📋 Vendor Directory ({len(filtered_df)} vendors)")

# Create star rating display
def create_stars(rating):
    if rating == 0:
        return "N/A"
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return "⭐" * full_stars + "✨" * half_star + "☆" * empty_stars + f" ({rating:.1f})"

display_df = filtered_df.copy()
display_df['Rating Display'] = display_df['Rating'].apply(create_stars)
display_df['Total Value'] = display_df['Total Value'].apply(lambda x: f"${x:,.0f}" if x > 0 else "N/A")
display_df['On-Time %'] = display_df['On-Time Delivery %'].apply(lambda x: f"{x}%" if x > 0 else "N/A")
display_df['Quality %'] = display_df['Quality Score %'].apply(lambda x: f"{x}%" if x > 0 else "N/A")

st.dataframe(
    display_df[['Vendor Code', 'Company Name', 'Country', 'Category', 'Rating Display', 'Status', 'Total Orders', 'On-Time %', 'Quality %']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Vendor Code": st.column_config.TextColumn("Code", width="small"),
        "Rating Display": st.column_config.TextColumn("Rating", width="medium"),
        "Status": st.column_config.TextColumn("Status", width="small"),
    }
)

# Vendor Detail View
st.markdown("---")
st.subheader("🔍 Vendor Details")

selected_vendor = st.selectbox("Select Vendor", vendor_df['Company Name'].tolist())

if selected_vendor:
    vendor = vendor_df[vendor_df['Company Name'] == selected_vendor].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Contact Information**")
        st.write(f"📧 {vendor['Email']}")
        st.write(f"👤 {vendor['Contact Person']}")
        st.write(f"🌍 {vendor['Country']}")

    with col2:
        st.markdown("**Performance Metrics**")
        if vendor['Rating'] > 0:
            st.write(f"⭐ Rating: {vendor['Rating']:.1f} / 5.0")
            st.write(f"📦 Total Orders: {vendor['Total Orders']}")
            st.write(f"💰 Total Value: ${vendor['Total Value']:,.0f}")
        else:
            st.write("No performance data yet")

    with col3:
        st.markdown("**Certifications**")
        if vendor['Certifications']:
            for cert in vendor['Certifications'].split(', '):
                st.write(f"✅ {cert}")
        else:
            st.write("No certifications on file")

# Add New Vendor
st.markdown("---")
st.subheader("➕ Add New Vendor")

with st.form("new_vendor_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        new_code = st.text_input("Vendor Code", value=f"V-{len(vendor_df)+1:03d}")
        new_name = st.text_input("Company Name")
        new_contact = st.text_input("Contact Person")

    with col2:
        new_email = st.text_input("Email")
        new_country = st.text_input("Country")
        new_category = st.selectbox("Category", list(vendor_df['Category'].unique()) + ['Other'])

    with col3:
        new_certs = st.text_input("Certifications", placeholder="ISO 9001, ISO 14001")
        new_status = st.selectbox("Status", ['Pending', 'Approved'])

    submitted = st.form_submit_button("Add Vendor", type="primary")

    if submitted and new_name:
        new_row = pd.DataFrame({
            'Vendor Code': [new_code],
            'Company Name': [new_name],
            'Contact Person': [new_contact],
            'Email': [new_email],
            'Country': [new_country],
            'Category': [new_category],
            'Rating': [0.0],
            'Status': [new_status],
            'Certifications': [new_certs],
            'Total Orders': [0],
            'Total Value': [0],
            'On-Time Delivery %': [0],
            'Quality Score %': [0]
        })
        st.session_state.vendor_df = pd.concat([st.session_state.vendor_df, new_row], ignore_index=True)
        st.success(f"✅ Added vendor: {new_name}")
        st.rerun()

# Export
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    buffer = io.BytesIO()
    vendor_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Export Vendors to Excel",
        data=buffer,
        file_name="vendor_directory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
