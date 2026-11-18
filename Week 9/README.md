# Week 9 — URI Path Versioning với Flask Blueprint

Project minh họa hai phiên bản API dùng chung một nguồn dữ liệu in-memory:

- `GET /api/v1/users/{id}` trả `id`, `full_name`, `email`.
- `GET /api/v2/users/{id}` trả `id`, `first_name`, `last_name`, `email`.
- `POST /api/v2/users` tạo user mới; v1 không có route POST.
- API v1 có `Sunset` và `Link: rel="successor-version"` response header.

## Chạy API

Từ thư mục `Week 9`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app
```

API lắng nghe tại `http://127.0.0.1:5000`.

## Thử hai schema

Mở terminal khác:

```powershell
curl.exe -i http://127.0.0.1:5000/api/v1/users/1
curl.exe -i http://127.0.0.1:5000/api/v2/users/1
```

V1 trả JSON tương tự:

```json
{"id":1,"full_name":"Văn Nguyễn","email":"a@vnu.vn"}
```

V2 trả JSON tương tự:

```json
{"id":1,"first_name":"Văn","last_name":"Nguyễn","email":"a@vnu.vn"}
```

V1 response còn có `Sunset: Fri, 01 Jan 2027 00:00:00 GMT` và đường dẫn successor trong header `Link`.

## Tạo user ở v2

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/v2/users `
  -H "Content-Type: application/json" `
  -d '{"first_name":"Minh","last_name":"Lê","email":"minh@vnu.vn"}'
```

Endpoint tạo user trả `201 Created` và header `Location` đến resource mới. Dữ liệu nằm trong bộ nhớ và sẽ trở về mẫu ban đầu khi tắt ứng dụng.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

OpenAPI 3 spec nằm tại `openapi.yaml`.
