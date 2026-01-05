"""
Commercial Evaluation Page - Procure-Pro-ISO
Comprehensive vendor price analysis with outlier detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.set_page_config(page_title="Commercial Evaluation | Procure-Pro-ISO", page_icon="💰", layout="wide")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(88, 86, 214, 1) 0%, rgba(103, 58, 183, 1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">💰 Commercial Evaluation</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Vendor price comparison with outlier detection & L1-L5 classification</p>
</div>
""", unsafe_allow_html=True)

# ============ REAL PV TESTING EQUIPMENT DATA ============
@st.cache_data
def load_pv_equipment_data():
    """Load real PV testing equipment data with vendor quotes"""
    equipment_data = {
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
            'Hi-Pot Tester',
            'Ground Continuity Tester',
            'Solar Cell Sorter',
            'Laminator - 2 Module',
            'Auto Stringer Machine',
            'Tabber & Stringer',
            'Glass Washer Machine',
            'Cell Crack Detector',
            'Module Frame Crimping Machine',
            'Junction Box Potting Machine',
            'Label Printer System'
        ],
        'Category': [
            'Environmental', 'Environmental', 'Environmental', 'Performance',
            'Electrical', 'Performance', 'Mechanical', 'Mechanical',
            'Quality', 'Quality', 'Environmental', 'Environmental',
            'Electrical', 'Electrical', 'Electrical', 'Electrical',
            'Performance', 'Mechanical', 'Mechanical', 'Electrical',
            'Electrical', 'Production', 'Production', 'Production',
            'Production', 'Production', 'Quality', 'Production',
            'Production', 'Production'
        ],
        'RIL_Budget': [
            320000, 55000, 285000, 450000, 145000, 220000, 380000, 125000,
            115000, 45000, 95000, 185000, 55000, 78000, 42000, 38000,
            85000, 32000, 28000, 48000, 35000, 520000, 280000, 650000,
            180000, 95000, 125000, 85000, 72000, 25000
        ],
        # Vendor Quotes (5 vendors per equipment)
        'Vendor_A': [
            285000, 48000, 268000, 425000, 138000, 205000, 355000, 118000,
            108000, 42000, 88000, 172000, 52000, 72000, 38000, 35000,
            78000, 29000, 25000, 44000, 32000, 495000, 265000, 620000,
            168000, 88000, 118000, 78000, 68000, 22000
        ],
        'Vendor_B': [
            298000, 52000, 275000, 440000, 142000, 215000, 368000, 122000,
            112000, 44000, 92000, 178000, 54000, 75000, 40000, 36000,
            82000, 30000, 26000, 46000, 33000, 510000, 272000, 635000,
            175000, 92000, 122000, 82000, 70000, 23000
        ],
        'Vendor_C': [
            275000, 45000, 258000, 410000, 132000, 198000, 342000, 115000,
            105000, 40000, 85000, 165000, 50000, 70000, 36000, 33000,
            75000, 28000, 24000, 42000, 30000, 480000, 258000, 605000,
            162000, 85000, 112000, 75000, 65000, 21000
        ],
        'Vendor_D': [
            310000, 56000, 288000, 465000, 155000, 228000, 385000, 128000,
            118000, 46000, 98000, 188000, 58000, 80000, 44000, 40000,
            88000, 34000, 30000, 50000, 36000, 535000, 285000, 665000,
            185000, 98000, 130000, 88000, 75000, 26000
        ],
        'Vendor_E': [
            265000, 42000, 248000, 395000, 128000, 190000, 328000, 110000,
            100000, 38000, 82000, 158000, 48000, 68000, 34000, 31000,
            72000, 26000, 22000, 40000, 28000, 465000, 248000, 585000,
            155000, 82000, 108000, 72000, 62000, 20000
        ]
    }
    return pd.DataFrame(equipment_data)

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
    'L1': {'color': '#22c55e', 'bg': '#dcfce7', 'label': 'Lowest'},
    'L2': {'color': '#84cc16', 'bg': '#ecfccb', 'label': '2nd Lowest'},
    'L3': {'color': '#eab308', 'bg': '#fef9c3', 'label': '3rd'},
    'L4': {'color': '#f97316', 'bg': '#ffedd5', 'label': '4th'},
    'L5': {'color': '#ef4444', 'bg': '#fee2e2', 'label': 'Highest'}
}

