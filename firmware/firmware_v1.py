import uasyncio as asyncio
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as SLOT
from pimoroni_yukon import SLOT1 as SLOT_MOTOR1
from pimoroni_yukon import SLOT3 as SLOT_SERVO1
from pimoroni_yukon.modules import RM2WirelessModule

# OWN MODULES
from firmware.motor import *
from firmware.board import *
from firmware.mqtt_as import *
from firmware.wireless import *
from firmware.serial_servo import *
from firmware.communication_matrix import *


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

# -----------------------MAIN LOOP------------------------------
async def main():
    client = NonBlockingMQTTClient(client_id="micropython_client", server="192.168.1.101")
    await client.connect()
    print("Connected to MQTT broker!")

    # ASSIGN MQTT CLIENT FOR FEEDBACK PUBLISHING
    motor1.client = client
    servo1.client = client

    # Yukon board subscriptions
    await client.subscribe(general_messages.TOPIC_LED_A_BLINK, board.dispatch)
    await client.subscribe(general_messages.TOPIC_LED_B_BLINK, board.dispatch)
    await client.subscribe(general_messages.TOPIC_MAIN_OUTPUT, board.dispatch)
    # Yukon motor 1 subscriptions
    await client.subscribe(motor1_messages.TOPIC_MOTOR_ENABLE, motor1.dispatch)
    await client.subscribe(motor1_messages.TOPIC_MOTOR_SPEED, motor1.dispatch)
    # Yukon servo 1 subscriptions
    await client.subscribe(servo1_messages.TOPIC_SERVO_ANGLE, servo1.dispatch)
    # Feedback requests
    await client.subscribe(feedback_messages.TOPIC_MOTOR1_FEEDBACK_REQ, motor1.dispatch)
    await client.subscribe(feedback_messages.TOPIC_SERVO1_FEEDBACK_REQ, servo1.dispatch)

    # ADD OWN FUNCTIONS
    asyncio.create_task(board.BOARD_GENERAL())
    asyncio.create_task(motor1.open_loop_velocity_control())
    asyncio.create_task(servo1.angle_control())

    # Publish a message to a topic
    #await client.publish("test/topic", "Hello from MicroPython!")

    # Keep the loop running to receive messages (adjust duration as needed)
    await asyncio.sleep(10000)

    # Disconnect cleanly
    await client.disconnect()
    print("Disconnected.")

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
    motor1.module.enable()
    # WIRELESS connection
    connect_wifi()



    # Run the async main loop
    asyncio.run(main())

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()

    # Attempt to disconnect from WiFi
    try:
        wlan.disconnect()
    except Exception:
        pass
