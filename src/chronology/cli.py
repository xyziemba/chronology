import chronology
from chronology import config
import os
import signal
import argparse
import psutil
from subprocess import PIPE
import sys


class Client(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="chronology.py",
            description="Control the Chronology daemon\nFor more info," +
            " go to https://github.com/xyziemba/chronology",)
        parser.add_argument("command",
                            choices=['start', 'stop', 'info',
                                     'add-dir', 'remove-dir'])
        parser.add_argument("-d", "--directory",
                            help="Specify a directory for"
                            "add-dir or remove-dir")
        parser.add_argument("-w", "--watchdirFile",
                            help="File specifying the directories to watch")
        parser.add_argument("-p", "--pidFile",
                            help="PID lock file")
        args = parser.parse_args()
        self.args = args

        if args.pidFile:
            self.pidConfig = config.PidConfig(args.pidFile)
        else:
            self.pidConfig = config.PidConfig()

        if args.watchdirFile:
            self.watchdirConfig = config.WatchdirConfig(args.watchdirFile)
        else:
            self.watchdirConfig = config.WatchdirConfig()

        if args.command == 'start':
            self._start()

        elif args.command == 'stop':
            self._stop()

        elif args.command == 'info':
            self._info()

        elif args.command == 'add-dir':
            if args.directory is None:
                parser.print_usage()
                print "\tadd-dir command requires "
                "specifying a directory with -d"
                sys.exit(0)
            self.addDir()

        elif args.command == 'remove-dir':
            if args.directory is None:
                parser.print_usage()
                print "\tremove-dir command requires specifying a "
                "directory with -d"
                sys.exit(0)
            self.removeDir()

    def _start(self):
        if not self.watchdirConfig.doesFileExist():
            print "No file found at %s" % self.watchdirConfig.watchdirFile
            print "Not configured to watch anything."
            print
            print "Run: chronology-cli.py add-dir -d <directory to watch>"
            return
        if self.pidConfig.isDaemonRunning():
            print "Daemon already running"
            return

        # Always pass the config file parameters. This makes E2E testing easier
        invocation = [sys.executable, self._findDaemonFile()]
        invocation.append('-p')
        invocation.append(self.pidConfig.filename)
        invocation.append('-w')
        invocation.append(self.watchdirConfig.filename)

        p = psutil.Popen(invocation, stdout=PIPE)
        print "Started daemon with PID", p.pid

    def _stop(self):
        pid = self.pidConfig.getChronologyPid()
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
            print "Sending SIGABRT. On Windows, "
            "kill %d with task manager" % pid
            proc.send_signal(signal.SIGABRT)
        else:
            print "Exited successfully."

    def _info(self):
        pid = self.pidConfig.getChronologyPid()

        if pid is None:
            print "Status: STOPPED\nDaemon is not running"
        else:
            print "Status: RUNNING\nDaemon is running with PID", pid

        print

        if self.watchdirConfig.doesFileExist() and \
                self.watchdirConfig.getWatchedFiles():
            print "Watch dirs:"
            for f in self.watchdirConfig.getWatchedFiles():
                print "\t", f
        else:
            print "Not configured to watch anything."
            print
            print "Run: chronology-cli.py add-dir -d <directory to watch>"

    def _addDir(self):
        # validate dir
        newDir = os.path.abspath(self.args.directory)

        if not os.path.exists(newDir):
            print "Unable to find %s" % newDir
            return

        self.watchdirConfig.addDirToWatch(args.directory)

        pid = self.pidConfig.getChronologyPid()
        if pid is not None:
            stop()
            start()

    def _removeDir(self):
        raise Exception("Not yet implemented. Edit %s by hand."
                        % config.watchdirFile)

    def _findDaemonFile(self):
        chronologyPackageDir = os.path.dirname(chronology.__file__)
        daemonFilePath = os.path.join(
            chronologyPackageDir, "chronology_daemon.py")

        return daemonFilePath
