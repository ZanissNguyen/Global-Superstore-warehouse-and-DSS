# SSOT 07: BẢNG CÔNG VIỆC, KẾ HOẠCH TRIỂN KHAI & TIÊU CHÍ NGHIỆM THU (TASKS BACKLOG & ACCEPTANCE CRITERIA)

> **Mã tài liệu:** SSOT-07  
> **Phiên bản:** 1.0  
> **Trạng thái:** Chính thức (Approved)  
> **Người biên soạn:** Tiến Nhất (Project Lead)

---

## 1. NGUYÊN TẮC QUẢN LÝ DỰ ÁN VÀ ĐỊNH NGHĨA HOÀN THÀNH (DEFINITION OF DONE - DOD)

Một hạng mục công việc (Task / Feature) chỉ được xem là **Hoàn thành (Done)** khi thỏa mãn tất cả các điều kiện sau:
1. **Mã nguồn hoàn chỉnh:** Viết đúng cấu trúc dự án, tuân thủ PEP8 (Python) hoặc chuẩn định dạng SQL, không chứa hardcoded credentials (dùng `.env`).
2. **Khả lặp & Không lỗi:** Script chạy thành công từ dòng lệnh (`CLI`) hoặc docker container mà không ném ngoại lệ không xử lý.
3. **Kiểm thử & Khớp dữ liệu:** Đạt 100% các tiêu chí nghiệm thu (Acceptance Criteria - AC); số liệu giữa các tầng (Bronze -> Silver -> Gold) không bị thất thoát ngoài quy tắc cho phép.
4. **Tài liệu hóa:** Cập nhật tài liệu kỹ thuật liên quan trong `docs/ssot/` và `temp-docs/GUIDE/`.

---

## 2. BẢNG PHÂN RÃ CÔNG VIỆC VÀ TIÊU CHÍ NGHIỆM THU CHI TIẾT (TASK BACKLOG)

### 2.1. Phân hệ Kho Dữ Liệu & Thiết kế CSDL (Data Warehouse & DDL)

#### **[TASK-DW-01] Thiết kế Mô hình Star Schema và Từ điển dữ liệu**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 30/10/2026 | **Trạng thái:** **DONE**
- **Mô tả:** Xác định Grain, Fact table `gold.fact_sales`, và 5 Dimension tables (`dim_date`, `dim_customer`, `dim_product`, `dim_geography`, `dim_ship_mode`).
- **Tiêu chí nghiệm thu (AC):**
  - **AC 1.1:** Bảng FactSales ở grain một dòng sản phẩm của đơn hàng, chứa các measures: `sales`, `quantity`, `discount`, `profit`, `shipping_cost`.
  - **AC 1.2:** Tất cả các bảng Dimension sử dụng Surrogate Key kiểu số nguyên làm Primary Key.
  - **AC 1.3:** DimDate đóng 2 vai trò riêng biệt (Role-playing) cho `order_date_key` và `ship_date_key`.

#### **[TASK-DW-02] Viết toàn bộ mã nguồn DDL khởi tạo Schemas và Tables**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 02/11/2026 | **Trạng thái:** **IN PROGRESS (Hoàn thiện toàn bộ file SQL)**
- **Mô tả:** Viết script SQL cho `bronze`, `silver`, `gold`, `dss` đảm bảo chạy tự động không lỗi.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 2.1:** Script `create_schema.sql` tạo đầy đủ 4 schema: `bronze`, `silver`, `gold`, `dss`.
  - **AC 2.2:** Script tạo bảng có đầy đủ Primary Key, Foreign Key ràng buộc, kiểu dữ liệu chuẩn (`NUMERIC(12,4)`, `INTEGER`, `DATE`, `VARCHAR`).
  - **AC 2.3:** Chạy lệnh DDL trên PostgreSQL trắng tạo thành công 100% cấu trúc không lỗi.

---

### 2.2. Phân hệ Pipeline ETL Medallion (ETL Bronze - Silver - Gold)

