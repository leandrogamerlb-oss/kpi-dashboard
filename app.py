import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #080d1a; }

section[data-testid="stSidebar"] {
    background-color: #0d1424;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* ── KPI HERO ── */
.kpi-hero {
    background: linear-gradient(135deg, #0f1f3d 0%, #0d2a4a 60%, #0a1e35 100%);
    border: 1px solid rgba(91,140,255,0.2);
    border-radius: 20px;
    padding: 32px 36px;
    position: relative;
    overflow: hidden;
}
.kpi-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(91,140,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.kpi-hero-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5B8CFF;
    margin-bottom: 10px;
}
.kpi-hero-value {
    font-size: 3.2rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 6px;
    font-family: 'DM Mono', monospace;
}
.kpi-hero-unit {
    font-size: 1.1rem;
    font-weight: 400;
    color: #7A8BA6;
    margin-left: 6px;
}
.kpi-hero-sub {
    font-size: 0.82rem;
    color: #4A6080;
    margin-top: 10px;
}

/* ── METRIC CARD ── */
.metric-card {
    background: #0f1729;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px 28px;
    height: 100%;
}
.metric-card-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4A6080;
    margin-bottom: 12px;
}
.metric-card-value {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    font-family: 'DM Mono', monospace;
    line-height: 1;
}
.metric-card-unit {
    font-size: 0.9rem;
    color: #7A8BA6;
    margin-left: 4px;
}
.metric-card-badge {
    display: inline-block;
    margin-top: 12px;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(0,194,168,0.12);
    color: #00C2A8;
}

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4A6080;
    margin-bottom: 4px;
    margin-top: 8px;
}

/* ── BADGE ── */
.badge-report {
    display: inline-block;
    background: rgba(91,140,255,0.12);
    color: #5B8CFF;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    margin-bottom: 20px;
}

hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)


# ── MONGO ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    uri = os.getenv("MONGO_URI") or st.secrets.get("MONGO_URI")
    if not uri:
        st.error("MongoDB URI não configurado.")
        st.stop()
    return pymongo.MongoClient(uri)


@st.cache_data(ttl=60)
def load_kpi_data():
    client = get_client()
    data = list(client["faturas"]["kpi_value"].find({}, {"_id": 0}))
    df = pd.DataFrame(data)
    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df


@st.cache_data(ttl=60)
def load_raw_data():
    client = get_client()
    data = list(client["faturas"]["documentos"].find({}, {"_id": 0}))
    df = pd.DataFrame(data)
    if not df.empty and "recorded_at" in df.columns:
        df["recorded_at"] = pd.to_datetime(df["recorded_at"], errors="coerce")
    return df


@st.cache_data(ttl=60)
def load_company():
    client = get_client()
    doc = client["faturas"]["company"].find_one({}, {"_id": 0})
    return doc or {}


# ── HELPERS ────────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#7A8BA6", size=12),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.06)", tickcolor="rgba(0,0,0,0)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)"),
    showlegend=False,
)

def sort_reports(reports):
    """Sort report IDs — tries to extract year+month numeric suffix."""
    def key(r):
        parts = r.replace("REP", "").split("_")
        try:
            return int("".join(parts))
        except Exception:
            return r
    return sorted(reports, key=key)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
company = load_company()

