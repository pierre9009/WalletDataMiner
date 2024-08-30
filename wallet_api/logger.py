# logger.py
import logging
from colorama import Fore, Style, init

# Initialisation de colorama pour Windows
init(autoreset=True)

class ColoredLogger(logging.Logger):
    COLOR_MAP = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def __init__(self, name):
        super().__init__(name)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        color = self.COLOR_MAP.get(logging.getLevelName(level), '')
        msg = f"{color}{msg}{Style.RESET_ALL}"
        super()._log(level, msg, args, exc_info, extra)

def setup_logger():
    logging.setLoggerClass(ColoredLogger)
    
    # Create the root logger and set the basic configuration
    logger = logging.getLogger()
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)  # Set root logger level to INFO

    # Configure Scrapy and other loggers
    scrapy_loggers = [
        "scrapy",
        "scrapy.core",
        "scrapy.utils",
        "scrapy.spidermw",
        "scrapy.middleware",
        "scrapy.extensions",
        "scrapy.downloader",
        "scrapy.scheduler",
        "scrapy.crawler",
        "scrapy.utils.spider",
        "scrapy.core.downloader.handlers",
        "scrapy.core.downloader"
    ]

    for module in scrapy_loggers:
        logging.getLogger(module).setLevel(logging.ERROR)

    # Configure other loggers if necessary
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    logging.getLogger("peewee").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

    return logging.getLogger(__name__)
def print_loggers():
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        print(f"Logger: {name}")
        print(f"  Level: {logger.level}")
        for handler in logger.handlers:
            print(f"  Handler: {handler}")
        print()