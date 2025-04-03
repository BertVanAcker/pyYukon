import time

from pyYukon.logger.logger import *
from pyYukon.communicator.communicator import *
from pyYukon.utils.constants import *
from pyYukon.utils.auxiliary import *


class encoder_motor():
    """
        encoder_motor: Class representing encoder DC motor module

         :param bool DEBUG: setting the verbose
         :param string UDP_IP: IP address of the target device
         :param int UDP_PORT: UDP port of the target device
    """
    def __init__(self,ID="MOTOR1",logger=None,communicator=None,steps_per_second = 10,verbose=False):

        self.verbose = verbose

        # --- LOGGER ---
        self.logger = logger

        # --- COMMUNICATOR ---
        self.communicator = communicator

        # --- ENCODER MOTOR MODULE ---
        self.ID = ID
        self.steps_per_second = steps_per_second
        self.topic_motor_enable = replace_wildcard(MOTOR_TOPICS.TOPIC_MOTOR_ENABLE, self.ID)
        self.topic_motor_speed = replace_wildcard(MOTOR_TOPICS.TOPIC_MOTOR_SPEED, self.ID)

        # --- ENCODER MOTOR FEEDBACK ---
        self.speed = 0.0
        self.rpm = 0.0
        self.current = 0.0
        self.voltage = 0.0
        self.power = 0.0


    # -------------------------- MOTOR FUNCTIONS -------------------------------------
    def enable_motor(self):
        """ Enable motor"""
        self.communicator.publish_mqtt(topic=self.topic_motor_enable,message="ON")
        self.logger.syslog(msg= self.ID+": enabled",level="INFO")

    def disable_motor(self):
        """ Disable motor"""
        self.communicator.publish_mqtt(topic=self.topic_motor_enable, message="OFF")
        self.logger.syslog(msg=self.ID + ": disabled", level="INFO")


    def set_speed(self,speed=None,speed_start=None,speed_end=None,duration=0.0):
        """ Set motor speed"""
        if speed_start is None and speed_end is None and speed is not None:
            self.communicator.publish_mqtt(topic=self.topic_motor_speed, message=speed)
            self.logger.syslog(msg=self.ID + ": speed setpoint "+ speed.__str__(), level="INFO")
        elif speed is None and speed_start is not None and speed_end is not None:
            total_steps = int(duration * self.steps_per_second)
            speed_profile = [speed_start + (speed_end - speed_start) * step / total_steps for step in range(total_steps + 1)]
            for speed in speed_profile:
                self.communicator.publish_mqtt(topic=self.topic_motor_speed, message=speed)
                self.logger.syslog(msg=self.ID + ": speed setpoint " + speed.__str__(), level="INFO")
                time.sleep(1/self.steps_per_second)