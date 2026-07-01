"""Tests for git bootstrap validation."""

from pathlib import Path

import pytest

from py_rust_gdextension_cookiecutter.git import (
    clear_bootstrap_files,
    find_license_file,
    validate_bootstrap_contents,
)


def test_find_license_file(tmp_path: Path) -> None:
    (tmp_path / "LICENSE.md").write_text("MIT", encoding="utf-8")
    found = find_license_file(tmp_path)
    assert found is not None
    assert found.name == "LICENSE.md"


def test_validate_bootstrap_allows_readme_license_gitignore(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Hi", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("target/", encoding="utf-8")
    validate_bootstrap_contents(tmp_path)


def test_validate_bootstrap_rejects_extra_files(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    with pytest.raises(RuntimeError, match="unexpected directory"):
        validate_bootstrap_contents(tmp_path)


def test_clear_bootstrap_preserves_license_bytes(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Hi", encoding="utf-8")
    (tmp_path / "LICENSE").write_bytes(b"MIT\n")
    has_license, filename, content = clear_bootstrap_files(tmp_path)
    assert has_license is True
    assert filename == "LICENSE"
    assert content == b"MIT\n"
    assert not (tmp_path / "README.md").exists()
