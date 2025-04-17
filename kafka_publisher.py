from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

def start_kafka_producer(bootstrap_server_ip: str, logger) -> KafkaProducer:
    try:
        producer = KafkaProducer(bootstrap_servers = bootstrap_server_ip)
    except KafkaError as ke:
        logger.error("Error while trying to connect to Kafka broker: " + str(ke))
    return producer

def send_msg(producer: KafkaProducer, msg: list[str], logger):
    for item in msg:
        future = producer.send('logs.ssh', bytes(item, encoding='utf8'))
        try:
            metadata = future.get(timeout=10)
            logger.debug("Message sent to Kafka Sevrer: " + str(msg))
        except KafkaTimeoutError as ke:
            logger.error("KafkaError occurred: " + str(ke))