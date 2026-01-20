import pytest
from app import create_app, db


@pytest.fixture(scope='function')
def client():
    """A test client for the app."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": 'sqlite:///:memory:',
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for form testing
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        # Teardown: drop all tables to ensure a clean state for the next test
        with app.app_context():
            db.drop_all()