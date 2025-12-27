from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize as globals [cite: 41, 45, 93]
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
jwt = JWTManager()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Use Postgres on USB via Docker [cite: 48, 249]
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://mert:password@db:5432/roverdb"
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Move to .env later [cite: 208]

    db.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)

    return app
