import os
import psutil

# use expanduser to resolve ~ in a platform-independent way
watchdirFile = os.path.expanduser("~/.chronology/watchdirs")
pidFile = os.path.expanduser("~/.chronology/chronology.pid")


def getWatchedFiles():
    if not os.path.exists(watchdirFile):
        raise Exception("Watch dir list not found at %s" % watchdirFile)

    watchedFiles = list()
    with open(watchdirFile, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            gitDir = os.path.join(line, ".git")
            if not os.path.exists(gitDir):
                raise Exception("%s is not a valid git repository" % line)
            watchedFiles.append(line)

    if len(watchedFiles) == 0:
        raise Exception("%s contains no watch directories.")

    return watchedFiles


def getChronologyPid():
    if not os.path.exists(pidFile):
        return None

    with open(pidFile, 'r') as f:
        return int(f.readline().strip())


def addDirToWatch(dir):
    raise Exception("Not yet implemented.")


def isDaemonRunning():
    pid = getChronologyPid()

    if pid is None:
        return False

    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

    cmdline = proc.cmdline()

    return "chronology_daemon.py" in cmdline[1]
