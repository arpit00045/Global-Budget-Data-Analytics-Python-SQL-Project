import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Global Budget Analytics Core",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# VIBRANT / MODERN THEME (custom CSS)
# --------------------------------------------------------------------------
VIVID_COLORS = ["#FF4E9B", "#7C4DFF", "#00E5FF", "#00E676", "#FFD600",
                "#FF6D00", "#40C4FF", "#FF1744", "#76FF03", "#D500F9"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Main app background */
.stApp {
    background: linear-gradient(160deg, #0f0c29 0%, #302b63 45%, #24243e 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #4c1d95 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * {
    color: #f5f3ff !important;
}

/* Title gradient text */
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #FF4E9B, #7C4DFF, #00E5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
}
.hero-subtitle {
    color: #cbd5e1;
    font-size: 1.05rem;
    margin-top: 4px;
    margin-bottom: 1.5rem;
}
.hero-emoji {
    -webkit-text-fill-color: initial;
    background: none;
}

/* KPI Cards */
.kpi-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 18px 20px;
    backdrop-filter: blur(6px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    height: 100%;
}
.kpi-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 10px 30px rgba(124, 77, 255, 0.35);
    border-color: rgba(124, 77, 255, 0.6);
}
.kpi-label {
    font-size: 0.85rem;
    color: #cbd5e1;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #ffffff;
}
.kpi-delta-up { color: #00E676; font-weight: 700; font-size: 0.95rem; }
.kpi-delta-down { color: #FF5252; font-weight: 700; font-size: 0.95rem; }

/* Section headers */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    border-left: 5px solid #7C4DFF;
    padding-left: 12px;
    margin: 1.2rem 0 0.6rem 0;
}

/* Tabs styling */
button[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 1rem;
    border-radius: 10px 10px 0 0;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #7C4DFF, #FF4E9B);
    color: white !important;
}

/* Dataframe / cards container */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Metrics native widget polish (fallback) */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 10px 14px;
    border: 1px solid rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)


def get_engine():
    # Reads from .streamlit/secrets.toml locally, or from Streamlit Cloud's
    # Secrets manager when deployed. Falls back to local defaults if no
    # secrets file is found at all (useful for quick local testing) —
    # accessing st.secrets raises an error when no secrets.toml exists,
    # so we guard the whole block with try/except.
    try:
        db_user = st.secrets.get("DB_USER", "root")
        db_password = st.secrets.get("DB_PASSWORD", "1243")
        db_host = st.secrets.get("DB_HOST", "localhost")
        db_port = st.secrets.get("DB_PORT", "3306")
        db_name = st.secrets.get("DB_NAME", "global_budget_db")
    except Exception:
        db_user = "root"
        db_password = "1243"
        db_host = "localhost"
        db_port = "3306"
        db_name = "global_budget_db"

    password_quoted = urllib.parse.quote_plus(db_password)
    return create_engine(
        f"mysql+mysqlconnector://{db_user}:{password_quoted}@{db_host}:{db_port}/{db_name}"
    )


def kpi_card(label, value, delta=None, delta_positive=True):
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# HERO HEADER
# --------------------------------------------------------------------------
st.markdown('<div class="hero-title"><span class="hero-emoji">🌍</span> Global Government Budget Analytics Core</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">An interactive platform exploring public finance shifts, sector dominance, and predictive trajectories.</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------
st.sidebar.markdown("## 🎛️ Control Panel")
with st.spinner("Loading countries..."):
    engine = get_engine()
    countries_df = pd.read_sql_query("SELECT country_name FROM countries ORDER BY country_name", engine)
    engine.dispose()

selected_country = st.sidebar.selectbox("🌐 Select a Country to Filter", countries_df['country_name'].tolist())
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**About**  \n"
    "This dashboard analyzes historical government spending, sector allocation, "
    "statistical anomalies, and forward-looking projections using live data."
)
st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: switch tabs above to explore different analytical lenses.")

# --------------------------------------------------------------------------
# NAVIGATION TABS
# --------------------------------------------------------------------------
tab_macro, tab_sectors, tab_anomalies, tab_research_lab = st.tabs([
    "📈 Macro Historical Trends",
    "🥧 Sector Structural Spreads",
    "🔍 Statistical Anomalies",
    "🔬 Macro Economic Research Lab"
])

