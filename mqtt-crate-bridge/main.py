# TODO: Configuration parameters should be passed as environment variables
# https://pypi.org/project/envparse/

import re
import time

import crate.client as crate
import paho.mqtt.client as mqtt

MQTT_HOST = 'mqtt'
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC_BASE = 'tas/hrt/uvc'
MQTT_TOPIC_REGEX = re.compile(f'^{MQTT_TOPIC_BASE}/([^/]*)$')

CRATE_HOST = 'http://crate:4200'
CRATE_USERNAME = 'crate'

TIME_CONSTANT = time.time() - time.monotonic()


def on_connect(client, userdata, flags, rc):
    print(f'MQTT-Crate Bridge connected (result code: {rc})')
    client.subscribe(f'{MQTT_TOPIC_BASE}/+')


def on_message(client, cursor: crate.connection.Cursor, msg: mqtt.MQTTMessage):
    m = MQTT_TOPIC_REGEX.match(msg.topic)
    if not m:
        return
    cursor.execute("""INSERT INTO uvc_sensor_readings
            (client_id, timestamp_millis, data) values (?, ?, ?)""",
                   (m.group(1),
                    int((msg.timestamp + TIME_CONSTANT) * 1000),
                    float(msg.payload)))


def create_table(conn: crate.connection.Connection):
    cursor = conn.cursor()
    stmnt = """
    CREATE TABLE IF NOT EXISTS uvc_sensor_readings (
        client_id text,
        timestamp_millis bigint,
        data double precision
    )
    """
    cursor.execute(stmnt)
    cursor.close()


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
    crate_conn = crate.connect(CRATE_HOST, username=CRATE_USERNAME)
    create_table(crate_conn)
    mqtt_client.user_data_set(crate_conn.cursor())
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_forever()


if __name__ == '__main__':
    # HACK: Give CrateIO time to start
    time.sleep(10)
    main()
