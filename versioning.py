"""Version file management for py-rust-gdextension-cookiecutter."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
BUMP_PATTERN = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
INIT_PY = ROOT / "src" / "py_rust_gdextension_cookiecutter" / "__init__.py"
INIT_VERSION_PATTERN = re.compile(r'^__version__ = "[^"]+"', re.MULTILINE)


def read_version(path: Path | None = None) -> str:
    """Return the semver string from VERSION."""
    version_path = path or VERSION_FILE
    if not version_path.is_file():
        raise FileNotFoundError(f"Missing version file: {version_path}")
    version = version_path.read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"VERSION must be semver major.minor.patch, got: {version!r}")
    return version


def write_version(version: str, path: Path | None = None) -> None:
    """Write a semver string to VERSION."""
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"Invalid semver: {version!r}")
    version_path = path or VERSION_FILE
    version_path.write_text(f"{version}\n", encoding="utf-8")


def sync_version_files(version: str) -> None:
    """Apply version to runtime metadata files."""
    write_version(version)
    if not INIT_PY.is_file():
        raise FileNotFoundError(f"Missing package init file: {INIT_PY}")
    init_text = INIT_PY.read_text(encoding="utf-8")
    if not INIT_VERSION_PATTERN.search(init_text):
        raise ValueError(f"Could not find __version__ assignment in {INIT_PY}")
    INIT_PY.write_text(
        INIT_VERSION_PATTERN.sub(f'__version__ = "{version}"', init_text),
        encoding="utf-8",
    )


def read_init_version() -> str:
    """Return __version__ from the package init module."""
    init_text = INIT_PY.read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"', init_text, re.MULTILINE)
    if match is None:
        raise ValueError(f"Could not parse __version__ in {INIT_PY}")
    return match.group(1)


def verify_version_sync() -> None:
    """Ensure VERSION matches __init__.py."""
    version = read_version()
    init_version = read_init_version()
    if version != init_version:
        raise RuntimeError(
            f"VERSION ({version}) does not match __init__.py ({init_version}). "
            "Run: invoke sync-version"
        )


def bump_semver(current: str, kind: str) -> str:
    """Return a new semver string after major, minor, or patch bump."""
    match = BUMP_PATTERN.fullmatch(current)
    if match is None:
        raise ValueError(f"Invalid semver: {current!r}")
    major, minor, patch = (int(match.group(i)) for i in range(1, 4))
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Bump kind must be major, minor, or patch, got: {kind!r}")


def choose_bump_kind(current: str) -> str:
    """Prompt interactively for a semver bump kind."""
    match = BUMP_PATTERN.fullmatch(current)
    if match is None:
        raise ValueError(f"Invalid semver: {current!r}")
    major, minor, patch = (int(match.group(i)) for i in range(1, 4))
    print(f"Current version: {current}")
    print()
    print("Select bump type:")
    print(f"  1) major ({major} -> {major + 1}.0.0)")
    print(f"  2) minor ({major}.{minor} -> {major}.{minor + 1}.0)")
    print(f"  3) patch ({current} -> {major}.{minor}.{patch + 1})")
    print()
    choice = input("Enter 1, 2, or 3 [3]: ").strip() or "3"
    mapping = {
        "1": "major",
        "2": "minor",
        "3": "patch",
        "major": "major",
        "minor": "minor",
        "patch": "patch",
    }
    if choice not in mapping:
        raise ValueError(f"Invalid choice: {choice!r}")
    return mapping[choice]


def _run_git(args: list[str], *, cwd: Path = ROOT) -> None:
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


def tag_exists(tag: str) -> bool:
    """Return True if an annotated or lightweight tag exists."""
    result = subprocess.run(
        ["git", "rev-parse", f"refs/tags/{tag}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def commit_and_tag(version: str, *, no_commit: bool) -> None:
    """Commit version files and create an annotated tag."""
    tag = f"v{version}"
    if tag_exists(tag):
        raise RuntimeError(f"Tag already exists: {tag}")

    if no_commit:
        print("Updated files only (--no-commit). Review changes, then commit and tag manually.")
        return

    _run_git(["add", "VERSION", str(INIT_PY.relative_to(ROOT))])
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        _run_git(["commit", "-m", f"Bump version to {version}"])
    _run_git(["tag", "-a", tag, "-m", f"Release {tag}"])
    print(f"Created commit and annotated tag {tag}.")
    print("Push with:")
    print("  git push origin HEAD")
    print(f"  git push origin {tag}")


def bump_version(*, kind: str | None = None, no_commit: bool = False) -> str:
    """Bump VERSION, sync files, and optionally commit and tag."""
    current = read_version()
    bump_kind = kind or choose_bump_kind(current)
    new_version = bump_semver(current, bump_kind)
    sync_version_files(new_version)
    print(f"Bumped version: {current} -> {new_version}")
    commit_and_tag(new_version, no_commit=no_commit)
    return new_version
