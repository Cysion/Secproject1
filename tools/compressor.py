import gzip
from logman import get_logger

def compress(path, logger = get_logger("compressor")):
    """compress the file at path to path.gz, returns 1 if successful, 0 if failed"""
    try:
        logger.debug("attempting to compress: " + path)
        with open(path) as compfile:
            with open(path + ".gz", "wb") as compedfile:
                compedfile.write(gzip.compress(compfile))
        
    except FileNotFoundError:
        logger.debug("File not found: " + path)
        return 0