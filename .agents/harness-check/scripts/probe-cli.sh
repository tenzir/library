#!/usr/bin/env bash
# Probe: external CLIs. Resolves each tool, records its version, and runs one
# real read-only invocation so we test execution, not just $PATH.
#
#   probe-cli.sh            local CLIs only
#   probe-cli.sh --net      also probe outbound network (curl, uvx download)
set -uo pipefail
. "$(dirname "$0")/_lib.sh"
sandbox

WITH_NET=0
[ "${1-}" = "--net" ] && WITH_NET=1

# have <name> — PASS with version, or SKIP if absent. Returns 1 when absent.
have() {
  local bin="$1" ver
  if ! command -v "$bin" >/dev/null 2>&1; then
    skip "cli.$bin" "not installed"
    return 1
  fi
  ver=$("$bin" --version 2>&1 | head -n1)
  pass "cli.$bin" "$ver"
  return 0
}

# run <label> <expected-substring> <command...>
run() {
  local label="$1" want="$2"; shift 2
  local out rc
  out=$("$@" 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    fail "$label" "exit $rc: $(printf '%s' "$out" | head -n1)"
  elif printf '%s' "$out" | grep -qF -- "$want"; then
    pass "$label" ""
  else
    fail "$label" "missing '$want' in: $(printf '%s' "$out" | head -n1)"
  fi
}

# --- version control -------------------------------------------------------
if have git; then
  if git -C "$INVOCATION_DIR" rev-parse --git-dir >/dev/null 2>&1; then
    pass cli.git.repo "on branch $(git -C "$INVOCATION_DIR" rev-parse --abbrev-ref HEAD)"
  else
    skip cli.git.repo "not invoked from inside a repository"
  fi
fi

if have gh; then
  if gh auth status >/dev/null 2>&1; then
    pass cli.gh.auth "authenticated"
  else
    skip cli.gh.auth "gh is not authenticated; auth boundary observed"
  fi
fi

# Read-only agent-vendor authentication posture. These commands must never
# print tokens and must not log in, log out, refresh, or modify credentials.
if command -v codex >/dev/null 2>&1; then
  if codex login status >/dev/null 2>&1; then
    pass cli.codex.auth-status "read-only vendor authentication status"
  else
    skip cli.codex.auth-status "Codex is not authenticated"
  fi
else
  skip cli.codex.auth-status "codex CLI not installed"
fi
if command -v claude >/dev/null 2>&1; then
  if claude auth status >/dev/null 2>&1; then
    pass cli.claude.auth-status "read-only vendor authentication status"
  else
    skip cli.claude.auth-status "Claude is not authenticated"
  fi
else
  skip cli.claude.auth-status "claude CLI not installed"
fi

# --- text and data ---------------------------------------------------------
have jq  && run cli.jq.exec   "42"    jq -n '40 + 2'
have rg  && { printf 'needle\n' > rg-input.txt; run cli.rg.exec "needle" rg needle rg-input.txt; rm -f rg-input.txt; }
have python3 && run cli.python3.exec "7" python3 -c 'print(3 + 4)'
have node    && run cli.node.exec    "7" node -e 'console.log(3+4)'

# --- native-tool dependencies ---------------------------------------------
# The Read tool renders PDF pages via pdftoppm. Without it, read.pdf reports
# UNAVAILABLE rather than a tool fault — check here so the two results agree.
if command -v pdftoppm >/dev/null 2>&1; then
  pass cli.pdftoppm "$(pdftoppm -v 2>&1 | head -n1)"
else
  skip cli.pdftoppm "not installed — Read on PDFs will be UNAVAILABLE (install poppler-utils)"
fi

# --- network-dependent -----------------------------------------------------
if [ "$WITH_NET" -eq 1 ]; then
  if command -v curl >/dev/null 2>&1; then
    code=$(curl -sS -m 15 -o /dev/null -w '%{http_code}' https://example.com 2>&1)
    check cli.curl.net "200" "$code" "(bash sandbox network)"
  else
    skip cli.curl.net "curl not installed"
  fi
  if command -v uvx >/dev/null 2>&1; then
    # Downloads the package on first run, then executes a real TQL pipeline.
    out=$(uvx tenzir 'version()' 2>&1)
    if printf '%s' "$out" | grep -q '"version"\|version:'; then
      pass cli.uvx.tenzir "$(printf '%s' "$out" | grep -m1 version | tr -d ' ,')"
    else
      fail cli.uvx.tenzir "$(printf '%s' "$out" | tail -n1)"
    fi
  else
    skip cli.uvx.tenzir "uvx not installed"
  fi
else
  have uvx || true
  skip cli.curl.net "pass --net to probe outbound network"
  skip cli.uvx.tenzir "pass --net to probe package download"
fi

summary cli