#### **[TASK-ETL-01] Hoàn thiện Ingestion & Lưu vết tầng Bronze**
- **Người thực hiện:** Thành Phát
- **Thời hạn:** 05/11/2026 | **Trạng thái:** **IN PROGRESS (90%)**
- **Mô tả:** Đọc file XLS/CSV, tính mã băm SHA-256, nạp bảng thô và bảng lưu vết `bronze.ingestion`.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 1.1:** Khi nạp một file mới, hệ thống tự động ghi nhận `source_name`, `content_hash`, `loaded_time`, `metadata` vào `bronze.ingestion`.
  - **AC 1.2:** Nếu chạy lại cùng một file đã nạp, hệ thống phát hiện trùng mã hash và dừng nạp (Idempotency).
  - **AC 1.3:** Tách riêng danh mục `bronze.market` và `bronze.postal_code` không bị trùng lặp.

#### **[TASK-ETL-02] Hiện thực Transformation & Data Validation tầng Silver**
- **Người thực hiện:** Thành Phát + Tiến Nhất
- **Thời hạn:** 07/11/2026 | **Trạng thái:** **READY TO RUN**
- **Mô tả:** Chuyển đổi dữ liệu từ `bronze.raw_orders` vào `silver.orders`: ép kiểu chuẩn, chuẩn hóa ngày tháng đa định dạng (`d/m/Y`, `d-m-Y` -> `DATE`), xử lý NULL Postal Code thành `'Unknown'`, JOIN với Returns (`is_returned`) và People (`regional_manager`).
- **Tiêu chí nghiệm thu (AC):**
  - **AC 2.1:** 100% số dòng của 51,290 bản ghi được parse ngày tháng chuẩn xác, không sinh NULL ở `order_date` và `ship_date`.
  - **AC 2.2:** Đảm bảo ràng buộc nghiệp vụ: `ship_date >= order_date`, `sales >= 0`, `quantity > 0`, `0 <= discount <= 1`.
  - **AC 2.3:** Script kiểm tra `check_nulls.sql`, `check_duplicates.sql`, `check_data_quality.sql` trả về 0 bản ghi vi phạm.

#### **[TASK-ETL-03] Hiện thực Dimensional Loading tầng Gold**
- **Người thực hiện:** Tiến Nhất + Thành Phát
- **Thời hạn:** 09/11/2026 | **Trạng thái:** **READY TO RUN**
- **Mô tả:** Tự động sinh `dim_date` (2011–2018), nạp các Dimension từ Silver, lookup surrogate key và nạp vào `fact_sales`.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 3.1:** Tổng số dòng của `gold.fact_sales` bằng đúng tổng số dòng hợp lệ của `silver.orders`.
  - **AC 3.2:** Không có bất kỳ khóa ngoại nào bị mồ côi (No orphan FKs: `WHERE order_date_key IS NULL OR customer_key IS NULL`).
  - **AC 3.3:** Tổng doanh thu $\sum \text{Sales}$ và lợi nhuận $\sum \text{Profit}$ giữa Silver và Gold khớp nhau chính xác 100% đến 4 chữ số thập phân.

#### **[TASK-ETL-04] Kiểm thử Nạp Dữ Liệu Tăng Trưởng (Incremental Loading)**
- **Người thực hiện:** Thành Phát
- **Thời hạn:** 10/11/2026 | **Trạng thái:** **QUEUED**
- **Mô tả:** Chạy nạp tập dữ liệu bổ sung 10,000 dòng (`Sample - Superstore.csv`) và xác nhận dữ liệu được nạp thêm mà không trùng lặp bản ghi cũ.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 4.1:** Số dòng trong `gold.fact_sales` tăng thêm tương ứng với số đơn hàng mới.
  - **AC 4.2:** Các Surrogate keys đã có của khách hàng/sản phẩm cũ được tái sử dụng; khách hàng/sản phẩm mới được cấp Surrogate keys mới liên tục.

---

### 2.3. Phân hệ Phân Tích OLAP & Data Marts

