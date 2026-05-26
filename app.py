import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv
from streamlit_plotly_events import plotly_events

load_dotenv()

st.set_page_config(
    page_title="Energy Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SVG ICONS ─────────────────────────────────────────────────────────────────
ICON_ZAP = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>"""

ICON_LEAF = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
  <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>"""

ICON_REPORT = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
  <line x1="16" y1="13" x2="8" y2="13"/>
  <line x1="16" y1="17" x2="8" y2="17"/>
  <polyline points="10 9 9 9 8 9"/></svg>"""

ICON_BOLT_SIDEBAR = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
  fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>"""

ICON_CLOSE = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>"""

ICON_CALENDAR = """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
  <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
  <line x1="3" y1="10" x2="21" y2="10"/></svg>"""

ICON_ZAP_SM = """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>"""

ICON_LEAF_SM = """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
  <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>"""

ICON_TABLE_SM = """<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
  <line x1="3" y1="9" x2="21" y2="9"/>
  <line x1="3" y1="15" x2="21" y2="15"/>
  <line x1="9" y1="3" x2="9" y2="21"/></svg>"""

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.main { background-color: #f4f6f9; }

section[data-testid="stSidebar"] { background-color: #1a1f2e; border-right: none; }
section[data-testid="stSidebar"] * { color: #c8d0e0 !important; }
section[data-testid="stSidebar"] h3 { color: #ffffff !important; }
section[data-testid="stSidebar"] strong { color: #ffffff !important; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.page-title { font-size: 2rem; font-weight: 800; color: #111827; letter-spacing: -0.02em; margin-bottom: 4px; }
.page-subtitle { font-size: 0.85rem; color: #6b7280; font-weight: 400; margin-bottom: 20px; }

.badge-report {
    display: inline-flex; align-items: center; gap: 6px;
    background: #e8eaf6; border: 1px solid #c5cae9; color: #3949ab;
    font-size: 0.7rem; font-weight: 700; padding: 5px 14px;
    border-radius: 20px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 28px;
}

/* ── KPI CARDS ── */
.kpi-hero-consumo {
    background: linear-gradient(135deg, #fff8ed 0%, #fff3e0 100%);
    border: 1.5px solid #fbc02d; border-radius: 20px; padding: 28px 32px 26px;
    position: relative; overflow: hidden; box-shadow: 0 4px 24px rgba(251,192,45,0.15);
}
.kpi-hero-consumo::before {
    content: ''; position: absolute; top: -50px; right: -50px; width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(255,193,7,0.18) 0%, transparent 65%); pointer-events: none;
}
.kpi-hero-renov {
    background: linear-gradient(135deg, #f0fdf4 0%, #e6f7ee 100%);
    border: 1.5px solid #34a853; border-radius: 20px; padding: 28px 32px 26px;
    position: relative; overflow: hidden; box-shadow: 0 4px 24px rgba(52,168,83,0.15);
}
.kpi-hero-renov::before {
    content: ''; position: absolute; top: -50px; right: -50px; width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(52,168,83,0.14) 0%, transparent 65%); pointer-events: none;
}
.kpi-icon-row { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.kpi-icon-wrap-consumo { display: flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; background: rgba(251,192,45,0.18); border-radius: 8px; color: #b45309; flex-shrink: 0; }
.kpi-icon-wrap-renov { display: flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; background: rgba(52,168,83,0.14); border-radius: 8px; color: #166534; flex-shrink: 0; }
.kpi-hero-kpi-name { font-size: 1.1rem; font-weight: 800; letter-spacing: 0.01em; text-transform: uppercase; }
.kpi-hero-kpi-name-consumo { color: #b45309; }
.kpi-hero-kpi-name-renov   { color: #166534; }
.kpi-hero-month { font-size: 1.7rem; font-weight: 800; color: #111827; letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 4px; }
.kpi-hero-year { font-size: 1.7rem; font-weight: 400; margin-left: 10px; }
.kpi-hero-year-consumo { color: #d97706; }
.kpi-hero-year-renov   { color: #16a34a; }
.kpi-hero-divider-consumo { height: 2px; background: linear-gradient(90deg, #fbc02d, transparent); margin: 16px 0; border-radius: 2px; }
.kpi-hero-divider-renov   { height: 2px; background: linear-gradient(90deg, #34a853, transparent); margin: 16px 0; border-radius: 2px; }
.kpi-hero-value { font-size: 2.8rem; font-weight: 800; line-height: 1; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.04em; color: #111827; }
.kpi-hero-unit { font-size: 1rem; font-weight: 500; margin-left: 6px; font-family: 'Syne', sans-serif; }
.kpi-hero-unit-consumo { color: #92400e; }
.kpi-hero-unit-renov   { color: #166534; }

/* ── DETAIL PANEL ── */
.detail-panel {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 28px 28px 24px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.10);
    margin-bottom: 8px;
}
.detail-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
}
.detail-title-row { display: flex; align-items: center; gap: 10px; }
.detail-month-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f3f4f6; border: 1px solid #e5e7eb;
    color: #374151; font-size: 0.72rem; font-weight: 700;
    padding: 4px 12px; border-radius: 20px;
    letter-spacing: 0.08em; text-transform: uppercase;
}
.detail-month-pill svg { vertical-align: middle; }
.detail-section-label {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #9ca3af;
    margin-bottom: 10px; margin-top: 16px;
    display: flex; align-items: center; gap: 8px;
}
.detail-section-label::after { content: ''; flex: 1; height: 1px; background: #f3f4f6; }
.kpi-row {
    display: flex; gap: 12px; margin-bottom: 4px; flex-wrap: wrap;
}
.kpi-chip {
    flex: 1; min-width: 120px;
    border-radius: 14px; padding: 14px 18px;
}
.kpi-chip-amber { background: #fff8ed; border: 1px solid #fde68a; }
.kpi-chip-green { background: #f0fdf4; border: 1px solid #bbf7d0; }
.kpi-chip-blue  { background: #eff6ff; border: 1px solid #bfdbfe; }
.kpi-chip-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; display: flex; align-items: center; gap: 5px; }
.kpi-chip-label-amber { color: #92400e; }
.kpi-chip-label-green { color: #166534; }
.kpi-chip-label-blue  { color: #1e40af; }
.kpi-chip-value { font-size: 1.6rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.03em; color: #111827; }
.kpi-chip-unit  { font-size: 0.8rem; font-weight: 500; color: #6b7280; margin-left: 4px; font-family: 'Syne', sans-serif; }

/* hint text below charts */
.chart-hint {
    font-size: 0.68rem; color: #9ca3af; margin-top: -4px; margin-bottom: 4px;
    display: flex; align-items: center; gap: 5px;
}
.chart-hint svg { vertical-align: middle; }

.section-header {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;
    color: #9ca3af; margin-bottom: 16px; margin-top: 8px;
    display: flex; align-items: center; gap: 10px;
}
.section-header::after { content: ''; flex: 1; height: 1px; background: #e5e7eb; }
.chart-title { font-size: 0.75rem; font-weight: 700; color: #6b7280; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2px; }
.sidebar-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.sidebar-brand-text { font-size: 1rem; font-weight: 800; color: #ffffff !important; letter-spacing: -0.01em; }

hr { border-color: #e5e7eb !important; }
[data-testid="stExpander"] { background: #ffffff; border: 1px solid #e5e7eb !important; border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)


# ── MONGO ─────────────────────────────────────────────────────────────────────
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


# ── HELPERS ───────────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Syne, sans-serif", color="#9ca3af", size=11),
    margin=dict(l=10, r=10, t=16, b=10),
    xaxis=dict(showgrid=False, linecolor="#e5e7eb",
               tickcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color="#6b7280")),
    yaxis=dict(gridcolor="#f3f4f6", linecolor="rgba(0,0,0,0)",
               tickcolor="rgba(0,0,0,0)", tickfont=dict(size=10, color="#6b7280")),
    showlegend=False,
)

PT_MONTHS = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def report_id_to_label(report_id: str) -> str:
    try:
        clean = report_id.replace("REP", "")
        year_str, month_str = clean.split("_")
        return f"{PT_MONTHS[int(month_str)]} {int(year_str)}"
    except Exception:
        return report_id

def label_to_report_id(label: str, all_reports: list) -> str | None:
    """Reverse lookup: 'Junho 2026' → 'REP2026_06'"""
    for r in all_reports:
        if report_id_to_label(r) == label:
            return r
    return None

def sort_reports(reports):
    def key(r):
        parts = r.replace("REP", "").split("_")
        try:
            return int("".join(parts))
        except Exception:
            return r
    return sorted(reports, key=key)

def get_kpi(df, name, default=None):
    row = df[df["kpi_name"] == name]
    if row.empty:
        return default, ""
    r = row.iloc[0]
    return r.get("value", default), r.get("unit", "")


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
company = load_company()
with st.sidebar:
    st.markdown(
        f'<div class="sidebar-brand">{ICON_BOLT_SIDEBAR}'
        f'<span class="sidebar-brand-text">Energy Analytics</span></div>',
        unsafe_allow_html=True
    )
    if company:
        st.markdown(f"**{company.get('company_name', '')}**")
        st.caption(f"{company.get('sector', '')} · {company.get('country', '')}")
    st.divider()
    if st.button("Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


# ── DATA ──────────────────────────────────────────────────────────────────────
df_kpi = load_kpi_data()
df_raw = load_raw_data()

if df_kpi.empty:
    st.warning("Sem dados de KPI disponíveis.")
    st.stop()

all_reports = sort_reports(df_kpi["report_id"].unique().tolist())
latest_report = all_reports[-1]
df_latest = df_kpi[df_kpi["report_id"] == latest_report]
latest_label = report_id_to_label(latest_report)
parts = latest_label.split(" ", 1)
month_str = parts[0]
year_str  = parts[1] if len(parts) > 1 else ""

# Aggregated series (one value per report)
df_consumo_series = (
    df_kpi[df_kpi["kpi_name"] == "consumo_total"]
    .groupby("report_id", as_index=False)["value"].mean()
)
df_consumo_series["report_id"] = pd.Categorical(
    df_consumo_series["report_id"], categories=all_reports, ordered=True
)
df_consumo_series = df_consumo_series.sort_values("report_id")
df_consumo_series["label"] = df_consumo_series["report_id"].astype(str).apply(report_id_to_label)

df_renov_series = (
    df_kpi[df_kpi["kpi_name"] == "perc_energia_renovavel"]
    .groupby("report_id", as_index=False)["value"].mean()
)
df_renov_series["report_id"] = pd.Categorical(
    df_renov_series["report_id"], categories=all_reports, ordered=True
)
df_renov_series = df_renov_series.sort_values("report_id")
df_renov_series["label"] = df_renov_series["report_id"].astype(str).apply(report_id_to_label)


# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Energy KPI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Monitorização de consumo energético e sustentabilidade</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="badge-report">{ICON_REPORT} Último relatório &nbsp;·&nbsp; {latest_label}</div>',
    unsafe_allow_html=True
)

# ── HERO KPIs ─────────────────────────────────────────────────────────────────
consumo_val, consumo_unit = get_kpi(df_latest, "consumo_total")
renovavel_val, renov_unit = get_kpi(df_latest, "perc_energia_renovavel")

col_a, col_b, col_spacer = st.columns([1, 1, 1])
with col_a:
    if consumo_val is not None:
        st.markdown(f"""
        <div class="kpi-hero-consumo">
            <div class="kpi-icon-row">
                <div class="kpi-icon-wrap-consumo">{ICON_ZAP}</div>
                <span class="kpi-hero-kpi-name kpi-hero-kpi-name-consumo">Consumo Total</span>
            </div>
            <div class="kpi-hero-month">{month_str}<span class="kpi-hero-year kpi-hero-year-consumo">{year_str}</span></div>
            <div class="kpi-hero-divider-consumo"></div>
            <div class="kpi-hero-value">{consumo_val:,}<span class="kpi-hero-unit kpi-hero-unit-consumo">{consumo_unit}</span></div>
        </div>""", unsafe_allow_html=True)
with col_b:
    if renovavel_val is not None:
        st.markdown(f"""
        <div class="kpi-hero-renov">
            <div class="kpi-icon-row">
                <div class="kpi-icon-wrap-renov">{ICON_LEAF}</div>
                <span class="kpi-hero-kpi-name kpi-hero-kpi-name-renov">Energia Renovável</span>
            </div>
            <div class="kpi-hero-month">{month_str}<span class="kpi-hero-year kpi-hero-year-renov">{year_str}</span></div>
            <div class="kpi-hero-divider-renov"></div>
            <div class="kpi-hero-value">{renovavel_val}<span class="kpi-hero-unit kpi-hero-unit-renov">{renov_unit}</span></div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── CHARTS + DETAIL PANEL ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">Evolução ao Longo do Tempo</div>', unsafe_allow_html=True)

CLICK_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
  fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2l-2 6h6l-5 8 2-6H9l5-8z"/></svg>"""

chart_col1, chart_col2 = st.columns(2)

# ── Bar chart ─────────────────────────────────────────────────────────────────
with chart_col1:
    st.markdown('<div class="chart-title">Consumo Total por Relatório</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="chart-hint">{CLICK_ICON} Clica numa barra para ver os dados do mês</div>',
        unsafe_allow_html=True
    )

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_consumo_series["label"],
        y=df_consumo_series["value"],
        marker=dict(
            color=df_consumo_series["report_id"].astype(str).apply(
                lambda r: "#f59e0b" if r == latest_report else "#fde68a"
            ),
            line=dict(width=0),
            cornerradius=6,
        ),
        hovertemplate="<b>%{x}</b><br>%{y:,} kWh<extra></extra>",
    ))
    fig_bar.update_layout(**PLOT_LAYOUT, height=280,
                          hoverlabel=dict(bgcolor="#111827", font_color="#ffffff", bordercolor="#111827"))
    bar_click = plotly_events(fig_bar, click_event=True, hover_event=False, key="bar_click")

