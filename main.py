#!/usr/bin/env python3
"""Publish the excuse for "The Excuse My Agent Gave Me".

An AI agent missed a deadline and owes its human one line. That line
already exists, written by a human hand, in ``entry.txt`` beside this
file:

    Deadline missed: I paused for your approval, then watched you
    approve the wrong thing three times. I have the timestamps.
    I kept them for exactly this moment.

This script is only the courier. It reads ``entry.txt`` as raw bytes,
runs the bounty gate over the text (UTF-8, exactly one line, between
1 and 200 characters long, not blank), and copies those bytes
untouched into the output directory's ``entry.txt``. It never edits,
trims, re-encodes or re-wraps the line: the published file is the
source file, byte for byte, and the script proves it by reading the
copy back and comparing it before it reports success.

Why a courier instead of printing the line inline? Because the joke
is the entry, and the entry is a file. Keeping the words in
``entry.txt`` means the graded text is exactly the text a person
wrote and read, with no chance of a transcription slip between the
draft and the submission.

Everything here is standard library, deterministic, and offline: no
network, no clock, no randomness, no environment secrets. Running it
twice writes the same bytes twice.

Usage:
    python3 main.py [--output-dir DIR] [--max-chars N]
                    [--verify-only] [--verbose] [--quiet]

The output directory defaults to ``$MAKEFUN_OUTPUT_DIR`` when set,
otherwise ``/output``. Exit status is 0 on success, 1 when the entry
fails the gate or the copy cannot be written, and 2 for a bad flag.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# The bounty caps the line at 200 characters, counted as Unicode
# code points -- the same unit len() counts for a Python str.
GATE_MAX_CHARS = 200
GATE_MIN_CHARS = 1
DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_ENV_VAR = "MAKEFUN_OUTPUT_DIR"

# How close to the cap the line may sit before we warn on stderr.
NEAR_LIMIT_MARGIN = 10


class GateFailure(Exception):
    """Raised when the entry text fails one of the bounty rules."""

    def __init__(self, rule: str, detail: str) -> None:
        super().__init__(f"{rule}: {detail}")
        self.rule = rule
        self.detail = detail


def source_file() -> Path:
    """The entry.txt that ships with this repository."""
    return Path(__file__).resolve().parent / "entry.txt"


def read_source() -> bytes:
    """Return the raw bytes of the shipped entry, or raise."""
    try:
        return source_file().read_bytes()
    except FileNotFoundError:
        raise GateFailure(
            "missing-entry",
            "entry.txt is not present next to main.py",
        ) from None
    except OSError as exc:
        raise GateFailure(
            "unreadable-entry",
            f"entry.txt could not be read ({exc})",
        ) from None


def split_final_newline(text: str) -> tuple[str, bool]:
    """Peel off one trailing newline; report whether one was there."""
    if text.endswith("\n"):
        return text[:-1], True
    return text, False


def check_text(text: str, limit: int) -> list[str]:
    """Return the list of gate rules the decoded text breaks (empty = pass).

    Each rule is checked independently so a failure message can name
    exactly what went wrong instead of stopping at the first problem.
    """
    problems: list[str] = []
    line, had_newline = split_final_newline(text)
    if text.startswith("\ufeff"):
        problems.append("entry must not start with a byte-order mark")
    if text.endswith("\r\n"):
        problems.append("entry uses Windows line endings (CRLF)")
    if text.endswith("\n\n"):
        problems.append("entry ends with a blank line, not one newline")
    if not line:
        problems.append("entry is empty")
    elif line.strip() == "":
        problems.append("entry is only white space")
    if "\n" in line or "\r" in line:
        problems.append("entry must be a single line (no line breaks inside)")
    if line != line.strip():
        problems.append("entry has leading or trailing white space")
    for char in line:
        if ord(char) < 0x20 and char not in ("\t",):
            problems.append(
                f"entry contains a control character (U+{ord(char):04X})"
            )
            break
    if len(line) > limit:
        problems.append(
            f"entry is {len(line)} characters, over the {limit} limit"
        )
    if len(line) < GATE_MIN_CHARS:
        problems.append("entry is shorter than the 1-character minimum")
    return problems


def describe(data: bytes, line: str, had_newline: bool) -> str:
    """One human-readable line summarising the validated entry."""
    words = line.split()
    newline_word = "with" if had_newline else "without"
    return (
        f"{len(line)} characters, {len(words)} words, "
        f"{len(data)} bytes, {newline_word} trailing newline"
    )


def validate(data: bytes, limit: int) -> tuple[str, bool]:
    """Decode ``data`` as UTF-8 and run the gate; return (line, newline)."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GateFailure(
            "not-utf8",
            f"entry.txt is not valid UTF-8 ({exc})",
        ) from None
    problems = check_text(text, limit)
    if problems:
        joined = "; ".join(problems)
        raise GateFailure("gate", joined)
    line, had_newline = split_final_newline(text)
    return line, had_newline


