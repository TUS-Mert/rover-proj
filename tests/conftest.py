import pytest
from app import create_app, db, bcrypt
from app.models.user import User


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        # Create user
        hashed_password = bcrypt.generate_password_hash("testpass123").decode("utf-8")
        user = User(email="test@example.com", password_hash=hashed_password)
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
    class AuthActions:
        def login(self, email="test@example.com", password="testpass123"):
            return client.post(
                "/login",
                data={"email": email, "password": password},
                follow_redirects=True,
            )

        def logout(self):
            return client.get("/logout", follow_redirects=True)

    return AuthActions()
