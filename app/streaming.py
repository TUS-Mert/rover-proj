from .camera import Camera
import time

# Global camera instance
camera = Camera()

def generate_frames():
    """A generator function that yields frames from the camera."""
    while True:
        frame = camera.get_frame()
        # Yield the frame in the multipart-replace format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # Control the streaming rate to the client to ~20 FPS
        time.sleep(0.05)