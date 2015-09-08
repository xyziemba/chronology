import os
import psutil

# use expanduser to resolve ~ in a platform-independent way
defaultWatchdirFile = os.path.expanduser("~/.chronology/watchdirs")
defaultPidFile = os.path.expanduser("~/.chronology/chronology.pid")


class ConfigFile(object):

    def __init__(self, filename):
        self.filename = filename

    def doesFileExist(self):
        return os.path.exists(self.filename)


class PidConfig(ConfigFile):

    def __init__(self, pidFile=None):
        # Arg pidFile is late-bound such that the test
        # infrastructure can monkeypatch defaultPidFile
        if not pidFile:
            pidFile = defaultPidFile
        super(PidConfig, self).__init__(pidFile)
        self.pidFile = pidFile

    def isDaemonRunning(self):
        pid = self.getChronologyPid()

        if pid is None:
            return False

        try:
            proc = psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

        cmdline = proc.cmdline()

        return "chronology_daemon.py" in cmdline[1]

    def getChronologyPid(self):
        if not os.path.exists(self.pidFile):
            return None

        with open(self.pidFile, 'r') as f:
            return int(f.readline().strip())

    def writeSelfAsPid(self):
        if self.isDaemonRunning():
            raise Exception("Will not delete PID of currently running daemon.")
        with open(self.pidFile, 'w') as f:
            f.writelines(str(os.getpid()))

    def deletePidFile(self):
        os.remove(self.pidFile)


class WatchdirConfig(ConfigFile):

    def __init__(self, watchdirFile=None):
        # Arg watchdirFile is late-bound such that the test
        # infrastructure can monkeypatch defaultWatchdirFile
        if not watchdirFile:
            watchdirFile = defaultWatchdirFile
        super(WatchdirConfig, self).__init__(watchdirFile)
        self.watchdirFile = watchdirFile

    def getWatchedFiles(self):
        if not os.path.exists(self.watchdirFile):
            raise Exception("Watch dir set not found at %s" %
                            self.watchdirFile)

        watchedFiles = set()  # set means we'll skip duplicates
        with open(self.watchdirFile, 'r') as f:
            for line in f:
                line = line.strip().rstrip(
                    os.sep)  # remove a trailing / or \
                if line == "" or line.startswith("#"):
                    continue
                watchedFiles.add(line)

        if len(watchedFiles) == 0:
            raise Exception("%s contains no watch directories."
                            % self.watchdirFile)

        return watchedFiles

    def addDirToWatch(self, directory):
        watchdirFileDirectory = os.path.dirname(self.watchdirFile)
        if not os.path.exists(watchdirFileDirectory):
            os.mkdir(watchdirFileDirectory)

        with open(self.watchdirFile, 'a+') as f:
            f.write("\n" + directory + "\n")
