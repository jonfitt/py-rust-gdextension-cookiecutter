"""Tests for versioning helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import versioning


def test_bump_semver_patch() -> None:
    assert versioning.bump_semver("1.2.3", "patch") == "1.2.4"


def test_bump_semver_minor() -> None:
    assert versioning.bump_semver("1.2.3", "minor") == "1.3.0"


def test_bump_semver_major() -> None:
    assert versioning.bump_semver("1.2.3", "major") == "2.0.0"


def test_sync_version_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    version_file = tmp_path / "VERSION"
    init_py = tmp_path / "src" / "pkg" / "__init__.py"
    init_py.parent.mkdir(parents=True)
    version_file.write_text("0.1.0\n", encoding="utf-8")
    init_py.write_text('__version__ = "0.1.0"\n', encoding="utf-8")

    monkeypatch.setattr(versioning, "VERSION_FILE", version_file)
    monkeypatch.setattr(versioning, "INIT_PY", init_py)

    versioning.sync_version_files("0.2.0")

    assert version_file.read_text(encoding="utf-8").strip() == "0.2.0"
    assert '__version__ = "0.2.0"' in init_py.read_text(encoding="utf-8")


def test_verify_version_sync_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    version_file = tmp_path / "VERSION"
    init_py = tmp_path / "src" / "pkg" / "__init__.py"
    init_py.parent.mkdir(parents=True)
    version_file.write_text("1.0.0\n", encoding="utf-8")
    init_py.write_text('__version__ = "1.0.0"\n', encoding="utf-8")

    monkeypatch.setattr(versioning, "VERSION_FILE", version_file)
    monkeypatch.setattr(versioning, "INIT_PY", init_py)

    versioning.verify_version_sync()


def test_verify_version_sync_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    version_file = tmp_path / "VERSION"
    init_py = tmp_path / "src" / "pkg" / "__init__.py"
    init_py.parent.mkdir(parents=True)
    version_file.write_text("1.0.0\n", encoding="utf-8")
    init_py.write_text('__version__ = "1.0.1"\n', encoding="utf-8")

    monkeypatch.setattr(versioning, "VERSION_FILE", version_file)
    monkeypatch.setattr(versioning, "INIT_PY", init_py)

    with pytest.raises(RuntimeError, match="does not match"):
        versioning.verify_version_sync()
