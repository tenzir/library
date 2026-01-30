#!/usr/bin/env bash
set -eo pipefail

packages=("$@")

uvx tenzir-test "${packages[@]}"
