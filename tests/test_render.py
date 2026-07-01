"""Integration tests for template rendering."""

from __future__ import annotations

from pathlib import Path

import pytest

from py_rust_gdextension_cookiecutter.prompts import ProjectOptions
from py_rust_gdextension_cookiecutter.render import render_project_local


@pytest.fixture
def base_options() -> ProjectOptions:
    return ProjectOptions(
        remote_url="https://github.com/example/demo-lib.git",
        repo_name="demo_lib",
        project_slug="demo_lib",
        project_name_display="Demo Lib",
        description="Demo library",
        author="Test Author",
        email="test@example.com",
        godot_compatibility_minimum="4.3",
        godot_crate_version="0.5.4",
        include_bevy_demo=False,
        has_remote_license=False,
        license_file="",
        gd_crate_name="demo_lib_gd",
        gd_library_base="demo_lib_gd",
        output_parent=".",
    )


def test_render_creates_expected_files(tmp_path: Path, base_options: ProjectOptions) -> None:
    destination = tmp_path / "demo_lib"
    render_project_local(base_options, destination)

    expected = [
        "VERSION",
        "Cargo.toml",
        "src/lib.rs",
        "extensions/demo_lib_gd/src/lib.rs",
        "examples/demo_lib_cli/src/main.rs",
        "godot/project.godot",
        "godot/demo_lib.gdextension",
        "packaging/godot-addon/demo_lib.gdextension",
        ".github/workflows/rust.yml",
        ".gitlab-ci.yml",
        "scripts/linux/ci-check.sh",
        "scripts/linux/sync-version.sh",
        "scripts/linux/bump-version.sh",
        "scripts/windows/version-lib.ps1",
    ]
    for relative in expected:
        assert (destination / relative).is_file(), relative

    cargo_toml = (destination / "Cargo.toml").read_text(encoding="utf-8")
    assert "demo_lib_gd" in cargo_toml
    assert "visualizer" not in cargo_toml
    assert "[workspace.package]" in cargo_toml
    assert "version.workspace = true" in cargo_toml
    assert (destination / "VERSION").read_text(encoding="utf-8").strip() == "0.1.0"
    assert "{{" not in cargo_toml


def test_render_with_bevy_includes_visualizer(tmp_path: Path, base_options: ProjectOptions) -> None:
    options = ProjectOptions(
        **{
            **base_options.__dict__,
            "include_bevy_demo": True,
        }
    )
    destination = tmp_path / "demo_lib"
    render_project_local(options, destination)

    assert (destination / "examples/demo_lib_visualizer/src/main.rs").is_file()
    cargo_toml = (destination / "Cargo.toml").read_text(encoding="utf-8")
    assert "demo_lib_visualizer" in cargo_toml


def test_render_with_remote_license(tmp_path: Path, base_options: ProjectOptions) -> None:
    options = ProjectOptions(
        **{
            **base_options.__dict__,
            "has_remote_license": True,
            "license_file": "LICENSE.md",
        }
    )
    destination = tmp_path / "demo_lib"
    render_project_local(options, destination)

    cargo_toml = (destination / "Cargo.toml").read_text(encoding="utf-8")
    assert 'license-file = "LICENSE.md"' in cargo_toml
    assert "license-file.workspace = true" in cargo_toml
    assert "license.workspace = true" not in cargo_toml

    gd_cargo = (destination / "extensions/demo_lib_gd/Cargo.toml").read_text(encoding="utf-8")
    assert "license-file.workspace = true" in gd_cargo
    assert "version.workspace = true" in gd_cargo
