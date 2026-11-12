# Ý chính thuyết trình DW và DSS cho ba người

> Thời lượng đề xuất: 12 phút, mỗi người 4 phút. Đây là dàn ý và số liệu đối chiếu, không phải lời thoại. Chia theo chức năng đang có trong source và cả 5 tab Streamlit.
>
> Số liệu nền được đọc từ PostgreSQL local ngày 12/11/2026, khi không có phiên upload hoạt động. Số sau upload là **kỳ vọng từ file demo trên nền sạch**; đọc lại bảng đối soát và UI trong lúc quay.

## Số liệu chung cần thống nhất

| Chỉ số | Database nền hiện tại | File demo 500 dòng | Sau khi upload thành công từ nền sạch |
|---|---:|---:|---:|
| Dòng Bronze, Silver, Gold | 51.290 ở mỗi tầng | +500 | 51.790 ở mỗi tầng |
| Đơn hàng riêng biệt | 25.035 | 204 trong file | Đọc lại trên UI; không mặc định cộng 204 nếu mã đơn trùng |
| Doanh thu | 12.642.501,91 USD | +613.777,19 USD | 13.256.279,10 USD |
| Lợi nhuận | 1.467.457,29 USD | +138.840,67 USD | 1.606.297,96 USD |

- Dữ liệu nền: ngày đặt hàng 01/01/2011–31/12/2014; 178.312 sản phẩm bán ra, 7 thị trường, 147 quốc gia; biên lợi nhuận 11,61%, chiết khấu bình quân mỗi dòng 14,29%.
- **51.290 là số dòng sản phẩm trong đơn hàng**, không phải số đơn. Biên lợi nhuận = `SUM(profit) / SUM(sales) × 100` trong phạm vi lọc.
- Sau upload, số trên tab Tổng quan phụ thuộc khoảng ngày và địa lý đang chọn. Muốn đối chiếu với cột tổng ở trên, chọn **Toàn bộ** và **Tất cả** địa lý.

## Người 1 — Bài toán, DW và Tổng quan kinh doanh (0:00–4:00)

### Ý cần nói

1. **Bài toán:** phân tích doanh thu đồng thời phát hiện nhóm có lợi nhuận âm; hỗ trợ quyết định về giá, kế hoạch doanh thu và bán kèm.
2. **Kiến trúc thực tế:** CSV → Bronze → Silver → Gold → truy vấn OLAP và tính DSS → Streamlit. PostgreSQL chạy trong Docker. Streamlit truy vấn PostgreSQL trực tiếp; FastAPI là dịch vụ tùy chọn, không phải đường dữ liệu mà UI đang gọi.
3. **Bronze:** lưu dòng nguồn và thông tin lần nạp; SHA-256 nhận biết file đã nạp để tránh nạp lặp cùng nội dung.
4. **Silver:** chuẩn hóa ngày, kiểu số và chuỗi; mã bưu chính trống thành `Unknown`. Có các câu kiểm tra dữ liệu; ở luồng CLI, một số hàm validation **in kết quả kiểm tra**, chưa phải toàn bộ là cổng chặn tự động.
5. **Gold:** `fact_sales` ở grain một dòng sản phẩm trong một đơn hàng, liên kết năm chiều `date`, `customer`, `product`, `geography`, `ship_mode` bằng khóa thay thế. Có ba materialized view cho sales, product và customer; biểu đồ UI hiện đọc fact/dimension để hỗ trợ bộ lọc ngày tùy ý.
6. **Tab Tổng quan kinh doanh:** năm KPI đầu trang; xu hướng theo ngày/tuần/tháng; đi sâu địa lý thị trường → khu vực → quốc gia; ba phân khúc Consumer, Corporate, Home Office; ngành hàng, ngành hàng con lỗ, điểm rủi ro và top 5–10 sản phẩm. Các bộ lọc dùng chung kỳ đặt hàng và phạm vi địa lý. YoY chỉ xuất hiện khi có dữ liệu cùng kỳ năm trước.

### Số liệu và thao tác nên chỉ trên màn hình

- Trên slide kiến trúc, ghi **51.290 dòng fact**; trên UI, chỉ KPI **25.035 đơn**, doanh thu **12,64 triệu USD**, lợi nhuận **1,47 triệu USD**, biên **11,61%** ở dữ liệu nền. Nếu KPI đang lọc, đưa về **Toàn bộ / Tất cả** trước.
- Thay khoảng thời gian rồi chọn thị trường, khu vực hoặc quốc gia để chứng minh slice và drill-down; chỉ vào nhóm có lợi nhuận âm, không đọc toàn bộ bảng.
- Top sản phẩm là biểu đồ thanh theo số lượng hoặc doanh thu; biểu đồ quạt là **tỷ trọng ngành hàng**, không phải tỷ trọng từng sản phẩm.

