#!/usr/bin/env bash
set -eo pipefail

workspace="$(pwd)"
packages=("$@")

docker run --rm \
  -e UV_CACHE_DIR=/tmp/uv-cache \
  -e XDG_DATA_HOME=/tmp/xdg-data \
  -v "${workspace}:/workspace" \
  -w /workspace \
  --entrypoint uv \
  tenzir/tenzir tool run tenzir-test "${packages[@]}"
