from flask import request
from flask_socketio import emit
from flask_jwt_extended import decode_token
# Import your socketio instance and hardware modules
from . import socketio, motion 

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        print("❌ Connection refused: No token provided.")
        return False

    try:
        decoded_token = decode_token(token)
        print(f"✅ Client connected with valid JWT. Identity: {decoded_token['sub']}")
        emit('response', {'status': 'connected', 'message': 'Connection successful!'})
    except Exception as e:
        print(f"❌ Connection refused: Invalid Token. Reason: {e}")
        return False # This disconnects the client

@socketio.on('command')
def handle_command(json):
    # This is now a protected event because the connection is authenticated
    action = json.get('action') 
    value = json.get('value', 0)
    
    print(f"Received command: {action}")
    # Trigger the hardware
    motion.execute(action, value)
    
    # Feedback to the UI
    emit('response', {'status': 'ok', 'action': action})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")