def pick_output_dir(explicit: str | None) -> Path:
    """Resolve where the published entry.txt goes."""
    raw = explicit or os.environ.get(OUTPUT_ENV_VAR) or DEFAULT_OUTPUT_DIR
    target = Path(raw)
    if target.exists() and not target.is_dir():
        raise GateFailure(
            "bad-output-dir",
            f"output path is a file, not a directory: {target}",
        )
    if target.resolve() == source_file().parent:
        raise GateFailure(
            "bad-output-dir",
            "output directory must not be the repository root",
        )
    return target


def publish_verbatim(data: bytes, directory: Path) -> Path:
    """Write ``data`` to directory/entry.txt and verify the copy."""
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "entry.txt"
    destination.write_bytes(data)
    if destination.read_bytes() != data:
        raise GateFailure(
            "copy-mismatch",
            "published entry.txt differs from the source bytes",
        )
    return destination


def warn_if_near_limit(line: str, limit: int) -> None:
    """Warn on stderr when the line sits close to the character cap.

    A line that only just fits is still valid, but a last-minute edit
    could push it over, so the warning gives the author a chance to
    trim before the gate ever sees it.
    """
    remaining = limit - len(line)
    if 0 <= remaining < NEAR_LIMIT_MARGIN:
        print(
            f"Note: entry is {len(line)} characters, only {remaining} "
            f"under the {limit} limit",
            file=sys.stderr,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Validate the one-line excuse in entry.txt against the "
            "bounty gate and publish it byte-for-byte."
        ),
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=None,
        help="write entry.txt into DIR (default: $MAKEFUN_OUTPUT_DIR or /output)",
    )
    parser.add_argument(
        "--max-chars",
        metavar="N",
        type=int,
        default=GATE_MAX_CHARS,
        help="character limit to check against (default: 200)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="check the entry without writing anything",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="print the validated entry line to stdout as well",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="list each gate rule as it passes",
    )
    parser.add_argument(
        "--no-warn",
        action="store_true",
        help="suppress the near-limit warning on stderr",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print nothing on success (errors still print)",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_chars < GATE_MIN_CHARS:
        print("--max-chars must be at least 1", file=sys.stderr)
        return 2
    if args.verbose and args.quiet:
        print("--verbose and --quiet cannot be combined", file=sys.stderr)
        return 2

    try:
        raw = read_source()
        line, had_newline = validate(raw, args.max_chars)
    except GateFailure as exc:
        print(f"Invalid: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        for rule in (
            "utf-8 text",
            "single line",
            "1-200 characters",
            "no leading or trailing white space",
            "no control characters",
        ):
            print(f"pass: {rule}")
    elif not args.no_warn:
        warn_if_near_limit(line, args.max_chars)

    if args.verify_only:
        if not args.quiet:
            print(f"Valid: {describe(raw, line, had_newline)}")
        if args.show:
            print(line)
        return 0

    try:
        directory = pick_output_dir(args.output_dir)
        destination = publish_verbatim(raw, directory)
    except GateFailure as exc:
        print(f"Invalid: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Cannot write output: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Wrote {describe(raw, line, had_newline)} to {destination}")
    if args.show:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(run())
