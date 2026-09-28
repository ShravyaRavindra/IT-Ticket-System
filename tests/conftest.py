import pytest

from app import create_app
from init_db import initialize_database


@pytest.fixture
def app(tmp_path):
    test_db = tmp_path / "test_tickets.db"

    app = create_app()

    app.config["TESTING"] = True
    app.config["DATABASE"] = test_db

    with app.app_context():
        initialize_database()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()