import time
from pyYukon.devices.yukon import *
from pyYukon.utils.constants import *


yukon = yukon(config="configuration/config.yaml", verbose=True)
yukon.start()

# ENABLE MOTOR 1
yukon.motor1.enable_motor()

# SIMPLE VELOCITY SETPOINT
yukon.motor1.set_speed(speed=1.0)
time.sleep(10)


yukon.motor1.disable_motor()
yukon.stop()

x=1
