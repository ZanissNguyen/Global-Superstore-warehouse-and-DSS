# SSOT 06: ĐẶC TẢ GIAO DIỆN DSS, BI DASHBOARD & BACKEND API (FRONTEND, BI & BACKEND SPECIFICATION)

> **Mã tài liệu:** SSOT-06  
> **Phiên bản:** 1.0  
> **Trạng thái:** Chính thức (Approved)  
> **Người biên soạn:** Tiến Nhất & Đức Phát

---

## 1. PHÂN TÍCH CHIẾN LƯỢC: POWER BI HAY PYTHON CHO DASHBOARD & DSS?

Một câu hỏi cốt lõi đặt ra trong quá trình thiết kế là: **Nên làm Dashboard bằng Power BI hay xây dựng ứng dụng web bằng Python?**

### 1.1. Bảng đối chiếu năng lực kỹ thuật:

| Tiêu chí so sánh | Power BI Desktop (.pbix) | Python Web App (FastAPI + Streamlit) |
|---|---|---|
| **Mục đích thiết kế chính** | Báo cáo Business Intelligence (BI), tổng hợp dữ liệu quá khứ, trực quan hóa đa chiều (Descriptive Analytics). | Hệ thống hỗ trợ ra quyết định (DSS), tương tác mô phỏng What-if động, dự báo và đề xuất hành động (Prescriptive Analytics). |
| **Khả năng tương tác lát cắt (Slice & Dice, Drill-down)** | **Xuất sắc:** Kéo thả linh hoạt, cross-filtering giữa các biểu đồ cực kỳ tự nhiên. | **Trung bình:** Cần viết code callback và cấu hình state để lọc đa chiều. |
| **Mô phỏng What-If đa biến động (Interactive Simulation)** | **Hạn chế:** Chỉ hỗ trợ thanh trượt What-if tham số DAX đơn giản; khó mô phỏng các hàm phi tuyến tính như co giãn cầu theo giá ($e$). | **Xuất sắc:** Hỗ trợ tương tác thanh trượt (slider), tính toán realtime bằng Python và hiển thị kịch bản so sánh tức thời. |
| **Tích hợp mô hình Học máy & Khai phá dữ liệu** | **Phức tạp:** Cần Python script visual hoặc Azure ML, khó chạy mượt mà trên máy người chấm không có cùng cấu hình. | **Tự nhiên & Trực tiếp:** Chạy trực tiếp mã nguồn Scikit-learn, Statsmodels, Apriori trong cùng runtime. |
| **Độ độc lập nền tảng & Triển khai** | Chỉ chạy trên hệ điều hành Windows; yêu cầu cài phần mềm Power BI Desktop (~1.5GB). | Chạy trên mọi nền tảng (Windows, macOS, Linux, Docker); mở trình duyệt là sử dụng được ngay. |
| **Đáp ứng yêu cầu môn học CO4031** | Đáp ứng tốt phần **Dashboard & Trực quan hóa OLAP**. | Đáp ứng hoàn hảo phần **Thành phần Hệ hỗ trợ Quyết định (DSS)**. |

### 1.2. Quyết định kiến trúc tối ưu: MÔ HÌNH SONG HÀNH (HYBRID ARCHITECTURE)

Nhóm thống nhất áp dụng kiến trúc **Song hành cộng hưởng** để tối đa hóa điểm số và trải nghiệm:
1. **Power BI (`reports/Global_Superstore_BI.pbix`):**
   - Đảm nhận toàn bộ báo cáo phân tích đa chiều kinh điển: *Executive Sales Overview, Geography & Market Performance, Product Portfolio*.
   - Kết nối trực tiếp vào schema `gold` (qua PostgreSQL ODBC/Connector).
2. **Interactive DSS Web App (`src/app/` chạy bằng Streamlit):**
   - Đảm nhận thành phần **Hỗ trợ Ra Quyết định Chuyên sâu (DSS Module)**:
     - Sandbox mô phỏng What-if thay đổi chiết khấu -> Nhận diện rủi ro lỗ và khuyến nghị điều chỉnh giá.
     - Trình khám phá dự báo doanh số 6 tháng tiếp theo (Forecast Explorer).
     - Công cụ tra cứu sản phẩm bán kèm (Cross-Selling Recommender).
3. **Backend API (`src/app/api/` chạy bằng FastAPI):**
   - Đóng vai trò là cầu nối cung cấp RESTful APIs cho web app, cho phép truy vấn dữ liệu từ PostgreSQL, thực thi mô hình mô phỏng và trả về JSON chuẩn.

---

## 2. Ý TƯỞNG THIẾT KẾ VÀ WIREFRAME GIAO DIỆN DSS (DSS UI MOCKUPS)

