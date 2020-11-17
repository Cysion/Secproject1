from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import random
from os import urandom
import hashlib
from confman import get_conf

def gen_rsa(secret:bytes, bits=2048) -> RSA.RsaKey:
    """DETERMINISTICALLY generates and returns an rsa key pair from the seed "secret"
    secret = seed for psrng. needs to be 128 bytes or longer. Any type accepted by
    random.seed will function. bytes strong preference for speed.
    bits = how large key size to use, any larger than default (2048) results in long-term
    database issues.
    """
    assert len(secret) >= 128
    det_getrandbytes = lambda x: random.getrandbits(8*x).to_bytes(x,"little")
    random.seed(secret) #<----- needs to be scrypted
    key = RSA.generate(bits, randfunc=det_getrandbytes)
    return key


def secret_scrambler(passw: str, salt: int, blen=128)->bytes:
    """Digests and returns a scrypt hash from passw and salt.
    passw = string with password from user
    salt = int comprised of pre-determined numbers (uid+rng number)
    blen = how many bytes ought the return value me, defaults to 128
    """
    return hashlib.scrypt(passw.encode("utf-8"),salt=salt.to_bytes(24,"little"),dklen=blen,n=2,r=4,p=1)


def qdigest(longstr):
    """wrapper for sha1 hexdigest. returns hash of longstr
    """
    sha1 = hashlib.sha1()
    sha1.update(longstr)
    return sha1.hexdigest()


def rsa_encrypt(pub_key:bytes, data:bytes) -> bytes:
    """encrypts data with pub_key. warning: slower than using symcrypto
    pub_key = rsa public key in str form. is imported by RSA.import_key()
    data = data to be encrypted
    """
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(pub_key))
    return cipher_rsa.encrypt(data)


def rsa_encrypt_long(pub_key:bytes, data) -> bytes:
    """Used to encrypt bigger datablobs with RSA. it splits the data in chunks of 
    180 bytes and encrypts them piecemeal then concatenates the result
    pub_key = rsa public key in str form. is imported by RSA.import_key()
    data = data to be encrypted"""
    cryptogram = b""
    for i in range(0, len(data), 180):
        cryptogram += rsa_encrypt(pub_key, data[i:i+180])
    return cryptogram
    #return b"".join([rsa_encrypt(pub_key, data[i:i+180].encode("utf-8")) for i in range(0, len(data), 180)])


def rsa_decrypt_long(priv_key:bytes, data) -> bytes:
    """Used to decrypt bigger datablobs with RSA. it splits the data in chunks of 
    256 bytes and decrypts them piecemeal then concatenates the result
    pub_key = rsa public key in str form. is imported by RSA.public_key.import_key()
    data = data to be encrypted"""
    plain_text = b""
    for i in range(0, len(data), 256):
        plain_text += rsa_decrypt(priv_key, data[i:i+256])
    return plain_text
    #return b"".join([rsa_decrypt(priv_key, text[i:i+256].encode("utf-8")) for i in range(0, len(data), 256)])


def rsa_decrypt(priv_key:bytes, data) -> bytes:
    """decrypts data with priv_key. warning: slower than using symcrypto
    priv_key = rsa private key in str form. is imported by RSA.import_key()
    data = data to be encrypted
    """
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(priv_key))
    return cipher_rsa.decrypt(data)


def gen_anon_id(uid: int, birthday: str, blen=256):
    """generates anonymous one-way id from uid and birthday.
    uid - user identity direct from database. used as salt
    """
    return hashlib.scrypt(birthday.encode("utf-8"),salt=uid.to_bytes(24,"little"),dklen=blen,n=2,r=4,p=1)


