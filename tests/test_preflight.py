import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import fnv_preflight as fnv


class EpicPreflightTests(unittest.TestCase):
    def test_manifest_finds_epic_install(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            install = root / "FalloutNewVegas"
            install.mkdir()
            (root / "game.item").write_text(json.dumps({
                "DisplayName": "Fallout New Vegas",
                "InstallLocation": str(install)
            }), encoding="utf-8")
            self.assertEqual(list(fnv.epic_install_roots(root)), [install])

    def test_language_folder(self):
        with tempfile.TemporaryDirectory() as d:
            game = Path(d) / "FalloutNewVegas"
            data = game / "Fallout New Vegas English" / "Data"
            data.mkdir(parents=True)
            (data / "FalloutNV.esm").write_bytes(b"TES4" + b"\x00" * 32)
            (data / "Fallout - Meshes.bsa").write_bytes(
                b"BSA\x00" + (104).to_bytes(4, "little") + b"\x00" * 28)
            self.assertEqual(fnv.find_data(game), data)
            report = fnv.audit(data, "manual")
            self.assertTrue(report["required_ok"])
            self.assertEqual(report["language"], "English")
            self.assertNotIn(str(data), json.dumps(report))

    def test_missing_meshes_bsa(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "FalloutNV.esm").write_bytes(b"TES4" + b"\x00" * 32)
            report = fnv.audit(root)
            self.assertFalse(report["required_ok"])
            self.assertIn("Fallout - Meshes.bsa", report["missing_required"])


if __name__ == "__main__":
    unittest.main()
