from paho.mqtt import client as mqtt
import logging

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("config")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid, reason_code, properties):
    try:
        userdata.remove(mid)
    except KeyError as e:
        raise e

def on_log(client, userdata, paho_log_level, messages, logger):
    if paho_log_level == mqtt.LogLevel.MQTT_LOG_ERR:
        logger.error(messages)

async def connect_and_send_to_broker(server_ip: str, port: int, logger: logging.Logger, msg: list[str]):
    """
    Starts mqtt client and connects to the broker. Once connected for every line in `msg`, 
    publishes a message on the mqtt broker.
    """

    # initial configuration for the client
    unacked_publish = set()
    mqttc = start_client()
    mqttc.on_publish = on_publish
    mqttc.user_data_set(unacked_publish)
    mqttc.connect(server_ip, port)
    mqttc.enable_logger()

    # loop is used to handle the connection between client and broker
    # also reconnect automatically if connection to the broker is interrupted
    mqttc.loop_start()

    publish_msg(mqttc, msg, unacked_publish, logger)

    mqttc.loop_stop()
    mqttc.disconnect()

def start_client() -> mqtt.Client:
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    return mqttc

def publish_msg(mqttc: mqtt.Client, msg: list[str], unacked_publish: set, logger):
    for item in msg:
        msg_info = mqttc.publish("logs/ssh", bytes(item, encoding='utf8'), qos=1)
        unacked_publish.add(msg_info.mid)
        logger.info("Message published to the broker: "+ item)