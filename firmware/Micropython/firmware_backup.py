import uasyncio as asyncio
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as SLOT
from pimoroni_yukon.modules import RM2WirelessModule
# OWN MODULES
from firmware.motor import *
from firmware.mqtt_as import *
from firmware.wireless import *
from firmware.communication_matrix import *


VERBOSE = True
# --------------------BEHAVIOR VARIABLES------------------------
LED_BLINK_ENABLE = False
LEDA_STATE = False
# BOARD
MAIN_OUTPUT = False
MAIN_OUTPUT_ISENABLED = False
# MOTOR
MOTOR_1_ENABLE = False
MOTOR_1_SETPOINT = 0


# ---------------------BEHAVIOR FUNCTIONS-----------------------
async def BOARD_GENERAL():
    global LEDA_STATE, MAIN_OUTPUT_ISENABLED
    while True:
        if VERBOSE: print("MAIN OUTPUT SETTING {}: {}".format(MAIN_OUTPUT, MAIN_OUTPUT_ISENABLED))

        # --- BLINKING LED A ---
        if LED_BLINK_ENABLE == "True":
            LEDA_STATE = not LEDA_STATE
            yukon.set_led('A', LEDA_STATE)
        else:
            yukon.set_led('A', False)

        # --- MAIN OUTPUT ---
        if MAIN_OUTPUT and not MAIN_OUTPUT_ISENABLED:
            MAIN_OUTPUT_ISENABLED = True
            yukon.enable_main_output()
        elif not MAIN_OUTPUT and MAIN_OUTPUT_ISENABLED:
            MAIN_OUTPUT_ISENABLED = False
            yukon.disable_main_output()

        await asyncio.sleep(2)  # Simulate periodic work


async def MOTOR_1():
    global VERBOSE, MOTOR_1_ENABLE, MOTOR_1_SETPOINT
    if VERBOSE: print(MOTOR_1_ENABLE + "-" + MOTOR_1_SETPOINT)


# -----------------------DISPATCH FUNCTION----------------------
async def on_message(topic, msg):
    global VERBOSE, LED_BLINK_ENABLE, MAIN_OUTPUT
    if VERBOSE: print("Received on topic {}: {}".format(topic, msg))
    if topic == incoming_messages.TOPIC_LED_BLINK:
        LED_BLINK_ENABLE = msg.decode()
    elif topic == incoming_messages.TOPIC_MAIN_OUTPUT:
        MAIN_OUTPUT = msg.decode()


# -----------------------MAIN LOOP------------------------------

async def main():
    client = NonBlockingMQTTClient(client_id="micropython_client", server="192.168.1.101")
    await client.connect()
    print("Connected to MQTT broker!")

    # Subscribe to a topic with the on_message callback
    await client.subscribe(incoming_messages.TOPIC_LED_BLINK, on_message)
    await client.subscribe(incoming_messages.TOPIC_MAIN_OUTPUT, on_message)

    # ADD OWN FUNCTIONS
    asyncio.create_task(BOARD_GENERAL())

    # Publish a message to a topic
    await client.publish("test/topic", "Hello from MicroPython!")

    # Keep the loop running to receive messages (adjust duration as needed)
    await asyncio.sleep(10000)

    # Disconnect cleanly
    await client.disconnect()
    print("Disconnected.")


yukon = Yukon()  # Create a new Yukon object, with a lower voltage limit set
module = RM2WirelessModule()  # Create a RM2WirelessModule object

# MOTOR 1


try:
    yukon.register_with_slot(module, SLOT)  # Register the RM2WirelessModule object with the slot
    yukon.verify_and_initialise()  # Verify that a RM2WirelessModule is attached to Yukon, and initialise it
    # Run script
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
