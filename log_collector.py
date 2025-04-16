import mqtt_publisher
import threading
import time
import os
from collections import Counter
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

async def start_log_collector(run_event: threading.Event, log_path, logger):
    """
    Listens to incoming connection from open sockets and dummy services.
    
    If the file in `LOG_PATH` does not exist the thread raises a `LogFileNotFound` that make the program quit gracefully.
    """

    logger.debug('Log Collector starting...')
    # procuder = start_kafka_producer('10.0.21.183:29092', logger)
    # logger.debug("Succesfully connected to Kafka Server.")
    try:
        last_modify: float = get_last_modify_time(log_path, logger)
        last_logs: list[str] = read_logs(log_path, logger)
    except FileNotFoundError as e:
        raise

    # loop until the thread is killed
    logger.info("Log Collector running.") 
    while(run_event.is_set()):
        # logger.debug(run_event)

        # if log file contains new lines, it sends them to mqtt broker
        if check_if_modified(last_modify, log_path, logger):
            last_modify = get_last_modify_time(log_path, logger)
            logger.debug("Log file has been modified.")

            new_raw_log = read_logs(log_path, logger)
            new_log = list(Counter(new_raw_log) - Counter(last_logs))
            last_logs = new_raw_log
            
            print(new_log)
            
            await mqtt_publisher.connect_and_send_to_broker( "10.0.21.183", 1883, log_path, logger, new_log)
            
            # send_msg(procuder, new_log, logger)
            

        time.sleep(3)
            

def check_if_modified(last_modify, log_path, logger) -> bool:
    """
    Checks if the file specifed in `LOG_PATH` parameter has been modified since `last_modify`.
    
    Returns an error if the specified file does not exist.
    """
    try:
        return get_last_modify_time(log_path, logger) != last_modify
    except FileNotFoundError as e:
        logger.error("Log file not found. Check the file path and restart the program.")
        logger.debug(e)
        raise


def read_logs(log_path, logger) -> list[str]:
    """
    Reads and returns the content of the specifed `LOG_PATH`.
    
    Returns an error if the specified file does not exist.
    """
    try:
        with open(log_path, "r") as f:
           return f.readlines()
    except FileNotFoundError as e:
        logger.error("Log file not found. Check the file path and restart the program.")
        logger.debug(e)
        raise

def get_last_modify_time(file, logger):
    """
    Gets and returns the last time the specified `file` has been modified.

    If the file does not exist the thread raises an exception that make the program quit gracefully.
    """
    try:
        return os.stat(file).st_mtime
    except FileNotFoundError as e:
        logger.error("Log file not found. Check the file path and restart the program.")
        logger.debug(e)
        raise