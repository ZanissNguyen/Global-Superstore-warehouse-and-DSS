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
