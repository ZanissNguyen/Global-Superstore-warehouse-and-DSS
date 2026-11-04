# HƯỚNG DẪN 01: THIẾT LẬP MÔI TRƯỜNG PHÁT TRIỂN & CSDL (ENVIRONMENT SETUP)

---

## 1. YÊU CẦU TIỀN ĐỀ (PREREQUISITES)

Để chạy trọn vẹn dự án, máy tính cần cài đặt sẵn:
1. **Python 3.10 – 3.12:** [Tải từ Python.org](https://www.python.org/downloads/) (Lưu ý tích chọn *"Add python.exe to PATH"* khi cài đặt).
2. **Docker Desktop:** [Tải từ Docker.com](https://www.docker.com/products/docker-desktop/) (Đảm bảo Docker daemon đang chạy).
3. **Git:** Quản lý mã nguồn.
4. *(Tùy chọn)* **Power BI Desktop:** Nếu muốn mở và chỉnh sửa file báo cáo `.pbix`.

---

## 2. THIẾT LẬP PYTHON VÀ CÀI ĐẶT THƯ VIỆN

### 2.1. Kiểm tra phiên bản Python:
Mở PowerShell hoặc Command Prompt tại thư mục gốc của dự án:
```powershell
python --version
pip --version
```

### 2.2. Tạo và kích hoạt môi trường ảo (Khuyến nghị):
```powershell
# Tạo môi trường ảo mang tên .venv
python -m venv .venv

# Kích hoạt trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# (Nếu gặp lỗi Execution Policy trên PowerShell, chạy lệnh sau rồi kích hoạt lại):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2.3. Cài đặt các gói thư viện phụ thuộc:
Cài đặt toàn bộ danh sách gói trong `requirements.txt`:
```powershell
pip install -r requirements.txt
```

Nếu cần chạy thêm các tính năng Web App và DSS Machine Learning, đảm bảo các thư viện sau đã có mặt:
```powershell
pip install streamlit scikit-learn statsmodels mlxtend
```

---

## 3. CẤU HÌNH BIẾN MÔI TRƯỜNG (`.env`)

Tại thư mục gốc của dự án, sao chép file mẫu `.env.example` thành `.env`:
```powershell
cp .env.example .env
```

Nội dung file `.env` chuẩn:
```ini
# Cấu hình kết nối PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=your_password_here
DB_NAME=global_superstore

# Cấu hình giao diện pgAdmin 4
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=your_password_here
```

### ⚠️ LƯU Ý ĐẶC BIỆT: XỬ LÝ XUNG ĐỘT CỔNG 5432 TRÊN WINDOWS
Nếu máy tính của bạn đã cài sẵn một bản PostgreSQL cục bộ hoặc có container Docker khác đang chiếm dụng cổng `5432` (ví dụ: `restaurant_ordering-postgres-1`):
1. Đổi cổng trong file `.env`:
   ```ini
   DB_PORT=5433
   ```
2. Trong file `docker-compose.yml`, cổng ngoài sẽ tự động nhận giá trị `5433:5432`.
3. Khi kết nối từ Python hoặc Power BI, dùng cổng `5433`.

---

## 4. KHỞI ĐỘNG CƠ SỞ DỮ LIỆU BẰNG DOCKER COMPOSE

Khởi động PostgreSQL 17 và pgAdmin 4 ở chế độ nền (background):
```powershell
docker compose up -d
```

Kiểm tra trạng thái hoạt động của các container:
```powershell
docker ps
```
Kết quả hiển thị `superstore_postgres` ở trạng thái `healthy` và `superstore_pgadmin` ở trạng thái `Up`.

### Truy cập pgAdmin 4:
- Mở trình duyệt tại: `http://localhost:5050`
- Đăng nhập bằng email và mật khẩu trong file `.env`.
- Thêm kết nối tới server:
  - **Host name:** `postgres` (nếu chạy trong mạng docker) hoặc `localhost` / `host.docker.internal`
  - **Port:** `5432` (bên trong container) hoặc `5433` (từ máy host)
  - **Username:** `admin`
  - **Password:** Mật khẩu trong file `.env`

---

## 5. KIỂM TRA KẾT NỐI TỪ PYTHON
Chạy lệnh kiểm tra kết nối từ terminal:
```powershell
python -c "from src.pipeline.database import create_db_engine, test_connection; engine = create_db_engine(); print('Database connection OK:', test_connection(engine))"
```
Nếu màn hình in ra:
```text
Database connection OK: True
```
Bạn đã hoàn tất bước thiết lập môi trường và sẵn sàng tiến hành khởi tạo CSDL!
