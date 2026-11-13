"""Check release changes and tag them after CI succeeds on main.

Changelog contents are validated separately by tenzir-ship. This script handles
Git history and the library's <package>/<version> tag namespace only.
"""

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

# Only stable releases are supported: tenzir-ship deletes superseded release
# candidate snapshots, which would conflict with immutable release history.
VERSION = re.compile(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
CANDIDATE = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+-rc\.[0-9]+")
# The top-level version of a package manifest. Tenzir rejects unquoted versions
# because YAML reads a value like `1.2` as a number.
MANIFEST_VERSION = re.compile(r"^version:[ \t]*(.*?)[ \t]*$", re.MULTILINE)
QUOTED = re.compile(r"""("|')([^"']*)\1""")


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
            # Removing a whole package also removes its release history; its
            # existing tags stay untouched.
            if f"{package}/package.yaml" not in after and path not in after:
                continue
            raise ValueError(f"Released history is immutable: {path}")
        if f"{package}/package.yaml" not in after:
            raise ValueError(f"Release has no package.yaml: {root}")
        if manifest not in after or f"{root}/notes.md" not in after:
            raise ValueError(f"Release needs manifest.yaml and notes.md: {root}")
        if CANDIDATE.fullmatch(version):
            raise ValueError(f"Release candidates are not supported: {root}")
        if not VERSION.fullmatch(version):
            raise ValueError(f"Invalid release version: {version}")
        tag = f"{package}/{version}"
        git("check-ref-format", f"refs/tags/{tag}")
        tags.add(tag)
    return sorted(tags)


def manifest_version(commit: str, package: str) -> str | None:
    """Read the version from a package's manifest at a commit, if it has one."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{package}/package.yaml"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    match = MANIFEST_VERSION.search(result.stdout)
    if match is None:
        return None
    quoted = QUOTED.fullmatch(match.group(1))
    if quoted is None:
        raise ValueError(f"Version in {package}/package.yaml must be quoted")
    return quoted.group(2)


def check_versions(tags: list[str], base: str, head: str) -> None:
    """Require each package manifest to state the version of its new release.

    tenzir-ship does not update `package.yaml`, so a release must bump the
    version there as well, and a version may only change with a release.
    """
    latest: dict[str, str] = {}
    for tag in tags:
        package, version = tag.split("/")
        if package not in latest or version_key(version) > version_key(
            latest[package]
        ):
            latest[package] = version
    for package, version in latest.items():
        actual = manifest_version(head, package)
        expected = version.removeprefix("v")
        if actual != expected:
            raise ValueError(
                f"Release {package}/{version} needs version: \"{expected}\" "
                f"in {package}/package.yaml, found {actual!r}"
            )
    changed = git("diff", "--name-only", "--no-renames", "-z", base, head).split("\0")
    for path in changed:
        parts = PurePosixPath(path).parts
        if len(parts) != 2 or parts[1] != "package.yaml" or parts[0] in latest:
            continue
        before = manifest_version(base, parts[0])
        after = manifest_version(head, parts[0])
        if after is not None and after != before:
            raise ValueError(
                f"{path} changes its version to {after!r} without a release"
            )


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


def snapshot(commit: str, tag: str) -> str | None:
    """Return the tree of a tag's release snapshot at a commit, if present."""
    package, version = tag.split("/")
    result = subprocess.run(
        [
            "git",
            "rev-parse",
            "--verify",
            "-q",
            f"{commit}:{package}/changelog/releases/{version}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.removeprefix("v").split("."))


def released_at(commit: str) -> dict[str, set[str]]:
    """Collect each package's release snapshots at a commit."""
    versions: dict[str, set[str]] = {}
    for path in files_at(commit):
        parts = PurePosixPath(path).parts
        if (
            len(parts) == 5
            and parts[1:3] == ("changelog", "releases")
            and parts[4] == "manifest.yaml"
        ):
            versions.setdefault(parts[0], set()).add(parts[3])
    return versions


def supersedes(commit: str, tag: str, head: str) -> bool:
    """Check whether a later commit already contains this release unchanged."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", head, commit], check=False
    )
    return result.returncode == 0 and snapshot(commit, tag) == snapshot(head, tag)


def check_order(tag, tags, head, released, existing) -> None:
    """Reject releases that are not newer than the package's prior versions."""
    package, version = tag.split("/")
    # tenzir-ship accepts explicit versions below existing releases, and some
    # packages have tags without release snapshots.
    for other in released.get(package, ()):
        if VERSION.fullmatch(other) and version_key(other) >= version_key(version):
            raise ValueError(f"Release {tag} is not newer than {package}/{other}")
    for other, commit in existing.items():
        other_package, _, other_version = other.partition("/")
        if (
            other in tags
            or other_package != package
            or not VERSION.fullmatch(other_version)
            or version_key(other_version) < version_key(version)
        ):
            continue
        # A later push may finish CI first and tag its newer release before us.
        if not supersedes(commit, tag, head):
            raise ValueError(f"Release {tag} is not newer than {other}")


def check_tags(tags: list[str], base: str, head: str, remote: str) -> list[str]:
    """Allow retries and earlier runs' tags, but never move an existing tag."""
    existing = remote_tags(remote) if tags else {}
    released = released_at(base) if tags else {}
    pending = []
    for tag in tags:
        if tag not in existing:
            check_order(tag, tags, head, released, existing)
            pending.append(tag)
        elif existing[tag] != head and snapshot(existing[tag], tag) != snapshot(
            head, tag
        ):
            # A different commit is fine only if it holds the same release, e.g.,
            # when a backfill range includes releases a later run already tagged.
            raise ValueError(f"Tag {tag} already exists at {existing[tag]}, not {head}")
        else:
            print(f"Already tagged: {tag} at {existing[tag]}")
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
    check_versions(tags, base, head)
    pending = check_tags(tags, base, head, args.remote)
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
