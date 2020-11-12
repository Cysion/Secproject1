from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import crypto
import confman
import hashlib
from io import BytesIO, IOBase
import gzip

CONF = confman.get_conf()["media"]

def get_filetype(filename: str) -> str:
    """simple function that handles exceptions thrown by trying to read the filetype from filename
    returns str
    filname = filename to extract type from"""
    filetype = ""
    try:
        filetype = filename.split(".")[-1]
    except:
        filetype = "Unknown"
    return filetype


def save_file(key: bytes, clearfile: bytes, anonid, maxsize = None, upload_name = None, filetype_override = None, rootdir = CONF["media_base_dir"], exists_error=True, comp_level = 6) -> tuple:
    """A function to save files into the default system. default method is to save files in rootdir/anonid/filesha1
    The function encrypts the file and prepends a header with information about the file. The header starts with ---BEGIN HEADER---
    and ends with ---END HEADER---. it also compresses the file with gzip compression before encrypting
    returns tuple of (filename, filesize)
    key = the encryption key to be used for AES encryption
    clearfile = the file to be compressed, encrypted and saved
    anonid = the anonymous id of the user that wishes to save the file
    maxsize = max allowed size of the input file, set to None or 0 for unlimited. raises RuntimeError if exceeded
    upload_name = the name of the file that is uploaded. only used to determine filetype
    filetype_override = overrides upload name for filetype setting
    root_dir = the root of all media storage sent to the default_storage class
    exists_error = throw FileExistsException if the file already exists
    comp_level = how much compression is to be used for gzip. larger number means smaller file but slower
    """
    #compress file
    orig_size = len(clearfile)
    if maxsize:
        if orig_size > maxsize:
            raise RuntimeError("File too large!")

    compfile = gzip.compress(clearfile, compresslevel=comp_level)
    del clearfile

    #encrypt file and purge original
    encfile = BytesIO(crypto.aes_encrypt(key, compfile))
    del compfile

    #add header to file
    datasig = hashlib.sha1()
    for i in range(0, -1, 1024):
        datasig.update(encfile.read(1024))
    header = f"""---BEGIN HEADER---
filetype:{filetype_override or get_filetype(upload_name)}
checksumsha1:{datasig.hexdigest()}
crypto:AES{len(key)*8}bit
compression:gzip
orig_size:{orig_size}
---END HEADER---\n""".encode("ascii")
    encfile.seek(0)
    encfile.write(header)
    encfile.seek(0)

    #hash file with header
    fullsig = hashlib.sha1()
    for i in range(0, -1, 1024):
        fullsig.update(encfile.read(1024))
    
    #decide name
    namesig = hashlib.sha1()
    namesig.update(anonid)
    newname = f"{namesig.hexdigest()}/{fullsig.hexdigest()}"
    save_path = f"{rootdir}/{newname}"

    #check if file already saved
    if default_storage.exists(save_path) and exists_error:
        raise FileExistsError
    
    #save file
    default_storage.save(save_path, ContentFile(encfile.read(-1)))
    return (newname, default_storage.size(save_path))


def open_file(key:bytes, filename:str, rootdir = CONF["media_base_dir"], decompress=True) -> tuple:
    """opens the file at filename with key to decrypt. checks both checksums and raises RuntimeError if any fails
    if the checksums clear, a tuple of the file header(str) and the file data(bytes) is returned
    root_dir = the root of all media storage sent to the default_storage class
    decompress = return decompressed file. faster if only to be re-encrypted
    """
    
    #open the file
    infile = default_storage.open(f"{rootdir}/{filename}")
    
    #verify full file integrity
    checksum = filename.split("/")[-1]
    fullsum = hashlib.sha1()
    for i in range(0, -1, 1024):
        fullsum.update(infile.read(1024))
    if checksum != fullsum.hexdigest():
        raise RuntimeError("checksum for full file not verified!")

    #extract header
    header, opened = header_and_file(infile, bytesio=False)
    infile.close()
    #verify partial file integrity
    partsum = hashlib.sha1()
    for i in range(0, -1, 1024):
        partsum.update(infile.read(1024))
    for line in header.split("\n"):
        splitline = line.split(":")
        if splitline[0] == "checksumsha1":
            if splitline[1] != partsum.hexdigest():
                raise RuntimeError("checksum for encrypted file not verified!")
    
    #decrypt and decompress file
    outfile = crypto.aes_decrypt(key, opened)
    if decompress:
        outfile = gzip.decompress(outfile)
    return (header, outfile)


def header_file(filename, rootdir = CONF["media_base_dir"], exists_error=True) -> str:
    """retrieve only the header of the file. fast function, only reads until end of header
    """
    return header_and_file(default_storage.open(f"{rootdir}/{filename}"), only_header=True)[0]


def header_and_file(infile:IOBase, bytesio=False, only_header=False) -> tuple:
    """opens filename and splits the header from the file. returns tuple of header(str) and file(bytes)
    file = file to split
    rootdir = the root of all media storage sent to the default_storage class
    bytesio = return file in bytesio mode instead of as bytes
    only_header = discard the file after reading and return a tuple of the header(str) and None
    """
    infile.seek(0)
    header = b""
    addnext = b""

    #iterate until the end of the header
    while addnext != b"---END HEADER---\n":
        addnext = infile.readline()
        header += addnext
    
    #add the rest of the file to retfile
    if not only_header:
        if bytesio:
            retfile = infile
        else:
            retfile = infile.read()
            infile.close()
        
    return (header.decode("ascii"), None if only_header else retfile)


def delete_file(filename:str, rootdir = CONF["media_base_dir"], exists_error=True):
    pass

    
def reencrypt_user():
    pass


if __name__ == "__main__":
    import django.core.files.storage
    django.core.files.storage.settings.configure()
    key = crypto.gen_aes(256)
    with open("testdata/testimg.png", "rb") as inf:
        sf = save_file(key, inf.read(), crypto.gen_anon_id(1234,"longbirthdaystring"), exists_error=False)
    header, outfile= open_file(key, sf[0])
    with open("test", "wb") as outf:
        outfile.write(outfile)


