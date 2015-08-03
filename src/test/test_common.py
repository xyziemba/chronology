import os


def fullPath(tmpdir, filename):
    return os.path.join(str(tmpdir), filename)


def createFileWithContent(path, content):
    with open(path, "w+") as f:
        f.write(content)
