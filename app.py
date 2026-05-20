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
    page_title="KPI Dashboard",
    page_icon="📊",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3154;
        text-align: center;
    }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: #7c83fd; }
    .metric-label { font-size: 0.9rem; color: #8b8fa8; margin-top: 5px; }
    h1 { color: #ffffff !important; }
    h2, h3 { color: #c5c7d4 !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_client():
    uri = os.getenv("MONGO_URI") or st.secrets["MONGO_URI"]
    return pymongo.MongoClient(uri)


def load_kpi_data():
    client = get_client()
    db = client["faturas"]
    data = list(db["kpi_value"].find({}, {"_id": 0}))
    return pd.DataFrame(data) if data else pd.DataFrame()


def load_raw_data():
    client = get_client()
    db = client["faturas"]
    data = list(db["documentos"].find({}, {"_id": 0}))
    return pd.DataFrame(data) if data else pd.DataFrame()


# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 KPI Dashboard — Energia")
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# Load data
df_kpi = load_kpi_data()
df_raw = load_raw_data()

if df_kpi.empty:
    st.warning("Sem dados de KPI disponíveis.")
    st.stop()

# Auto-refresh info
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} — Os dados são carregados em tempo real do MongoDB.")

st.markdown("---")

# ── KPI CARDS ──
st.subheader("📌 KPIs por Report")

reports = df_kpi["report_id"].unique() if "report_id" in df_kpi.columns else []

for report in sorted(reports):
    st.markdown(f"### 📁 {report}")
    df_report = df_kpi[df_kpi["report_id"] == report]
    cols = st.columns(len(df_report))
    for i, (_, row) in enumerate(df_report.iterrows()):
        with cols[i]:
            unit = row.get("unit", "")
            value = row.get("value", 0)
            name = row.get("kpi_name", "").replace("_", " ").title()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value} <span style="font-size:1rem">{unit}</span></div>
                <div class="metric-label">{name}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("")

st.markdown("---")

# ── GRÁFICOS ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Consumo Total por Report")
    df_consumo = df_kpi[df_kpi["kpi_name"] == "consumo_total"] if "kpi_name" in df_kpi.columns else pd.DataFrame()
    if not df_consumo.empty:
        fig = px.bar(
            df_consumo,
            x="report_id",
            y="value",
            color="report_id",
            labels={"value": "kWh", "report_id": "Report"},
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#c5c7d4",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de consumo total.")

with col2:
    st.subheader("🌿 % Energia Renovável por Report")
    df_renov = df_kpi[df_kpi["kpi_name"] == "perc_energia_renovavel"] if "kpi_name" in df_kpi.columns else pd.DataFrame()
    if not df_renov.empty:
        fig2 = px.bar(
            df_renov,
            x="report_id",
            y="value",
            color="report_id",
            labels={"value": "%", "report_id": "Report"},
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#c5c7d4",
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de energia renovável.")

st.markdown("---")

# ── DADOS RAW ──
if not df_raw.empty:
    st.subheader("📄 Dados Raw — Documentos")

    if "category" in df_raw.columns:
        categories = ["Todas"] + sorted(df_raw["category"].unique().tolist())
        selected = st.selectbox("Filtrar por categoria", categories)
        if selected != "Todas":
            df_raw = df_raw[df_raw["category"] == selected]

    st.dataframe(df_raw, use_container_width=True)

st.markdown("---")

# ── TABELA KPIs ──
st.subheader("📋 Todos os KPIs")
st.dataframe(df_kpi, use_container_width=True)