#### **[TASK-OLAP-01] Hiện thực Bộ câu truy vấn OLAP chuẩn mực**
- **Người thực hiện:** Đức Phát + Thành Phát
- **Thời hạn:** 10/11/2026 | **Trạng thái:** **READY TO RUN**
- **Mô tả:** Viết và kiểm thử các truy vấn SQL cho Roll-up, Drill-down, Slice, Dice, Pivot, Window Functions và GROUP BY CUBE/ROLLUP.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 1.1:** Có đầy đủ script SQL tương ứng với từng thao tác trong `src/sql/gold/marts/` và tài liệu giải thích ngữ cảnh kinh doanh.
  - **AC 1.2:** Truy vấn thực thi mượt mà dưới 500ms trên cơ sở dữ liệu có Index.

#### **[TASK-OLAP-02] Xây dựng và Tối ưu hóa Materialized Views (Data Marts)**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 10/11/2026 | **Trạng thái:** **READY TO RUN**
- **Mô tả:** Tạo 3 Materialized Views (`mv_sales_mart`, `mv_product_mart`, `mv_customer_mart`) phục vụ BI và DSS.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 2.1:** Materialized Views được tạo thành công kèm các Index trên cột thời gian và địa lý.
  - **AC 2.2:** Có script tự động `REFRESH MATERIALIZED VIEW` tích hợp vào luồng cuối của ETL pipeline.

---

### 2.4. Phân hệ Hệ Hỗ Trợ Quyết Định (DSS Engine & Algorithms)

#### **[TASK-DSS-01] Hiện thực Mô hình Mô phỏng What-If (Discount & Profit Simulation)**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 11/11/2026 | **Trạng thái:** **READY TO CODE**
- **Mô tả:** Module Python nhận các tham số điều chỉnh chiết khấu và độ co giãn cầu, tính toán doanh thu/lợi nhuận mới và xuất ra cảnh báo quyết định.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 1.1:** Hàm Python tính toán chính xác công thức co giãn cầu $e$, trả về kết quả Baseline vs Simulated.
  - **AC 1.2:** Trả về thông điệp khuyến nghị tự động (Approve / Caution / Reject) dựa trên ngưỡng biên lợi nhuận 5% và 12%.

#### **[TASK-DSS-02] Hiện thực Mô hình Dự báo Doanh số (Sales & Demand Forecasting)**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 12/11/2026 | **Trạng thái:** **READY TO CODE**
- **Mô tả:** Module Python trích xuất chuỗi thời gian từ Gold, huấn luyện mô hình Exponential Smoothing / Moving Average, đánh giá MAE/RMSE/MAPE, dự báo 3-6 tháng tới và lưu kết quả vào `dss.forecast_result`.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 2.1:** Tách tập Train/Test theo trình tự thời gian (không shuffle).
  - **AC 2.2:** Ghi đầy đủ metadata lần chạy vào `dss.forecast_run` và các điểm dự báo vào `dss.forecast_result`.

#### **[TASK-DSS-03] Hiện thực Khai phá Luật kết hợp Giỏ hàng (Market Basket Analysis)**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 12/11/2026 | **Trạng thái:** **READY TO CODE**
- **Mô tả:** Module Python trích xuất giao dịch theo `order_id` và `product_id`, chạy thuật toán Apriori/FP-Growth, lọc luật theo Support, Confidence, Lift và lưu vào `dss.association_rule`.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 3.1:** Chuyển đổi dữ liệu dạng transaction matrix sạch không trùng lặp.
  - **AC 3.2:** Khai phá ra các luật có $\text{Lift} > 1.2$, kèm tên sản phẩm rõ nghĩa.

---

### 2.5. Phân hệ Giao Diện Người Dùng & Backend (UI / Power BI / App)

