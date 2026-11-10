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
                   SUM(f.sales)::float AS sales
            FROM gold.fact_sales f JOIN gold.dim_date d ON d.date_key=f.order_date_key
            GROUP BY 1 ORDER BY 1
        """), engine)
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
        wmape = "wmape" if has_horizon else "NULL::numeric AS wmape"
        history_end = "COALESCE(history_end, train_end)" if has_history_end else "train_end"
        if not has_horizon and horizon != 6:
            return history, None, pd.DataFrame()
        if selected_run is None:
            condition = "AND horizon_months = :horizon" if has_horizon else ""
            run = pd.read_sql(text(f"""
                SELECT run_id, model_name, {history_end} AS data_end,
                       mae, rmse, mape, {wmape}, created_at
                FROM dss.forecast_run
                WHERE target_metric='sales' {condition}
                ORDER BY run_id DESC LIMIT 1
            """), engine, params={"horizon": horizon})
        else:
            run = pd.read_sql(text(f"""
                SELECT run_id, model_name, {history_end} AS data_end,
                       mae, rmse, mape, {wmape}, created_at
                FROM dss.forecast_run WHERE run_id=:run_id AND target_metric='sales'
            """), engine, params={"run_id": selected_run})
        if run.empty:
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
    st.subheader("Kế hoạch doanh thu & dự báo")
    left, right = st.columns(2)
    window = left.selectbox("Lịch sử hiển thị", ["12 tháng", "24 tháng", "48 tháng", "Toàn bộ"],
                            key="forecast_window")
    horizon = right.selectbox("Chân trời dự báo", [3, 6], index=1, key="forecast_horizon")
    session = active_session()
    selected_run = None
    if session and session["database_name"] == database:
        selected_run = session["forecast_3_id" if horizon == 3 else "forecast_6_id"]
    history, run, forecast = _load_forecast(database, selected_run, horizon)
    if history.empty:
        st.warning("Gold chưa có doanh thu tháng.")
        return
    if run is None or forecast.empty:
        st.warning("Chưa có lần dự báo phù hợp với chân trời đã chọn.")
        if session is None and st.button("Chạy dự báo từ dữ liệu hiện tại", key="forecast_run_now"):
            engine = create_db_engine(database=database)
            try:
                run_forecasts(engine)
            finally:
                engine.dispose()
            st.rerun()
        return
    if window != "Toàn bộ":
        history = history.tail(int(window.split()[0]))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history.month_date, y=history.sales, mode="lines+markers",
                             name="Doanh thu thực", line={"color": "#2563EB"}))
    dates = pd.to_datetime(forecast.forecast_date)
    values = forecast.predicted_value.astype(float)
    fig.add_trace(go.Scatter(x=dates, y=values, mode="lines+markers",
                             name="Dự báo", line={"color": "#EA580C", "dash": "dash"}))
    if forecast.lower_bound.notna().all() and forecast.upper_bound.notna().all():
        fig.add_trace(go.Scatter(
            x=list(dates) + list(dates[::-1]),
            y=forecast.upper_bound.astype(float).tolist() +
              forecast.lower_bound.astype(float).tolist()[::-1],
            fill="toself", fillcolor="rgba(234,88,12,0.15)",
            line={"color": "rgba(0,0,0,0)"}, name="Khoảng sai số backtest"))
    fig.update_layout(xaxis_title="Tháng", yaxis_title="Doanh thu ($)", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    a, b, c, d = st.columns(4)
    a.metric("MAE backtest", f"${float(run.mae):,.2f}")
    b.metric("RMSE backtest", f"${float(run.rmse):,.2f}")
    c.metric("MAPE backtest", f"{float(run.mape):.2f}%")
    d.metric("WMAPE backtest", f"{float(run.wmape):.2f}%" if pd.notna(run.wmape) else "Chưa có")
    st.caption(f"Run #{int(run.run_id)} · {run.model_name} · dữ liệu tới {pd.Timestamp(run.data_end):%d/%m/%Y} "
               f"· chạy lúc {pd.Timestamp(run.created_at):%d/%m/%Y %H:%M}.")
    if run.model_name == "Exponential Smoothing with Trend":
        st.warning("Đây là run dự báo cũ dùng hệ số làm mượt cố định và cách tính sai số chưa chuẩn. "
                   "Chạy dự báo mới để có backtest theo thời gian.")
    else:
        st.caption("Khoảng sai số lấy từ sai lệch backtest theo từng tháng dự báo; "
                   "chưa được hiệu chỉnh thành khoảng tin cậy 95%.")
