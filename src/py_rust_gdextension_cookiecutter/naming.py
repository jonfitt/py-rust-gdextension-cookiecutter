"""Derive crate and repository names from user input."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def repo_name_from_remote(remote_url: str) -> str:
    """Return the repository directory name from a git remote URL."""
    url = remote_url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    if url.startswith("git@"):
        # git@github.com:org/repo
        _, _, path = url.partition(":")
        name = path.rsplit("/", 1)[-1]
    else:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        name = path.rsplit("/", 1)[-1]

    if not name:
        raise ValueError(f"Could not determine repository name from remote: {remote_url!r}")
    return name


def slugify(name: str) -> str:
    """Convert a display name to a valid Rust crate name (snake_case)."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    if not slug:
        raise ValueError("Project name must contain at least one letter or digit.")
    if slug[0].isdigit():
        slug = f"project_{slug}"
    return slug


def display_name_from_slug(slug: str) -> str:
    """Turn a snake_case slug into a title-case display name."""
    return " ".join(part.capitalize() for part in slug.split("_"))


def gd_crate_name(project_slug: str) -> str:
    return f"{project_slug}_gd"


def gd_library_base(project_slug: str) -> str:
    return gd_crate_name(project_slug)


def validate_rust_crate_name(name: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(
            f"Invalid Rust crate name {name!r}. "
            "Use lowercase letters, digits, and underscores; start with a letter."
        )
