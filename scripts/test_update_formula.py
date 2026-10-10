import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import update_formula as updater


class UpdateTests(unittest.TestCase):
    def release(self, **overrides):
        version = "0.3.0"
        names = [f"circuit_{version}_{os_name}_{arch}.tar.gz" for os_name in ("darwin", "linux") for arch in ("arm64", "amd64")]
        return {"tag_name": "v" + version, "draft": False, "prerelease": False,
                "assets": [{"name": name} for name in names + ["checksums.txt"]], **overrides}

    def test_drafts_prereleases_and_invalid_tags_are_rejected(self):
        for changes in ({"draft": True}, {"prerelease": True}, {"tag_name": "v0.3.0-rc.1"}, {"tag_name": "../main"}):
            with self.subTest(changes=changes), patch.object(updater, "release_commit") as commit:
                with self.assertRaises(RuntimeError):
                    updater.validated_release(self.release(**changes))
                commit.assert_not_called()

    def test_both_exact_commit_workflow_gates_are_required(self):
        commit = "a" * 40
        ci = {"head_sha": commit, "head_branch": "main", "status": "completed", "conclusion": "success", "event": "push"}
        release = {**ci, "head_branch": "v0.3.0"}
        for runs in ([[], [release]], [[ci], []], [[{**ci, "head_sha": "b" * 40}], [release]], [[ci], [{**release, "conclusion": "failure"}]]):
            with self.subTest(runs=runs), patch.object(updater, "release_commit", return_value=commit), patch.object(updater, "gh_json", side_effect=[{"workflow_runs": r} for r in runs]):
                with self.assertRaises(RuntimeError):
                    updater.validated_release(self.release())
        with patch.object(updater, "release_commit", return_value=commit), patch.object(updater, "gh_json", side_effect=[{"workflow_runs": [ci]}, {"workflow_runs": [release]}]):
            self.assertEqual(updater.validated_release(self.release()), "v0.3.0")

    def test_checksum_mismatch_does_not_change_formula(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Formula").mkdir()
            formula = root / "Formula/circuit.rb"
            original = 'class Circuit < Formula\n  version "0.1.0"\nend\n'
            formula.write_text(original)
            def download(command, **kwargs):
                out = Path(command[command.index("--dir") + 1])
                names = [a["name"] for a in self.release()["assets"] if a["name"] != "checksums.txt"]
                if "checksums.txt" in command:
                    digest = hashlib.sha256(b"expected").hexdigest()
                    (out / "checksums.txt").write_text("\n".join(f"{digest}  {name}" for name in names))
                else:
                    for name in names:
                        (out / name).write_bytes(b"tampered")
            with patch.object(updater, "ROOT", root), patch.object(updater, "gh_json", return_value=self.release()), patch.object(updater, "validated_release", return_value="v0.3.0"), patch.object(updater.subprocess, "run", side_effect=download):
                with self.assertRaisesRegex(RuntimeError, "checksum mismatch"):
                    updater.main()
            self.assertEqual(formula.read_text(), original)

    def test_duplicate_checksums_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            checksums = Path(tmp) / "checksums.txt"
            checksums.write_text(("a" * 64 + "  archive.tar.gz\n") * 2)
            with self.assertRaises(RuntimeError):
                updater.read_checksums(checksums)


if __name__ == "__main__":
    unittest.main()
