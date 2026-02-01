import os
from gpiozero import Robot, Servo

# Detect environment
IS_PROD = os.getenv('ENV') == 'production'

if IS_PROD:
    from gpiozero.pins.lgpio import LPiFactory
    factory = LPiFactory()
else:
    from gpiozero.pins.mock import MockFactory, MockPWMPin
    factory = MockFactory(pin_class=MockPWMPin) 
    print("Running with Mock Hardware (PWM Supported)")

class MotionController:
    def __init__(self):
        # Now this won't crash because 'factory' understands PWM/Frequency
        self.rover = Robot(left=(17, 18), right=(22, 23), pin_factory=factory)
        self.camera = Servo(25, pin_factory=factory)
    def execute(self, action, value=0):
        if action == "forward":
            self.rover.forward()
        elif action == "backward":
            self.rover.backward()
        elif action == "left":
            self.rover.left()
        elif action == "right":
            self.rover.right()
        elif action == "stop":
            self.rover.stop()
        print(f"Executed {action}")


# Global instance for the app to use
_controller = MotionController()
def execute(action, value=0):
    _controller.execute(action, value)

