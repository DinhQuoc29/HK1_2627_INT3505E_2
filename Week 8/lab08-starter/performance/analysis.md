# Lab 4 — Phân tích kết quả đo thực tế

## Thiết lập

Đo ngày 16/11/2026 trên máy local với Locust 2.47.0, Flask development server và SQLite. Các kịch bản chạy tuần tự trên cùng máy, dùng cùng locustfile với wait time 1–3 giây. p95 và RPS lấy từ dòng Aggregated cuối của Locust.

| Kịch bản | Users | Spawn rate | Thời lượng | Requests | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 2/s | 30s | 139 | 9 | 0.00% | 4.79 |
| B | 50 | 5/s | 60s | 1,378 | 12 | 0.07% | 23.20 |
| C | 200 | 50/s | 30s | 2,888 | 62 | 0.14% | 97.88 |

## Nhận xét

1. **p95 cao nhất là kịch bản C: 62 ms**, so với 9 ms ở A và 12 ms ở B. Khi tăng lên 200 users, độ trễ đuôi tăng rõ rệt; mức cao nhất quan sát được cũng tăng từ 16 ms ở A lên 223 ms ở C. Kết quả phù hợp với việc tăng tranh chấp tài nguyên và lịch chạy request, nhưng phép đo này không cô lập được nguyên nhân cụ thể.

2. **Lỗi được ghi nhận nằm ở GET /books?year={year}.** A có 0/23 lỗi tìm kiếm năm; B có 1/173 (0.58%); C có 4/438 (0.91%). Toàn kịch bản tương ứng 0/139, 1/1,378 (0.07%) và 4/2,888 (0.14%). Mã gọi response.failure() ngẫu nhiên với xác suất 1% sau khi request tìm kiếm trả HTTP 200. Đây là lỗi tổng hợp do Locust đánh dấu phía client để mô phỏng lỗi; Flask không trả HTTP 500. Số mẫu tìm kiếm ít ở A và B nên tỷ lệ đo được dao động quanh 1%, và A không nhất thiết phải có lỗi.

3. Với ngưỡng giả định p95 < 300 ms, **cả A, B và C đều đạt trong lần đo này** (cao nhất là 62 ms). Đây không phải bằng chứng cho SLO production: API chạy bằng Flask development server và SQLite trên cùng máy tạo tải, thời gian đo ngắn, và tải chỉ đại diện cho task mix của bài lab.

4. **Bonus — pool giới hạn 5 connections:** nếu SQLAlchemy dùng pool_size=5 và max_overflow=0 thì tối đa 5 request cùng lúc mượn connection DB; request khác phải chờ connection được trả về. Khi chờ quá pool_timeout, SQLAlchemy có thể ném TimeoutError; nếu ứng dụng không xử lý exception đó, request có thể thành HTTP 500. Với SQLite, tranh chấp ghi còn có thể làm tăng latency hoặc gây lỗi khóa DB. 200 Locust users không đồng nghĩa 200 thao tác DB đồng thời vì mỗi user chỉ gửi một request mỗi lần rồi chờ 1–3 giây. Để xác nhận, khởi động API với SQLALCHEMY_ENGINE_OPTIONS gồm pool_size=5, max_overflow=0 và pool_timeout cố định; chạy lại kịch bản C, so sánh p95, RPS và failures với baseline, rồi đối chiếu lỗi HTTP/server log. Tách riêng HTTP 500 thật khỏi lỗi tổng hợp do response.failure().

References: official [SQLAlchemy QueuePool documentation](https://docs.sqlalchemy.org/en/21/core/pooling.html) and [Flask-SQLAlchemy configuration](https://flask-sqlalchemy.palletsprojects.com/en/stable/config/).

## Cách chạy lại

Khởi động API ở terminal thứ nhất bằng python -m app --port 5000. Ở terminal thứ hai, chạy ba lệnh Locust A, B, C trong README; các file HTML nằm trong reports/.
