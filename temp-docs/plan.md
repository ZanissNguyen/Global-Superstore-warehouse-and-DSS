Giai đoạn: Bronze + Silver	Thành viên	bắt đầu	kết thúc	bắt đầu	kết thúc
- Viết bronze layer: đinh nghĩa các tiêu chí kiểm tra dữ liệu	Thành Phát	17/10	23/10	2/11	6/11
- Viết bronze layer: nghiên cứu về flow upload thêm dữ liệu					
- Có thể là có một bảng audit lại file csv ai upload? ai chạy script? script có báo lỗi không?					
- Lấy file 51k record là góc, file 10k record là dữ liệu realtime để test upload?					
- Tìm hiểu và silver layer					
- Phân tích nghiệp vụ, xác định KPI.	Tiến Nhất				
- Vẽ star schema, xác định grain, fact/dimension.					
- Tạo database, DDL (mức init)					
- Học Power BI (không rõ cần không) ít nhất là biết dùng với file csv, excel, code trong powerBI	Đức Phát				
- Build/ thiết kế giao diện khung, với mockdata					
- Phác thảo báo cáo					
Giai đôạn: Golden + DSS		24/10	30/10	6/11	10/11
- Lên ý tưởng thiết kế giao diện cho DSS	Tiến Nhất				
- Phân tích DSS cho hệ thống					
- Viết các câu truy vấn để hiện thực OLAP	Đức Phát				
	Thành Phát				
Giai đoạn: Trực quan hóa + báo cáo		31/10	6/11	10/11	14/11
- Viết hàm backend? tích hợp với frontend/ powerBI	Tiến Nhất				
	Đức Phát				
- Làm slide	Thành Phát				
- Kiểm thử DSS?	Thành Phát				


## 
Mục tiêu	Scope	Comment
Phân tích yêu cầu nghiệp vụ và xác định bài toán cần giải quyết.	System	Phân tích với dataset e-commerce có gì? làm được gì? trả lời những câu hỏi nghiệp vụ nào
Thiết kế kho dữ liệu theo mô hình đa chiều (star schema / snowflake schema), bao gồm cả quy trình ETL.		Đây là toàn bộ pipeline của bài mình
Hiện thực hệ thống hoàn chỉnh với backend (cơ sở dữ liệu, ETL, OLAP) và frontend (dashboard / giao diện truy vấn). 	Application	backend: có thể tạm demo với local file -> cần thử với docker/ postgres riel
Phát triển một thành phần hệ hỗ trợ quyết định (DSS) dựa trên kho dữ liệu đã xây dựng.		frontend: dùng powerBI hoặc viết frontend webapp chỉ --> report + dss demo
Đánh giá kết quả, phân tích hạn chế và đề xuất hướng phát triển.	DSS	DSS là làm gì? đề xuất hướng giải quyết khi có một kết quả report 
Trình bày kết quả trước lớp hoặc qua video.		DSS có thể đơn giản là áp một công thức cung cầu, tính lợi nhuận, highlight các product, order đáng lưu tâm
	Report	thành viên làm phần nào viết phần đó
	Slide	có thể xong report -> nén cho notebook?


##

Kiến trúc Medialion		
Layer	Tên	Mô tả
Bronze	Raw data layer	Lưu bản sao dữ liệu nguồn, giữ nguyên giá trị gốc, ghi nhận nguồn và thời điểm nạp.
SIlver	Cleaned & conformed data	Chuẩn hóa kiểu dữ liệu, xử lý NULL, kiểm tra trùng lặp, chuẩn hóa khóa và kiểm tra tính nhất quán giữa Orders, Returns, People.
Gold	Dimensional Data Warehouse	Star schema, fact/dimension tables, bảng tổng hợp phục vụ OLAP và dashboard.
Power BI/ frontend		DSS
Dashboard, slice, dice, drill-down, roll-up.		Phát hiện vấn đề, xếp hạng ưu tiên, mô phỏng quyết định.

##
Sản phẩm	Trạng thái
Báo cáo	FALSE
Mã nguồn	FALSE
Script demo	FALSE
Slide	FALSE
Link drive nếu không báo cáo trên lớp	FALSE