### Chuyển ý

- Bàn giao cho Người 2 ở câu hỏi: “Khi có file giao dịch mới, hệ thống cập nhật các phân tích này như thế nào?”

## Người 2 — OLAP, nạp dữ liệu mới và What-if (4:00–8:00)

### Ý cần nói

1. **OLAP gắn với UI:** slice theo ngày/địa lý; roll-up xu hướng theo ngày, tuần, tháng; drill-down địa lý và sản phẩm; xếp hạng Top N; lọc nhóm lỗ. Repo có bảy truy vấn OLAP mẫu (Roll-up, Drill-down, Slice/Dice, Pivot, MoM, Top Products, Cube), nhưng Pivot/MoM/Cube là ví dụ bổ sung, không phải chart đang hiển thị. SQL của chart nằm trong `src/sql/gold/dashboard/`.
2. **Data mart:** ba materialized view đã có lần lượt 7.424 dòng sales mart, 29.363 dòng product mart và 1.590 dòng customer mart ở database nền đang kiểm tra. Mart được refresh sau ETL; **không nói UI đọc trực tiếp mart**. Grain của mart không bao phủ mọi bộ lọc ngày và địa lý trên UI.
3. **File demo:** `dataset/incremental_orders_2015_q1.csv` có 500 dòng, 204 đơn, doanh thu 613.777,19 USD, lợi nhuận 138.840,67 USD. Chọn file chỉ xem trước, chưa đổi dữ liệu Gold.
4. **Xử lý sau khi bấm nút:** kiểm tra file và Row ID → clone database nền thành `demo_<mã phiên>` → Bronze → Silver → Gold → đối soát số dòng và tiền → refresh ba mart → chạy lại dự báo và bán kèm → kích hoạt database demo. Bảng đối soát lấy số **trước/sau từ hai database**. Nếu có lỗi trước khi kích hoạt, phiên đang dùng vẫn hoạt động.
5. **Các lần upload tiếp:** mỗi lần tạo database demo **mới từ nền**, không cộng nối vào phiên demo trước. Có thể thay file rồi xử lý lại; UI chưa hỗ trợ sửa từng dòng CSV. Database demo cũ chưa được dọn tự động.
6. **Tab Quyết định giá và chiết khấu:** baseline doanh thu, lợi nhuận, chiết khấu lấy từ Gold theo kỳ/thị trường/ngành hàng. Thanh trượt đổi chiết khấu và độ co giãn giả định; mô hình tính thay đổi giá, cầu, doanh thu, chi phí và lợi nhuận rồi đưa khuyến nghị. Đây là **kịch bản giả định**, không ghi kết quả vào Gold; độ co giãn chưa được ước lượng từ dữ liệu.

### Thao tác demo và kết quả cần đối chiếu

- Chọn file 500 dòng, chỉ vào preview và bấm **Xử lý dữ liệu và kích hoạt phiên**. Trong lúc chờ, giải thích từng bước backend đang báo trên UI.
- Chỉ vào bảng trước/sau: mỗi tầng tăng **500 dòng**; doanh thu tăng **613.777,19 USD** và lợi nhuận tăng **138.840,67 USD**. Trở lại tab Tổng quan, chọn **Toàn bộ** để thấy dữ liệu mới và mốc năm 2015.
- Sang What-if, đổi chiết khấu, cho thấy doanh thu hoặc lợi nhuận kịch bản và thông báo khuyến nghị thay đổi. Nói rõ đây là số mô phỏng, không phải số thực sau ETL.

## Người 3 — Dự báo, bán kèm và quay về nền (8:00–12:00)

### Ý cần nói

