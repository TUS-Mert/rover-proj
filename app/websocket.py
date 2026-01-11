from flask import request
from flask_socketio import emit
from flask_jwt_extended import decode_token
# Import your socketio instance and hardware modules
from . import socketio, motion 

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    try:
        decode_token(token)
        print("✅ Client connected with valid JWT")
    except Exception:
        print("❌ Connection refused: Invalid Token")
        return False 

@socketio.on('command')
def handle_command(json):
    action = json.get('action') 
    value = json.get('value', 0)
    
    # Trigger the hardware
    motion.execute(action, value)
    
    # Feedback to the UI
    emit('response', {'status': 'ok', 'action': action})