import logging
import os


DEFAULT_DIR = "logs"

def get_logger(name, global_level=logging.INFO, file_level=logging.INFO, term_level=logging.DEBUG, save_dir=DEFAULT_DIR):
    logger = logging.getLogger(loggerName)
    logger.setLevel(global_level)
    formatter = logging.Formatter(f"%(asctime)s - [%(name)s] - [%(levelname)s]:\t%(message)s")

    file_handler = logging.FileHandler(os.path.join("logs", f"{loggerName}.log"))
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(term_level)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    return logger
    
def log_cleaner():
