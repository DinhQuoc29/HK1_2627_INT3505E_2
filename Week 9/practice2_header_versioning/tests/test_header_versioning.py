def test_missing_version_header_defaults_to_latest_v2(client):
    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "a@vnu.vn",
    }
    assert response.headers["X-API-Version-Served"] == "2"


def test_explicit_v1_returns_full_name_schema(client):
    response = client.get("/users/1", headers={"X-API-Version": "1"})

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "full_name": "Văn Nguyễn",
        "email": "a@vnu.vn",
    }
    assert response.headers["X-API-Version-Served"] == "1"


def test_explicit_v2_returns_split_name_schema(client):
    response = client.get("/users/2", headers={"X-API-Version": "2"})

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 2,
        "first_name": "Trang",
        "last_name": "Trần",
        "email": "b@vnu.vn",
    }
    assert response.headers["X-API-Version-Served"] == "2"


def test_dated_version_uses_current_schema_and_is_reported(client):
    response = client.get(
        "/users/1", headers={"X-API-Version": "2024-06-20"}
    )

    assert response.status_code == 200
    assert response.get_json()["first_name"] == "Văn"
    assert response.get_json()["last_name"] == "Nguyễn"
    assert response.headers["X-API-Version-Served"] == "2024-06-20"


def test_unsupported_version_returns_400_without_fallback(client):
    response = client.get("/users/1", headers={"X-API-Version": "99"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "unsupported version"}
    assert "X-API-Version-Served" not in response.headers


def test_not_found_keeps_the_selected_version_header(client):
    response = client.get("/users/999", headers={"X-API-Version": "1"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}
    assert response.headers["X-API-Version-Served"] == "1"
