import mqtt_publisher
import log_parser
from log_parser import CowrieSearchStrings as CSS
import threading
import time
import os
from collections import Counter

async def start_log_collector(run_event: threading.Event, log_path, logger):
    """
    Listens to incoming connection from open sockets and dummy services.
    
    If the file in `LOG_PATH` does not exist the thread raises a `LogFileNotFound` that make the program quit gracefully.
    """

    logger.debug('Log Collector starting...')
        
    try:
        last_modify: float = get_last_modify_time(log_path, logger)
        previous_logs: list[str] = read_logs(log_path, logger)
    except FileNotFoundError as e:
        raise

    # loop until the thread is killed
    logger.info("Log Collector running.") 
    while(run_event.is_set()):

        # if log file contains new lines, it sends them to mqtt broker
        if check_if_modified(last_modify, log_path, logger):
            last_modify = get_last_modify_time(log_path, logger)
            logger.debug("Log file has been modified.")

            recent_logs = read_logs(log_path, logger)
            new_raw_logs = list(Counter(recent_logs) - Counter(previous_logs))
            previous_logs = recent_logs
            
            # search_strings is a list of SearchStrings, an enumerator defined in log_parser.py containing the string patterns of cowrie logs
            search_strings = [CSS.COWRIE_SSH_CMD, CSS.COWRIE_SSH_LOGIN]
            json_logs: list[str] = log_parser.logs_into_json(new_raw_logs, search_strings, logger)


            await mqtt_publisher.connect_and_send_to_broker( "10.0.21.183", 1883, log_path, logger, json_logs)
            
            # send_msg(procuder, new_raw_logs, logger) 

        time.sleep(3)
            

def check_if_modified(last_modify, log_path, logger) -> bool:
    """
    Checks if the file specifed in `LOG_PATH` parameter has been modified since `last_modify`.
    
    ### Returns 
    an error if the specified file does not exist.
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
    
    ### Returns 
    an error if the specified file does not exist.
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