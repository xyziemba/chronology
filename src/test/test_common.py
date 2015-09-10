import os
import random

words = None
wordFilePath = os.path.join(os.path.dirname(__file__), 'dict.txt')
with open(wordFilePath) as f:
    words = map(lambda x: x.rstrip(), f.readlines())


def fullPath(tmpdir, filename):
    return os.path.join(str(tmpdir), filename)


def createFileWithContent(path, content):
    with open(path, "w+") as f:
        f.write(content)


def appendContent(path, content):
    with open(path, "a+") as f:
        f.write(content)


def appendRandomLine(path):
    content = "%f\n" % random.random()
    appendContent(path, content)


def removeRandomLine(path):
    with open(path, "r+") as f:
        lines = f.readlines()
        if len(lines) == 0:
            return  # nothing to shuffle
        chosenData = random.choice(lines)
        lines.remove(chosenData)
        f.seek(0)
        f.writelines(lines)
        f.truncate()


def createRandomFile(path):
    if not os.path.isdir(path):
        raise Exception(
            "createRandom File requires a directory."
            " %s is not a directory." % path)

    wordOne = random.choice(words)
    wordTwo = random.choice(words)
    wordThree = random.choice(words)

    filepath = os.path.join(path, wordOne + wordTwo + wordThree)

    with open(filepath, "w+") as f:
        pass

    return filepath
