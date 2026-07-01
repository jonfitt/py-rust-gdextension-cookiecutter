# Security Policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch. Older tags may not receive backports unless noted in a security advisory.

| Version | Supported |
| ------- | --------- |
| latest on `main` | yes |
| older tags | best effort |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you believe you have found a security issue, report it privately:

1. Open a [GitHub private vulnerability report](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.repo_name }}/security/advisories/new) on this repository, **or**
2. Contact the maintainer through GitHub (@{{ cookiecutter.github_username }}) with details if private advisories are unavailable.

Include as much detail as possible:

- Description of the vulnerability and potential impact
- Steps to reproduce
- Affected code paths, crates, or Godot extension surfaces
- Any suggested fix or mitigation

## What to expect

- **Acknowledgment** within a reasonable timeframe (typically a few business days)
- **Status updates** as the issue is triaged and addressed
- **Credit** in the advisory for reporters who wish to be named, unless you prefer to remain anonymous

We appreciate responsible disclosure and will work with reporters to understand and resolve valid reports promptly.
