"""Forecast tab; all values come from one persisted DSS run."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import text

from src.app.demo_backend import active_session
from src.dss.predictive.run import run_forecasts
from src.pipeline.database import create_db_engine
from src.pipeline.reader import read_sql


def _load_forecast(database, selected_run, horizon):
    engine = create_db_engine(database=database)
    try:
        history = pd.read_sql(text(read_sql("dss/forecast/monthly_history.sql")), engine)
        if history.empty:
            return history, None, pd.DataFrame()
        # Legacy base DB may not have the new metrics yet.
        has_horizon = pd.read_sql(text(read_sql("dss/forecast/has_horizon_column.sql")), engine).iloc[0]["n"] > 0
        has_history_end = pd.read_sql(text(read_sql("dss/forecast/has_history_end_column.sql")), engine).iloc[0]["n"] > 0
        if not has_horizon:
            return history, None, pd.DataFrame()
        run_kind = "latest" if selected_run is None else "selected"
        schema_kind = "history" if has_history_end else "legacy"
        run_sql = read_sql(f"dss/forecast/{run_kind}_run_{schema_kind}.sql")
        params = {"horizon": horizon}
        if selected_run is not None:
            params["run_id"] = selected_run
        run = pd.read_sql(text(run_sql), engine, params=params)
        if run.empty:
            return history, None, pd.DataFrame()
        if pd.Timestamp(run.iloc[0]["data_end"]).date() < pd.Timestamp(history.last_order_date.iloc[-1]).date():
            return history, None, pd.DataFrame()
        result = pd.read_sql(text(read_sql("dss/forecast/future_results.sql")), engine, params={"run_id": int(run.iloc[0]["run_id"]), "horizon": horizon})
        return history, run.iloc[0], result
    finally:
        engine.dispose()


def render_forecast_tab(database):
    st.subheader("Kế hoạch doanh thu và dự báo")
    window = st.selectbox("Lịch sử hiển thị", ["12 tháng", "24 tháng", "48 tháng", "Toàn bộ"],
                          key="forecast_window")
    horizon = 6
    st.caption("Dự báo cố định cho 6 tháng tiếp theo.")
    session = active_session()
    selected_run = None
    if session and session["database_name"] == database:
        selected_run = session["forecast_6_id"]
    history, run, forecast = _load_forecast(database, selected_run, horizon)
    if session is None and not history.empty and (run is None or forecast.empty):
        with st.spinner("Đang tạo dự báo 6 tháng cho dữ liệu nền..."):
            engine = create_db_engine(database=database)
            try:
                run_forecasts(engine)
            finally:
                engine.dispose()
        history, run, forecast = _load_forecast(database, None, horizon)
    if history.empty:
        st.warning("Gold chưa có doanh thu tháng.")
        return
    if run is None or forecast.empty:
        st.warning("Chưa có run dự báo 6 tháng hợp lệ cho phiên dữ liệu này.")
        return
    if window != "Toàn bộ":
        history = history.tail(int(window.split()[0]))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history.month_date, y=history.sales, mode="lines+markers",
                             name="Doanh thu thực", line={"color": "#3973C7"}))
    dates = pd.to_datetime(forecast.forecast_date)
    values = forecast.predicted_value.astype(float)
    fig.add_trace(go.Scatter(x=dates, y=values, mode="lines+markers",
                             name="Dự báo", line={"color": "#3A8F9E", "dash": "dash"}))
    if forecast.lower_bound.notna().all() and forecast.upper_bound.notna().all():
        fig.add_trace(go.Scatter(
            x=list(dates) + list(dates[::-1]),
            y=forecast.upper_bound.astype(float).tolist() +
              forecast.lower_bound.astype(float).tolist()[::-1],
            fill="toself", fillcolor="rgba(58,143,158,0.14)",
            line={"color": "rgba(0,0,0,0)"}, name="Khoảng sai số backtest"))
    fig.update_layout(xaxis_title="Tháng", yaxis_title="Doanh thu USD", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    a, b, c, d = st.columns(4)
    a.metric("MAE backtest", f"${float(run.mae):,.2f}")
    b.metric("RMSE backtest", f"${float(run.rmse):,.2f}")
    c.metric("MAPE backtest", f"{float(run.mape):.2f}%")
    d.metric("WMAPE backtest", f"{float(run.wmape):.2f}%" if pd.notna(run.wmape) else "Chưa có")
    st.caption(f"Lần chạy {int(run.run_id)}, {run.model_name}, dữ liệu tới {pd.Timestamp(run.data_end):%d/%m/%Y}, "
               f"chạy lúc {pd.Timestamp(run.created_at):%d/%m/%Y %H:%M}.")
    st.caption("Khoảng sai số lấy từ sai lệch backtest theo từng tháng dự báo; "
               "chưa được hiệu chỉnh thành khoảng tin cậy 95%.")
