import logging
import threading
import time

def start_container_handler(run_event: threading.Event, logger):
    """Manages the containers used to fake vulnerable services in restricted environments."""
    
    logger = logging.getLogger(__name__)
    logger.info('container_handler starting...')
    while(run_event.is_set()):
        # logger.info("container_handler running.")
        time.sleep(1)
