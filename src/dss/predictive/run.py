"""Monthly Gold sales forecasting with chronological backtests."""

import argparse
import json

import numpy as np
import pandas as pd
from sqlalchemy import text

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql
from src.pipeline.reader import read_sql


def extract_sales_series(engine):
    df = query_sql(engine, read_sql("dss/forecast/extract_sales_series.sql"))
    if df.empty:
        raise ValueError("Gold chưa có dữ liệu để dự báo.")
    dates = pd.to_datetime(df.month_date)
    if len(pd.date_range(dates.iloc[0], dates.iloc[-1], freq="MS")) != len(df):
        raise ValueError("Chuỗi tháng có khoảng trống; cần xử lý trước khi dự báo.")
    return df


def _seasonal_naive(values, horizon):
    return np.array([values[-12 + h % 12] for h in range(horizon)], dtype=float)


def _ets(values, horizon, alpha, beta, gamma):
    values = np.asarray(values, dtype=float)
    if len(values) < 24:
        raise ValueError("Holt-Winters cần ít nhất 24 tháng lịch sử.")
    level = float(np.mean(values[:12]))
    trend = float((np.mean(values[12:24]) - level) / 12)
    season = (values[:12] - level).astype(float).copy()
    fitted = []
    for i, actual in enumerate(values):
        old = level
        seasonal = season[i % 12]
        fitted.append(level + trend + seasonal)
        level = alpha * (actual - seasonal) + (1 - alpha) * (level + trend)
        trend = beta * (level - old) + (1 - beta) * trend
        season[i % 12] = gamma * (actual - level) + (1 - gamma) * seasonal
    future = [level + (h + 1) * trend + season[(len(values) + h) % 12]
              for h in range(horizon)]
    return np.maximum(0, future), np.asarray(fitted)


def _fit_ets(values, horizon):
    best = None
    for alpha in (0.1, 0.3, 0.5, 0.7, 0.9):
        for beta in (0.1, 0.3, 0.5):
            for gamma in (0.1, 0.3, 0.5):
                pred, fitted = _ets(values, horizon, alpha, beta, gamma)
                score = float(np.mean(np.abs(values[12:] - fitted[12:])))
                if best is None or score < best[0]:
                    best = (score, pred, (alpha, beta, gamma))
    return best[1], best[2]


def fit_forecast(df, target_col="total_sales", horizon=6):
    if horizon not in (3, 6):
        raise ValueError("Chỉ hỗ trợ chân trời 3 hoặc 6 tháng.")
    values = df[target_col].astype(float).to_numpy()
    n = len(values)
    if n < 30:
        raise ValueError("Cần ít nhất 30 tháng lịch sử để backtest.")
    origins = [i for i in (n - 18, n - 12, n - 6) if i >= 24]
    errors = {"Seasonal naive": [], "Holt-Winters additive": []}
    actuals = []
    for origin in origins:
        train = values[:origin]
        actual = values[origin:origin + horizon]
        actuals.extend(actual)
        errors["Seasonal naive"].append(actual - _seasonal_naive(train, horizon))
        ets_pred, _ = _fit_ets(train, horizon)
        errors["Holt-Winters additive"].append(actual - ets_pred)
    model = min(errors, key=lambda name: np.mean(np.abs(np.concatenate(errors[name]))))
    residuals = np.stack(errors[model])
    future, params = (_seasonal_naive(values, horizon), {}) if model == "Seasonal naive" else _fit_ets(values, horizon)
    if model != "Seasonal naive":
        params = dict(zip(("alpha", "beta", "gamma"), params))
    flat = residuals.ravel()
    dates = pd.to_datetime(df.month_date)
    future_dates = pd.date_range(dates.iloc[-1] + pd.DateOffset(months=1), periods=horizon, freq="MS")
    widths = np.max(np.abs(residuals), axis=0)
    return {
        "model_name": model, "params": params, "horizon": horizon,
        "train_start": dates.iloc[0].date(), "train_end": dates.iloc[origins[0] - 1].date(),
        "history_end": pd.Timestamp(df.last_order_date.iloc[-1]).date(),
        "test_start": dates.iloc[origins[0]].date(), "test_end": dates.iloc[-1].date(),
        "mae": float(np.mean(np.abs(flat))), "rmse": float(np.sqrt(np.mean(flat ** 2))),
        "mape": float(np.mean(np.abs(flat) / np.maximum(np.abs(actuals), 1)) * 100),
        "wmape": float(np.sum(np.abs(flat)) / max(np.sum(np.abs(actuals)), 1) * 100),
        "future_dates": future_dates, "future_preds": future.tolist(),
        "lower_bounds": np.maximum(0, future - widths).tolist(),
        "upper_bounds": (future + widths).tolist(),
    }


def persist_forecast(engine, target_metric, result):
    with engine.begin() as conn:
        conn.execute(text(read_sql("dss/forecast/upgrade_run.sql")))
        run_id = conn.execute(text(read_sql("dss/forecast/insert_run.sql")), {"model": result["model_name"], "target": target_metric,
                "train_start": result["train_start"], "train_end": result["train_end"],
                "test_start": result["test_start"], "test_end": result["test_end"],
                "mae": result["mae"], "rmse": result["rmse"], "mape": result["mape"],
                "horizon": result["horizon"], "wmape": result["wmape"],
                "params": json.dumps(result["params"]),
                "history_end": result["history_end"]}).scalar_one()
        for dt, pred, low, high in zip(result["future_dates"], result["future_preds"],
                                       result["lower_bounds"], result["upper_bounds"]):
            conn.execute(text(read_sql("dss/forecast/insert_result.sql")), {"run_id": run_id, "dt": dt.date(), "pred": float(pred),
                    "low": float(low), "high": float(high)})
    return run_id


def run_forecasts(engine):
    df = extract_sales_series(engine)
    return {h: persist_forecast(engine, "sales", fit_forecast(df, horizon=h))
            for h in (3, 6)}


def main():
    parser = argparse.ArgumentParser(description="Forecast monthly Gold sales")
    parser.add_argument("--target", choices=("sales", "quantity"), default="sales")
    parser.add_argument("--horizon", type=int, choices=(3, 6), default=6)
    args = parser.parse_args()
    engine = create_db_engine()
    try:
        df = extract_sales_series(engine)
        target = "total_sales" if args.target == "sales" else "total_quantity"
        result = fit_forecast(df, target, args.horizon)
        run_id = persist_forecast(engine, args.target, result)
        print(f"Forecast run #{run_id}: {result['model_name']}, MAE={result['mae']:.2f}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
