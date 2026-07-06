"""Command-line interface for generating Rust GDExtension projects."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from py_rust_gdextension_cookiecutter.prompts import collect_options
from py_rust_gdextension_cookiecutter.render import render_project

console = Console()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--remote", "-r", help="Git remote URL for an empty or bootstrap repository.")
@click.option("--project-name", "-n", help="Display and crate name (defaults from remote).")
@click.option("--description", "-d", help="Short project description.")
@click.option("--author", help="Author name for Cargo.toml.")
@click.option("--email", help="Author email for Cargo.toml.")
@click.option("--godot-version", default=None, help="Godot compatibility minimum (default: 4.3).")
@click.option(
    "--godot-crate-version",
    default=None,
    help="Version of the godot Rust crate (default: 0.5.4).",
)
@click.option("--bevy/--no-bevy", "include_bevy_demo", default=None, help="Include Bevy example.")
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Parent directory for the cloned repository.",
)
def main(
    remote: str | None,
    project_name: str | None,
    description: str | None,
    author: str | None,
    email: str | None,
    godot_version: str | None,
    godot_crate_version: str | None,
    include_bevy_demo: bool | None,
    output_dir: Path | None,
) -> None:
    """Generate a Rust GDExtension workspace by cloning a git remote and scaffolding into it."""
    try:
        options = collect_options(
            remote=remote,
            project_name=project_name,
            description=description,
            author=author,
            email=email,
            godot_version=godot_version,
            godot_crate_version=godot_crate_version,
            include_bevy_demo=include_bevy_demo,
            output_dir=str(output_dir) if output_dir is not None else None,
        )
        project_path = render_project(options)
    except (RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"\n[bold green]Project created at[/bold green] {project_path}")
    console.print("\nNext steps:")
    console.print(f"  cd {project_path.name}")
    console.print("  ./scripts/linux/setup-git-hooks.sh    # hooks + local .gitconfig")
    console.print("  # Edit .gitconfig if needed (gitignored; not pushed)")
    console.print(f"  cargo build -p {options.gd_crate_name}")
    console.print("  # Open godot/ in Godot 4 and run the demo scene")
    if options.include_bevy_demo:
        console.print(f"  cargo run -p {options.project_slug}_visualizer")


if __name__ == "__main__":
    main()
