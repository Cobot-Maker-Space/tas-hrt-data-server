import argparse
import json

import paho.mqtt.client as mqtt
import roslibpy

MQTT_KEEPALIVE = 600
MQTT_TOPIC = "tas/hrt/odometry"

last_pose = None
last_twist = None


def odom_callback(mqtt_client, message):
    global last_twist, last_pose
    pose = message["pose"]["pose"]
    twist = message["twist"]["twist"]
    if twist != last_twist or pose != last_pose:
        last_pose = pose
        last_twist = twist
        d = {
            "pose": pose,
            "twist": twist,
        }
        mqtt_client.publish(MQTT_TOPIC, json.dumps(d))
        mqtt_client.loop()


def main(args):
    ros_client = roslibpy.Ros(host=args.rosbridge_host, port=args.rosbridge_port)
    mqtt_client = mqtt.Client()
    mqtt_client.connect(args.mqtt_host, args.mqtt_port, MQTT_KEEPALIVE)
    odom_topic = roslibpy.Topic(ros_client, "/odom", "nav_msgs/Odometry")
    odom_topic.subscribe(callback=lambda msg: odom_callback(mqtt_client, msg))
    ros_client.run_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Log ROS odometry messages to MQTT")
    p.add_argument("mqtt_host", help="MQTT broker host address")
    p.add_argument("mqtt_port", help="MQTT broker host port", type=int)
    p.add_argument("rosbridge_host", help="ROS bridge host address")
    p.add_argument("rosbridge_port", help="ROS bridge host port", type=int)
    main(p.parse_args())
