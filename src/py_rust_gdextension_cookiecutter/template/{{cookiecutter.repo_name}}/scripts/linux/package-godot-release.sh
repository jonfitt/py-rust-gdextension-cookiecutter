#!/usr/bin/env bash
# Assemble consumable Godot addon and demo release zips from per-platform GDExtension binaries.
#
# Usage:
#   ./scripts/linux/package-godot-release.sh VERSION LINUX_SO WIN_DLL MAC_ARM64_DYLIB
#
# VERSION may include a leading "v" (e.g. v0.1.0); it is stripped from zip file names.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:?Usage: package-godot-release.sh VERSION LINUX_SO WIN_DLL MAC_ARM64_DYLIB}"
VERSION="${VERSION#v}"
LINUX_SO="${2:?missing Linux .so path}"
WIN_DLL="${3:?missing Windows .dll path}"
MAC_DYLIB="${4:?missing macOS arm64 .dylib path}"

for f in "$LINUX_SO" "$WIN_DLL" "$MAC_DYLIB"; do
  if [[ ! -f "$f" ]]; then
    echo "error: binary not found: $f" >&2
    exit 1
  fi
done

DIST="$ROOT/dist"
ADDON_NAME="{{ cookiecutter.project_slug }}"
ADDON_DIR="$DIST/$ADDON_NAME"
DEMO_NAME="{{ cookiecutter.project_slug }}-demo-${VERSION}"
DEMO_DIR="$DIST/$DEMO_NAME"

rm -rf "$DIST"
mkdir -p "$ADDON_DIR/bin/linux/x86_64"
mkdir -p "$ADDON_DIR/bin/windows/x86_64"
mkdir -p "$ADDON_DIR/bin/macos/arm64"

cp "$ROOT/packaging/godot-addon/{{ cookiecutter.project_slug }}.gdextension" "$ADDON_DIR/"
cp "$ROOT/packaging/godot-addon/README.md" "$ADDON_DIR/"
cp "$LINUX_SO" "$ADDON_DIR/bin/linux/x86_64/lib{{ cookiecutter.gd_library_base }}.so"
cp "$WIN_DLL" "$ADDON_DIR/bin/windows/x86_64/{{ cookiecutter.gd_library_base }}.dll"
cp "$MAC_DYLIB" "$ADDON_DIR/bin/macos/arm64/lib{{ cookiecutter.gd_library_base }}.dylib"

ADDON_ZIP="{{ cookiecutter.project_slug }}-${VERSION}.zip"
DEMO_ZIP="${DEMO_NAME}.zip"

(cd "$DIST" && zip -rq "$ADDON_ZIP" "$ADDON_NAME")

mkdir -p "$DEMO_DIR/addons"
cp -r "$ADDON_DIR" "$DEMO_DIR/addons/{{ cookiecutter.project_slug }}"
cp "$ROOT/godot/project.godot" "$DEMO_DIR/"
cp -r "$ROOT/godot/demo" "$DEMO_DIR/demo"

(cd "$DIST" && zip -rq "$DEMO_ZIP" "$DEMO_NAME")

(
  cd "$DIST"
  sha256sum "$ADDON_ZIP" "$DEMO_ZIP" > "checksums-${VERSION}.txt"
)

echo "Created $DIST/$ADDON_ZIP"
echo "Created $DIST/$DEMO_ZIP"
echo "Created $DIST/checksums-${VERSION}.txt"
