import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "bookmark-this" / "scripts" / "bookmark_system.py"
SPEC = importlib.util.spec_from_file_location("bookmark_system", SCRIPT)
bookmark_system = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bookmark_system)


class BookmarkSystemTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        config_dir = self.root / ".bookmark-system"
        bookmarks_dir = self.root / "bookmarks"
        config_dir.mkdir()
        bookmarks_dir.mkdir()
        config = json.loads((REPO_ROOT / "examples" / "config.json").read_text(encoding="utf-8"))
        (config_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        (bookmarks_dir / "example.md").write_text(
            (REPO_ROOT / "examples" / "example-bookmark.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_rebuild_visualize_and_validate(self):
        config = bookmark_system.load_config(self.root)
        bookmark_system.rebuild(self.root, config)
        bookmark_system.visualize(self.root, config)
        self.assertEqual(bookmark_system.validate(self.root, config), 0)

        index = (self.root / "index.md").read_text(encoding="utf-8")
        visualizer = (self.root / "visualizer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Example Research Tool", index)
        self.assertIn("Research", index)
        self.assertIn("Example Research Tool", visualizer)
        self.assertIn('id="search"', visualizer)
        self.assertIn("Why this survived", visualizer)
        self.assertIn("Current session", visualizer)
        self.assertIn("data:image/png;base64,", visualizer)
        self.assertIn('id="graph-canvas"', visualizer)
        self.assertIn("Relationship map", visualizer)

    def test_refuses_to_replace_unmarked_index(self):
        config = bookmark_system.load_config(self.root)
        (self.root / "index.md").write_text("Personal notes\n", encoding="utf-8")
        with self.assertRaises(bookmark_system.SystemError):
            bookmark_system.rebuild(self.root, config)

    def test_ingestion_defaults_are_safe(self):
        config = bookmark_system.load_config(self.root)
        self.assertFalse(config["ingestion"]["enabled"])
        self.assertTrue(config["ingestion"]["deduplicate"])
        self.assertTrue(config["ingestion"]["preserve_legacy_folders"])
        self.assertFalse(config["ingestion"]["delete_sources"])

        config["ingestion"]["delete_sources"] = True
        (self.root / ".bookmark-system" / "config.json").write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(bookmark_system.SystemError):
            bookmark_system.load_config(self.root)


if __name__ == "__main__":
    unittest.main()
