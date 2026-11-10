"""Gold-backed executive dashboard with one consistent order-date filter."""

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql


PERIODS = ("Toàn bộ", "1 tuần", "30 ngày", "90 ngày", "1 năm", "Tùy chọn")
GRAINS = {"Ngày": "day", "Tuần": "week", "Tháng": "month"}
DEFAULT_GRAIN = {
    "Toàn bộ": "Tháng", "1 tuần": "Ngày", "30 ngày": "Tuần",
    "90 ngày": "Tuần", "1 năm": "Tháng", "Tùy chọn": "Tháng",
}
PRESET_GRAINS = {
    "Toàn bộ": ("Tháng",),
    "1 tuần": ("Ngày",),
    "30 ngày": ("Tuần", "Tháng"),
    "90 ngày": ("Tuần", "Tháng"),
    "1 năm": ("Tuần", "Tháng"),
}


def _query(sql: str, params: dict | None = None) -> pd.DataFrame:
    engine = create_db_engine()
    try:
        return query_sql(engine, sql, params)
    finally:
        engine.dispose()


def _date_key(value: date) -> int:
    return int(value.strftime("%Y%m%d"))


def _date_params(start: date, end: date) -> dict:
    return {"start_key": _date_key(start), "end_key": _date_key(end)}


@st.cache_data(ttl=60)
def load_order_date_bounds() -> tuple[date, date]:
    df = _query("""
        SELECT MIN(d.full_date) AS first_date, MAX(d.full_date) AS last_date
        FROM gold.fact_sales f
        JOIN gold.dim_date d ON f.order_date_key = d.date_key;
    """)
    first, last = df.iloc[0]["first_date"], df.iloc[0]["last_date"]
    if pd.isna(first) or pd.isna(last):
        raise ValueError("Gold chưa có đơn hàng để hiển thị.")
    return pd.Timestamp(first).date(), pd.Timestamp(last).date()


def resolve_period(choice: str, first: date, last: date,
                   custom_start: date | None = None,
                   custom_end: date | None = None) -> tuple[date, date]:
    if choice == "Toàn bộ":
        start, end = first, last
    elif choice == "1 tuần":
        start, end = last - timedelta(days=6), last
    elif choice == "30 ngày":
        start, end = last - timedelta(days=29), last
    elif choice == "90 ngày":
        start, end = last - timedelta(days=89), last
    elif choice == "1 năm":
        start = (pd.Timestamp(last) - pd.DateOffset(years=1) + pd.Timedelta(days=1)).date()
        end = last
    elif choice == "Tùy chọn" and custom_start and custom_end:
        start, end = custom_start, custom_end
    else:
        raise ValueError("Khoảng thời gian không hợp lệ.")
    if choice != "Tùy chọn":
        start = max(start, first)
    if (start >= end if choice == "Tùy chọn" else start > end) or start < first or end > last:
        raise ValueError("Khoảng ngày phải nằm trong dữ liệu Gold; ngày kết thúc phải sau ngày bắt đầu.")
    return start, end


def allowed_grains(choice: str, start: date, end: date) -> tuple[str, ...]:
    if choice != "Tùy chọn":
        return PRESET_GRAINS[choice]
    days = (end - start).days + 1
    if days <= 7:
        return ("Ngày",)
    if days < 30:
        return ("Tuần",)
    if days <= 365:
        return ("Tuần", "Tháng")
    return ("Tháng",)


def _prepare_custom_dates(first: date, last: date) -> None:
    start = st.session_state.get("executive_start")
    end = st.session_state.get("executive_end")
    if not isinstance(start, date) or not first <= start < last:
        start = first
    if not isinstance(end, date) or not first < end <= last:
        end = last
    if start >= end:
        start, end = first, last
    st.session_state["executive_start"] = start
    st.session_state["executive_end"] = end


def prior_year_period(start: date, end: date, first: date) -> tuple[date, date] | None:
    previous_start = (pd.Timestamp(start) - pd.DateOffset(years=1)).date()
    previous_end = (pd.Timestamp(end) - pd.DateOffset(years=1)).date()
    return (previous_start, previous_end) if previous_start >= first else None


@st.cache_data(ttl=60)
def load_period_kpis(start: date, end: date) -> dict:
    df = _query("""
        SELECT COUNT(*) AS line_count,
               COUNT(DISTINCT order_id) AS order_count,
               COALESCE(SUM(sales), 0) AS sales,
               COALESCE(SUM(profit), 0) AS profit,
               COALESCE(AVG(discount), 0) AS avg_discount
        FROM gold.fact_sales
        WHERE order_date_key BETWEEN :start_key AND :end_key;
    """, _date_params(start, end))
    row = df.iloc[0]
    sales, profit = float(row["sales"]), float(row["profit"])
    return {
        "line_count": int(row["line_count"]),
        "order_count": int(row["order_count"]),
        "sales": sales,
        "profit": profit,
        "margin_pct": profit / sales * 100 if sales else 0.0,
        "discount_pct": float(row["avg_discount"]) * 100,
    }


