"""
Procure-Pro-ISO - Streamlit Procurement Analysis App
Main entry point for multi-page Streamlit application
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Procure-Pro-ISO",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.8);
        margin: 0.5rem 0 0 0;
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid;
    }
    .kpi-blue { border-left-color: #3b82f6; }
    .kpi-green { border-left-color: #22c55e; }
    .kpi-orange { border-left-color: #f97316; }
    .kpi-purple { border-left-color: #8b5cf6; }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, rgba(88, 86, 214, 0.1) 0%, rgba(103, 58, 183, 0.1) 100%);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem;">
    <h2 style="color: #5856d6;">📦 Procure-Pro-ISO</h2>
    <p style="color: #666; font-size: 0.8rem;">ISO Compliant Procurement</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Main page content
st.markdown("""
<div class="main-header">
    <h1>📦 Procure-Pro-ISO</h1>
    <p>Comprehensive ISO-compliant Procurement Lifecycle Management</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
## Welcome to Procure-Pro-ISO

This application provides comprehensive procurement management with ISO compliance features:

### 📊 Features

- **Dashboard** - Real-time KPIs and procurement overview
- **Equipment Master** - Manage equipment inventory with Excel import
- **RFQ Management** - Create and track requests for quotation
- **Vendor Management** - Supplier directory with performance ratings
- **Technical Evaluation** - CTQ matrix and vendor scoring
- **Commercial Evaluation** - TCO calculator and price comparison

### 🚀 Getting Started

Use the **sidebar navigation** to access different modules, or click the links below:

""")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/1_📊_Dashboard.py", label="📊 Dashboard", icon="📊")
    st.page_link("pages/2_📦_Equipment_Master.py", label="📦 Equipment Master", icon="📦")

with col2:
    st.page_link("pages/3_📝_RFQ_Management.py", label="📝 RFQ Management", icon="📝")
    st.page_link("pages/4_👥_Vendor_Management.py", label="👥 Vendor Management", icon="👥")

with col3:
    st.page_link("pages/5_🔬_Technical_Evaluation.py", label="🔬 Technical Evaluation", icon="🔬")
    st.page_link("pages/6_💰_Commercial_Evaluation.py", label="💰 Commercial Evaluation", icon="💰")

st.markdown("---")

# Quick stats
st.subheader("📈 Quick Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Equipment", value="12", delta="+2")
with col2:
    st.metric(label="Total Budget", value="$1.8M", delta="+5.2%")
with col3:
    st.metric(label="Active RFQs", value="3", delta="-1")
with col4:
    st.metric(label="Pending Approvals", value="4", delta="+2")

st.markdown("---")
st.caption("Procure-Pro-ISO v1.0 | ISO 17025, ISO 9001, IATF 16949 Compliant")
