# Security Audit – Social Network API

## 1. Scope

Audit các endpoint:

- `POST /auth/login`
- `POST /auth/refresh`
- `GET /posts/{id}`

Mục tiêu: xác định các điểm có nguy cơ rò rỉ thông tin nhạy cảm, token, dữ liệu cá nhân hoặc dữ liệu nội bộ hệ thống.

## 2. Potential Information Leakage Risks

### 2.1. User Enumeration – Login Endpoint

**Endpoint:** `POST /auth/login`

**Risk:** API trả về thông báo khác nhau khi email không tồn tại và khi mật khẩu sai. Kẻ tấn công có thể sử dụng phản hồi để xác định tài khoản hợp lệ.

**Example:**

- `Email does not exist`
- `Incorrect password`

**Mitigation:**

- Trả về thông báo chung: `Invalid email or password`.
- Giới hạn số lần đăng nhập thất bại.
- Áp dụng rate limiting và giám sát các hành vi đăng nhập bất thường.

### 2.2. Password Leakage Through Logs

**Endpoint:** `POST /auth/login`

**Risk:** Request body chứa mật khẩu có thể bị ghi vào application logs, reverse proxy logs hoặc hệ thống theo dõi lỗi.

**Mitigation:**

- Không ghi log mật khẩu hoặc toàn bộ request body chứa thông tin xác thực.
- Mask các trường nhạy cảm trong logging middleware.
- Giới hạn quyền truy cập log và thời gian lưu trữ.

### 2.3. Access Token and Refresh Token Leakage

**Endpoints:** `POST /auth/login`, `POST /auth/refresh`

**Risk:** Token có thể bị lộ qua log, URL, báo cáo lỗi, công cụ giám sát hoặc lưu trữ phía client không an toàn. Kẻ tấn công có thể sử dụng token bị đánh cắp để mạo danh người dùng.

**Mitigation:**

- Chỉ truyền token qua HTTPS.
- Không đưa token vào URL hoặc log.
- Nếu sử dụng cookie, bật `Secure`, `HttpOnly` và cấu hình `SameSite` phù hợp.
- Giới hạn thời hạn access token và triển khai refresh token rotation, phát hiện tái sử dụng token.

### 2.4. JWT Claims and Signing Information Leakage

**Endpoints:** `POST /auth/refresh`, `GET /posts/{id}`

**Risk:** JWT payload thường chỉ được mã hóa Base64URL, không được mã hóa bí mật. Các claims như email, user ID, role hoặc thông tin nội bộ có thể bị đọc bởi bất kỳ ai sở hữu token. Thông báo lỗi xác minh token cũng có thể làm lộ thông tin triển khai.

**Mitigation:**

- Không đưa mật khẩu, dữ liệu cá nhân nhạy cảm hoặc bí mật vào JWT claims.
- Xác minh chữ ký, thuật toán được cho phép, `exp`, `iss` và `aud`.
- Kiểm tra mục đích sử dụng token để tránh dùng refresh token như access token.
- Không trả về stack trace hoặc chi tiết khóa ký trong API response.

### 2.5. Broken Object-Level Authorization (BOLA / IDOR)

**Endpoint:** `GET /posts/{id}`

**Risk:** Người dùng thay đổi `id` trong request để đọc bài viết riêng tư hoặc nội dung của người dùng khác mà họ không có quyền truy cập.

**Mitigation:**

- Kiểm tra quyền truy cập trên từng bài viết ở phía server.
- Áp dụng chính sách quyền riêng tư như public, followers-only hoặc private.
- Không coi việc biết UUID hoặc ID khó đoán là cơ chế phân quyền.
- Có thể trả về `404 Not Found` cho tài nguyên không tồn tại hoặc không được phép nhìn thấy để giảm khả năng dò tìm.

### 2.6. Sensitive Data Exposure in Post Responses

**Endpoint:** `GET /posts/{id}`

**Risk:** API có thể trả về email, số điện thoại, địa chỉ IP, thông tin moderation hoặc dữ liệu nội bộ của tác giả dù client không cần những trường đó.

**Mitigation:**

- Sử dụng response DTO với danh sách trường được cho phép rõ ràng.
- Chỉ trả về dữ liệu cần thiết cho chức năng đọc bài viết.
- Áp dụng kiểm soát quyền riêng tư và phân loại dữ liệu.
- Không serialize trực tiếp toàn bộ database entity.

### 2.7. Information Disclosure Through Error Messages

**All endpoints**

**Risk:** Error response có thể chứa SQL queries, stack traces, đường dẫn file, tên bảng, phiên bản framework hoặc chi tiết cấu hình nội bộ.

**Mitigation:**

- Chuẩn hóa lỗi theo các mã như `INVALID_CREDENTIALS`, `INVALID_REFRESH_TOKEN` và `INTERNAL_SERVER_ERROR`.
- Trả thông báo ngắn gọn, không chứa thông tin nội bộ.
- Ghi chi tiết kỹ thuật vào log được bảo vệ, liên kết bằng `requestId`.
- Không trả exception message trực tiếp cho client.

### 2.8. Timing and Rate-Limit Side Channels

**Endpoints:** `POST /auth/login`, `POST /auth/refresh`

**Risk:** Khác biệt về thời gian phản hồi hoặc việc thiếu giới hạn request có thể hỗ trợ dò tài khoản, brute-force mật khẩu hoặc thử nhiều refresh token.

**Mitigation:**

- Áp dụng rate limiting theo tài khoản và địa chỉ IP với ngưỡng phù hợp.
- Sử dụng cơ chế xác minh mật khẩu an toàn như Argon2id hoặc bcrypt.
- Theo dõi các mẫu request bất thường và có biện pháp chống tự động hóa.
- Tránh phản hồi tiết lộ trạng thái tài khoản hoặc token.

## 3. Security Requirements Checklist

- [ ] Tất cả endpoint production sử dụng HTTPS.
- [ ] Login không phân biệt email không tồn tại với mật khẩu sai.
- [ ] Password và token không xuất hiện trong log.
- [ ] Access token và refresh token được xác minh đúng mục đích.
- [ ] `GET /posts/{id}` kiểm tra quyền trên từng tài nguyên.
- [ ] Response không chứa dữ liệu cá nhân hoặc dữ liệu nội bộ không cần thiết.
- [ ] Error response không chứa stack trace hoặc thông tin cấu hình.
- [ ] Rate limiting được áp dụng cho endpoint xác thực.
- [ ] Refresh token rotation và thu hồi token được xử lý an toàn.

## 4. Conclusion

Các rủi ro ưu tiên cao là rò rỉ thông tin xác thực, sử dụng token sai mục đích, thiếu kiểm soát quyền truy cập đối với bài viết và trả về dữ liệu nhạy cảm trong response.

Cần triển khai các biện pháp giảm thiểu và kiểm thử bảo mật trước khi đưa API lên production.

**Note:** Đây là đánh giá dựa trên thiết kế API. Cần kiểm tra code thực tế, cấu hình triển khai và log để xác nhận các rủi ro có thực sự tồn tại hay không.
