# Contributing

Thank you for your interest in contributing to **{{ cookiecutter.project_name_display }}**.

## How to contribute

This project uses a **fork and pull request** workflow. Outside contributors do not receive write access to the repository; all changes go through a reviewed pull request.

1. **Fork** the repository on GitHub.
2. **Create a branch** on your fork (do not open pull requests from your fork's `main` branch).
3. **Make your changes** and add or update tests where appropriate.
4. **Run checks locally** before opening a PR:
   ```bash
   ./scripts/linux/setup-git-hooks.sh
   ./scripts/linux/ci-check.sh
   ```
   On Windows: `scripts\windows\setup-git-hooks.cmd` then `scripts\windows\ci-check.cmd`

   `setup-git-hooks` configures pre-commit and your local `.gitconfig` commit identity (see
   [`scripts/README.md`](./scripts/README.md)).
5. **Open a pull request** against `main` on the upstream repository.
6. Wait for **CI to pass** and for a **maintainer review**. A maintainer will merge approved changes.

## Pull request guidelines

- Keep pull requests focused on a single change or feature.
- Use a clear title and description. The PR template prompts for the important details.
- Link related issues when applicable (`Fixes #123`).
- Update documentation in `docs/` when you change public APIs.
- Respond to review feedback and resolve conversation threads.

## Branch protection

The `main` branch is protected:

- All changes must go through a pull request.
- At least one approving review from a code owner is required.
- The `build` CI check must pass on the latest commit.
- Only the repository owner (@{{ cookiecutter.github_username }}) can merge pull requests.
- Merge commits are not allowed on `main`; approved PRs are squash-merged.

After creating the repository on GitHub and adding `origin`, apply branch protection:

```bash
./scripts/linux/setup-branch-protection.sh
```

Replace `@{{ cookiecutter.github_username }}` in [`.github/CODEOWNERS`](./.github/CODEOWNERS) if you did not set `github_username` when generating the project.

## Reporting security issues

Do **not** open a public issue for security vulnerabilities. See [SECURITY.md](./SECURITY.md) for responsible disclosure instructions.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
