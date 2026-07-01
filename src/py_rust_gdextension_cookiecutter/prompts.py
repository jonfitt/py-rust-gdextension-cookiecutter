"""Interactive prompts for project generation."""

from __future__ import annotations

from dataclasses import dataclass

import click

from py_rust_gdextension_cookiecutter.naming import (
    display_name_from_slug,
    gd_crate_name,
    gd_library_base,
    repo_name_from_remote,
    slugify,
    validate_rust_crate_name,
)


@dataclass(frozen=True)
class ProjectOptions:
    remote_url: str
    repo_name: str
    project_slug: str
    project_name_display: str
    description: str
    author: str
    email: str
    godot_compatibility_minimum: str
    godot_crate_version: str
    include_bevy_demo: bool
    has_remote_license: bool
    license_file: str
    gd_crate_name: str
    gd_library_base: str
    output_parent: str


def collect_options(
    *,
    remote: str | None,
    project_name: str | None,
    description: str | None,
    author: str | None,
    email: str | None,
    godot_version: str | None,
    godot_crate_version: str | None,
    include_bevy_demo: bool | None,
    output_dir: str | None,
    has_remote_license: bool = False,
) -> ProjectOptions:
    """Collect generation options interactively or from CLI flags."""
    if not remote:
        remote = click.prompt("Git remote URL", type=str).strip()
    if not remote:
        raise click.ClickException("Git remote URL is required.")

    default_repo_name = repo_name_from_remote(remote)
    if not project_name:
        project_name = click.prompt(
            "Project name",
            default=display_name_from_slug(slugify(default_repo_name)),
        ).strip()

    project_slug = slugify(project_name)
    validate_rust_crate_name(project_slug)

    if description is None:
        description = click.prompt(
            "Short description",
            default=f"{project_name} — Rust library with Godot 4 GDExtension bindings",
        ).strip()

    if author is None:
        author = click.prompt("Author name", default="", show_default=False).strip()

    if email is None:
        email = click.prompt("Author email", default="", show_default=False).strip()

    if godot_version is None:
        godot_version = click.prompt("Godot compatibility minimum", default="4.3").strip()

    if godot_crate_version is None:
        godot_crate_version = click.prompt("godot crate version", default="0.5.4").strip()

    if include_bevy_demo is None:
        include_bevy_demo = click.confirm(
            "Include a Bevy visualizer example?",
            default=False,
        )

    if output_dir is None:
        output_dir = click.prompt("Output parent directory", default=".").strip()

    repo_name = default_repo_name

    return ProjectOptions(
        remote_url=remote,
        repo_name=repo_name,
        project_slug=project_slug,
        project_name_display=project_name,
        description=description,
        author=author,
        email=email,
        godot_compatibility_minimum=godot_version,
        godot_crate_version=godot_crate_version,
        include_bevy_demo=include_bevy_demo,
        has_remote_license=has_remote_license,
        license_file="",
        gd_crate_name=gd_crate_name(project_slug),
        gd_library_base=gd_library_base(project_slug),
        output_parent=output_dir,
    )


def to_cookiecutter_context(options: ProjectOptions, *, year: str) -> dict[str, str]:
    """Convert options to cookiecutter extra_context values (all strings)."""
    return {
        "repo_name": options.repo_name,
        "project_slug": options.project_slug,
        "project_name_display": options.project_name_display,
        "description": options.description,
        "author": options.author,
        "email": options.email,
        "godot_compatibility_minimum": options.godot_compatibility_minimum,
        "godot_crate_version": options.godot_crate_version,
        "include_bevy_demo": "yes" if options.include_bevy_demo else "no",
        "has_remote_license": "yes" if options.has_remote_license else "no",
        "license_file": options.license_file,
        "gd_crate_name": options.gd_crate_name,
        "gd_library_base": options.gd_library_base,
        "year": year,
    }
