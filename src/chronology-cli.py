#!/usr/bin/env python

import chronology
from chronology import config
import os
import signal
import argparse
import psutil
from subprocess import PIPE
import sys

parser = argparse.ArgumentParser(
    prog="chronology.py",
    description="Control the Chronology daemon")
parser.add_argument("command",
                    choices=['start', 'stop',
                             'info', 'add-dir', 'remove-dir'])
args = parser.parse_args()


def start():
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
        print "Daemon is not running"
    else:
        print "Daemon is running with PID", pid


def addDir():
    pass


def removeDir():
    raise Exception("Not yet implemented. Edit %s by hand."
                    % config.watchdirFile)


def findDaemonFile():
    chronologyPackageDir = os.path.dirname(chronology.__file__)
    daemonFilePath = os.path.join(chronologyPackageDir, "chronology_daemon.py")

    return daemonFilePath

if args.command == 'start':
    start()

elif args.command == 'stop':
    stop()

elif args.command == 'info':
    info()

elif args.command == 'add-dir':
    addDir()

elif args.command == 'remove-dir':
    removeDir()
