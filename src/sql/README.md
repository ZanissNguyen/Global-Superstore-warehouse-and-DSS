# SQL trong ứng dụng

Python đọc các file trong thư mục này bằng `src.pipeline.reader.read_sql(path)`, với `path` tính từ `src/sql/`. Truy vấn dữ liệu dùng `query_sql(engine, read_sql(path), params)`; lệnh ghi dùng `text(read_sql(path))` trong transaction hiện có.

- `gold/dashboard/`: truy vấn cho tab Tổng quan, lọc theo ngày đặt hàng và phạm vi địa lý.
- `gold/whatif/`, `dss/forecast/`, `dss/association/`: nguồn dữ liệu và kết quả DSS.
- `demo/`, `incremental/`: điều khiển phiên demo và đối soát ETL.
- `api/`, `export/`, `system/`: API, xuất dữ liệu và tiện ích database.

Giá trị thay đổi theo người dùng truyền qua bind parameters như `:start_key` và `:market`. Các trường hợp thay đổi tên cột dùng file SQL riêng cho từng biến thể. Các file `gold/marts/olap_*.sql` là ví dụ OLAP, không thay cho truy vấn của dashboard.
