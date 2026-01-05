import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(page_title="Evaluation | Procure-Pro-ISO", page_icon="🔬", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #5856d6 0%, #673ab7 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <h2 style="color: white; margin: 0;">🔬 Technical & Commercial Evaluation</h2>
    <p style="color: rgba(255,255,255,0.8); margin: 0;">Vendor comparison with outlier detection</p>
</div>
""", unsafe_allow_html=True)

# Real Equipment Data from Procurement Tracker
@st.cache_data
def load_equipment_data():
    return pd.DataFrame({
        'Equipment': [
            'Climatic Chamber (TC/HF/DH) - 20 Module',
            'UV Chamber - 2 Module',
            'Power Supply for PID Test (20 channel)',
            'Steady State Simulator',
            'EL Tester for Module',
            'Flasher Xenon Based',
            'Hail Tester',
            'Salt Mist Chamber',
            'PCT Chamber',
            'Mechanical Load Tester',
            'Hot Spot Endurance Tester',
            'Bypass Diode Tester'
        ],
        'Category': [
            'Environmental', 'Environmental', 'Electrical', 'Electrical',
            'Quality', 'Quality', 'Mechanical', 'Environmental',
            'Environmental', 'Mechanical', 'Electrical', 'Electrical'
        ],
        'L1_Price': [285000, 45000, 125000, 180000, 95000, 220000, 340000, 78000, 156000, 89000, 67000, 45000],
        'L2_Price': [298000, 48500, 118000, 195000, 102000, 235000, 365000, 82000, 168000, 94000, 72000, 48000],
        'L3_Price': [275000, 42000, 132000, 175000, 88000, 215000, 328000, 75000, 148000, 86000, 65000, 43000],
        'L4_Price': [310000, 52000, 128000, 188000, 98000, 228000, 355000, 85000, 162000, 92000, 70000, 47000],
        'L5_Price': [265000, 41000, 135000, 172000, 91000, 208000, 318000, 72000, 145000, 84000, 63000, 42000],
        'L1_Tech': [92, 88, 95, 90, 87, 93, 89, 91, 88, 86, 90, 92],
        'L2_Tech': [88, 85, 92, 87, 84, 90, 86, 88, 85, 83, 87, 89],
        'L3_Tech': [94, 90, 93, 92, 89, 95, 91, 93, 90, 88, 92, 94],
        'L4_Tech': [86, 82, 88, 85, 81, 87, 84, 86, 83, 80, 85, 87],
        'L5_Tech': [90, 87, 91, 88, 86, 91, 88, 90, 87, 85, 89, 91],
        'L1_Delivery': [45, 30, 60, 45, 35, 50, 75, 40, 55, 40, 35, 30],
        'L2_Delivery': [60, 45, 75, 60, 50, 65, 90, 55, 70, 55, 50, 45],
        'L3_Delivery': [40, 25, 55, 40, 30, 45, 70, 35, 50, 35, 30, 25],
        'L4_Delivery': [75, 55, 85, 70, 60, 80, 100, 65, 85, 65, 60, 55],
        'L5_Delivery': [50, 35, 65, 50, 40, 55, 80, 45, 60, 45, 40, 35]
    })

# Supplier Classification
supplier_info = {
    'L1': {'name': 'Precision Machinery Co.', 'country': 'USA', 'color': '#3b82f6', 'tier': 'Tier 1'},
    'L2': {'name': 'TechParts International', 'country': 'Germany', 'color': '#8b5cf6', 'tier': 'Tier 1'},
    'L3': {'name': 'AutomaTech Solutions', 'country': 'Japan', 'color': '#22c55e', 'tier': 'Tier 1'},
    'L4': {'name': 'GlobalTools Ltd', 'country': 'China', 'color': '#f97316', 'tier': 'Tier 2'},
    'L5': {'name': 'Swiss Precision AG', 'country': 'Switzerland', 'color': '#ef4444', 'tier': 'Tier 1'}
}

equipment_df = load_equipment_data()

# Tabs
tab1, tab2, tab3 = st.tabs(["🔬 Technical Evaluation", "💰 Commercial Evaluation", "📊 Combined Analysis"])

# ============ TAB 1: TECHNICAL EVALUATION ============
with tab1:
    st.subheader("🏷️ Supplier Classification (L1-L5)")

    # Supplier cards
    cols = st.columns(5)
    for i, (code, info) in enumerate(supplier_info.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {info['color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: {info['color']}; margin: 0;">{code}</h4>
                <p style="margin: 0.25rem 0; font-weight: 500;">{info['name']}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">🌍 {info['country']} | {info['tier']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Technical Scores Summary
    st.subheader("📊 Technical Score Comparison")

    # Calculate average technical scores per supplier
    tech_cols = ['L1_Tech', 'L2_Tech', 'L3_Tech', 'L4_Tech', 'L5_Tech']
    tech_avgs = {col.replace('_Tech', ''): equipment_df[col].mean() for col in tech_cols}

    # Radar chart for technical scores
    tech_scores_df = pd.DataFrame({
        'Supplier': list(tech_avgs.keys()),
        'Avg Technical Score': list(tech_avgs.values()),
        'Color': [supplier_info[s]['color'] for s in tech_avgs.keys()]
    }).sort_values('Avg Technical Score', ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(tech_scores_df, x='Supplier', y='Avg Technical Score',
                     color='Supplier', color_discrete_map={s: supplier_info[s]['color'] for s in tech_avgs.keys()},
                     title="Average Technical Scores by Supplier")
        fig.update_layout(showlegend=False, height=350, yaxis_range=[0, 100])
        fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Min Threshold (85)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**🏆 Technical Rankings**")
        for i, row in tech_scores_df.iterrows():
            rank = tech_scores_df.index.get_loc(i) + 1
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][rank-1]
            st.markdown(f"{medal} **{row['Supplier']}**: {row['Avg Technical Score']:.1f}")

    # Detailed Technical Matrix
    st.subheader("📋 Technical Score Matrix by Equipment")
    tech_display = equipment_df[['Equipment', 'L1_Tech', 'L2_Tech', 'L3_Tech', 'L4_Tech', 'L5_Tech']].copy()
    tech_display.columns = ['Equipment', 'L1', 'L2', 'L3', 'L4', 'L5']
    st.dataframe(tech_display, use_container_width=True, hide_index=True)

# ============ TAB 2: COMMERCIAL EVALUATION ============
with tab2:
    st.subheader("💵 Price Comparison with Outlier Detection")

    # Select equipment for analysis
    selected_equipment = st.selectbox("Select Equipment for Analysis", equipment_df['Equipment'].tolist())
    eq_row = equipment_df[equipment_df['Equipment'] == selected_equipment].iloc[0]

    # Get prices for selected equipment
    prices = {
        'L1': eq_row['L1_Price'],
        'L2': eq_row['L2_Price'],
        'L3': eq_row['L3_Price'],
        'L4': eq_row['L4_Price'],
        'L5': eq_row['L5_Price']
    }

    price_df = pd.DataFrame({
        'Supplier': list(prices.keys()),
        'Price': list(prices.values()),
        'Supplier Name': [supplier_info[s]['name'] for s in prices.keys()],
        'Color': [supplier_info[s]['color'] for s in prices.keys()]
    })

    # Calculate statistics
    price_values = list(prices.values())
    mean_price = np.mean(price_values)
    std_price = np.std(price_values)
    q1 = np.percentile(price_values, 25)
    q3 = np.percentile(price_values, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Identify outliers
    price_df['Is_Outlier'] = (price_df['Price'] < lower_bound) | (price_df['Price'] > upper_bound)
    outliers = price_df[price_df['Is_Outlier']]
    non_outliers = price_df[~price_df['Is_Outlier']]

    col1, col2 = st.columns([2, 1])

    with col1:
        # Box plot for outlier detection
        fig = go.Figure()

        # Add box plot
        fig.add_trace(go.Box(
            y=price_df['Price'],
            name='Price Distribution',
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            marker=dict(
                color=[supplier_info[s]['color'] for s in price_df['Supplier']],
                size=12
            ),
            text=price_df['Supplier'],
            hovertemplate='%{text}: $%{y:,.0f}<extra></extra>'
        ))

        # Highlight outliers
        if len(outliers) > 0:
            fig.add_trace(go.Scatter(
                y=outliers['Price'],
                x=[0] * len(outliers),
                mode='markers',
                marker=dict(size=20, color='red', symbol='x'),
                name='Outliers',
                text=outliers['Supplier'],
                hovertemplate='OUTLIER - %{text}: $%{y:,.0f}<extra></extra>'
            ))

        fig.update_layout(
            title=f"Price Distribution: {selected_equipment}",
            yaxis_title="Price ($)",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**📈 Statistics**")
        st.metric("Mean Price", f"${mean_price:,.0f}")
        st.metric("Std Deviation", f"${std_price:,.0f}")
        st.metric("IQR Range", f"${lower_bound:,.0f} - ${upper_bound:,.0f}")

        if len(outliers) > 0:
            st.warning(f"⚠️ {len(outliers)} outlier(s) detected!")
            for _, row in outliers.iterrows():
                st.write(f"  • {row['Supplier']}: ${row['Price']:,}")
        else:
            st.success("✅ No outliers detected")

    # Outlier Removal Feature
    st.markdown("---")
    st.subheader("🔧 Outlier Removal Analysis")

    remove_outliers = st.checkbox("Remove outliers from analysis", value=False)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 BEFORE Outlier Removal**")
        st.write(f"• Suppliers: {len(price_df)}")
        st.write(f"• Mean: ${mean_price:,.0f}")
        st.write(f"• Min: ${min(price_values):,}")
        st.write(f"• Max: ${max(price_values):,}")
        st.write(f"• Range: ${max(price_values) - min(price_values):,}")

    with col2:
        if remove_outliers and len(outliers) > 0:
            clean_prices = non_outliers['Price'].tolist()
            clean_mean = np.mean(clean_prices)
            st.markdown("**📊 AFTER Outlier Removal**")
            st.write(f"• Suppliers: {len(non_outliers)}")
            st.write(f"• Mean: ${clean_mean:,.0f}")
            st.write(f"• Min: ${min(clean_prices):,}")
            st.write(f"• Max: ${max(clean_prices):,}")
            st.write(f"• Range: ${max(clean_prices) - min(clean_prices):,}")

            savings = mean_price - clean_mean
            st.success(f"💰 Adjusted mean saves ${abs(savings):,.0f} ({abs(savings)/mean_price*100:.1f}%)")
        else:
            st.markdown("**📊 AFTER Outlier Removal**")
            st.info("Enable checkbox above to see cleaned statistics")

    # Price Comparison Cards
    st.markdown("---")
    st.subheader("💳 Supplier Price Cards")

    cols = st.columns(5)
    min_price = price_df['Price'].min()

    for i, (_, row) in enumerate(price_df.iterrows()):
        with cols[i]:
            is_lowest = row['Price'] == min_price
            is_outlier = row['Is_Outlier']
            border_color = "#ef4444" if is_outlier else ("#22c55e" if is_lowest else "#e5e7eb")
            badge = "🏆 Lowest" if is_lowest else ("⚠️ Outlier" if is_outlier else "")

            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px;
                        border: 2px solid {border_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
                <h4 style="color: {supplier_info[row['Supplier']]['color']}; margin: 0;">{row['Supplier']}</h4>
                <p style="margin: 0.25rem 0; font-size: 0.75rem; color: #666;">{row['Supplier Name']}</p>
                <h2 style="margin: 0.5rem 0;">${row['Price']:,}</h2>
                <span style="font-size: 0.8rem;">{badge}</span>
            </div>
            """, unsafe_allow_html=True)

