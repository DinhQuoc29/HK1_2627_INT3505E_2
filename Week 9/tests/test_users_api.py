def test_v1_returns_legacy_full_name_schema_and_sunset_headers(client):
    response = client.get("/api/v1/users/1")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "full_name": "Văn Nguyễn",
        "email": "a@vnu.vn",
    }
    assert response.headers["Sunset"] == "Fri, 01 Jan 2027 00:00:00 GMT"
    assert response.headers["Link"] == (
        '</api/v2/users/1>; rel="successor-version"'
    )


def test_v2_returns_split_name_schema(client):
    response = client.get("/api/v2/users/1")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "a@vnu.vn",
    }


def test_unknown_user_is_not_found_in_both_versions(client):
    for path in ("/api/v1/users/999", "/api/v2/users/999"):
        response = client.get(path)
        assert response.status_code == 404
        assert response.get_json() == {"error": "nf"}


def test_v2_can_create_user_and_v1_does_not_expose_post(client):
    response = client.post(
        "/api/v2/users",
        json={
            "first_name": "Minh",
            "last_name": "Lê",
            "email": "minh@vnu.vn",
        },
    )

    assert response.status_code == 201
    created = response.get_json()
    assert created == {
        "id": 3,
        "first_name": "Minh",
        "last_name": "Lê",
        "email": "minh@vnu.vn",
    }
    assert response.headers["Location"] == "/api/v2/users/3"
    assert client.get(response.headers["Location"]).get_json() == created
    assert client.post("/api/v1/users", json={}).status_code == 404


def test_v2_rejects_incomplete_create_payload(client):
    response = client.post(
        "/api/v2/users",
        json={"first_name": "Minh", "last_name": "Lê"},
    )

    assert response.status_code == 400
    assert response.get_json()["fields"] == ["email"]
