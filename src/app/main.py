"""Global Superstore decision support dashboard."""

import streamlit as st

from src.app.demo_backend import active_database, active_session
from src.app.executive import render_executive_tab
from src.app.whatif import render_whatif_tab
from src.app.forecast import render_forecast_tab
from src.app.crosssell import render_crosssell_tab
from src.app.upload import render_upload_tab
from src.pipeline.database import database_scope


st.set_page_config(page_title="Global Superstore DSS",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root {
    --ui-blue: #2456A6;
    --ui-blue-dark: #173F7A;
    --ui-blue-light: #EDF4FC;
    --ui-border: #DCE5F0;
    --ui-muted: #5D7089;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
[data-testid="stApp"] button, [data-testid="stApp"] input,
[data-testid="stApp"] textarea, [data-testid="stApp"] select,
[data-testid="stApp"] [data-baseweb="select"],
[data-testid="stApp"] [data-testid="stDataFrame"],
[data-baseweb="popover"], [role="listbox"], [role="option"],
[data-testid="stApp"] .js-plotly-plot svg text {
    font-family: "Times New Roman", Times, serif !important;
}

[data-testid="stAppViewContainer"] {
    background: #F7F9FC;
}

[data-testid="stHeader"] {
    background: rgba(247, 249, 252, 0.96);
}

[data-testid="stMainBlockContainer"] {
    max-width: 1480px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    color: #173453;
    letter-spacing: -0.02em;
    line-height: 1.25;
}

h1 {
    font-size: clamp(1.75rem, 2.6vw, 2.25rem);
    font-weight: 700;
    margin-bottom: 0.3rem;
}

h2, h3 {
    font-weight: 650;
}

[data-testid="stCaptionContainer"] {
    color: var(--ui-muted);
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0.25rem;
    padding: 0.35rem;
    background: #FFFFFF;
    border: 1px solid var(--ui-border);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(20, 52, 88, 0.04);
}

[data-testid="stTabs"] button[role="tab"] {
    min-height: 2.65rem;
    padding: 0.55rem 0.8rem;
    border-radius: 8px;
    color: #48617E;
    font-weight: 550;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--ui-blue-dark);
    background: var(--ui-blue-light);
    font-weight: 650;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: var(--ui-blue);
}

[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    padding-top: 1.2rem;
}

[data-testid="stMetric"] {
    min-height: 112px;
    padding: 1rem 1.1rem;
    border: 1px solid var(--ui-border);
    border-radius: 12px;
    background: #FFFFFF;
    box-shadow: 0 2px 8px rgba(20, 52, 88, 0.035);
}

[data-testid="stMetricLabel"] {
    color: var(--ui-muted);
    font-weight: 550;
}

[data-testid="stMetricValue"] {
    color: var(--ui-blue-dark);
    font-weight: 680;
    font-size: clamp(1.3rem, 1.75vw, 1.7rem);
    line-height: 1.2;
}

[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="input"] {
    border-radius: 9px;
    background: #FFFFFF;
}

[data-testid="stSelectbox"] input[role="combobox"] {
    caret-color: transparent !important;
    cursor: pointer !important;
}

[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"] {
    border: 1px solid var(--ui-border);
    border-radius: 12px;
    background: #FFFFFF;
}

[data-testid="stPlotlyChart"] {
    padding: 0.3rem;
}

[data-testid="stButton"] button {
    border-radius: 9px;
    font-weight: 600;
}

[data-testid="stExpander"] {
    border: 1px solid var(--ui-border);
    border-radius: 10px;
    background: #FFFFFF;
}

@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="stMetric"] {
        min-height: 96px;
    }
}
</style>
""", unsafe_allow_html=True)
st.title("Global Superstore Hệ hỗ trợ quyết định")

try:
    database = active_database()
    session = active_session()
except Exception as exc:
    st.error(f"Không kết nối được PostgreSQL: {exc}")
    st.stop()

if session:
    st.caption(f"Phiên dữ liệu: {session['session_id']}, database {database}")
else:
    st.caption(f"Dữ liệu nền, database {database}")

tabs = st.tabs([
    "Tổng quan kinh doanh",
    "Quyết định giá và chiết khấu",
    "Kế hoạch doanh thu và dự báo",
    "Cơ hội bán kèm",
    "Nạp dữ liệu và đối soát",
])

with database_scope(database):
    with tabs[0]:
        try:
            render_executive_tab()
        except Exception as exc:
            st.error(f"Không đọc được tổng quan từ Gold: {exc}")
    with tabs[1]:
        try:
            render_whatif_tab()
        except Exception as exc:
            st.error(f"Không đọc được dữ liệu cho kịch bản: {exc}")
    with tabs[2]:
        try:
            render_forecast_tab(database)
        except Exception as exc:
            st.error(f"Không đọc được run dự báo: {exc}")
    with tabs[3]:
        try:
            render_crosssell_tab(database)
        except Exception as exc:
            st.error(f"Không đọc được luật bán kèm: {exc}")
    with tabs[4]:
        try:
            render_upload_tab()
        except Exception as exc:
            st.error(f"Không đọc được trạng thái nạp dữ liệu: {exc}")
