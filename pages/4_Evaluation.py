"""
Technical & Commercial Evaluation Page - Procure-Pro-ISO
Comprehensive vendor analysis with box & whisker plots, L1-L5 classification, and outlier detection
"""

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
    <p style="color: rgba(255,255,255,0.8); margin: 0;">Vendor comparison with box & whisker plots and L1-L5 classification</p>
</div>
""", unsafe_allow_html=True)

# ============ REAL PV TESTING EQUIPMENT DATA ============
@st.cache_data
def load_equipment_data():
    """Load real PV testing equipment data with vendor quotes"""
    return pd.DataFrame({
        'Equipment': [
            'Climatic Chamber (TC/HF/DH) - 20 Module',
            'UV Chamber - 2 Module',
            'Climate Chamber DH - 20 Module',
            'Sun Simulator AAA Flasher',
            'Power Supply for TCHF (20 channel)',
            'SSS Steady State Simulator',
            'Hail Tester',
            'Dynamic Mechanical Load Test',
            'EL Tester for Module',
            'Thermal Imaging Camera',
            'Salt Mist Chamber',
            'PCT Chamber (Pressure Cooker Test)',
            'Bypass Diode Tester',
            'Hot Spot Endurance Tester',
            'Wet Leakage Current Tester',
            'Insulation Resistance Tester',
            'IV Curve Tracer',
            'Junction Box Pull Tester',
            'Ribbon Pull Tester',
            'Hi-Pot Tester'
        ],
        'Category': [
            'Environmental', 'Environmental', 'Environmental', 'Performance',
            'Electrical', 'Performance', 'Mechanical', 'Mechanical',
            'Quality', 'Quality', 'Environmental', 'Environmental',
            'Electrical', 'Electrical', 'Electrical', 'Electrical',
            'Performance', 'Mechanical', 'Mechanical', 'Electrical'
        ],
        'RIL_Budget': [
            320000, 55000, 285000, 450000, 145000, 220000, 380000, 125000,
            115000, 45000, 95000, 185000, 55000, 78000, 42000, 38000,
            85000, 32000, 28000, 48000
        ],
        # Vendor Quotes
        'Vendor_A': [
            285000, 48000, 268000, 425000, 138000, 205000, 355000, 118000,
            108000, 42000, 88000, 172000, 52000, 72000, 38000, 35000,
            78000, 29000, 25000, 44000
        ],
        'Vendor_B': [
            298000, 52000, 275000, 440000, 142000, 215000, 368000, 122000,
            112000, 44000, 92000, 178000, 54000, 75000, 40000, 36000,
            82000, 30000, 26000, 46000
        ],
        'Vendor_C': [
            275000, 45000, 258000, 410000, 132000, 198000, 342000, 115000,
            105000, 40000, 85000, 165000, 50000, 70000, 36000, 33000,
            75000, 28000, 24000, 42000
        ],
        'Vendor_D': [
            310000, 56000, 288000, 465000, 155000, 228000, 385000, 128000,
            118000, 46000, 98000, 188000, 58000, 80000, 44000, 40000,
            88000, 34000, 30000, 50000
        ],
        'Vendor_E': [
            265000, 42000, 248000, 395000, 128000, 190000, 328000, 110000,
            100000, 38000, 82000, 158000, 48000, 68000, 34000, 31000,
            72000, 26000, 22000, 40000
        ],
        # Technical Scores (out of 100)
        'Tech_A': [92, 88, 90, 95, 91, 89, 87, 90, 93, 88, 86, 91, 89, 87, 90, 88, 92, 85, 86, 89],
        'Tech_B': [88, 85, 87, 92, 88, 86, 84, 87, 90, 85, 83, 88, 86, 84, 87, 85, 89, 82, 83, 86],
        'Tech_C': [94, 90, 92, 97, 93, 91, 89, 92, 95, 90, 88, 93, 91, 89, 92, 90, 94, 87, 88, 91],
        'Tech_D': [86, 82, 84, 89, 85, 83, 81, 84, 87, 82, 80, 85, 83, 81, 84, 82, 86, 79, 80, 83],
        'Tech_E': [90, 87, 89, 94, 90, 88, 86, 89, 92, 87, 85, 90, 88, 86, 89, 87, 91, 84, 85, 88]
    })

# Vendor Information
VENDORS = {
    'Vendor_A': {'name': 'Weiss Technik GmbH', 'country': 'Germany', 'specialty': 'Environmental Testing'},
    'Vendor_B': {'name': 'Espec Corporation', 'country': 'Japan', 'specialty': 'Climate Chambers'},
    'Vendor_C': {'name': 'Pasan SA (Meyer Burger)', 'country': 'Switzerland', 'specialty': 'Solar Testing'},
    'Vendor_D': {'name': 'Berger Instruments', 'country': 'USA', 'specialty': 'PV Equipment'},
    'Vendor_E': {'name': 'Jinchen Machinery', 'country': 'China', 'specialty': 'Production Equipment'}
}

# L1-L5 Color Mapping (L1=Lowest=Green, L5=Highest=Red)
L_COLORS = {
    'L1': {'color': '#22c55e', 'bg': '#dcfce7', 'label': 'Lowest Quote'},
    'L2': {'color': '#84cc16', 'bg': '#ecfccb', 'label': '2nd Lowest'},
    'L3': {'color': '#eab308', 'bg': '#fef9c3', 'label': 'Middle'},
    'L4': {'color': '#f97316', 'bg': '#ffedd5', 'label': '4th'},
    'L5': {'color': '#ef4444', 'bg': '#fee2e2', 'label': 'Highest Quote'}
}

# Load data
equipment_df = load_equipment_data()
vendor_cols = ['Vendor_A', 'Vendor_B', 'Vendor_C', 'Vendor_D', 'Vendor_E']
tech_cols = ['Tech_A', 'Tech_B', 'Tech_C', 'Tech_D', 'Tech_E']

# ============ HELPER FUNCTIONS ============
def classify_vendors_l1_l5(prices):
    """Classify vendors as L1-L5 based on price ranking (L1=lowest)"""
    sorted_vendors = sorted(prices.items(), key=lambda x: x[1])
    classification = {}
    for i, (vendor, price) in enumerate(sorted_vendors):
        classification[vendor] = f'L{i+1}'
    return classification

def detect_outliers_iqr(values, multiplier=1.5):
    """Detect outliers using IQR method"""
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return lower, upper, [v for v in values if v < lower or v > upper]

def detect_outliers_std(values, num_std=2):
    """Detect outliers using standard deviation method"""
    mean = np.mean(values)
    std = np.std(values)
    lower = mean - num_std * std
    upper = mean + num_std * std
    return lower, upper, [v for v in values if v < lower or v > upper]

def detect_outliers_pct(values, pct=30):
    """Detect outliers using percentage deviation method"""
    mean = np.mean(values)
    threshold = mean * (pct / 100)
    lower = mean - threshold
    upper = mean + threshold
    return lower, upper, [v for v in values if v < lower or v > upper]

# ============ SIDEBAR ============
st.sidebar.header("🔧 Analysis Settings")

# Category filter
categories = ['All'] + sorted(equipment_df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Filter by Category", categories)

if selected_category != 'All':
    filtered_df = equipment_df[equipment_df['Category'] == selected_category].copy()
else:
    filtered_df = equipment_df.copy()

# Outlier detection settings
st.sidebar.subheader("Outlier Detection")
outlier_method = st.sidebar.selectbox(
    "Method",
    ["IQR (1.5x)", "IQR (2.0x)", "IQR (3.0x)", "Std Dev (2σ)", "Std Dev (3σ)", "% Deviation (30%)", "% Deviation (50%)"]
)

manual_outlier_removal = st.sidebar.checkbox("Enable manual outlier removal", value=False)

# ============ TABS ============
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Box & Whisker Analysis",
    "🔬 Technical Evaluation",
    "💰 Commercial Evaluation",
    "📋 Combined Analysis"
])

# ============ TAB 1: BOX & WHISKER PLOTS ============
with tab1:
    st.subheader("📊 Box & Whisker Plot - Price Distribution by Equipment")

    # L1-L5 Legend
    st.markdown("**L1-L5 Classification Legend:**")
    legend_cols = st.columns(5)
    for i, (level, info) in enumerate(L_COLORS.items()):
        with legend_cols[i]:
            st.markdown(f"""
            <div style="background: {info['bg']}; padding: 0.5rem; border-radius: 6px;
                        border-left: 4px solid {info['color']}; text-align: center;">
                <strong style="color: {info['color']};">{level}</strong>
                <span style="font-size: 0.7rem; color: #666;"> - {info['label']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Equipment selector
    selected_equipment = st.selectbox("Select Equipment for Detailed Analysis", filtered_df['Equipment'].tolist())
    eq_row = filtered_df[filtered_df['Equipment'] == selected_equipment].iloc[0]

    # Get prices
    prices = {col: eq_row[col] for col in vendor_cols}
    budget = eq_row['RIL_Budget']
    price_values = list(prices.values())

    # Calculate statistics
    mean_price = np.mean(price_values)
    median_price = np.median(price_values)
    std_price = np.std(price_values)
    q1 = np.percentile(price_values, 25)
    q3 = np.percentile(price_values, 75)
    iqr = q3 - q1

    # Detect outliers based on method
    if "IQR (1.5x)" in outlier_method:
        lower_bound, upper_bound, outlier_values = detect_outliers_iqr(price_values, 1.5)
    elif "IQR (2.0x)" in outlier_method:
        lower_bound, upper_bound, outlier_values = detect_outliers_iqr(price_values, 2.0)
    elif "IQR (3.0x)" in outlier_method:
        lower_bound, upper_bound, outlier_values = detect_outliers_iqr(price_values, 3.0)
    elif "Std Dev (2σ)" in outlier_method:
        lower_bound, upper_bound, outlier_values = detect_outliers_std(price_values, 2)
    elif "Std Dev (3σ)" in outlier_method:
        lower_bound, upper_bound, outlier_values = detect_outliers_std(price_values, 3)
    elif "30%" in outlier_method:
        lower_bound, upper_bound, outlier_values = detect_outliers_pct(price_values, 30)
    else:
        lower_bound, upper_bound, outlier_values = detect_outliers_pct(price_values, 50)

    # Classify vendors
    classification = classify_vendors_l1_l5(prices)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Create box plot
        fig = go.Figure()

        # Box plot (without text/hovertemplate which can cause issues)
        fig.add_trace(go.Box(
            y=price_values,
            name='Price Distribution',
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            marker=dict(
                color=[L_COLORS[classification[v]]['color'] for v in vendor_cols],
                size=14,
                line=dict(width=2, color='white')
            ),
            line=dict(color='#5856d6', width=2),
            fillcolor='rgba(88, 86, 214, 0.3)',
            hoverinfo='y'
        ))

        # Add individual vendor points with proper labels
        for vendor in vendor_cols:
            price = prices[vendor]
            level = classification[vendor]
            fig.add_trace(go.Scatter(
                x=[0],
                y=[price],
                mode='markers',
                marker=dict(
                    color=L_COLORS[level]['color'],
                    size=16,
                    line=dict(width=2, color='white')
                ),
                name=f"{level}: {VENDORS[vendor]['name'][:15]}",
                hovertemplate=f"{VENDORS[vendor]['name']}<br>{level}: ${price:,}<extra></extra>",
                showlegend=False
            ))

        # RIL Budget line
        fig.add_hline(
            y=budget,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"RIL Budget: ${budget:,}",
            annotation_position="right"
        )

        # Min/Max labels
        min_vendor = min(prices, key=prices.get)
        max_vendor = max(prices, key=prices.get)

        fig.add_trace(go.Scatter(
            x=[0.3], y=[min(price_values)],
            mode='markers+text',
            marker=dict(size=18, color='#22c55e', symbol='star'),
            text=[f"L1: {VENDORS[min_vendor]['name'][:12]}"],
            textposition='middle right',
            name='L1 (Lowest)',
            hovertemplate=f"L1 Lowest: ${min(price_values):,}<br>{VENDORS[min_vendor]['name']}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=[0.3], y=[max(price_values)],
            mode='markers+text',
            marker=dict(size=18, color='#ef4444', symbol='x'),
            text=[f"L5: {VENDORS[max_vendor]['name'][:12]}"],
            textposition='middle right',
            name='L5 (Highest)',
            hovertemplate=f"L5 Highest: ${max(price_values):,}<br>{VENDORS[max_vendor]['name']}<extra></extra>"
        ))

        # Mark outliers
        outlier_vendors = [v for v, p in prices.items() if p in outlier_values]
        if outlier_vendors:
            fig.add_trace(go.Scatter(
                x=[0] * len(outlier_vendors),
                y=[prices[v] for v in outlier_vendors],
                mode='markers',
                marker=dict(size=25, color='red', symbol='circle-open', line=dict(width=3)),
                name='Outliers',
                hovertemplate='OUTLIER: $%{y:,.0f}<extra></extra>'
            ))

        fig.update_layout(
            title=f"<b>{selected_equipment}</b>",
            yaxis_title="Price (USD)",
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(tickformat="$,.0f")
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**📈 Statistics**")

        stats_data = [
            ("Mean", mean_price, "#1f2937"),
            ("Median", median_price, "#1f2937"),
            ("Std Dev", std_price, "#1f2937"),
            ("Q1 (25%)", q1, "#1f2937"),
            ("Q3 (75%)", q3, "#1f2937"),
            ("IQR", iqr, "#1f2937"),
            ("Min (L1)", min(price_values), "#22c55e"),
            ("Max (L5)", max(price_values), "#ef4444"),
            ("RIL Budget", budget, "#ef4444")
        ]

        for label, value, color in stats_data:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.4rem;
                        background: #f9fafb; border-radius: 4px; margin-bottom: 0.2rem;">
                <span style="color: #666; font-size: 0.85rem;">{label}</span>
                <span style="font-weight: bold; color: {color}; font-size: 0.85rem;">${value:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

        # Budget comparison
        avg_vs_budget = ((mean_price - budget) / budget) * 100
        st.markdown(f"""
        <div style="padding: 1rem; background: {'#dcfce7' if avg_vs_budget < 0 else '#fee2e2'};
                    border-radius: 8px; margin-top: 1rem; text-align: center;">
            <p style="margin: 0; color: #666; font-size: 0.8rem;">Avg vs Budget</p>
            <h3 style="margin: 0; color: {'#22c55e' if avg_vs_budget < 0 else '#ef4444'};">
                {'Under' if avg_vs_budget < 0 else 'Over'} {abs(avg_vs_budget):.1f}%
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Outlier detection result
        if outlier_values:
            st.warning(f"⚠️ {len(outlier_values)} outlier(s) detected!")
            for ov in outlier_vendors:
                st.write(f"• {VENDORS[ov]['name']}: ${prices[ov]:,}")
        else:
            st.success("✅ No outliers detected")

    # Before/After Outlier Removal
    st.markdown("---")
    st.subheader("🔧 Outlier Removal Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 BEFORE Outlier Removal**")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | Vendors | {len(price_values)} |
        | Mean | ${mean_price:,.0f} |
        | Median | ${median_price:,.0f} |
        | Std Dev | ${std_price:,.0f} |
        | Range | ${max(price_values) - min(price_values):,} |
        """)

    with col2:
        if outlier_values and manual_outlier_removal:
            clean_values = [p for p in price_values if p not in outlier_values]
            if clean_values:
                st.markdown("**📊 AFTER Outlier Removal**")
                st.markdown(f"""
                | Metric | Value |
                |--------|-------|
                | Vendors | {len(clean_values)} |
                | Mean | ${np.mean(clean_values):,.0f} |
                | Median | ${np.median(clean_values):,.0f} |
                | Std Dev | ${np.std(clean_values):,.0f} |
                | Range | ${max(clean_values) - min(clean_values):,} |
                """)

                savings = mean_price - np.mean(clean_values)
                st.success(f"💰 Mean adjusted by ${abs(savings):,.0f} ({abs(savings)/mean_price*100:.1f}%)")
        else:
            st.markdown("**📊 AFTER Outlier Removal**")
            st.info("Enable manual removal in sidebar to see cleaned statistics")

# ============ TAB 2: TECHNICAL EVALUATION ============
with tab2:
    st.subheader("🔬 Technical Score Comparison")

    # Technical scores summary
    tech_avgs = {}
    for i, vendor in enumerate(vendor_cols):
        tech_col = tech_cols[i]
        tech_avgs[VENDORS[vendor]['name']] = filtered_df[tech_col].mean()

    tech_df = pd.DataFrame({
        'Vendor': list(tech_avgs.keys()),
        'Avg Score': list(tech_avgs.values())
    }).sort_values('Avg Score', ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            tech_df, x='Vendor', y='Avg Score',
            color='Avg Score',
            color_continuous_scale=['#ef4444', '#eab308', '#22c55e'],
            title="Average Technical Score by Vendor"
        )
        fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Min Threshold (85)")
        fig.update_layout(height=400, yaxis_range=[0, 100], showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**🏆 Technical Rankings**")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, (_, row) in enumerate(tech_df.iterrows()):
            st.markdown(f"{medals[i]} **{row['Vendor'][:20]}**: {row['Avg Score']:.1f}")

    # Technical matrix
    st.markdown("---")
    st.subheader("📋 Technical Score Matrix")

    tech_display = filtered_df[['Equipment', 'Category'] + tech_cols].copy()
    tech_display.columns = ['Equipment', 'Category'] + [VENDORS[v]['name'][:15] for v in vendor_cols]
    st.dataframe(tech_display, use_container_width=True, hide_index=True)

# ============ TAB 3: COMMERCIAL EVALUATION ============
with tab3:
    st.subheader("💰 Commercial Evaluation - L1-L5 Classification")

    # Build L1-L5 cards for each equipment
    for idx, row in filtered_df.head(8).iterrows():
        eq_name = row['Equipment']
        budget = row['RIL_Budget']
        prices = {col: row[col] for col in vendor_cols}

        sorted_vendors = sorted(prices.items(), key=lambda x: x[1])

        with st.expander(f"📦 {eq_name}", expanded=idx < 2):
            cols = st.columns(6)

            for i, (vendor, price) in enumerate(sorted_vendors):
                level = f'L{i+1}'
                vs_budget = ((price - budget) / budget) * 100

                with cols[i]:
                    st.markdown(f"""
                    <div style="background: {L_COLORS[level]['bg']}; padding: 0.75rem; border-radius: 8px;
                                border: 2px solid {L_COLORS[level]['color']}; text-align: center; min-height: 140px;">
                        <h4 style="color: {L_COLORS[level]['color']}; margin: 0;">{level}</h4>
                        <p style="margin: 0.2rem 0; font-size: 0.65rem; color: #666;">{VENDORS[vendor]['name'][:16]}</p>
                        <h3 style="margin: 0.3rem 0; font-size: 1.1rem;">${price:,}</h3>
                        <p style="margin: 0; font-size: 0.7rem; color: {'#22c55e' if vs_budget < 0 else '#ef4444'};">
                            {'✅' if vs_budget < 0 else '⚠️'} {vs_budget:+.1f}%
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            # Average card
            with cols[5]:
                avg_price = np.mean(list(prices.values()))
                st.markdown(f"""
                <div style="background: #f3e8ff; padding: 0.75rem; border-radius: 8px;
                            border: 2px solid #8b5cf6; text-align: center; min-height: 140px;">
                    <h4 style="color: #8b5cf6; margin: 0;">AVG</h4>
                    <p style="margin: 0.2rem 0; font-size: 0.65rem; color: #666;">Average</p>
                    <h3 style="margin: 0.3rem 0; font-size: 1.1rem;">${avg_price:,.0f}</h3>
                    <p style="margin: 0; font-size: 0.7rem;">Budget: ${budget:,}</p>
                </div>
                """, unsafe_allow_html=True)

# ============ TAB 4: COMBINED ANALYSIS ============
with tab4:
    st.subheader("📋 Technical-Commercial Comparison Table")

    # Build comparison table
    comparison_data = []

    for idx, row in filtered_df.iterrows():
        eq_name = row['Equipment']
        category = row['Category']
        budget = row['RIL_Budget']
        prices = {col: row[col] for col in vendor_cols}

        sorted_vendors = sorted(prices.items(), key=lambda x: x[1])

        comp_row = {'Equipment': eq_name, 'Category': category}

        for i, (vendor, price) in enumerate(sorted_vendors):
            level = f'L{i+1}'
            comp_row[f'{level} Vendor'] = VENDORS[vendor]['name'][:18]
            comp_row[f'{level} Quote'] = price

        comp_row['Average'] = np.mean(list(prices.values()))
        comp_row['Budget'] = budget
        comp_row['Deviation %'] = ((comp_row['Average'] - budget) / budget) * 100

        comparison_data.append(comp_row)

    comparison_df = pd.DataFrame(comparison_data)

    # View mode
    view_mode = st.radio("View Mode", ["Full Table", "Quotes Only", "Summary"], horizontal=True)

    if view_mode == "Full Table":
        display_df = comparison_df.copy()
    elif view_mode == "Quotes Only":
        display_df = comparison_df[['Equipment', 'L1 Quote', 'L2 Quote', 'L3 Quote', 'L4 Quote', 'L5 Quote', 'Average', 'Budget', 'Deviation %']].copy()
    else:
        display_df = comparison_df[['Equipment', 'L1 Quote', 'L5 Quote', 'Average', 'Budget', 'Deviation %']].copy()

    # Format columns
    for col in display_df.columns:
        if 'Quote' in col or col in ['Average', 'Budget']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")

    if 'Deviation %' in display_df.columns:
        display_df['Deviation %'] = comparison_df['Deviation %'].apply(lambda x: f"{x:+.1f}%")

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    total_budget = filtered_df['RIL_Budget'].sum()
    total_l1 = sum(filtered_df[vendor_cols].min(axis=1))
    total_avg = sum(filtered_df[vendor_cols].mean(axis=1))
    total_l5 = sum(filtered_df[vendor_cols].max(axis=1))

    with col1:
        st.metric("Total Budget", f"${total_budget:,.0f}")
    with col2:
        st.metric("Total L1", f"${total_l1:,.0f}", f"{((total_l1-total_budget)/total_budget)*100:+.1f}%")
    with col3:
        st.metric("Total Avg", f"${total_avg:,.0f}", f"{((total_avg-total_budget)/total_budget)*100:+.1f}%")
    with col4:
        st.metric("Total L5", f"${total_l5:,.0f}", f"{((total_l5-total_budget)/total_budget)*100:+.1f}%")

# ============ EXPORT SECTION ============
st.markdown("---")
st.subheader("📥 Export Reports")

col1, col2, col3 = st.columns(3)

with col1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, sheet_name='Equipment Data', index=False)
        comparison_df.to_excel(writer, sheet_name='L1-L5 Comparison', index=False)

    st.download_button(
        "📥 Full Evaluation Report",
        buffer.getvalue(),
        "evaluation_report.xlsx",
        type="primary"
    )

with col2:
    price_buffer = io.BytesIO()
    filtered_df[['Equipment', 'Category', 'RIL_Budget'] + vendor_cols].to_excel(
        price_buffer, index=False, engine='openpyxl'
    )
    st.download_button("📥 Price Data", price_buffer.getvalue(), "price_data.xlsx")

with col3:
    tech_buffer = io.BytesIO()
    filtered_df[['Equipment', 'Category'] + tech_cols].to_excel(
        tech_buffer, index=False, engine='openpyxl'
    )
    st.download_button("📥 Technical Scores", tech_buffer.getvalue(), "technical_scores.xlsx")
