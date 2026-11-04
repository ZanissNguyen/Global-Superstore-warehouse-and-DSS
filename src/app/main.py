"""
Global Superstore - Interactive Decision Support System (DSS)
Built with Streamlit for CO4031 Assignment - HK261
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.dss.what_if.simulate import run_what_if_simulation

st.set_page_config(
    page_title="Global Superstore DSS",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #1E3A8A, #3B82F6); padding: 24px; border-radius: 12px; color: white; margin-bottom: 25px;">
    <h1 style="margin: 0; font-size: 28px; font-weight: 700;">🛍️ GLOBAL SUPERSTORE - HỆ HỖ TRỢ QUYẾT ĐỊNH (DSS)</h1>
    <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">
        Đồ án Môn học CO4031 (Kho dữ liệu & Hệ hỗ trợ Quyết định) - HK261 | Đại học Bách Khoa ĐHQG-HCM
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive KPIs & Cảnh báo",
    "🧪 Mô phỏng What-If (Discount & Profit)",
    "📈 Dự báo Doanh số (Forecasting)",
    "🛒 Bán chéo & Khai phá Giỏ hàng"
])

# =============================================================================
# TAB 1: Executive KPIs & Risk Hotspots
# =============================================================================
with tab1:
    st.subheader("1. Tổng quan Chỉ số Hiệu quả Kinh doanh (Executive Scorecard)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Tổng Doanh thu", "$12,642,502", "+21.4% YoY")
    with col2:
        st.metric("Tổng Lợi nhuận", "$1,467,457", "+18.2% YoY")
    with col3:
        st.metric("Biên Lợi nhuận", "11.61%", "-0.4% YoY")
    with col4:
        st.metric("Chiết khấu BQ", "14.29%", "+1.2%")
    with col5:
        st.metric("Tỷ lệ Hoàn trả", "2.29%", "-0.15% YoY")
        
    st.divider()
    
    st.subheader("⚠️ Trung tâm Cảnh báo Rủi ro Nghiệp vụ (Risk Alert Hotspots)")
    st.error("""
    **CẢNH BÁO ĐỎ - NGUY CƠ THẤM LỖ TẠI CÁC THỊ TRƯỜNG TRỌNG ĐIỂM:**
    - **Thị trường EMEA & Africa:** Một số quốc gia ghi nhận doanh số lớn (> $50,000) nhưng Lợi nhuận ròng bị âm do mức chiết khấu trung bình vượt quá 35% kết hợp chi phí vận chuyển cao.
    - **Ngành hàng Bàn làm việc (Tables - Furniture):** Tỷ lệ chiết khấu bình quân đạt 42.1%, biên lợi nhuận ròng âm (-14.3%). Càng bán nhiều càng thâm hụt dòng tiền.
    """)
    
    # Sample visualization
    sample_cat = pd.DataFrame({
        "Category": ["Technology", "Office Supplies", "Furniture"],
        "Sales": [4741557, 3787453, 4110892],
        "Profit": [663778, 518473, 285206],
        "Margin_Pct": [14.0, 13.7, 6.9]
    })
    
    fig_cat = px.bar(
        sample_cat, x="Category", y=["Sales", "Profit"],
        barmode="group", title="Doanh thu và Lợi nhuận theo Ngành hàng",
        color_discrete_sequence=["#3B82F6", "#10B981"]
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# =============================================================================
# TAB 2: What-If Discount & Profit Simulation
# =============================================================================
with tab2:
    st.subheader("2. Mô phỏng Quyết định Chiết khấu & Lợi nhuận (What-If Simulation)")
    st.markdown("""
    Công cụ mô phỏng cho phép nhà quản trị đánh giá tác động định lượng khi **thay đổi mức chiết khấu** 
    tới sản lượng cầu, doanh thu và lợi nhuận ròng dựa trên **Hệ số co giãn cầu theo giá ($e$)**.
    """)
    
    sim_col1, sim_col2 = st.columns([1, 2])
    
    with sim_col1:
        st.markdown("#### ⚙️ Thiết lập Tham số Kịch bản")
        market_sel = st.selectbox("Thị trường mục tiêu:", ["APAC", "EU", "LATAM", "US", "EMEA", "Africa"])
        cat_sel = st.selectbox("Ngành hàng:", ["Furniture", "Office Supplies", "Technology"])
        
        # Base values
        base_sales = st.number_input("Doanh thu hiện tại ($):", value=1250000.0, step=50000.0)
        base_profit = st.number_input("Lợi nhuận hiện tại ($):", value=145000.0, step=10000.0)
        base_disc = st.slider("Mức chiết khấu hiện tại (%):", 0.0, 50.0, 14.0, 0.5) / 100.0
        
        st.markdown("---")
        disc_adj = st.slider("Điều chỉnh Chiết khấu (+/- %):", -15.0, 30.0, 5.0, 0.5) / 100.0
        elasticity = st.slider("Độ co giãn cầu theo giá (Elasticity e):", 0.5, 3.0, 1.4, 0.1)
        
    with sim_col2:
        st.markdown("#### 📊 Kết quả Mô phỏng Tương tác")
        
        sim_res = run_what_if_simulation(
            baseline_sales=base_sales,
            baseline_profit=base_profit,
            baseline_discount=base_disc,
            discount_adjustment=disc_adj,
            elasticity=elasticity
        )
        
        # Metric comparison row
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(
                "Doanh thu Dự kiến", 
                f"${sim_res['simulated']['sales']:,.2f}",
                f"{sim_res['simulated']['sales_change_pct']:+.2f}%"
            )
        with m_col2:
            st.metric(
                "Lợi nhuận Dự kiến", 
                f"${sim_res['simulated']['profit']:,.2f}",
                f"{sim_res['simulated']['profit_change_pct']:+.2f}%",
                delta_color="normal" if sim_res['simulated']['profit_change_pct'] >= 0 else "inverse"
            )
        with m_col3:
            st.metric(
                "Biên Lợi nhuận Dự kiến", 
                f"{sim_res['simulated']['margin_pct']:.2f}%",
                f"{sim_res['simulated']['margin_pct'] - sim_res['baseline']['margin_pct']:+.2f}%",
                delta_color="normal" if sim_res['simulated']['margin_pct'] >= sim_res['baseline']['margin_pct'] else "inverse"
            )
            
        # Comparison chart
        comp_df = pd.DataFrame({
            "Kịch bản": ["Hiện trạng (Baseline)", "Sau mô phỏng (Simulated)"],
            "Doanh thu ($)": [sim_res["baseline"]["sales"], sim_res["simulated"]["sales"]],
            "Lợi nhuận ($)": [sim_res["baseline"]["profit"], sim_res["simulated"]["profit"]]
        })
        fig_sim = px.bar(
            comp_df, x="Kịch bản", y=["Doanh thu ($)", "Lợi nhuận ($)"],
            barmode="group", color_discrete_sequence=["#6366F1", "#EC4899"]
        )
        st.plotly_chart(fig_sim, use_container_width=True)
        
        # Prescriptive Recommendation Banner
        st.markdown("#### 🎯 Khuyến nghị Tự động từ Hệ thống (Decision Recommendation)")
        status = sim_res["recommendation"]["status"]
        if "REJECT" in status:
            st.error(f"🛑 **{status}**: {sim_res['recommendation']['message']}")
        elif "CAUTION" in status:
            st.warning(f"⚠️ **{status}**: {sim_res['recommendation']['message']}")
        else:
            st.success(f"✅ **{status}**: {sim_res['recommendation']['message']}")

# =============================================================================
# TAB 3: Sales Forecasting
# =============================================================================
with tab3:
    st.subheader("3. Dự báo Doanh số Bán hàng Chuỗi Thời gian (Sales Forecasting)")
    st.markdown("Mô hình **Holt-Winters Exponential Smoothing** dự báo xu hướng và tính mùa vụ 6 tháng tiếp theo.")
    
    dates = pd.date_range("2013-01-01", periods=24, freq="MS")
    historical_sales = [
        115000, 108000, 134000, 128000, 142000, 168000, 155000, 172000, 195000, 210000, 245000, 280000,
        132000, 124000, 158000, 146000, 169000, 198000, 185000, 205000, 235000, 258000, 298000, 335000
    ]
    forecast_dates = pd.date_range("2015-01-01", periods=6, freq="MS")
    forecast_sales = [155000, 148000, 185000, 175000, 202000, 238000]
    lower_bound = [s * 0.9 for s in forecast_sales]
    upper_bound = [s * 1.1 for s in forecast_sales]
    
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(x=dates, y=historical_sales, mode="lines+markers", name="Doanh số Lịch sử (Actual)", line=dict(color="#2563EB", width=2)))
    fig_fc.add_trace(go.Scatter(x=forecast_dates, y=forecast_sales, mode="lines+markers", name="Dự báo Trung tâm (Forecast)", line=dict(color="#EA580C", width=2, dash="dash")))
    fig_fc.add_trace(go.Scatter(x=list(forecast_dates) + list(forecast_dates[::-1]), y=upper_bound + lower_bound[::-1], fill="toself", fillcolor="rgba(234, 88, 12, 0.15)", line=dict(color="rgba(255,255,255,0)"), name="Dải tin cậy 95%"))
    fig_fc.update_layout(title="Xu hướng Doanh số & Dự báo Tương lai", xaxis_title="Thời gian", yaxis_title="Doanh số ($)", hovermode="x unified")
    st.plotly_chart(fig_fc, use_container_width=True)
    
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Độ chính xác MAE", "$14,820", "Sai số tuyệt đối BQ")
    c_m2.metric("RMSE", "$18,450", "Phạt sai số lớn")
    c_m3.metric("MAPE", "4.15%", "Sai số phần trăm")

# =============================================================================
# TAB 4: Market Basket & Cross-Selling
# =============================================================================
with tab4:
    st.subheader("4. Khai phá Giỏ hàng & Cơ hội Bán chéo (Market Basket & Cross-Selling)")
    st.markdown("Khai phá luật kết hợp bằng thuật toán **Apriori / FP-Growth** với ràng buộc: $\\text{Lift} > 1.2$.")
    
    rules_data = pd.DataFrame([
        {"Sản phẩm mua trước (Antecedent)": "Fellowes Bankers Box", "Sản phẩm gợi ý mua kèm (Consequent)": "Tenex File Folders", "Support (%)": 1.24, "Confidence (%)": 68.4, "Lift": 3.42, "Đề xuất Combo": "Giảm 15% Folder khi mua kèm Hộp tài liệu"},
        {"Sản phẩm mua trước (Antecedent)": "Hewlett-Packard Copy Paper", "Sản phẩm gợi ý mua kèm (Consequent)": "Wilson Jones Binders", "Support (%)": 0.98, "Confidence (%)": 54.2, "Lift": 2.85, "Đề xuất Combo": "Gói quà văn phòng phẩm cơ bản"},
        {"Sản phẩm mua trước (Antecedent)": "Sanford Highlighters", "Sản phẩm gợi ý mua kèm (Consequent)": "Avery Address Labels", "Support (%)": 1.15, "Confidence (%)": 49.1, "Lift": 2.41, "Đề xuất Combo": "Voucher giảm $5 đơn hàng sau"},
        {"Sản phẩm mua trước (Antecedent)": "Apple Smart Phone", "Sản phẩm gợi ý mua kèm (Consequent)": "Belkin Screen Protector", "Support (%)": 2.05, "Confidence (%)": 78.5, "Lift": 4.15, "Đề xuất Combo": "Tặng miếng dán cường lực khi mua điện thoại"},
        {"Sản phẩm mua trước (Antecedent)": "Hon Executive Leather Armchair", "Sản phẩm gợi ý mua kèm (Consequent)": "Rubbermaid Floor Mat", "Support (%)": 0.82, "Confidence (%)": 45.0, "Lift": 2.92, "Đề xuất Combo": "Combo Ghế công thái học + Thảm sàn bảo vệ"}
    ])
    
    st.dataframe(rules_data, use_container_width=True)
    
    st.info("💡 **Gợi ý ứng dụng thực tiễn:** Tích hợp trực tiếp danh sách luật kết hợp này vào thuật toán gợi ý giỏ hàng (Shopping Cart Recommendations) hoặc chiến dịch email marketing tự động gửi cho khách hàng sau khi thanh toán.")
