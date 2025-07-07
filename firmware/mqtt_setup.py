from umqtt.simple import MQTTClient
from firmware.communication_matrix import *



#---------------------- MQTT INITIALIZATION-------------------
SERVER="192.168.1.101"
ClientID = 'Yukon_board'
user = "emqx"
password = "public"

def mqtt_setup(client_id="Yukon_board", server="192.168.1.101"):
    client = MQTTClient(client_id, server, 1883, user, password)
    return client

def yukon_subscriptions(client=None):
    #BOARD SUBSCRIPTIONS
    client.subscribe(general_messages.TOPIC_ACTION)

