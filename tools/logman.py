import logging
import os
import gzip
from datetime import datetime
from tools.confman import get_conf

CONF = get_conf(sections=["logs"])

DEFAULT_DIR = "logs"

def get_logger(name, global_level=logging.INFO, file_level=logging.INFO, term_level=logging.DEBUG, save_dir=DEFAULT_DIR):
    logger = logging.getLogger(name)
    logger.setLevel(global_level)
    formatter = logging.Formatter(f"%(asctime)s - [%(name)s] - [%(levelname)s]:\t%(message)s")

    file_handler = logging.FileHandler(os.path.join("logs", f"{name}.log"))
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(term_level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("Logger aquired")
    return logger


def log_cleaner(logdir = DEFAULT_DIR):
    for logfile in os.listdir(logdir):
        filep = os.path.join(logdir, logfile)
        filet = logfile.split(".")[-1]
        if os.path.getsize(filep) >= CONF["max_raw_size"] and filet != "gz":
            with open(filep, "rb") as inf:
                with open(f"{filep}-{datetime.now().strftime(fmt='%Y%m%d%H%M%S')}.gz", "wb") as outf:
                    outf.write(gzip.compress(inf.read()))
        elif filet == "gz":
            pass