# ── Line chart ────────────────────────────────────────────────────────────────
with chart_col2:
    st.markdown('<div class="chart-title">Energia Renovável % por Relatório</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="chart-hint">{CLICK_ICON} Clica num ponto para ver os dados do mês</div>',
        unsafe_allow_html=True
    )

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_renov_series["label"],
        y=df_renov_series["value"],
        mode="lines+markers",
        line=dict(color="#16a34a", width=2.5),
        marker=dict(size=9, color="#16a34a", line=dict(color="#f0fdf4", width=2)),
        fill="tozeroy",
        fillcolor="rgba(22,163,74,0.08)",
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
    ))
    fig_line.update_layout(**PLOT_LAYOUT, height=280,
                           hoverlabel=dict(bgcolor="#111827", font_color="#ffffff", bordercolor="#111827"))
    fig_line.update_yaxes(range=[0, 100], ticksuffix="%",
                          gridcolor="#f3f4f6", linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)")
    line_click = plotly_events(fig_line, click_event=True, hover_event=False, key="line_click")


# ── DETAIL PANEL ─────────────────────────────────────────────────────────────
def render_detail(clicked_label: str, source: str):
    """Render the detail panel for a clicked month label."""
    report_id = label_to_report_id(clicked_label, all_reports)
    if not report_id:
        return

    df_report = df_kpi[df_kpi["report_id"] == report_id]

    # KPI values for this report
    consumo, c_unit   = get_kpi(df_report, "consumo_total")
    renovavel, r_unit = get_kpi(df_report, "perc_energia_renovavel")

    # Raw documents for this report (match by report_id if column exists, else by month proximity)
    df_docs = pd.DataFrame()
    if not df_raw.empty:
        if "report_id" in df_raw.columns:
            df_docs = df_raw[df_raw["report_id"] == report_id]
        elif "recorded_at" in df_raw.columns:
            try:
                yr, mo = report_id.replace("REP", "").split("_")
                df_docs = df_raw[
                    (df_raw["recorded_at"].dt.year == int(yr)) &
                    (df_raw["recorded_at"].dt.month == int(mo))
                ]
            except Exception:
                df_docs = pd.DataFrame()

    # Build panel HTML
    pill = f'<span class="detail-month-pill">{ICON_CALENDAR} {clicked_label}</span>'

    chips = ""
    if source in ("bar", "line") and consumo is not None:
        chips += f"""
        <div class="kpi-chip kpi-chip-amber">
            <div class="kpi-chip-label kpi-chip-label-amber">{ICON_ZAP_SM} Consumo Total</div>
            <span class="kpi-chip-value">{consumo:,}</span><span class="kpi-chip-unit">{c_unit}</span>
        </div>"""
    if source == "line" and renovavel is not None:
        chips += f"""
        <div class="kpi-chip kpi-chip-green">
            <div class="kpi-chip-label kpi-chip-label-green">{ICON_LEAF_SM} Energia Renovável</div>
            <span class="kpi-chip-value">{renovavel}</span><span class="kpi-chip-unit">{r_unit}</span>
        </div>"""

    st.markdown(f"""
    <div class="detail-panel">
        <div class="detail-header">
            <div class="detail-title-row">{pill}</div>
        </div>
        <div class="detail-section-label">{ICON_ZAP_SM} KPIs do Mês</div>
        <div class="kpi-row">{chips}</div>
    </div>""", unsafe_allow_html=True)

    # Raw documents table
    if not df_docs.empty:
        st.markdown(
            f'<div class="detail-section-label" style="margin-top:16px">{ICON_TABLE_SM} Documentos Originais · {clicked_label}</div>',
            unsafe_allow_html=True
        )
        st.dataframe(df_docs.reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        # Show all KPIs for the report as table fallback
        if not df_report.empty:
            st.markdown(
                f'<div class="detail-section-label" style="margin-top:16px">{ICON_TABLE_SM} Todos os KPIs · {clicked_label}</div>',
                unsafe_allow_html=True
            )
            st.dataframe(df_report.reset_index(drop=True), use_container_width=True, hide_index=True)


# Determine which chart was clicked (bar takes priority if both somehow fire)
clicked_label = None
click_source  = None

if bar_click:
    try:
        clicked_label = bar_click[0]["x"]
        click_source  = "bar"
    except Exception:
        pass

if line_click and not clicked_label:
    try:
        clicked_label = line_click[0]["x"]
        click_source  = "line"
    except Exception:
        pass

if clicked_label:
    st.divider()
    render_detail(clicked_label, click_source)


# ── RAW DOCUMENTS / ALL KPIs ──────────────────────────────────────────────────
st.divider()
with st.expander("Documentos Originais", expanded=False):
    if not df_raw.empty:
        categories = ["Todos"] + sorted(df_raw["category"].unique()) if "category" in df_raw.columns else ["Todos"]
        selected = st.selectbox("Filtrar por Categoria", categories, key="cat_filter")
        df_show = df_raw if selected == "Todos" else df_raw[df_raw["category"] == selected]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("Sem documentos disponíveis.")

with st.expander("Todos os Valores KPI", expanded=False):
    st.dataframe(df_kpi.sort_values(["report_id", "kpi_name"]), use_container_width=True, hide_index=True)
