"""
Procure-Pro-ISO - Procurement Dashboard
Deploy to Streamlit Cloud
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Procure-Pro-ISO", page_icon="📦", layout="wide")

# Data
@st.cache_data
def load_equipment():
    return pd.DataFrame({
        'ID': ['EQ-001', 'EQ-002', 'EQ-003', 'EQ-004', 'EQ-005', 'EQ-006', 'EQ-007', 'EQ-008'],
        'Name': ['CNC Milling Machine', 'CMM System', 'Robot Arm', 'Laser Cutter', 'EDM Machine', 'CNC Lathe', 'Surface Grinder', 'Optical Comparator'],
        'Category': ['Manufacturing', 'Quality', 'Automation', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Quality'],
        'Manufacturer': ['HAAS', 'Zeiss', 'FANUC', 'TRUMPF', 'Mitsubishi', 'Mazak', 'Okamoto', 'Nikon'],
        'Qty': [2, 1, 4, 1, 2, 3, 2, 1],
        'Unit_Price': [89500, 125000, 45000, 320000, 78000, 95000, 42000, 35000],
        'Total': [179000, 125000, 180000, 320000, 156000, 285000, 84000, 35000],
        'Status': ['Active', 'Ordered', 'Pending', 'Active', 'Delivered', 'Active', 'Pending', 'Active']
    })

@st.cache_data
def load_vendors():
    return pd.DataFrame({
        'Code': ['V-001', 'V-002', 'V-003', 'V-004', 'V-005', 'V-006'],
        'Company': ['Precision Machinery Co.', 'TechParts Intl', 'AutomaTech Solutions', 'QualityFirst Instruments', 'GlobalTools Ltd', 'Swiss Precision AG'],
        'Country': ['USA', 'Germany', 'Japan', 'Germany', 'China', 'Switzerland'],
        'Rating': [4.8, 4.5, 4.9, 4.7, 4.2, 5.0],
        'OnTime': [96, 92, 99, 94, 88, 100],
        'Quality': [98, 95, 99, 97, 90, 100],
        'Orders': [24, 18, 12, 15, 32, 8],
        'Status': ['Approved', 'Approved', 'Approved', 'Approved', 'Approved', 'Approved']
    })

@st.cache_data
def load_rfqs():
    return pd.DataFrame({
        'RFQ': ['RFQ-2024-001', 'RFQ-2024-002', 'RFQ-2024-003', 'RFQ-2024-004', 'RFQ-2024-005'],
        'Title': ['CNC Machinery', 'QC Equipment', 'Automation Systems', 'Laser Cutting', 'EDM Package'],
        'Value': [450000, 180000, 280000, 350000, 200000],
        'Status': ['Open', 'Closed', 'Open', 'Draft', 'Awarded'],
        'Priority': ['High', 'Normal', 'Critical', 'High', 'Normal'],
        'Responses': [3, 4, 2, 0, 4],
        'Vendors': [5, 4, 6, 0, 4]
    })

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #5856d6 0%, #673ab7 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">📦 Procure-Pro-ISO</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0;">ISO-Compliant Procurement Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Load data
equipment = load_equipment()
vendors = load_vendors()
rfqs = load_rfqs()

# KPI Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Equipment", "12", "+2")
col2.metric("Total Budget", "$1.8M", "+5.2%")
col3.metric("Active RFQs", "3", "-1")
col4.metric("Pending Approvals", "4", "+2")

st.markdown("---")

# Charts
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Budget vs Spending")
    budget = pd.DataFrame({
        'Month': ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'],
        'Budget': [1.2, 1.35, 1.5, 1.65, 1.75, 1.8],
        'Spent': [0.98, 1.15, 1.38, 1.52, 1.68, 1.42]
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=budget['Month'], y=budget['Budget'], name='Budget', fill='tozeroy', line=dict(color='#8b5cf6')))
    fig.add_trace(go.Scatter(x=budget['Month'], y=budget['Spent'], name='Spent', fill='tozeroy', line=dict(color='#3b82f6')))
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), yaxis_title="$ Millions", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 RFQ Status")
    status = rfqs['Status'].value_counts()
    fig = px.pie(values=status.values, names=status.index, hole=0.4, color_discrete_sequence=['#3b82f6','#22c55e','#f97316','#8b5cf6','#9ca3af'])
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# Tables
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Active RFQs")
    rfq_display = rfqs[['RFQ', 'Title', 'Value', 'Status', 'Priority']].copy()
    rfq_display['Value'] = rfq_display['Value'].apply(lambda x: f"${x:,}")
    st.dataframe(rfq_display, use_container_width=True, hide_index=True)

with col2:
    st.subheader("⭐ Top Vendors")
    vendor_display = vendors[['Company', 'Rating', 'OnTime', 'Quality']].copy()
    vendor_display.columns = ['Company', 'Rating', 'On-Time %', 'Quality %']
    st.dataframe(vendor_display, use_container_width=True, hide_index=True)

st.markdown("---")

# Equipment Table
st.subheader("📦 Equipment Master List")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    search = st.text_input("🔍 Search", placeholder="Search equipment...")
with col2:
    cat_filter = st.selectbox("Category", ['All'] + list(equipment['Category'].unique()))
with col3:
    status_filter = st.selectbox("Status", ['All'] + list(equipment['Status'].unique()))

filtered = equipment.copy()
if search:
    filtered = filtered[filtered['Name'].str.contains(search, case=False)]
if cat_filter != 'All':
    filtered = filtered[filtered['Category'] == cat_filter]
if status_filter != 'All':
    filtered = filtered[filtered['Status'] == status_filter]

display_eq = filtered.copy()
display_eq['Unit_Price'] = display_eq['Unit_Price'].apply(lambda x: f"${x:,}")
display_eq['Total'] = display_eq['Total'].apply(lambda x: f"${x:,}")
st.dataframe(display_eq, use_container_width=True, hide_index=True)

# Export
col1, col2 = st.columns([1, 4])
with col1:
    buffer = io.BytesIO()
    equipment.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button("📥 Export Excel", buffer.getvalue(), "equipment.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.caption("Procure-Pro-ISO v1.0 | ISO 17025, ISO 9001, IATF 16949")
