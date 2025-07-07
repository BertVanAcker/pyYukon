import uasyncio as asyncio
from pimoroni_yukon.modules import BigMotorModule
#OWN MODULES
from firmware.communication_matrix import *
from firmware.constants import *

class YukonBoard:
    def __init__(self, yukon=None,update=2,verbose=False):
        #Yukon object
        self.yukon = yukon

        #Auxiliary
        self.verbose = verbose
        self.UPDATE = update

        # Board parameters
        self.LED_A_STATE = False
        self.LED_A_BLINK = "False"
        self.LED_B_STATE = False
        self.LED_B_BLINK = "False"
        self.MAIN_OUTPUT_STATE = False
        self.MAIN_OUTPUT_ISENABLED = False

    def BOARD_GENERAL(self):

        # --- BLINKING LED A ---
        if "True" in self.LED_A_BLINK:
            self.LED_A_STATE = not self.LED_A_STATE
            self.yukon.set_led('A', self.LED_A_STATE)
        elif "True" in self.LED_B_BLINK:
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

    def dispatch(self,action,value):

        if action == actions.ACTION_BLINK_A:
            self.LED_A_BLINK = value
        elif action == actions.ACTION_BLINK_B:
            self.LED_B_BLINK = value
        elif action== actions.ACTION_OUTPUT_ENABLE:
            self.MAIN_OUTPUT_STATE = value