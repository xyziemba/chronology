//
//  main.c
//  TimeTravel
//
//  Created by Xy Ziemba on 6/27/15.
//  Copyright (c) 2015 Ziemba. All rights reserved.
//

#include <stdio.h>
#include <signal.h>
#include <uv.h>
#include <git2.h>

const char TEST_PATH[] = "C:\\testPath";
// TODO: in the future, we want this to be .timetravel
const char STORAGE_DIR[] = ".git";
const char DIRECTORY_CHAR = '\\';

volatile sig_atomic_t g_continueLoop = 1;
uv_loop_t g_mainLoop; // set once at the beginning of the program
const char *g_gitDir = NULL;
const git_repository *g_gitRepo;

int isPathInStorageDirectory(const char *path);
void fs_event_callback(uv_fs_event_t *handle, const char *filename, int events,
                       int status);
int _file_exists(const char *fileName);
int checkDirAndStartupGit(git_repository **out, const char *directory);
int commitAllToRepository(git_repository *repo, const char *message);
int main(int argc, char const *argv[]);

#define FILE_EXIST(str) _file_exists(str) >= 0
#define FILE_EXIST_NOT(str) _file_exists(str) < 0

/*
void HandleSIGINT(int sig) {
    if (sig == SIGINT)
        g_continueLoop = 0;
}*/

/**
 * Checks whether this path is in the storage directory.
 * This is used to filter in fs_event_callback.
 * @param path Path to check
 * @return 0 if not present, anything else if present
 */
int isPathInStorageDirectory(const char *path) {
    char *loc = strstr(path, STORAGE_DIR);
    return path == loc;
}

void fs_event_callback(uv_fs_event_t *handle, const char *filename, int events,
                       int status) {
    char path[1024];
    size_t size = 1023;
    // Does not handle error if path is longer than 1023.
    uv_fs_event_getpath(handle, path, &size);
    path[++size] = '\0';

    fprintf(stderr, "Change detected in %s: ", path);
    if (events & UV_RENAME)
        fprintf(stdout, "renamed");
    if (events & UV_CHANGE)
        fprintf(stdout, "changed");

    fprintf(stdout, " %s\n", filename ? filename : "");

    if (!isPathInStorageDirectory(filename)) {
        commitAllToRepository(g_gitRepo, "TimeTravel record");
    }
}

/*
 * Input: name of file or directory to test for
 * Output: 0 if file exists, -1 if the file doesn't exist, -2 for any other
 * error
 */
int _file_exists(const char *fileName) {
    uv_fs_t fileHandle;

    int result =
        uv_fs_stat(&g_mainLoop, &fileHandle, fileName, NULL /* run sync */);

    if (result == UV_ENOENT) {
        return -1;
    } else if (result < 0) {
        printf("Unexpected result in file_exists.\nuv_fs_stat returned %s: %s",
               uv_err_name(result), uv_strerror(result));
        return -2;
    }

    uv_fs_req_cleanup(&fileHandle);
    return 0;
}

/**
 Finds the local repository for input watch directory.
 If one doesn't exist, it creates an appropriate git repository.
 @param out Returned git_repository pointer. Callee must free with
 git_repository_free
 @param directory Directory to use
 @return 0 if OK, negative value if failed
 */
int checkDirAndStartupGit(git_repository **out, const char *directory) {
    size_t gitDir_len = strlen(directory) + strlen(STORAGE_DIR) +
                        1 /* delimiter */ + 1 /* null char */;
    char *gitDir = calloc(gitDir_len, sizeof(char));
    // we don't have a free for this since it persists for the life of the
    // program

    strcat(gitDir, directory);
    gitDir[strlen(directory)] = DIRECTORY_CHAR;
    strcat(gitDir, STORAGE_DIR);

    g_gitDir = gitDir;

    if (FILE_EXIST_NOT(g_gitDir)) {
        git_repository_init_options opts = GIT_REPOSITORY_INIT_OPTIONS_INIT;
        if (git_repository_init_ext(out, directory, &opts) < 0) {
            printf("[checkDirAndStartupGit] Failed to initialize repository at "
                   "'%s'.\n",
                   directory);
            return -1;
        }
        if (commitAllToRepository(*out, "TimeTravel Startup") < 0) {
            printf(
                "[checkDirAndStartupGit] Failed to perform initial commit.\n");
            return -2;
        }
    } else {
        if (git_repository_open(out, directory) < 0) {
            printf(
                "[checkDirAndStartupGit] Failed to open repository at '%s'.\n",
                directory);
            return -3;
        }
    }

    return 0;
}

/**
 * Commit all changes directly to repo using defaults
 * and the specified message.
 * @param repo The repository
 * @param message The message encoded as UTF-8
 * @return 0 if OK, negative value if failed
 */
