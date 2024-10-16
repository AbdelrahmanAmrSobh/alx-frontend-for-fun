#!/usr/bin/python3
"""Module used to translate from markdown to html"""
from hashlib import md5
from sys import stderr
import os
import sys


def translate_line(line: str):
    """Method that translate Additional tags for text like bold, md5, ..."""
    tags = {
        "**": "b",
        "__": "em",
    }
    for key, value in tags.items():
        count = line.count(key)
        for i in range(count):
            line = line.replace(key, f"<{value}>" if i % 2 == 0
                                else f"</{value}>", 1)
    more_logic = [
        ["[[", "]]"],
        ["((", "))"],
    ]
    index = 0
    for open_tag, close_tag in more_logic:
        index = index + 1
        start = line.find(open_tag)
        end = line.find(close_tag)
        if start == -1 or end == -1:
            continue
        part = line[start+2: end]
        if index == 1:
            part = md5(part.encode()).hexdigest()
        else:
            part = part.replace("C", "")
            part = part.replace("c", "")
        line = line[:start+2] + part + line[end:]
        line = line.replace(open_tag, "", 1)
        line = line.replace(close_tag, "", 1)

    return line


def translate_text(line, new_line, line_added):
    """Method used to translate paragraph"""
    line = line.replace("\n", "")
    prefix = ""
    postfix = ""
    first_space = new_line.find(" ")
    if not line_added or line_added.find("</") > -1:
        prefix = "<p>\n"
    if (not new_line or new_line.startswith(("* ", "- ", "\n")))\
            or (first_space > 0 and new_line.startswith(first_space * "#")):
        postfix = "\n</p>\n"
    else:
        postfix = "<br>\n"
    return f"{prefix}\t{line}{postfix}"


def translate_list(line, old_line, new_line, tag_used):
    """Method used to translate unordered and ordered list"""
    line = line.replace("\n", "")
    prefix = ""
    postfix = ""
    start_character = "- " if tag_used == "ul" else "* "
    if not old_line or not old_line.startswith(start_character):
        prefix = f"<{tag_used}>\n"
    if not new_line or not new_line.startswith(start_character):
        postfix = f"</{tag_used}>\n"
    return f"{prefix}\t<li>{line[2:]}</li>\n{postfix}"


def translate_header(line):
    """Method used to translate header"""
    line = line.replace("\n", "")
    size = line.find(" ")
    line = line[size + 1:]
    if size > 6:
        size = 6
    return f"<h{size}>{line}</h{size}>\n"


def translate(input_file, output_file):
    """Method that handles translation of markdown file"""
    with open(input_file, 'r') as in_f, open(output_file, 'w') as out_f:
        lines = in_f.readlines()
        length = len(lines)
        old_line = ""
        line_added = ""
        for index, line in enumerate(lines):
            new_line = lines[index + 1] if index + 1 < length else ""
            first_space = line.find(" ")
            if first_space > 0 and line.startswith("#" * first_space):
                current_line = translate_header(line)
            elif line.startswith("- "):
                current_line = translate_list(line, old_line, new_line, "ul")
            elif line.startswith("* "):
                current_line = translate_list(line, old_line, new_line, "ol")
            elif not line.startswith("\n"):
                current_line = translate_text(line, new_line, line_added)
            else:
                continue
            out_f.write(translate_line(current_line))
            line_added = current_line
            old_line = line


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=stderr)
        sys.exit(1)
    markdown_file = sys.argv[1]
    if not os.path.isfile(markdown_file):
        print(f"Missing {markdown_file}", file=stderr)
        sys.exit(1)
    translate(markdown_file, sys.argv[2] if argc > 2 else "README.html")
    sys.exit(0)
