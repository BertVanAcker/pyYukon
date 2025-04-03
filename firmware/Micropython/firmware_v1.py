import uasyncio as asyncio
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as SLOT
from pimoroni_yukon import SLOT1 as SLOT_MOTOR1
from pimoroni_yukon.modules import RM2WirelessModule

# OWN MODULES
from firmware.motor import *
from firmware.board import *
from firmware.mqtt_as import *
from firmware.wireless import *
from firmware.communication_matrix import *


VERBOSE = True
#---------------------- GENERAL INITIALIZATION-------------------

yukon = Yukon()  # Create a new Yukon object, with a lower voltage limit set
module = RM2WirelessModule()  # Create a RM2WirelessModule object

# ---------------------BOARD INITIALIZATION-----------------------
board = YukonBoard(yukon=yukon,update=2,verbose=VERBOSE)

# ---------------------MOTORS INITIALIZATION-----------------------
motor1 = EncoderDCMotor(ENCODER_PIO=0, ENCODER_SM=0,ENCODER_CPR=12, GEAR_RATIO=30,UPDATES=20,verbose=VERBOSE)

# -----------------------MAIN LOOP------------------------------
async def main():
    client = NonBlockingMQTTClient(client_id="micropython_client", server="192.168.1.101")
    await client.connect()
    print("Connected to MQTT broker!")

    # Yukon board subscriptions
    await client.subscribe(general_messages.TOPIC_LED_A_BLINK, board.dispatch)
    await client.subscribe(general_messages.TOPIC_LED_B_BLINK, board.dispatch)
    await client.subscribe(general_messages.TOPIC_MAIN_OUTPUT, board.dispatch)
    # Yukon motor 1 subscriptions
    await client.subscribe(motor1_messages.TOPIC_MOTOR_ENABLE, motor1.dispatch)
    await client.subscribe(motor1_messages.TOPIC_MOTOR_SPEED, motor1.dispatch)

    # ADD OWN FUNCTIONS
    asyncio.create_task(board.BOARD_GENERAL())
    asyncio.create_task(motor1.open_loop_velocity_control())

    # Publish a message to a topic
    #await client.publish("test/topic", "Hello from MicroPython!")

    # Keep the loop running to receive messages (adjust duration as needed)
    await asyncio.sleep(10000)

    # Disconnect cleanly
    await client.disconnect()
    print("Disconnected.")

try:
    yukon.register_with_slot(module, SLOT)  # Register the RM2WirelessModule object with the slot
    yukon.register_with_slot(motor1.module, SLOT_MOTOR1)
    yukon.verify_and_initialise()  # Verify that a RM2WirelessModule is attached to Yukon, and initialise it
    yukon.enable_main_output()  # Turn on power to the module slots

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
