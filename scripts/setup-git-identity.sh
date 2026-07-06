#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [ ! -f "${ROOT}/.gitconfig" ]; then
	cp "${ROOT}/.gitconfig.example" "${ROOT}/.gitconfig"
	echo "Created .gitconfig from .gitconfig.example — edit name and email before committing."
fi
git config --local include.path ../.gitconfig

echo "Local commit identity: $(git config user.email) <$(git config user.name)>."
