#!/usr/bin/env python3

from fileinput import FileInput
from sys import argv, stderr
import tempfile

if len(argv) < 2:
    stderr.write(f"Usage: {sys.argv[0]} <md>")
    exit(2)

_seen = dict()


def href(title):
    """
    An attempt to replicate how GitHub creates title anchors.
    """
    global _seen
    h = "".join([x.lower() if x.isalnum() else ("-" if x == " " else "") for x in title])
    _seen[h] = _seen.get(h, 0) + 1
    if _seen[h] > 1:
        return f"{h}-{_seen[h]-1}"
    return h

tocfile = tempfile.NamedTemporaryFile()

with open(tocfile.name, "w") as toc:
    intoc = False
    for line in FileInput(files=(argv[1])):
        if line.startswith("#"):
            line = line.rstrip("#").strip()
            title = line.lstrip("#")
            level = len(line) - len(title)
            title = title.strip()
            toc.write(f"{'  ' * (level - 1)}* [{title}](#{href(title)})\n")
        elif intoc:
            continue



intoc = False
for line in FileInput(files=(argv[1])):
    if line.startswith("#"):
        title = line.strip("#").strip().lower()
        intoc = title == "table of contents"
        if intoc:
            print(line.rstrip())
            print()
            with open(tocfile.name) as toc:
                for t in toc:
                    print(t.rstrip())
            print()
    if intoc:
        continue
    print(line.rstrip())
