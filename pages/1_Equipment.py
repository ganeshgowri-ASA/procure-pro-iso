import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Equipment | Procure-Pro-ISO", page_icon="📦", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #5856d6 0%, #673ab7 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <h2 style="color: white; margin: 0;">📦 Equipment Master</h2>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.DataFrame({
        'ID': ['EQ-001', 'EQ-002', 'EQ-003', 'EQ-004', 'EQ-005', 'EQ-006', 'EQ-007', 'EQ-008'],
        'Name': ['CNC Milling Machine', 'CMM System', 'Robot Arm', 'Laser Cutter', 'EDM Machine', 'CNC Lathe', 'Surface Grinder', 'Optical Comparator'],
        'Category': ['Manufacturing', 'Quality', 'Automation', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Quality'],
        'Manufacturer': ['HAAS', 'Zeiss', 'FANUC', 'TRUMPF', 'Mitsubishi', 'Mazak', 'Okamoto', 'Nikon'],
        'Model': ['VF-2SS', 'CONTURA G3', 'M-20iD/25', 'TruLaser 3030', 'MV2400R', 'QT-250MY', 'ACC-820DX', 'V-24B'],
        'Qty': [2, 1, 4, 1, 2, 3, 2, 1],
        'Unit_Price': [89500, 125000, 45000, 320000, 78000, 95000, 42000, 35000],
        'Total': [179000, 125000, 180000, 320000, 156000, 285000, 84000, 35000],
        'Status': ['Active', 'Ordered', 'Pending', 'Active', 'Delivered', 'Active', 'Pending', 'Active']
    })

if 'equipment' not in st.session_state:
    st.session_state.equipment = load_data()

df = st.session_state.equipment

# Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Items", len(df))
col2.metric("Total Value", f"${df['Total'].sum():,}")
col3.metric("Active", len(df[df['Status']=='Active']))
col4.metric("Pending", len(df[df['Status']=='Pending']))

st.markdown("---")

# Upload
st.subheader("📤 Import Equipment Data")
uploaded = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
if uploaded:
    try:
        new_data = pd.read_excel(uploaded)
        st.success(f"Loaded {len(new_data)} rows")
        with st.expander("Preview"):
            st.dataframe(new_data)
        if st.button("Import", type="primary"):
            st.session_state.equipment = pd.concat([df, new_data], ignore_index=True)
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")

# Filters
col1, col2, col3 = st.columns(3)
search = col1.text_input("🔍 Search")
cat = col2.selectbox("Category", ['All'] + list(df['Category'].unique()))
status = col3.selectbox("Status", ['All'] + list(df['Status'].unique()))

filtered = df.copy()
if search:
    filtered = filtered[filtered['Name'].str.contains(search, case=False) | filtered['ID'].str.contains(search, case=False)]
if cat != 'All':
    filtered = filtered[filtered['Category'] == cat]
if status != 'All':
    filtered = filtered[filtered['Status'] == status]

# Table
st.subheader(f"📋 Equipment List ({len(filtered)} items)")
display = filtered.copy()
display['Unit_Price'] = display['Unit_Price'].apply(lambda x: f"${x:,}")
display['Total'] = display['Total'].apply(lambda x: f"${x:,}")
st.dataframe(display, use_container_width=True, hide_index=True)

# Export
col1, col2 = st.columns([1, 4])
buffer = io.BytesIO()
df.to_excel(buffer, index=False, engine='openpyxl')
col1.download_button("📥 Export Excel", buffer.getvalue(), "equipment.xlsx")

# Add Form
st.markdown("---")
st.subheader("➕ Add Equipment")
with st.form("add_eq"):
    c1, c2, c3 = st.columns(3)
    new_id = c1.text_input("ID", f"EQ-{len(df)+1:03d}")
    new_name = c2.text_input("Name")
    new_cat = c3.selectbox("Cat", ['Manufacturing', 'Quality', 'Automation'])
    c1, c2, c3 = st.columns(3)
    new_mfr = c1.text_input("Manufacturer")
    new_qty = c2.number_input("Qty", 1)
    new_price = c3.number_input("Unit Price", 0)
    if st.form_submit_button("Add", type="primary") and new_name:
        new_row = pd.DataFrame({'ID': [new_id], 'Name': [new_name], 'Category': [new_cat], 'Manufacturer': [new_mfr], 'Model': [''], 'Qty': [new_qty], 'Unit_Price': [new_price], 'Total': [new_qty*new_price], 'Status': ['Pending']})
        st.session_state.equipment = pd.concat([df, new_row], ignore_index=True)
        st.success(f"Added {new_name}")
        st.rerun()
