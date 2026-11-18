"""Legacy user representation: full_name."""

from flask import Blueprint, current_app, jsonify, make_response

from .users_data import get_user


bp = Blueprint("v1", __name__)


def _v1_response(payload, status, user_id):
    response = make_response(jsonify(payload), status)
    response.headers["Sunset"] = current_app.config["V1_SUNSET"]
    response.headers["Link"] = (
        f'</api/v2/users/{user_id}>; rel="successor-version"'
    )
    return response


@bp.get("/users/<int:user_id>")
def get_user_v1(user_id):
    user = get_user(user_id)
    if user is None:
        return _v1_response({"error": "nf"}, 404, user_id)

    return _v1_response(
        {
            "id": user["id"],
            "full_name": f'{user["first_name"]} {user["last_name"]}',
            "email": user["email"],
        },
        200,
        user_id,
    )
