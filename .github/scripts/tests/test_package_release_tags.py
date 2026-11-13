"""Exercise release detection and publishing against disposable Git repositories."""

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "package-release-tags.py"
spec = importlib.util.spec_from_file_location("package_release_tags", SCRIPT)
release_tags = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_tags)


class ReleaseTagsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        previous = Path.cwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, previous)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Release test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "tag.gpgsign", "false")
        self.write("README.md", "Test library\n")
        self.base = self.commit()
        self.remote = str(self.root / "remote.git")
        self.git("init", "--bare", self.remote)
        self.git("remote", "add", "origin", self.remote)
        self.git("push", "origin", "main")

    def git(self, *args):
        return subprocess.check_output(
            ["git", *args], text=True, stderr=subprocess.PIPE
        ).strip()

    def write(self, path, content):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "Test change")
        return self.git("rev-parse", "HEAD")

    def release(self, package="tenzir", version="v0.1.0"):
        self.write(f"{package}/package.yaml", f"id: {package}\nname: {package}\n")
        root = f"{package}/changelog/releases/{version}"
        self.write(
            f"{root}/manifest.yaml", "created: 2026-01-01\nintro: Test release\n"
        )
        self.write(f"{root}/notes.md", "# Test release\n")
        return root

    def test_no_releases(self):
        self.write("tenzir/changelog/unreleased/change.md", "Not a release\n")
        head = self.commit()
        self.assertEqual(release_tags.release_tags(self.base, head), [])

    def test_multiple_packages_and_versions(self):
        self.release("tenzir", "v0.1.0")
        self.release("tenzir", "v0.2.0")
        self.release("suricata", "v0.3.0")
        head = self.commit()
        tags = release_tags.release_tags(self.base, head)
        self.assertEqual(tags, ["suricata/v0.3.0", "tenzir/v0.1.0", "tenzir/v0.2.0"])
        pending = release_tags.check_tags(tags, head, "origin")
        release_tags.publish_tags(pending, head, "origin")
        self.assertEqual(release_tags.remote_tags("origin"), dict.fromkeys(tags, head))
        for tag in tags:
            self.assertEqual(self.git("cat-file", "-t", f"refs/tags/{tag}"), "tag")
        # A rerun is a no-op, including for annotated tags.
        self.assertEqual(release_tags.check_tags(tags, head, "origin"), [])
        release_tags.publish_tags([], head, "origin")

    def test_tags_the_tested_commit_not_current_head(self):
        self.release()
        tested = self.commit()
        self.write("README.md", "Later change\n")
        self.commit()
        tags = release_tags.release_tags(self.base, tested)
        release_tags.publish_tags(tags, tested, "origin")
        self.assertEqual(release_tags.remote_tags("origin"), {"tenzir/v0.1.0": tested})

    def test_detects_releases_across_multiple_commits_in_one_push(self):
        self.release("tenzir")
        self.commit()
        self.release("suricata")
        head = self.commit()
        self.assertEqual(
            release_tags.release_tags(self.base, head),
            ["suricata/v0.1.0", "tenzir/v0.1.0"],
        )

    def test_ignores_unchanged_existing_releases(self):
        self.release("tenzir")
        base = self.commit()
        self.release("suricata")
        head = self.commit()
        self.assertEqual(release_tags.release_tags(base, head), ["suricata/v0.1.0"])

    def test_rejects_historical_edits(self):
        root = self.release()
        base = self.commit()
        self.write(f"{root}/notes.md", "Changed history\n")
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "immutable"):
            release_tags.release_tags(base, head)

    def test_rejects_historical_deletions(self):
        root = self.release()
        base = self.commit()
        Path(f"{root}/manifest.yaml").unlink()
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "immutable"):
            release_tags.release_tags(base, head)

    def test_rejects_adding_files_to_existing_release(self):
        root = self.release()
        base = self.commit()
        self.write(f"{root}/entries/extra.md", "Extra entry\n")
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "immutable"):
            release_tags.release_tags(base, head)

    def test_allows_removing_released_package(self):
        self.release("tenzir")
        self.release("suricata")
        base = self.commit()
        self.git("rm", "-r", "-q", "tenzir")
        head = self.commit()
        self.assertEqual(release_tags.release_tags(base, head), [])

    def test_rejects_removing_releases_of_kept_package(self):
        root = self.release()
        base = self.commit()
        self.git("rm", "-r", "-q", root)
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "immutable"):
            release_tags.release_tags(base, head)

    def test_rejects_release_candidates(self):
        self.release(version="v0.1.0-rc.1")
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "Release candidates are not supported"):
            release_tags.release_tags(self.base, head)

    def test_rejects_missing_notes(self):
        root = self.release()
        Path(f"{root}/notes.md").unlink()
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "needs manifest.yaml and notes.md"):
            release_tags.release_tags(self.base, head)

    def test_rejects_missing_manifest(self):
        root = self.release()
        Path(f"{root}/manifest.yaml").unlink()
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "needs manifest.yaml and notes.md"):
            release_tags.release_tags(self.base, head)

    def test_rejects_missing_package(self):
        self.release()
        Path("tenzir/package.yaml").unlink()
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "no package.yaml"):
            release_tags.release_tags(self.base, head)

    def test_rejects_invalid_version(self):
        self.release(version="latest")
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "Invalid release version"):
            release_tags.release_tags(self.base, head)

    def test_rejects_remote_conflict_before_creating_any_tags(self):
        self.git("tag", "tenzir/v0.1.0", self.base)
        self.git("push", "origin", "refs/tags/tenzir/v0.1.0")
        self.release("tenzir")
        self.release("suricata")
        head = self.commit()
        tags = release_tags.release_tags(self.base, head)
        with self.assertRaisesRegex(ValueError, "already exists"):
            release_tags.check_tags(tags, head, "origin")
        self.assertEqual(self.git("tag", "--list"), "tenzir/v0.1.0")
        self.assertEqual(
            release_tags.remote_tags("origin"), {"tenzir/v0.1.0": self.base}
        )

    def test_accepts_existing_lightweight_tag_at_same_commit(self):
        self.release()
        head = self.commit()
        self.git("tag", "tenzir/v0.1.0", head)
        self.git("push", "origin", "refs/tags/tenzir/v0.1.0")
        self.assertEqual(release_tags.check_tags(["tenzir/v0.1.0"], head, "origin"), [])

    def test_recovers_from_local_tag_after_failed_push(self):
        self.release()
        head = self.commit()
        self.git("tag", "-a", "tenzir/v0.1.0", head, "-m", "Previous attempt")
        release_tags.publish_tags(["tenzir/v0.1.0"], head, "origin")
        self.assertEqual(release_tags.remote_tags("origin"), {"tenzir/v0.1.0": head})

    def test_rejects_local_tag_conflict(self):
        self.git("tag", "tenzir/v0.1.0", self.base)
        self.release()
        head = self.commit()
        with self.assertRaisesRegex(ValueError, "Local tag"):
            release_tags.publish_tags(["tenzir/v0.1.0"], head, "origin")
        self.assertEqual(release_tags.remote_tags("origin"), {})

    def test_atomic_push_does_not_partially_publish(self):
        self.release("tenzir")
        self.release("suricata")
        head = self.commit()
        hook = Path(self.remote) / "hooks/update"
        hook.write_text('#!/bin/sh\n[ "$1" != "refs/tags/tenzir/v0.1.0" ]\n')
        hook.chmod(0o755)
        with self.assertRaises(subprocess.CalledProcessError):
            release_tags.publish_tags(
                ["suricata/v0.1.0", "tenzir/v0.1.0"], head, "origin"
            )
        self.assertEqual(release_tags.remote_tags("origin"), {})


if __name__ == "__main__":
    unittest.main()
