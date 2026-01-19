from app.models import User
from app import db, bcrypt


def test_user_login_and_access(client):
    """
    GIVEN a Flask application configured for testing
    WHEN a new user is created and logs in via a POST request
    THEN check that the login is successful and they can access the root page
    """
    # 1. Create a test user directly in the in-memory database
    password_hash = bcrypt.generate_password_hash("testpassword").decode("utf-8")
    new_user = User(username="testuser", password=password_hash)
    with client.application.app_context():
        db.session.add(new_user)
        db.session.commit()

    # 2. Simulate a user logging in with a form POST request
    response = client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)

    # 3. Check that the login was successful and the page has changed
    assert response.status_code == 200
    # A good way to check for successful login is to see if 'Logout' is now visible
    assert b'Logout' in response.data
    assert b'Login' not in response.data