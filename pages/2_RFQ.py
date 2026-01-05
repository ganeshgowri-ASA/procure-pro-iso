import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="RFQ | Procure-Pro-ISO", page_icon="📝", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #5856d6 0%, #673ab7 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <h2 style="color: white; margin: 0;">📝 RFQ Management</h2>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_rfqs():
    return pd.DataFrame({
        'RFQ': ['RFQ-2024-001', 'RFQ-2024-002', 'RFQ-2024-003', 'RFQ-2024-004', 'RFQ-2024-005'],
        'Title': ['CNC Machinery Procurement', 'Quality Control Equipment', 'Automation Systems', 'Laser Cutting System', 'EDM Equipment Package'],
        'Value': [450000, 180000, 280000, 350000, 200000],
        'Status': ['Open', 'Closed', 'Open', 'Draft', 'Awarded'],
        'Priority': ['High', 'Normal', 'Critical', 'High', 'Normal'],
        'Issue_Date': ['2024-01-15', '2024-01-10', '2024-01-20', '2024-01-25', '2024-01-05'],
        'Closing_Date': ['2024-02-15', '2024-02-01', '2024-02-20', '2024-02-25', '2024-01-25'],
        'Responses': [3, 4, 2, 0, 4],
        'Vendors': [5, 4, 6, 0, 4]
    })

if 'rfqs' not in st.session_state:
    st.session_state.rfqs = load_rfqs()

df = st.session_state.rfqs

# Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total RFQs", len(df))
col2.metric("Open", len(df[df['Status']=='Open']))
col3.metric("Total Value", f"${df['Value'].sum()/1e6:.2f}M")
col4.metric("Avg Response", f"{(df['Responses'].sum()/df['Vendors'].replace(0,1).sum()*100):.0f}%")

st.markdown("---")

# Upload
st.subheader("📤 Upload RFQ Documents")
files = st.file_uploader("Upload files", type=['pdf', 'xlsx', 'docx'], accept_multiple_files=True)
if files:
    st.success(f"Uploaded {len(files)} file(s)")

st.markdown("---")

# Filters
col1, col2 = st.columns(2)
status_f = col1.selectbox("Status", ['All', 'Open', 'Closed', 'Draft', 'Awarded'])
priority_f = col2.selectbox("Priority", ['All', 'Critical', 'High', 'Normal', 'Low'])

filtered = df.copy()
if status_f != 'All':
    filtered = filtered[filtered['Status'] == status_f]
if priority_f != 'All':
    filtered = filtered[filtered['Priority'] == priority_f]

# Table
st.subheader("📋 RFQ List")
display = filtered.copy()
display['Value'] = display['Value'].apply(lambda x: f"${x:,}")
display['Response Rate'] = (filtered['Responses']/filtered['Vendors'].replace(0,1)*100).round().astype(int).astype(str) + '%'
st.dataframe(display[['RFQ', 'Title', 'Priority', 'Status', 'Value', 'Response Rate']], use_container_width=True, hide_index=True)

# Comparison
st.markdown("---")
st.subheader("📊 Vendor Comparison")

quotes = pd.DataFrame({
    'Vendor': ['Precision Machinery', 'TechParts Intl', 'AutomaTech'],
    'Quote': [185775, 189152, 190810],
    'Delivery': [45, 60, 90],
    'Technical': [92, 90, 89],
    'Warranty': ['3 years', '2 years', '2 years']
})

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(quotes, x='Vendor', y='Quote', color='Vendor', title="Quote Comparison")
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.bar(quotes, x='Vendor', y='Delivery', color='Vendor', title="Delivery Days")
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

quotes['Quote'] = quotes['Quote'].apply(lambda x: f"${x:,}")
st.dataframe(quotes, use_container_width=True, hide_index=True)

# Export
buffer = io.BytesIO()
df.to_excel(buffer, index=False, engine='openpyxl')
st.download_button("📥 Export RFQs", buffer.getvalue(), "rfqs.xlsx")