with tab_macro:
    st.markdown('<div class="section-header">Global Spending Growth Pathways</div>', unsafe_allow_html=True)
    with st.spinner("Fetching macro budget data..."):
        engine = get_engine()
        q = """
            SELECT b.year, b.total_budget_billions_usd
            FROM budgets b JOIN countries c ON b.country_id = c.country_id
            WHERE c.country_name = %s ORDER BY b.year
        """
        df_macro = pd.read_sql_query(q, engine, params=(selected_country,))
        engine.dispose()

    if not df_macro.empty:
        # KPI row
        latest = df_macro.iloc[-1]
        prev = df_macro.iloc[-2] if len(df_macro) > 1 else None
        peak_row = df_macro.loc[df_macro['total_budget_billions_usd'].idxmax()]
        growth_pct = None
        if prev is not None and prev['total_budget_billions_usd'] != 0:
            growth_pct = ((latest['total_budget_billions_usd'] - prev['total_budget_billions_usd'])
                          / prev['total_budget_billions_usd']) * 100

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_card("Latest Budget", f"${latest['total_budget_billions_usd']:,.1f}B")
        with k2:
            if growth_pct is not None:
                kpi_card("YoY Growth", f"{growth_pct:+.2f}%", delta=f"vs {int(prev['year'])}", delta_positive=growth_pct >= 0)
            else:
                kpi_card("YoY Growth", "N/A")
        with k3:
            kpi_card("Peak Year", f"{int(peak_row['year'])}", delta=f"${peak_row['total_budget_billions_usd']:,.1f}B", delta_positive=True)
        with k4:
            kpi_card("Years Tracked", f"{df_macro['year'].nunique()}")

        st.markdown("<br>", unsafe_allow_html=True)

        fig = px.line(df_macro, x="year", y="total_budget_billions_usd",
                      title=f"Historical Expenditure Strategy: {selected_country}",
                      template="plotly_dark",
                      labels={"total_budget_billions_usd": "Total Budget (Billions USD)"},
                      color_discrete_sequence=["#00E5FF"])
        fig.update_traces(line=dict(width=3), fill="tozeroy", fillcolor="rgba(0,229,255,0.15)")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Poppins", size=13),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No records found for the selection.")

with tab_sectors:
    st.markdown('<div class="section-header">Allocation Distribution Analysis</div>', unsafe_allow_html=True)
    with st.spinner("Fetching sector allocation data..."):
        engine = get_engine()
        q_sec = """
            SELECT b.year, sa.sector_name, sa.allocated_percentage, sa.allocated_amount_billions_usd
            FROM sector_allocations sa
            JOIN budgets b ON sa.budget_id = b.budget_id
            JOIN countries c ON b.country_id = c.country_id
            WHERE c.country_name = %s
        """
        df_sec = pd.read_sql_query(q_sec, engine, params=(selected_country,))
        engine.dispose()

    if not df_sec.empty:
        top_sector = (df_sec.groupby("sector_name")["allocated_percentage"].mean()
                      .sort_values(ascending=False).idxmax())
        n_sectors = df_sec["sector_name"].nunique()
        k1, k2 = st.columns(2)
        with k1:
            kpi_card("Dominant Sector (avg)", top_sector)
        with k2:
            kpi_card("Tracked Sectors", f"{n_sectors}")

        st.markdown("<br>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_area = px.area(df_sec, x="year", y="allocated_percentage", color="sector_name",
                                title="Structural Budget Shifts Over Time", template="plotly_dark",
                                color_discrete_sequence=VIVID_COLORS)
            fig_area.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                    font=dict(family="Poppins", size=12))
            st.plotly_chart(fig_area, use_container_width=True)
        with col_c2:
            fig_box = px.box(df_sec, x="sector_name", y="allocated_percentage", color="sector_name",
                              title="Variance and Spread Across Sectors", template="plotly_dark",
                              color_discrete_sequence=VIVID_COLORS)
            fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                   font=dict(family="Poppins", size=12), showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No sector records found.")

with tab_anomalies:
    st.markdown('<div class="section-header">Descriptive Outlier Detection</div>', unsafe_allow_html=True)
    st.markdown("Identifies fiscal years where spending shifted sharply outside normal historical baselines.")

    if not df_macro.empty:
        mean_val = df_macro['total_budget_billions_usd'].mean()
        std_val = df_macro['total_budget_billions_usd'].std()

        df_macro['z_score'] = (df_macro['total_budget_billions_usd'] - mean_val) / std_val
        anomalies = df_macro[df_macro['z_score'].abs() > 1.96]

        k1, k2, k3 = st.columns(3)
        with k1:
            kpi_card("Mean Budget", f"${mean_val:,.1f}B")
        with k2:
            kpi_card("Std Deviation", f"${std_val:,.1f}B")
        with k3:
            kpi_card("Outliers Found", f"{len(anomalies)}", delta_positive=len(anomalies) == 0)

        st.markdown("<br>", unsafe_allow_html=True)

        # Scatter plot highlighting outliers
        df_plot = df_macro.copy()
        df_plot["status"] = np.where(df_plot['z_score'].abs() > 1.96, "Outlier", "Normal")
        fig_out = px.scatter(df_plot, x="year", y="total_budget_billions_usd", color="status",
                              color_discrete_map={"Normal": "#00E5FF", "Outlier": "#FF1744"},
                              size=df_plot['z_score'].abs().clip(lower=1) * 8,
                              title="Budget Trend with Flagged Outliers", template="plotly_dark")
        fig_out.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               font=dict(family="Poppins", size=12))
        st.plotly_chart(fig_out, use_container_width=True)

        st.write("### 🚩 Flagged Fiscal Outlier Periods (Z-Score > 1.96):")
        if not anomalies.empty:
            st.dataframe(anomalies.style.background_gradient(cmap='Reds', subset=['total_budget_billions_usd']), use_container_width=True)
        else:
            st.success("Excellent budget structural stability! No extreme statistical outliers discovered.")

