from gpiozero import Robot, Servo
from gpiozero.pins.lgpio import LPiFactory

# RPi 5 requires the lgpio factory
factory = LPiFactory()


class MotionController:
    def __init__(self):
        # Pins for L298N and SG90 Servo [cite: 107]
        self.rover = Robot(left=(17, 18), right=(22, 23), pin_factory=factory)
        self.camera = Servo(25, pin_factory=factory)

    def execute(self, action, value=None):
        """Maps JSON actions to hardware calls [cite: 109]"""
        if action == "forward":
            self.rover.forward()
        elif action == "stop":
            self.rover.stop()
        elif action == "tilt":
            # Map 0-180 degrees to -1 to 1 for gpiozero [cite: 106]
            self.camera.value = (value / 90.0) - 1.0
