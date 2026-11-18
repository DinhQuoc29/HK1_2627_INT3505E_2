"""Small in-memory user store shared by API versions."""

from copy import deepcopy
from threading import Lock


USERS = {
    1: {"first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"},
    2: {"first_name": "Trang", "last_name": "Trần", "email": "b@vnu.vn"},
}
_lock = Lock()


def get_user(user_id):
    with _lock:
        user = USERS.get(user_id)
        return {"id": user_id, **user} if user is not None else None


def create_user(first_name, last_name, email):
    with _lock:
        user_id = max(USERS, default=0) + 1
        USERS[user_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
        return {"id": user_id, **USERS[user_id]}


def snapshot_users():
    with _lock:
        return deepcopy(USERS)


def restore_users(snapshot):
    with _lock:
        USERS.clear()
        USERS.update(deepcopy(snapshot))
