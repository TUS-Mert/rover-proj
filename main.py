from app import create_app, socketio
from init_db import initialize_database

app = create_app()

if __name__ == '__main__':
    # Flask-SocketIO wraps the server to handle both HTTP and WS on the same port
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

    # Load configuration from environment variables with sensible defaults
    HOST = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_RUN_PORT', 5000))
    # FLASK_DEBUG is a string 'True' or 'False' by default
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

    # The `allow_unsafe_werkzeug` flag should be tied to the debug status
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG, allow_unsafe_werkzeug=DEBUG)