with tab_research_lab:
    st.markdown('<div class="section-header">🔬 Deep Exploratory Research Workspace</div>', unsafe_allow_html=True)
    st.markdown("Advanced analytical modules calculating structural correlation shifts and spending volatility.")

    # Render Analysis C (Correlation Matrix) visually as an interactive heatmap
    st.subheader("Cross-Sector Allocation Correlation Matrix")
    with st.spinner("Computing correlations..."):
        engine = get_engine()
        q_corr = """
            SELECT b.year, sa.sector_name, sa.allocated_percentage
            FROM sector_allocations sa
            JOIN budgets b ON sa.budget_id = b.budget_id
            JOIN countries c ON b.country_id = c.country_id
            WHERE c.country_name = %s;
        """
        df_corr_raw = pd.read_sql(q_corr, engine, params=(selected_country,))
        engine.dispose()

    if not df_corr_raw.empty:
        pivot_df = df_corr_raw.pivot(index='year', columns='sector_name', values='allocated_percentage')
        corr_matrix = pivot_df.corr()

        # Build an interactive Plotly Heatmap chart layout
        fig_heat = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="Viridis",  # vibrant continuous scale
            labels=dict(color="Correlation Coefficient"),
            template="plotly_dark"
        )
        fig_heat.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Poppins", size=12))
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- Volatility Index & Rolling Statistics ---
    st.subheader("Volatility Index & Rolling Statistics")
    with st.spinner("Calculating volatility metrics..."):
        engine = get_engine()
        q_vol = """
            SELECT b.year, b.total_budget_billions_usd
            FROM budgets b JOIN countries c ON b.country_id = c.country_id
            WHERE c.country_name = %s ORDER BY b.year ASC
        """
        df_vol = pd.read_sql(q_vol, engine, params=(selected_country,))
        engine.dispose()

    if not df_vol.empty:
        df_vol = df_vol.sort_values('year')
        df_vol['rolling_mean'] = df_vol['total_budget_billions_usd'].rolling(window=10).mean()
        df_vol['rolling_std'] = df_vol['total_budget_billions_usd'].rolling(window=10).std()
        df_vol['volatility_index'] = (df_vol['rolling_std'] / df_vol['rolling_mean']) * 100

        st.markdown("Rolling 10-year Volatility Index (Coefficient of Variation)")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=df_vol['year'], y=df_vol['volatility_index'], mode='lines+markers',
                                      name='Volatility Index', line=dict(color='#FFD600', width=3),
                                      marker=dict(size=6, color='#FF6D00')))
        fig_vol.update_layout(template='plotly_dark', yaxis_title='Volatility Index (%)',
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               font=dict(family="Poppins", size=12))
        st.plotly_chart(fig_vol, use_container_width=True)

        st.write("Recent rolling statistics (non-null rows):")
        st.dataframe(df_vol.dropna().tail(10), use_container_width=True)
    else:
        st.info("Not enough historical data to compute volatility metrics for this country.")

    # --- Polynomial Projection (Analytical) ---
    st.subheader("Polynomial Projection (Analytical)")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        proj_degree = st.selectbox("Projection degree", [1, 2, 3], index=1)
        proj_horizon = st.number_input("Forecast horizon year", min_value=2025, max_value=2050, value=2035)
    with col_p2:
        apply_scenario = st.checkbox("Apply scenario shock to projection")
        shock_pct = st.slider("Shock %", -50, 100, 0)

    if not df_vol.empty:
        x = df_vol['year'].astype(int).values
        y = df_vol['total_budget_billions_usd'].astype(float).values
        if len(x) > proj_degree:
            coeffs = np.polyfit(x, y, deg=proj_degree)
            poly = np.poly1d(coeffs)
            years_future = np.arange(int(x.max()) + 1, int(proj_horizon) + 1)
            proj_vals = poly(years_future)
            if apply_scenario and shock_pct != 0:
                proj_vals = proj_vals * (1 + shock_pct / 100.0)

            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=x, y=y, mode='markers+lines', name='Historical',
                                           marker=dict(color='#40C4FF', size=6),
                                           line=dict(color='#40C4FF', width=2)))
            fig_proj.add_trace(go.Scatter(x=years_future, y=proj_vals, mode='lines', name='Projection',
                                           line=dict(color='#FF4E9B', dash='dash', width=3)))
            fig_proj.update_layout(title=f"Polynomial Projection (deg {proj_degree}) for {selected_country}",
                                    template='plotly_dark', xaxis_title='Year', yaxis_title='Budget (Billions USD)',
                                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                    font=dict(family="Poppins", size=12), hovermode="x unified")
            st.plotly_chart(fig_proj, use_container_width=True)

            df_proj_out = pd.DataFrame({'year': years_future, 'projected_budget': proj_vals})
            st.dataframe(df_proj_out.style.format({'projected_budget': '${:,.2f}'}), use_container_width=True)
        else:
            st.warning("Not enough historical points for the selected polynomial degree.")