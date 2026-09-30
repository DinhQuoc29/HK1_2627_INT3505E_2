# Thiết kế Resource cho Blog API

## 1. Xác định Resources trong miền (Domain Resources)

Resources trong miền:

* **Users / Authors (`users`)**: Đại diện cho tài khoản người dùng, tác giả bài viết hoặc độc giả trong hệ thống.
* **Profiles (`profiles`)**: Hồ sơ công khai của người dùng (tiểu sử, avatar, liên kết mạng xã hội), liên kết 1-1 với `User`.
* **Posts (`posts`)**: Các bài viết do tác giả đăng tải, chứa nội dung chính, tiêu đề, ngày đăng và trạng thái bài viết.
* **Comments (`comments`)**: Phản hồi, bình luận của người dùng tương tác dưới một bài viết cụ thể (quan hệ phụ thuộc 1-N với `Post`).
* **Tags (`tags`)**: Nhãn phân loại chủ đề bài viết (quan hệ N-N với `Post`).
* **Follows (`followers` / `following`)**: Mối quan hệ tương tác theo dõi giữa người dùng này với người dùng khác.

---

## 2. Phân loại Collection, Item và Sub-resource

Kiến trúc REST chia các tài nguyên thành 3 cấp độ chính nhằm tối ưu hóa tính phân cấp và mô tả rõ ràng quan hệ ngữ cảnh :

### 2.1 Bảng phân loại tổng quan

| Loại Resource | Ý nghĩa / Định nghĩa | Mẫu URI (Pattern) | Phương thức HTTP & Mục đích |
| :--- | :--- | :--- | :--- |
| **Collection** | Tập hợp danh sách các thực thể độc lập ở cấp gốc. | `/api/v1/posts`<br>`/api/v1/users`<br>`/api/v1/tags` | `GET`: Truy vấn danh sách có phân trang/lọc<br>`POST`: Tạo mới thực thể trong danh sách |
| **Item (Document)** | Một thực thể dữ liệu đơn lẻ được định danh bởi khóa duy nhất (ID hoặc slug). | `/api/v1/posts/{post_id}`<br>`/api/v1/users/{user_id}`<br>`/api/v1/tags/{tag_id}` | `GET`: Đọc chi tiết thực thể<br>`PUT`/`PATCH`: Cập nhật toàn bộ/một phần<br>`DELETE`: Xóa thực thể |
| **Sub-resource (Collection)** | Danh sách các thực thể phụ thuộc hoàn toàn vào ngữ cảnh của một Item cha. | `/api/v1/posts/{post_id}/comments`<br>`/api/v1/posts/{post_id}/tags`<br>`/api/v1/users/{user_id}/followers` | `GET`: Đọc danh sách phụ thuộc<br>`POST`: Thêm thực thể phụ thuộc vào Item cha |
| **Sub-resource (Item)** | Một thực thể đơn lẻ bên trong mối quan hệ phân cấp phụ thuộc. | `/api/v1/posts/{post_id}/comments/{comment_id}`<br>`/api/v1/users/{user_id}/following/{target_user_id}` | `GET`: Xem chi tiết đối tượng con<br>`PUT`/`DELETE`: Thao tác trực tiếp (sửa bình luận, hủy follow) |

---

### 2.2 Chi tiết ánh xạ ngữ cảnh nghiệp vụ

#### A. Nhóm Posts & Comments
* **Collection:** `/api/v1/posts` quản lý toàn bộ các bài đăng trên nền tảng.
* **Item:** `/api/v1/posts/{post_id}` đại diện cho bài viết cụ thể.
* **Sub-resource:** Bình luận không tồn tại độc lập mà gắn liền với vòng đời của bài viết:
  * `/api/v1/posts/{post_id}/comments`: Collection bình luận của bài viết.
  * `/api/v1/posts/{post_id}/comments/{comment_id}`: Item bình luận xác định trong bài viết đó.

#### B. Nhóm Tags (Quan hệ N-N)
* **Global Collection:** `/api/v1/tags` dùng để quản lý từ điển danh mục tag của hệ thống.
* **Sub-resource:** `/api/v1/posts/{post_id}/tags` dùng để gán hoặc lọc các thẻ gắn kèm theo một bài viết cụ thể.

#### C. Nhóm Users & Following (Quan hệ tương tác)
* **Collection & Item:** `/api/v1/users` và `/api/v1/users/{user_id}`.
* **Sub-resource:** Mối quan hệ mạng xã hội theo dõi giữa người dùng:
  * `/api/v1/users/{user_id}/followers`: Danh sách người dùng đang theo dõi `{user_id}`.
  * `/api/v1/users/{user_id}/following`: Danh sách người dùng mà `{user_id}` đang theo dõi.
  * `/api/v1/users/{user_id}/following/{target_user_id}`: Đại diện trạng thái quan hệ follow giữa hai cá nhân (`PUT` để theo dõi, `DELETE` để hủy).