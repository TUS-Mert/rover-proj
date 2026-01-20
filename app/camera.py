import time
import threading
import os
import numpy as np

# 1. Safe Import: Try to load OpenCV, but don't crash if it's missing.
try:
    import cv2
except ImportError:
    cv2 = None

# 2. Determine Simulation Mode
# We simulate if:
# - cv2 is missing (CI environment)
# - SIMULATE_HARDWARE env var is set
# - FLASK_ENV is set to 'testing'
SIMULATE = (cv2 is None) or \
           (os.getenv('SIMULATE_HARDWARE') == 'true') or \
           (os.getenv('FLASK_ENV') == 'testing')

class Camera:
    def __init__(self):
        self.video = None
        self.jpeg_frame = None
        self.lock = threading.Lock()
        self.is_running = True
        self.thread = None

        # 3. Initialization Logic
        if SIMULATE:
            print("📸 Simulation Mode: Skipping Real Camera Hardware.")
            # Generate a safe placeholder immediately
            self.jpeg_frame = self._create_jpeg_mock("Simulation Mode")
        else:
            try:
                # Real Hardware Init
                self.video = cv2.VideoCapture(0)
                if not self.video.isOpened():
                    raise RuntimeError("Could not start camera.")
                print("✅ Real camera initialized.")
                self.jpeg_frame = self._create_jpeg_mock("Initializing...")
            except Exception as e:
                print(f"❌ Camera Error: {e}")
                print("📸 Fallback to simulation.")
                # Fallback if hardware fails despite libraries being present
                self.video = None
                self.jpeg_frame = self._create_jpeg_mock("Camera Failed")

        # Start the background thread (even in simulation, to keep logic consistent)
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.daemon = True
        self.thread.start()

    def get_frame(self):
        """Thread-safe access to the latest frame."""
        with self.lock:
            # If for some reason frame is None, return a fallback byte string
            if self.jpeg_frame is None:
                return self._create_jpeg_mock("No Frame")
            return self.jpeg_frame

    def _update_loop(self):
        """Main loop to capture or generate frames."""
        while self.is_running:
            # --- PATH A: SIMULATION / NO HARDWARE ---
            if SIMULATE or self.video is None:
                # In testing/CI, we sleep longer to save CPU
                if os.getenv('FLASK_ENV') == 'testing':
                    time.sleep(0.1) 
                    continue
                
                # In simulation dev mode, update the timestamp
                timestamp = time.strftime("%H:%M:%S")
                with self.lock:
                    self.jpeg_frame = self._create_jpeg_mock(f"SIMULATION\n{timestamp}")
                time.sleep(0.5)
                continue

            # --- PATH B: REAL HARDWARE ---
            success, image = self.video.read()
            if success:
                # Encode to JPEG
                ret, buffer = cv2.imencode('.jpg', image)
                if ret:
                    with self.lock:
                        self.jpeg_frame = buffer.tobytes()
            else:
                print("⚠️ Camera frame read failed.")
            
            # Maintain ~20 FPS
            time.sleep(0.05)

    def _create_jpeg_mock(self, text):
        """Creates a placeholder image safely."""
        # SAFETY CHECK: If cv2 is missing, return raw bytes (Magic JPEG Header)
        # This prevents the 'NameError: name 'cv2' is not defined' crash
        if cv2 is None:
            return b'\xff\xd8\xff\xe0\x00\x10JFIF' 

        # If cv2 exists, draw the text
        try:
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add text (Green color)
            cv2.putText(img, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            ret, jpeg = cv2.imencode('.jpg', img)
            if ret:
                return jpeg.tobytes()
        except Exception:
            pass
            
        # Ultimate fallback if drawing fails
        return b'\xff\xd8\xff\xe0\x00\x10JFIF'

    def stop(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        if self.video and self.video.isOpened():
            self.video.release()

    def __del__(self):
        self.stop()