int commitAllToRepository(git_repository *repo, const char *message) {
    git_index *index;

    if (git_repository_index(&index, repo) < 0) {
        printf("[commitAllToRepository] Failed to get index.\n");
        return -1;
    }

    // create str array with "*"
    git_strarray gitStrArrayWithWildcard;
    const char *strArrayWithWildcard[1];
    strArrayWithWildcard[0] = "*";
    gitStrArrayWithWildcard.strings = (char **)strArrayWithWildcard;
    gitStrArrayWithWildcard.count = 1;

    // commit all files to index
    if (git_index_add_all(
            index, &gitStrArrayWithWildcard,
            GIT_INDEX_ADD_DISABLE_PATHSPEC_MATCH /* no .gitignore */, NULL,
            NULL)) {
        printf(
            "[commitAllToRepository] Failed to commit all files to index.\n");
        return -2;
    }

    // write index to tree
    git_oid tree_oid;
    if (git_index_write_tree(&tree_oid, index) < 0) {
        printf("[commitAllToRepository] Failed to write index to a tree.\n");
        return -3;
    }

    // write index to disk. This prevents a mismatched index later.
    if (git_index_write(index) < 0) {
        printf("[commitAllToRepository] Failed to write index to disk.\n");
        return -3;
    }

    // get tree itself
    git_tree *tree;
    if (git_tree_lookup(&tree, repo, &tree_oid) < 0) {
        printf("[commitAllToRepository] Failed to get tree from oid.\n");
        return -4;
    }

    // create signature
    git_signature *sig;
    if (git_signature_now(&sig, "TimeTravel", "internal@timetravel.io") < 0) {
        printf("[commitAllToRepository] Failed to create signature.\n");
        return -5;
    }

    // get current HEAD
    git_oid headOid;
    int headNotFound = 0;
    int retVal = git_reference_name_to_id(&headOid, repo, "HEAD");
    if (retVal == GIT_ENOTFOUND) {
        // head couldn't be found. That means that this repo hasn't been
        // used yet, so we uze the "zero" OID
        if (git_oid_fromstr(&headOid, GIT_OID_HEX_ZERO) < 0) {
            printf("[commitAllToRepository] Failed to create null OID.\n");
            return -6;
        }
        headNotFound = 1;
    } else if (retVal < 0) {
        // TODO: this might happen anyways when initializing. Look into that :)
        printf("[commitAllToRepository] Failed to find head reference.\n");
        return -6;
    }

    // lookup commit for that oid unless it's the zero OID
    git_commit *last_commit;
    if (!headNotFound) {
        if (git_commit_lookup(&last_commit, repo, &headOid) < 0) {
            printf("[commitAllToRepository] Failed to get commit from HEAD "
                   "oid.\n");
            return -7;
        }
    }

    // create parent array
    const git_commit *parents[1];
    parents[0] = last_commit;
    int parentsCount = headNotFound ? 0 : 1;

    // commit tree
    git_oid commitOid;
    if (git_commit_create(&commitOid, repo, "HEAD", sig, sig, "UTF-8", message,
                          tree, parentsCount, parents) < 0) {
        printf("[commitAllToRepository] Commit failed.\n");
        return -8;
    }

    // cleanup
    git_index_free(index);
    git_tree_free(tree);
    git_signature_free(sig);
    git_commit_free(last_commit);

    return 0;
}

int main(int argc, char const *argv[]) {
    // Helper functions use UV, so initialization must happen first!
    uv_loop_init(&g_mainLoop);
    uv_disable_stdio_inheritance();
    git_libgit2_init();

    // first parameter, if it exists, is the file watch location
    // otherwise, use TEST_PATH
    const char *watchLocation;
    if (argc > 2) {
        watchLocation = argv[1];
    } else {
        watchLocation = TEST_PATH;
    }

    if (FILE_EXIST_NOT(watchLocation)) {
        printf("[main] Unable to find path '%s'\n", watchLocation);
        return -1;
    }

    git_repository *repo;
    if (checkDirAndStartupGit(&repo, watchLocation) < 0) {
        printf("[main] Failed to startup.\n");
        return -1;
    }

    g_gitRepo = repo;

    uv_fs_event_t watcherHandle;
    uv_fs_event_init(&g_mainLoop, &watcherHandle);
    uv_fs_event_start(&watcherHandle, &fs_event_callback, watchLocation,
                      UV_FS_EVENT_RECURSIVE);

    uv_run(&g_mainLoop, UV_RUN_DEFAULT);

    git_repository_free(repo);
    git_libgit2_shutdown();
    uv_loop_close(&g_mainLoop);
    return 0;
}
