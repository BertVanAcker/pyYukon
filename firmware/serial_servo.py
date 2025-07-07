from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.devices.lx_servo import LXServo
import uasyncio as asyncio
import ujson as json
import time
import struct
# OWN MODULES
from firmware.communication_matrix import *
from firmware.constants import *

class SerialServo:
    def __init__(self, SERVO_ID=1,DURATION=1,UPDATES=1,verbose=False):

        self.verbose=verbose
        # SERVO parameters
        self.SERVO_ID = SERVO_ID                         # The ID of the servo to control
        self.DURATION = DURATION                         # The duration of the movement
        # Monitoring parameters
        self.UPDATES = UPDATES                           # How many times to update the motors per second
        # YUKON MODULE INITIALIZATION
        self.module = SerialServoModule()                # Create a SerialServoModule object
        self.servo = None

        # ACTUATION parameters
        self.enable = False
        self.angle = 0.0

        # MQTT CLIENT
        self.client = None

    def set_servo_module(self):
        self.servo = LXServo(self.SERVO_ID, self.module.uart, self.module.duplexer)

    def angle_control(self):
        """servo angle control """
        if self.enable:
            self.servo.move_to(self.angle, self.DURATION)
            time.sleep(self.DURATION)
            self.enable = False

    def dispatch(self, action, value):
        if action == actions.ACTION_SERVO_SET_ANGLE:
            self.angle = int(value)
            self.enable = True

    def feedback(self):
        angle = self.servo.read_angle()
        voltage = self.servo.read_voltage()
        temperature = self.servo.read_temperature()

        data = {
            "angle": angle,
            "voltage": voltage,
            "temperature": temperature
        }

        # Convert to JSON string
        json_data = json.dumps(data)

        self.client.publish(feedback_messages.TOPIC_SERVO_FEEDBACK, json_data, qos=0)


