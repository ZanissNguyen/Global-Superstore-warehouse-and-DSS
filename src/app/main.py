"""Global Superstore decision support dashboard."""

import streamlit as st

from src.app.demo_backend import active_database, active_session
from src.app.executive import render_executive_tab
from src.app.whatif import render_whatif_tab
from src.app.forecast import render_forecast_tab
from src.app.crosssell import render_crosssell_tab
from src.app.upload import render_upload_tab
from src.pipeline.database import database_scope


st.set_page_config(page_title="Global Superstore DSS", page_icon="🛍️",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
[data-testid="stSelectbox"] input[role="combobox"] {
    caret-color: transparent !important;
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)
st.title("Global Superstore · Hệ hỗ trợ quyết định")

try:
    database = active_database()
    session = active_session()
except Exception as exc:
    st.error(f"Không kết nối được PostgreSQL: {exc}")
    st.stop()

if session:
    st.caption(f"Phiên dữ liệu: {session['session_id']} · database {database}")
else:
    st.caption(f"Dữ liệu nền · database {database}")

tabs = st.tabs([
    "Tổng quan kinh doanh",
    "Quyết định giá & chiết khấu",
    "Kế hoạch doanh thu & dự báo",
    "Cơ hội bán kèm",
    "Nạp dữ liệu & đối soát",
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
