import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from backupverify.__main__ import main
from backupverify.manifest import build_manifest, load_manifest, save_manifest
from backupverify.verify import verify


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "data"
        (self.root / "sub").mkdir(parents=True)
        (self.root / "a.txt").write_text("abc", encoding="utf-8")
        (self.root / "sub" / "b.txt").write_text("hello", encoding="utf-8")
        self.manifest = build_manifest(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_unchanged_folder_is_clean(self):
        report = verify(self.root, self.manifest)
        self.assertTrue(report.clean)
        self.assertEqual(sorted(report.ok), ["a.txt", "sub/b.txt"])

    def test_same_size_different_content_is_changed(self):
        (self.root / "a.txt").write_text("xyz", encoding="utf-8")
        report = verify(self.root, self.manifest)
        self.assertEqual(report.changed, ["a.txt"])
        self.assertFalse(report.clean)

    def test_deleted_file_is_missing(self):
        (self.root / "sub" / "b.txt").unlink()
        self.assertEqual(verify(self.root, self.manifest).missing, ["sub/b.txt"])

    def test_added_file_is_new(self):
        (self.root / "c.txt").write_text("new", encoding="utf-8")
        self.assertEqual(verify(self.root, self.manifest).new, ["c.txt"])

    def test_symlinks_are_skipped(self):
        outside = Path(self.tmp.name) / "secret.txt"
        outside.write_text("outside", encoding="utf-8")
        (self.root / "link.txt").symlink_to(outside)
        self.assertNotIn("link.txt", build_manifest(self.root)["files"])

    def test_manifest_round_trip_and_version_check(self):
        path = Path(self.tmp.name) / "m.json"
        save_manifest(self.manifest, path)
        self.assertEqual(load_manifest(path), self.manifest)
        path.write_text(json.dumps({"version": 99, "files": {}}), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_manifest(path)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "data"
        self.root.mkdir()
        (self.root / "a.txt").write_text("abc", encoding="utf-8")
        self.manifest = Path(self.tmp.name) / "m.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["backupverify", *args])
        return code, out.getvalue()

    def test_create_then_verify_exit_codes(self):
        code, _ = self.run_cli("create", str(self.root), str(self.manifest))
        self.assertEqual(code, 0)
        self.assertEqual(self.run_cli("verify", str(self.root), str(self.manifest))[0], 0)
        (self.root / "a.txt").write_text("xyz", encoding="utf-8")
        code, out = self.run_cli("verify", str(self.root), str(self.manifest))
        self.assertEqual(code, 1)
        self.assertIn("changed: a.txt", out)

    def test_usage_and_bad_input_exit_2(self):
        self.assertEqual(main(["backupverify"]), 2)
        self.assertEqual(main(["backupverify", "verify", "/no/such/dir", str(self.manifest)]), 2)


if __name__ == "__main__":
    unittest.main()
