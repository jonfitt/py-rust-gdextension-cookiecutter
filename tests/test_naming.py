"""Tests for naming helpers."""

import pytest

from py_rust_gdextension_cookiecutter.naming import (
    display_name_from_slug,
    gd_crate_name,
    repo_name_from_remote,
    slugify,
    validate_rust_crate_name,
)


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        ("git@github.com:org/my-lib.git", "my-lib"),
        ("https://github.com/org/my-lib.git", "my-lib"),
        ("https://github.com/org/my-lib", "my-lib"),
        ("git@gitlab.com:team/sub/my_project.git", "my_project"),
    ],
)
def test_repo_name_from_remote(remote: str, expected: str) -> None:
    assert repo_name_from_remote(remote) == expected


def test_slugify_display_name() -> None:
    assert slugify("My Awesome Lib") == "my_awesome_lib"
    assert display_name_from_slug("my_awesome_lib") == "My Awesome Lib"


def test_gd_crate_name() -> None:
    assert gd_crate_name("fibonacci_sphere") == "fibonacci_sphere_gd"


def test_validate_rust_crate_name_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        validate_rust_crate_name("1bad")


def test_validate_rust_crate_name_accepts_valid() -> None:
    validate_rust_crate_name("good_name")
