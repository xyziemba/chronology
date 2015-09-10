import pygit2
import pyuv


REF_PREFIX = "refs/chronology/"


class Watcher(object):

    enabled = True  # swap to false when fsWatcherHandle is stopped

    def __init__(self, repoDir, fsWatcherHandle):
        self._repoDir = repoDir
        self._fsWatcherHandle = fsWatcherHandle
        fsWatcherHandle.start(repoDir, 4, self.watcherCallback)
        # Below, 4 --> UV_FS_EVENT_RECURSIVE
        self._repo = pygit2.Repository(repoDir)

    def stop(self):
        if not self.enabled:
            # this might not be necessary, but IDK if a second
            # close call on fsWatcherHandle could cause a problem.
            # I'm playing it safe now.
            raise Exception("FsWatcher has already been stopped")

        self.enabled = False
        self._fsWatcherHandle.close()

    def commitChanges(self):
        # todo: handle repro.head_is_unborn
        headLoc = self._repo.lookup_reference("HEAD")
        headLocName = headLoc.target

        # import re
        # matchResult = re.match("refs/heads/(.*)", headLocName)
        # if matchResult != None:
        #     timeTravelRefName = REF_PREFIX + matchResult.groups(1)[0]
        # else:
        #     timeTravelRefName = REF_PREFIX + headLocName.target
        timeTravelRefName = REF_PREFIX + headLoc.get_object().hex

        print "Using ref:", timeTravelRefName

        index = self._repo.index
        index.add_all(["*"])
        new_tree = index.write_tree()

        try:
            timeTravelRef = self._repo.lookup_reference(timeTravelRefName)
        except KeyError:
            print timeTravelRefName, "ref not found"
            timeTravelRef = self._repo.create_reference(
                timeTravelRefName, headLoc.get_object().id)

        sig = pygit2.Signature("Chronology", "none@chronology.sh")
        self._repo.create_commit(
            timeTravelRefName, sig, sig, "Time!\n",
            new_tree, [timeTravelRef.target])

    def watcherCallback(self, fsevent_handle, filename, events, error):
        print filename
        if (filename.find(".git") == 0):  # found .git at the root of the path
            return

        self.commitChanges()
