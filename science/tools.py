from datetime import datetime
import time
import os
import hashlib
from tools.confman import get_conf
from tools.logman import get_logger

from science.models import ResearchData


ID_DESC={
    "PF":"Anonymous user profile",
    "g2":"page click",
    "g1":"page enter",
    "g3":"page leave",
    "u1":"user logon",
    "u2":"user logoff",
    "u3":"profile edit",
    "i1":"howto access",
    "r1":"share with",
    "p1":"contact add",
    "p2":"contact use",
    "p3":"step open",
    "s1":"save.me print click",
    "s2":"save.me send click",
    "s3":"save.me step",
    "m1":"add memory",
    "m2":"del memory",
    "m3":"view memory",
    "c1":"wellness index"
}

CONF = get_conf()

LOGGER = get_logger("scienceview")

def get_sha(obj) -> str:
    """returns sha256 hexdigest of obj. returns string
    obj = bytes of object to be hashed
    """
    obj = str(obj)
    obj += "a" * (1024-len(obj)) if len(obj) < 1024 else obj
    hashhold = hashlib.sha256()
    hashhold.update(obj.encode("utf-8"))
    return hashhold.hexdigest()


def new_entry(action_id:str, anonid: bytes, value, role="User", mangle=False):
    """add new entry to research database. returns None
    action_id = identifier of action that is translated to a description by ID_DESC
    anonid = anonid of user that too action
    value = special value to be assigend to the id. string or iterable
    role = role of the user that took the action. defaults to "User"
    mangle = only add a hashed version of the value to database"""
    if not CONF["research"]["enable_collection"] == "True":
        return
    anonid = get_sha(anonid)
    actiontime = str(int(time.time()))
    value = ",".join(value) if type(value) == list else value
    value = get_sha(value) if mangle else value
    package = ResearchData(ActionId=action_id, AnonId=anonid.encode("utf-8"), Value=value, Time=datetime, Role=role)
    package.save()
    if CONF["research"]["output_to_console"] == "True":
        LOGGER.info(f"SciPak {role}: {anonid[0:5]} '{ID_DESC[action_id]}' and value '{value}' at {actiontime}")


def export_data(maxlines=1000, rootdir=CONF["research"]["exportdir"], timefrom=0, timeto=float("inf")):
    LOGGER.info("Data export initialized")
    i = 0
    foldername = os.path.join(rootdir, str(datetime.now().strftime(CONF["research"]["timestrf"])))
    try:
        os.makedirs(foldername)
    except FileExistsError:
        pass

    for package in get_all_data():
        if i%maxlines == 0:
            try:
                file.close()
            except NameError:
                pass
            file = open(os.path.join(foldername,f"entries{i}-{i+maxlines}.csv"), "w")
        if timefrom < int(package[3]) < timeto: 
            file.write(",".join([str(i) for i in package]) + "\n")
        i+=1


def forget_me(anonid):
    #select all in table with anonid and burn it
    ResearchData.objects.filter(AnonId=get_sha(anonid).encode("utf-8")).delete()
    return


def find_me(anonid):
    """generator for all the research data that belongs to a user. """
    anonid = get_sha(anonid).encode("utf-8")
    for data in ResearchData.objects.filter(AnonId=anonid).iterator():
        yield (ID_DESC[data.ActionId], data.Value, data.Time.now())


def get_all_data() -> tuple:
    for data in ResearchData.objects.iterator():
        yield (data.ActionId, get_sha(data.AnonId), data.Value, data.Time.timestamp(), data.Role)


def gen_otp(minsize=1024) -> str:
    timestr = "time:" + str(int(time.time()))
    longstr = "key:"
    try:
        with open("export-key.txt", "r") as inf:
            lines = inf.readlines()
            oldtime = int(lines[0].split(":")[1])
            if time.time() - oldtime < CONF["research"]["key_lifetime"]:
                return lines[1]
    except FileNotFoundError:
        pass
    while len(longstr) < minsize:
        longstr += get_sha(os.urandom(256))
    with open("export-key.txt", "w") as outf:
        outf.write(timestr + "\n" + longstr)
        LOGGER.info(f"New export key generated at time {timestr}")
    return longstr





def gdpr_csv(anonid: bytes, linebreak = "\n") -> str:
    outstr = ""
    packages = find_me(anonid)
    for package in packages:
        outstr += "\t" + "\t".join([str(i) for i in package]) + linebreak
    return outstr
