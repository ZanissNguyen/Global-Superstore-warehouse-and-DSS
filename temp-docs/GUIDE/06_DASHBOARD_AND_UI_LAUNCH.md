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
   - Quan sát 5 thẻ KPI tài chính cấp cao (Doanh thu $12.64M, Lợi nhuận $1.47M, Biên LN 11.61%, Chiết khấu BQ 14.29%, Tỷ lệ hoàn trả 2.29%).
   - **Biểu đồ Doanh thu và Lợi nhuận theo 48 Tháng (Dual-Axis):** Quan sát sự kết hợp nhịp nhàng giữa Doanh thu (cột xanh) và Lợi nhuận (đường xanh lá), hover để xem số lượng đơn hàng thực tế (180 đến hơn 1,000 đơn/tháng).
   - Trung tâm cảnh báo rủi ro nghiệp vụ: Nhận diện các điểm nóng "thấm lỗ" tại thị trường EMEA/Africa và ngành hàng Tables.
   - Cơ cấu Doanh thu & Lợi nhuận theo Ngành hàng (Technology, Furniture, Office Supplies).
2. **Trang 2: What-If Discount & Profit Simulation Sandbox:**
   - Chọn Thị trường mục tiêu (ví dụ: `APAC`) và Ngành hàng (ví dụ: `Furniture`). Hệ thống tự động nạp Doanh thu, Lợi nhuận, Chiết khấu gốc từ CSDL.
   - Tinh chỉnh mức chiết khấu mong muốn (+/- %) và hệ số co giãn cầu $e$.
   - Quan sát kết quả mô phỏng tức thời: Doanh thu, Lợi nhuận, Biên lợi nhuận dự kiến và Biểu đồ đối chiếu trực quan.
   - Đọc kết luận khuyến nghị tự động (ACCEPT / CAUTION / REJECT) có giải thích nguyên nhân kinh tế lượng.
3. **Trang 3: Sales Forecasting Explorer:**
   - Xem đồ thị chuỗi thời gian doanh thu 48 tháng lịch sử kết hợp 6 tháng dự báo tương lai (Holt-Winters) kèm dải tin cậy 95%.
   - Thẻ đánh giá sai số mô hình thực nghiệm: MAE, RMSE, MAPE (< 15%).
4. **Trang 4: Market Basket & Cross-Selling Navigator:**
   - Thẻ tóm tắt số lượng luật khai phá, Max Lift, Max Confidence.
   - Thanh trượt động lọc luật theo hệ số Lift mong muốn.
   - Bảng phân tích chi tiết: Sản phẩm chọn mua $\rightarrow$ Gợi ý bán kèm, kèm đề xuất hành động combo / voucher.
   - Khung mở rộng hướng dẫn lệnh CLI khai phá mới cho Sub-Category và SKU level.

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

### 3.3. Tương tác trên Báo cáo Power BI & Lưu ý Trực quan hóa:
- **Trang 1: Executive Sales Performance:** Sử dụng thanh trượt Năm/Quý để lọc dữ liệu; xem biểu đồ Clustered Column & Line thể hiện Doanh số và Lợi nhuận theo tháng.
  - *Lưu ý quan trọng:* Tuyệt đối không kéo cột thô `sales` / `profit` vào biểu đồ để tránh bị lỗi `Count = 1`. Luôn sử dụng DAX Measure `[Total Sales] = SUM(fact_sales[sales])` và `[Total Profit] = SUM(fact_sales[profit])` từ file `reports/powerbi/03_DAX_MEASURES.dax`.
- **Trang 2: Product Performance & Pareto ABC:** Xem biểu đồ Scatter Plot giữa Sales và Profit định vị 17 ngành hàng; biểu đồ Pareto 80/20 chứng minh quy luật 20% mặt hàng mang lại 80% lợi nhuận; bảng cảnh báo Top 10 sản phẩm gây lỗ nhiều nhất.
- **Trang 3: Customer Segment & Cross-Selling:** Biểu đồ Donut tỷ trọng phân khúc (Consumer, Corporate, Home Office) và Bảng gợi ý bán chéo trích xuất trực tiếp từ bảng `dss.association_rule`.
