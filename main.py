import signal
import threading
import container_handler
import connection_listener
import log_collector
import asyncio
import custom_formatter as cf
import time


def signal_handler(sig, frame):
    """
    Handles KeyboardInterrupt and stops threads execution."
    """
    logger.info('SIGINT received. Shutting down gracefully...')
    while run_event.is_set():
        run_event.clear()
        run_event.wait(1)
        logger.debug("Value of run_event: " + str(run_event))

def log_thread_exceptions(args):
    """
    Makes the program exit when a Thread raises an unhandled error.
    """
    logger.error("An exception occurred in a thread")
    logger.debug(args)
    run_event.clear()

def main():

    signal.signal(signal.SIGINT, signal_handler)
    logger.info('main Started')
    run_event.set()

    SSH_LOG_PATH = "log_test.txt"

    th_container_handler = threading.Thread(target=container_handler.start_container_handler, args=(run_event, logger, ))
    th_connection_listener = threading.Thread(target=connection_listener.start_connection_listener, args=(run_event, logger, ))

    # async runtinme for this thread
    th_ssh_log_collector = threading.Thread(target=asyncio.run, args=(log_collector.start_log_collector(run_event, SSH_LOG_PATH, logger), ))

    threads = [th_container_handler, th_connection_listener, th_ssh_log_collector]
    
    # handles exceptions from threads
    threading.excepthook = log_thread_exceptions
    try:
        for th in threads:
            th.start()
        try:
            while run_event.is_set():
                time.sleep(3)
        finally:
            logger.info('Waiting for threads to finish...')

            # at the end threads are joined to stop the program
            for th in threads:
                try:
                    th.join()
                except Exception as e:
                    logger.error("Exception raised from thread " + th + ": " + e)
            logger.info("All threads have stopped.")
    except Exception as e:
        logger.error('Exiting because of an unexpected error', e)

if __name__ == '__main__':
    logger = cf.CustomFormatter.init_logger()

    run_event = threading.Event()
    
    main()