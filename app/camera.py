import cv2
import time
import numpy as np
import threading

class Camera:
    def __init__(self):
        self.video = None
        self.jpeg_frame = None
        self.lock = threading.Lock()
        self.is_running = True

        try:
            # Try to initialize the camera
            # On a Raspberry Pi, you might need to use a specific backend like:
            # self.video = cv2.VideoCapture(0, cv2.CAP_V4L2)
            self.video = cv2.VideoCapture(0)
            if not self.video.isOpened():
                raise RuntimeError("Could not start camera.")
            print("✅ Real camera initialized.")
        except Exception as e:
            print(f"❌ Failed to initialize real camera: {e}")
            print("📸 Using mock camera feed instead.")
            self.video = None # Ensure it's None if init fails

        # Generate an initial "loading" frame
        self.jpeg_frame = self._create_jpeg_mock("Initializing Stream...")

        # Start the background frame grabbing thread
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.daemon = True
        self.thread.start()

    def get_frame(self):
        """Return the most recent, pre-encoded JPEG frame."""
        with self.lock:
            return self.jpeg_frame

    def _update_loop(self):
        """The background thread's main loop to capture and encode frames."""
        while self.is_running:
            jpeg_bytes = None
            if self.video:
                success, image = self.video.read()
                if success:
                    ret, buffer = cv2.imencode('.jpg', image)
                    if ret:
                        jpeg_bytes = buffer.tobytes()
                else:
                    print("⚠️ Camera frame read failed. Switching to mock feed.")
                    self.video.release()
                    self.video = None
            
            if jpeg_bytes is None:
                # If camera failed or was never present, generate a mock frame
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                jpeg_bytes = self._create_jpeg_mock(f"NO CAMERA DETECTED\n{timestamp}")

            with self.lock:
                self.jpeg_frame = jpeg_bytes
            
            # Control the capture frame rate to ~20 FPS
            time.sleep(0.05)

    def _create_jpeg_mock(self, text):
        """Creates a JPEG image with text overlay."""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        y0, dy = 240, 30 # Center the text
        for i, line in enumerate(text.split('\n')):
            y = y0 + i * dy
            cv2.putText(img, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def stop(self):
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join()
        if self.video:
            self.video.release()
        print("Camera thread stopped and resources released.")

    def __del__(self):
        self.stop()