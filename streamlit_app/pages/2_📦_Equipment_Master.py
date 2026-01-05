"""
Equipment Master Page - Procure-Pro-ISO
Manage equipment inventory with Excel import/export
"""

import streamlit as st
import pandas as pd
import io
import sys
sys.path.append('..')
from data.sample_data import get_equipment_data

st.set_page_config(page_title="Equipment Master | Procure-Pro-ISO", page_icon="📦", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">📦 Equipment Master List</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Manage equipment inventory</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for equipment data
if 'equipment_df' not in st.session_state:
    st.session_state.equipment_df = get_equipment_data()

# Stats Row
col1, col2, col3, col4 = st.columns(4)

df = st.session_state.equipment_df

with col1:
    st.metric("Total Equipment", len(df))
with col2:
    st.metric("Total Value", f"${df['Total Price'].sum():,.0f}")
with col3:
    st.metric("Active Items", len(df[df['Status'] == 'Active']))
with col4:
    st.metric("Pending RFQs", len(df[df['RFQ Status'] == 'Pending']))

st.markdown("---")

# File Upload Section
st.subheader("📤 Upload Equipment Data")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload Excel file to import equipment data",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with equipment data. Required columns: Name, Category, Manufacturer, Quantity, Unit Price"
    )

    if uploaded_file is not None:
        try:
            imported_df = pd.read_excel(uploaded_file)
            st.success(f"✅ Loaded {len(imported_df)} rows from {uploaded_file.name}")

            with st.expander("Preview Imported Data"):
                st.dataframe(imported_df, use_container_width=True)

            if st.button("Import Data", type="primary"):
                # Merge with existing data
                st.session_state.equipment_df = pd.concat([st.session_state.equipment_df, imported_df], ignore_index=True)
                st.success("Data imported successfully!")
                st.rerun()

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

with col2:
    st.markdown("**Download Template**")
    template_df = pd.DataFrame({
        'Equipment ID': ['EQ-XXX'],
        'Name': ['Equipment Name'],
        'Category': ['Manufacturing'],
        'Manufacturer': ['Brand'],
        'Model': ['Model-X'],
        'Specifications': ['Specs here'],
        'Quantity': [1],
        'Unit Price': [50000],
        'Status': ['Pending'],
        'RFQ Status': ['Pending']
    })

    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Download Template",
        data=buffer,
        file_name="equipment_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("---")

# Filters
st.subheader("🔍 Filter Equipment")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("Search", placeholder="Search by name, ID, manufacturer...")

with col2:
    categories = ['All'] + list(df['Category'].unique())
    selected_category = st.selectbox("Category", categories)

with col3:
    statuses = ['All'] + list(df['Status'].unique())
    selected_status = st.selectbox("Status", statuses)

# Apply filters
filtered_df = df.copy()

if search:
    mask = (
        filtered_df['Name'].str.contains(search, case=False, na=False) |
        filtered_df['Equipment ID'].str.contains(search, case=False, na=False) |
        filtered_df['Manufacturer'].str.contains(search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]

# Equipment Table
st.subheader(f"📋 Equipment List ({len(filtered_df)} items)")

# Style the dataframe
def style_status(val):
    colors = {
        'Active': 'background-color: #dcfce7; color: #166534;',
        'Pending': 'background-color: #fef3c7; color: #92400e;',
        'Ordered': 'background-color: #dbeafe; color: #1e40af;',
        'Delivered': 'background-color: #f3e8ff; color: #6b21a8;'
    }
    return colors.get(val, '')

# Display dataframe
display_df = filtered_df[['Equipment ID', 'Name', 'Category', 'Manufacturer', 'Model', 'Quantity', 'Unit Price', 'Total Price', 'Status', 'RFQ Status']].copy()
display_df['Unit Price'] = display_df['Unit Price'].apply(lambda x: f"${x:,.0f}")
display_df['Total Price'] = display_df['Total Price'].apply(lambda x: f"${x:,.0f}")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Equipment ID": st.column_config.TextColumn("ID", width="small"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "RFQ Status": st.column_config.TextColumn("RFQ", width="small"),
    }
)

# Export Button
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    buffer = io.BytesIO()
    filtered_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Export to Excel",
        data=buffer,
        file_name="equipment_master.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

with col2:
    if st.button("🔄 Refresh Data"):
        st.session_state.equipment_df = get_equipment_data()
        st.rerun()

# Add New Equipment Form
st.markdown("---")
st.subheader("➕ Add New Equipment")

with st.form("new_equipment_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        new_id = st.text_input("Equipment ID", value=f"EQ-{len(df)+1:03d}")
        new_name = st.text_input("Name")
        new_category = st.selectbox("Category", ['Manufacturing', 'Quality', 'Automation', 'Other'])

    with col2:
        new_manufacturer = st.text_input("Manufacturer")
        new_model = st.text_input("Model")
        new_specs = st.text_area("Specifications", height=100)

    with col3:
        new_qty = st.number_input("Quantity", min_value=1, value=1)
        new_price = st.number_input("Unit Price ($)", min_value=0, value=0)
        new_status = st.selectbox("Status", ['Pending', 'Active', 'Ordered'])

    submitted = st.form_submit_button("Add Equipment", type="primary")

    if submitted and new_name:
        new_row = pd.DataFrame({
            'Equipment ID': [new_id],
            'Name': [new_name],
            'Category': [new_category],
            'Manufacturer': [new_manufacturer],
            'Model': [new_model],
            'Specifications': [new_specs],
            'Quantity': [new_qty],
            'Unit Price': [new_price],
            'Total Price': [new_qty * new_price],
            'Status': [new_status],
            'RFQ Status': ['Pending']
        })
        st.session_state.equipment_df = pd.concat([st.session_state.equipment_df, new_row], ignore_index=True)
        st.success(f"✅ Added {new_name} to equipment list!")
        st.rerun()
