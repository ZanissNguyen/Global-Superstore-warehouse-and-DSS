# HƯỚNG DẪN 07: XỬ LÝ SỰ CỐ & CÁC LỖI THƯỜNG GẶP (TROUBLESHOOTING GUIDE)

---

## 1. SỰ CỐ XUNG ĐỘT CỔNG DOCKER POSTGRES (PORT CONFLICT 5432)

### Triệu chứng:
Khi chạy lệnh `docker compose up -d`, Docker báo lỗi:
```text
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:5432 -> 0.0.0.0:0: bind: address already in use
```

### Nguyên nhân:
Cổng 5432 đang bị chiếm dụng bởi một dịch vụ PostgreSQL cài trực tiếp trên máy Windows hoặc một container Docker khác (ví dụ: một dự án backend khác đang chạy).

### Cách khắc phục:
1. Mở file `.env` và sửa giá trị `DB_PORT`:
   ```ini
   DB_PORT=5433
   ```
2. Khởi động lại Docker:
   ```powershell
   docker compose down
   docker compose up -d
   ```
3. Lúc này, PostgreSQL sẽ lắng nghe trên cổng `5433` ở máy chủ. Cả mã nguồn Python và Power BI đều sẽ tự động kết nối qua cổng 5433 mà không cần sửa code.

---

## 2. LỖI THIẾU THƯ VIỆN PYTHON (MODULENOTFOUNDERROR)

### Triệu chứng:
Chạy lệnh Python báo lỗi: `ModuleNotFoundError: No module named 'psycopg2'` hoặc `No module named 'sqlalchemy'` hoặc `No module named 'xlrd'`.

### Cách khắc phục:
Cài đặt bổ sung gói bị thiếu:
```powershell
pip install psycopg2-binary sqlalchemy xlrd openpyxl streamlit scikit-learn mlxtend
```

---

## 3. LỖI MÃ HÓA KHI ĐỌC FILE CSV NGUỒN (UNICODEDECODEERROR)

### Triệu chứng:
```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position ...: invalid continuation byte
```

### Nguyên nhân:
File dữ liệu `superstore_dataset2011-2015.csv` từ Kaggle được lưu dưới bảng mã ANSI / Latin-1 (ISO-8859-1) hoặc Windows-1252 do có chứa ký tự tên riêng tiếng Tây Ban Nha / Pháp.

### Cách khắc phục:
Trong module `src/pipeline/reader.py`, nhóm đã lập trình sẵn cơ chế tự động thử lần lượt các bảng mã `['utf-8', 'cp1252', 'latin1']`. Nếu bạn tự đọc bằng pandas, luôn chỉ định rõ:
```python
df = pd.read_csv(file_path, encoding='latin1')
```

---

## 4. LỖI PARSE NGÀY THÁNG ĐA ĐỊNH DẠNG (DATE PARSING ERROR)

### Triệu chứng:
```text
ValueError: time data '13-01-2011' does not match format '%m/%d/%Y'
```

### Nguyên nhân:
Trong tập dữ liệu Global Superstore, có những dòng lưu ngày dạng `1/1/2011` (dùng dấu gạch chéo) và có những dòng lưu `13-01-2011` (dùng dấu gạch nối, ngày đứng trước tháng).

### Cách khắc phục:
Sử dụng tham số `format='mixed'` và `dayfirst=True` trong pandas:
```python
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True)
```
Tất cả các ngày sẽ được chuẩn hóa đồng nhất về định dạng chuẩn ISO: `YYYY-MM-DD`.

---

## 5. LỖI KẾT NỐI CƠ SỞ DỮ LIỆU BỊ TỪ CHỐI (CONNECTION REFUSED)

### Triệu chứng:
```text
sqlalchemy.exc.OperationalError: connection to server at "localhost", port 5432 failed: Connection refused
```

### Cách khắc phục:
1. Kiểm tra xem container PostgreSQL có đang chạy không:
   ```powershell
   docker ps
   ```
2. Nếu container bị dừng, khởi động lại:
   ```powershell
   docker compose restart postgres
   ```
3. Xem log của container để kiểm tra nguyên nhân:
   ```powershell
   docker logs superstore_postgres
   ```

---

## 6. LỖI LỆNH STREAMLIT HOẶC UVICORN KHÔNG ĐƯỢC NHẬN DIỆN (COMMANDNOTFOUNDEXCEPTION)

