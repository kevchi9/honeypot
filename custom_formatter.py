import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    green = "\x1b[32;20m"
    blue = "\x1b[36;20m"
    bold_green = "\x1b[32;1m"
    bold_blue = "\x1b[36;1m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    p1_format = "%(asctime)s"
    p2_format = "%(message)s [%(filename)s:%(lineno)d]"
    
    FORMATS = {
        logging.DEBUG: blue + p1_format + bold_blue + " |  %(levelname)s  | " + reset + blue + p2_format + reset,
        logging.INFO: green + p1_format + bold_green + " |  %(levelname)s   | " + reset + green + p2_format + reset,
        logging.WARNING: yellow + p1_format + yellow + " | %(levelname)s | " + reset + yellow + p2_format + reset,
        logging.ERROR: red + p1_format + bold_red + " |  %(levelname)s  | " + reset + red + p2_format + reset,
        logging.CRITICAL: bold_red + p1_format + " | %(levelname)s| " + p2_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
    def init_logger() -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)
        return logger