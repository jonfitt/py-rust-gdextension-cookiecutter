"""Clone a git remote and prepare the directory for scaffolding."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

LICENSE_CANDIDATES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "License")


@dataclass(frozen=True)
class CloneResult:
    path: Path
    has_remote_license: bool
    license_filename: str | None
    license_bytes: bytes | None


def _run_git(args: list[str], *, cwd: Path | None = None) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")


def find_license_file(directory: Path) -> Path | None:
    for name in LICENSE_CANDIDATES:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def _is_allowed_bootstrap_file(path: Path) -> bool:
    lower = path.name.lower()
    if lower == ".gitignore":
        return True
    if lower.startswith("readme"):
        return True
    return lower in {"license", "license.md", "license.txt"}


def validate_bootstrap_contents(directory: Path) -> None:
    """Ensure the clone only contains files we know how to merge."""
    for entry in directory.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir():
            raise RuntimeError(
                f"Remote repository contains unexpected directory {entry.name!r}. "
                "Only an empty repo or one with README, LICENSE, and/or .gitignore is supported."
            )
        if not _is_allowed_bootstrap_file(entry):
            raise RuntimeError(
                f"Remote repository contains unexpected file {entry.name!r}. "
                "Only an empty repo or one with README, LICENSE, and/or .gitignore is supported."
            )


def clear_bootstrap_files(directory: Path) -> tuple[bool, str | None, bytes | None]:
    """Remove bootstrap files before rendering; preserve license bytes if present."""
    license_path = find_license_file(directory)
    license_filename: str | None = None
    license_bytes: bytes | None = None
    if license_path is not None:
        license_filename = license_path.name
        license_bytes = license_path.read_bytes()

    for entry in list(directory.iterdir()):
        if entry.name == ".git":
            continue
        if entry.is_file():
            entry.unlink()

    return license_filename is not None, license_filename, license_bytes


def restore_license(directory: Path, filename: str, content: bytes) -> None:
    (directory / filename).write_bytes(content)


def clone_repository(remote_url: str, destination: Path) -> CloneResult:
    """Clone remote into destination and validate bootstrap files."""
    if destination.exists():
        if any(destination.iterdir()):
            raise RuntimeError(f"Destination already exists and is not empty: {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)

    _run_git(["clone", remote_url, str(destination)])

    validate_bootstrap_contents(destination)
    has_license, license_filename, license_bytes = clear_bootstrap_files(destination)

    return CloneResult(
        path=destination,
        has_remote_license=has_license,
        license_filename=license_filename,
        license_bytes=license_bytes,
    )


def merge_rendered_tree(source: Path, destination: Path) -> None:
    """Copy rendered scaffold into the cloned repository."""
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
