import argparse
import threading
import time 
import sys


from django.core.management import execute_from_command_line as django_manage


from confman import get_conf
import logman


CONF = get_conf()
LOGGER = logman.get_logger("timeman")

def compress_logs():
    logman.log_cleaner()

def queue_executer(args):
    parser = argparse.ArgumentParser(description="Run automated tasks for 12steps")
    parser.add_argument("-p", "--purge", help="Look through sessions and remove ones that have expired",
    metavar="")
    parser.add_argument("-c", "--compress-logs", help="Uses gzip compression on large logfiles",
    metavar = "")
    parser.add_argument("--test")
    args = parser.parse_args(args)
    if args.purge:
        django_manage(["manage.py","clearsessions"])
    print(args.test)
    if threading.current_thread() != threading.main_thread():
        threading.current_thread().join()


def send_worker(work, workers):
    #check if there are idle workers
    if threading.active_count()-1 <= len(workers):
        #find idle worker
        for worker in workers:
            try:
                #send idle worker back to work
                worker._args=(work,)
                worker.start()
                break
            except RuntimeError:
                pass
                #worker busy
    else:
        #if there are no idle workers, send back the work
        return work
    return None


def clock(runfor, tab, sleepfor = 1, threads = 4):
    runtime = 0
    threads = [threading.Thread(target = queue_executer) for i in range(threads)]
    nextrun = []
    tstart = time.time()
    while not runtime or runtime < runfor:
        runtime += 1
        for work in nextrun:
                leftovers = send_worker(work.split(" "), threads)
                if leftovers:
                    nextrun.append(leftovers)
        for key in tab:
            if runtime % key == 0:
                leftovers = send_worker(tab[key].split(" "), threads)
                if leftovers:
                    nextrun.append(leftovers)
        time.sleep(1)
    try:
        time.sleep(sleepfor - (time.time() - tstart))
    except ValueError:
        print("time for a run exceeded! must've been a lot of work to do!")


def devvy():
    crontab = {
        1:"--test 1",
        5:"--test 5",
        60:"",
        300:"",
        3600:"",
        86400:"",
        604800:""
    }
    clock(500, crontab)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        devvy()
    else:
        queue_executer(sys.argv[1:])
