from django.shortcuts import render

# Create your views here.
from datetime import datetime
import time
import os
import hashlib
from tools.confman import get_conf
from tools.logman import get_logger

from science.models import ResearchData


ID_DESC={
    "PROFILE":"Anonymous user profile",
    "g2":"page click",
    "g1":"page enter",
    "g3":"page leave",
    "u1":"user logon",
    "u2":"user logoff",
    "u3":"prof change",
    "h1":"intro watch",
    "h2":"prep guide",
    "r1":"share with",
    "p1":"contact add",
    "p2":"contact use",
    "s1":"print click",
    "s2":"send click",
    "m1":"add memory",
    "m2":"del memory",
    "m3":"view memory",
    "c1":"wellness ind"
}

CONF = get_conf()

LOGGER = get_logger("scienceview")

def get_sha(obj) -> str:
    obj = str(obj)
    obj += "a" * (1024-len(obj)) if len(obj) < 1024 else obj
    hashhold = hashlib.sha256()
    hashhold.update(obj.encode("utf-8"))
    return hashhold.hexdigest()


def new_entry(action_id:str, anonid: bytes, value:str, mangle=False):
    if not CONF["enable_collection"] == "True":
        return
    actiontime = str(int(time.time())) if CONF["research"]["timestandard"] == "unix" else str(datetime.now().strftime(CONF["research"]["strftime"]))
    value = ",".join(value) if type(value) == list else value
    value = get_sha(value) if mangle else value
    package = ResearchData(ActionId=action_id, AnonId=anonid, Value=value, Time=datetime)
    package.save()
    LOGGER.info(f"SciPak {anonid[0:len(anonid)//4]} '{ID_DESC[action_id]}' and value '{value}' at time {actiontime}")


def export_data(dir, maxlines=1000, rootdir=CONF["research"]["exportdir"], timefrom=0, timeto=float("inf")):
    i = 0
    foldername = datetime.now().strftime(CONF["research"]["strftime"])
    try:
        os.mkdir(foldername)
    except FileExistsError:
        pass
    for package in get_all_data():
        if i%maxlines == 0:
            try:
                file.close()
            except NameError:
                pass
            file = open(os.path.join(rootdir,foldername,f"entries{i}-{i+maxlines}.csv"), "a")
        if timefrom < int(package[3]) < timeto: 
            file.write(",".join(package))
        i+=1


def forget_me(anonid):
    #select all in table with anonid and burn it
    ResearchData.objects.filter(AnonId=anonid).delete()
    return


def find_me(anonid):
    #select all in table with anonid and return
    return ResearchData.objects.filter(AnonId=anonid)


def get_all_data() -> tuple:
    for data in ResearchData.objects.iterator():
        yield (data.ActionId, data.AnonId, data.Value, data.Time)
