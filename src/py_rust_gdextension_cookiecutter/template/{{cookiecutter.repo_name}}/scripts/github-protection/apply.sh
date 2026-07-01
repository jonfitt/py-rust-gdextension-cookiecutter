#!/usr/bin/env bash
# Apply GitHub repository protection settings via the gh CLI.
#
# Usage:
#   apply.sh [--repo-path PATH] [--check CONTEXT] [--skip-files] [--skip-security-features] [--dry-run]
#
# Resolves owner/repo from the origin remote URL. The repository owner (user or
# organization) becomes the code owner and the only bypass actor who can merge.

set -euo pipefail

RULESET_NAME="Protect main"
REPO_PATH="."
CI_CHECK=""
SKIP_FILES=0
SKIP_SECURITY=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: apply.sh [options]

Apply branch protection rules, merge settings, security features, and (by default)
community health files to a GitHub repository.

The repository owner is read from `git remote get-url origin` (for example
https://github.com/OWNER/REPO.git). That owner is used for CODEOWNERS, review
requests, and merge bypass permissions.

Options:
  --repo-path PATH           Local clone path (default: current directory)
  --check CONTEXT            Required CI status check name (default: auto-detect)
  --ruleset-name NAME        Ruleset name (default: "Protect main")
  --skip-files               Do not create local CODEOWNERS, templates, etc.
  --skip-security-features   Skip secret scanning / Dependabot security updates
  --dry-run                  Print actions without calling the GitHub API
  -h, --help                 Show this help

Examples:
  ./scripts/linux/setup-branch-protection.sh
  ./scripts/github-protection/apply.sh --check build
  ./scripts/github-protection/apply.sh --skip-security-features
EOF
}

log() { printf '==> %s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-path) REPO_PATH="${2:?}"; shift 2 ;;
    --check) CI_CHECK="${2:?}"; shift 2 ;;
    --ruleset-name) RULESET_NAME="${2:?}"; shift 2 ;;
    --skip-files) SKIP_FILES=1; shift ;;
    --skip-security-features) SKIP_SECURITY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
done

REPO_PATH="$(cd "$REPO_PATH" && pwd)"

command -v gh >/dev/null 2>&1 || die "gh CLI is not installed. Install GitHub CLI: https://cli.github.com/"

if ! gh auth status >/dev/null 2>&1; then
  die "gh is not authenticated. Run: gh auth login"
fi

resolve_repo_slug() {
  local remote url
  if ! remote="$(git -C "$REPO_PATH" remote get-url origin 2>/dev/null)"; then
    die "No git remote 'origin' found in: $REPO_PATH"
  fi

  url="${remote%.git}"
  if [[ "$url" =~ github\.com[:/]([^/]+)/([^/]+)$ ]]; then
    printf '%s/%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    return
  fi

  die "Could not parse owner/repo from origin URL: $remote"
}

explain_gh_error() {
  local context="$1"
  local response="$2"

  if [[ "$response" == *"Not Found"* ]] || [[ "$response" == *"HTTP 404"* ]]; then
    cat >&2 <<EOF

$context

GitHub returned 404. Common causes:
  - The repository does not exist or you lack admin access.
  - The gh CLI is authenticated as a different user than the repository owner.

EOF
    return
  fi

  if [[ "$response" == *"advanced security"* ]] || [[ "$response" == *"Advanced Security"* ]] \
      || [[ "$response" == *"GH013"* ]]; then
    cat >&2 <<EOF

$context

Secret scanning features are not available on this repository.

  Public repositories:  secret scanning is included for free.
  Private repositories: requires GitHub Advanced Security (paid GitHub Team /
                        Enterprise plan, or an active trial).

If this is a private repo on a free account, either:
  1. Make the repository public, or
  2. Upgrade the account / enable Advanced Security for the organization, or
  3. Re-run with --skip-security-features to apply branch protection only.

Raw API response:
$response

EOF
    return
  fi

  if [[ "$response" == *"Upgrade to GitHub Pro"* ]] || [[ "$response" == *"private repositories"* ]]; then
    cat >&2 <<EOF

$context

This feature is not available on your current GitHub plan for this repository type.

Private repositories on free personal accounts cannot enable some security
features without upgrading to GitHub Pro or making the repository public.

Re-run with --skip-security-features to apply branch protection and merge settings.

Raw API response:
$response

EOF
    return
  fi

  cat >&2 <<EOF

$context

Unexpected GitHub API error:
$response

EOF
}

