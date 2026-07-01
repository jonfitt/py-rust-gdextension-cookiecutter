#!/usr/bin/env python3
"""Post-generation cleanup for optional template pieces."""

from __future__ import annotations

import shutil
import stat
from pathlib import Path


def _chmod_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> None:
    include_bevy = "{{ cookiecutter.include_bevy_demo }}" == "yes"
    project_slug = "{{ cookiecutter.project_slug }}"
    repo_root = Path(".").resolve()

    for pattern in (
        repo_root / ".githooks" / "pre-commit",
        * (repo_root / "scripts" / "linux").glob("*.sh"),
    ):
        if pattern.is_file():
            _chmod_executable(pattern)

    visualizer = repo_root / "examples" / f"{project_slug}_visualizer"
    bevy_deps = repo_root / "scripts" / "linux" / "setup-bevy-deps.sh"

    if not include_bevy:
        if visualizer.exists():
            shutil.rmtree(visualizer)
        if bevy_deps.is_file():
            bevy_deps.unlink()


if __name__ == "__main__":
    main()
