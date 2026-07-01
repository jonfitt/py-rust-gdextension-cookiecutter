# {{ cookiecutter.project_name_display }} — project guide for Python developers

<!-- TODO: Expand this guide as the project grows. -->

| Python | Rust (this project) |
|--------|---------------------|
| `pyproject.toml` | `Cargo.toml` |
| `import mypackage` | `use {{ cookiecutter.project_slug }}::...` |
| `pytest` | `cargo test` |
| Virtualenv | `target/` build directory |

## Repository layout

```text
{{ cookiecutter.repo_name }}/
├── VERSION                         # single source of truth for release version
├── Cargo.toml                      # workspace + {{ cookiecutter.project_slug }} library package
├── src/                            # {{ cookiecutter.project_slug }} library
├── extensions/{{ cookiecutter.gd_crate_name }}/
├── examples/
├── godot/
└── docs/                           # architecture, Godot API, CI, project guide
```

## Cargo.toml files

### Root `Cargo.toml` (workspace + library)

```toml
[workspace.package]
version = "0.1.0"
{% if cookiecutter.has_remote_license == "yes" %}
license-file = "{{ cookiecutter.license_file }}"
{% endif %}

[package]
name = "{{ cookiecutter.project_slug }}"
version.workspace = true
edition = "2024"
description = "..."
{% if cookiecutter.has_remote_license == "yes" %}
license-file.workspace = true
{% endif %}
```

Release version lives in root **`VERSION`** (not duplicated by hand in each crate). Root
`[workspace.package] version` and this document are synced from it via
`scripts/linux/sync-version.sh` or `scripts/windows/sync-version.cmd`.
Workspace members set `version.workspace = true`.

## Common commands

```bash
cargo build
cargo test
cargo run -p {{ cookiecutter.project_slug }}_cli
cargo build -p {{ cookiecutter.gd_crate_name }}
```
