from datetime import datetime
import time
from confman import get_conf
import os
ID_DESC={
    "g1":"page click",
    "g2":"page enter",
    "g3":"page leave",
    "m1":"into watch",
    "m2":"prep guide",
    "r1":"share with"
}

IMPLIES={
    "g1":["g2","g3"]
}

CONF = get_conf()


def new_entry(action_id: list, anonid, value, imply=True):
    actiontime = str(int(time.time())) if CONF["research"]["timestandard"] == "unix" else int(datetime.now().strftime(CONF["research"]["strftime"]))
    value = ",".join(value) if type(value) == list else value
    send_package(action_id, anonid, value, actiontime)
    if imply and (action_id in IMPLIES):
        for implied in IMPLIES[action_id]:
            new_entry(implied, anonid, value, imply=False)


def retrieve_packages():
    pack_ids = get_all_ids()
    for pack_id in pack_ids:
        yield retrieve_package(pack_id)
    return
    

def export_data(dir, maxlines=1000, rootdir=CONF["research"]["exportdir"], timefrom=0, timeto=float("inf")):
    i = 0
    foldername = datetime.now().strftime(CONF["research"]["strftime"])
    try:
        os.mkdir(foldername)
    except FileExistsError:
        pass
    file = open(os.path.join(rootdir, f"entries0-{maxlines}.csv"), "w")
    for package in retrieve_packages():
        if i%maxlines == 0:
            file.close()
            file = open(os.path.join(rootdir,foldername,f"entries{i}-{i+maxlines}.csv"))
            if timefrom < int(package[3]) < timeto: 
                
                i+=1









#rle territory
def get_all_ids() -> list:
    #return all primary keys in the table so all actions can be fetched
    return list()

def retrieve_package(datapoint_id) -> tuple:
    #return tuple of (action_id, value, time, anonid) from primary key datapoint_id
    return tuple()

def send_package(action_id, anonid, value, datetime) -> None:
    #add entry in database
    pass