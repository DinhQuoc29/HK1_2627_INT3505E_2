# BÀI TẬP 2: AUDIT PUBLIC API THỰC TẾ
**Môn học:** Phát triển ứng dụng Web / Dịch vụ Web & API  
**Đối tượng khảo sát:** **GitHub REST API (v2022-11-28)**  
**Base URL:** `https://api.github.com`  

---

## I. TỔNG QUAN VỀ GITHUB REST API
GitHub REST API là một trong những chuẩn mực thực tế (industry standard) về thiết kế RESTful API cho hàng triệu lập trình viên trên toàn cầu. API này quản lý toàn bộ hệ sinh thái tài nguyên của GitHub (repositories, issues, pull requests, users, commits, webhooks...).

API tuân thủ các nguyên tắc thiết kế hướng tài nguyên (Resource-Oriented Architecture), hỗ trợ định dạng dữ liệu chuẩn JSON, xác thực qua OAuth2 / Personal Access Token, và cung cấp đầy đủ siêu dữ liệu (metadata) qua HTTP Headers (Rate-limiting, Caching ETag, Pagination Link).

---

## II. BẢNG TỔNG HỢP 5 ENDPOINTS ĐƯỢC AUDIT

| STT | HTTP Method | Endpoint | Chức năng chính | Thành công | RESTful? |
|:---:|:---:|:---|:---|:---:|:---:|
| 1 | `GET` | `/repos/{owner}/{repo}` | Lấy thông tin chi tiết một repository | `200 OK` | **Có** |
| 2 | `POST` | `/repos/{owner}/{repo}/issues` | Tạo mới một Issue trong repository | `201 Created` | **Có** |
| 3 | `PATCH` | `/repos/{owner}/{repo}/issues/{issue_number}` | Cập nhật một phần thuộc tính Issue | `200 OK` | **Có** |
| 4 | `DELETE` | `/repos/{owner}/{repo}/issues/comments/{comment_id}` | Xóa một bình luận trong Issue | `204 No Content` | **Có** |
| 5 | `PUT` | `/user/starred/{owner}/{repo}` | Gắn sao (Star) một repository | `204 No Content` | **Có (Pragmatic)** |

---

## III. AUDIT CHI TIẾT TỪNG ENDPOINT

### 1. Endpoint 1: Lấy thông tin Repository
* **URL:** `GET https://api.github.com/repos/{owner}/{repo}`
* **Ví dụ:** `GET https://api.github.com/repos/octocat/Hello-World`
* **Mục đích:** Truy vấn thông tin chi tiết của một repository cụ thể.

#### Headers:
* **Request Headers:**
  * `Accept: application/vnd.github+json` *(Bắt buộc theo chuẩn định dạng phiên bản của GitHub)*
  * `Authorization: Bearer <token>` *(Tùy chọn cho public repo, bắt buộc cho private repo)*
  * `X-GitHub-Api-Version: 2022-11-28` *(Chỉ định rõ version API)*
  * `If-None-Match: "<ETag>"` *(Hỗ trợ caching có điều kiện)*
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`
  * `ETag: W/"..."` *(Phục vụ conditional request/caching)*
  * `X-RateLimit-Limit: 60` (hoặc 5000 đối với authenticated user)
  * `X-RateLimit-Remaining: 58`
  * `X-RateLimit-Reset: 1726927200`

#### Status Codes:
* `200 OK`: Truy vấn thành công, trả về JSON đại diện cho repository.
* `304 Not Modified`: Nội dung chưa thay đổi (khi client gửi đúng ETag).
* `404 Not Found`: Repository không tồn tại hoặc client không có quyền xem.

#### Đánh giá tính RESTful: **CÓ (Tuân thủ chuẩn REST)**
* **URI:** Sử dụng danh từ phân cấp rõ ràng (`/repos/{owner}/{repo}`), không chứa động từ.
* **HTTP Method:** `GET` an toàn (Safe) và có tính lũy kế (Idempotent), không thay đổi trạng thái hệ thống.
* **HATEOAS:** Trong JSON trả về có sẵn danh sách các URL liên quan (`issues_url`, `commits_url`, `owner.url`), cho phép client điều hướng tiếp theo nguyên lý HATEOAS.

---

### 2. Endpoint 2: Tạo Issue mới
* **URL:** `POST https://api.github.com/repos/{owner}/{repo}/issues`
* **Ví dụ:** `POST https://api.github.com/repos/octocat/Hello-World/issues`
* **Mục đích:** Tạo một tài nguyên Issue mới thuộc về repository đã cho.

