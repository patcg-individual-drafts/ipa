#!/usr/bin/env python3

import argparse
from fileinput import input
import re
from sys import argv, stderr
import tempfile


_seen = dict()
_xml = re.compile(r"</?[a-zA-Z]\w+>")


def href(title):
    """
    An attempt to replicate how GitHub creates title anchors.
    """
    global _xml
    title = _xml.sub("", title)
    h = "".join(
        [x.lower() if x.isalnum() else ("-" if x == " " else "") for x in title]
    )

    global _seen
    _seen[h] = _seen.get(h, 0) + 1
    if _seen[h] > 1:
        return f"{h}-{_seen[h]-1}"
    return h


parser = argparse.ArgumentParser(description="Add a markdown ToC")
parser.add_argument(
    "-d",
    "--depth",
    dest="depth",
    type=ord,
    default=3,
    help="Maximum heading level to include",
)
parser.add_argument(
    "-t",
    "--title",
    dest="titles",
    action="append",
    default=["table of contents", "Table of Contents"],
    help="Title of ToC section",
)
parser.add_argument("file", nargs=1, help="Markdown file")
args = parser.parse_args()

tocfile = tempfile.NamedTemporaryFile()

with open(tocfile.name, "w") as toc:
    intoc = False
    for line in input(files=(args.file)):
        if line.startswith("#"):
            line = line.rstrip("#").strip()
            title = line.lstrip("#")
            level = len(line) - len(title)
            title = title.strip()
            if level <= args.depth:
                toc.write(f"{'  ' * (level - 1)}* [{title}](#{href(title)})\n")
        elif intoc:
            continue


intoc = False
for line in input(files=(args.file)):
    if line.startswith("#"):
        title = line.strip("#").strip().lower()
        intoc = title in args.titles
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
