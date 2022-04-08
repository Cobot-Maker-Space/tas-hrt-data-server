import argparse

import paho.mqtt.client as mqtt

MQTT_KEEPALIVE = 600
MQTT_TOPIC = "tas/hrt/session"


def main(args):
    client = mqtt.Client()
    client.connect(args.mqtt_host, args.mqtt_port, MQTT_KEEPALIVE)
    print("Enter the session name")
    session = input()
    print(f"Session '{session}' will start when you press enter")
    input()
    client.publish(MQTT_TOPIC, f"Session '{session}' started")
    client.loop()
    print(f"Session '{session}' will stop when you press enter")
    input()
    client.publish(MQTT_TOPIC, f"Session '{session}' stopped")
    client.loop()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Log sessions to MQTT")
    p.add_argument("mqtt_host", help="MQTT broker host address")
    p.add_argument("mqtt_port", help="MQTT broker host port", type=int)
    main(p.parse_args())
