"""Gold-backed discount scenario with a time-filtered baseline."""

import plotly.express as px
import pandas as pd
import streamlit as st

from src.app.executive import PERIODS, load_order_date_bounds, resolve_period, _query
from src.dss.what_if.simulate import run_what_if_simulation


def render_whatif_tab():
    st.subheader("Quyết định giá và chiết khấu")
    st.caption("Đây là kịch bản giả định theo độ co giãn do người dùng chọn; không thay đổi dữ liệu thực trong Gold.")
    first, last = load_order_date_bounds()
    period = st.selectbox("Khoảng thời gian", PERIODS, key="whatif_period")
    if period == "Tùy chọn":
        left, right = st.columns(2)
        start = left.date_input("Từ ngày", value=first, min_value=first,
                                max_value=last - pd.Timedelta(days=1), key="whatif_start")
        end = right.date_input("Đến ngày", value=last,
                               min_value=start + pd.Timedelta(days=1),
                               max_value=last, key="whatif_end")
    else:
        start = end = None
    start, end = resolve_period(period, first, last, start, end)
    st.caption(f"Dữ liệu nền từ {start:%d/%m/%Y} đến {end:%d/%m/%Y}.")
    options = _query("""
        SELECT DISTINCT g.market FROM gold.dim_geography g ORDER BY g.market
    """)["market"].dropna().tolist()
    categories = _query("""
        SELECT DISTINCT p.category FROM gold.dim_product p ORDER BY p.category
    """)["category"].dropna().tolist()
    col1, col2 = st.columns(2)
    market = col1.selectbox("Thị trường", ["Tất cả", *options], key="whatif_market")
    category = col2.selectbox("Ngành hàng", ["Tất cả", *categories], key="whatif_category")
    baseline = _query("""
        SELECT COALESCE(SUM(f.sales), 0) AS sales,
               COALESCE(SUM(f.profit), 0) AS profit,
               COALESCE(AVG(f.discount), 0) AS discount,
               COUNT(*) AS lines
        FROM gold.fact_sales f
        JOIN gold.dim_geography g ON g.geography_key = f.geography_key
        JOIN gold.dim_product p ON p.product_key = f.product_key
        WHERE f.order_date_key BETWEEN :start_key AND :end_key
          AND (:market = 'Tất cả' OR g.market = :market)
          AND (:category = 'Tất cả' OR p.category = :category)
    """, {"start_key": int(start.strftime("%Y%m%d")), "end_key": int(end.strftime("%Y%m%d")),
          "market": market, "category": category}).iloc[0]
    if not baseline["lines"]:
        st.info("Không có giao dịch trong bộ lọc này.")
        return
    sales, profit, discount = map(float, (baseline["sales"], baseline["profit"], baseline["discount"]))
    c1, c2, c3 = st.columns(3)
    c1.metric("Doanh thu thực", f"${sales:,.2f}")
    c2.metric("Lợi nhuận thực", f"${profit:,.2f}")
    c3.metric("Chiết khấu bình quân", f"{discount * 100:.1f}%")
    adj = st.slider("Thay đổi chiết khấu theo điểm phần trăm", -15.0, 30.0, 5.0, 0.5,
                    key="whatif_adjustment") / 100
    elasticity = st.slider("Độ co giãn giả định", 0.5, 3.0, 1.4, 0.1,
                           key="whatif_elasticity")
    result = run_what_if_simulation(sales, profit, discount, adj, elasticity)
    sim = result["simulated"]
    a, b, c = st.columns(3)
    a.metric("Doanh thu kịch bản", f"${sim['sales']:,.2f}", f"{sim['sales_change_pct']:+.1f}%")
    b.metric("Lợi nhuận kịch bản", f"${sim['profit']:,.2f}", f"{sim['profit_change_pct']:+.1f}%")
    c.metric("Biên lợi nhuận kịch bản", f"{sim['margin_pct']:.1f}%")
    chart = pd.DataFrame({
        "Kịch bản": ["Thực tế", "Giả định"],
        "Doanh thu": [sales, sim["sales"]],
        "Lợi nhuận": [profit, sim["profit"]],
    })
    st.plotly_chart(px.bar(chart, x="Kịch bản", y=["Doanh thu", "Lợi nhuận"],
                           barmode="group",
                           color_discrete_sequence=["#3973C7", "#3A8F9E"]), width="stretch")
    status = result["recommendation"]["status"]
    message = result["recommendation"]["message"]
    if "REJECT" in status:
        st.error(message)
    elif "CAUTION" in status:
        st.warning(message)
    else:
        st.success(message)
    st.caption("Mô hình chỉ giả định nhu cầu thay đổi theo độ co giãn; chưa ước lượng độ co giãn từ giao dịch.")
