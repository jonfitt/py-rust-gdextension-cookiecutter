# py-rust-gdextension-cookiecutter

Generate Rust GDExtension workspaces for Godot 4 by cloning a git remote and scaffolding a complete project layout.

## Install

The easiest way to run the generator is to download the `.whl` from a [GitHub Release](https://github.com/jonfitt/py-rust-gdextension-cookiecutter/releases) and invoke it with `uvx` — no virtualenv and no install step:

```bash
uvx --from py_rust_gdextension_cookiecutter-0.1.0-py3-none-any.whl py-rust-gd
```

Replace the wheel filename with the version you downloaded.

Alternatively, install with pip:

```bash
pip install py-rust-gdextension-cookiecutter
```

Or from a checkout:

```bash
pip install .
```

## Usage

```bash
py-rust-gd
```

The CLI clones your git remote (empty or containing only `README`, `LICENSE`, and/or `.gitignore`), then scaffolds:

- Core Rust library crate
- Godot 4 GDExtension (`cdylib`)
- Native CLI demo (and optional Bevy visualizer)
- Godot demo project
- CI workflows, git hooks, and release packaging scripts
- Documentation stubs

### Flags

```bash
py-rust-gd \
  --remote git@github.com:you/my-lib.git \
  --project-name "My Lib" \
  --no-bevy \
  --output-dir .
```

### Remote repository contents

The remote may be empty or contain only:

- `README*` (overwritten)
- `LICENSE`, `LICENSE.md`, or `LICENSE.txt` (preserved; used as `license-file` in `Cargo.toml`)
- `.gitignore` (overwritten)

Any other files or directories cause the generator to fail with a clear error.

## Development

```bash
pip install -e ".[dev]"
pre-commit install
```

### Invoke tasks

| Task | Description |
|------|-------------|
| `invoke format` | Apply Ruff formatting |
| `invoke lint` | Ruff format check, Ruff lint, and Mypy |
| `invoke test` | Run pytest |
| `invoke ci` | Lint and test (same as GitHub Actions) |
| `invoke sync-version` | Apply `VERSION` to `__init__.py` |
| `invoke bump` | Bump `VERSION`, commit, and tag `vX.Y.Z` |

```bash
invoke lint
invoke test
invoke ci
invoke bump
```

Pre-commit runs `invoke lint` on each commit. GitHub Actions runs `invoke ci` on pushes and pull requests to `main`.

## Releasing

`VERSION` at the repository root is the single source of truth (Hatch reads it at build time).

```bash
invoke bump              # interactive major/minor/patch selection
invoke bump --kind patch
invoke bump --no-commit  # update files only
git push origin HEAD
git push origin v0.1.0
```

Pushing a `vX.Y.Z` tag triggers [`.github/workflows/release.yml`](.github/workflows/release.yml), which builds a platform-independent wheel (`py3-none-any`) and sdist, then attaches them to a GitHub Release.
