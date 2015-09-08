import pytest
import os
import pygit2

from chronology import config

from test_common import *

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

    repo = pygit2.init_repository(repoDir)

    testFile = os.path.join(repoDir, "foo")
    createFileWithContent(testFile, "This file is named foo.")

    repo.index.add_all()
    repo.index.write()
    new_tree = repo.index.write_tree()

    sig = pygit2.Signature("Test Fixture", "test-fixture@chronology.io")
    repo.create_commit(
        "refs/heads/master", sig, sig, "Initial commit for fixture\n",
        new_tree, [])

    watchdirConfig = config.WatchdirConfig()
    watchdirConfig.addDirToWatch(repoDir)

    return repoDir

