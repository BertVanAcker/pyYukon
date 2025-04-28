import time
import struct

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
        self.topic_servo_feedback_req = replace_wildcard(SERVO_TOPICS.TOPIC_SERVO_FEEDBACK_REQ, self.ID)
        self.topic_servo_feedback = replace_wildcard(SERVO_TOPICS.TOPIC_SERVO_FEEDBACK, self.ID)

        # --- REGISTER FEEDBACK CALLBACK ---
        self.communicator.subscribe(event_key=self.topic_servo_feedback, callback=self._feedback_callback)

        # --- ENCODER MOTOR FEEDBACK ---
        self.angle = 0.0
        self.current = 0.0
        self.temperature = 0.0

        self.angle_history = []
        self.current_history = []
        self.temperature_history = []

    # -------------------------- MOTOR FUNCTIONS -------------------------------------
    def set_angle(self,angle=None):
        """ Set servo angle"""
        self.communicator.publish_mqtt(topic=self.topic_servo_angle, message=angle)
        self.logger.syslog(msg=self.ID + ": angle setpoint " + angle.__str__(), level="INFO")

    def retrieve_feedback(self):
        """ Retrieve feedback from the module"""
        self.communicator.publish_mqtt(topic=self.topic_servo_feedback_req,message="REQ")
        self.logger.syslog(msg="Retrieve feedback from module: "+self.ID ,level="INFO")

    def _feedback_callback(self, msg):
        """ Callback function for retrieving module feedback """
        self.logger.syslog(msg="Retrieved feedback from module: " + self.ID, level="INFO")
        try:
            byte_data = bytes(msg[2:-1], "utf-8").decode("unicode_escape").encode("latin1")         # STRING TO BYTES [2:-1]
            unpacked_data = struct.unpack('fff', byte_data)
            self.angle, self.current, self.temperature = unpacked_data
            # update history
            self.angle_history.append(self.angle)
            self.current_history.append(self.current)
            self.temperature_history.append(self.temperature)
        except:
            self.logger.syslog(msg="Unable to interpret feedback from module: " + self.ID, level="ERROR")