Giao diện web DSS được tổ chức thành 4 phân hệ chức năng trực quan:

```text
+----------------------------------------------------------------------------------------------------+
|  GLOBAL SUPERSTORE - EXECUTIVE DECISION SUPPORT SYSTEM (DSS)                      [User: Director] |
+----------------------------------------------------------------------------------------------------+
| [Tab 1: Executive KPI] | [Tab 2: What-If Simulator] | [Tab 3: Forecast] | [Tab 4: Cross-Selling]   |
+----------------------------------------------------------------------------------------------------+
```

### 2.1. Tab 1: Executive KPI & Risk Monitoring (Giám sát Tổng quan & Cảnh báo)
- **Top Metrics Row:**
  - `Total Sales: $12.64M` (Tăng trưởng YoY: +21.4%)
  - `Net Profit: $1.47M` (Biên lợi nhuận: 11.6%)
  - `Avg Discount: 14.3%` (Cảnh báo vàng tại APAC: 18.2%)
  - `Return Rate: 2.3%` (Mức an toàn < 3%)
- **Cảnh báo rủi ro (Risk Alert Center):**
  - Highlight đỏ: Danh sách 5 quốc gia có doanh thu > \$100K nhưng lợi nhuận bị âm do chiết khấu quá cao.

```text
+----------------------------------------------------------------------------------------------------+
| [ KPI CARDS ]                                                                                      |
|  +--------------------+  +--------------------+  +--------------------+  +----------------------+  |
|  | TOTAL SALES        |  | NET PROFIT         |  | PROFIT MARGIN      |  | RETURN RATE          |  |
|  | $12,642,501.9      |  | $1,467,457.3       |  | 11.61%             |  | 2.29%                |  |
|  | (+21.4% YoY)       |  | (+18.2% YoY)       |  | (Target: >=12%)    |  | (Threshold: <=3%)    |  |
|  +--------------------+  +--------------------+  +--------------------+  +----------------------+  |
+----------------------------------------------------------------------------------------------------+
| [ CRITICAL ALERTS: NEGATIVE PROFIT HOTSPOTS ]                                                      |
|  (!) WARNING: Market 'APAC' - Category 'Furniture' has Margin = -2.4% (Sales: $450K, Profit: -$11K)|
|  (!) ACTION NEEDED: 12 Products in 'Tables' sub-category selling at average discount 45%.         |
+----------------------------------------------------------------------------------------------------+
```

---

### 2.2. Tab 2: What-If Discount & Profit Simulator (Mô phỏng Quyết định Chiết khấu)
- **Khu vực điều khiển tham số (Control Panel bên trái):**
  - Chọn Thị trường mục tiêu: Dropdown `[APAC / EMEA / EU / LATAM / US]`.
  - Chọn Ngành hàng: Dropdown `[Furniture / Office Supplies / Technology]`.
  - Thanh trượt điều chỉnh Chiết khấu ($\Delta \text{Discount}$): `-20%` đến `+30%`.
  - Thanh trượt giả định độ co giãn cầu ($e$): `0.5` đến `2.5` (Mặc định `1.4`).
- **Khu vực hiển thị kết quả mô phỏng (Simulation Results bên phải):**
  - Biểu đồ cột so sánh: **Trước mô phỏng (Baseline)** vs **Sau mô phỏng (Simulated)**.
  - Hộp khuyến nghị tự động (Prescriptive Recommendation Box):
    - *"Nếu áp dụng chiết khấu 25% cho ngành hàng Furniture tại APAC, doanh thu tăng \$85,000 nhưng lợi nhuận giảm \$24,000 (Margin rơi xuống 3.2%). HỆ THỐNG KHUYẾN NGHỊ: TỪ CHỐI KỊCH BẢN NÀY."*

```text
+----------------------------------------------------------------------------------------------------+
| WHAT-IF SIMULATION SANDBOX                                                                         |
+-----------------------------------+----------------------------------------------------------------+
| [ PARAMETERS SELECTION ]          | [ SIMULATION OUTCOMES ]                                        |
| Target Market: [ APAC         v ] | Baseline Profit: $438,421  --->  Simulated Profit: $392,110    |
| Category:      [ Furniture    v ] | Baseline Sales:  $1,240,000 ---> Simulated Sales:  $1,360,000  |
| Discount Adjust: [---O-------] +5%| Profit Margin:   35.3%     --->  Margin:           28.8%       |
| Elasticity (e):  [-----O-----] 1.4+----------------------------------------------------------------+
|                                   | [ DECISION RECOMMENDATION ENGINE ]                             |
| [ Run Simulation ]  [ Reset ]     | [!] CAUTION: Decreasing margin by 6.5%. Volume gain is NOT     |
|                                   |     sufficient to cover discount erosion.                      |
+-----------------------------------+----------------------------------------------------------------+
```

