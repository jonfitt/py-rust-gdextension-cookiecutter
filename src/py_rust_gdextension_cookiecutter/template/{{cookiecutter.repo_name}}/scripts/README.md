# Project scripts

| Setup | Scripts | Pre-commit install |
|-------|---------|-------------------|
| Linux / WSL | `scripts/linux/*.sh` | `./scripts/linux/setup-git-hooks.sh` |
| Windows | `scripts/windows/*.ps1` or `*.cmd` | `scripts\windows\setup-git-hooks.cmd` |

## Linux / WSL

```bash
./scripts/linux/ci-check.sh
./scripts/linux/setup-git-hooks.sh
./scripts/linux/setup-branch-protection.sh
./scripts/linux/package-godot-release.sh VERSION linux.so win.dll mac.dylib
./scripts/linux/bump-version.sh
./scripts/linux/sync-version.sh
```

{% if cookiecutter.include_bevy_demo == "yes" %}
```bash
./scripts/linux/setup-bevy-deps.sh
```
{% endif %}

## Windows

```cmd
scripts\windows\ci-check.cmd
scripts\windows\setup-git-hooks.cmd
scripts\windows\setup-branch-protection.cmd
scripts\windows\bump-version.cmd
scripts\windows\sync-version.cmd
```

PowerShell equivalents:

```powershell
.\scripts\windows\ci-check.ps1
.\scripts\windows\setup-git-hooks.ps1
.\scripts\windows\setup-branch-protection.ps1
.\scripts\windows\bump-version.ps1
.\scripts\windows\sync-version.ps1
```

## Versioning

`VERSION` at the repository root is the single source of truth. Workspace crates inherit
`version.workspace = true` from `[workspace.package]` in root `Cargo.toml`. Cargo cannot read
`VERSION` directly; run `sync-version` after editing `VERSION` by hand (updates `Cargo.toml`,
`Cargo.lock`, and `docs/description.md`), or use `bump-version` before a release (syncs
files, commits, and creates `vX.Y.Z`).

## CI

`ci-check` matches the test jobs in [`.github/workflows/rust.yml`](../.github/workflows/rust.yml)
and [`.gitlab-ci.yml`](../.gitlab-ci.yml). See [`docs/ci.md`](../docs/ci.md).

## Git hooks

`.githooks/pre-commit` verifies the local commit email (when [`.gitconfig`](../.gitconfig)
exists), then runs the platform CI script (`ci-check`), including VERSION sync verification.

Copy [`.gitconfig.example`](../.gitconfig.example) to `.gitconfig` (gitignored) and set your
name and email. The setup script creates `.gitconfig` from the example if missing and includes
it in your local `.git/config` so it overrides a global Git identity for this repo only.

```bash
./scripts/linux/setup-git-hooks.sh
```

```cmd
scripts\windows\setup-git-hooks.cmd
```

## GitHub branch protection

After creating the repository on GitHub and running `gh auth login`, apply branch protection
from the repository root. The script reads `owner/repo` from `git remote origin` and configures
that owner as the sole merger and code owner.

```bash
./scripts/linux/setup-branch-protection.sh
```

```cmd
scripts\windows\setup-branch-protection.cmd
```

`scripts/github-protection/apply.sh` configures:

- Squash-only merges and auto-delete merged branches
- Dependabot security updates, secret scanning, and push protection (when available)
- A ruleset on the default branch: PR + code-owner review, required CI check, linear history
- Local community files (CODEOWNERS, Dependabot, SECURITY, issue/PR templates) if missing

On private repositories or free accounts, security features may fail with a detailed error.
Re-run with `--skip-security-features` to apply branch protection without secret scanning.

```bash
./scripts/github-protection/apply.sh --check build
./scripts/github-protection/apply.sh --skip-security-features
./scripts/github-protection/apply.sh --skip-files
```