1. **Tab Kế hoạch doanh thu và dự báo:** tổng hợp doanh thu Gold theo tháng; so sánh seasonal naïve với Holt–Winters cộng mùa vụ bằng backtest theo thứ tự thời gian. Hệ số Holt–Winters được chọn trên dữ liệu, mô hình được chọn theo MAE backtest. UI hiển thị **6 tháng dự báo cố định**; dropdown 12/24/48 tháng chỉ đổi lượng lịch sử hiển thị.
2. **Lưu kết quả:** mỗi run có `run_id`, mô hình, tham số, MAE/RMSE/MAPE/WMAPE và các điểm dự báo trong `dss.forecast_run` / `dss.forecast_result`. Reload trang đọc lại run đã lưu; upload thành công tạo run mới cho database demo. Dải sai số lấy từ residual backtest theo từng bước dự báo, **chưa phải khoảng tin cậy 95%**.
3. **Số nền đã kiểm tra:** run dự báo 6 tháng `#3` chọn **Holt-Winters additive**, MAPE **7,79%**, WMAPE **8,87%**. Sau upload, đọc mô hình và sai số **đang hiện trên UI**, không lặp lại số của run nền.
4. **Tab Cơ hội bán kèm:** gom sản phẩm theo `order_id`, đếm cặp xuất hiện cùng nhau, tính support, confidence và lift theo hai chiều luật A → B và B → A; lưu kết quả vào `dss.association_run` / `dss.association_rule`. UI tìm sản phẩm, lọc lift và hiển thị số giao dịch hỗ trợ **ước tính** từ support đã làm tròn.
5. **Số nền đã kiểm tra:** run bán kèm `#1` phân tích **25.035 giao dịch** và lưu **27 luật**. Metadata cũ ghi “Apriori Association Mining”, nhưng mã hiện tại **đếm cặp sản phẩm trực tiếp**, không phải triển khai Apriori tổng quát cho tập nhiều sản phẩm. Sau upload, đọc số luật của run mới trên UI.
6. **Quay về nền:** nút **Quay về dữ liệu nền** đổi nguồn đọc của cả năm tab về database ban đầu, xóa cache UI; không xóa database demo. Đây là cách lặp lại bài demo mà giữ bộ nền ổn định.

### Thao tác và kết luận

- Ở tab dự báo, chỉ đường doanh thu thực, 6 điểm dự báo, tên mô hình, `run_id` và chỉ số backtest. Ở tab bán kèm, tìm một sản phẩm rồi tăng ngưỡng lift.
- Cuối demo bấm **Quay về dữ liệu nền**, mở lại Tổng quan để chứng minh số liệu trở về mốc ban đầu.
- Kết luận bằng ba giá trị: **kho dữ liệu có grain rõ**, **OLAP tương tác theo cùng bộ lọc**, **DSS tạo và lưu kết quả theo phiên dữ liệu**. Hướng phát triển: dữ liệu trả hàng thực, ước lượng độ co giãn, quản lý database demo cũ.

## Checklist trước khi quay và điều không nên khẳng định

- Đưa UI về dữ liệu nền; kiểm tra Docker/PostgreSQL healthy, mở sẵn `http://localhost:8501`, chuẩn bị đúng file CSV 500 dòng. Dự phòng ảnh hoặc video ngắn của bảng đối soát nếu ETL chạy lâu.
- File demo có mã hóa `cp1252`; dùng bộ upload của UI, vốn thử nhiều encoding. Đọc CSV bằng mặc định UTF-8 trong một lệnh pandas riêng có thể báo lỗi dù file hợp lệ.
- Không gọi 51.290 là số đơn, không gọi nạp file là CDC thời gian thực, không nói FastAPI là backend bắt buộc của Streamlit.
- Không khẳng định đã tích hợp thông tin hoàn trả hoặc quản lý vùng: SQL Silver hiện gán `is_returned = FALSE` và `regional_manager = NULL`.
- Không dùng MAPE **4,15%**, “dải tin cậy 95%”, tốc độ truy vấn “dưới 50 ms” hoặc dashboard `.pbix` hoàn chỉnh từ slide cũ nếu chưa có minh chứng tương ứng. Repo hiện có tài liệu/script Power BI, chưa có file `.pbix`.
- Sau khi upload, chỉ đọc số đang hiển thị trên UI; KPI thay đổi theo kỳ, địa lý và database phiên đang hoạt động.

## Nguồn để người trình bày tự kiểm tra

- Luồng chạy lần đầu: [README](../../README.md); UI năm tab: [main.py](../../src/app/main.py); chi tiết UI: [05_UI_OVERVIEW_AND_DEMO_PLAN.md](05_UI_OVERVIEW_AND_DEMO_PLAN.md).
- ETL: [bronze_to_gold.py](../../src/pipeline/flows/bronze_to_gold.py), [transform_orders.sql](../../src/sql/silver/transform/transform_orders.sql), [create_fact_sales.sql](../../src/sql/gold/schema/create_fact_sales.sql).
- Upload và đối soát: [demo_backend.py](../../src/app/demo_backend.py); OLAP UI: [dashboard SQL](../../src/sql/gold/dashboard/); Data mart: [create_materialized_views.sql](../../src/sql/gold/marts/create_materialized_views.sql).
- DSS: [simulate.py](../../src/dss/what_if/simulate.py), [predictive/run.py](../../src/dss/predictive/run.py), [association/run.py](../../src/dss/association/run.py).
