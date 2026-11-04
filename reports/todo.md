# BÁO CÁO BÀI TẬP LỚN CO4031 - TOÀN VĂN (REPORT OUTLINE & PROGRESS)

> **Môn học:** Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031) - HK261  
> **Giảng viên hướng dẫn:** ThS./TS. Đỗ Thanh Thái  
> **Người thực hiện:** Đức Phát (Lead Writer), Tiến Nhất, Thành Phát  
> **Hạn nộp:** 23:59 Chủ Nhật, 15/11/2026

---

## BỐ CỤC CHUẨN CỦA BÁO CÁO (THEO ĐỀ CƯƠNG BÁCH KHOA)

### TRANG BÌA (Cover Page)
- [x] Logo ĐH Bách Khoa ĐHQG-HCM, Khoa KH&KT Máy Tính.
- [x] Tên đề tài: *Xây dựng Kho dữ liệu và Hệ hỗ trợ Quyết định cho Doanh nghiệp Bán lẻ Toàn cầu (Global Superstore)*.
- [x] Danh sách thành viên nhóm, MSSV, tỷ lệ phần trăm đóng góp.
- [ ] Link Video demo YouTube (Unlisted) / Google Drive (cập nhật trước 15/11).
- [x] Link Github Repository.

---

### CHƯƠNG 1: TỔNG QUAN VÀ PHÂN TÍCH NGHIỆP VỤ (BUSINESS ANALYSIS)
- [x] **1.1 Giới thiệu bài toán & bộ dữ liệu:** Global Superstore (51,290 bản ghi, 147 quốc gia, 3 ngành hàng lớn).
- [x] **1.2 Các thách thức quản trị kinh doanh:** Thâm hụt biên lợi nhuận do chiết khấu, sản phẩm lỗ, biến động chuỗi cung ứng.
- [x] **1.3 Bộ chỉ số KPI cốt lõi:**
  - Sales Performance: Doanh thu, Lợi nhuận ròng, Profit Margin %, Avg Discount %, MoM Growth, Return Rate %.
  - Product Performance: Units Sold, Contribution %, Unit Profitability, Phân loại Pareto ABC.
  - Customer Analytics: AOV, Purchase Frequency, Phân khúc RFM.
- [x] **1.4 Ma trận câu hỏi nghiệp vụ:** Chi tiết các nhóm câu hỏi S01–S07, P01–P08, C01–C07.

---

### CHƯƠNG 2: THIẾT KẾ KHO DỮ LIỆU (DATA WAREHOUSE DESIGN)
- [x] **2.1 Kiến trúc tổng thể:** Mô hình Medallion (Bronze -> Silver -> Gold).
- [x] **2.2 Xác định Grain:** Một dòng sản phẩm trong đơn hàng (`Row ID`).
- [x] **2.3 Thiết kế Mô hình hình sao (Star Schema):**
  - Fact trung tâm: `FactSales` (Additive measures, non-additive rates, degenerate dimensions).
  - 5 Dimension tables: `DimDate` (Role-playing), `DimCustomer`, `DimProduct`, `DimGeography`, `DimShipMode`.
- [x] **2.4 Chiến lược khóa và SCD:** Sử dụng Surrogate Keys kiểu số nguyên, chiến lược SCD Type 1.
- [x] **2.5 Giải pháp kỹ thuật đặc thù:** Xử lý 80.5% NULL Postal Code, xử lý ngày tháng đa định dạng (`d/m/Y` và `d-m-Y`).

---

### CHƯƠNG 3: HIỆN THỰC QUY TRÌNH ETL (ETL IMPLEMENTATION)
- [x] **3.1 Tầng Bronze:** Ingestion audit logging, mã băm SHA-256 chống trùng lặp, lưu nguyên trạng dữ liệu thô.
- [x] **3.2 Tầng Silver:** Làm sạch dữ liệu, ép kiểu chuẩn PostgreSQL, xử lý NULL, nối cờ hoàn trả (`is_returned`) và Trưởng vùng (`regional_manager`).
- [x] **3.3 Bộ kiểm tra chất lượng dữ liệu (Data Quality Checks):** Check nulls, check duplicates, check constraints.
- [x] **3.4 Tầng Gold:** Sinh lịch tự động, nạp Dimension và Fact bằng SQL surrogate lookup.
- [x] **3.5 Kiểm thử nạp gia tăng (Incremental Loading):** Quy trình nạp bổ sung file dữ liệu mới 10,000 dòng.