# Load data
equipment_df = load_pv_equipment_data()
vendor_cols = ['Vendor_A', 'Vendor_B', 'Vendor_C', 'Vendor_D', 'Vendor_E']

# ============ HELPER FUNCTIONS ============
def classify_vendors_l1_l5(prices):
    """Classify vendors as L1-L5 based on price ranking"""
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

def detect_outliers_percentage(values, pct_threshold=30):
    """Detect outliers using percentage deviation from mean"""
    mean = np.mean(values)
    threshold = mean * (pct_threshold / 100)
    lower = mean - threshold
    upper = mean + threshold
    return lower, upper, [v for v in values if v < lower or v > upper]

# ============ SIDEBAR FILTERS ============
st.sidebar.header("🔧 Analysis Settings")

# Equipment filter
categories = ['All'] + sorted(equipment_df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Filter by Category", categories)

if selected_category != 'All':
    filtered_df = equipment_df[equipment_df['Category'] == selected_category].copy()
else:
    filtered_df = equipment_df.copy()

# Outlier detection method
st.sidebar.subheader("Outlier Detection")
outlier_method = st.sidebar.selectbox(
    "Detection Method",
    ["IQR (Interquartile Range)", "Standard Deviation", "Percentage Deviation"]
)

if outlier_method == "IQR (Interquartile Range)":
    iqr_multiplier = st.sidebar.select_slider("IQR Multiplier", options=[1.0, 1.5, 2.0, 2.5, 3.0], value=1.5)
elif outlier_method == "Standard Deviation":
    std_multiplier = st.sidebar.select_slider("Std Dev Multiplier", options=[1.0, 1.5, 2.0, 2.5, 3.0], value=2.0)
else:
    pct_threshold = st.sidebar.slider("Deviation Threshold (%)", 10, 50, 30)

# Manual outlier removal
st.sidebar.subheader("Manual Outlier Removal")
manual_remove = st.sidebar.checkbox("Enable manual removal", value=False)

# ============ TAB LAYOUT ============
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Box & Whisker Analysis",
    "🏷️ L1-L5 Classification",
    "📋 Comparison Table",
    "📈 Summary & Export"
])

