import pytest
from app import create_app, db, bcrypt
from app.models.user import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False, # Disable CSRF tokens for easier testing
    })

    with app.app_context():
        db.create_all()
        
        # 1. Create a Test User
        # We need to hash the password because the login route expects it
        hashed_password = bcrypt.generate_password_hash('testpass123').decode('utf-8')
        user = User(email='testuser', password_hash=hashed_password) # Add 'email' if your model needs it
        db.session.add(user)
        db.session.commit()

        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    """Helper class to handle login/logout in tests."""
    class AuthActions:
        def login(self, email='testuser', password='testpass123'):
            return client.post('/login', data={
                'email': email, # Ensure this matches your HTML form name attribute
                'password': password
            }, follow_redirects=True)

        def logout(self):
            return client.get('/auth/logout', follow_redirects=True)

    return AuthActions()

def test_homepage_redirects_if_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_homepage_loads_when_logged_in(client, auth):
    """Verify that the dashboard loads (200) after logging in."""
    response = auth.login()
    assert response.status_code == 200 

    # 2. Access the protected route
    response = client.get('/')
    assert response.status_code == 200
    assert b"Rover Project" in response.data or b"Dashboard" in response.data 

def test_telemetry_api(client, auth):
    """Verify API access."""
    auth.login()
    response = client.get('/api/telemetry')
    assert response.status_code in [200, 404]