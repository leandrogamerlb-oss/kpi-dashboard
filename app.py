import streamlit as st
import pymongo
import pandas as pd
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

/* ── BACKGROUND ── */
.main { background-color: #f4f6f9; }

section[data-testid="stSidebar"] {
    background-color: #1a1f2e;
    border-right: none;
}
section[data-testid="stSidebar"] * { color: #c8d0e0 !important; }
section[data-testid="stSidebar"] h3 { color: #ffffff !important; }
section[data-testid="stSidebar"] strong { color: #ffffff !important; }

.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* ── PAGE TITLE ── */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 400;
    margin-bottom: 20px;
}

/* ── BADGE ── */
.badge-report {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #e8eaf6;
    border: 1px solid #c5cae9;
    color: #3949ab;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 28px;
}

/* ── KPI HERO — CONSUMO (amber) ── */
.kpi-hero-consumo {
    background: linear-gradient(135deg, #fff8ed 0%, #fff3e0 100%);
    border: 1.5px solid #fbc02d;
    border-radius: 20px;
    padding: 28px 32px 26px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(251,192,45,0.15);
}
.kpi-hero-consumo::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(255,193,7,0.18) 0%, transparent 65%);
    pointer-events: none;
}

/* ── KPI HERO — RENOVAVEL (green) ── */
.kpi-hero-renov {
    background: linear-gradient(135deg, #f0fdf4 0%, #e6f7ee 100%);
    border: 1.5px solid #34a853;
    border-radius: 20px;
    padding: 28px 32px 26px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(52,168,83,0.15);
}
.kpi-hero-renov::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(52,168,83,0.14) 0%, transparent 65%);
    pointer-events: none;
}

/* ── SHARED CARD INTERNALS ── */
.kpi-hero-kpi-name {
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.kpi-hero-kpi-name-consumo { color: #b45309; }
.kpi-hero-kpi-name-renov   { color: #166534; }

.kpi-hero-month {
    font-size: 1.7rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 4px;
}
.kpi-hero-year {
    font-size: 1.7rem;
    font-weight: 400;
    margin-left: 10px;
}
.kpi-hero-year-consumo { color: #d97706; }
.kpi-hero-year-renov   { color: #16a34a; }

.kpi-hero-divider-consumo {
    height: 2px;
    background: linear-gradient(90deg, #fbc02d, transparent);
    margin: 16px 0;
    border-radius: 2px;
}
.kpi-hero-divider-renov {
    height: 2px;
    background: linear-gradient(90deg, #34a853, transparent);
    margin: 16px 0;
    border-radius: 2px;
}

.kpi-hero-value {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.04em;
    color: #111827;
}
.kpi-hero-unit {
    font-size: 1rem;
    font-weight: 500;
    margin-left: 6px;
    font-family: 'Syne', sans-serif;
    letter-spacing: 0;
}
.kpi-hero-unit-consumo { color: #92400e; }
.kpi-hero-unit-renov   { color: #166534; }

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #9ca3af;
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
    background: #e5e7eb;
}

/* ── CHART TITLE ── */
.chart-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #6b7280;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

hr { border-color: #e5e7eb !important; }

/* Streamlit expander light theme */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e5e7eb !important;
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
    font=dict(family="Syne, sans-serif", color="#9ca3af", size=11),
    margin=dict(l=10, r=10, t=16, b=10),
    xaxis=dict(
        showgrid=False,
        linecolor="#e5e7eb",
        tickcolor="rgba(0,0,0,0)",
        tickfont=dict(size=10, color="#6b7280"),
    ),
    yaxis=dict(
        gridcolor="#f3f4f6",
        linecolor="rgba(0,0,0,0)",
        tickcolor="rgba(0,0,0,0)",
        tickfont=dict(size=10, color="#6b7280"),
    ),
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

def sort_reports(reports):
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
parts = latest_label.split(" ", 1)
month_str = parts[0]
year_str  = parts[1] if len(parts) > 1 else ""

st.markdown('<div class="page-title">Energy KPI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Monitorização de consumo energético e sustentabilidade</div>', unsafe_allow_html=True)
st.markdown(f'<div class="badge-report">📋 Último relatório · {latest_label}</div>', unsafe_allow_html=True)


# ── HERO KPIs ──────────────────────────────────────────────────────────────────
consumo, consumo_unit = get_kpi(df_latest, "consumo_total")
renovavel, renov_unit = get_kpi(df_latest, "perc_energia_renovavel")

col_a, col_b, col_spacer = st.columns([1, 1, 1])

with col_a:
    if consumo is not None:
        st.markdown(f"""
        <div class="kpi-hero-consumo">
            <div class="kpi-hero-kpi-name kpi-hero-kpi-name-consumo">⚡ Consumo Total</div>
            <div class="kpi-hero-month">
                {month_str}<span class="kpi-hero-year kpi-hero-year-consumo">{year_str}</span>
            </div>
            <div class="kpi-hero-divider-consumo"></div>
            <div class="kpi-hero-value">
                {consumo:,}<span class="kpi-hero-unit kpi-hero-unit-consumo">{consumo_unit}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_b:
    if renovavel is not None:
        st.markdown(f"""
        <div class="kpi-hero-renov">
            <div class="kpi-hero-kpi-name kpi-hero-kpi-name-renov">🌱 Energia Renovável</div>
            <div class="kpi-hero-month">
                {month_str}<span class="kpi-hero-year kpi-hero-year-renov">{year_str}</span>
            </div>
            <div class="kpi-hero-divider-renov"></div>
            <div class="kpi-hero-value">
                {renovavel}<span class="kpi-hero-unit kpi-hero-unit-renov">{renov_unit}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()


# ── CHARTS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Evolução ao Longo do Tempo</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="chart-title">Consumo Total por Relatório</div>', unsafe_allow_html=True)
    df_consumo_all = (
        df_kpi[df_kpi["kpi_name"] == "consumo_total"]
        .groupby("report_id", as_index=False)["value"].mean()
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
                    lambda r: "#f59e0b" if r == latest_report else "#fde68a"
                ),
                line=dict(width=0),
                cornerradius=6,
            ),
            hovertemplate="<b>%{x}</b><br>%{y:,} kWh<extra></extra>",
        ))
        fig.update_layout(**PLOT_LAYOUT, height=280)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de consumo.")

with chart_col2:
    st.markdown('<div class="chart-title">Energia Renovável % por Relatório</div>', unsafe_allow_html=True)
    df_renov_all = (
        df_kpi[df_kpi["kpi_name"] == "perc_energia_renovavel"]
        .groupby("report_id", as_index=False)["value"].mean()
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
            line=dict(color="#16a34a", width=2.5),
            marker=dict(size=8, color="#16a34a", line=dict(color="#f0fdf4", width=2)),
            fill="tozeroy",
            fillcolor="rgba(22,163,74,0.08)",
            hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
        ))
        fig2.update_layout(**PLOT_LAYOUT, height=280)
        fig2.update_yaxes(
            range=[0, 100],
            ticksuffix="%",
            gridcolor="#f3f4f6",
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
