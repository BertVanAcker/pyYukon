from pimoroni_yukon.modules import BigMotorModule
import uasyncio as asyncio
import struct
import ujson as json
# OWN MODULES
from firmware.communication_matrix import *
from firmware.constants import *

class EncoderDCMotor:
    def __init__(self, ENCODER_PIO=0, ENCODER_SM=0,ENCODER_CPR=12, GEAR_RATIO=30,UPDATES=30,verbose=False):

        self.verbose=verbose
        # Motor parameters
        self.ENCODER_PIO = ENCODER_PIO  # The PIO system to use (0 or 1) for the motor's encoder
        self.ENCODER_SM = ENCODER_SM  # The State Machines (SM) to use for the motor's encoder
        self.GEAR_RATIO = GEAR_RATIO  # The gear ratio of the motor
        self.ENCODER_CPR = ENCODER_CPR  # The number of counts a single encoder shaft revolution will produce
        self.MOTOR_CPR = self.GEAR_RATIO * self.ENCODER_CPR  # The number of counts a single motor shaft revolution will produce
        # Monitoring parameters
        self.UPDATES = UPDATES  # How many times to update the motors per second
        # YUKON MODULE INITIALIZATION
        self.module = BigMotorModule(encoder_pio=self.ENCODER_PIO,encoder_sm=self.ENCODER_SM,counts_per_rev=self.MOTOR_CPR)

        # ACTUATION parameters
        self._enable = False
        self.speed = 0.0

        #MQTT CLIENT
        self.client = None

        # FEEDBACK PARAMETERS
        self.current = 0.0
        self.voltage = 0.0
        self.power = 0.0
        self.speed = 0.0
        self.rpm = 0.0

    def enable(self):
        self._enable = True
        self.module.enable()  # Enable the motor driver on the BigMotorModule

    def disable(self):
        self._enable = False
        self.module.disable()  # Disable the motor driver on the BigMotorModule

    def velocity_control(self):
        """Open loop velocity control """
        if self._enable:
            self.module.motor.speed(float(self.speed))
        else:
            self.speed = 0.0
            self.module.motor.speed(0.0)



    def dispatch(self,action,value):

        if action == actions.ACTION_MOTOR_ENABLE:
            if "True" in value:
                self._enable = True
            else:
                self._enable = False
        elif action == actions.ACTION_MOTOR_SET_SPEED:
            print("setting speed")
            self.speed = value

    def feedback(self):
        self.current = 0.00  # TODO: fetch current
        self.voltage = 12.00     #TODO: fetch voltage
        self.power = 0.0        #TODO: fetch or calculate
        self.rpm = 10.00         # TODO: fetch or calculate

        data = {
            "current": self.current,
            "voltage": self.voltage,
            "power": self.power,
            "speed": self.speed,
            "rpm": self.rpm,
        }

        # Convert to JSON string
        json_data = json.dumps(data)

        self.client.publish(feedback_messages.TOPIC_MOTOR1_FEEDBACK, json_data,qos=0)


