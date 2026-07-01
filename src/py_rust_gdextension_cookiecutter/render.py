"""Render the cookiecutter template into a cloned repository."""

from __future__ import annotations

import shutil
import tempfile
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path

from cookiecutter.main import cookiecutter

from py_rust_gdextension_cookiecutter.git import (
    clone_repository,
    merge_rendered_tree,
    restore_license,
)
from py_rust_gdextension_cookiecutter.prompts import ProjectOptions, to_cookiecutter_context


def template_directory() -> Path:
    return Path(str(resources.files("py_rust_gdextension_cookiecutter") / "template"))


def render_project(options: ProjectOptions) -> Path:
    """Clone the remote, render the template, and return the project path."""
    output_parent = Path(options.output_parent).resolve()
    destination = output_parent / options.repo_name

    clone_result = clone_repository(options.remote_url, destination)
    options = ProjectOptions(
        **{
            **options.__dict__,
            "has_remote_license": clone_result.has_remote_license,
            "license_file": clone_result.license_filename or "",
        }
    )

    context = to_cookiecutter_context(
        options,
        year=str(datetime.now(UTC).year),
    )

    with tempfile.TemporaryDirectory(prefix="py-rust-gd-") as tmp_dir:
        rendered_root = Path(
            cookiecutter(
                str(template_directory()),
                no_input=True,
                extra_context=context,
                output_dir=tmp_dir,
                overwrite_if_exists=True,
            )
        )
        merge_rendered_tree(rendered_root, destination)

    if clone_result.has_remote_license:
        assert clone_result.license_filename is not None
        assert clone_result.license_bytes is not None
        restore_license(
            destination,
            clone_result.license_filename,
            clone_result.license_bytes,
        )

    return destination


def render_project_local(options: ProjectOptions, destination: Path) -> Path:
    """Render without cloning (for tests)."""
    destination.mkdir(parents=True, exist_ok=True)
    context = to_cookiecutter_context(
        options,
        year=str(datetime.now(UTC).year),
    )

    with tempfile.TemporaryDirectory(prefix="py-rust-gd-") as tmp_dir:
        rendered_root = Path(
            cookiecutter(
                str(template_directory()),
                no_input=True,
                extra_context=context,
                output_dir=tmp_dir,
                overwrite_if_exists=True,
            )
        )
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(rendered_root, destination)

    return destination
