#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import subprocess
import sys

SUPPORTED_EXTS = {".c", ".h", ".cpp", ".hpp", ".ino"}

HEADER_TEMPLATE = """/*
 * {filename}
 *
 *  Created on: {created_on}
 *      Author: {author}
 */
"""

def is_added_in_index(path: str) -> bool:
    """
    True nếu file có status 'A' trong index (staged).
    Chuẩn hoá về đường dẫn tương đối với repo root để so sánh ổn định trên Win/*nix.
    """
    try:
        # Lấy repo root
        toplevel = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True
        ).strip()
        # Path relative với repo root
        rel = os.path.relpath(os.path.abspath(path), start=toplevel)

        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-status", "--", rel],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        for line in out.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2 and os.path.normpath(parts[1]) == os.path.normpath(rel):
                return parts[0].strip().upper().startswith("A")
    except Exception:
        return False
    return False


def detect_line_ending(raw_bytes: bytes) -> str:
    # Bảo toàn CRLF nếu thấy trong nội dung
    if b"\r\n" in raw_bytes:
        return "\r\n"
    return "\n"


def has_our_header(text: str, author: str) -> bool:
    # Header đã tồn tại?
    # Kiểm tra vài key lines để idempotent
    if "Created on:" in text and f"Author: {author}" in text:
        # thêm điều kiện block comment mở đầu
        if text.lstrip().startswith("/*"):
            return True
    return False


def insert_after_shebang(text: str, header: str, newline: str) -> str:
    # Nếu có shebang ở dòng đầu, chèn header sau shebang
    if text.startswith("#!"):
        first_newline = text.find("\n")
        if first_newline == -1:
            # file 1 dòng shebang -> thêm newline + header + newline
            return text + newline + header + newline
        # giữ nguyên shebang dòng đầu
        return text[: first_newline + 1] + header + newline + text[first_newline + 1 :]
    else:
        return header + newline + text


def format_date_human(d: dt.datetime) -> str:
    # Windows không hỗ trợ %-d, nên tự ráp phần ngày
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def process_file(path: str, author: str) -> int:
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTS:
        return 0  # bỏ qua

    # Chỉ làm với file Added trong index
    if not is_added_in_index(path):
        return 0

    # Đọc file
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except Exception:
        return 0

    newline = detect_line_ending(raw)
    try:
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        return 0

    if has_our_header(text, author):
        return 0  # đã có header

    # Tạo header
    today = dt.datetime.now()
    created_on = format_date_human(today)
    filename = os.path.basename(path)
    header = HEADER_TEMPLATE.format(filename=filename, created_on=created_on, author=author).strip()

    # Nếu đầu file có BOM, giữ nguyên
    bom = ""
    if text.startswith("\ufeff"):
        bom = "\ufeff"
        text = text.lstrip("\ufeff")

    # Chèn header (sau shebang nếu có)
    new_text = insert_after_shebang(text, header, newline)
    new_text = bom + new_text

    # Ghi đè lại
    with open(path, "wb") as f:
        f.write(new_text.encode("utf-8"))

    # Add lại vào index vì pre-commit yêu cầu file đã được sửa phải re-stage
    try:
        subprocess.check_call(["git", "add", "--", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    return 1


def main():
    parser = argparse.ArgumentParser(description="Insert NKD copyright header for newly added files.")
    parser.add_argument("--author", default="Nguyen Kha Duong", help="Author name to place in header.")
    parser.add_argument("files", nargs="*", help="Files passed by pre-commit.")
    args = parser.parse_args()

    changed = 0
    for path in args.files:
        changed += process_file(path, args.author)

    # pre-commit: exit 0 ok; non-zero để hiển thị “Files were modified by hook”
    # Nhưng chúng ta muốn trả 0 dù có sửa, để không fail commit (pre-commit sẽ tự hiển thị diff)
    return 0


if __name__ == "__main__":
    sys.exit(main())
