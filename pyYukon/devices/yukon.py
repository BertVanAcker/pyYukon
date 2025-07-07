from pyYukon.devices.serialServo import serial_servo
from pyYukon.logger.logger import *
from pyYukon.communicator.communicator import *
from pyYukon.utils.constants import *
from pyYukon.utils.auxiliary import *
from pyYukon.devices.motor import *


class yukon():
    """
        Yukon: Class representing generic yukon device

         :param bool DEBUG: setting the verbose
         :param string UDP_IP: IP address of the target device
         :param int UDP_PORT: UDP port of the target device
    """
    def __init__(self,config=None,verbose=False):
        self.verbose = verbose
        self.config = load_config(config_file=config)

        # --- LOGGER ---
        self.logger = self.configure_logger()
        self.logger.syslog(msg="Yukon: logger initialized",level="INFO")

        # --- COMMUNICATOR ---
        self.communicator = communicator(config=config,LOGGER=self.logger,ACTIVE_COMM="MQTT",DEBUG=verbose)
        self.communicator.activateMQTT()

        # --- YUKON MODULES ---
        self.motor1 = encoder_motor(ID="MOTOR1",logger=self.logger,communicator=self.communicator,steps_per_second=10,verbose=self.verbose)
        self.servo1 = serial_servo(ID="SERVO1",logger=self.logger,communicator=self.communicator,verbose=self.verbose)
        # --- ACTIVATE COMMUNCATION ---






    # -------------------------- BOARD FUNCTIONS -------------------------------------
    def enable_main_output(self):
        """ Enable main output of the Yukon board"""
        msg = formatMessage(module="BOARD",action="OUTPUT_ENABLE",value=True)
        self.communicator.publish_mqtt(topic=YUKON_BOARD_TOPICS.TOPIC_ACTION,message=msg)
        self.logger.syslog(msg="Yukon: main output enabled",level="INFO")

    def disable_main_output(self):
        """ Enable main output of the Yukon board"""
        msg = formatMessage(module="BOARD", action="OUTPUT_ENABLE", value=False)
        self.communicator.publish_mqtt(topic=YUKON_BOARD_TOPICS.TOPIC_ACTION,message=msg)
        self.logger.syslog(msg="Yukon: main output disabled",level="INFO")

    def blink_led(self,LED=YUKON_BOARD.YK_LED_A,activation = "True"):
        if LED == YUKON_BOARD.YK_LED_A:
            msg = formatMessage(module="BOARD", action="ACTION_BLINK_A", value=activation)
            self.communicator.publish_mqtt(topic=YUKON_BOARD_TOPICS.TOPIC_ACTION,message=msg)
            self.logger.syslog(msg="Yukon: blinking "+LED, level="INFO")
        elif LED == YUKON_BOARD.YK_LED_B:
            msg = formatMessage(module="BOARD", action="ACTION_BLINK_B", value=activation)
            self.communicator.publish_mqtt(topic=YUKON_BOARD_TOPICS.TOPIC_ACTION, message=msg)
            self.logger.syslog(msg="Yukon: blinking " + LED, level="INFO")
        else:
            self.logger.syslog(msg="Yukon: Unable to set state of "+LED, level="ERROR")


    def _request_module_feedback(self):
        """Request periodic feedback from all modules"""
        self.motor1.retrieve_feedback()
        self.servo1.retrieve_feedback()


    def configure_logger(self):
        path='logs/device.log'
        if 'logging' in self.config:
            path = self.config['logging']['file']

        return logger(name="yukon_logger",path=path,verbose=self.verbose)