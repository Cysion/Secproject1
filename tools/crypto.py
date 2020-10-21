from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import random
from os import urandom
import hashlib


def gen_rsa(secret) -> RSA.RsaKey:
    """DETERMINISTICALLY generates and returns an rsa key pair from the seed "secret"
    secret = seed for psrng. needs to be 128 bytes or longer. Any type accepted by
    random.seed will function. bytes preferred.
    """
    assert len(secret) >= 128
    det_getrandbytes = lambda x: random.getrandbits(8*x).to_bytes(x,"little")
    random.seed(secret) #<----- needs to be scrypted
    key = RSA.generate(2048, randfunc=det_getrandbytes)
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


def rsa_encrypt(pub_key, data):
    """encrypts data with pub_key. warning: slower than using symcrypto
    pub_key = rsa public key in str form. is imported by RSA.import_key()
    data = data to be encrypted
    """
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(pub_key))
    return cipher_rsa.encrypt(data)


def rsa_decrypt(priv_key, data):
    """decrypts data with priv_key. warning: slower than using symcrypto
    priv_key = rsa private key in str form. is imported by RSA.import_key()
    data = data to be encrypted
    """
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(priv_key))
    return cipher_rsa.decrypt(data)

if __name__ == "__main__":
    import json
    sections = (1,1,1,1)
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

        



