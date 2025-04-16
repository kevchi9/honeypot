from enum import Enum
from paho.mqtt import client as mqtt
import json
import logging

class Services(Enum):
    SSH = "/logs/ssh.log"
    FTP = "/logs/ftp.log"
    RDP = "/logs/rdp.log"
    WS = "/logs/apache.log"
    TEST = "log_test.txt"

class Topics(Enum):
    SSH = "logs/ssh"
    FTP = "logs/ftp"
    RDP = "logs/rdp"
    WS = "logs/apache"
    TEST = "log_test"

def get_service_from_log(log_path: str) -> Services:
    for item in Services:
        if item.value == log_path:
            return item
        
def get_topic_from_service(service: Services) -> Topics:
    for item in Topics:
        if service.name == item.name:
            return item

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

async def connect_and_send_to_broker(server_ip: str, port: int, log_path, logger: logging.Logger, msg: list[str]):
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

    service: Services = get_service_from_log(log_path)

    publish_msg(mqttc, msg, service, unacked_publish, logger)

    mqttc.loop_stop()
    mqttc.disconnect()

def start_client() -> mqtt.Client:
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "publisher_test", clean_session=True)
    return mqttc

def build_msg(client_id: bytes, msg: str, service: Services, logger: logging.Logger) -> str:
    """
    Creates a json structure with the `msg` parameter in the `payload` field.
    
    Returns a `str` representing the json object.
    """

    return json.dumps({"pulisher_id": client_id.decode("utf-8") , "payload": msg, "service": service.name})

def publish_msg(mqttc: mqtt.Client, msg: list[str], service: Services, unacked_publish: set, logger: logging.Logger):
    for item in msg:
        formatted_msg = build_msg(mqttc._client_id, item, service, logger)
        topic = get_topic_from_service(service)
        msg_info = mqttc.publish(topic.value, bytes(formatted_msg, encoding='utf8'), qos=0, retain=False)
        unacked_publish.add(msg_info.mid)
        logger.info("Message published to the broker: "+ item)