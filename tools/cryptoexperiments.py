from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import random
from os import urandom
import hashlib


def gen_rsa(secret):
    assert len(secret) >= 128
    det_getrandbytes = lambda x: random.getrandbits(8*x).to_bytes(x,"little")
    random.seed(secret) #<----- needs to be scrypted
    key = RSA.generate(2048, randfunc=det_getrandbytes)
    return key


def secret_scrambler(passw: str, salt: int)->bytes:
    return hashlib.scrypt(passw.encode("utf-8"),salt=salt.to_bytes(24,"little"),dklen=128,n=2,r=4,p=1)


def qdigest(longstr):
    sha1 = hashlib.sha1()
    sha1.update(longstr)
    return sha1.hexdigest()


def aes_encrypt(aes_key, data):
    pass

def aes_decrypt(aes_key, data):
    
    
def rsa_encrypt(pub_key, data):
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(pub_key))
    return cipher_rsa.encrypt(data)



def rsa_decrypt(priv_key, data):
    pass


if __name__ == "__main__":
    print("create a fake user!")
    passw = input("passw: ")
    uid = int(input("uid (salt): "))
    print("every key in this demo is hashed with sha1 for convenience")
    print("passw is hashed with scrypt. this is then used to generate rsa- and aes keys")
    scram = secret_scrambler(passw,uid)
    print("random will be seeded with: ", qdigest(scram), " for rsa keygen")
    key = gen_rsa(scram)
    print("priv key: ",qdigest(ey.export_key()),"\npub_key: ",qdigest(key.publickey().export_key()))
    print("write data that is encrypted with the users key!")
    data = input("data: ")
    cdata = rsa_encrypt(key.publickey().export_key(), data)
    print("data: ", qdigest(data))
    print("encrypted data: ", qdigest(cdata))


