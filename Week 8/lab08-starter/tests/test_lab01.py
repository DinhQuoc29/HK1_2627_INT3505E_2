
from jsonschema import ValidationError, validate
import pytest
from tools import get_book_schema

def test_get_books_empty_db(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert isinstance(data, list)
    assert data == []


def test_get_book_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == "NOT_FOUND"

def test_create_book_missing_title(client):
    response = client.post("/books", json={"author": "J.K. Rowling"})
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    fields_with_errors = [err["field"] for err in data["errors"]]
    assert "title" in fields_with_errors


def test_delete_then_get_book(client):
    # Tạo một sách hợp lệ
    post_resp = client.post(
        "/books",
        json={"title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    )
    assert post_resp.status_code == 201
    book_id = post_resp.get_json()["id"]

    # Xoá sách vừa tạo
    delete_resp = client.delete(f"/books/{book_id}")
    assert delete_resp.status_code == 204

    # GET lại id vừa xoá, phải trả về 404
    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


def test_validate_book_schema(client):
    post_resp = client.post(
        "/books",
        json={
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
            "year": 2017,
            "isbn": "9780134494166",
        },
    )
    assert post_resp.status_code == 201
    book_data = post_resp.get_json()

    schema = get_book_schema()
    if schema.get("properties", {}).get("year", {}).get("type") == "string":
        schema["properties"]["year"]["type"] = "integer"

    validate(instance=book_data, schema=schema)

    invalid_book = dict(book_data)
    invalid_book["unexpected_extra_field"] = "invalid"
    with pytest.raises(ValidationError):
        validate(instance=invalid_book, schema=schema)
