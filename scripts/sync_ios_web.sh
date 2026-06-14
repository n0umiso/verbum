#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WEB_DIR="$ROOT_DIR/ios/Verbum/Resources/Web"

mkdir -p "$WEB_DIR"
cp "$ROOT_DIR/index.html" "$WEB_DIR/index.html"
rm -rf "$WEB_DIR/data"
cp -R "$ROOT_DIR/data" "$WEB_DIR/data"
find "$WEB_DIR" -name .DS_Store -delete

echo "Synced web assets to ios/Verbum/Resources/Web"