# ============ TAB 1: BOX & WHISKER ANALYSIS ============
with tab1:
    st.subheader("📊 Box & Whisker Plot - Vendor Price Distribution")

    # Select equipment for detailed analysis
    selected_equipment = st.selectbox(
        "Select Equipment for Detailed Analysis",
        filtered_df['Equipment'].tolist()
    )

    eq_row = filtered_df[filtered_df['Equipment'] == selected_equipment].iloc[0]

    # Get prices for selected equipment
    prices = {col: eq_row[col] for col in vendor_cols}
    budget = eq_row['RIL_Budget']

    # Calculate statistics
    price_values = list(prices.values())
    mean_price = np.mean(price_values)
    median_price = np.median(price_values)
    std_price = np.std(price_values)
    min_price = min(price_values)
    max_price = max(price_values)
    q1 = np.percentile(price_values, 25)
    q3 = np.percentile(price_values, 75)
    iqr = q3 - q1

    # Detect outliers based on selected method
    if outlier_method == "IQR (Interquartile Range)":
        lower_bound, upper_bound, outlier_values = detect_outliers_iqr(price_values, iqr_multiplier)
    elif outlier_method == "Standard Deviation":
        lower_bound, upper_bound, outlier_values = detect_outliers_std(price_values, std_multiplier)
    else:
        lower_bound, upper_bound, outlier_values = detect_outliers_percentage(price_values, pct_threshold)

    # Classify vendors L1-L5
    classification = classify_vendors_l1_l5(prices)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Create box and whisker plot
        fig = go.Figure()

        # Add box plot (without text/hovertemplate which can cause issues)
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
        for i, vendor in enumerate(vendor_cols):
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

        # Add RIL Budget line
        fig.add_hline(
            y=budget,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"RIL Budget: ${budget:,}",
            annotation_position="right"
        )

        # Add scatter points for min/max with vendor labels
        min_vendor = min(prices, key=prices.get)
        max_vendor = max(prices, key=prices.get)

        fig.add_trace(go.Scatter(
            x=[0.3], y=[min_price],
            mode='markers+text',
            marker=dict(size=20, color='#22c55e', symbol='star'),
            text=[f"L1: {VENDORS[min_vendor]['name'][:15]}"],
            textposition='middle right',
            name='Lowest (L1)',
            hovertemplate=f"Lowest: ${min_price:,}<br>{VENDORS[min_vendor]['name']}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=[0.3], y=[max_price],
            mode='markers+text',
            marker=dict(size=20, color='#ef4444', symbol='x'),
            text=[f"L5: {VENDORS[max_vendor]['name'][:15]}"],
            textposition='middle right',
            name='Highest (L5)',
            hovertemplate=f"Highest: ${max_price:,}<br>{VENDORS[max_vendor]['name']}<extra></extra>"
        ))

        # Highlight outliers
        outlier_vendors = [v for v, p in prices.items() if p in outlier_values]
        if outlier_vendors:
            outlier_prices = [prices[v] for v in outlier_vendors]
            fig.add_trace(go.Scatter(
                x=[0] * len(outlier_vendors),
                y=outlier_prices,
                mode='markers',
                marker=dict(size=25, color='red', symbol='circle-open', line=dict(width=3)),
                name='Outliers',
                hovertemplate='OUTLIER: $%{y:,.0f}<extra></extra>'
            ))

        fig.update_layout(
            title=f"<b>Price Distribution: {selected_equipment}</b>",
            yaxis_title="Price (USD)",
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(tickformat="$,.0f")
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**📈 Statistics**")

        # Statistics cards
        stats = [
            ("Mean", mean_price),
            ("Median", median_price),
            ("Std Dev", std_price),
            ("Min (L1)", min_price),
            ("Max (L5)", max_price),
            ("Q1 (25%)", q1),
            ("Q3 (75%)", q3),
            ("IQR", iqr),
            ("RIL Budget", budget)
        ]

        for label, value in stats:
            color = "#ef4444" if label == "RIL Budget" else "#1f2937"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 0.5rem;
                        background: #f9fafb; border-radius: 4px; margin-bottom: 0.25rem;">
                <span style="color: #666;">{label}</span>
                <span style="font-weight: bold; color: {color};">${value:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

        # Budget deviation
        avg_vs_budget = ((mean_price - budget) / budget) * 100
        deviation_color = "#22c55e" if avg_vs_budget < 0 else "#ef4444"
        deviation_text = "Under" if avg_vs_budget < 0 else "Over"

        st.markdown(f"""
        <div style="padding: 1rem; background: {'#dcfce7' if avg_vs_budget < 0 else '#fee2e2'};
                    border-radius: 8px; margin-top: 1rem; text-align: center;">
            <p style="margin: 0; color: #666;">Avg vs Budget</p>
            <h3 style="margin: 0; color: {deviation_color};">{deviation_text} {abs(avg_vs_budget):.1f}%</h3>
        </div>
        """, unsafe_allow_html=True)

        # Outlier alert
        if outlier_values:
            st.warning(f"⚠️ {len(outlier_values)} outlier(s) detected!")
            for ov in outlier_vendors:
                st.write(f"• {VENDORS[ov]['name']}: ${prices[ov]:,}")
        else:
            st.success("✅ No outliers detected")

    # Outlier Removal Analysis
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
        | Min | ${min_price:,} |
        | Max | ${max_price:,} |
        | Range | ${max_price - min_price:,} |
        """)

    with col2:
        if outlier_values and (manual_remove or len(outlier_values) > 0):
            clean_values = [p for p in price_values if p not in outlier_values]
            if clean_values:
                clean_mean = np.mean(clean_values)
                clean_median = np.median(clean_values)
                clean_std = np.std(clean_values)

                st.markdown("**📊 AFTER Outlier Removal**")
                st.markdown(f"""
                | Metric | Value |
                |--------|-------|
                | Vendors | {len(clean_values)} |
                | Mean | ${clean_mean:,.0f} |
                | Median | ${clean_median:,.0f} |
                | Std Dev | ${clean_std:,.0f} |
                | Min | ${min(clean_values):,} |
                | Max | ${max(clean_values):,} |
                | Range | ${max(clean_values) - min(clean_values):,} |
                """)

                savings = mean_price - clean_mean
                st.success(f"💰 Mean adjusted by ${abs(savings):,.0f} ({abs(savings)/mean_price*100:.1f}%)")
            else:
                st.warning("All values are outliers!")
        else:
            st.markdown("**📊 AFTER Outlier Removal**")
            st.info("No outliers to remove or manual removal not enabled")

# ============ TAB 2: L1-L5 CLASSIFICATION ============
with tab2:
    st.subheader("🏷️ Vendor Classification (L1-L5)")

    # Legend
    st.markdown("**Classification Legend:**")
    legend_cols = st.columns(5)
    for i, (level, info) in enumerate(L_COLORS.items()):
        with legend_cols[i]:
            st.markdown(f"""
            <div style="background: {info['bg']}; padding: 0.75rem; border-radius: 8px;
                        border-left: 4px solid {info['color']}; text-align: center;">
                <strong style="color: {info['color']};">{level}</strong>
                <p style="margin: 0; font-size: 0.75rem; color: #666;">{info['label']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Build L1-L5 classification table
    classification_data = []

    for idx, row in filtered_df.iterrows():
        eq_name = row['Equipment']
        prices = {col: row[col] for col in vendor_cols}
        budget = row['RIL_Budget']

        # Sort vendors by price
        sorted_vendors = sorted(prices.items(), key=lambda x: x[1])

        row_data = {'Equipment': eq_name, 'Budget': budget}

        for i, (vendor, price) in enumerate(sorted_vendors):
            level = f'L{i+1}'
            row_data[f'{level}_Vendor'] = VENDORS[vendor]['name']
            row_data[f'{level}_Quote'] = price
            row_data[f'{level}_vs_Budget'] = ((price - budget) / budget) * 100

        # Calculate average (excluding outliers if enabled)
        price_list = list(prices.values())
        if manual_remove:
            if outlier_method == "IQR (Interquartile Range)":
                _, _, outliers = detect_outliers_iqr(price_list, iqr_multiplier)
            elif outlier_method == "Standard Deviation":
                _, _, outliers = detect_outliers_std(price_list, std_multiplier)
            else:
                _, _, outliers = detect_outliers_percentage(price_list, pct_threshold)
            clean_prices = [p for p in price_list if p not in outliers]
            row_data['Avg'] = np.mean(clean_prices) if clean_prices else np.mean(price_list)
        else:
            row_data['Avg'] = np.mean(price_list)

        row_data['Avg_vs_Budget'] = ((row_data['Avg'] - budget) / budget) * 100

        classification_data.append(row_data)

    classification_df = pd.DataFrame(classification_data)

    # Display classification cards for each equipment
    for idx, row in classification_df.iterrows():
        with st.expander(f"📦 {row['Equipment']}", expanded=idx < 3):
            cols = st.columns(6)

            # L1-L5 vendor cards
            for i in range(5):
                level = f'L{i+1}'
                with cols[i]:
                    vendor_name = row[f'{level}_Vendor']
                    quote = row[f'{level}_Quote']
                    vs_budget = row[f'{level}_vs_Budget']

                    budget_indicator = "✅" if vs_budget < 0 else "⚠️"

                    st.markdown(f"""
                    <div style="background: {L_COLORS[level]['bg']}; padding: 1rem; border-radius: 8px;
                                border: 2px solid {L_COLORS[level]['color']}; text-align: center; min-height: 150px;">
                        <h4 style="color: {L_COLORS[level]['color']}; margin: 0;">{level}</h4>
                        <p style="margin: 0.25rem 0; font-size: 0.7rem; color: #666;">{vendor_name[:18]}</p>
                        <h3 style="margin: 0.5rem 0;">${quote:,}</h3>
                        <p style="margin: 0; font-size: 0.75rem; color: {'#22c55e' if vs_budget < 0 else '#ef4444'};">
                            {budget_indicator} {vs_budget:+.1f}%
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            # Summary card
            with cols[5]:
                avg = row['Avg']
                avg_vs_budget = row['Avg_vs_Budget']
                st.markdown(f"""
                <div style="background: #f3e8ff; padding: 1rem; border-radius: 8px;
                            border: 2px solid #8b5cf6; text-align: center; min-height: 150px;">
                    <h4 style="color: #8b5cf6; margin: 0;">AVG</h4>
                    <p style="margin: 0.25rem 0; font-size: 0.7rem; color: #666;">Average Quote</p>
                    <h3 style="margin: 0.5rem 0;">${avg:,.0f}</h3>
                    <p style="margin: 0; font-size: 0.75rem;">
                        Budget: ${row['Budget']:,}
                    </p>
                </div>
                """, unsafe_allow_html=True)

# ============ TAB 3: COMPARISON TABLE ============
with tab3:
    st.subheader("📋 Technical-Commercial Comparison Table")

    # Build comprehensive comparison table
    comparison_data = []

    for idx, row in filtered_df.iterrows():
        eq_name = row['Equipment']
        category = row['Category']
        budget = row['RIL_Budget']
        prices = {col: row[col] for col in vendor_cols}

        # Sort vendors by price to get L1-L5
        sorted_vendors = sorted(prices.items(), key=lambda x: x[1])

        comp_row = {
            'Equipment': eq_name,
            'Category': category,
        }

        # Add L1-L5 vendors and quotes
        for i, (vendor, price) in enumerate(sorted_vendors):
            level = f'L{i+1}'
            comp_row[f'{level} Vendor'] = VENDORS[vendor]['name'][:20]
            comp_row[f'{level} Quote'] = price

        # Calculate average
        price_list = list(prices.values())
        comp_row['Average'] = np.mean(price_list)
        comp_row['Budget'] = budget
        comp_row['Deviation %'] = ((comp_row['Average'] - budget) / budget) * 100

        comparison_data.append(comp_row)

    comparison_df = pd.DataFrame(comparison_data)

    # Display options
    view_option = st.radio(
        "View Mode",
        ["Full Table", "Quotes Only", "Vendors Only", "Summary"],
        horizontal=True
    )

    if view_option == "Full Table":
        display_df = comparison_df.copy()
    elif view_option == "Quotes Only":
        display_df = comparison_df[['Equipment', 'Category', 'L1 Quote', 'L2 Quote', 'L3 Quote', 'L4 Quote', 'L5 Quote', 'Average', 'Budget', 'Deviation %']].copy()
    elif view_option == "Vendors Only":
        display_df = comparison_df[['Equipment', 'Category', 'L1 Vendor', 'L2 Vendor', 'L3 Vendor', 'L4 Vendor', 'L5 Vendor']].copy()
    else:
        display_df = comparison_df[['Equipment', 'Category', 'L1 Quote', 'L5 Quote', 'Average', 'Budget', 'Deviation %']].copy()

    # Format currency columns
    currency_cols = [col for col in display_df.columns if 'Quote' in col or col in ['Average', 'Budget']]
    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")

    if 'Deviation %' in display_df.columns:
        display_df['Deviation %'] = comparison_df['Deviation %'].apply(lambda x: f"{x:+.1f}%")

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

    # Visual comparison chart
    st.markdown("---")
    st.subheader("📊 Visual Price Comparison")

    # Create comparison bar chart
    chart_data = []
    for idx, row in filtered_df.head(10).iterrows():
        for vendor in vendor_cols:
            chart_data.append({
                'Equipment': row['Equipment'][:25],
                'Vendor': VENDORS[vendor]['name'],
                'Price': row[vendor],
                'Budget': row['RIL_Budget']
            })

    chart_df = pd.DataFrame(chart_data)

    fig = px.bar(
        chart_df,
        x='Equipment',
        y='Price',
        color='Vendor',
        barmode='group',
        title="Vendor Quotes Comparison (Top 10 Equipment)",
        color_discrete_sequence=['#3b82f6', '#8b5cf6', '#22c55e', '#f97316', '#ef4444']
    )

    # Add budget line for each equipment
    for eq in chart_df['Equipment'].unique():
        budget = chart_df[chart_df['Equipment'] == eq]['Budget'].iloc[0]
        eq_idx = list(chart_df['Equipment'].unique()).index(eq)

    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        yaxis_tickformat="$,.0f",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# ============ TAB 4: SUMMARY & EXPORT ============
with tab4:
    st.subheader("📈 Summary Analysis")

    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)

    total_budget = filtered_df['RIL_Budget'].sum()
    total_l1 = sum(filtered_df[vendor_cols].min(axis=1))
    total_l5 = sum(filtered_df[vendor_cols].max(axis=1))
    total_avg = sum(filtered_df[vendor_cols].mean(axis=1))

    with col1:
        st.metric("Total Budget", f"${total_budget:,.0f}")
    with col2:
        st.metric("Total L1 (Lowest)", f"${total_l1:,.0f}", f"{((total_l1-total_budget)/total_budget)*100:+.1f}%")
    with col3:
        st.metric("Total Average", f"${total_avg:,.0f}", f"{((total_avg-total_budget)/total_budget)*100:+.1f}%")
    with col4:
        st.metric("Total L5 (Highest)", f"${total_l5:,.0f}", f"{((total_l5-total_budget)/total_budget)*100:+.1f}%")

    st.markdown("---")

    # Vendor win analysis
    st.subheader("🏆 Vendor Win Analysis (L1 Awards)")

    l1_wins = {}
    for idx, row in filtered_df.iterrows():
        prices = {col: row[col] for col in vendor_cols}
        l1_vendor = min(prices, key=prices.get)
        vendor_name = VENDORS[l1_vendor]['name']
        l1_wins[vendor_name] = l1_wins.get(vendor_name, 0) + 1

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.pie(
            values=list(l1_wins.values()),
            names=list(l1_wins.keys()),
            title="L1 (Lowest Quote) Awards by Vendor",
            color_discrete_sequence=['#3b82f6', '#8b5cf6', '#22c55e', '#f97316', '#ef4444']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**🎯 L1 Awards**")
        for vendor, count in sorted(l1_wins.items(), key=lambda x: -x[1]):
            pct = count / len(filtered_df) * 100
            st.markdown(f"""
            <div style="padding: 0.5rem; background: #f9fafb; border-radius: 4px; margin-bottom: 0.25rem;">
                <span style="font-weight: 500;">{vendor}</span>
                <span style="float: right;">{count} ({pct:.0f}%)</span>
            </div>
            """, unsafe_allow_html=True)

    # Export section
    st.markdown("---")
    st.subheader("📥 Export Reports")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Full report
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='Equipment Data', index=False)
            comparison_df.to_excel(writer, sheet_name='L1-L5 Comparison', index=False)
            pd.DataFrame(l1_wins.items(), columns=['Vendor', 'L1 Wins']).to_excel(writer, sheet_name='Vendor Analysis', index=False)

        st.download_button(
            label="📥 Full Commercial Report",
            data=buffer.getvalue(),
            file_name="commercial_evaluation_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

    with col2:
        # Price comparison only
        price_buffer = io.BytesIO()
        price_df = filtered_df[['Equipment', 'Category', 'RIL_Budget'] + vendor_cols].copy()
        price_df.to_excel(price_buffer, index=False, engine='openpyxl')

        st.download_button(
            label="📥 Price Comparison",
            data=price_buffer.getvalue(),
            file_name="price_comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col3:
        # L1-L5 classification
        l1l5_buffer = io.BytesIO()
        classification_df.to_excel(l1l5_buffer, index=False, engine='openpyxl')

        st.download_button(
            label="📥 L1-L5 Classification",
            data=l1l5_buffer.getvalue(),
            file_name="l1_l5_classification.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem;">
    <p>Procure-Pro-ISO | Commercial Evaluation Module</p>
    <p>Equipment count: {eq_count} | Categories: {cat_count}</p>
</div>
""".format(eq_count=len(filtered_df), cat_count=filtered_df['Category'].nunique()), unsafe_allow_html=True)
