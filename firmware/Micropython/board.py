import uasyncio as asyncio
from pimoroni_yukon.modules import BigMotorModule
#OWN MODULES
from firmware.communication_matrix import *

class YukonBoard:
    def __init__(self, yukon=None,update=2,verbose=False):
        #Yukon object
        self.yukon = yukon

        #Auxiliary
        self.verbose = verbose
        self.UPDATE = update

        # Board parameters
        self.LED_A_STATE = False
        self.LED_A_BLINK = False
        self.LED_B_STATE = False
        self.LED_B_BLINK = False
        self.MAIN_OUTPUT_STATE = False
        self.MAIN_OUTPUT_ISENABLED = False



    async def BOARD_GENERAL(self):

        while True:
            if self.verbose: print("MAIN OUTPUT SETTING {}: {}".format(self.MAIN_OUTPUT_STATE, self.MAIN_OUTPUT_ISENABLED))
            # --- BLINKING LED A ---
            if self.LED_A_BLINK == "True":
                self.LED_A_STATE = not self.LED_A_STATE
                self.yukon.set_led('A', self.LED_A_STATE)
            if self.LED_B_BLINK == "True":
                self.LED_B_STATE = not self.LED_B_STATE
                self.yukon.set_led('B', self.LED_B_STATE)
            else:
                self.yukon.set_led('A', False)
                self.yukon.set_led('B', False)

            # --- MAIN OUTPUT ---
            if self.MAIN_OUTPUT_STATE and not self.MAIN_OUTPUT_ISENABLED:
                self.MAIN_OUTPUT_ISENABLED = True
                self.yukon.enable_main_output()
            elif not self.MAIN_OUTPUT_STATE and self.MAIN_OUTPUT_ISENABLED:
                self.MAIN_OUTPUT_ISENABLED = False
                self.yukon.disable_main_output()

            await asyncio.sleep(self.UPDATE)  # Simulate periodic work

    async def dispatch(self,topic, msg):

        if self.verbose: print("Received on topic {}: {}".format(topic, msg))
        if topic == general_messages.TOPIC_LED_A_BLINK:
            self.LED_A_BLINK = msg.decode()
        elif topic == general_messages.TOPIC_LED_B_BLINK:
            self.LED_B_BLINK = msg.decode()
        elif topic == general_messages.TOPIC_MAIN_OUTPUT:
            self.MAIN_OUTPUT_STATE = msg.decode()