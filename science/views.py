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
    if not CONF["research"]["enable_collection"] == "True":
        return
    actiontime = str(int(time.time()))
    value = ",".join(value) if type(value) == list else value
    value = get_sha(value) if mangle else value
    package = ResearchData(ActionId=action_id, AnonId=anonid, Value=value, Time=datetime)
    package.save()
    if CONF["research"]["output_to_console"] == "True":
        LOGGER.info(f"SciPak {anonid[0:5]} '{ID_DESC[action_id]}' and value '{value}' at time {actiontime}")


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
            print(package)
            file.write(",".join([str(i) for i in package]) + "\n")
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
        yield (data.ActionId, get_sha(data.AnonId), data.Value, data.Time.timestamp())


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


def export_view(request):
    one_time_pass = gen_otp().split(":")[1]
    if request.method == 'POST':
        if request.POST["export_key"] == one_time_pass:
            export_data()
        else:
            LOGGER.warning("Wrong export key used!")
    args = {
        'POST': request.POST,
        'form': {
            "export_key":"Enter one time key",
        }
    }
    return render(request, 'science/export.html', args)

