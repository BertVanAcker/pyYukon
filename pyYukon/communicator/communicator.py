import serial
import paho.mqtt.client as mqtt
from pyYukon.utils.constants import *
from pyYukon.utils.auxiliary import *

class communicator():
    """
        Communicator: Class representing the generic communication handler

         :param bool DEBUG: setting the verbose
         :param string UDP_IP: IP address of the target device
         :param string UDP_PORT: UDP port of the target device
         :param string COM_PORT: COM port of the target device
         :param int COM_BAUD: Baud rate of the target device

         :param object Logger: Logger object for uniform logging
    """
    def __init__(self,config=None,COM_PORT=SERIAL_CONFIG.YK_DEFAULT_PORT, COM_BAUD=SERIAL_CONFIG.YK_DEFAULT_BAUD, MQTT_BROKER=MQTT_CONFIG.YK_MQTT_BROKER, MQTT_PORT=MQTT_CONFIG.YK_MQTT_PORT,ACTIVE_COMM="MQTT", DEBUG=True, LOGGER=None):

        # verbose and logging
        self._debug = DEBUG
        self._logger = LOGGER

        # communicator configuration
        self.config = load_config(config_file=config)

        # serial (USB) interface
        self.COM_PORT = COM_PORT
        self.COM_BAUD = COM_BAUD
        self.Serial_socket = None

        # MQTT interface
        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.mqtt_client = mqtt.Client()
        self.mqtt_subscribe_topics = []

        # active communcation
        self.event_callbacks = {}  # Store callbacks for MQTT, Redis
        self.activeCOMM = ACTIVE_COMM  # UBSserial [Serial] / MQTT connection [MQTT]

        #if self.activeCOMM == "MQTT":
        #    self.activateMQTT()



    def activateSerial(self):
        """
              Function to activate the serial communication method
        """
        self.activeCOMM = "Serial"
        self.Serial_socket = serial.Serial(self.COM_PORT, self.COM_BAUD)
        # close and re-open
        self.Serial_socket.close()
        self.Serial_socket.open()

    def activateMQTT(self):
        """" Function to activate the MQTT communication"""

        # configure the MQTT connection
        if 'YUKON_COMM_CONFIG' in self.config:
            board_feedback = self.config['YUKON_COMM_CONFIG']
            for item in board_feedback:
                if 'property' in item and 'name' in item['property']:
                    self.mqtt_subscribe_topics.append(item['property']['topic'])

            modules_feedback = self.config['YUKON_COMM_CONFIG']['modules']
            for item in modules_feedback:
                if 'module' in item:
                    feedbacks = item['module']['feedbacks']
                    for module_item in feedbacks:
                        self.mqtt_subscribe_topics.append(module_item['topic'])

        self.initialize_mqtt()



    def initialize_mqtt(self):
        """Initialize MQTT subscriptions based on the config file."""
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(self.config['mqtt_broker'], self.config['mqtt_port'])

        for topic in self.mqtt_subscribe_topics:
            self.mqtt_client.subscribe(topic)
            self._logger.syslog(msg=f"Subscribed to MQTT topic: {topic}", level="INFO")
            #self._logger.info(f"Subscribed to MQTT topic: {topic}")

        self.mqtt_client.loop_start()

    def on_mqtt_message(self, client, userdata, message):
        """Handle incoming MQTT messages and trigger any registered callbacks."""
        payload = message.payload.decode("utf-8")
        topic = message.topic
        self._logger.syslog(msg=f"Received MQTT message: {payload} on topic: {topic}", level="INFO")

        # Trigger any registered callbacks for this topic
        self.trigger_callbacks(topic, payload)

    def publish_mqtt(self, topic, message):
        """Publish a message to an MQTT topic."""
        #if topic in self.mqtt_publish_topics:
        #    self.mqtt_client.publish(topic, message)
        #    self.logger.info(f"Published to MQTT topic {topic}: {message}")
        #else:
        #    self.logger.warning(f"Cannot publish to {topic}: Not configured in yaml")
        self.mqtt_client.publish(topic, message)
        self._logger.syslog(msg=f"Published to MQTT topic {topic}: {message}", level="INFO")


    def trigger_callbacks(self, event_key, data):
        """
        Trigger all callbacks associated with an event.
        :param event_key: The event key (MQTT topic, Redis key, etc.)
        :param data: The data to pass to the callbacks
        """
        if event_key in self.event_callbacks:
            for callback in self.event_callbacks[event_key]:
                callback(data)

    def subscribe(self, event_key, callback):
        """
        Register a callback for a given event key (MQTT topic, Redis key).
        :param event_key: The event key (MQTT topic, Redis key, etc.)
        :param callback: The function to call when the event is triggered
        """
        if event_key not in self.event_callbacks:
            self.event_callbacks[event_key] = []
        self.event_callbacks[event_key].append(callback)
        self._logger.syslog(msg=f"Registered callback for event: {event_key}", level="INFO")

    def shutdown(self):
        """Shut down the Event Handler."""
        self.mqtt_client.loop_stop()
        self._logger.info("Event Handler shut down.")