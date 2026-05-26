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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.main { background-color: #060b16; }

section[data-testid="stSidebar"] {
    background-color: #09111f;
    border-right: 1px solid rgba(255,255,255,0.05);
}

.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* ── PAGE TITLE ── */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #3d5473;
    font-weight: 400;
    margin-bottom: 20px;
}

/* ── KPI HERO ── */
.kpi-hero {
    background: linear-gradient(145deg, #0c1a35 0%, #0a2040 55%, #081830 100%);
    border: 1px solid rgba(91,140,255,0.18);
    border-radius: 20px;
    padding: 30px 32px 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
}
.kpi-hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(91,140,255,0.1) 0%, transparent 65%);
    pointer-events: none;
}
.kpi-hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(91,140,255,0.15), transparent);
}
.kpi-hero-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #5B8CFF;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
/* Month — top, prominent */
.kpi-hero-month {
    font-size: 1.55rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.01em;
    line-height: 1.1;
    margin-bottom: 6px;
}
.kpi-hero-year {
    font-size: 1.55rem;
    font-weight: 400;
    color: #5B8CFF;
    margin-left: 8px;
    letter-spacing: -0.01em;
}
/* Divider between month and value */
.kpi-hero-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(91,140,255,0.25), transparent);
    margin: 14px 0;
}
/* Value — bottom, secondary */
.kpi-hero-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #a8c4ff;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.03em;
}
.kpi-hero-unit {
    font-size: 0.95rem;
    font-weight: 400;
    color: #3d5a80;
    margin-left: 6px;
    font-family: 'Syne', sans-serif;
    letter-spacing: 0;
}

/* ── METRIC CARD ── */
.metric-card {
    background: #0a1220;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 22px 26px;
    height: 100%;
    box-shadow: 0 2px 16px rgba(0,0,0,0.3);
}
.metric-card-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #2e4a68;
    margin-bottom: 10px;
}
.metric-card-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
    letter-spacing: -0.02em;
}
.metric-card-unit {
    font-size: 0.85rem;
    color: #3d5473;
    margin-left: 4px;
    font-family: 'Syne', sans-serif;
}
.metric-card-badge {
    display: inline-block;
    margin-top: 10px;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(0,194,168,0.1);
    color: #00C2A8;
    letter-spacing: 0.06em;
}

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #2e4a68;
    margin-bottom: 16px;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

/* ── BADGE ── */
.badge-report {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(91,140,255,0.08);
    border: 1px solid rgba(91,140,255,0.15);
    color: #5B8CFF;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 28px;
}

/* ── CHART CONTAINER ── */
.chart-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #4a6a8a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

hr { border-color: rgba(255,255,255,0.05) !important; }

/* Streamlit overrides */
[data-testid="stExpander"] {
    background: #0a1220;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
}
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
    font=dict(family="Syne, sans-serif", color="#3d5473", size=11),
    margin=dict(l=10, r=10, t=16, b=10),
    xaxis=dict(
        showgrid=False,
        linecolor="rgba(255,255,255,0.04)",
        tickcolor="rgba(0,0,0,0)",
        tickfont=dict(size=10, color="#3d5473"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(0,0,0,0)",
        tickcolor="rgba(0,0,0,0)",
        tickfont=dict(size=10, color="#3d5473"),
    ),
    showlegend=False,
)

# Portuguese month names
PT_MONTHS = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def report_id_to_label(report_id: str) -> str:
    """
    Converts 'REP2026_06' → 'Junho 2026'.
    Falls back gracefully if the format is unexpected.
    """
    try:
        clean = report_id.replace("REP", "")          # '2026_06'
        year_str, month_str = clean.split("_")
        year = int(year_str)
        month = int(month_str)
        return f"{PT_MONTHS[month]} {year}"
    except Exception:
        return report_id  # safe fallback

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
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


# ── DATA ───────────────────────────────────────────────────────────────────────
df_kpi = load_kpi_data()
df_raw = load_raw_data()

if df_kpi.empty:
    st.warning("Sem dados de KPI disponíveis.")
    st.stop()

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
latest_label = report_id_to_label(latest_report)

st.markdown('<div class="page-title">Energy KPI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Monitorização de consumo energético e sustentabilidade</div>', unsafe_allow_html=True)
st.markdown(f'<div class="badge-report">📋 Último relatório · {latest_label}</div>', unsafe_allow_html=True)


# ── HERO KPIs ──────────────────────────────────────────────────────────────────
consumo, consumo_unit   = get_kpi(df_latest, "consumo_total")
renovavel, renov_unit   = get_kpi(df_latest, "perc_energia_renovavel")

col_a, col_b, col_spacer = st.columns([1, 1, 1])

