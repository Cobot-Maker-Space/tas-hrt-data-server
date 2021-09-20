import random
import time

import crate.client as c
import paho.mqtt.client as mqtt

MQTT_HOST = '10.0.10.1'
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC = 'tas/hrt/uvc/test_client_1'


def main():
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
    c.connect()
    while True:
        client.loop()
        time.sleep(1)
        client.publish(MQTT_TOPIC, str(random.random()))


if __name__ == '__main__':
    main()
