import crypto
import gzip
import itertools
import time
from hashlib import sha1

def unique_combiner(list_1, list_2):
    unique_combinations = [] 
    for i1 in list_1:
        for i2 in list_2:
            unique_combinations.append((i1, i2))
    return unique_combinations


def testgen():
    aes_keysizes = [128, 256]
    rsa_keysizes = [1024, 2048, 4096]
    files = ["1M", "10M", "100M"]
    rsaable = [crypto.gen_aes(128), crypto.gen_aes(256)]
    clevels = range(1, 10)

    rsa_runs = unique_combiner(rsa_keysizes, unique_combiner(rsaable, clevels))
    aes_runs = unique_combiner(aes_keysizes, unique_combiner(files, clevels))
    return rsa_runs, aes_runs


def runtest(enc, dec, enc_key, dec_key, run):
    results = {
        "specs":f"{run[0]} bit key\ndata: {run[1][0]}\nlevel {run[1][1]} compression",
        "encrypt":None,
        "decrypt":None,
        "hashes":[]}
    h1, h2, h3 = sha1(), sha1(), sha1()

    baseblob = None
    try:
        with open(f"testdata/{run[1][0]}.blob", "rb") as file:
            baseblob = file.read()
    except FileNotFoundError:
        baseblob = run[1][0]
    
    h1.update(baseblob)
    results["hashes"].append(h1.digest())
    encstarttime = time.time()
    encblob = enc(enc_key, gzip.compress(baseblob, run[1][1]))
    encendtime = time.time()
    h2.update(encblob)
    results["hashes"].append(h2.digest())

    decstarttime = time.time()
    decblob = gzip.decompress(dec(dec_key, encblob))
    decendtime = time.time()
    h3.update(decblob)
    results["hashes"].append(h3.digest())

    results["encrypt"] = encendtime - encstarttime 
    results["decrypt"] = decendtime - decstarttime
    return results


def benchaes(runs):
    print("testing AES")
    times = []
    i = 0
    for run in runs:
        i += 1
        print("test ", i, " of ", len(runs))
        key = crypto.gen_aes(run[0])
        times.append(runtest(crypto.aes_encrypt, crypto.aes_decrypt, key, key, run))
    return times


def benchrsa(runs):
    times = []
    i = 0
    for run in runs:
        i += 1
        print("test ", i, " of ", len(runs))
        key = crypto.gen_rsa(crypto.secret_scrambler("benchmark", 1010), bits=run[0])
        times.append(runtest(crypto.rsa_encrypt, crypto.rsa_decrypt, key.publickey().export_key(), key.export_key(), run))
    return times



def fancy_display(times):
    for time in times:
        print("-"*30)
        for key in time:
            print(key, " : ", time[key])
        print("-"*30)
    print("\n\n")


def main():
    print("starting tests")
    rsa_runs, aes_runs = testgen()
    
    times_aes = benchaes(aes_runs)
    #print(times_aes)
    print("aes_times")
    fancy_display(times_aes)

    times_rsa = benchrsa(rsa_runs)
    #print(times_rsa)
    print("rsa times")
    fancy_display(times_rsa)




if __name__ == "__main__":
    main()