gh_api() {
  local method="$1"
  local endpoint="$2"
  local context="$3"
  local input_file="${4:-}"

  local response
  if [[ -n "$input_file" ]]; then
    if ! response="$(gh api --method "$method" "$endpoint" --input "$input_file" 2>&1)"; then
      explain_gh_error "$context" "$response"
      return 1
    fi
  else
    if ! response="$(gh api --method "$method" "$endpoint" 2>&1)"; then
      explain_gh_error "$context" "$response"
      return 1
    fi
  fi

  printf '%s' "$response"
}

extract_first_job_name() {
  awk '
    /^jobs:/ { in_jobs = 1; next }
    in_jobs && /^  [A-Za-z0-9_.-]+:/ {
      line = $0
      sub(/^  /, "", line)
      sub(/:.*$/, "", line)
      gsub(/\r/, "", line)
      print line
      exit
    }
  ' "$1"
}

detect_ci_check() {
  local workflows_dir="$REPO_PATH/.github/workflows"
  local candidate file job

  if [[ -n "$CI_CHECK" ]]; then
    printf '%s' "$CI_CHECK"
    return
  fi

  for candidate in rust.yml ci.yml test.yml build.yml; do
    file="$workflows_dir/$candidate"
    if [[ -f "$file" ]]; then
      job="$(extract_first_job_name "$file")"
      if [[ -n "$job" ]]; then
        printf '%s' "$job"
        return
      fi
    fi
  done

  for file in "$workflows_dir"/*.yml "$workflows_dir"/*.yaml; do
    [[ -f "$file" ]] || continue
    job="$(extract_first_job_name "$file")"
    if [[ -n "$job" ]]; then
      printf '%s' "$job"
      return
    fi
  done

  printf 'build'
}

detect_display_name() {
  local name=""

  if [[ -f "$REPO_PATH/Cargo.toml" ]]; then
    name="$(sed -n 's/^name = "\(.*\)"/\1/p' "$REPO_PATH/Cargo.toml" | head -1 | tr -d '\r')"
  fi

  if [[ -z "$name" ]]; then
    name="$(basename "$REPO_PATH")"
  fi

  printf '%s' "$name"
}

detect_license_note() {
  if [[ -f "$REPO_PATH/LICENSE.md" ]]; then
    printf 'the same license as the project ([LICENSE.md](./LICENSE.md)).'
  elif [[ -f "$REPO_PATH/LICENSE" ]]; then
    printf 'the same license as the project ([LICENSE](./LICENSE)).'
  else
    printf 'the same license as the project.'
  fi
}

write_if_missing() {
  local path="$1"
  local content="$2"

  if [[ -f "$path" ]]; then
    warn "Skipping existing file: $path"
    return
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "[dry-run] Would create: $path"
    return
  fi

  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$content" >"$path"
  log "Created: $path"
}

render_local_files() {
  local owner="$1"
  local slug="$2"
  local check="$3"
  local display_name="$4"
  local license_note="$5"

  write_if_missing "$REPO_PATH/.github/CODEOWNERS" "# Default reviewers for all changes. @${owner} is requested automatically on every pull request.
* @${owner}"

  write_if_missing "$REPO_PATH/.github/dependabot.yml" "version: 2
updates:
  - package-ecosystem: cargo
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5"

  write_if_missing "$REPO_PATH/SECURITY.md" "# Security Policy

## Supported versions

Security fixes are applied to the latest release on the \`main\` branch. Older tags may not receive backports unless noted in a security advisory.

| Version | Supported |
| ------- | --------- |
| latest on \`main\` | yes |
| older tags | best effort |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you believe you have found a security issue, report it privately:

1. Open a [GitHub private vulnerability report](https://github.com/${slug}/security/advisories/new) on this repository, **or**
2. Contact the maintainer through GitHub (@${owner}) with details if private advisories are unavailable.

Include as much detail as possible:

- Description of the vulnerability and potential impact
- Steps to reproduce
- Affected components and entry points
- Any suggested fix or mitigation

## What to expect

- **Acknowledgment** within a reasonable timeframe (typically a few business days)
- **Status updates** as the issue is triaged and addressed
- **Credit** in the advisory for reporters who wish to be named, unless you prefer to remain anonymous

We appreciate responsible disclosure and will work with reporters to understand and resolve valid reports promptly."

  write_if_missing "$REPO_PATH/.github/pull_request_template.md" "## Summary

<!-- What does this PR change and why? -->

## Related issues

<!-- Link issues: Fixes #123, Relates to #456 -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor / cleanup
- [ ] Documentation
- [ ] CI / tooling
- [ ] Other (describe below)

## Testing

<!-- How did you verify this? List commands run and relevant scenarios. -->

- [ ] \`./scripts/linux/ci-check.sh\` (or \`scripts\\windows\\ci-check.cmd\`)
- [ ] Godot extension / demo tested (if applicable)

## Checklist

- [ ] PR targets \`main\` and is opened from a feature branch (not from a fork's \`main\`)
- [ ] Changes are scoped to this PR (no unrelated edits)
- [ ] Documentation updated if behavior or public API changed"

  write_if_missing "$REPO_PATH/.github/ISSUE_TEMPLATE/bug_report.md" "---
name: Bug report
about: Report incorrect behavior or a crash
title: \"[Bug] \"
labels: bug
assignees: ''
---

## Description

<!-- A clear description of the bug. -->

## Steps to reproduce

1.
2.
3.

## Expected behavior

<!-- What should happen? -->

## Actual behavior

<!-- What happens instead? -->

## Environment

- **Version / commit:**
- **Rust toolchain (\`rustc --version\`):**
- **OS:**
- **Godot version** (if using the GDExtension):

## Additional context

<!-- Logs, screenshots, minimal repro, or links to a branch. -->"

  write_if_missing "$REPO_PATH/.github/ISSUE_TEMPLATE/feature_request.md" "---
name: Feature request
about: Suggest an idea or improvement
title: \"[Feature] \"
labels: enhancement
assignees: ''
---

## Problem

<!-- What problem does this solve? Who is affected? -->

## Proposed solution

<!-- Describe the feature or API you would like. -->

## Alternatives considered

<!-- Other approaches you thought about. -->

## Additional context

<!-- Use cases, sketches, links, or prior art. -->"

  write_if_missing "$REPO_PATH/.github/ISSUE_TEMPLATE/config.yml" "blank_issues_enabled: false
contact_links:
  - name: Security vulnerability
    url: https://github.com/${slug}/security/advisories/new
    about: Report security issues privately — do not open a public issue."

  if [[ -f "$REPO_PATH/CONTRIBUTING.md" ]]; then
    warn "Skipping existing file: $REPO_PATH/CONTRIBUTING.md"
    return
  fi

  write_if_missing "$REPO_PATH/CONTRIBUTING.md" "# Contributing

Thank you for your interest in contributing to **${display_name}**.

## How to contribute

This project uses a **fork and pull request** workflow. Outside contributors do not receive write access to the repository; all changes go through a reviewed pull request.

1. **Fork** the repository on GitHub.
2. **Create a branch** on your fork (do not open pull requests from your fork's \`main\` branch).
3. **Make your changes** and add or update tests where appropriate.
4. **Run checks locally** before opening a PR:
   \`\`\`bash
   ./scripts/linux/ci-check.sh
   \`\`\`
   On Windows: \`scripts\\windows\\ci-check.cmd\`
5. **Open a pull request** against \`main\` on the upstream repository.
6. Wait for **CI to pass** and for a **maintainer review**. A maintainer will merge approved changes.

## Pull request guidelines

- Keep pull requests focused on a single change or feature.
- Use a clear title and description. The PR template prompts for the important details.
- Link related issues when applicable (\`Fixes #123\`).
- Respond to review feedback and resolve conversation threads.

## Branch protection

The \`main\` branch is protected:

- All changes must go through a pull request.
- At least one approving review from a code owner is required.
- The \`${check}\` CI check must pass on the latest commit.
- Only the repository owner (@${owner}) can merge pull requests.
- Merge commits are not allowed on \`main\`; approved PRs are squash-merged.

## Reporting security issues

Do **not** open a public issue for security vulnerabilities. See [SECURITY.md](./SECURITY.md) for responsible disclosure instructions.

## License

By contributing, you agree that your contributions will be licensed under ${license_note}"
}

apply_repo_settings() {
  local slug="$1"
  local tmp
  tmp="$(mktemp)"

  cat >"$tmp" <<'EOF'
{
  "delete_branch_on_merge": true,
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false
}
EOF

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "[dry-run] Would PATCH repos/${slug} (merge settings)"
  else
    gh_api PATCH "repos/${slug}" "Updating merge settings for ${slug}" "$tmp" >/dev/null \
      || { rm -f "$tmp"; return 1; }
    log "Merge settings updated (squash only, delete branch on merge)."
  fi

  rm -f "$tmp"

  if [[ "$SKIP_SECURITY" -eq 1 ]]; then
    warn "Skipping security feature enablement (--skip-security-features)."
    return 0
  fi

  cat >"$tmp" <<'EOF'
{
  "security_and_analysis": {
    "dependabot_security_updates": { "status": "enabled" },
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" }
  }
}
EOF

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "[dry-run] Would PATCH repos/${slug} (security features)"
    rm -f "$tmp"
    return 0
  fi

  if ! gh_api PATCH "repos/${slug}" "Enabling security features for ${slug}" "$tmp" >/dev/null; then
    rm -f "$tmp"
    warn "Security features could not be enabled. Branch protection was still applied."
    warn "Use --skip-security-features on private/free-plan repos to suppress this step."
    return 0
  fi

  rm -f "$tmp"
  log "Security features enabled (Dependabot updates, secret scanning, push protection)."
}

apply_ruleset() {
  local slug="$1"
  local owner_id="$2"
  local owner_type="$3"
  local check="$4"
  local tmp ruleset_id
  tmp="$(mktemp)"

  cat >"$tmp" <<EOF
{
  "name": "${RULESET_NAME}",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "${check}" }
        ]
      }
    },
    { "type": "required_linear_history" },
    { "type": "non_fast_forward" },
    { "type": "deletion" },
    { "type": "update" }
  ],
  "bypass_actors": [
    {
      "actor_id": ${owner_id},
      "actor_type": "${owner_type}",
      "bypass_mode": "always"
    }
  ]
}
EOF

  ruleset_id="$(gh api "repos/${slug}/rulesets" --jq ".[] | select(.name == \"${RULESET_NAME}\") | .id" 2>/dev/null | tr -d '\r' | head -1 || true)"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ -n "$ruleset_id" ]]; then
      log "[dry-run] Would PUT repos/${slug}/rulesets/${ruleset_id}"
    else
      log "[dry-run] Would POST repos/${slug}/rulesets"
    fi
    rm -f "$tmp"
    return 0
  fi

  if [[ -n "$ruleset_id" ]]; then
    gh_api PUT "repos/${slug}/rulesets/${ruleset_id}" "Updating ruleset '${RULESET_NAME}' on ${slug}" "$tmp" >/dev/null \
      || { rm -f "$tmp"; return 1; }
    log "Updated ruleset '${RULESET_NAME}' (id: ${ruleset_id})."
  else
    gh_api POST "repos/${slug}/rulesets" "Creating ruleset '${RULESET_NAME}' on ${slug}" "$tmp" >/dev/null \
      || { rm -f "$tmp"; return 1; }
    log "Created ruleset '${RULESET_NAME}'."
  fi

  rm -f "$tmp"
}

main() {
  local slug owner owner_id owner_type is_private default_branch check display_name license_note

  slug="$(resolve_repo_slug)"
  owner="${slug%%/*}"

  log "Repository: ${slug}"
  log "Local path: ${REPO_PATH}"

  if ! gh repo view "$slug" --json isPrivate,defaultBranchRef >/dev/null 2>&1; then
    die "Cannot access ${slug}. Ensure the repository exists on GitHub and gh has admin access."
  fi

  is_private="$(gh repo view "$slug" --json isPrivate -q .isPrivate)"
  default_branch="$(gh repo view "$slug" --json defaultBranchRef -q .defaultBranchRef.name)"
  owner_id="$(gh api "repos/${slug}" --jq .owner.id | tr -d '\r')"
  owner_type="$(gh api "repos/${slug}" --jq .owner.type | tr -d '\r')"

  if [[ "$is_private" == "true" ]]; then
    warn "Repository is private. Secret scanning may require GitHub Advanced Security."
    warn "If API calls fail, re-run with --skip-security-features."
  else
    log "Repository visibility: public"
  fi

  if [[ "$default_branch" != "main" ]]; then
    warn "Default branch is '${default_branch}', not 'main'. Ruleset still targets ~DEFAULT_BRANCH."
  fi

  check="$(detect_ci_check)"
  display_name="$(detect_display_name)"
  license_note="$(detect_license_note)"

  log "Repository owner: @${owner} (${owner_type}, id ${owner_id})"
  log "Detected CI status check: ${check}"

  if [[ "$SKIP_FILES" -eq 0 ]]; then
    log "Scaffolding community health files (existing files are preserved)..."
    render_local_files "$owner" "$slug" "$check" "$display_name" "$license_note"
  else
    log "Skipping local file scaffolding (--skip-files)."
  fi

  apply_repo_settings "$slug"
  apply_ruleset "$slug" "$owner_id" "$owner_type" "$check"

  cat <<EOF

Done. Applied GitHub protection to ${slug}.

Remote settings:
  - Squash merge only, auto-delete head branches
  - Ruleset "${RULESET_NAME}" on default branch
  - Required review from code owner (@${owner})
  - Required status check: ${check}
  - Only @${owner} can merge (ruleset bypass actor)

Next steps:
  1. Commit and push any new local files so CODEOWNERS and templates take effect.
  2. Open https://github.com/${slug}/rules to verify the ruleset.
  3. Ensure CI has run at least once so the "${check}" check appears on pull requests.

EOF
}

main "$@"
