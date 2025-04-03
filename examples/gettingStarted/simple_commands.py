import time
from pyYukon.devices.yukon import *
from pyYukon.utils.constants import *


yukon = yukon(config="configuration/config.yaml", verbose=True)
yukon.set_led(YUKON_BOARD.YK_LED_A,led_state=True)
time.sleep(5)
yukon.set_led(YUKON_BOARD.YK_LED_A,led_state=False)
x=1