---

### CHƯƠNG 4: KHAI THÁC TRUY VẤN OLAP VÀ DATA MARTS
- [x] **4.1 Thiết kế Materialized Views (Data Marts):** `mv_sales_mart`, `mv_product_mart`, `mv_customer_mart`.
- [x] **4.2 Hiện thực các thao tác OLAP:**
  - Roll-Up (Thời gian và Địa lý).
  - Drill-Down (Ngành hàng -> Phân nhóm -> Từng mã SKU).
  - Slice & Dice (Cắt lát thị trường APAC, khối hộp đa chiều).
  - Pivot (Xoay 4 quý thành 4 cột ngang so sánh doanh thu).
  - Window Functions (MoM Sales Growth, DENSE_RANK Top 5).
  - Siêu lập phương GROUP BY CUBE.

---

### CHƯƠNG 5: HỆ HỖ TRỢ QUYẾT ĐỊNH (DECISION SUPPORT SYSTEM)
- [x] **5.1 Cơ sở lý thuyết:** Khung lý thuyết DSS của Efraim Turban và chu trình 4 bước của Herbert Simon (Intelligence -> Design -> Choice -> Implementation).
- [x] **5.2 Mô hình mô phỏng What-If (Discount & Profit Simulation):** Công thức toán học co giãn cầu theo giá $e$, kịch bản điều chỉnh chiết khấu, bộ quy tắc khuyến nghị tự động (Approve / Caution / Reject).
- [x] **5.3 Mô hình Dự báo Chuỗi thời gian (Sales Forecasting):** Exponential Smoothing (Holt-Winters), đánh giá sai số MAE, RMSE, MAPE, dự báo 6 tháng tới kèm dải tin cậy 95%.
- [x] **5.4 Khai phá Luật kết hợp Giỏ hàng (Market Basket Analysis):** Thuật toán Apriori/FP-Growth, các chỉ số Support, Confidence, Lift (> 1.2), ứng dụng đề xuất gói combo bán chéo.
- [x] **5.5 Lưu trữ DSS:** Schema `dss` trong PostgreSQL (`forecast_run`, `forecast_result`, `association_run`, `association_rule`).

---

### CHƯƠNG 6: GIAO DIỆN NGƯỜI DÙNG & TÍCH HỢP HỆ THỐNG
- [x] **6.1 Báo cáo Power BI (.pbix):** 3 trang Dashboard nghiệp vụ (Sales Executive, Product & Geography, Customer RFM).
- [x] **6.2 Ứng dụng Web Tương tác DSS (Streamlit):** Sandbox thử nghiệm What-if thời gian thực, trực quan hóa dự báo và gợi ý giỏ hàng.
- [x] **6.3 Dịch vụ Backend REST API (FastAPI):** Các endpoint RESTful chuẩn phục vụ web app và ứng dụng ngoài.

---

### CHƯƠNG 7: ĐÁNH GIÁ KẾT QUẢ, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN
- [ ] **7.1 Đánh giá mức độ hoàn thành:** Đối chiếu với các chuẩn đầu ra (L.O.1.1 -> L.O.4.2) của môn học.
- [ ] **7.2 Hạn chế của hệ thống:** Giới hạn của dữ liệu lịch sử tĩnh, thiếu dữ liệu tồn kho và thời gian giao hàng thực tế theo giờ.
- [ ] **7.3 Hướng phát triển:** Tích hợp pipeline luồng (Streaming ETL với Kafka/Spark Streaming), mô hình ML sâu hơn (XGBoost, Prophet), cá nhân hóa gợi ý sản phẩm thời gian thực.

---

### TÀI LIỆU THAM KHẢO (REFERENCES)
- Sách Kimball, Turban, Han-Kamber, Elmasri theo chuẩn IEEE.