@st.cache_data(ttl=60)
def load_period_trend(start: date, end: date, grain: str) -> pd.DataFrame:
    if grain not in GRAINS:
        raise ValueError("Đơn vị thời gian không hợp lệ.")
    df = _query("""
        SELECT CAST(date_trunc(:grain, d.full_date) AS date) AS period,
               COUNT(DISTINCT f.order_id) AS order_count,
               ROUND(SUM(f.sales), 2) AS sales,
               ROUND(SUM(f.profit), 2) AS profit
        FROM gold.fact_sales f
        JOIN gold.dim_date d ON f.order_date_key = d.date_key
        WHERE f.order_date_key BETWEEN :start_key AND :end_key
        GROUP BY 1 ORDER BY 1;
    """, {**_date_params(start, end), "grain": GRAINS[grain]})
    if not df.empty:
        df[["sales", "profit"]] = df[["sales", "profit"]].astype(float)
        df["period"] = pd.to_datetime(df["period"])
    return df


@st.cache_data(ttl=60)
def load_period_categories(start: date, end: date) -> pd.DataFrame:
    df = _query("""
        SELECT p.category AS category,
               SUM(f.quantity) AS quantity,
               ROUND(SUM(f.sales), 2) AS sales,
               ROUND(SUM(f.profit), 2) AS profit,
               ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
        FROM gold.fact_sales f
        JOIN gold.dim_product p ON f.product_key = p.product_key
        WHERE f.order_date_key BETWEEN :start_key AND :end_key
        GROUP BY p.category ORDER BY sales DESC;
    """, _date_params(start, end))
    if not df.empty:
        df["quantity"] = df["quantity"].astype(int)
        df[["sales", "profit", "margin_pct"]] = df[["sales", "profit", "margin_pct"]].astype(float)
    return df


@st.cache_data(ttl=60)
def load_risk_hotspots(start: date, end: date) -> pd.DataFrame:
    # Requiring three orders avoids raising a red alert from one loss-making line.
    return _query("""
        WITH segments AS (
            SELECT 'Thị trường' AS kind,
                   CONCAT(g.market, ' / ', g.country) AS segment,
                   COUNT(DISTINCT f.order_id) AS orders,
                   ROUND(SUM(f.sales), 2) AS sales,
                   ROUND(SUM(f.profit), 2) AS profit
            FROM gold.fact_sales f
            JOIN gold.dim_geography g ON f.geography_key = g.geography_key
            WHERE f.order_date_key BETWEEN :start_key AND :end_key
            GROUP BY g.market, g.country
            HAVING COUNT(DISTINCT f.order_id) >= 3 AND SUM(f.profit) < 0
            UNION ALL
            SELECT 'Ngành hàng con' AS kind,
                   CONCAT(p.category, ' / ', p.sub_category) AS segment,
                   COUNT(DISTINCT f.order_id) AS orders,
                   ROUND(SUM(f.sales), 2) AS sales,
                   ROUND(SUM(f.profit), 2) AS profit
            FROM gold.fact_sales f
            JOIN gold.dim_product p ON f.product_key = p.product_key
            WHERE f.order_date_key BETWEEN :start_key AND :end_key
            GROUP BY p.category, p.sub_category
            HAVING COUNT(DISTINCT f.order_id) >= 3 AND SUM(f.profit) < 0
        )
        SELECT * FROM segments ORDER BY profit ASC LIMIT 5;
    """, _date_params(start, end))


@st.cache_data(ttl=60)
def load_period_products(start: date, end: date, category: str | None) -> pd.DataFrame:
    df = _query("""
        SELECT p.product_id, p.product_name,
               SUM(f.quantity) AS quantity,
               ROUND(SUM(f.sales), 2) AS sales
        FROM gold.fact_sales f
        JOIN gold.dim_product p ON f.product_key = p.product_key
        WHERE f.order_date_key BETWEEN :start_key AND :end_key
          AND (:category IS NULL OR p.category = :category)
        GROUP BY p.product_id, p.product_name;
    """, {**_date_params(start, end), "category": category})
    if not df.empty:
        df["quantity"] = df["quantity"].astype(int)
        df["sales"] = df["sales"].astype(float)
    return df


def rank_products(products: pd.DataFrame, metric: str, top_n: int) -> pd.DataFrame:
    if metric not in ("quantity", "sales") or top_n not in (5, 7):
        raise ValueError("Tùy chọn top sản phẩm không hợp lệ.")
    ranked = products.sort_values([metric, "product_name", "product_id"],
                                  ascending=[False, True, True]).head(top_n).copy()
    total = float(products[metric].sum())
    ranked["share_pct"] = (ranked[metric] / total * 100).round(3) if total else 0.0
    ranked["short_name"] = ranked["product_name"].str.slice(0, 32)
    return ranked


