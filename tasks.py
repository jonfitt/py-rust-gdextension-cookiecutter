"""Invoke tasks for linting, tests, and releases."""

from __future__ import annotations

from invoke import Context, task  # type: ignore[attr-defined]
from versioning import bump_version, read_version, sync_version_files, verify_version_sync

PYTHON_TARGETS = "src/py_rust_gdextension_cookiecutter tests tasks.py versioning.py"


@task
def format(c: Context) -> None:
    """Apply Ruff formatting."""
    c.run(f"ruff format {PYTHON_TARGETS}", pty=True)


@task
def lint(c: Context) -> None:
    """Run Ruff format check, Ruff lint, Mypy, and VERSION sync verification."""
    c.run(f"ruff format --check {PYTHON_TARGETS}", pty=True)
    c.run(f"ruff check {PYTHON_TARGETS}", pty=True)
    c.run("mypy src/py_rust_gdextension_cookiecutter tasks.py versioning.py tests", pty=True)
    verify_version_sync()


@task
def test(c: Context) -> None:
    """Run the test suite."""
    c.run("pytest", pty=True)


@task
def ci(c: Context) -> None:
    """Run linting and tests (used by GitHub Actions)."""
    lint(c)
    test(c)


@task
def sync_version(_c: Context) -> None:
    """Apply VERSION to __init__.py."""
    version = read_version()
    sync_version_files(version)
    print(f"Synced version {version} from VERSION.")


@task(
    optional=["kind"],
    help={
        "kind": "Semver bump: major, minor, or patch (prompted if omitted).",
        "no_commit": "Update VERSION only; do not commit or tag.",
    },
)
def bump(_c: Context, kind: str | None = None, no_commit: bool = False) -> None:
    """Bump VERSION, sync metadata, commit, and create tag vX.Y.Z."""
    bump_version(kind=kind, no_commit=no_commit)
