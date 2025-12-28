from flask import request
from flask_socketio import emit
from flask_jwt_extended import jwt_required, decode_token
from . import create_app, socketio
from .motion import MotionController

app = create_app()
motion = MotionController()

@socketio.on('connect')
def handle_connect():
    """Secure access check as per Security Design [cite: 195, 197]"""
    token = request.args.get('token')
    try:
        # Validates JWT on handshake [cite: 197]
        decode_token(token)
    except Exception:
        return False # Refuse connection [cite: 221]

@socketio.on('command')
def handle_command(json):
    """Translates JSON commands into physical actions [cite: 38, 105]"""
    action = json.get('action') # e.g., 'forward' [cite: 106]
    value = json.get('value', 0)
    
    # Trigger the hardware
    motion.execute(action, value)
    
    # Log command to DB for audit as per spec [cite: 73, 139]
    # (Implementation for DB logging goes here next)
    emit('response', {'status': 'ok', 'action': action})

if __name__ == '__main__':
    # Flask server as the central hub [cite: 93]
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)