#### Headers:
* **Request Headers:**
  * `Accept: application/vnd.github+json`
  * `Content-Type: application/json`
  * `Authorization: Bearer <token>`
  * `X-GitHub-Api-Version: 2022-11-28`
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`
  * `Location: https://api.github.com/repos/octocat/Hello-World/issues/42` *(URI của tài nguyên mới)*

#### Request Body (JSON):
```json
{
  "title": "Bug: Không thể tải ảnh hồ sơ",
  "body": "Gặp lỗi 403 khi tải lên ảnh định dạng .webp",
  "labels": ["bug", "frontend"]
}
```

#### Status Codes:
* `201 Created`: Tạo tài nguyên thành công. Response body trả về object Issue vừa tạo.
* `400 Bad Request`: Payload JSON bị lỗi cú pháp.
* `401 Unauthorized`: Chưa truyền token hoặc token không hợp lệ.
* `403 Forbidden`: Tài khoản không có quyền tạo issue hoặc bị giới hạn rate limit.
* `422 Unprocessable Entity`: Dữ liệu không thỏa mãn validation (ví dụ: thiếu trường `title`).

#### Đánh giá tính RESTful: **CÓ (Tuân thủ chuẩn mực)**
* **HTTP Method:** `POST` đúng ngữ nghĩa là tạo tài nguyên phụ thuộc (sub-resource `/issues`) dưới collection của repository. Không có tính idempotent.
* **Mã phản hồi chuẩn:** Sử dụng đúng mã `201 Created` kèm theo header `Location` trỏ trực tiếp đến tài nguyên vừa được khởi tạo.

---

### 3. Endpoint 3: Cập nhật một Issue
* **URL:** `PATCH https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}`
* **Ví dụ:** `PATCH https://api.github.com/repos/octocat/Hello-World/issues/42`
* **Mục đích:** Thay đổi một hoặc một vài thuộc tính của Issue (tiêu đề, nội dung, trạng thái mở/đóng).

#### Headers:
* **Request Headers:**
  * `Accept: application/vnd.github+json`
  * `Content-Type: application/json`
  * `Authorization: Bearer <token>`
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`

#### Request Body (JSON):
```json
{
  "state": "closed",
  "state_reason": "completed"
}
```

#### Status Codes:
* `200 OK`: Cập nhật thành công, trả về thực thể Issue sau khi sửa đổi.
* `301 Moved Permanently`: Issue thuộc về repo đã được chuyển quyền sở hữu hoặc đổi tên.
* `403 Forbidden`: Thiếu quyền sửa Issue.
* `404 Not Found`: Không tìm thấy issue hoặc repository tương ứng.
* `422 Unprocessable Entity`: Giá trị cập nhật không hợp lệ (ví dụ `state` sai định dạng).

#### Đánh giá tính RESTful: **CÓ (Xuất sắc)**
* **Sử dụng `PATCH` thay vì `PUT`:** REST quy định `PUT` là thay thế toàn bộ (full replacement), còn `PATCH` dùng cho cập nhật cục bộ/một phần (partial update). GitHub phân tách rất chuẩn: client chỉ cần gửi những trường muốn đổi (như `state: "closed"`), các trường khác được giữ nguyên.
* **Trạng thái:** Dùng mã `200 OK` kèm theo representation mới nhất của tài nguyên.

---

### 4. Endpoint 4: Xóa bình luận của Issue
* **URL:** `DELETE https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}`
* **Ví dụ:** `DELETE https://api.github.com/repos/octocat/Hello-World/issues/comments/123456789`
* **Mục đích:** Xóa vĩnh viễn một bình luận cụ thể theo định danh `comment_id`.

#### Headers:
* **Request Headers:**
  * `Accept: application/vnd.github+json`
  * `Authorization: Bearer <token>`
* **Response Headers:**
  * `X-RateLimit-Remaining: ...`
  * Không có `Content-Type` do không trả về body.

#### Status Codes:
* `204 No Content`: Xóa thành công, server không gửi kèm nội dung trả về trong response body.
* `403 Forbidden`: Người dùng không có quyền xóa comment của người khác.
* `404 Not Found`: Comment ID không tồn tại trên hệ thống.

#### Đánh giá tính RESTful: **CÓ (Tuân thủ chuẩn REST)**
* **HTTP Method:** `DELETE` có tính Idempotent (thao tác xóa cùng 1 ID nhiều lần đưa hệ thống về cùng trạng thái).
* **Status Code:** `204 No Content` là mã trạng thái chuẩn xác nhất cho thao tác DELETE thành công không cần trả về payload.
* **Định tuyến:** Định tuyến trực tiếp tới tài nguyên danh từ cụ thể (`/comments/{comment_id}`).