def gen_aes(keysize=128) -> bytes:
    """uses os urandom to generate a keysize-bit key (defaults to 128 bit). returns keysize bits
    binary object
    keysize = size of key to be generated, must be divisible by 8"""
    assert not keysize%8
    return urandom(keysize//8)


def aes_encrypt(sym_key:bytes, data) -> bytes:
    """simple wrapper function that encrypts data with aes
    returns object where the first 16 bytes is nonce, next 16 is tag, rest is ciphertext
    sym_key = key to use for encryption. must be bytes-like.
    data = data to be encrypted. bytes like preferred"""
    cipher = AES.new(sym_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    del data
    return b''.join([cipher.nonce, tag, ciphertext])


def aes_decrypt(sym_key:bytes, data) -> bytes:
    """simple wrapper function that decrypts data with aes
    uses structure left by aes_encrypt to read cleartext from nonce, tag and cipher. returns cleartext
    sym_key = key to use for encryption. must be bytes-like.
    data = data to be decrypted. bytes like preferred"""
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(sym_key, AES.MODE_EAX, nonce)
    cleartext = cipher.decrypt_and_verify(ciphertext, tag)
    return cleartext


if __name__ == "__main__":

    #WHAT FOLLOWS IS A USAGE DEMO FOR ABOVE FUNCTIONS
    import json
    sections = (0,0,0,0,0,0,1)
    print("this is a short presentation of the crypro functions for this project")
    if sections[0]:
        print("create a fake user!")
        uid = int(input("uid (salt): "))
        passw = input("passw: ")
        print("every key in this demo is hashed with sha1 for convenience")
        print("passw is hashed with scrypt. this is then used to generate rsa- and aes keys")
        scram = secret_scrambler(passw,uid)
        print("random will be seeded with: ", qdigest(scram), " for rsa keygen")
        key = gen_rsa(scram)
        print("priv key: ",qdigest(key.export_key()),"\npub_key: ",qdigest(key.publickey().export_key()))
        print("len of real priv key: ", len(key.export_key()),"len of real pub key: ", len(key.publickey().export_key()))
    if sections[1]:
        print("now we will make a mock-up user entry file")
        with open("user.txt", "w") as userfile:
            userdict = {
                "uid":str(uid),
                "pub_key":str(key.publickey().export_key()),
            }
            json.dump(userdict,userfile,indent=4)
        print("user mock up done in user.txt")
    if sections[2]:
        print("write data that is encrypted with the users key!")
        data = input("data: ").encode("utf-8")
        cdata = rsa_encrypt(key.publickey().export_key(), data)
        ddata = rsa_decrypt(key.export_key(), cdata)
        print("data: ", qdigest(data))
        print("encrypted data: ", qdigest(cdata))
        print("decrypted data: ", qdigest(ddata))
        print("decrypted data (real): ", ddata.decode("utf-8"))
    if sections[3]:
        print("now we will try to authenticate as the previously entered user from userfile")
        ud = {}
        with open("user.txt") as uf:
            ud = json.load(uf)
        neuid = input("uid: ")
        assert neuid == ud["uid"]
        passw = input("passw: ")
        keys = gen_rsa(secret_scrambler(passw, int(neuid)))
        if str(keys.publickey().export_key()) == ud["pub_key"]:
            print(f"you are {neuid}")
        else:
            print(f"you are not {neuid}")
    if sections[4]:
        print("now we encrypt and decrypt with aes key")
        key = gen_aes(128)
        print("your key is ", key)
        print("the string 'testing' will be encrypted with the key")
        blob = aes_encrypt(key, "testing".encode("utf-8"))
        print("the blob is ", blob)
        dec = aes_decrypt(key, blob)
        print("decrypted is ", dec.decode("utf-8"))
    if sections[5]:
        text="lång jävla sträng!"
        for i in range(1600):
            text += "i"
        cryptogram = rsa_encrypt_long(key.publickey().export_key(), text.encode("utf-8"))
        text2 = rsa_decrypt_long(key.export_key(), cryptogram).decode("utf-8")
        
        assert text==text2
    if sections[6]:
        #lets test deterministic encryption of data
        data = b":)"*80
        keys = gen_rsa(secret_scrambler("fungus",1337))
        ciphertext = rsa_encrypt(keys.publickey().export_key(), data)
        ciphers = []
        for i in range(1000):
            print(i)
            ciphers.append(rsa_encrypt(keys.publickey().export_key(), data))
        assert ciphertext in ciphers