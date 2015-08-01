import chronology
from chronology import config
import os
import signal
import argparse
import psutil
from subprocess import PIPE
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="chronology.py",
        description="Control the Chronology daemon\nFor more info," +
        " go to https://github.com/xyziemba/chronology",)
    parser.add_argument("command",
                        choices=['start', 'stop', 'info',
                                 'add-dir', 'remove-dir'])
    parser.add_argument("-d", "--directory",
                        help="Specify a directory for add-dir or remove-dir")
    args = parser.parse_args()

    if args.command == 'start':
        start()

    elif args.command == 'stop':
        stop()

    elif args.command == 'info':
        info()

    elif args.command == 'add-dir':
        if args.directory == None:
            parser.print_usage()
            print "\tadd-dir command requires specifying a directory with -d"
            sys.exit(0)
        addDir(args.directory)

    elif args.command == 'remove-dir':
        if args.directory == None:
            parser.print_usage()
            print "\tremove-dir command requires specifying a "
            "directory with -d"
            sys.exit(0)
        removeDir(args.directory)


def start():
    if not os.path.exists(config.watchdirFile):
        print "No file found at %s" % config.watchdirFile
        print "Not configured to watch anything."
        print
        print "Run: chronology-cli.py add-dir -d <directory to watch>"
        return
    if config.getChronologyPid() is not None:
        print "Daemon already running"
        return
    p = psutil.Popen([sys.executable, findDaemonFile()], stdout=PIPE)
    print "Started daemon with PID", p.pid


def stop():
    pid = config.getChronologyPid()
    if pid is None:
        print "Daemon is not running"
        return

    proc = psutil.Process(pid)
    print "Stopping PID %d with SIGINT" % pid
    proc.send_signal(signal.SIGINT)

    try:
        proc.wait(timeout=5)
    except psutil.TimeoutExpired:
        print "Timed out."
        print "Sending SIGABRT. On Windows, kill %d with task manager" % pid
        proc.send_signal(signal.SIGABRT)
    else:
        print "Exited successfully."


def info():
    pid = config.getChronologyPid()

    if pid is None:
        print "Status: STOPPED\nDaemon is not running"
    else:
        print "Status: RUNNING\nDaemon is running with PID", pid

    print

    if os.path.exists(config.watchdirFile):
        print "Watch dirs:"
        for f in config.getWatchedFiles():
            print "\t", f
    else:
        print "Not configured to watch anything."
        print
        print "Run: chronology-cli.py add-dir -d <directory to watch>"


def addDir(directory):
    # validate dir
    newDir = os.path.abspath(directory)

    if not os.path.exists(newDir):
        print "Unable to find %s" % newDir
        return

    watchdirFileDir = os.path.dirname(config.watchdirFile)
    if not os.path.exists(watchdirFileDir):
        os.mkdir(watchdirFileDir)

    with open(config.watchdirFile, 'a+') as f:
        f.write("\n"+newDir+"\n")

    pid = config.getChronologyPid()
    if pid is not None:
        stop()
        start()


def removeDir(directory):
    raise Exception("Not yet implemented. Edit %s by hand."
                    % config.watchdirFile)


def findDaemonFile():
    chronologyPackageDir = os.path.dirname(chronology.__file__)
    daemonFilePath = os.path.join(chronologyPackageDir, "chronology_daemon.py")

    return daemonFilePath