# ============ TAB 3: COMBINED ANALYSIS ============
with tab3:
    st.subheader("📊 Technical-Commercial Comparison Matrix")

    # Build comprehensive comparison table
    comparison_data = []

    for _, eq in equipment_df.iterrows():
        row_data = {'Equipment': eq['Equipment'], 'Category': eq['Category']}

        for supplier in ['L1', 'L2', 'L3', 'L4', 'L5']:
            price = eq[f'{supplier}_Price']
            tech = eq[f'{supplier}_Tech']
            delivery = eq[f'{supplier}_Delivery']

            # Calculate combined score (40% tech, 40% price normalized, 20% delivery)
            # Normalize price (lower is better, so invert)
            prices_list = [eq[f'{s}_Price'] for s in ['L1', 'L2', 'L3', 'L4', 'L5']]
            price_score = 100 - ((price - min(prices_list)) / (max(prices_list) - min(prices_list)) * 100) if max(prices_list) != min(prices_list) else 100

            # Normalize delivery (lower is better)
            deliveries = [eq[f'{s}_Delivery'] for s in ['L1', 'L2', 'L3', 'L4', 'L5']]
            delivery_score = 100 - ((delivery - min(deliveries)) / (max(deliveries) - min(deliveries)) * 100) if max(deliveries) != min(deliveries) else 100

            combined = tech * 0.4 + price_score * 0.4 + delivery_score * 0.2

            row_data[f'{supplier}_Price'] = price
            row_data[f'{supplier}_Tech'] = tech
            row_data[f'{supplier}_Combined'] = round(combined, 1)

        comparison_data.append(row_data)

    comparison_df = pd.DataFrame(comparison_data)

    # Display mode selector
    view_mode = st.radio("View Mode", ["Prices", "Technical Scores", "Combined Scores"], horizontal=True)

    if view_mode == "Prices":
        display_cols = ['Equipment', 'Category'] + [f'{s}_Price' for s in ['L1', 'L2', 'L3', 'L4', 'L5']]
        display_df = comparison_df[display_cols].copy()
        display_df.columns = ['Equipment', 'Category', 'L1', 'L2', 'L3', 'L4', 'L5']
        for col in ['L1', 'L2', 'L3', 'L4', 'L5']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,}")
    elif view_mode == "Technical Scores":
        display_cols = ['Equipment', 'Category'] + [f'{s}_Tech' for s in ['L1', 'L2', 'L3', 'L4', 'L5']]
        display_df = comparison_df[display_cols].copy()
        display_df.columns = ['Equipment', 'Category', 'L1', 'L2', 'L3', 'L4', 'L5']
    else:
        display_cols = ['Equipment', 'Category'] + [f'{s}_Combined' for s in ['L1', 'L2', 'L3', 'L4', 'L5']]
        display_df = comparison_df[display_cols].copy()
        display_df.columns = ['Equipment', 'Category', 'L1', 'L2', 'L3', 'L4', 'L5']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Winner Analysis
    st.markdown("---")
    st.subheader("🏆 Best Supplier by Equipment (Combined Score)")

    winners = []
    for _, eq in comparison_df.iterrows():
        combined_scores = {s: eq[f'{s}_Combined'] for s in ['L1', 'L2', 'L3', 'L4', 'L5']}
        best = max(combined_scores, key=combined_scores.get)
        winners.append({
            'Equipment': eq['Equipment'],
            'Best Supplier': best,
            'Supplier Name': supplier_info[best]['name'],
            'Combined Score': combined_scores[best],
            'Price': eq[f'{best}_Price'],
            'Tech Score': eq[f'{best}_Tech']
        })

    winners_df = pd.DataFrame(winners)
    winners_df['Price'] = winners_df['Price'].apply(lambda x: f"${x:,}")

    st.dataframe(winners_df, use_container_width=True, hide_index=True)

    # Summary by Supplier
    st.markdown("---")
    st.subheader("📈 Supplier Win Summary")

    win_counts = winners_df['Best Supplier'].value_counts()

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.pie(values=win_counts.values, names=win_counts.index,
                     color=win_counts.index,
                     color_discrete_map={s: supplier_info[s]['color'] for s in win_counts.index},
                     title="Equipment Awards by Supplier")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**🎯 Awards Count**")
        for supplier, count in win_counts.items():
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="width: 12px; height: 12px; background: {supplier_info[supplier]['color']};
                            border-radius: 50%; margin-right: 0.5rem;"></div>
                <span><b>{supplier}</b>: {count} equipment ({count/len(winners_df)*100:.0f}%)</span>
            </div>
            """, unsafe_allow_html=True)

# Export Section
st.markdown("---")
st.subheader("📥 Export Reports")

col1, col2, col3 = st.columns(3)

with col1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        equipment_df.to_excel(writer, sheet_name='Equipment Data', index=False)
        comparison_df.to_excel(writer, sheet_name='Comparison Matrix', index=False)
        pd.DataFrame(winners).to_excel(writer, sheet_name='Winners', index=False)
    st.download_button("📥 Full Evaluation Report", buffer.getvalue(), "evaluation_report.xlsx", type="primary")

with col2:
    tech_buffer = io.BytesIO()
    equipment_df[['Equipment', 'Category', 'L1_Tech', 'L2_Tech', 'L3_Tech', 'L4_Tech', 'L5_Tech']].to_excel(
        tech_buffer, index=False, engine='openpyxl')
    st.download_button("📥 Technical Scores", tech_buffer.getvalue(), "technical_scores.xlsx")

with col3:
    price_buffer = io.BytesIO()
    equipment_df[['Equipment', 'Category', 'L1_Price', 'L2_Price', 'L3_Price', 'L4_Price', 'L5_Price']].to_excel(
        price_buffer, index=False, engine='openpyxl')
    st.download_button("📥 Price Comparison", price_buffer.getvalue(), "price_comparison.xlsx")
