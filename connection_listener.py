import logging
import threading
import time

def start_connection_listener(run_event: threading.Event, logger):
    """Listens to incoming connection from open sockets and dummy services."""
    
    logger = logging.getLogger(__name__)
    logger.info('connection_listener starting...')
    while(run_event.is_set()):
        # logger.info("connection_listener running.")
        time.sleep(1)