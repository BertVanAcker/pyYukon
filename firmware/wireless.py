import network
import time

# Wi-Fi Credentials
SSID = "home-net-lab"
PASSWORD = "@BMKR_LAB"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)

    print("Wi-Fi connected:", wlan.ifconfig())
