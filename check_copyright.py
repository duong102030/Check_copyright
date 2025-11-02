#!/usr/bin/env python3
import sys
import os
from datetime import datetime

AUTHOR = "Nguyen Kha Duong"
CONTACT = "duong nguyen kha.daniel@gmail.com"

def get_copyright_header(filename):
    """Return the copyright header text."""
    today = datetime.now().strftime("%B %d, %Y")
    header = f"""/*
 * {os.path.basename(filename)}
 *
 *  Created on: {today}
 *      Author: {AUTHOR}
 *      Contact via email: {CONTACT}
 */
"""
    return header

def has_copyright(content):
    """Check if file already has NKD copyright header."""
    return "Author: Nguyen Kha Duong" in content or "Created on:" in content

def add_copyright(filename):
    """Add copyright header to a single file."""
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    if has_copyright(content):
        return False  # already has header

    header = get_copyright_header(filename)
    new_content = header + "\n" + content

    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[+] Added copyright header to {filename}")
    return True


def main():
    modified_files = sys.argv[1:]
    if not modified_files:
        print("No files to check.")
        return 0

    for filename in modified_files:
        if os.path.isfile(filename):
            add_copyright(filename)

    return 0


if __name__ == "__main__":
    sys.exit(main())
