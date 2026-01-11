import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Initialize the db object here so it can be imported by models
db = SQLAlchemy()
socketio = SocketIO(manage_session=False)

def create_app():
    load_dotenv()
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Bind extensions to this app
    db.init_app(app)
    
    # ADD THIS LINE:
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    with app.app_context():
        from . import models 
    
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # AND IMPORT YOUR EVENTS SO THEY REGISTER
    from . import websocket 
    return app