"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. test_response_extra_field_blocked: Validate a Book response using JSON Schema;
       add an unknown field (password_hash) in a fixture and assert ValidationError.

Do not depend on test execution order. Fixtures: client, app, sample_book, book_with_extra_field.
"""
from jsonschema import ValidationError, validate
import pytest
from tools import get_book_schema


# Test A: GET /books khi CSDL rỗng trả về mảng rỗng (không phải null)
def test_get_books_empty_db(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert isinstance(data, list)
    assert data == []


# Test B: GET /books/<id> với id không tồn tại trả về 404 + JSON chứa "code": "NOT_FOUND"
def test_get_book_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == "NOT_FOUND"


# Test C: POST /books thiếu title trả về 400 + trong errors có field "title"
def test_create_book_missing_title(client):
    response = client.post("/books", json={"author": "J.K. Rowling"})
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    fields_with_errors = [err["field"] for err in data["errors"]]
    assert "title" in fields_with_errors


# Test D: Xoá rồi GET cùng id — phải trả về 404
def test_delete_then_get_book(client):
    post_resp = client.post(
        "/books",
        json={"title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    )
    assert post_resp.status_code == 201
    book_id = post_resp.get_json()["id"]

    delete_resp = client.delete(f"/books/{book_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


# BONUS: Thêm test test_response_extra_field_blocked dùng jsonschema
# chứng minh backend không lộ password_hash (giả lập bằng cách add field lạ trong fixture).
def test_response_extra_field_blocked(client, sample_book, book_with_extra_field):
    schema = get_book_schema()
    if schema.get("properties", {}).get("year", {}).get("type") == "string":
        schema["properties"]["year"]["type"] = "integer"

    for prop, prop_schema in schema.get("properties", {}).items():
        if prop_schema.get("nullable") and isinstance(prop_schema.get("type"), str):
            prop_schema["type"] = [prop_schema["type"], "null"]

    # 1. Chứng minh backend không lộ password_hash và khớp schema (additionalProperties: false)
    real_response = client.get(f"/books/{sample_book}")
    assert real_response.status_code == 200
    book_data = real_response.get_json()
    assert "password_hash" not in book_data
    validate(instance=book_data, schema=schema)

    # 2. Giả lập bị lộ password_hash thông qua fixture -> schema phải chặn và ném ValidationError
    assert "password_hash" in book_with_extra_field
    with pytest.raises(ValidationError):
        validate(instance=book_with_extra_field, schema=schema)