with st.sidebar:
    st.markdown("### ⚡ Energy Analytics")
    if company:
        st.markdown(f"**{company.get('company_name', '')}**")
        st.caption(f"{company.get('sector', '')} · {company.get('country', '')}")
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption(f"Updated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


# ── DATA ───────────────────────────────────────────────────────────────────────
df_kpi = load_kpi_data()
df_raw = load_raw_data()

if df_kpi.empty:
    st.warning("Sem dados de KPI disponíveis.")
    st.stop()

# Latest report (sorted alphanumerically — works for REP2026_05, REP2026_06, …)
all_reports = sort_reports(df_kpi["report_id"].unique().tolist())
latest_report = all_reports[-1]
df_latest = df_kpi[df_kpi["report_id"] == latest_report]

def get_kpi(df, name, default=None):
    row = df[df["kpi_name"] == name]
    if row.empty:
        return default, ""
    r = row.iloc[0]
    return r.get("value", default), r.get("unit", "")


# ── PAGE HEADER ────────────────────────────────────────────────────────────────
st.markdown("## Energy KPI Dashboard")
st.caption("Executive analytics for energy consumption and sustainability monitoring.")
st.markdown(f'<div class="badge-report">Latest Report · {latest_report}</div>', unsafe_allow_html=True)


# ── HERO KPIs (latest report) ──────────────────────────────────────────────────
consumo, consumo_unit   = get_kpi(df_latest, "consumo_total")
renovavel, renov_unit   = get_kpi(df_latest, "perc_energia_renovavel")

col_a, col_b, col_spacer = st.columns([1, 1, 1])

with col_a:
    if consumo is not None:
        st.markdown(f"""
        <div class="kpi-hero">
            <div class="kpi-hero-label">⚡ Total Consumption</div>
            <div class="kpi-hero-value">{consumo:,}<span class="kpi-hero-unit">{consumo_unit}</span></div>
            <div class="kpi-hero-sub">{latest_report}</div>
        </div>
        """, unsafe_allow_html=True)

with col_b:
    if renovavel is not None:
        st.markdown(f"""
        <div class="kpi-hero">
            <div class="kpi-hero-label">🌱 Renewable Energy</div>
            <div class="kpi-hero-value">{renovavel}<span class="kpi-hero-unit">{renov_unit}</span></div>
            <div class="kpi-hero-sub">{latest_report}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()


# ── CHARTS: EVOLUTION OVER TIME ────────────────────────────────────────────────
st.markdown('<div class="section-header">Evolution Over Time</div>', unsafe_allow_html=True)
st.markdown(" ")

chart_col1, chart_col2 = st.columns(2)

# Consumo over time
with chart_col1:
    st.markdown("**Total Consumption per Report**")
    df_consumo_all = df_kpi[df_kpi["kpi_name"] == "consumo_total"].copy()
    df_consumo_all["report_id"] = pd.Categorical(
        df_consumo_all["report_id"], categories=all_reports, ordered=True
    )
    df_consumo_all = df_consumo_all.sort_values("report_id")

    if not df_consumo_all.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_consumo_all["report_id"],
            y=df_consumo_all["value"],
            marker=dict(
                color=df_consumo_all["report_id"].astype(str).apply(
                    lambda r: "#5B8CFF" if r == latest_report else "#1e3060"
                ),
                line=dict(width=0),
            ),
            hovertemplate="<b>%{x}</b><br>%{y:,} kWh<extra></extra>",
        ))
        fig.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de consumo.")

# Renovável over time
with chart_col2:
    st.markdown("**Renewable Energy % per Report**")
    df_renov_all = df_kpi[df_kpi["kpi_name"] == "perc_energia_renovavel"].copy()
    df_renov_all["report_id"] = pd.Categorical(
        df_renov_all["report_id"], categories=all_reports, ordered=True
    )
    df_renov_all = df_renov_all.sort_values("report_id")

    if not df_renov_all.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_renov_all["report_id"],
            y=df_renov_all["value"],
            mode="lines+markers",
            line=dict(color="#00C2A8", width=2.5),
            marker=dict(size=7, color="#00C2A8"),
            fill="tozeroy",
            fillcolor="rgba(0,194,168,0.07)",
            hovertemplate="<b>%{x}</b><br>%{y} %<extra></extra>",
        ))
        fig2.update_layout(**PLOT_LAYOUT, height=280)
        fig2.update_yaxes(range=[0, 100], gridcolor="rgba(255,255,255,0.05)",
                          linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de energia renovável.")

st.divider()


# ── SECONDARY METRIC CARDS (all KPIs for latest report) ───────────────────────
st.markdown('<div class="section-header">All KPIs · ' + latest_report + '</div>', unsafe_allow_html=True)
st.markdown(" ")

kpi_rows = df_latest.to_dict("records")
if kpi_rows:
    cols = st.columns(min(len(kpi_rows), 4))
    for i, row in enumerate(kpi_rows):
        with cols[i % len(cols)]:
            name = row.get("kpi_name", "").replace("_", " ").title()
            val  = row.get("value", "—")
            unit = row.get("unit", "")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-card-label">{name}</div>
                <div class="metric-card-value">{val}<span class="metric-card-unit">{unit}</span></div>
                <div class="metric-card-badge">{latest_report}</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()


# ── RAW DOCUMENTS ──────────────────────────────────────────────────────────────
with st.expander("📄 Raw Documents", expanded=False):
    if not df_raw.empty:
        categories = ["All"] + sorted(df_raw["category"].unique()) if "category" in df_raw.columns else ["All"]
        selected = st.selectbox("Filter by Category", categories, key="cat_filter")
        df_show = df_raw if selected == "All" else df_raw[df_raw["category"] == selected]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("Sem documentos disponíveis.")

with st.expander("📊 All KPI Values", expanded=False):
    st.dataframe(df_kpi.sort_values(["report_id", "kpi_name"]), use_container_width=True, hide_index=True)
