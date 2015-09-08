#!/usr/bin/env python2

import rlcompleter
import readline
readline.parse_and_bind('tab:complete')

import signal
import os
import pyuv

import config
from watcher import Watcher

import argparse

# Globals
watchers = list()
signalHandle = None


def signalCallback(signal_handle, signal_num):
    print "Shutting down..."
    for watcher in watchers:
        watcher.stop()
    signalHandle.close()


def main():

    parser = argparse.ArgumentParser(
        prog="chronology_daemon.py",
        description="Worker for Chronology.\n"
        "You should generally use chronology-cli.py to invoke this daemon.")
    parser.add_argument("-w", "--watchdirFile",
                        help="File specifying the directories to watch")
    parser.add_argument("-p", "--pidFile",
                        help="PID lock file")
    args = parser.parse_args()

    if args.pidFile:
        pidConfig = config.PidConfig(args.pidFile)
    else:
        pidConfig = config.PidConfig()

    if args.watchdirFile:
        watchdirConfig = config.WatchdirConfig(args.watchdirFile)
    else:
        watchdirConfig = config.WatchdirConfig()

    print "Daemon PID:", os.getpid()
    loop = pyuv.Loop.default_loop()

    for folder in watchdirConfig.getWatchedFiles():
        print "Watching", folder
        fsEventHandle = pyuv.fs.FSEvent(loop)
        watchers.append(Watcher(folder, fsEventHandle))

    global signalHandle
    signalHandle = pyuv.Signal(loop)
    signalHandle.start(signalCallback, signal.SIGINT)

    pidConfig.writeSelfAsPid()
    loop.run()
    pidConfig.deletePidFile()

if __name__ == '__main__':
    main()