def _percent_delta(current: float, previous: float | None) -> str | None:
    return f"{(current / previous - 1) * 100:+.1f}% YoY" if previous and previous > 0 else None


def _point_delta(current: float, previous: float | None) -> str | None:
    return f"{current - previous:+.2f} điểm % YoY" if previous is not None else None


def _money(value: float) -> str:
    return f"-${abs(value):,.0f}" if value < 0 else f"${value:,.0f}"


def _sync_grain() -> None:
    st.session_state["executive_grain"] = DEFAULT_GRAIN[st.session_state["executive_period"]]


def render_executive_tab() -> None:
    st.subheader("Tổng quan doanh thu & rủi ro")
    if st.button("Làm mới dữ liệu", key="executive_refresh"):
        st.cache_data.clear()
        st.rerun()

    try:
        first, last = load_order_date_bounds()
    except Exception as exc:
        st.error(f"Không đọc được dữ liệu Gold: {exc}")
        return

    period_col, grain_col = st.columns(2)
    with period_col:
        choice = st.selectbox("Khoảng thời gian", PERIODS, key="executive_period", on_change=_sync_grain)

    custom_start = custom_end = None
    if choice == "Tùy chọn":
        if first >= last:
            st.info("Cần dữ liệu của ít nhất hai ngày để chọn khoảng ngày tùy chỉnh.")
            return
        _prepare_custom_dates(first, last)
        start_col, end_col = st.columns(2)
        with start_col:
            custom_start = st.date_input(
                "Từ ngày", min_value=first,
                max_value=st.session_state["executive_end"] - timedelta(days=1),
                key="executive_start", format="DD/MM/YYYY",
            )
        with end_col:
            custom_end = st.date_input(
                "Đến ngày", min_value=custom_start + timedelta(days=1),
                max_value=last, key="executive_end", format="DD/MM/YYYY",
            )
    try:
        start, end = resolve_period(choice, first, last, custom_start, custom_end)
    except ValueError as exc:
        st.warning(str(exc))
        return

    grain_options = allowed_grains(choice, start, end)
    if st.session_state.get("executive_grain") not in grain_options:
        st.session_state["executive_grain"] = grain_options[0]
    with grain_col:
        grain = st.selectbox("Đơn vị trên biểu đồ xu hướng", grain_options, key="executive_grain")

    st.caption(f"Theo ngày đặt hàng: {start:%d/%m/%Y} – {end:%d/%m/%Y}. Mốc gần nhất trong Gold: {last:%d/%m/%Y}.")
    try:
        current = load_period_kpis(start, end)
        prior_range = prior_year_period(start, end, first) if choice != "Toàn bộ" else None
        previous = load_period_kpis(*prior_range) if prior_range else None
        trend = load_period_trend(start, end, grain)
        categories = load_period_categories(start, end)
        risks = load_risk_hotspots(start, end)
    except Exception as exc:
        st.error(f"Không truy vấn được dữ liệu Gold cho kỳ đã chọn: {exc}")
        return

    if current["line_count"] == 0:
        st.info("Không có đơn hàng trong khoảng thời gian đã chọn.")
        return
    comparable = previous if previous and previous["line_count"] else None
    if choice != "Toàn bộ" and not comparable:
        st.caption("Không đủ dữ liệu cùng kỳ năm trước để tính YoY.")
    cols = st.columns(5)
    cols[0].metric("Doanh thu", _money(current["sales"]),
                   _percent_delta(current["sales"], comparable["sales"] if comparable else None))
    cols[1].metric("Lợi nhuận", _money(current["profit"]),
                   _percent_delta(current["profit"], comparable["profit"] if comparable else None))
    cols[2].metric("Biên lợi nhuận", f"{current['margin_pct']:.2f}%",
                   _point_delta(current["margin_pct"], comparable["margin_pct"] if comparable else None))
    cols[3].metric("Số đơn hàng", f"{current['order_count']:,}",
                   _percent_delta(current["order_count"], comparable["order_count"] if comparable else None))
    cols[4].metric("Chiết khấu TB/dòng", f"{current['discount_pct']:.2f}%",
                   _point_delta(current["discount_pct"], comparable["discount_pct"] if comparable else None),
                   delta_color="inverse")
    if comparable:
        st.caption("YoY so với cùng khoảng ngày năm trước.")
    st.caption("Tỷ lệ hoàn trả chưa hiển thị vì dữ liệu nguồn chưa có thông tin trả hàng đáng tin cậy.")

    st.subheader("Doanh thu và lợi nhuận theo thời gian")
    if trend.empty:
        st.info("Không có dữ liệu xu hướng trong kỳ.")
    else:
        trend = trend.copy()
        date_format = {"Ngày": "%d/%m/%Y", "Tuần": "Tuần %d/%m", "Tháng": "%m/%Y"}[grain]
        trend["label"] = trend["period"].dt.strftime(date_format)
        tick_step = max(1, (len(trend) + 11) // 12)
        tick_labels = trend["label"].iloc[::tick_step].tolist()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=trend["label"], y=trend["sales"], name="Doanh thu ($)",
                             marker_color="#3B82F6"))
        fig.add_trace(go.Scatter(x=trend["label"], y=trend["profit"], name="Lợi nhuận ($)",
                                 mode="lines+markers", yaxis="y2", line=dict(color="#10B981", width=2)))
        fig.update_layout(xaxis_title=f"Thời gian ({grain.lower()})", yaxis_title="Doanh thu ($)",
                          xaxis=dict(type="category", tickangle=-45,
                                     tickmode="array", tickvals=tick_labels),
                          yaxis2=dict(title="Lợi nhuận ($)", overlaying="y", side="right"),
                          hovermode="x unified", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")

    st.subheader("Doanh thu và lợi nhuận theo ngành hàng")
    if categories.empty:
        st.info("Không có ngành hàng trong kỳ.")
    else:
        display_categories = categories.rename(columns={"category": "Ngành hàng", "quantity": "Số lượng",
                                                         "sales": "Doanh thu ($)",
                                                         "profit": "Lợi nhuận ($)", "margin_pct": "Biên lợi nhuận (%)"})
        fig_cat = px.bar(display_categories, x="Ngành hàng", y=["Doanh thu ($)", "Lợi nhuận ($)"],
                         barmode="group", labels={"value": "USD", "variable": "Chỉ số"},
                         color_discrete_sequence=["#3B82F6", "#10B981"])
        st.plotly_chart(fig_cat, width="stretch")
        st.dataframe(display_categories, hide_index=True, width="stretch")

    st.subheader("Điểm rủi ro có lợi nhuận âm")
    st.caption("Xét thị trường/quốc gia và ngành hàng con có ít nhất 3 đơn trong kỳ; xếp theo mức lỗ.")
    if risks.empty:
        st.success("Không có nhóm nào đạt điều kiện cảnh báo trong kỳ đã chọn.")
    else:
        for row in risks.itertuples(index=False):
            st.warning(f"{row.kind}: {row.segment} — {int(row.orders):,} đơn, "
                       f"doanh thu {_money(float(row.sales))}, lợi nhuận {_money(float(row.profit))}.")

    st.subheader("Top sản phẩm bán chạy và tỷ trọng theo ngành hàng")
    category_col, rank_col, top_col = st.columns(3)
    with category_col:
        category_choice = st.selectbox("Ngành hàng của sản phẩm", ["Tất cả", *categories["category"].tolist()],
                                       key="executive_product_category")
    with rank_col:
        rank_choice = st.selectbox("Xếp hạng theo", ["Số lượng", "Doanh thu"], key="executive_rank")
    with top_col:
        top_n = st.selectbox("Số sản phẩm", list(range(5, 11)),
                             index=2, key="executive_top_n")
    try:
        products = load_period_products(start, end, None if category_choice == "Tất cả" else category_choice)
    except Exception as exc:
        st.error(f"Không truy vấn được sản phẩm: {exc}")
        return
    if products.empty:
        st.info("Không có sản phẩm trong bộ lọc đã chọn.")
        return
    metric = "quantity" if rank_choice == "Số lượng" else "sales"
    ranked = rank_products(products, metric, top_n)
    unit = "sản phẩm" if metric == "quantity" else "$"
    st.caption(f"Biểu đồ thanh: top {top_n} sản phẩm trong ngành hàng đã chọn. "
               f"Biểu đồ quạt: tỷ trọng {rank_choice.lower()} của tất cả ngành hàng trong cùng kỳ.")
    bar_col, pie_col = st.columns(2)
    with bar_col:
        st.markdown("**Sản phẩm bán chạy**")
        bar_data = ranked.sort_values(metric)
        fig_bar = px.bar(bar_data, x=metric, y="short_name", orientation="h",
                         labels={metric: f"{rank_choice} ({unit})", "short_name": "Sản phẩm"},
                         hover_data={"product_name": True, "share_pct": ":.2f", "short_name": False})
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, width="stretch")
    with pie_col:
        st.markdown("**Tỷ trọng theo ngành hàng**")
        fig_pie = px.pie(categories, names="category", values=metric, hole=0.4)
        fig_pie.update_traces(textinfo="label+percent",
                              hovertemplate=f"%{{label}}<br>{rank_choice}: %{{value:,.2f}} (%{{percent}})<extra></extra>")
        st.plotly_chart(fig_pie, width="stretch")
