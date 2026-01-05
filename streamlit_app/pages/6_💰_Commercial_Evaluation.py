"""
Commercial Evaluation Page - Procure-Pro-ISO
TCO calculator and price comparison
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import sys
sys.path.append('..')
from data.sample_data import get_commercial_evaluation_data

st.set_page_config(page_title="Commercial Evaluation | Procure-Pro-ISO", page_icon="💰", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">💰 Commercial Evaluation</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">TCO calculator and price comparison</p>
</div>
""", unsafe_allow_html=True)

# Load data
pricing_df, tco_df = get_commercial_evaluation_data()

# RFQ Selection
st.subheader("📋 Select RFQ for Evaluation")
selected_rfq = st.selectbox("RFQ", ["RFQ-2024-001: CNC Machinery Procurement"])

st.markdown("---")

# Price Comparison Cards
st.subheader("💵 Price Comparison")

col1, col2, col3 = st.columns(3)

# Find lowest TCO
tco_totals = tco_df[tco_df['Cost Category'] == 'Total 5-Year TCO'].iloc[0]
min_tco_vendor = tco_totals[['Precision Machinery', 'TechParts Intl', 'AutomaTech']].idxmin()

for i, (col, vendor) in enumerate(zip([col1, col2, col3], pricing_df.itertuples())):
    with col:
        is_lowest = vendor.Vendor.split()[0] in min_tco_vendor

        # Get TCO for this vendor
        vendor_key = 'Precision Machinery' if 'Precision' in vendor.Vendor else 'TechParts Intl' if 'Tech' in vendor.Vendor else 'AutomaTech'
        vendor_tco = tco_totals[vendor_key]

        border_color = "#22c55e" if is_lowest else "#e5e7eb"
        badge = "🏆 Lowest TCO" if is_lowest else ""

        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1f2937;">{vendor.Vendor}</h4>
                <span style="font-size: 0.75rem; color: #22c55e;">{badge}</span>
            </div>

            <div style="text-align: center; padding: 1rem; background: #f9fafb; border-radius: 8px; margin-bottom: 1rem;">
                <h2 style="margin: 0; color: #1f2937;">${vendor.Total:,.0f}</h2>
                <p style="margin: 0; color: #666; font-size: 0.875rem;">Initial Quote</p>
            </div>

            <div style="border-top: 1px solid #e5e7eb; padding-top: 1rem;">
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;">
                    <span style="color: #666;">Unit Price</span>
                    <span style="font-weight: 500;">${vendor._3:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;">
                    <span style="color: #666;">Quantity</span>
                    <span style="font-weight: 500;">{vendor.Quantity}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;">
                    <span style="color: #666;">Discount</span>
                    <span style="font-weight: 500; color: #22c55e;">-{vendor._6}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;">
                    <span style="color: #666;">Shipping</span>
                    <span style="font-weight: 500;">${vendor.Shipping:,.0f}</span>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-top: 1rem;
                        padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                <div style="text-align: center;">
                    <p style="margin: 0; font-weight: bold;">{vendor._11}d</p>
                    <p style="margin: 0; font-size: 0.75rem; color: #666;">Delivery</p>
                </div>
                <div style="text-align: center;">
                    <p style="margin: 0; font-weight: bold;">{vendor._10}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: #666;">Terms</p>
                </div>
                <div style="text-align: center;">
                    <p style="margin: 0; font-weight: bold;">{vendor.Warranty}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: #666;">Warranty</p>
                </div>
            </div>

            <div style="margin-top: 1rem; padding: 0.75rem; background: #f3e8ff; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #7c3aed; font-weight: 500;">5-Year TCO</span>
                    <span style="color: #7c3aed; font-weight: bold; font-size: 1.25rem;">${vendor_tco:,.0f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# TCO Breakdown Chart
st.subheader("📊 Total Cost of Ownership Breakdown")

col1, col2 = st.columns([2, 1])

with col1:
    # Prepare data for chart (exclude total row)
    chart_df = tco_df[tco_df['Cost Category'] != 'Total 5-Year TCO'].copy()

    fig = go.Figure()

    colors = ['#8b5cf6', '#3b82f6', '#22c55e']
    vendors = ['Precision Machinery', 'TechParts Intl', 'AutomaTech']

    for i, vendor in enumerate(vendors):
        fig.add_trace(go.Bar(
            name=vendor,
            y=chart_df['Cost Category'],
            x=chart_df[vendor],
            orientation='h',
            marker_color=colors[i]
        ))

    fig.update_layout(
        barmode='group',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Cost ($)"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**TCO Summary**")

    tco_summary = tco_df[tco_df['Cost Category'] == 'Total 5-Year TCO'].iloc[0]

    for vendor in ['Precision Machinery', 'TechParts Intl', 'AutomaTech']:
        is_min = vendor == min_tco_vendor
        icon = "🏆" if is_min else "💰"
        color = "#22c55e" if is_min else "#1f2937"

        st.markdown(f"""
        <div style="padding: 0.75rem; background: {'#dcfce7' if is_min else '#f9fafb'};
                    border-radius: 8px; margin-bottom: 0.5rem;">
            <p style="margin: 0; font-weight: 500; color: {color};">{icon} {vendor}</p>
            <p style="margin: 0; font-size: 1.25rem; font-weight: bold; color: {color};">${tco_summary[vendor]:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

# Detailed Price Comparison Table
st.markdown("---")
st.subheader("📋 Detailed Price Comparison")

st.dataframe(tco_df, use_container_width=True, hide_index=True)

# TCO Calculator
st.markdown("---")
st.subheader("🧮 TCO Calculator")

st.markdown("Adjust parameters to recalculate Total Cost of Ownership:")

col1, col2, col3 = st.columns(3)

with col1:
    analysis_years = st.number_input("Analysis Period (Years)", min_value=1, max_value=10, value=5)
with col2:
    discount_rate = st.number_input("Discount Rate (%)", min_value=0.0, max_value=20.0, value=8.0)
with col3:
    maintenance_rate = st.number_input("Annual Maintenance (%)", min_value=0.0, max_value=20.0, value=5.0)

if st.button("Recalculate TCO", type="primary"):
    st.markdown("**Recalculated TCO (with adjusted parameters):**")

    # Simple TCO recalculation
    for vendor in pricing_df.itertuples():
        vendor_key = 'Precision Machinery' if 'Precision' in vendor.Vendor else 'TechParts Intl' if 'Tech' in vendor.Vendor else 'AutomaTech'

        initial = vendor.Total
        maintenance = initial * (maintenance_rate / 100) * analysis_years
        # Simple NPV adjustment
        npv_factor = sum(1 / (1 + discount_rate/100)**i for i in range(1, analysis_years + 1))
        adjusted_tco = initial + maintenance * (npv_factor / analysis_years)

        st.write(f"**{vendor.Vendor}**: ${adjusted_tco:,.0f} (over {analysis_years} years)")

# Recommendation
st.markdown("---")
st.subheader("📝 Recommendation")

st.markdown(f"""
<div style="background: linear-gradient(135deg, #f3e8ff 0%, #dbeafe 100%);
            padding: 1.5rem; border-radius: 10px; border-left: 4px solid #8b5cf6;">
    <div style="display: flex; align-items: start; gap: 1rem;">
        <span style="font-size: 2rem;">🏆</span>
        <div>
            <h4 style="margin: 0; color: #1f2937;">Recommendation</h4>
            <p style="margin: 0.5rem 0 0 0; color: #4b5563;">
                Based on the comprehensive TCO analysis, <strong>Precision Machinery Co.</strong> offers the best value
                with a 5-year TCO of <strong>${tco_totals['Precision Machinery']:,.0f}</strong>. This includes the lowest
                combined cost for initial purchase, installation, training, and ongoing maintenance.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Export
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        pricing_df.to_excel(writer, sheet_name='Vendor Pricing', index=False)
        tco_df.to_excel(writer, sheet_name='TCO Breakdown', index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Export Commercial Report",
        data=buffer,
        file_name="commercial_evaluation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