#### **[TASK-UI-01] Xây dựng Báo cáo Power BI (.pbix)**
- **Người thực hiện:** Đức Phát
- **Thời hạn:** 13/11/2026 | **Trạng thái:** **IN PROGRESS (Wireframing)**
- **Mô tả:** Thiết kế 3 trang Dashboard: Executive Sales, Product & Geography Performance, Customer RFM.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 1.1:** File `.pbix` kết nối trực tiếp vào schema `gold` của PostgreSQL.
  - **AC 1.2:** Có đầy đủ Slicers (Năm, Quý, Vùng, Phân khúc), biểu đồ Card KPIs, biểu đồ Line/Bar và tính năng Drill-through.

#### **[TASK-UI-02] Xây dựng Backend REST API (FastAPI)**
- **Người thực hiện:** Tiến Nhất
- **Thời hạn:** 13/11/2026 | **Trạng thái:** **READY TO CODE**
- **Mô tả:** Cung cấp các endpoint `/api/kpi/summary`, `/api/dss/what-if`, `/api/dss/forecast`, `/api/dss/association-rules`.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 2.1:** API khởi chạy mượt mà trên cổng 8000 (hoặc cổng cấu hình).
  - **AC 2.2:** Swagger UI (`/docs`) hiển thị đầy đủ schema input/output chuẩn OpenAPI.

#### **[TASK-UI-03] Xây dựng Giao diện Tương tác DSS (Streamlit App)**
- **Người thực hiện:** Tiến Nhất + Đức Phát
- **Thời hạn:** 13/11/2026 | **Trạng thái:** **READY TO CODE**
- **Mô tả:** Giao diện web trực quan cho phép người quản lý kéo thanh trượt thử nghiệm kịch bản What-if, xem biểu đồ dự báo và tra cứu combo sản phẩm bán kèm.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 3.1:** Ứng dụng chạy bằng 1 lệnh `streamlit run src/app/main.py`.
  - **AC 3.2:** Tương tác thanh trượt What-if phản hồi tức thời dưới 1 giây.

---

### 2.6. Phân hệ Báo Cáo, Slide & Đóng Gói Sản Phẩm (Reports & Final Submission)

#### **[TASK-REP-01] Soạn thảo Báo cáo BTL Toàn diện (PDF)**
- **Người thực hiện:** Đức Phát + Tiến Nhất
- **Thời hạn:** 14/11/2026 | **Trạng thái:** **IN PROGRESS**
- **Mô tả:** Soạn thảo báo cáo PDF theo chuẩn học thuật ĐH Bách Khoa: Đặt vấn đề, Thiết kế DW, ETL Pipeline, Phép toán OLAP, Mô hình DSS, Đánh giá và Hướng phát triển.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 1.1:** Trang bìa có đầy đủ thông tin: Trường, Khoa, Môn học, GVHD, Danh sách thành viên, Tỷ lệ đóng góp, Link Video demo và Link Github.
  - **AC 1.2:** Nội dung chi tiết từ 30–50 trang, hình vẽ rõ nét, bảng biểu rõ ràng.

#### **[TASK-REP-02] Thiết kế Slide & Kịch bản Thuyết trình**
- **Người thực hiện:** Thành Phát
- **Thời hạn:** 14/11/2026 | **Trạng thái:** **QUEUED**
- **Mô tả:** Soạn slide 20–25 trang tóm tắt điểm nổi bật nhất của đồ án.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 2.1:** File PDF slide thuyết trình hoàn thiện, phân chia phần trình bày cho cả 3 thành viên.

#### **[TASK-REP-03] Quay Video Demo Thuyết trình & Đóng gói File ZIP**
- **Người thực hiện:** Cả nhóm
- **Thời hạn:** 15/11/2026 (17:00) | **Trạng thái:** **QUEUED**
- **Mô tả:** Quay video thời lượng 10–15 phút, cả 3 thành viên đều xuất hiện và thuyết trình; đóng gói toàn bộ mã nguồn, dữ liệu mẫu, báo cáo và nộp lên hệ thống LMS trước 23:59 ngày 15/11/2026.
- **Tiêu chí nghiệm thu (AC):**
  - **AC 3.1:** Link video upload Youtube Unlisted / Google Drive mở quyền xem cho giảng viên.
  - **AC 3.2:** File ZIP nộp đúng cấu trúc quy định của BTL.
