import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Evaluation | Procure-Pro-ISO", page_icon="🔬", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #5856d6 0%, #673ab7 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <h2 style="color: white; margin: 0;">🔬 Technical & Commercial Evaluation</h2>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["🔬 Technical Evaluation", "💰 Commercial Evaluation"])

with tab1:
    st.subheader("🏆 Vendor Scores")

    scores = pd.DataFrame({
        'Vendor': ['Precision Machinery', 'TechParts Intl', 'AutomaTech'],
        'Overall': [90.2, 88.7, 88.1],
        'Technical': [92, 90, 89],
        'Quality': [95, 88, 91],
        'Delivery': [88, 87, 85],
        'Compliance': [86, 90, 88],
        'Recommendation': ['Recommended', 'Recommended', 'Acceptable']
    })

    col1, col2, col3 = st.columns(3)
    for i, (col, v) in enumerate(zip([col1, col2, col3], scores.itertuples())):
        with col:
            badge = ["🥇", "🥈", "🥉"][i]
            color = "#22c55e" if v.Overall >= 90 else "#3b82f6" if v.Overall >= 85 else "#f97316"
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;">
                <h4>{v.Vendor}</h4>
                <p style="color: #666;">{badge} Rank #{i+1}</p>
                <h1 style="color: {color};">{v.Overall}</h1>
                <p style="color: #666;">Overall Score</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 1rem;">
                    <div style="background: #f3f4f6; padding: 0.5rem; border-radius: 4px;"><b>{v.Technical}</b><br><small>Technical</small></div>
                    <div style="background: #f3f4f6; padding: 0.5rem; border-radius: 4px;"><b>{v.Quality}</b><br><small>Quality</small></div>
                    <div style="background: #f3f4f6; padding: 0.5rem; border-radius: 4px;"><b>{v.Delivery}</b><br><small>Delivery</small></div>
                    <div style="background: #f3f4f6; padding: 0.5rem; border-radius: 4px;"><b>{v.Compliance}</b><br><small>Compliance</small></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar Chart
    st.subheader("📊 Comparison")
    categories = ['Technical', 'Quality', 'Delivery', 'Compliance']
    fig = go.Figure()
    colors = ['#8b5cf6', '#3b82f6', '#22c55e']
    for i, v in enumerate(scores.itertuples()):
        vals = [v.Technical, v.Quality, v.Delivery, v.Compliance, v.Technical]
        fig.add_trace(go.Scatterpolar(r=vals, theta=categories+[categories[0]], name=v.Vendor, line_color=colors[i], fill='toself', fillcolor=f'rgba{(int(colors[i][1:3],16), int(colors[i][3:5],16), int(colors[i][5:7],16), 0.2)}'))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # CTQ Matrix
    st.subheader("📋 CTQ Matrix")
    ctq = pd.DataFrame({
        'Parameter': ['Spindle Speed', 'Accuracy', 'Tool Capacity', 'Work Area', 'Power', 'Warranty'],
        'Weight': ['15%', '20%', '10%', '15%', '12%', '8%'],
        'Requirement': ['≥12000 RPM', '≤0.005mm', '≥24 tools', '≥1000mm', '≥30HP', '≥2 years'],
        'Precision': ['12000 ✓', '0.003mm ✓', '30 ✓', '1016mm ✓', '30HP ✓', '3yr ✓'],
        'TechParts': ['10000 ✗', '0.004mm ✓', '24 ✓', '1200mm ✓', '35HP ✓', '2yr ✓'],
        'AutomaTech': ['15000 ✓', '0.005mm ✓', '20 ✗', '1000mm ✓', '25HP ✗', '2yr ✓']
    })
    st.dataframe(ctq, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("💵 Price Comparison")

    pricing = pd.DataFrame({
        'Vendor': ['Precision Machinery', 'TechParts Intl', 'AutomaTech'],
        'Unit_Price': [89500, 92000, 87000],
        'Qty': [2, 2, 2],
        'Discount': [5, 8, 3],
        'Shipping': [4500, 6200, 8500],
        'Total': [185775, 189152, 190810],
        'Delivery': [45, 60, 90],
        'Warranty': ['3 years', '2 years', '2 years']
    })

    col1, col2, col3 = st.columns(3)
    for i, (col, v) in enumerate(zip([col1, col2, col3], pricing.itertuples())):
        with col:
            is_lowest = v.Total == pricing['Total'].min()
            badge = "🏆 Lowest" if is_lowest else ""
            border = "#22c55e" if is_lowest else "#e5e7eb"
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid {border};">
                <div style="display: flex; justify-content: space-between;">
                    <h4 style="margin: 0;">{v.Vendor}</h4>
                    <span style="color: #22c55e;">{badge}</span>
                </div>
                <div style="text-align: center; padding: 1rem; background: #f9fafb; border-radius: 8px; margin: 1rem 0;">
                    <h2 style="margin: 0;">${v.Total:,}</h2>
                    <small>Total Quote</small>
                </div>
                <p>Unit: ${v.Unit_Price:,} × {v.Qty}</p>
                <p>Discount: -{v.Discount}%</p>
                <p>Shipping: ${v.Shipping:,}</p>
                <hr>
                <p>⏱️ {v.Delivery} days | 🛡️ {v.Warranty}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TCO
    st.subheader("📊 5-Year TCO")
    tco = pd.DataFrame({
        'Category': ['Initial Purchase', 'Installation', 'Training', 'Maintenance (5yr)', 'Warranty Ext.', 'Spare Parts', 'TOTAL'],
        'Precision': [185775, 12000, 0, 45000, 0, 18000, 260775],
        'TechParts': [189152, 15000, 5000, 52000, 12000, 22000, 295152],
        'AutomaTech': [190810, 18000, 8000, 48000, 15000, 20000, 299810]
    })

    fig = go.Figure()
    tco_chart = tco[tco['Category'] != 'TOTAL']
    for col, color in zip(['Precision', 'TechParts', 'AutomaTech'], ['#8b5cf6', '#3b82f6', '#22c55e']):
        fig.add_trace(go.Bar(name=col, y=tco_chart['Category'], x=tco_chart[col], orientation='h', marker_color=color))
    fig.update_layout(barmode='group', height=350, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    display_tco = tco.copy()
    for col in ['Precision', 'TechParts', 'AutomaTech']:
        display_tco[col] = display_tco[col].apply(lambda x: f"${x:,}")
    st.dataframe(display_tco, use_container_width=True, hide_index=True)

    st.success("**Recommendation:** Precision Machinery Co. offers lowest 5-year TCO of $260,775")

# Export
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    scores.to_excel(writer, sheet_name='Technical', index=False)
    pricing.to_excel(writer, sheet_name='Commercial', index=False)
st.download_button("📥 Export Evaluation Report", buffer.getvalue(), "evaluation.xlsx")
