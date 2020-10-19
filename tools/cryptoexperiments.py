from Crypto.PublicKey import RSA
import random
from os import urandom

def cysiofunc(x):
    bitties = random.getrandbits(8*x).to_bytes(x,"little")
    #print("x is: ", x, "\nbitties is: ",len(bitties))
    return bitties

def gen_keys(secret, randfuck=urandom):
    random.seed(secret) #<----- needs to be scrypted
    key = RSA.generate(2048, randfunc=randfuck)
    priv_key = key.export_key()
    pub_key = key.publickey().export_key()
    print("Priv key:\n", priv_key)
    print("\n\nPub key:\n", pub_key)

if __name__ == "__main__":
    cysiofunc = lambda x: random.getrandbits(8*x).to_bytes(x,"little")
    print("cysiofunc:")
    gen_keys("bonkyougotohornyjail", cysiofunc)
    print("urandom 1:")
    gen_keys("bonkyougotohornyjail")

