"""
RFQ Management Page - Procure-Pro-ISO
Create and manage Requests for Quotation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import io
import sys
sys.path.append('..')
from data.sample_data import get_rfq_data, get_vendor_data

st.set_page_config(page_title="RFQ Management | Procure-Pro-ISO", page_icon="📝", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">📝 RFQ Management</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Request for Quotation workflow</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'rfq_df' not in st.session_state:
    st.session_state.rfq_df = get_rfq_data()

rfq_df = st.session_state.rfq_df
vendor_df = get_vendor_data()

# Quick Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total RFQs", len(rfq_df))
with col2:
    st.metric("Open RFQs", len(rfq_df[rfq_df['Status'] == 'Open']))
with col3:
    total_value = rfq_df['Estimated Value'].sum()
    st.metric("Total Value", f"${total_value/1000000:.2f}M")
with col4:
    avg_response = (rfq_df['Responses'].sum() / rfq_df['Vendors Invited'].replace(0, 1).sum() * 100)
    st.metric("Avg Response Rate", f"{avg_response:.0f}%")

st.markdown("---")

# File Upload for RFQ Documents
st.subheader("📤 Upload RFQ Documents")

uploaded_files = st.file_uploader(
    "Upload RFQ documents (PDF, Excel)",
    type=['pdf', 'xlsx', 'xls', 'docx'],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
    for f in uploaded_files:
        st.write(f"  • {f.name} ({f.size/1024:.1f} KB)")

st.markdown("---")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("🔍 Search RFQs", placeholder="Search by number or title...")

with col2:
    status_filter = st.selectbox("Status", ['All', 'Open', 'Closed', 'Draft', 'Awarded'])

with col3:
    priority_filter = st.selectbox("Priority", ['All', 'Critical', 'High', 'Normal', 'Low'])

# Apply filters
filtered_df = rfq_df.copy()

if search:
    mask = (
        filtered_df['RFQ Number'].str.contains(search, case=False, na=False) |
        filtered_df['Title'].str.contains(search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if status_filter != 'All':
    filtered_df = filtered_df[filtered_df['Status'] == status_filter]

if priority_filter != 'All':
    filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]

# RFQ Table
st.subheader(f"📋 RFQ List ({len(filtered_df)} items)")

display_df = filtered_df.copy()
display_df['Estimated Value'] = display_df['Estimated Value'].apply(lambda x: f"${x:,.0f}")
display_df['Response Rate'] = (display_df['Responses'] / display_df['Vendors Invited'].replace(0, 1) * 100).round(0).astype(str) + '%'

st.dataframe(
    display_df[['RFQ Number', 'Title', 'Priority', 'Status', 'Issue Date', 'Closing Date', 'Estimated Value', 'Response Rate']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Priority": st.column_config.TextColumn("Priority", width="small"),
        "Status": st.column_config.TextColumn("Status", width="small"),
    }
)

# Vendor Comparison Section
st.markdown("---")
st.subheader("📊 Vendor Comparison")

# Select RFQ for comparison
selected_rfq = st.selectbox("Select RFQ for Vendor Comparison", rfq_df['RFQ Number'].tolist())

if selected_rfq:
    st.markdown(f"**Comparing vendors for: {selected_rfq}**")

    # Mock vendor quotes for comparison
    vendor_quotes = pd.DataFrame({
        'Vendor': ['Precision Machinery Co.', 'TechParts International', 'AutomaTech Solutions'],
        'Quote Amount': [185775, 189152, 190810],
        'Delivery Days': [45, 60, 90],
        'Payment Terms': ['Net 30', 'Net 45', 'Net 30'],
        'Warranty': ['3 years', '2 years', '2 years'],
        'Technical Score': [92, 90, 89],
        'Status': ['Received', 'Received', 'Received']
    })

    col1, col2 = st.columns(2)

    with col1:
        # Quote comparison chart
        fig = px.bar(
            vendor_quotes,
            x='Vendor',
            y='Quote Amount',
            color='Vendor',
            title="Quote Comparison",
            color_discrete_sequence=['#8b5cf6', '#3b82f6', '#22c55e']
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Delivery comparison
        fig = px.bar(
            vendor_quotes,
            x='Vendor',
            y='Delivery Days',
            color='Vendor',
            title="Delivery Timeline (Days)",
            color_discrete_sequence=['#8b5cf6', '#3b82f6', '#22c55e']
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Vendor quotes table
    st.markdown("**Vendor Quotes Detail**")
    vendor_quotes['Quote Amount'] = vendor_quotes['Quote Amount'].apply(lambda x: f"${x:,.0f}")
    st.dataframe(vendor_quotes, use_container_width=True, hide_index=True)

# Create New RFQ
st.markdown("---")
st.subheader("➕ Create New RFQ")

with st.form("new_rfq_form"):
    col1, col2 = st.columns(2)

    with col1:
        new_title = st.text_input("RFQ Title")
        new_description = st.text_area("Description", height=100)
        new_priority = st.selectbox("Priority", ['Normal', 'Low', 'High', 'Critical'])

    with col2:
        new_closing_date = st.date_input("Closing Date")
        new_value = st.number_input("Estimated Value ($)", min_value=0, value=0)
        selected_vendors = st.multiselect(
            "Invite Vendors",
            vendor_df[vendor_df['Status'] == 'Approved']['Company Name'].tolist()
        )

    submitted = st.form_submit_button("Create RFQ", type="primary")

    if submitted and new_title:
        new_rfq_num = f"RFQ-2024-{len(rfq_df)+1:03d}"
        new_row = pd.DataFrame({
            'RFQ Number': [new_rfq_num],
            'Title': [new_title],
            'Description': [new_description],
            'Status': ['Draft'],
            'Priority': [new_priority],
            'Issue Date': [pd.Timestamp.now().strftime('%Y-%m-%d')],
            'Closing Date': [new_closing_date.strftime('%Y-%m-%d')],
            'Estimated Value': [new_value],
            'Vendors Invited': [len(selected_vendors)],
            'Responses': [0]
        })
        st.session_state.rfq_df = pd.concat([st.session_state.rfq_df, new_row], ignore_index=True)
        st.success(f"✅ Created {new_rfq_num}: {new_title}")
        st.rerun()

# Export
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    buffer = io.BytesIO()
    rfq_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Export RFQs to Excel",
        data=buffer,
        file_name="rfq_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
