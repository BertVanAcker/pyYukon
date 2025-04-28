from pimoroni_yukon.modules import BigMotorModule
import uasyncio as asyncio
import struct
# OWN MODULES
from firmware.communication_matrix import *

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
        self.enable = False
        self.speed = 0.0

        #MQTT CLIENT
        self.client = None

    def enable(self):
        self.module.enable()  # Enable the motor driver on the BigMotorModule

    def disable(self):
        self.module.disable()  # Disable the motor driver on the BigMotorModule

    async def open_loop_velocity_control(self):
        """Open loop velocity control """
        while True:
            if self.enable:
                self.module.motor.speed(float(self.speed))
            else:
                self.speed = 0.0
                self.module.motor.speed(0.0)
            await asyncio.sleep(1 / self.UPDATES)  #Periodic work

    async def dispatch(self, topic, msg):

        if self.verbose: print("Received on topic {}: {}".format(topic, msg))
        if topic == motor1_messages.TOPIC_MOTOR_ENABLE:
            if msg.decode() == "ON":
                self.enable = True
            else:
                self.enable = False

        if topic == motor1_messages.TOPIC_MOTOR_SPEED:
            self.speed = msg.decode()

        # feedback
        if topic == feedback_messages.TOPIC_MOTOR1_FEEDBACK_REQ:
            current = 0        #TODO: fetch current
            voltage = 12.0     #TODO: fetch voltage
            power = 0.0        #TODO: fetch or calculate
            speed = 0.0        #TODO: fetch speed
            rpm = 0.0          # TODO: fetch or calculate

            packed_data = struct.pack('fffff', current, voltage, power,rpm,speed)

            #TODO: publish the parameters to MQTT
            await self.client.publish(feedback_messages.TOPIC_MOTOR1_FEEDBACK, packed_data)


