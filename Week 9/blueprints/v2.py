"""Current user representation: first_name and last_name."""

from flask import Blueprint, jsonify, make_response, request, url_for

from .users_data import create_user, get_user


bp = Blueprint("v2", __name__)
_USER_FIELDS = ("first_name", "last_name", "email")


@bp.get("/users/<int:user_id>")
def get_user_v2(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify({"error": "nf"}), 404
    return jsonify(user)


@bp.post("/users")
def create_user_v2():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "error": "validation_error",
            "message": "Request body must be a JSON object",
        }), 400

    invalid_fields = [
        field
        for field in _USER_FIELDS
        if not isinstance(payload.get(field), str) or not payload[field].strip()
    ]
    if invalid_fields:
        return jsonify({
            "error": "validation_error",
            "message": "first_name, last_name, and email are required",
            "fields": invalid_fields,
        }), 400

    user = create_user(*(payload[field].strip() for field in _USER_FIELDS))
    response = make_response(jsonify(user), 201)
    response.headers["Location"] = url_for("v2.get_user_v2", user_id=user["id"])
    return response
