import pytest
import os
import pygit2

from chronology import config

from test_common import *
from repo import *

repoDirName = "repo"
configDirName = "config"


@pytest.fixture(autouse=True)
def monkeypatchConfig(tmpdir, monkeypatch):
    sTmpdir = str(tmpdir)
    configDir = os.path.join(sTmpdir, configDirName)

    monkeypatch.setattr(
        config, "defaultWatchdirFile", os.path.join(configDir, "watchdirs"))
    monkeypatch.setattr(
        config, "defaultPidFile", os.path.join(configDir, "chronology.pid"))


@pytest.fixture
def oneRepoOneCommit(tmpdir):
    sTmpdir = str(tmpdir)
    repoDir = os.path.join(sTmpdir, repoDirName)

    repo = RepoBuilder(repoDir).addCommits(1)

    watchdirConfig = config.WatchdirConfig()
    watchdirConfig.addDirToWatch(repoDir)

    return [repo]
