# Hệ thống chỉ số đo lường hiệu quả kinh doanh (KPIs)

Hệ thống chuẩn hóa 12 chỉ số đo lường hiệu quả kinh doanh, được chia thành ba nhóm: **Tài chính, Sản phẩm và Khách hàng**. Các chỉ số được định nghĩa thống nhất về công thức tính toán và ý nghĩa quản trị nhằm đảm bảo tính nhất quán trong quá trình phân tích dữ liệu và xây dựng các báo cáo hỗ trợ ra quyết định.

## 1. Nhóm chỉ số tài chính

| STT | Tên chỉ số | Ký hiệu | Công thức xác định | Phân loại và ý nghĩa quản trị |
|---|---|---|---|---|
| 1 | Tổng doanh thu | S | `SUM(sales)` | Additive. Phản ánh tổng quy mô doanh số thuần. |
| 2 | Tổng lợi nhuận | P | `SUM(profit)` | Additive. Đo lường hiệu quả sinh lời thực tế sau chi phí. |
| 3 | Biên lợi nhuận | M | `SUM(profit) / SUM(sales) × 100%` | Non-additive. Đánh giá tỷ suất sinh lời trên doanh thu. |
| 4 | Chiết khấu bình quân | D̄ | `AVG(discount) × 100%` | Semi-additive. Giám sát mức độ giảm giá trung bình. |
| 5 | Giá trị đơn hàng trung bình (AOV) | AOV | `SUM(sales) / COUNT(DISTINCT order_id)` | Non-additive. Đo lường quy mô chi tiêu bình quân trên mỗi đơn hàng (504,99 USD). |
| 6 | Tăng trưởng doanh thu tháng (MoM) | g_MoM | `((S_t - S_(t-1)) / S_(t-1)) × 100%` | Non-additive. Theo dõi động lượng tăng trưởng doanh thu giữa hai tháng liên tiếp. |

## 2. Nhóm chỉ số sản phẩm

| STT | Tên chỉ số | Ký hiệu | Công thức xác định | Phân loại và ý nghĩa quản trị |
|---|---|---|---|---|
| 7 | Sản lượng tiêu thụ | Q | `SUM(quantity)` | Additive. Tổng số đơn vị hàng hóa được tiêu thụ (178.312 đơn vị). |
| 8 | Tỷ trọng doanh thu tích lũy Pareto | P_cum(k) | `(SUM(Sales của k sản phẩm đứng đầu) / SUM(Sales toàn bộ sản phẩm)) × 100%` | Non-additive. Xác định nhóm sản phẩm đóng góp phần lớn doanh thu, hỗ trợ ưu tiên quản lý danh mục. |
| 9 | Độ nâng kết hợp (Lift) | Lift(A → B) | `P(A ∩ B) / (P(A) × P(B))` | Đo lường mức độ liên kết giữa hai sản phẩm trong hành vi mua kèm, phục vụ đề xuất bán chéo (Cross-selling). |

## 3. Nhóm chỉ số khách hàng

| STT | Tên chỉ số | Ký hiệu | Công thức xác định | Phân loại và ý nghĩa quản trị |
|---|---|---|---|---|
| 10 | Độ mới giao dịch (Recency) | R | `Reference Date - MAX(order_date)` | Số ngày kể từ lần mua hàng gần nhất của khách hàng tính đến mốc tham chiếu. |
| 11 | Tần suất mua (Frequency) | F | `COUNT(DISTINCT order_id)` | Tổng số đơn hàng độc lập mà một khách hàng đã thực hiện. |
| 12 | Giá trị chi tiêu (Monetary) | M_cust | `SUM(sales)` | Tổng giá trị doanh thu mà khách hàng đóng góp trong toàn bộ vòng đời. |

## 4. Quy ước phân loại độ đo

Các chỉ số được phân loại theo khả năng tổng hợp khi thực hiện các phép phân tích đa chiều (OLAP):

- **Additive:** Có thể cộng trực tiếp qua tất cả các chiều phân tích. Ví dụ: Tổng doanh thu, tổng lợi nhuận và sản lượng tiêu thụ.
- **Semi-additive:** Chỉ có thể tổng hợp qua một số chiều nhất định; cần xác định phương pháp tổng hợp phù hợp. Ví dụ: Chiết khấu bình quân.
- **Non-additive:** Không thể cộng trực tiếp các giá trị đã tổng hợp; cần tính toán lại từ các thành phần cơ sở. Ví dụ: Biên lợi nhuận, AOV và tỷ lệ tăng trưởng.

## 5. Lưu ý triển khai

1. Các chỉ số tỷ lệ như Biên lợi nhuận, AOV và MoM phải được tính lại tại cấp độ dữ liệu đang phân tích, không lấy trung bình cộng các tỷ lệ đã tổng hợp ở cấp thấp hơn.
2. AOV được tính trên số lượng đơn hàng phân biệt (`order_id`), không phải số dòng giao dịch.
3. Chiết khấu bình quân sử dụng trung bình cộng trên các dòng giao dịch. Nếu cần phản ánh mức chiết khấu có trọng số, phải định nghĩa một KPI riêng.
4. Pareto cần sắp xếp sản phẩm theo doanh thu hoặc lợi nhuận giảm dần trước khi tính tỷ trọng tích lũy.
5. Lift lớn hơn 1 thể hiện mối liên kết mua kèm dương; bằng 1 thể hiện độc lập thống kê; nhỏ hơn 1 thể hiện mối liên kết âm.
6. Recency cần sử dụng một mốc tham chiếu (`Reference Date`) thống nhất trong mỗi lần phân tích.
7. Frequency và Monetary được tính theo từng khách hàng, trong khi Recency phản ánh khoảng thời gian từ lần mua gần nhất đến mốc tham chiếu.