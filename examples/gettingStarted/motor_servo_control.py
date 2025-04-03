import time
from pyYukon.devices.yukon import *
from pyYukon.utils.constants import *


yukon = yukon(config="configuration/config.yaml", verbose=True)
# ENABLE MOTOR 1
yukon.motor1.enable_motor()

# SIMPLE VELOCITY SETPOINT
yukon.motor1.set_speed(speed=1.0)
time.sleep(5)
yukon.servo1.set_angle(angle=180)
time.sleep(2)
yukon.servo1.set_angle(angle=0)

time.sleep(5)
yukon.motor1.disable_motor()

