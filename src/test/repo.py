# functions for repository manipulation

import os
import pygit2
from test_common import *

testSig = pygit2.Signature("Test Fixture", "test-fixture@chronology.sh")


class RepoBuilder(object):

    def __init__(self, repoDir, init=True):
        self.repoDir = repoDir

        if init:
            self._repo = pygit2.init_repository(repoDir)
        else:
            self._repo = pygit2.repository(repoDir)

    def addCommits(self, numCommits):
        for i in xrange(numCommits):
            filepath = createRandomFile(self.repoDir)
            for j in xrange(10):
                appendRandomLine(filepath)
            self.syncAndCommitRepo()

    def syncAndCommitRepo(self):
        self._repo.index.add_all()
        self._repo.index.write()
        new_tree = self._repo.index.write_tree()

        def createCommit(ref, parents):
            self._repo.create_commit(
                ref, testSig, testSig, "A Commit", new_tree, parents)

        if self._repo.head_is_unborn:
            createCommit("refs/heads/master", [])
        else:
            createCommit(self._repo.head.name, [self._repo.head.target])

        return self

    def switchToBranch(branchName, createAutomatically=True):
        raise Exception("NYI")
