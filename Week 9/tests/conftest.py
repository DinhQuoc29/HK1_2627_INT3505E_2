import pytest

from app import create_app
from blueprints import users_data


@pytest.fixture(autouse=True)
def restore_user_store():
    snapshot = users_data.snapshot_users()
    yield
    users_data.restore_users(snapshot)


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as test_client:
        yield test_client
