import time
import struct

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
        self.topic_motor_feedback_req = replace_wildcard(MOTOR_TOPICS.TOPIC_MOTOR_FEEDBACK_REQ, self.ID)
        self.topic_motor_feedback = replace_wildcard(MOTOR_TOPICS.TOPIC_MOTOR_FEEDBACK, self.ID)

        # --- REGISTER FEEDBACK CALLBACK ---
        self.communicator.subscribe(event_key=self.topic_motor_feedback, callback=self._feedback_callback)

        # --- ENCODER MOTOR FEEDBACK ---
        self.speed = 0.0
        self.rpm = 0.0
        self.current = 0.0
        self.voltage = 0.0
        self.power = 0.0

        self.speed_history = []
        self.rpm_history = []
        self.current_history = []
        self.voltage_history = []
        self.power_history = []



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

    def retrieve_feedback(self):
        """ Retrieve feedback from the module"""
        self.communicator.publish_mqtt(topic=self.topic_motor_feedback_req,message="REQ")
        self.logger.syslog(msg="Retrieve feedback from module: "+self.ID ,level="INFO")

    def _feedback_callback(self, msg):
        """ Callback function for retrieving module feedback """
        self.logger.syslog(msg="Retrieved feedback from module: " + self.ID, level="INFO")
        try:
            byte_data = bytes(msg[2:-1], "utf-8").decode("unicode_escape").encode("latin1")  # STRING TO BYTES [2:-1]
            unpacked_data = struct.unpack('fffff', byte_data)
            self.current, self.voltage, self.power,self.rpm,self.speed = unpacked_data
            # update history
            self.current_history.append(self.current)
            self.voltage_history.append(self.voltage)
            self.power_history.append(self.power)
            self.rpm_history.append(self.rpm)
            self.speed_history.append(self.speed)
        except:
            self.logger.syslog(msg="Unable to interpret feedback from module: " + self.ID, level="ERROR")