#!/usr/bin/env python3
"""Post-generation cleanup for optional template pieces."""

from __future__ import annotations

import shutil
import stat
import subprocess
from pathlib import Path

AUTHOR = "{{ cookiecutter.author }}".strip()
EMAIL = "{{ cookiecutter.email }}".strip()


def _chmod_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _setup_local_gitconfig(repo_root: Path) -> None:
    """Create a gitignored .gitconfig and wire it into the local clone."""
    gitconfig = repo_root / ".gitconfig"
    if gitconfig.is_file():
        return

    example = repo_root / ".gitconfig.example"
    if AUTHOR and EMAIL:
        gitconfig.write_text(
            "# Local Git identity for this repository (not committed).\n"
            "[user]\n"
            f"\temail = {EMAIL}\n"
            f"\tname = {AUTHOR}\n",
            encoding="utf-8",
        )
    elif example.is_file():
        shutil.copy(example, gitconfig)

    if not gitconfig.is_file() or not (repo_root / ".git").exists():
        return

    subprocess.run(
        ["git", "config", "--local", "include.path", "../.gitconfig"],
        cwd=repo_root,
        check=True,
    )


def main() -> None:
    include_bevy = "{{ cookiecutter.include_bevy_demo }}" == "yes"
    project_slug = "{{ cookiecutter.project_slug }}"
    repo_root = Path(".").resolve()

    for pattern in (
        repo_root / ".githooks" / "pre-commit",
        *(repo_root / "scripts" / "linux").glob("*.sh"),
    ):
        if pattern.is_file():
            _chmod_executable(pattern)

    _setup_local_gitconfig(repo_root)

    visualizer = repo_root / "examples" / f"{project_slug}_visualizer"
    bevy_deps = repo_root / "scripts" / "linux" / "setup-bevy-deps.sh"

    if not include_bevy:
        if visualizer.exists():
            shutil.rmtree(visualizer)
        if bevy_deps.is_file():
            bevy_deps.unlink()


if __name__ == "__main__":
    main()
