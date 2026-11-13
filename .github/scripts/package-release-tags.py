"""Check release changes and tag them after CI succeeds on main.

Changelog contents are validated separately by tenzir-ship. This script handles
Git history and the library's <package>/<version> tag namespace only.
"""

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

VERSION = re.compile(
    r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-rc\.[1-9][0-9]*)?"
)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def files_at(commit: str) -> set[str]:
    return set(git("ls-tree", "-r", "--name-only", "-z", commit).split("\0"))


def release_tags(base: str, head: str) -> list[str]:
    """Find new releases, rejecting changes to existing release snapshots."""
    before = files_at(base)
    after = files_at(head)
    changed = git("diff", "--name-only", "--no-renames", "-z", base, head).split("\0")
    tags = set()
    for path in changed:
        parts = PurePosixPath(path).parts
        if len(parts) < 5 or parts[0].startswith("."):
            continue
        if parts[1:3] != ("changelog", "releases"):
            continue
        package, version = parts[0], parts[3]
        root = f"{package}/changelog/releases/{version}"
        manifest = f"{root}/manifest.yaml"
        if manifest in before:
            raise ValueError(f"Released history is immutable: {path}")
        if f"{package}/package.yaml" not in after:
            raise ValueError(f"Release has no package.yaml: {root}")
        if manifest not in after or f"{root}/notes.md" not in after:
            raise ValueError(f"Release needs manifest.yaml and notes.md: {root}")
        if not VERSION.fullmatch(version):
            raise ValueError(f"Invalid release version: {version}")
        tag = f"{package}/{version}"
        git("check-ref-format", f"refs/tags/{tag}")
        tags.add(tag)
    return sorted(tags)


def remote_tags(remote: str) -> dict[str, str]:
    """Resolve both lightweight and annotated remote tags to commits."""
    refs = {}
    for line in git("ls-remote", "--tags", remote).splitlines():
        sha, ref = line.split("\t")
        refs[ref.removeprefix("refs/tags/")] = sha
    return {
        tag: refs.get(f"{tag}^{{}}", sha)
        for tag, sha in refs.items()
        if not tag.endswith("^{}")
    }


def check_tags(tags: list[str], head: str, remote: str) -> list[str]:
    """Allow retries at the same commit, but never move an existing tag."""
    existing = remote_tags(remote) if tags else {}
    pending = []
    for tag in tags:
        if tag not in existing:
            pending.append(tag)
        elif existing[tag] != head:
            raise ValueError(f"Tag {tag} already exists at {existing[tag]}, not {head}")
        else:
            print(f"Already tagged: {tag} at {head}")
    return pending


def publish_tags(tags: list[str], head: str, remote: str) -> None:
    for tag in tags:
        # A previous attempt may have created the local tag before a push failed.
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            if result.stdout.strip() != head:
                raise ValueError(f"Local tag {tag} points to another commit")
        else:
            git("tag", "-a", tag, head, "-m", f"Release {tag}")
    if tags:
        # Publish all releases in this push together, without force-updating refs.
        git(
            "push",
            "--atomic",
            remote,
            *(f"refs/tags/{tag}:refs/tags/{tag}" for tag in tags),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="PR base or pre-push commit")
    parser.add_argument("--head", default="HEAD", help="Commit whose CI checks ran")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--publish", action="store_true", help="Create and push tags")
    args = parser.parse_args()
    base = git("rev-parse", "--verify", f"{args.base}^{{commit}}")
    head = git("rev-parse", "--verify", f"{args.head}^{{commit}}")
    tags = release_tags(base, head)
    pending = check_tags(tags, head, args.remote)
    for tag in pending:
        print(f"Release tag: {tag} at {head}")
    if not tags:
        print("No new package releases.")
    if args.publish:
        publish_tags(pending, head, args.remote)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
