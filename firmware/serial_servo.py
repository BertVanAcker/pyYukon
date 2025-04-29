from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.devices.lx_servo import LXServo
import uasyncio as asyncio
import ujson as json
import struct
# OWN MODULES
from firmware.communication_matrix import *

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

    async def angle_control(self):
        """servo angle control """
        while True:
            if self.enable:
                self.servo.move_to(self.angle, self.DURATION)
                asyncio.sleep(self.DURATION)
                self.enable = False
            await asyncio.sleep(1 / self.UPDATES)  #Periodic work

    async def dispatch(self, topic, msg):
        if self.verbose: print("Received on topic {}: {}".format(topic, msg))
        if topic == servo1_messages.TOPIC_SERVO_ANGLE:
            self.angle = int(msg.decode())
            self.enable = True

        # feedback
        if topic == feedback_messages.TOPIC_SERVO1_FEEDBACK_REQ:

            # TODO: RETRIEVE PARAMETERS FROM MODULE!!
            angle = 12.34
            current = 1.23
            temperature = 45.67

            data = {
                "angle": angle,
                "current": current,
                "temperature": temperature
            }

            # Convert to JSON string
            json_data = json.dumps(data)

            await self.client.publish(feedback_messages.TOPIC_SERVO_FEEDBACK, json_data)

