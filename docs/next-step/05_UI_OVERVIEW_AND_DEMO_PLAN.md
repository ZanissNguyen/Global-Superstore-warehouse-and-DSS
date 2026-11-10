# Tổng quan UI — Global Superstore DSS

> Tài liệu này mô tả **chức năng đang có trong UI**. Mở giao diện bằng
> `python -m streamlit run src/app/main.py` tại `http://localhost:8501`.
> Hướng dẫn cài đặt lần đầu nằm trong [README](../../README.md).

## 1. Dữ liệu và các tab

UI đọc PostgreSQL theo **phiên dữ liệu đang hoạt động**. Khi chưa kích hoạt phiên
demo, mọi tab đọc database nền cấu hình trong `.env`. Sau khi nạp file thành công,
mọi tab đọc database demo mới. Tiêu đề UI cho biết mã phiên và tên database hiện tại.

| Tab | Nội dung chính | Nguồn và cách tính |
|---|---|---|
| **Tổng quan kinh doanh** | KPI và xu hướng; hiệu quả theo thị trường/khu vực/quốc gia; ba phân khúc khách hàng; ngành hàng, ngành hàng con và nhóm lỗ; top sản phẩm và tỷ trọng ngành hàng. | Truy vấn `gold.fact_sales` và các dimension theo **cùng khoảng ngày đặt hàng và phạm vi địa lý**. YoY so với cùng kỳ năm trước khi đủ dữ liệu. |
| **Quyết định giá & chiết khấu** | Baseline theo kỳ, thị trường và ngành hàng; thay đổi chiết khấu, độ co giãn; kết quả và khuyến nghị. | Baseline từ Gold. Kết quả là **kịch bản giả định**, tính lại theo tham số người dùng và không ghi vào Gold. Độ co giãn chưa được huấn luyện từ dữ liệu. |
| **Kế hoạch danh thu & dự báo** | Doanh thu lịch sử theo tháng, dự báo cố định 6 tháng, khoảng sai số, MAE/RMSE/MAPE/WMAPE và thông tin run. | Lịch sử từ Gold; dự báo và sai số từ **cùng một run** trong `dss.forecast_run` và `dss.forecast_result` của phiên đang hoạt động. |
| **Cơ hội bán kèm** | Luật mua kèm, support, confidence, lift, số giao dịch hỗ trợ ước tính; tìm sản phẩm và lọc lift. | Đọc `dss.association_run` và toàn bộ luật đã lưu trong `dss.association_rule` của run đang hoạt động. |
| **Nạp dữ liệu & đối soát** | Xem trước CSV, chạy ETL, theo dõi bước xử lý, đối soát trước/sau/chênh lệch, xem lịch sử phiên và quay về dữ liệu nền. | File đang xem trước chưa thay đổi Gold; chỉ phiên hoàn tất mới được kích hoạt. |

### Bộ lọc và biểu đồ ở tab Tổng quan

- **Khoảng thời gian:** Toàn bộ, 1 tuần, 30 ngày, 90 ngày, 1 năm hoặc Tùy chọn.
  Mốc gần nhất là ngày đặt hàng mới nhất **trong Gold**, không phải ngày hiện tại của máy.
- **Đơn vị xu hướng:** 1 tuần → ngày; 30/90 ngày và 1 năm → tuần hoặc tháng;
  Toàn bộ → tháng. Kỳ Tùy chọn chỉ cho chọn đơn vị phù hợp độ dài kỳ.
  Với Tùy chọn, ngày bắt đầu phải trước ngày kết thúc.
- **Địa lý:** thị trường → khu vực → quốc gia. Các lựa chọn khu vực/quốc gia
  chỉ hiện khi cấp cha đã chọn và tự đặt lại khi cấp cha hoặc kỳ thời gian đổi.
  Phạm vi địa lý áp dụng đồng thời cho KPI, xu hướng, ngành hàng, phân khúc,
  cảnh báo và top sản phẩm. Biểu đồ địa lý đi sâu theo cấp đang chọn.
- **Phân khúc:** Consumer, Corporate, Home Office; so sánh doanh thu, lợi nhuận,
  biên lợi nhuận, số khách hàng, số đơn và doanh thu trên mỗi đơn. Không có RFM.
- **Danh mục:** xem ngành hàng và ngành hàng con; nhóm ngành hàng con lỗ cần
  ít nhất 3 đơn trong kỳ. Không bổ sung drill-down xuống SKU.
- **Top sản phẩm:** chọn ngành hàng, xếp theo số lượng hoặc doanh thu,
  và chọn **5–10 sản phẩm** (mặc định 7). Biểu đồ thanh thể hiện sản phẩm;
  biểu đồ quạt thể hiện tỷ trọng **các ngành hàng** theo cùng kỳ và cùng thước đo.
  Bảng chi tiết top sản phẩm đã được bỏ.