### Triệu chứng:
```text
streamlit : The term 'streamlit' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

### Nguyên nhân:
Thư mục `Scripts` của Python (ví dụ: `C:\Users\<User>\AppData\Roaming\Python\Python312\Scripts`) chưa được cấu hình vào biến môi trường hệ thống (`PATH`) của Windows.

### Cách khắc phục:
Chạy thông qua module Python với cờ `-m` (luôn hoạt động ổn định trên mọi máy tính):
```powershell
python -m streamlit run src/app/main.py
```
Tương tự đối với dịch vụ FastAPI:
```powershell
python -m uvicorn src.app.api.main:app --reload --port 8000
```

---

## 7. LỖI CARDINALITY VIOLATION KHI NẠP DIM_GEOGRAPHY

### Triệu chứng:
```text
psycopg2.errors.CardinalityViolation: ON CONFLICT DO UPDATE command cannot affect row a second time
```

### Nguyên nhân:
Trong tập dữ liệu Global Superstore, có những thành phố/tiểu bang cùng tên xuất hiện ở các thị trường khác nhau hoặc cùng một vị trí địa lý nhưng đơn hàng được phân bổ vào các vùng quản lý khác nhau (ví dụ: `Vienna, Austria` thuộc cả `EMEA` và `EU`).

### Cách khắc phục:
Nhóm đã chuẩn hóa cấu trúc bảng và câu lệnh nạp:
1. Mở rộng ràng buộc duy nhất trong `gold.dim_geography` thành:
   `UNIQUE (country, state, city, postal_code, market, region)`
2. Sử dụng `SELECT DISTINCT ON (country, state, city, postal_code, market, region)` trong `src/sql/gold/dimensions/load_dim_geography.sql` để loại trừ hoàn toàn việc xung đột bản ghi trong cùng một lệnh thực thi.


---

## 8. SỰ CỐ POWER BI DESKTOP: BIỂU ĐỒ DOANH THU & LỢI NHUẬN CÁI NÀO COUNT CŨNG LÀ 1

### Triệu chứng:
Khi tạo biểu đồ Doanh thu và Lợi nhuận theo tháng (Line and Clustered Column Chart) trên Power BI Desktop:
- Trục tung hiển thị nhãn `Count of sales` hoặc `Count of profit`.
- Tất cả các cột/điểm trên biểu đồ đều có giá trị bằng `1` (hoặc đồ thị phẳng lì, không thể hiện tổng số tiền từ vài chục nghìn đến hàng trăm nghìn USD).

### Nguyên nhân:
1. **Kéo trực tiếp cột thô thay vì dùng DAX Measure:** Người dùng kéo trực tiếp cột `sales` / `profit` từ bảng `fact_sales` vào vùng Y-axis / Values. Nếu Power BI nhận diện cột là `Text` hoặc để mặc định phép gộp là `Count`, nó sẽ đếm từng dòng là 1 thay vì tính tổng giá trị tiền tệ.
2. **Chưa tạo mối quan hệ (Model Relationship) giữa bảng Ngày và bảng Fact:** Trong tab **Model view**, bảng `gold dim_date` chưa được liên kết với bảng `gold fact_sales`. Khi không có quan hệ, Power BI không thể gom nhóm các đơn hàng theo tháng.
3. **Kéo nhầm cột định danh bản ghi (`row_id` hoặc `order_date_key`):** Cột `row_id` là mã duy nhất cho từng dòng trong 51,290 bản ghi. Kéo `row_id` vào trục hoành sẽ khiến biểu đồ vẽ 51,290 điểm rời rạc, mỗi điểm ứng với đúng 1 giao dịch (`count = 1`).

### Cách khắc phục chuẩn mực (3 bước):
1. **Kiểm tra và tạo liên kết trong Model View:**
   - Mở tab **Model view** (biểu tượng lược đồ bên trái Power BI Desktop).
   - Kéo trường `date_key` từ bảng `gold dim_date` thả vào trường `order_date_key` của bảng `gold fact_sales`.
   - Đảm bảo quan hệ được tạo là **1-to-Many ($1 : *)$**, hướng lọc **Single**, trạng thái **Active** (đường nét liền).
2. **Kiểm tra kiểu dữ liệu trong Data View:**
   - Chọn bảng `gold fact_sales`, bấm vào cột `sales` và `profit`.
   - Kiểm tra thanh công cụ: **Data type = Decimal Number** (hoặc Fixed Decimal Number), **Format = Currency (\$ English)**.
3. **Sử dụng DAX Measure chuẩn (TUYỆT ĐỐI không kéo cột thô):**
   - Vào menu **Home** -> **New Measure**, nhập các công thức từ file `reports/powerbi/03_DAX_MEASURES.dax`:
     ```dax
     Total Sales = SUM('gold fact_sales'[sales])
     Total Profit = SUM('gold fact_sales'[profit])
     Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)
     ```
   - Cấu hình Visual **Line & Clustered Column Chart**:
     - **X-axis (Trục hoành):** Kéo `gold dim_date[year_month]`
     - **Column y-axis (Cột):** Kéo measure `[Total Sales]` (Sẽ hiển thị chuẩn xác từ $91,152 đến $555,279/tháng).
     - **Line y-axis (Đường):** Kéo measure `[Total Profit]` (Hiển thị từ $5,585 đến $62,856/tháng).

---

## 9. SỰ CỐ KHAI PHÁ GIỎ HÀNG BÁO "DISCOVERED 0 VALID RULES" (0 LUẬT KẾT HỢP)

### Triệu chứng:
Khi chạy lệnh khai phá giỏ hàng:
```powershell
python -m src.dss.association.run --algorithm apriori --min-support 0.005 --min-confidence 0.25 --min-lift 1.2
```
Console in ra:
```text
Analyzed 25035 transactions. Discovered 0 valid rules.
Persisted 0 association rules to dss schema under run #X.
```

### Nguyên nhân:
1. Khi không truyền tham số `--level`, thuật toán mặc định chạy ở cấp độ **Tên sản phẩm chi tiết (`product`)**, với danh mục gồm hơn **10,292 mặt hàng SKU khác nhau** trong 25,035 đơn hàng.
2. Tham số `--min-support 0.005` (0.5%) tương đương việc đòi hỏi hai mã sản phẩm chi tiết cụ thể phải xuất hiện chung trong tối thiểu **125 đơn hàng** ($25,035 \times 0.005 \approx 125$).
3. Trong thực tế ngành bán lẻ, các mặt hàng cụ thể (ví dụ: một cây bút bi xanh và một tập giấy note vàng) có mức độ phân tán rất cao (Data Sparsity), hiếm khi đồng xuất hiện tới 125 lần. Do đó, thuật toán không tìm được tập mục thỏa mãn và trả về 0 luật.

### Cách khắc phục chuẩn:
Tùy vào mục tiêu phân tích kinh doanh, sử dụng một trong hai lệnh sau:

**Lựa chọn 1: Khai phá cấp độ Ngành hàng con (Sub-Category) — Khuyến nghị cho Quản lý danh mục:**
```powershell
python -m src.dss.association.run --level sub_category --min-support 0.005 --min-confidence 0.10 --min-lift 1.05
```
- Khai phá ra **14 luật** có ý nghĩa nghiệp vụ cao:
  - Khách mua *Copiers (Máy photocopy)* $\rightarrow$ Gợi ý *Labels (Nhãn dán)* hoặc *Envelopes (Phong bì)* (Lift: 1.17x).
  - Khách mua *Appliances (Thiết bị gia dụng)* $\rightarrow$ Gợi ý *Paper (Giấy in)* hoặc *Binders (Bìa còng)* (Lift: 1.16x).
  - Khách mua *Accessories (Phụ kiện điện tử)* $\rightarrow$ Gợi ý *Phones (Điện thoại)* (Lift: 1.07x).

**Lựa chọn 2: Khai phá cấp độ Mặt hàng chi tiết (Product SKU) — Khuyến nghị cho Gợi ý Combo cụ thể:**
```powershell
python -m src.dss.association.run --level product --min-count 3 --min-confidence 0.10 --min-lift 1.2
```
- Sử dụng tham số `--min-count 3` (đồng xuất hiện từ 3 đơn hàng trở lên) thay cho tỷ lệ phần trăm support cố định.
- Khai phá ra **27 luật** với hệ số Lift cực đại lên tới **315.57x** (ví dụ: *Memorex Flash Drive* và *Jiffy Mailers*).

---

## 10. LỖI POSTGRESQL "SELECT DISTINCT, ORDER BY expressions must appear in select list"

### Triệu chứng:
Khi truy vấn danh sách luật kết hợp hoặc bảng tổng hợp bằng SQL có mệnh đề `SELECT DISTINCT ... ORDER BY lift DESC`, hệ thống báo lỗi:
```text
psycopg2.errors.InvalidColumnReference: for SELECT DISTINCT, ORDER BY expressions must appear in select list
LINE: ORDER BY lift DESC
```

### Nguyên nhân:
Trong hệ quản trị CSDL PostgreSQL, khi sử dụng mệnh đề `SELECT DISTINCT`, tiêu chuẩn SQL đòi hỏi tất cả các biểu thức hoặc cột xuất hiện trong mệnh đề `ORDER BY` bắt buộc phải có mặt chính xác (nguyên mẫu hoặc cùng alias) trong danh sách `SELECT`. Nếu trong `SELECT` sử dụng hàm `ROUND(lift, 2) AS "Lift"` nhưng trong `ORDER BY` lại gọi `lift`, PostgreSQL sẽ từ chối thực thi để đảm bảo tính xác định (determinism) của các dòng loại bỏ trùng lặp.

### Cách khắc phục:
Bọc câu lệnh trong một subquery để tách biệt bước loại bỏ trùng lặp (`DISTINCT`) và bước sắp xếp (`ORDER BY`):
```sql
SELECT 
    antecedent_names AS "San_Pham_Mua_Truoc",
    consequent_names AS "San_Pham_Goi_Y_Mua_Kem",
    ROUND(support * 100, 3) AS "Support_%",
    ROUND(confidence * 100, 2) AS "Confidence_%",
    ROUND(lift, 2) AS "Lift"
FROM (
    SELECT DISTINCT antecedent_names, consequent_names, support, confidence, lift
    FROM dss.association_rule
) sub
ORDER BY "Lift" DESC
LIMIT 25;
```
*(Cơ chế này đã được cập nhật chuẩn mực vào hàm `load_db_rules()` trong `src/app/main.py`)*.
