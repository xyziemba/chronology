import os
import psutil

# use expanduser to resolve ~ in a platform-independent way
watchdirFile = os.path.expanduser("~/.timetravel/watchdirs")
pidFile = os.path.expanduser("~/.timetravel/timetravel.pid")


def getWatchedFiles():
    if not os.path.exists(watchdirFile):
        raise Exception("Watch dir list not found at %s" % watchdirFile)

    watchedFiles = list()
    with open(watchdirFile, 'r') as f:
        for line in f:
            line = line.strip()
            gitDir = os.path.join(line, ".git")
            if not os.path.exists(gitDir):
                raise Exception("%s is not a valid git repository" % line)
            watchedFiles.append(line)

    if len(watchedFiles) == 0:
        raise Exception("%s contains no watch directories.")

    return watchedFiles


def getTimeTravelPid():
    if not os.path.exists(pidFile):
        return None

    with open(pidFile, 'r') as f:
        return int(f.readline().strip())


def addDirToWatch(dir):
    raise Exception("Not yet implemented.")


def isDaemonRunning():
    pid = getTimeTravelPid()

    if pid is None:
        return False

    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

    cmdline = proc.cmdline()

    return "timetravel_daemon.py" in cmdline[1]
