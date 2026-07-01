# {{ cookiecutter.project_name_display }}

{{ cookiecutter.description }}

## Workspace

| Crate / path | Role |
|--------------|------|
| [`{{ cookiecutter.project_slug }}`](./) | Core library |
| [`examples/{{ cookiecutter.project_slug }}_cli`](./examples/{{ cookiecutter.project_slug }}_cli/) | Native CLI demo |
{% if cookiecutter.include_bevy_demo == "yes" %}
| [`examples/{{ cookiecutter.project_slug }}_visualizer`](./examples/{{ cookiecutter.project_slug }}_visualizer/) | Bevy visualizer |
{% endif %}
| [`extensions/{{ cookiecutter.gd_crate_name }}`](./extensions/{{ cookiecutter.gd_crate_name }}/) | Godot 4 GDExtension |
| [`godot/`](./godot/) | Godot 4 demo project |

## Quick start

```bash
cargo build -p {{ cookiecutter.gd_crate_name }}
cargo test
cargo run -p {{ cookiecutter.project_slug }}_cli
```

Open `godot/project.godot` in Godot {{ cookiecutter.godot_compatibility_minimum }}+ and run the demo scene.

<!-- TODO: Document your library API and Godot classes (see docs/). -->

## Development

```bash
./scripts/linux/ci-check.sh
./scripts/linux/setup-git-hooks.sh
```

See [`docs/ci.md`](./docs/ci.md) for GitHub Actions and GitLab CI details.

## Releasing

Bump the version, then push the commit and tag:

```bash
./scripts/linux/bump-version.sh
git push origin HEAD
git push origin v0.1.0
```

Pushing a `vX.Y.Z` tag triggers the **release pipeline** on your git host (if configured):

- **GitHub:** [`.github/workflows/release.yml`](./.github/workflows/release.yml) — builds per-platform GDExtension binaries and publishes addon/demo zips to GitHub Releases.
- **GitLab:** [`.gitlab-ci.yml`](./.gitlab-ci.yml) — same packaging, published as a GitLab Release.

Remove the CI config you do not use. Full details: [`docs/ci.md`](./docs/ci.md).

### Manual packaging

To assemble release zips locally (after building all platform binaries):

```bash
./scripts/linux/package-godot-release.sh 0.1.0 \
  path/to/lib{{ cookiecutter.gd_library_base }}.so \
  path/to/{{ cookiecutter.gd_library_base }}.dll \
  path/to/lib{{ cookiecutter.gd_library_base }}.dylib
```