---

### 5. Endpoint 5: Đánh dấu sao (Star) Repository
* **URL:** `PUT https://api.github.com/user/starred/{owner}/{repo}`
* **Ví dụ:** `PUT https://api.github.com/user/starred/octocat/Hello-World`
* **Mục đích:** Người dùng hiện tại gắn sao (Star) cho repository chỉ định.
* *(Ghi chú đối ứng: `DELETE /user/starred/{owner}/{repo}` dùng để Unstar; `GET` dùng để kiểm tra đã star hay chưa).*

#### Headers:
* **Request Headers:**
  * `Accept: application/vnd.github+json`
  * `Authorization: Bearer <token>`
  * `Content-Length: 0` *(Request không cần body)*
* **Response Headers:**
  * `X-RateLimit-Limit: 5000`

#### Status Codes:
* `204 No Content`: Thao tác Star thành công (không trả về body).
* `304 Not Modified`: Nếu đã star từ trước.
* `401 Unauthorized`: Chưa xác thực người dùng.
* `404 Not Found`: Repo cần star không tồn tại.

#### Đánh giá tính RESTful: **CÓ (Pragmatic REST)**
* **Tại sao là RESTful?**
  * Hành động "Star" thay vì thiết kế theo kiểu RPC (`POST /repos/{owner}/{repo}/star`) được chuyển đổi thành **tài nguyên liên kết quan hệ (Relationship Resource)**: `starred`.
  * Thao tác gán quan hệ `PUT /user/starred/{owner}/{repo}` mang tính **Idempotent**: Dù client có gửi request PUT 1 lần hay 10 lần thì repository đó vẫn ở trạng thái "đã được gắn sao".
  * Để hủy star, GitHub dùng `DELETE /user/starred/{owner}/{repo}` rất nhất quán và trực quan theo triết lý CRUD trên quan hệ.
* **Điểm lưu ý:** Việc dùng `PUT` mà không gửi payload body là biến thể thiết thực (pragmatic) để mô hình hóa trạng thái bật/tắt (toggle) của quan hệ giữa 2 tài nguyên mà không cần tạo bảng trung gian phức tạp ở tầng URI.

---

## IV. ĐÁNH GIÁ TỔNG QUAN TÍNH RESTFUL CỦA GITHUB API

Khi đối chiếu với **Mô hình Trưởng thành Richardson (Richardson Maturity Model - RMM)**:

1. **Level 0 (The Swamp of POX):** GitHub vượt qua hoàn toàn, không dùng một endpoint đơn lẻ để xử lý tất cả như SOAP hay XML-RPC.
2. **Level 1 (Resources):** GitHub tổ chức hệ thống phân cấp tài nguyên dạng danh từ rõ ràng (`/users`, `/repos`, `/issues`, `/pulls`), thể hiện rõ quan hệ sở hữu cha-con (`/repos/{owner}/{repo}/issues`).
3. **Level 2 (HTTP Verbs & Status Codes):** GitHub tuân thủ rất nghiêm ngặt:
   * Sử dụng đúng các động từ: `GET` (đọc, an toàn), `POST` (tạo mới, non-idempotent), `PUT` (thay thế / đặt trạng thái, idempotent), `PATCH` (sửa một phần), `DELETE` (xóa).
   * Phân biệt rõ các status codes chuẩn: `200`, `201`, `204`, `304`, `400`, `401`, `403`, `404`, `422`.
4. **Level 3 (Hypermedia Controls - HATEOAS):** 
   * GitHub đạt mức độ cao của Level 3: Trong mỗi JSON response đều trả về các URL liên quan (ví dụ trường `comments_url`, `events_url`, `html_url`).
   * Phân trang (Pagination) sử dụng chuẩn `Link` Header theo RFC 5988 (`rel="next"`, `rel="prev"`, `rel="first"`, `rel="last"`), giúp client không cần tự tính toán offset/page URL.

### Kết luận:
GitHub REST API là một minh chứng tiêu biểu cho **RESTful API chuẩn công nghiệp**. API vừa đảm bảo các nguyên lý cốt lõi của REST (Stateless, Resource-based, Uniform Interface, HATEOAS), vừa có những tinh chỉnh thực tế (Pragmatic REST) để tối ưu hiệu năng và trải nghiệm lập trình viên (Developer Experience - DX).
