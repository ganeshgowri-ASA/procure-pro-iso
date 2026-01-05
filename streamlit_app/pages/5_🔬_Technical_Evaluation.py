"""
Technical Evaluation Page - Procure-Pro-ISO
CTQ matrix and vendor technical scoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import sys
sys.path.append('..')
from data.sample_data import get_technical_evaluation_data

st.set_page_config(page_title="Technical Evaluation | Procure-Pro-ISO", page_icon="🔬", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">🔬 Technical Evaluation</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">CTQ matrix and vendor scoring</p>
</div>
""", unsafe_allow_html=True)

# Load data
scores_df, ctq_df = get_technical_evaluation_data()

# RFQ Selection
st.subheader("📋 Select RFQ for Evaluation")
selected_rfq = st.selectbox("RFQ", ["RFQ-2024-001: CNC Machinery Procurement"])

st.markdown("---")

# Vendor Score Cards
st.subheader("🏆 Vendor Scores")

col1, col2, col3 = st.columns(3)

# Sort by Overall Score descending for ranking
scores_sorted = scores_df.sort_values('Overall Score', ascending=False).reset_index(drop=True)

for i, col in enumerate([col1, col2, col3]):
    if i < len(scores_sorted):
        row = scores_sorted.iloc[i]
        vendor_name = row['Vendor']
        overall_score = row['Overall Score']
        tech_score = row['Technical Score']
        quality_score = row['Quality Score']
        delivery_score = row['Delivery Score']
        compliance_score = row['Compliance Score']
        recommendation = row['Recommendation']

        with col:
            # Determine card styling based on rank
            if i == 0:
                border_color = "#fbbf24"
                badge = "🥇 Rank #1"
            elif i == 1:
                border_color = "#9ca3af"
                badge = "🥈 Rank #2"
            else:
                border_color = "#cd7f32"
                badge = "🥉 Rank #3"

            # Score color
            if overall_score >= 90:
                score_color = "#22c55e"
            elif overall_score >= 85:
                score_color = "#3b82f6"
            else:
                score_color = "#f97316"

            # Recommendation badge colors
            rec_color = {"Recommended": "#22c55e", "Acceptable": "#3b82f6", "Not Recommended": "#ef4444"}

            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-top: 4px solid {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: #1f2937;">{vendor_name}</h4>
                    <span style="font-size: 0.75rem; color: #666;">{badge}</span>
                </div>
                <div style="text-align: center; padding: 1.5rem; background: #f9fafb; border-radius: 8px; margin-bottom: 1rem;">
                    <h1 style="margin: 0; color: {score_color}; font-size: 3rem;">{overall_score}</h1>
                    <p style="margin: 0; color: #666;">Overall Score</p>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 4px;">
                        <p style="margin: 0; font-weight: bold;">{tech_score}</p>
                        <p style="margin: 0; font-size: 0.75rem; color: #666;">Technical</p>
                    </div>
                    <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 4px;">
                        <p style="margin: 0; font-weight: bold;">{quality_score}</p>
                        <p style="margin: 0; font-size: 0.75rem; color: #666;">Quality</p>
                    </div>
                    <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 4px;">
                        <p style="margin: 0; font-weight: bold;">{delivery_score}</p>
                        <p style="margin: 0; font-size: 0.75rem; color: #666;">Delivery</p>
                    </div>
                    <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 4px;">
                        <p style="margin: 0; font-weight: bold;">{compliance_score}</p>
                        <p style="margin: 0; font-size: 0.75rem; color: #666;">Compliance</p>
                    </div>
                </div>
                <div style="margin-top: 1rem; text-align: center;">
                    <span style="background: {rec_color.get(recommendation, '#9ca3af')}20;
                                color: {rec_color.get(recommendation, '#666')};
                                padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.875rem;">
                        {recommendation}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Radar Chart Comparison
st.subheader("📊 Performance Comparison")

col1, col2 = st.columns([2, 1])

with col1:
    # Create radar chart
    categories = ['Technical', 'Quality', 'Delivery', 'Compliance']

    fig = go.Figure()

    colors = ['#8b5cf6', '#3b82f6', '#22c55e']

    for i, (idx, row) in enumerate(scores_df.iterrows()):
        values = [
            row['Technical Score'],
            row['Quality Score'],
            row['Delivery Score'],
            row['Compliance Score']
        ]
        values.append(values[0])  # Close the polygon

        # Parse color to rgba
        hex_color = colors[i].lstrip('#')
        r, g, b = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=row['Vendor'].split()[0],
            line_color=colors[i],
            fillcolor=f'rgba({r}, {g}, {b}, 0.2)'
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Score Summary**")
    st.dataframe(
        scores_df[['Vendor', 'Overall Score', 'Recommendation']],
        use_container_width=True,
        hide_index=True
    )

# CTQ Comparison Matrix
st.markdown("---")
st.subheader("📋 CTQ Comparison Matrix")

st.markdown("*Critical to Quality parameters evaluation across all vendors*")

# Display CTQ dataframe (styled version removed to avoid deprecated applymap)
st.dataframe(ctq_df, use_container_width=True, hide_index=True)

# Legend
st.markdown("""
<div style="display: flex; gap: 2rem; margin-top: 1rem;">
    <span style="color: #166534;">✓ = Compliant</span>
    <span style="color: #991b1b;">✗ = Non-Compliant</span>
</div>
""", unsafe_allow_html=True)

# Scoring Calculator
st.markdown("---")
st.subheader("🧮 Score Calculator")

st.markdown("Adjust weights to recalculate vendor scores:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    w_technical = st.slider("Technical Weight %", 0, 100, 40)
with col2:
    w_quality = st.slider("Quality Weight %", 0, 100, 25)
with col3:
    w_delivery = st.slider("Delivery Weight %", 0, 100, 20)
with col4:
    w_compliance = st.slider("Compliance Weight %", 0, 100, 15)

total_weight = w_technical + w_quality + w_delivery + w_compliance

if total_weight != 100:
    st.warning(f"⚠️ Weights should sum to 100%. Current total: {total_weight}%")
else:
    st.success("✅ Weights sum to 100%")

    # Recalculate scores
    recalc_df = scores_df.copy()
    recalc_df['Recalculated Score'] = (
        recalc_df['Technical Score'] * w_technical / 100 +
        recalc_df['Quality Score'] * w_quality / 100 +
        recalc_df['Delivery Score'] * w_delivery / 100 +
        recalc_df['Compliance Score'] * w_compliance / 100
    ).round(1)

    recalc_df = recalc_df.sort_values('Recalculated Score', ascending=False)

    st.markdown("**Recalculated Rankings:**")
    st.dataframe(
        recalc_df[['Vendor', 'Recalculated Score', 'Recommendation']],
        use_container_width=True,
        hide_index=True
    )

# Export
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        scores_df.to_excel(writer, sheet_name='Vendor Scores', index=False)
        ctq_df.to_excel(writer, sheet_name='CTQ Matrix', index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Export TBE Report",
        data=buffer,
        file_name="technical_evaluation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
