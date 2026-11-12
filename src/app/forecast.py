"""Forecast tab; all values come from one persisted DSS run."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import text

from src.app.demo_backend import active_session
from src.dss.predictive.run import run_forecasts
from src.pipeline.database import create_db_engine


def _load_forecast(database, selected_run, horizon):
    engine = create_db_engine(database=database)
    try:
        history = pd.read_sql(text("""
            SELECT date_trunc('month', d.full_date)::date AS month_date,
                   SUM(f.sales)::float AS sales,
                   MAX(d.full_date) AS last_order_date
            FROM gold.fact_sales f JOIN gold.dim_date d ON d.date_key=f.order_date_key
            GROUP BY 1 ORDER BY 1
        """), engine)
        if history.empty:
            return history, None, pd.DataFrame()
        # Legacy base DB may not have the new metrics yet.
        has_horizon = pd.read_sql(text("""
            SELECT COUNT(*) AS n FROM information_schema.columns
            WHERE table_schema='dss' AND table_name='forecast_run'
              AND column_name='horizon_months'
        """), engine).iloc[0]["n"] > 0
        has_history_end = pd.read_sql(text("""
            SELECT COUNT(*) AS n FROM information_schema.columns
            WHERE table_schema='dss' AND table_name='forecast_run'
              AND column_name='history_end'
        """), engine).iloc[0]["n"] > 0
        if not has_horizon:
            return history, None, pd.DataFrame()
        history_end = "COALESCE(history_end, train_end)" if has_history_end else "train_end"
        compatible = ("target_metric='sales' AND horizon_months=:horizon "
                      "AND model_name IN ('Seasonal naive', 'Holt-Winters additive')")
        if selected_run is None:
            run = pd.read_sql(text(f"""
                SELECT run_id, model_name, {history_end} AS data_end,
                       mae, rmse, mape, wmape, created_at
                FROM dss.forecast_run
                WHERE {compatible}
                ORDER BY run_id DESC LIMIT 1
            """), engine, params={"horizon": horizon})
        else:
            run = pd.read_sql(text(f"""
                SELECT run_id, model_name, {history_end} AS data_end,
                       mae, rmse, mape, wmape, created_at
                FROM dss.forecast_run WHERE run_id=:run_id AND {compatible}
            """), engine, params={"run_id": selected_run, "horizon": horizon})
        if run.empty:
            return history, None, pd.DataFrame()
        if pd.Timestamp(run.iloc[0]["data_end"]).date() < pd.Timestamp(history.last_order_date.iloc[-1]).date():
            return history, None, pd.DataFrame()
        result = pd.read_sql(text("""
            SELECT forecast_date, predicted_value, lower_bound, upper_bound
            FROM dss.forecast_result WHERE run_id=:run_id AND actual_value IS NULL
            ORDER BY forecast_date LIMIT :horizon
        """), engine, params={"run_id": int(run.iloc[0]["run_id"]), "horizon": horizon})
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