---

### 2.3. Tab 3: Sales Forecasting Explorer (Dự báo Doanh số Tương lai)
- Người dùng chọn khoảng thời gian dự báo (3 tháng, 6 tháng, 12 tháng).
- Biểu đồ chuỗi thời gian hiển thị:
  - Đường nét liền màu xanh: Doanh số thực tế lịch sử (Actual).
  - Đường nét đứt màu cam: Dự báo trung tâm (Point Forecast).
  - Vùng đổ bóng mờ: Dải khoảng tin cậy 95% (Confidence Interval).
- Bảng số liệu chi tiết theo từng tháng và các chỉ số kiểm định mô hình (MAE, RMSE, MAPE).

---

### 2.4. Tab 4: Market Basket & Cross-Selling Navigator (Khai phá Bán kèm)
- Chọn một sản phẩm gốc (Antecedent).
- Hệ thống hiển thị bảng các sản phẩm gợi ý mua kèm (Consequents) có điểm Lift cao nhất.
- Nêu rõ xác suất: *"72% khách hàng mua Bàn học cũng sẽ mua Kẹp tài liệu (Lift = 3.2)"*.
- Đề xuất combo gói sản phẩm để thiết lập chương trình khuyến mại.

---

## 3. ĐẶC TẢ HỢP ĐỒNG BACKEND API (FASTAPI REST CONTRACTS)

Backend được tổ chức trong `src/app/api/`, cung cấp các endpoint RESTful chuẩn:

### 3.1. `GET /api/kpi/summary`
- **Mục đích:** Trả về các chỉ số KPI tổng quan toàn hệ thống.
- **Query params:** `year` (optional), `market` (optional).
- **Response JSON:**
```json
{
  "total_sales": 12642501.9,
  "total_profit": 1467457.3,
  "profit_margin_pct": 11.61,
  "total_orders": 25035,
  "avg_discount_pct": 14.29,
  "return_rate_pct": 2.29,
  "total_units_sold": 178312
}
```

### 3.2. `POST /api/dss/what-if`
- **Mục đích:** Thực thi mô phỏng What-if với các tham số do người dùng điều chỉnh.
- **Request JSON:**
```json
{
  "market": "APAC",
  "category": "Furniture",
  "discount_adjustment": 0.05,
  "elasticity": 1.4
}
```
- **Response JSON:**
```json
{
  "baseline": {
    "sales": 1240000.0,
    "profit": 438421.0,
    "margin_pct": 35.35
  },
  "simulated": {
    "sales": 1360000.0,
    "profit": 392110.0,
    "margin_pct": 28.83,
    "sales_change_pct": 9.68,
    "profit_change_pct": -10.56
  },
  "recommendation": {
    "status": "CAUTION",
    "message": "Tăng chiết khấu làm giảm tổng lợi nhuận $46,311 (-10.56%). Không khuyến nghị áp dụng trên diện rộng."
  }
}
```

### 3.3. `GET /api/dss/forecast`
- **Mục đích:** Lấy kết quả dự báo doanh thu chuỗi thời gian.
- **Query params:** `horizon` (mặc định 6 tháng), `category` (optional).
- **Response JSON:**
```json
{
  "model": "Holt-Winters Exponential Smoothing",
  "metrics": { "mae": 15420.5, "rmse": 19800.2, "mape": 4.12 },
  "forecast": [
    { "date": "2015-01-01", "predicted": 125400.0, "lower": 112000.0, "upper": 138800.0 },
    { "date": "2015-02-01", "predicted": 131200.0, "lower": 116500.0, "upper": 145900.0 },
    { "date": "2015-03-01", "predicted": 142000.0, "lower": 125000.0, "upper": 159000.0 }
  ]
}
```

### 3.4. `GET /api/dss/association-rules`
- **Mục đích:** Lấy danh sách luật kết hợp sản phẩm mua kèm có điểm Lift cao nhất.
- **Query params:** `min_lift` (mặc định 1.2), `limit` (mặc định 20).
- **Response JSON:**
```json
{
  "algorithm": "Apriori",
  "total_rules": 42,
  "rules": [
    {
      "antecedents": ["OFF-BIN-10000010"],
      "antecedent_name": "Fellowes Bankers Box",
      "consequents": ["OFF-ST-10001420"],
      "consequent_name": "Tenex File Folders",
      "support": 0.0124,
      "confidence": 0.6842,
      "lift": 3.42
    }
  ]
}
```
