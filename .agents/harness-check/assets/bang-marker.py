#!/usr/bin/env python3
"""Disposable marker for the `!`-typed shell probe.

Typing `!python3 assets/bang-marker.py` at the Claude Code prompt is a human
action the agent cannot perform for itself. Running it exercises the
transcript's `system`/`local_command` path (a shell command typed with `!`)
and launches a real `python3` process, then prints one distinctive marker a
collector query can correlate against the run.

It reads nothing, writes nothing, and takes no arguments.
"""
import os

print(f"harness-check-bang-marker pid={os.getpid()}")
