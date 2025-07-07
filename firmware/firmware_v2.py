from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as SLOT
from pimoroni_yukon import SLOT1 as SLOT_MOTOR1
from pimoroni_yukon import SLOT3 as SLOT_SERVO1
from pimoroni_yukon.modules import RM2WirelessModule

# OWN MODULES
from firmware.motor import *
from firmware.board import *
from firmware.mqtt_setup import *
from firmware.wireless import *
from firmware.serial_servo import *
from firmware.timed_function import *
import ujson


VERBOSE = True
#---------------------- GENERAL INITIALIZATION-------------------
VOLTAGE_LIMIT = 8.4         # The voltage to not exceed, to protect the servos -> TODO: user other servo to enable 12V motors
POWER_ON_DELAY = 2.0        # The time to sleep after turning on the power, for serial servos to power on

yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
module = RM2WirelessModule()  # Create a RM2WirelessModule object

# ---------------------BOARD INITIALIZATION-----------------------
board = YukonBoard(yukon=yukon,update=2,verbose=VERBOSE)

# ---------------------MOTORS INITIALIZATION-----------------------
motor1 = EncoderDCMotor(ENCODER_PIO=0, ENCODER_SM=0,ENCODER_CPR=12, GEAR_RATIO=30,UPDATES=20,verbose=VERBOSE)


# ---------------------SERIAL SERVO INITIALIZATION-----------------------
servo1 = SerialServo(SERVO_ID=1,DURATION=0.5,UPDATES=1,verbose=VERBOSE)


#--------------------DISPATCH FUNCTION-------------------------
def dispatch(topic, msg):
    if VERBOSE:print('received message %s on topic %s' % (msg, topic))
    #DECODE DATA
    data = ujson.loads(msg)

    #BOARD TOPICS
    if "BOARD" in data["module"]:
        board.dispatch(action=data["action"], value=data["value"])
    elif "MOTOR1" in data["module"]:
        motor1.dispatch(action=data["action"], value=data["value"])
    elif "SERVO" in data["module"]:
        servo1.dispatch(action=data["action"], value=data["value"])



# -------------------PERIODIC FUNCTIONS-------------------------
boardFunction = timerFuction(1,board.BOARD_GENERAL)
motorFunction = timerFuction(0.5,motor1.velocity_control)
servoFunction = timerFuction(0.5,servo1.angle_control)

boardFeedbackFunction = timerFuction(1,board.feedback)
motorFeedbackFunction = timerFuction(1,motor1.feedback)
servoFeedbackFunction = timerFuction(1,servo1.feedback)

# -----------------------MAIN LOOP------------------------------
def main():
    client = mqtt_setup(client_id="YUKON_FIRMWARE_v2",server="192.168.1.101")
    #ASSIGN MQTT CLIENTS
    board.client = client
    motor1.client = client
    servo1.client = client

    client.set_callback(dispatch)
    client.connect()
    print("Connected to MQTT broker!")
    # subscriptions
    yukon_subscriptions(client=client)

    # start all periodic functions
    boardFunction.start()
    boardFeedbackFunction.start()
    motorFunction.start()
    motorFeedbackFunction.start()
    servoFunction.start()
    servoFeedbackFunction.start()

    while True:
        client.check_msg()


try:
    yukon.register_with_slot(module, SLOT)                      # Register the RM2WirelessModule object with the slot
    yukon.register_with_slot(motor1.module, SLOT_MOTOR1)        # Register the BigMotor object with the slot
    yukon.register_with_slot(servo1.module, SLOT_SERVO1)        # Register the SerialServo object with the slot
    yukon.verify_and_initialise()  # Verify that a RM2WirelessModule is attached to Yukon, and initialise it
    yukon.enable_main_output()  # Turn on power to the module slots

    yukon.monitored_sleep(POWER_ON_DELAY)  # Wait for serial servos to power up
    # Create an LXServo object to interact with the servo,
    # giving it access to the module's UART and Duplexer
    servo1.set_servo_module()

    # Enable motor 1
    motor1.enable()
    # WIRELESS connection
    connect_wifi()

    # Run the main loop
    main()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()

    # Attempt to disconnect from WiFi
    try:
        wlan.disconnect()
    except Exception:
        pass
