# KẾ HOẠCH & BỐ CỤC SLIDE THUYẾT TRÌNH CO4031 (PRESENTATION SLIDES)

> **Môn học:** Kho dữ liệu và Hệ hỗ trợ Quyết định (CO4031) - HK261  
> **Thời lượng thuyết trình:** 15 phút trình bày + 5 phút Q&A  
> **Người thực hiện:** Thành Phát (Lead Designer), Tiến Nhất, Đức Phát  
> **Quy định bắt buộc:** Tất cả 3 thành viên đều phải xuất hiện và trình bày phần của mình!

---

## PHÂN CHIA THUYẾT TRÌNH GIỮA CÁC THÀNH VIÊN (15 PHÚT)

| Phần | Người trình bày | Nội dung chính | Thời lượng dự kiến |
|:---:|:---:|---|:---:|
| **Phần 1: Giới thiệu & DW Design** | **Tiến Nhất** | - Đặt vấn đề, bối cảnh Global Superstore, KPIs cốt lõi.<br>- Kiến trúc Medallion & Thiết kế Star Schema (Grain, Fact, Dimensions). | 5 phút |
| **Phần 2: ETL Pipeline & OLAP** | **Thành Phát** | - Quy trình ETL Bronze -> Silver -> Gold (Audit, Dedup, Data Quality).<br>- Nạp gia tăng (Incremental Load).<br>- Demo các câu truy vấn OLAP (Roll-up, Drill-down, Slice/Dice, Pivot). | 5 phút |
| **Phần 3: DSS Engine & Demo UI** | **Đức Phát** | - Khung lý thuyết DSS & Mô hình Simon.<br>- Mô phỏng What-if Discount & Profit, Sales Forecasting, Market Basket.<br>- Demo giao diện tương tác DSS Web App & Dashboard Power BI.<br>- Kết luận & Hướng phát triển. | 5 phút |

---

## CHI TIẾT CẤU TRÚC 20 SLIDES

1. **Slide 1: Trang tiêu đề:** Tên đề tài, Trường/Khoa, Tên GVHD, Danh sách 3 thành viên kèm vai trò.
2. **Slide 2: Bối cảnh doanh nghiệp & Bài toán kinh doanh:** Quy mô Global Superstore (51k đơn hàng, 147 quốc gia), bài toán thâm hụt biên lợi nhuận do chiết khấu.
3. **Slide 3: Bộ chỉ số KPI & Câu hỏi nghiệp vụ:** 15+ KPIs cốt lõi phân bố theo 3 nhóm (Sales, Product, Customer).
4. **Slide 4: Kiến trúc hệ thống tổng thể:** Sơ đồ phân tầng Medallion + DSS Engine + Power BI / Web App.
5. **Slide 5: Thiết kế Mô hình hình sao (Star Schema):** Sơ đồ quan hệ FactSales trung tâm nối với 5 Dimension tables bằng Surrogate Keys.
6. **Slide 6: Phân tích Grain & Chiến lược xử lý dữ liệu:** Grain 1 dòng đơn hàng, giải pháp xử lý 80.5% NULL Postal Code, chuẩn hóa ngày tháng hỗn hợp.
7. **Slide 7: Tầng Bronze (Raw Ingestion):** Cơ chế tính mã băm SHA-256, bảng lưu vết `bronze.ingestion`, khả năng chống trùng lặp dữ liệu (Idempotency).
8. **Slide 8: Tầng Silver (Cleaned & Standardized):** Chuẩn hóa kiểu dữ liệu, các ràng buộc chất lượng (Data Quality Rules), tích hợp cờ hoàn trả (`is_returned`) và Quản lý vùng (`regional_manager`).
9. **Slide 9: Tầng Gold & Nạp gia tăng (Incremental Loading):** Quy trình nạp các bảng Chiều và Fact, kết quả kiểm thử nạp bổ sung file 10,000 dòng.
10. **Slide 10: Khai thác OLAP Đa chiều (Phần 1):** Demo trực quan thao tác Roll-up (Thời gian/Địa lý) và Drill-down (Khoan sâu danh mục sản phẩm).
11. **Slide 11: Khai thác OLAP Đa chiều (Phần 2):** Demo thao tác Slice & Dice, Pivot 4 quý, và Window Functions (MoM Growth Rate, DENSE_RANK).
12. **Slide 12: Tối ưu hóa truy vấn với Data Marts (Materialized Views):** Hiệu năng truy vấn giảm từ hàng trăm ms xuống dưới 50ms nhờ Materialized Views và Indexing.
13. **Slide 13: Khung lý thuyết Hệ hỗ trợ Quyết định (DSS):** Chu trình 4 giai đoạn của Herbert Simon (Intelligence -> Design -> Choice -> Implementation) tích hợp trong hệ thống.
14. **Slide 14: Mô hình Mô phỏng What-If (Discount & Profit):** Công thức độ co giãn cầu theo giá $e$, mô phỏng điều chỉnh chiết khấu và thuật toán khuyến nghị tự động.
15. **Slide 15: Mô hình Dự báo Doanh số Chuỗi Thời gian (Sales Forecasting):** Thuật toán Exponential Smoothing (Holt-Winters), độ chính xác MAE/RMSE/MAPE, dự báo 6 tháng tới kèm dải tin cậy 95%.
16. **Slide 16: Khai phá Giỏ hàng & Bán chéo (Market Basket Analysis):** Thuật toán Apriori/FP-Growth, các luật kết hợp có Lift > 1.2, ứng dụng tạo combo khuyến mãi.
17. **Slide 17: Demo Giao diện Tương tác DSS (Streamlit App):** Hình ảnh thực tế của ứng dụng web DSS, thao tác thanh trượt What-if và kết quả phản hồi tức thời.
18. **Slide 18: Demo Báo cáo Đa chiều Power BI (.pbix):** 3 trang Dashboard nghiệp vụ chuẩn doanh nghiệp với Slicers và Drill-through.
19. **Slide 19: Đánh giá kết quả & Hạn chế:** Đối chiếu chuẩn đầu ra học phần, những điểm đã làm tốt và các điểm còn hạn chế.
20. **Slide 20: Lời cảm ơn & Phiên Q&A:** Thông tin liên hệ nhóm, mở đầu phiên hỏi đáp với Giảng viên.