- **Biên lợi nhuận (%)** = `SUM(profit) / SUM(sales) × 100` trong phạm vi đã chọn.
  **Tỷ trọng (share %)** là phần đóng góp của nhóm vào tổng doanh thu hoặc
  số lượng trong cùng phạm vi; hai chỉ số có ý nghĩa khác nhau.

Tab What-If có bộ lọc kỳ riêng cho baseline. Tab Dự báo chỉ chọn **số tháng lịch sử
hiển thị** (12/24/48/toàn bộ); dự báo luôn theo tháng và hiển thị 6 tháng tiếp theo.

## 2. Nạp file demo và đổi phiên

File demo dự kiến là `dataset/incremental_orders_2015_q1.csv` gồm **500 dòng,
204 đơn**. Database nền sạch từ dataset hiện tại có **51.290 dòng Gold**.
Các mốc này dùng để kiểm tra demo, không được gắn cứng vào KPI.

1. **Chọn file CSV:** UI kiểm tra cột bắt buộc, đúng 500 dòng, ngày và số hợp lệ,
   `Row ID` không trùng trong file hoặc database nền; hiển thị 5 dòng mẫu,
   khoảng ngày, số đơn, doanh thu và lợi nhuận. Chọn file **chưa chạy ETL**.
2. **Bấm “Xử lý dữ liệu và kích hoạt phiên”:** backend thực hiện
   `Kiểm tra file → Tạo database demo từ nền → Bronze → Silver → Gold → Đối soát
   → Refresh marts → Chạy lại dự báo và bán kèm → Kích hoạt phiên`.
   UI báo bước đang chạy, thành công hoặc lỗi.
3. **Đối soát:** hệ thống so số dòng tăng ở Bronze/Silver/Gold và chênh lệch
   doanh thu, lợi nhuận với file. Khi mọi bước đạt, database demo trở thành
   nguồn đọc của tất cả tab; cache được xóa và UI tải lại. Bảng đối soát
   **Trước / Sau / Chênh lệch** vẫn xem được sau khi tải lại trang.
4. **Upload lần sau:** tạo **database demo mới từ database nền**, không nạp nối
   vào phiên demo trước. Cùng file 500 dòng trên nền sạch cho kết quả
   `51.290 → 51.790` ở mỗi lần chạy, không thành `52.290`.
   Nếu xử lý lỗi, phiên trước vẫn hoạt động.
5. **“Quay về dữ liệu nền”:** mọi tab chuyển lại database nền, xóa cache và
   file xem trước trên UI. Thao tác này **không xóa** database demo hay lịch sử phiên.

Upload đơn thuần, tải lại trang hoặc chỉnh bộ lọc không tự chạy ETL.
Các database demo cũ hiện được giữ lại; UI chưa có chức năng chọn lại phiên cũ
hoặc dọn dẹp database demo tự động. Việc đổi phiên ở đây áp dụng cho **Streamlit UI**;
FastAPI hiện kết nối trực tiếp database cấu hình trong `.env`.

## 3. Dự báo và bán kèm

Pipeline dự báo tổng hợp doanh thu Gold theo **tháng**, so sánh seasonal naïve
(cùng tháng năm trước) với Holt–Winters cộng mùa vụ 12 tháng. Hệ số Holt–Winters
được chọn từ dữ liệu huấn luyện; mô hình được so sánh bằng backtest theo thứ tự
thời gian, riêng cho chân trời 3 và 6 tháng. Kết quả, tham số và sai số được lưu
theo `run_id`. Khoảng sai số trên biểu đồ lấy từ các lần backtest theo từng tháng
dự báo; **chưa phải khoảng tin cậy 95%**. UI chỉ dùng run theo phương pháp mới
và đúng dữ liệu hiện tại. Nếu database nền chỉ có run cũ, UI tạo run mới một lần
rồi đọc kết quả đã lưu ở các lần tải trang sau. File upload cũng chạy cùng
pipeline trước khi kích hoạt phiên demo.

Tab bán kèm khai phá **cặp sản phẩm** xuất hiện trong cùng đơn, tính support,
confidence và lift rồi lưu theo `run_id`. “Số luật phát hiện” lấy từ metadata
của run; “số luật lưu trong DB” là số dòng thực có thể xem. Số giao dịch hỗ trợ
trên UI là **ước tính** vì support được lưu dưới dạng số đã làm tròn.

Mã nguồn chính: [UI](../../src/app/main.py),
[điều phối upload](../../src/app/demo_backend.py),
[dự báo](../../src/dss/predictive/run.py) và
[khai phá luật](../../src/dss/association/run.py).
