# Đánh Giá Thiết Kế Kiến Trúc Spotify Web API

Tài liệu này phân tích và đánh giá hai tiêu chí cốt lõi trong tiêu chuẩn thiết kế RESTful API của **Spotify Web API**:
1. **Versioning & Deprecation Policy**
2. **Naming Conventions & Resource Structuring**

---

## 1. Versioning & Deprecation

### 1.1. Chiến lược Định danh Phiên bản (URI Versioning)
* **URI Prefix tĩnh (`/v1`):** Mọi endpoint công khai của Spotify đều tuân theo chuẩn gốc:
  ```text
  https://api.spotify.com/v1/{resource}
  ```
* **Backwards-Compatible Evolution:** 
  * Thay vì phát hành phiên bản lớn `/v2`, Spotify duy trì tiền tố `/v1` xuyên suốt nhiều năm bằng cách chọn phương pháp tiến hóa tương thích ngược.
  * Các tính năng mới được tích hợp dưới dạng endpoint mới hoặc các trường dữ liệu tùy chọn (`optional fields`) trong response body, hạn chế tối đa việc gây đứt gãy hệ thống hiện hành.

### 1.2. Chính sách Ngừng Hỗ Trợ (Deprecation & Sunset Policy)
* **Lộ trình thông báo trước (Advance Notice):** Spotify áp dụng thời gian thông báo (thường từ **3 đến 6 tháng**) trước khi tắt hoàn toàn một endpoint hoặc gỡ bỏ các trường quan trọng.
* **Kênh truyền thông kỹ thuật:**
  * Thông báo chính thức qua **Developer Changelog** và Dashboard của nhà phát triển.
  * Gửi cảnh báo tự động qua email quản trị viên đối với các ứng dụng có phát sinh lưu lượng truy cập vào endpoint nằm trong danh sách loại bỏ.
* **Gắn thẻ tài liệu & Sunsetting:**
  * Các endpoint lỗi thời được gắn nhãn `[Deprecated]` rõ ràng trên tài liệu Open API / API Reference, kèm theo gợi ý chuyển đổi sang endpoint thay thế.
  * Ngắt quyền truy cập từng phần (ví dụ: các đợt siết chặt quyền truy cập vào endpoint *Recommendations*, *Audio Analysis* gần đây đối với tài khoản chưa xác minh).

---

## 2. Naming Conventions & URL Structure

Spotify áp dụng các quy chuẩn đặt tên nhất quán và chặt chẽ, tạo điều kiện thuận lợi cho việc phát triển SDK và tự động hóa mã nguồn (code generation).

| Thành phần | Quy tắc chuẩn | Ví dụ minh họa | Đánh giá kỹ thuật |
| :--- | :--- | :--- | :--- |
| **Path / Resource** | `kebab-case` & `lowercase` | `/v1/browse/new-releases`<br>`/v1/browse/categories` | Chuẩn hóa chữ thường giúp tránh sự cố định tuyến (routing) phân biệt hoa-thường trên các web server khác nhau. Dấu gạch nối giúp dễ đọc. |
| **Collections (Tập hợp)** | Danh từ số nhiều (`plurals`) | `/v1/tracks/{id}`<br>`/v1/albums/{id}`<br>`/v1/artists/{id}` | Phản ánh cấu trúc tài nguyên chuẩn REST: một đối tượng cụ thể (id) luôn trực thuộc một tập hợp số nhiều. |
| **Sub-resources (Phân cấp)** | Cấu trúc phân cấp chuẩn | `/v1/albums/{id}/tracks`<br>`/v1/artists/{id}/top-tracks` | Biểu diễn mối quan hệ quan hệ cha-con (1-N) rõ ràng trong cây tài nguyên. |
| **Query Parameters** | `snake_case` | `?include_groups=album,single`<br>`?target_danceability=0.8`<br>`?limit=20&offset=0` | Nhất quán tuyệt đối với các tham số truy vấn, không pha trộn với `camelCase`. |
| **JSON Fields (Payload)** | `snake_case` | `duration_ms`<br>`release_date`<br>`available_markets` | Thống nhất với quy ước đặt tên của Query Parameters, giúp việc map dữ liệu trong client đồng nhất. |
| **Singleton / Alias** | Đại từ định danh ngắn | `/v1/me`<br>`/v1/me/playlists` | Dùng alias `/me` đại diện trực tiếp cho tài nguyên của người dùng hiện hành (được giải mã từ access token), tránh việc phải truyền User ID vào path. |

---
