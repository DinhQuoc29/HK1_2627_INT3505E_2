# Practice 2 — Header Versioning với decorator

Ứng dụng độc lập minh họa versioning qua `X-API-Version`. Cả ba phiên bản dùng chung URL `GET /users/{id}`:

- Không gửi header: dùng phiên bản ổn định mới nhất, hiện là v2.
- `X-API-Version: 1`: trả `full_name`.
- `X-API-Version: 2`: trả `first_name` và `last_name`.
- `X-API-Version: 2024-06-20`: phiên bản ngày, dùng schema hiện tại của v2.
- Version không được hỗ trợ trả HTTP 400, không fallback.

Response hợp lệ có `X-API-Version-Served` để cho biết schema thực tế đã trả.

## Chạy

Từ thư mục `Week 9/practice2_header_versioning`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app
```

API chạy tại `http://127.0.0.1:5000`.

## Thử bằng curl

```powershell
curl.exe -i http://127.0.0.1:5000/users/1
curl.exe -i -H "X-API-Version: 1" http://127.0.0.1:5000/users/1
curl.exe -i -H "X-API-Version: 2024-06-20" http://127.0.0.1:5000/users/1
curl.exe -i -H "X-API-Version: 99" http://127.0.0.1:5000/users/1
```

Mặc định và dated version trả schema v2. Request cuối trả HTTP 400.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
