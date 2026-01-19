import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Use in-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_index_redirect(client):
    """Test that accessing index redirects to login if not authenticated."""
    response = client.get('/')
    # Should redirect (302) to login page
    assert response.status_code == 302
    assert '/login' in response.location


def test_login_page_loads(client):
    """Test that the login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200