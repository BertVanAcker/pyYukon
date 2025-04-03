import time

from pyYukon.logger.logger import *
from pyYukon.communicator.communicator import *
from pyYukon.utils.constants import *
from pyYukon.utils.auxiliary import *


class serial_servo():
    """
        serial_servo: Class representing serial servo module

         :param bool DEBUG: setting the verbose
         :param string UDP_IP: IP address of the target device
         :param int UDP_PORT: UDP port of the target device
    """
    def __init__(self,ID="SERVO1",logger=None,communicator=None,verbose=False):

        self.verbose = verbose

        # --- LOGGER ---
        self.logger = logger

        # --- COMMUNICATOR ---
        self.communicator = communicator

        # --- ENCODER MOTOR MODULE ---
        self.ID = ID
        self.topic_servo_angle = replace_wildcard(SERVO_TOPICS.TOPIC_SERVO_ANGLE, self.ID)

        # --- ENCODER MOTOR FEEDBACK ---
        self.angle = 0.0
        self.voltage = 0.0
        self.temperature = 0.0

    # -------------------------- MOTOR FUNCTIONS -------------------------------------
    def set_angle(self,angle=None):
        """ Set servo angle"""
        self.communicator.publish_mqtt(topic=self.topic_servo_angle, message=angle)
        self.logger.syslog(msg=self.ID + ": angle setpoint " + angle.__str__(), level="INFO")