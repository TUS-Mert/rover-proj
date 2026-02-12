import threading
from flask import request, current_app
from flask_socketio import emit
from flask_jwt_extended import decode_token

# Import your socketio instance and hardware modules
from . import socketio, motion, db
from .models import User, CommandLog
from .sensors import sensor_manager

# A simple in-memory store for session data.
# NOTE: In a multi-worker production setup, a shared store like Redis or a
# database would be necessary to map session IDs to users across processes.
connected_users = {}

# Background thread for BME280
thread = None
thread_lock = threading.Lock()

def background_sensor_thread(app):
    """Sends sensor data to clients every 2 seconds."""
    ticks = 0
    while True:
        socketio.sleep(2)
        data = sensor_manager.get_average_readings()

        if data:
            socketio.emit("bme_data", data)

            # Log data to DB every minute (30 * 2s = 60s)
            ticks += 1
            if ticks >= 30:
                with app.app_context():
                    sensor_manager.log_data(data)
                ticks = 0

@socketio.on("connect")
def handle_connect():
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
        print("❌ Connection refused: No token provided in Authorization header.")
        return False

    try:
        decoded_token = decode_token(token)
        user_email = decoded_token["sub"]
        user = User.query.filter_by(email=user_email).first()

        if not user:
            print(f"❌ Connection refused: User '{user_email}' not found in database.")
            return False

        if not user.can_read:
            print(f"❌ Connection refused: User '{user_email}' has no privileges.")
            return False

        # Store user ID against their session ID for logging purposes
        connected_users[request.sid] = user.id

        print(f"✅ Client connected. SID: {request.sid}, User ID: {user.id}")
        
        # Start the background thread if it's not running
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_sensor_thread, current_app._get_current_object())

        emit("response", {"status": "connected", "message": "Connection successful!"})
    except Exception as e:
        print(f"❌ Connection refused: Invalid Token. Reason: {e}")
        return False  # This disconnects the client


@socketio.on("command")
def handle_command(json):
    user_id = connected_users.get(request.sid)
    if not user_id:
        print(f"❌ Command rejected: No authenticated user for session {request.sid}")
        return

    # Check for write privileges
    user = User.query.get(user_id)
    if not user or not user.can_write:
        print(f"❌ Command rejected: User {user_id} does not have write permission.")
        emit("response", {"status": "error", "message": "Insufficient permissions"})
        return

    action = json.get("action")
    value = json.get("value", 0)

    # Log the command to the database
    log_entry = CommandLog(
        command=action,
        user_id=user_id,
        is_executed=True,  # Assuming immediate execution
        executed_at=db.func.now(),
    )
    db.session.add(log_entry)
    db.session.commit()

    print(f"User {user_id} executed command: {action}")
    # Trigger the hardware
    motion.execute(action, value)

    # Feedback to the UI
    emit("response", {"status": "ok", "action": action})


@socketio.on("disconnect")
def handle_disconnect():
    user_id = connected_users.pop(request.sid, None)
    if user_id:
        print(f"Client disconnected. SID: {request.sid}, User ID: {user_id}")
    else:
        print(f"Client disconnected. SID: {request.sid} (user was not mapped).")
