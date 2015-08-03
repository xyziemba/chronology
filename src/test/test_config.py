from chronology import cli, config
import time
import os
import pytest

from test_common import *


class TestConfigFile(object):
    configFileName = "foo.txt"

    def test_fileDoesNotExist(self, tmpdir):
        path = fullPath(tmpdir, self.configFileName)
        cfg = config.ConfigFile(path)
        assert not cfg.doesFileExist()

    def test_fileDoesExist(self, tmpdir):
        path = fullPath(tmpdir, self.configFileName)
        cfg = config.ConfigFile(path)
        createFileWithContent(path, "Hello file!")
        assert cfg.doesFileExist()


class TestPidFile(object):
    pidFileName = "chronology.pid"

    def test_noPid(self, tmpdir):
        path = fullPath(tmpdir, self.pidFileName)
        pidConfig = config.PidConfig(path)
        assert not pidConfig.doesFileExist()
        assert not pidConfig.isDaemonRunning()
        assert pidConfig.getChronologyPid() is None

    def test_withPid(self, tmpdir):
        path = fullPath(tmpdir, self.pidFileName)
        pidConfig = config.PidConfig(path)
        createFileWithContent(path, "1234")
        assert pidConfig.doesFileExist()
        assert not pidConfig.isDaemonRunning()
        assert pidConfig.getChronologyPid() == 1234

    def test_writeReadDeletePid(self, tmpdir):
        path = fullPath(tmpdir, self.pidFileName)
        pidConfig = config.PidConfig(path)
        pidConfig.writeSelfAsPid()
        assert pidConfig.doesFileExist()
        assert not pidConfig.isDaemonRunning()
        assert pidConfig.getChronologyPid() == os.getpid()

        pidConfig.deletePidFile()
        assert pidConfig.getChronologyPid() is None

    # Todo: run a test with a fixture that:
    # 1. spins up chronology
    # 2. checks that the daemon is correctly reported
    # def test_withRun(self, repoWithOneCommit):
    #     pass


class TestWatchdirConfig(object):
    watchdirConfigFileName = "watchdirs"

    def runReadTest(self, tmpdir, fileContents, expectedWatchdirs):
        path = fullPath(tmpdir, self.watchdirConfigFileName)
        createFileWithContent(path, fileContents)
        wdConfig = config.WatchdirConfig(path)
        foundWatchdirs = wdConfig.getWatchedFiles()
        assert type(foundWatchdirs) is set

        diff = set(expectedWatchdirs).symmetric_difference(foundWatchdirs)
        assert len(diff) == 0

    def test_emptyFile(self, tmpdir):
        with pytest.raises(Exception) as exinfo:
            self.runReadTest(
                tmpdir,
                "",
                [""])
        assert 'contains no watch directories' in str(exinfo.value)

    # TODO: parameterize the tests below using pytest's support for that
    def test_singleLineWithSlash(self, tmpdir):
        self.runReadTest(
            tmpdir,
            "/foo/bar/",
            ["/foo/bar"])

    def test_singleLineWithoutSlash(self, tmpdir):
        self.runReadTest(
            tmpdir,
            "/foo/bar",
            ["/foo/bar"])

    def test_singleLinePlusCarriageReturn(self, tmpdir):
        self.runReadTest(
            tmpdir,
            "/foo/bar/\n",
            ["/foo/bar"])

    def test_singleLinePlusComment(self, tmpdir):
        self.runReadTest(
            tmpdir,
            """/foo/bar/
            #COMMENT""",
            ["/foo/bar"])

    def test_multiLine(self, tmpdir):
        self.runReadTest(
            tmpdir,
            "/foo/bar/\n/faz/baz",
            ["/foo/bar", "/faz/baz"])

    def test_multiLinePlusComment(self, tmpdir):
        self.runReadTest(
            tmpdir,
            """/foo/bar/
            #COMMENT
            /faz/baz""",
            ["/foo/bar", "/faz/baz"])
