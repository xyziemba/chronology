#!/usr/bin/env python2

import rlcompleter
import readline
readline.parse_and_bind('tab:complete')

import signal
import os
import pyuv

import config
from watcher import Watcher


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

loop = pyuv.Loop.default_loop()

watchers = list()
for folder in config.getWatchedFiles():
    print "Watching", folder
    fsEventHandle = pyuv.fs.FSEvent(loop)
    watchers.append(Watcher(folder, fsEventHandle))


signalHandle = pyuv.Signal(loop)
signalHandle.start(signalCallback, signal.SIGINT)

createPidFile()
loop.run()
deletePidFile()
