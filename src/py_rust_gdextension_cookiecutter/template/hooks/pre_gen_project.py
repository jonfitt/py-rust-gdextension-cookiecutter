#!/usr/bin/env python3
"""Validate cookiecutter context before generation."""

import re
import sys


def main() -> int:
    slug = "{{ cookiecutter.project_slug }}"
    if not re.fullmatch(r"[a-z][a-z0-9_]*", slug):
        print(
            f"error: invalid Rust crate name {slug!r}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
