#!/usr/bin/env python2

import rlcompleter
import readline
readline.parse_and_bind('tab:complete')

import signal
import os
import pyuv

import config
from watcher import Watcher

# Globals
watchers = list()
signalHandle = None


def signalCallback(signal_handle, signal_num):
    print "Shutting down..."
    for watcher in watchers:
        watcher.stop()
    signalHandle.close()


def createPidFile():
    with open(config.pidFile, 'w') as f:
        f.writelines(str(os.getpid()))


def deletePidFile():
    os.remove(config.pidFile)


def main():
    print "Daemon PID:", os.getpid()
    loop = pyuv.Loop.default_loop()

    for folder in config.getWatchedFiles():
        print "Watching", folder
        fsEventHandle = pyuv.fs.FSEvent(loop)
        watchers.append(Watcher(folder, fsEventHandle))

    global signalHandle
    signalHandle = pyuv.Signal(loop)
    signalHandle.start(signalCallback, signal.SIGINT)

    createPidFile()
    loop.run()
    deletePidFile()

if __name__ == '__main__':
    main()
