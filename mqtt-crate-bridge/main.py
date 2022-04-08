import re
import time

from threading import Lock
from typing import final

import crate.client as crate
import paho.mqtt.client as mqtt

MQTT_HOST = "mqtt"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC_UVC_BASE = "tas/hrt/uvc"
MQTT_TOPIC_UVC_REGEX = re.compile(f"^{MQTT_TOPIC_UVC_BASE}/([^/]*)$")
MQTT_TOPIC_LOG = "tas/hrt/session"
MQTT_TOPIC_ODOM_LOG = "tas/hrt/odometry"

CRATE_HOST = "http://crate:4200"
CRATE_USERNAME = "crate"

TIME_CONSTANT = time.time() - time.monotonic()

MUTEX = Lock()


def on_connect(client, userdata, flags, rc):
    print(f"MQTT-Crate Bridge connected (result code: {rc})")
    client.subscribe(f"{MQTT_TOPIC_UVC_BASE}/+")
    client.subscribe(MQTT_TOPIC_LOG)
    client.subscribe(MQTT_TOPIC_ODOM_LOG)


def on_message(client, cursor: crate.connection.Cursor, msg: mqtt.MQTTMessage):
    m = MQTT_TOPIC_UVC_REGEX.match(msg.topic)
    MUTEX.acquire()
    try:
        if m:
            cursor.execute(
                """INSERT INTO uvc
                    (client_id, timestamp_millis, data) values (?, ?, ?)""",
                (
                    m.group(1),
                    int((msg.timestamp + TIME_CONSTANT) * 1000),
                    float(msg.payload),
                ),
            )
        elif msg.topic == MQTT_TOPIC_LOG:
            cursor.execute(
                """INSERT INTO session
                    (timestamp_millis, message) values (?, ?)""",
                (
                    int((msg.timestamp + TIME_CONSTANT) * 1000),
                    msg.payload.decode(encoding="UTF8"),
                ),
            )
        elif msg.topic == MQTT_TOPIC_ODOM_LOG:
            cursor.execute(
                """INSERT INTO odometry
                    (timestamp_millis, data) values (?, ?)""",
                (
                    int((msg.timestamp + TIME_CONSTANT) * 1000),
                    msg.payload.decode(encoding="UTF8"),
                ),
            )
    finally:
        MUTEX.release()


def create_tables(conn: crate.connection.Connection):
    cursor = conn.cursor()
    stmnt = """
    CREATE TABLE IF NOT EXISTS uvc (
        client_id text,
        timestamp_millis bigint,
        data double precision
    )
    """
    cursor.execute(stmnt)
    stmnt = """
    CREATE TABLE IF NOT EXISTS session (
        timestamp_millis bigint,
        message text
    )
    """
    cursor.execute(stmnt)
    stmnt = """
    CREATE TABLE IF NOT EXISTS odometry (
        timestamp_millis bigint,
        data text
    )
    """
    cursor.execute(stmnt)
    cursor.close()


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
    crate_conn = crate.connect(CRATE_HOST, username=CRATE_USERNAME)
    create_tables(crate_conn)
    mqtt_client.user_data_set(crate_conn.cursor())
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_forever()


if __name__ == "__main__":
    # HACK: Give CrateIO time to start
    time.sleep(10)
    main()
