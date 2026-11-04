# HƯỚNG DẪN 06: KHỞI CHẠY GIAO DIỆN DSS & BÁO CÁO POWER BI (UI & BI LAUNCH GUIDE)

---

## 1. KHỞI CHẠY ỨNG DỤNG WEB TƯƠNG TÁC DSS (STREAMLIT APP)

Ứng dụng web DSS cho phép người dùng trực tiếp trải nghiệm các tính năng hỗ trợ quyết định mà không cần cài đặt Power BI Desktop.

### 1.1. Lệnh khởi chạy:
Từ thư mục gốc dự án, thực hiện lệnh (sử dụng tiền tố `python -m` để đảm bảo chạy được trên mọi môi trường Windows PowerShell kể cả khi chưa thêm thư mục Scripts vào PATH):
```powershell
python -m streamlit run src/app/main.py
```
*(Hoặc lệnh rút gọn nếu `streamlit` đã có trong PATH: `streamlit run src/app/main.py`)*

### 1.2. Truy cập ứng dụng:
Mở trình duyệt web bất kỳ tại địa chỉ:
```text
http://localhost:8501
```

### 1.3. Hướng dẫn trải nghiệm các tính năng trên giao diện:
1. **Trang 1: Executive Overview & KPI Dashboard:**
   - Quan sát các thẻ KPI tổng quát: Tổng doanh thu, Lợi nhuận ròng, Biên lợi nhuận, Tỷ lệ chiết khấu, Tỷ lệ hoàn trả.
   - Quan sát danh sách cảnh báo "Vùng có doanh số cao nhưng lợi nhuận âm".
2. **Trang 2: What-If Discount & Profit Simulation Sandbox:**
   - Chọn Thị trường (ví dụ: `APAC`) và Danh mục (ví dụ: `Furniture`).
   - Kéo thanh trượt điều chỉnh mức chiết khấu tăng thêm từ `0%` đến `+15%`.
   - Quan sát biểu đồ cột biến thiên tức thời giữa **Hiện trạng (Baseline)** và **Mô phỏng (Simulated)**.
   - Đọc kết luận khuyến nghị do hệ thống tự động đưa ra ở khung dưới.
3. **Trang 3: Sales Forecasting Explorer:**
   - Xem đồ thị chuỗi thời gian doanh thu qua các năm và đường dự báo 6 tháng tới kèm vùng dải tin cậy 95%.
4. **Trang 4: Market Basket & Cross-Selling Navigator:**
   - Chọn một mã sản phẩm để xem danh sách các sản phẩm nên gợi ý bán kèm với hệ số Lift cao nhất.

---

## 2. KHỞI CHẠY DỊCH VỤ BACKEND REST API (FASTAPI)

Nếu muốn sử dụng hoặc kiểm thử hệ thống qua các endpoint API JSON:
```powershell
python -m uvicorn src.app.api.main:app --reload --port 8000
```
- Truy cập tài liệu tương tác Swagger UI tại:
  ```text
  http://localhost:8000/docs
  ```
- Thử nghiệm gửi request tới endpoint:
  - `GET /api/kpi/summary`
  - `POST /api/dss/what-if`
  - `GET /api/dss/forecast`
  - `GET /api/dss/association-rules`

---

## 3. HƯỚNG DẪN MỞ BÁO CÁO TRÊN POWER BI DESKTOP

### 3.1. Mở file báo cáo mẫu:
Mở file `reports/Global_Superstore_BI.pbix` bằng phần mềm **Power BI Desktop**.

### 3.2. Cấu hình kết nối tới PostgreSQL:
Nếu Power BI yêu cầu xác thực kết nối CSDL:
1. Vào **Home** -> **Transform Data** -> **Data Source Settings**.
2. Chọn nguồn **PostgreSQL Database** và bấm **Edit**:
   - **Server:** `localhost:5432` *(hoặc `localhost:5433` nếu đã đổi cổng)*
   - **Database:** `global_superstore`
   - **Data Connectivity mode:** Chọn `Import` (khuyến nghị cho biểu đồ mượt mà) hoặc `DirectQuery`.
3. Nhập thông tin đăng nhập:
   - **User name:** `admin`
   - **Password:** Mật khẩu trong file `.env`
4. Bấm **Apply Changes** để Power BI nạp dữ liệu từ các bảng `gold.fact_sales`, `gold.dim_*` và `dss.*`.

### 3.3. Tương tác trên Báo cáo Power BI:
- **Trang 1: Sales Performance:** Sử dụng thanh trượt Năm/Quý để lọc dữ liệu; nhấp đúp vào một quốc gia trên bản đồ thế giới để xem doanh thu chi tiết.
- **Trang 2: Product Performance:** Xem biểu đồ Scatter Plot giữa Sales và Profit; lọc theo Category để xem phân tích Pareto 80/20.
- **Trang 3: Customer Segment & RFM:** Lọc khách hàng theo phân khúc và điểm Recency.
