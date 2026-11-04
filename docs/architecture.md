# KIẾN TRÚC TỔNG THỂ HỆ THỐNG KHO DỮ LIỆU & HỆ HỖ TRỢ QUYẾT ĐỊNH
## GLOBAL SUPERSTORE DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)

> **Môn học:** Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031) - HK261, ĐH Bách Khoa ĐHQG-HCM  
> **Tài liệu đặc tả SSOT chính:** [docs/ssot/index.md](file:///e:/bku/261/DW/codebase/Global-Superstore-warehouse-and-DSS/docs/ssot/index.md)

---

## 1. SƠ ĐỒ KIẾN TRÚC TỔNG THỂ (SYSTEM ARCHITECTURE DIAGRAM)

```mermaid
flowchart TD
    subgraph Layer0["0. NGUỒN DỮ LIỆU (RAW SOURCES)"]
        S1["Global Superstore.xls (51,290 bản ghi)\n- Orders Sheet\n- Returns Sheet\n- People Sheet"]
        S2["Sample - Superstore.csv (~10,000 bản ghi)\n- Incremental Testing"]
    end

    subgraph Layer1["1. BRONZE LAYER (RAW INGESTION)"]
        B1["bronze.ingestion\nAudit logging, SHA-256 hash, timestamps"]
        B2["bronze.raw_orders\nRaw schema, all columns as TEXT"]
        B3["bronze.postal_code & bronze.market"]
    end

    subgraph Layer2["2. SILVER LAYER (STANDARDIZED & CLEANED)"]
        SV1["silver.orders\n- Cleaned types (Integer, Numeric, Date)\n- Mixed Date Parser (d/m/Y, d-m-Y -> YYYY-MM-DD)\n- Postal Code 'Unknown' imputation\n- Joined Returns (is_returned) & People (manager)"]
        SV2["Silver Validation Suite\n- check_nulls.sql\n- check_duplicates.sql\n- check_data_quality.sql"]
    end

    subgraph Layer3["3. GOLD LAYER (DIMENSIONAL STAR SCHEMA)"]
        G_FACT["gold.fact_sales\nGrain: 1 Order Line Item"]
        G_DATE["gold.dim_date\nRole-playing: Order Date & Ship Date"]
        G_CUST["gold.dim_customer (SCD1)"]
        G_PROD["gold.dim_product (SCD1)"]
        G_GEO["gold.dim_geography"]
        G_SHIP["gold.dim_ship_mode"]
        G_MARTS["Materialized Views (Data Marts):\n- gold.mv_sales_mart\n- gold.mv_product_mart\n- gold.mv_customer_mart"]
    end

    subgraph Layer4["4. DSS ENGINE & STORAGE"]
        D_MODELS["src/dss/ Engine\n- What-If Discount Simulation\n- Sales Forecasting (Holt-Winters)\n- Market Basket (Apriori/FP-Growth)"]
        D_STORAGE["PostgreSQL Schema: dss\n- dss.forecast_run & dss.forecast_result\n- dss.association_run & dss.association_rule"]
    end

    subgraph Layer5["5. GIAO DIỆN & TRỰC QUAN HÓA (PRESENTATION)"]
        PBI["Power BI Dashboard (.pbix)\n- Sales Performance Report\n- Product Portfolio Matrix\n- Customer RFM Insights"]
        FAST_API["FastAPI Backend (src/app/api/)\n- REST Endpoints for OLAP & DSS"]
        STREAMLIT["Streamlit Web App (src/app/main.py)\n- Interactive What-If Sandbox\n- Real-time Slider Simulation\n- Prescriptive Recommendations"]
    end

    Layer0 -->|Extract & Hash| Layer1
    Layer1 -->|Transform & Clean| Layer2
    Layer2 -->|Dimensional ETL| Layer3
    Layer3 -->|Analytical Datafeed| Layer4
    Layer4 -->|Store Predictions & Rules| Layer4
    Layer3 -->|Direct Connection| PBI
    Layer4 -->|Direct Connection| PBI
    Layer3 -->|SQL Queries| FAST_API
    Layer4 -->|SQL Queries| FAST_API
    FAST_API -->|REST API / JSON| STREAMLIT
    Layer4 -->|Direct Python Engine| STREAMLIT
```

---

## 2. NGUYÊN TẮC THIẾT KẾ CỐT LÕI (CORE DESIGN PRINCIPLES)

1. **Tuân thủ Chuẩn mực Ralph Kimball:**
   - Fact table được xây dựng tại mức hạt chi tiết nhất (**Atomic Grain** = 1 dòng sản phẩm trong đơn hàng).
   - Tất cả các bảng Dimension sử dụng Khóa thay thế số nguyên (**Surrogate Keys** `SERIAL` / `INTEGER`) thay vì dựa vào Natural Keys để tăng tốc độ truy vấn và hỗ trợ nạp dữ liệu từ nhiều nguồn.
   - `DimDate` là một **Role-Playing Dimension** được nối 2 lần với `FactSales` qua `order_date_key` và `ship_date_key`.

2. **Khung lý thuyết DSS của Efraim Turban & Herbert Simon:**
   - Hệ thống không dừng lại ở việc báo cáo quá khứ (Descriptive Analytics qua Power BI), mà cung cấp bộ công cụ tương tác giải quyết bài toán bán cấu trúc:
     - **What-If Simulation:** Mô phỏng sự biến thiên của lợi nhuận ròng khi thay đổi chiết khấu dựa trên độ co giãn cầu $e$.
     - **Predictive Analytics:** Dự báo chuỗi thời gian doanh số tương lai kèm khoảng tin cậy 95%.
     - **Prescriptive Recommendations:** Đưa ra khuyến nghị tự động (Approve / Caution / Reject) giúp nhà quản trị ra quyết định tối ưu.

3. **Mô hình Song hành (Hybrid UI Architecture):**
   - **Power BI (.pbix):** Chuyên phục vụ báo cáo BI đa chiều, cắt lát dữ liệu, drill-down nhanh.
   - **Python DSS Web App (Streamlit + FastAPI):** Chuyên phục vụ tính năng tương tác What-If trực tiếp, dự báo và đề xuất bán chéo theo thời gian thực.
