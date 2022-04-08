import argparse
import datetime
import re
import time

import crate.client as c
import paho.mqtt.client as mqtt

MQTT_KEEPALIVE = 60
MQTT_TOPIC_UVC_BASE = "tas/hrt/uvc"
MQTT_TOPIC_UVC_REGEX = re.compile(f"^{MQTT_TOPIC_UVC_BASE}/([^/]*)$")

TIME_CONSTANT = time.time() - time.monotonic()

READINGS = {}


def on_connect(client, userdata, flags, rc):
    print(f"MQTT-Crate Bridge connected (result code: {rc})")
    client.subscribe(f"{MQTT_TOPIC_UVC_BASE}/+")


def on_message(client, user_data, msg: mqtt.MQTTMessage):
    m = MQTT_TOPIC_UVC_REGEX.match(msg.topic)
    if m:
        device = m.group(1)
        dt = datetime.datetime.fromtimestamp(msg.timestamp + TIME_CONSTANT)
        dtf = dt.strftime("%M:%S")
        READINGS[device] = (dtf, msg.payload)
        print("", end="\r")
        for k in READINGS.keys():
            t, v = READINGS[k]
            print(f" | [{t}] {k[9:]}: {float(v):.4f}", end="")


def main(args):
    client = mqtt.Client()
    client.connect(args.mqtt_host, args.mqtt_port, MQTT_KEEPALIVE)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Log sessions to MQTT")
    p.add_argument("mqtt_host", help="MQTT broker host address")
    p.add_argument("mqtt_port", help="MQTT broker host port", type=int)
    main(p.parse_args())
