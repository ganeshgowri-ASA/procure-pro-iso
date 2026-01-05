import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Vendors | Procure-Pro-ISO", page_icon="👥", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #5856d6 0%, #673ab7 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <h2 style="color: white; margin: 0;">👥 Vendor Management</h2>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_vendors():
    return pd.DataFrame({
        'Code': ['V-001', 'V-002', 'V-003', 'V-004', 'V-005', 'V-006'],
        'Company': ['Precision Machinery Co.', 'TechParts International', 'AutomaTech Solutions', 'QualityFirst Instruments', 'GlobalTools Ltd', 'Swiss Precision AG'],
        'Contact': ['John Smith', 'Maria Garcia', 'Kenji Tanaka', 'Hans Mueller', 'Li Wei', 'Pierre Dubois'],
        'Email': ['john@precision.com', 'maria@techparts.com', 'kenji@automatech.jp', 'hans@qualityfirst.de', 'liwei@globaltools.cn', 'pierre@swissprecision.ch'],
        'Country': ['USA', 'Germany', 'Japan', 'Germany', 'China', 'Switzerland'],
        'Category': ['Manufacturing', 'Components', 'Automation', 'Quality', 'Tooling', 'Precision'],
        'Rating': [4.8, 4.5, 4.9, 4.7, 4.2, 5.0],
        'OnTime': [96, 92, 99, 94, 88, 100],
        'Quality': [98, 95, 99, 97, 90, 100],
        'Orders': [24, 18, 12, 15, 32, 8],
        'Value': [1250000, 890000, 720000, 560000, 420000, 380000],
        'Status': ['Approved', 'Approved', 'Approved', 'Approved', 'Approved', 'Approved']
    })

if 'vendors' not in st.session_state:
    st.session_state.vendors = load_vendors()

df = st.session_state.vendors

# Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Vendors", len(df))
col2.metric("Approved", len(df[df['Status']=='Approved']))
col3.metric("Avg Rating", f"{df['Rating'].mean():.1f}/5")
col4.metric("Total Value", f"${df['Value'].sum()/1e6:.1f}M")

st.markdown("---")

# Performance Chart
st.subheader("📊 Performance Overview")
fig = go.Figure()
fig.add_trace(go.Bar(name='On-Time %', x=df['Company'], y=df['OnTime'], marker_color='#3b82f6'))
fig.add_trace(go.Bar(name='Quality %', x=df['Company'], y=df['Quality'], marker_color='#22c55e'))
fig.update_layout(barmode='group', height=350, margin=dict(l=0,r=0,t=10,b=0))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Filters
col1, col2 = st.columns(2)
search = col1.text_input("🔍 Search vendors")
status_f = col2.selectbox("Status", ['All', 'Approved', 'Pending'])

filtered = df.copy()
if search:
    filtered = filtered[filtered['Company'].str.contains(search, case=False)]
if status_f != 'All':
    filtered = filtered[filtered['Status'] == status_f]

# Table with stars
st.subheader("📋 Vendor Directory")

def stars(r):
    return "⭐" * int(r) + f" ({r:.1f})"

display = filtered.copy()
display['Rating'] = display['Rating'].apply(stars)
display['Value'] = display['Value'].apply(lambda x: f"${x:,}")
display['OnTime'] = display['OnTime'].astype(str) + '%'
display['Quality'] = display['Quality'].astype(str) + '%'

st.dataframe(display[['Code', 'Company', 'Country', 'Category', 'Rating', 'OnTime', 'Quality', 'Orders', 'Status']], use_container_width=True, hide_index=True)

# Details
st.markdown("---")
st.subheader("🔍 Vendor Details")
selected = st.selectbox("Select Vendor", df['Company'].tolist())
v = df[df['Company'] == selected].iloc[0]

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Contact**")
    st.write(f"👤 {v['Contact']}")
    st.write(f"📧 {v['Email']}")
    st.write(f"🌍 {v['Country']}")
with col2:
    st.markdown("**Performance**")
    st.write(f"⭐ Rating: {v['Rating']}/5")
    st.write(f"📦 Orders: {v['Orders']}")
    st.write(f"💰 Value: ${v['Value']:,}")
with col3:
    st.markdown("**Metrics**")
    st.write(f"⏱️ On-Time: {v['OnTime']}%")
    st.write(f"✅ Quality: {v['Quality']}%")

# Export
buffer = io.BytesIO()
df.to_excel(buffer, index=False, engine='openpyxl')
st.download_button("📥 Export Vendors", buffer.getvalue(), "vendors.xlsx")
