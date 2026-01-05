"""
Dashboard Page - Procure-Pro-ISO
Real-time KPIs and procurement overview
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('..')
from data.sample_data import (
    get_equipment_data, get_rfq_data, get_vendor_data,
    get_budget_trend_data, get_recent_activity
)

st.set_page_config(page_title="Dashboard | Procure-Pro-ISO", page_icon="📊", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">📊 Dashboard</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Overview of procurement activities</p>
</div>
""", unsafe_allow_html=True)

# Load data
equipment_df = get_equipment_data()
rfq_df = get_rfq_data()
vendor_df = get_vendor_data()
budget_df = get_budget_trend_data()
activities = get_recent_activity()

# KPI Cards
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3b82f6;">
        <p style="color: #666; margin: 0; font-size: 0.9rem;">Total Equipment</p>
        <h2 style="color: #1f2937; margin: 0.5rem 0;">12</h2>
        <p style="color: #22c55e; margin: 0; font-size: 0.8rem;">↑ +2 from last month</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #22c55e;">
        <p style="color: #666; margin: 0; font-size: 0.9rem;">Total Budget</p>
        <h2 style="color: #1f2937; margin: 0.5rem 0;">$1.8M</h2>
        <p style="color: #22c55e; margin: 0; font-size: 0.8rem;">↑ +5.2% from last month</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #f97316;">
        <p style="color: #666; margin: 0; font-size: 0.9rem;">Active RFQs</p>
        <h2 style="color: #1f2937; margin: 0.5rem 0;">3</h2>
        <p style="color: #ef4444; margin: 0; font-size: 0.8rem;">↓ -1 from last month</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #8b5cf6;">
        <p style="color: #666; margin: 0; font-size: 0.9rem;">Pending Approvals</p>
        <h2 style="color: #1f2937; margin: 0.5rem 0;">4</h2>
        <p style="color: #22c55e; margin: 0; font-size: 0.8rem;">↑ +2 from last month</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts Row
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💰 Budget vs Spending Trend")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=budget_df['Month'], y=budget_df['Budget'],
        mode='lines+markers', name='Budget',
        line=dict(color='#8b5cf6', width=3),
        fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=budget_df['Month'], y=budget_df['Spent'],
        mode='lines+markers', name='Spent',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Amount ($)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 RFQ Status")

    rfq_status = rfq_df['Status'].value_counts()
    colors = {'Open': '#3b82f6', 'Closed': '#22c55e', 'Draft': '#9ca3af', 'Awarded': '#8b5cf6'}

    fig = px.pie(
        values=rfq_status.values,
        names=rfq_status.index,
        color=rfq_status.index,
        color_discrete_map=colors,
        hole=0.4
    )
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    st.plotly_chart(fig, use_container_width=True)

# Bottom Row
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Active RFQs")

    active_rfqs = rfq_df[['RFQ Number', 'Title', 'Status', 'Estimated Value', 'Responses', 'Vendors Invited']].head(4)
    active_rfqs['Response Rate'] = (active_rfqs['Responses'] / active_rfqs['Vendors Invited'].replace(0, 1) * 100).round(0).astype(str) + '%'
    active_rfqs['Estimated Value'] = active_rfqs['Estimated Value'].apply(lambda x: f"${x:,.0f}")

    st.dataframe(
        active_rfqs[['RFQ Number', 'Title', 'Status', 'Estimated Value', 'Response Rate']],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("🔔 Recent Activity")

    for activity in activities[:5]:
        icon = {'rfq': '📝', 'approval': '✅', 'vendor': '👥', 'equipment': '📦', 'evaluation': '📊'}.get(activity['type'], '📌')
        st.markdown(f"""
        <div style="padding: 0.75rem; background: #f9fafb; border-radius: 8px; margin-bottom: 0.5rem;">
            <p style="margin: 0; font-size: 0.9rem;">{icon} {activity['message']}</p>
            <p style="margin: 0; font-size: 0.75rem; color: #9ca3af;">{activity['time']}</p>
        </div>
        """, unsafe_allow_html=True)

# Equipment by Category
st.subheader("📦 Equipment by Category")

category_counts = equipment_df['Category'].value_counts()
col1, col2, col3 = st.columns(3)

categories = [('Manufacturing', '#3b82f6'), ('Quality', '#22c55e'), ('Automation', '#f97316')]

for i, (cat, color) in enumerate(categories):
    count = category_counts.get(cat, 0)
    with [col1, col2, col3][i]:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
            <div style="width: 12px; height: 12px; background: {color}; border-radius: 50%;
                        display: inline-block; margin-bottom: 0.5rem;"></div>
            <h3 style="color: #1f2937; margin: 0;">{count}</h3>
            <p style="color: #666; margin: 0; font-size: 0.9rem;">{cat}</p>
        </div>
        """, unsafe_allow_html=True)