with col_a:
    if consumo is not None:
        # Split "Junho 2026" → month + year for styled rendering
        parts = latest_label.split(" ", 1)
        month_str = parts[0]
        year_str = parts[1] if len(parts) > 1 else ""
        st.markdown(f"""
        <div class="kpi-hero">
            <div class="kpi-hero-label">⚡ Consumo Total</div>
            <div class="kpi-hero-month">{month_str}<span class="kpi-hero-year">{year_str}</span></div>
            <div class="kpi-hero-divider"></div>
            <div class="kpi-hero-value">{consumo:,}<span class="kpi-hero-unit">{consumo_unit}</span></div>
        </div>
        """, unsafe_allow_html=True)

with col_b:
    if renovavel is not None:
        parts = latest_label.split(" ", 1)
        month_str = parts[0]
        year_str = parts[1] if len(parts) > 1 else ""
        st.markdown(f"""
        <div class="kpi-hero">
            <div class="kpi-hero-label">🌱 Energia Renovável</div>
            <div class="kpi-hero-month">{month_str}<span class="kpi-hero-year">{year_str}</span></div>
            <div class="kpi-hero-divider"></div>
            <div class="kpi-hero-value">{renovavel}<span class="kpi-hero-unit">{renov_unit}</span></div>
        </div>
        """, unsafe_allow_html=True)

st.divider()


# ── CHARTS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Evolução ao Longo do Tempo</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# ── Consumo total per report (bar) ──
with chart_col1:
    st.markdown('<div class="chart-title">Consumo Total por Relatório</div>', unsafe_allow_html=True)

    df_consumo_all = (
        df_kpi[df_kpi["kpi_name"] == "consumo_total"]
        .groupby("report_id", as_index=False)["value"]
        .mean()          # aggregate duplicates
    )
    df_consumo_all["report_id"] = pd.Categorical(
        df_consumo_all["report_id"], categories=all_reports, ordered=True
    )
    df_consumo_all = df_consumo_all.sort_values("report_id")
    df_consumo_all["label"] = df_consumo_all["report_id"].astype(str).apply(report_id_to_label)

    if not df_consumo_all.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_consumo_all["label"],
            y=df_consumo_all["value"],
            marker=dict(
                color=df_consumo_all["report_id"].astype(str).apply(
                    lambda r: "#5B8CFF" if r == latest_report else "#162340"
                ),
                line=dict(width=0),
                cornerradius=6,
            ),
            hovertemplate="<b>%{x}</b><br>%{y:,} kWh<extra></extra>",
        ))
        layout = dict(**PLOT_LAYOUT, height=280)
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de consumo.")

# ── Renovável per report (line) — aggregated to ONE point per report ──
with chart_col2:
    st.markdown('<div class="chart-title">Energia Renovável % por Relatório</div>', unsafe_allow_html=True)

    df_renov_all = (
        df_kpi[df_kpi["kpi_name"] == "perc_energia_renovavel"]
        .groupby("report_id", as_index=False)["value"]
        .mean()          # ← FIX: one point per report, eliminates double dots
    )
    df_renov_all["report_id"] = pd.Categorical(
        df_renov_all["report_id"], categories=all_reports, ordered=True
    )
    df_renov_all = df_renov_all.sort_values("report_id")
    df_renov_all["label"] = df_renov_all["report_id"].astype(str).apply(report_id_to_label)

    if not df_renov_all.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_renov_all["label"],
            y=df_renov_all["value"],
            mode="lines+markers",
            line=dict(color="#00C2A8", width=2.5),
            marker=dict(
                size=8,
                color="#00C2A8",
                line=dict(color="#060b16", width=2),
            ),
            fill="tozeroy",
            fillcolor="rgba(0,194,168,0.06)",
            hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
        ))
        layout2 = dict(**PLOT_LAYOUT, height=280)
        fig2.update_layout(**layout2)
        fig2.update_yaxes(
            range=[0, 100],
            ticksuffix="%",
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(0,0,0,0)",
            tickcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de energia renovável.")

st.divider()


# ── RAW DOCUMENTS ──────────────────────────────────────────────────────────────
with st.expander("📄 Documentos Originais", expanded=False):
    if not df_raw.empty:
        categories = ["Todos"] + sorted(df_raw["category"].unique()) if "category" in df_raw.columns else ["Todos"]
        selected = st.selectbox("Filtrar por Categoria", categories, key="cat_filter")
        df_show = df_raw if selected == "Todos" else df_raw[df_raw["category"] == selected]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("Sem documentos disponíveis.")

with st.expander("📊 Todos os Valores KPI", expanded=False):
    st.dataframe(df_kpi.sort_values(["report_id", "kpi_name"]), use_container_width=True, hide_index=True)
