import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Energy Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────
# CSS
# ─────────────────────────────────────
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.main {
    background-color: #0b1020;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid rgba(255,255,255,0.05);
}

.block-container {
    padding-top: 2rem;
}

.metric-card {
    background: #151b2e;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 24px;
    transition: 0.2s ease;
}

.metric-card:hover {
    border-color: #5B8CFF;
    transform: translateY(-2px);
}

.metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: white;
}

.metric-label {
    font-size: 0.82rem;
    color: #98A2B3;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 8px;
}

hr {
    border-color: rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# MONGO
# ─────────────────────────────────────
@st.cache_resource
def get_client():

    uri = os.getenv("MONGO_URI")

    if not uri:
        uri = st.secrets.get("MONGO_URI")

    if not uri:
        st.error("MongoDB URI não configurado.")
        st.stop()

    return pymongo.MongoClient(uri)


# ─────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────
@st.cache_data(ttl=60)
def load_kpi_data():

    client = get_client()

    db = client["faturas"]

    data = list(
        db["kpi_value"].find({}, {"_id": 0})
    )

    return pd.DataFrame(data)


@st.cache_data(ttl=60)
def load_raw_data():

    client = get_client()

    db = client["faturas"]

    data = list(
        db["documentos"].find({}, {"_id": 0})
    )

    return pd.DataFrame(data)


# ─────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────
with st.sidebar:

    st.title("Energy Analytics")

    st.caption("Real-Time KPI Monitoring")

    st.divider()

    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.caption(
        f"Updated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

# ─────────────────────────────────────
# HEADER
# ─────────────────────────────────────
st.title("Energy KPI Dashboard")

st.caption(
    "Executive analytics platform for energy consumption and sustainability monitoring."
)

st.divider()

# ─────────────────────────────────────
# DATA
# ─────────────────────────────────────
df_kpi = load_kpi_data()
df_raw = load_raw_data()

if df_kpi.empty:
    st.warning("No KPI data available.")
    st.stop()

# ─────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────
st.subheader("Key Performance Indicators")

reports = (
    df_kpi["report_id"].unique()
    if "report_id" in df_kpi.columns
    else []
)

for report in sorted(reports):

    st.markdown(f"### {report}")

    df_report = df_kpi[df_kpi["report_id"] == report]

    cols = st.columns(len(df_report))

    for i, (_, row) in enumerate(df_report.iterrows()):

        with cols[i]:

            unit = row.get("unit", "")
            value = row.get("value", 0)

            name = (
                row.get("kpi_name", "")
                .replace("_", " ")
                .title()
            )

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">
                    {value} {unit}
                </div>

                <div class="metric-label">
                    {name}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────
# CHARTS
# ─────────────────────────────────────
col1, col2 = st.columns(2)

# CONSUMO
with col1:

    st.subheader("Total Consumption")

    df_consumo = df_kpi[
        df_kpi["kpi_name"] == "consumo_total"
    ]

    if not df_consumo.empty:

        fig = px.bar(
            df_consumo,
            x="report_id",
            y="value",
            template="plotly_dark",
            color_discrete_sequence=["#5B8CFF"]
        )

        fig.update_layout(
            paper_bgcolor="#0b1020",
            plot_bgcolor="#0b1020",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# RENOVAVEL
with col2:

    st.subheader("Renewable Energy")

    df_renov = df_kpi[
        df_kpi["kpi_name"] == "perc_energia_renovavel"
    ]

    if not df_renov.empty:

        fig2 = px.bar(
            df_renov,
            x="report_id",
            y="value",
            template="plotly_dark",
            color_discrete_sequence=["#00C2A8"]
        )

        fig2.update_layout(
            paper_bgcolor="#0b1020",
            plot_bgcolor="#0b1020",
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

st.divider()

# ─────────────────────────────────────
# RAW DATA
# ─────────────────────────────────────
st.subheader("Documents")

if not df_raw.empty:

    if "category" in df_raw.columns:

        categories = (
            ["All"] +
            sorted(df_raw["category"].unique())
        )

        selected = st.selectbox(
            "Category",
            categories
        )

        if selected != "All":

            df_raw = df_raw[
                df_raw["category"] == selected
            ]

    st.dataframe(
        df_raw,
        use_container_width=True
    )

st.divider()

# ─────────────────────────────────────
# KPI TABLE
# ─────────────────────────────────────
st.subheader("All KPIs")

st.dataframe(
    df_kpi,
    use_container_width=True
)
