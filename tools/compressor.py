import gzip

def compress(path, addtime):
    """compress the file at path to path.gz, returns path.gz if successful, 0 if failed"""
    try:
        with open(path) as compfile:
            with open(path + ".gz", "wb") as compedfile:
                compedfile.write(gzip.compress(compfile))

    except FileNotFoundError:
        return 0

    else:
        return path + ".gz"