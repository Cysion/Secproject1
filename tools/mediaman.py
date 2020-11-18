from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import tools.crypto as crypto
import tools.confman as confman
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


def get_sha1(obj: IOBase) -> str:
    """A function to get sha1 in a memory efficient way. returns hexdigest of obj
    obj = io object to digest"""
    hashhold = hashlib.sha1()
    try:
        for chunk in iter(lambda: obj.read(4096), b""):
                hashhold.update(chunk)
        obj.seek(0)
    except AttributeError:
        hashhold.update(obj)
    return hashhold.hexdigest()



def save_file(key: bytes, clearfile: bytes, anonid, maxsize = None, upload_name = None, filetype_override = None, rootdir = CONF["media_base_dir"], exists_error=True, comp_level = 6, compress = True) -> tuple:
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

    if compress:
        clearfile = gzip.compress(clearfile, compresslevel=comp_level)

    #encrypt file and purge original
    encfile = crypto.aes_encrypt(key, clearfile)
    del clearfile
    #add header to file
    header = f"""---BEGIN HEADER---
filetype:{filetype_override or get_filetype(upload_name)}
crypto:AES{len(key)*8}bit
compression:gzip
orig_size:{orig_size}
half_key_hash:{get_sha1(key)}
---END HEADER---\n""".encode("ascii")
    encfile = header + encfile

    #hash file with header
    fullsig = get_sha1(encfile)
    #decide name
    namesig = get_sha1(anonid)
    newname = f"{namesig}/{fullsig}"
    save_path = f"{rootdir}/{newname}"

    #check if file already saved
    if default_storage.exists(save_path) and exists_error:
        raise FileExistsError

    #save file
    default_storage.save(save_path, ContentFile(encfile))
    return (newname, default_storage.size(save_path))


def open_file(key:bytes, filename:str, rootdir = CONF["media_base_dir"], decompress=True, header_check=True) -> tuple:
    """opens the file at filename with key to decrypt. checks both checksums and raises RuntimeError if any fails
    if the checksums clear, a tuple of the file header(str) and the file data(bytes) is returned
    root_dir = the root of all media storage sent to the default_storage class
    decompress = return decompressed file. faster if only to be re-encrypted
    """
    #open the file
    infile = default_storage.open(f"{rootdir}/{filename}")
    #verify full file integrity
    checksum = filename.split("/")[-1]
    fullsum = get_sha1(infile)
    if checksum != fullsum:
        raise RuntimeError("Checksum for file not verified!")
    infile.seek(0)
    #extract header
    opened = infile.read()
    header, opened = header_and_file(infile, bytesio=False)
    infile.close()
    checkfor = {
        "half_key_hash":get_sha1(key)
    }
    if header_check:
        for line in header.split("\n"):
            splitline = line.split(":")
            if splitline[0] in checkfor:
                if splitline[1] != checkfor[splitline[0]]:
                    raise RuntimeError(f"{splitline[0]} failed to check out for file: {filename}")
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
    ptr = infile.tell()
    #add the rest of the file to retfile
    if not only_header:
        if bytesio:
            retfile = infile
        else:
            retfile = infile.read()
            infile.close()

    return (header.decode("ascii"), None if only_header else retfile)


def delete_file(filename:str, rootdir = CONF["media_base_dir"], exists_error=False):
    """Permanently deletes filename from storage
    filename = name of file to be deleted
    rootdir = the root of all media storage sent to the default_storage class
    exists_error = throw FileNotFoundError if filename doesnt exist"""
    if default_storage.exists(f"{rootdir}/{filename}"):
        default_storage.delete(f"{rootdir}/{filename}")
    elif exists_error:
        raise FileNotFoundError
    else:
        return


def reencrypt_user(anonid, old_key, new_key = crypto.gen_aes(256), rootdir = CONF["media_base_dir"]):
    """reencrypts all files in anonid directory with new_key. the new key is returned.
    anonid = anonid of the directory whose files are to be reencrypted
    old_key = key currently used to encrypt files
    new_key = the key to be used for encryption (if left empty will be generated)
    rootdir = the root of all media storage sent to the default_storage class
    """

    dirname = get_sha1(anonid)
    files = default_storage.listdir(f"{rootdir}/{dirname}")[1]
    for file in files:
        fullpath = f"{dirname}/{file}"
        filedata = open_file(old_key, fullpath, decompress=False, header_check=False)[1]
        delete_file(fullpath, exists_error=True)
        save_file(new_key, filedata, anonid, compress=False)
    return new_key


def open_all_files(key:bytes, anonid, rootdir = CONF["media_base_dir"], decompress=True):
    """returns a list of tuples containing the headers and data of an entire user directory.
    Very memory inefficient
    key = symkey for decryption
    anonid = anonid of the directory whose files are to be fetched
    rootdir = the root of all media storage sent to the default_storage class"""
    files_data = []
    dirname = get_sha1(anonid)
    files = default_storage.listdir(f"{rootdir}/{dirname}")[1]
    for file in files:
        fullpath = f"{dirname}/{file}"
        files_data.append(open_file(key, fullpath, rootdir=rootdir, decompress=decompress))
    return files_data


def delete_all_files(anonid, rootdir = CONF["media_base_dir"]):
    """used to IRREVERSIBLY clear all data from a user. will completely purse the directory of given anonid
    anonid = anonid of the directory to be purged
    rootdir = the root of all media storage sent to the default_storage class"""
    files_data = []
    dirname = get_sha1(anonid)
    files = default_storage.listdir(f"{rootdir}/{dirname}")[1]
    for file in files:
        fullpath = f"{dirname}/{file}"
        delete_file(fullpath)


if __name__ == "__main__":
    import django.core.files.storage
    django.core.files.storage.settings.configure()
    key = crypto.gen_aes(256)
    anonid = crypto.gen_anon_id(1234,"longbirthdaystring")
    delete_all_files(anonid)
    #test encryption and decryption
    with open("testdata/testimg.png", "rb") as inf:
        sf = save_file(key, inf.read(), anonid)
    header, outfile = open_file(key, sf[0])
    with open("test.png", "wb") as outf:
        outf.write(outfile)
    delete_file(sf[0])
    #test re-encryption
    newkey = crypto.gen_aes(256)
    #fill with sloth

    #generate encrypted sloths
    with open("testdata/testimg.png", "rb") as inf:
        dat = inf.read()
        for i in range(9):
            save_file(key, dat, anonid, exists_error=False)

    reencrypt_user(anonid, key, newkey)
    try:
        open_all_files(key, anonid)
    except RuntimeError:
        print("WRONG KEY DINGUS!")
    i = 0
    all_data = open_all_files(newkey, anonid)
    for file_data in all_data:
        i += 1
        with open(f"test{i}.png", "wb") as auss:
            auss.write(file_data[1])

    input()
    delete_all_files(anonid)
