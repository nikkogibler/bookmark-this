import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "bookmark-this" / "scripts" / "bookmark_system.py"
SPEC = importlib.util.spec_from_file_location("bookmark_system", SCRIPT)
bookmark_system = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bookmark_system)
MEDIA_SCRIPT = REPO_ROOT / "skills" / "bookmark-this" / "scripts" / "extract_page_metadata.py"
MEDIA_SPEC = importlib.util.spec_from_file_location("extract_page_metadata", MEDIA_SCRIPT)
extract_page_metadata = importlib.util.module_from_spec(MEDIA_SPEC)
assert MEDIA_SPEC.loader is not None
MEDIA_SPEC.loader.exec_module(extract_page_metadata)
BACKFILL_SCRIPT = REPO_ROOT / "skills" / "bookmark-this" / "scripts" / "backfill_media.py"
BACKFILL_SPEC = importlib.util.spec_from_file_location("backfill_media", BACKFILL_SCRIPT)
backfill_media = importlib.util.module_from_spec(BACKFILL_SPEC)
assert BACKFILL_SPEC.loader is not None
BACKFILL_SPEC.loader.exec_module(backfill_media)


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
        self.assertIn('id="facet-kind"', visualizer)
        self.assertIn('id="facet-search"', visualizer)
        self.assertIn('id="sort-by"', visualizer)
        self.assertIn('id="group-by"', visualizer)
        self.assertIn("node('details','bookmark-group')", visualizer)
        self.assertIn("node('summary','group-head')", visualizer)
        self.assertIn("Why this survived", visualizer)
        self.assertIn("Current session", visualizer)
        self.assertIn("data:image/png;base64,", visualizer)
        self.assertIn("data:image/jpeg;base64,", visualizer)
        self.assertNotIn('id="graph-canvas"', visualizer)
        self.assertNotIn('id="graph-view"', visualizer)
        self.assertNotIn("Relationship map", visualizer)
        self.assertIn('data-theme-choice="archive"', visualizer)
        self.assertIn('data-theme-choice="grove"', visualizer)
        self.assertIn('data-theme-choice="signal"', visualizer)
        self.assertIn('data-theme-choice="monograph"', visualizer)
        self.assertIn('data-mode-choice="dark"', visualizer)
        self.assertIn("bookmark-this-theme", visualizer)
        payload_match = re.search(r'<script id="bookmark-data" type="application/json">(.*?)</script>', visualizer, re.DOTALL)
        self.assertIsNotNone(payload_match)
        payload = json.loads(payload_match.group(1))
        self.assertEqual(payload["items"][0]["sourceProfiles"], ["Example Browser"])
        self.assertEqual(payload["items"][0]["legacyFolders"], ["Bookmarks / Research"])
        self.assertEqual(payload["items"][0]["keywords"], ["evidence mapping", "research workflow"])
        self.assertEqual(payload["items"][0]["enrichmentStatus"], "verified")
        self.assertEqual(payload["items"][0]["id"], "bookmarks/example.md")
        self.assertFalse(payload["items"][0]["hidden"])
        template = (REPO_ROOT / "skills" / "bookmark-this" / "assets" / "visualizer-template.html").read_text(encoding="utf-8")
        self.assertIn("__BACKGROUND_IMAGE__", template)
        self.assertIn("var(--background-art)", template)
        self.assertIn("var(--dashboard-wash)", template)
        self.assertIn("let theme = 'monograph', mode = 'dark';", template)
        self.assertIn("theme = 'monograph'; if (!modes.has(mode)) mode = 'dark';", template)
        self.assertIn('"richMedia"', visualizer)
        self.assertIn("Load playable media", visualizer)
        self.assertIn("__BOOKMARK_EDIT_TOKEN__", visualizer)
        self.assertIn("Manage bookmark", visualizer)
        self.assertIn("Filtered out 0", visualizer)

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

    def test_rich_media_defaults_are_private(self):
        config = bookmark_system.load_config(self.root)
        self.assertTrue(config["rich_media"]["cache_preview_images"])
        self.assertFalse(config["rich_media"]["allow_remote_video_embeds"])
        self.assertFalse(config["rich_media"]["allow_remote_stock_charts"])
        self.assertTrue(config["visualizer"]["editing_enabled"])

    def test_visualizer_mutations_write_markdown_and_use_recoverable_trash(self):
        config = bookmark_system.load_config(self.root)
        bookmark_system.rebuild(self.root, config)
        bookmark_system.visualize(self.root, config)
        note = self.root / "bookmarks" / "example.md"

        result = bookmark_system.mutate_bookmark(
            self.root,
            config,
            {"action": "set-tags", "id": "bookmarks/example.md", "tags": ["Research Notes", "AI"]},
        )
        self.assertEqual(result["tags"], ["research-notes", "ai"])
        self.assertEqual(bookmark_system.parse_frontmatter(note)["tags"], ["research-notes", "ai"])

        bookmark_system.mutate_bookmark(self.root, config, {"action": "hide", "id": "bookmarks/example.md"})
        self.assertTrue(bookmark_system.metadata_bool(bookmark_system.parse_frontmatter(note)["visualizer_hidden"]))
        bookmark_system.mutate_bookmark(self.root, config, {"action": "restore", "id": "bookmarks/example.md"})
        self.assertFalse(bookmark_system.metadata_bool(bookmark_system.parse_frontmatter(note)["visualizer_hidden"]))

        result = bookmark_system.mutate_bookmark(self.root, config, {"action": "trash", "id": "bookmarks/example.md"})
        self.assertFalse(note.exists())
        self.assertTrue((self.root / result["trash"]).is_file())
        self.assertNotIn("Example Research Tool", (self.root / "visualizer" / "index.html").read_text(encoding="utf-8"))

    def test_visualizer_mutations_reject_paths_outside_bookmarks(self):
        config = bookmark_system.load_config(self.root)
        with self.assertRaises(bookmark_system.SystemError):
            bookmark_system.mutate_bookmark(
                self.root,
                config,
                {"action": "hide", "id": "../example.md"},
            )
        with self.assertRaises(bookmark_system.SystemError):
            bookmark_system.serve(self.root, config, "0.0.0.0", 0)

    def test_extracts_open_graph_video_and_explicit_ticker(self):
        html = b'''<html><head>
        <title>Fallback title</title>
        <meta property="og:title" content="Example market video">
        <meta property="og:image" content="/share.jpg">
        <meta property="og:image:alt" content="A market chart">
        <link rel="canonical" href="https://example.com/watch">
        </head></html>'''
        with patch.object(extract_page_metadata, "fetch", return_value=(html, "text/html", "https://example.com/watch")):
            result = extract_page_metadata.extract("https://example.com/watch", "NASDAQ:AAPL", None)
        self.assertEqual(result["title"], "Example market video")
        self.assertEqual(result["preview_image_url"], "https://example.com/share.jpg")
        self.assertEqual(result["media_type"], "stock")
        self.assertEqual(result["ticker"], "NASDAQ:AAPL")

    def test_provider_embed_allowlist_targets(self):
        self.assertEqual(
            extract_page_metadata.provider_embed("https://youtu.be/dQw4w9WgXcQ"),
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
        )
        self.assertEqual(
            extract_page_metadata.provider_embed("https://www.instagram.com/reel/ABC_123/"),
            "https://www.instagram.com/reel/ABC_123/embed/",
        )

    def test_visualizer_keywords_prefer_explicit_values_and_derive_a_fallback(self):
        self.assertEqual(
            bookmark_system.visualizer_keywords(
                {"keywords": ["Evidence Mapping", "research workflow"]},
                "Ignored title",
                "example.com",
            ),
            ["Evidence Mapping", "research workflow"],
        )
        self.assertEqual(
            bookmark_system.visualizer_keywords({}, "A Better Research Workflow", "example.com"),
            ["better", "research", "workflow"],
        )

    def test_media_backfill_preserves_note_body(self):
        note = self.root / "bookmarks" / "example.md"
        original = note.read_text(encoding="utf-8")
        with patch.object(
            backfill_media.media,
            "extract",
            return_value={
                "media_type": "video",
                "preview_image_url": "https://example.com/preview.jpg",
                "embed_url": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            },
        ):
            result = backfill_media.inspect_note(note, self.root, None, False)
        written = backfill_media.write_result(result)
        updated = note.read_text(encoding="utf-8")
        self.assertEqual(written["status"], "updated")
        self.assertIn('media_type: "video"', updated)
        self.assertIn("## What it is\n\nA minimal example showing the bookmark structure.", updated)
        self.assertIn("## Sources\n\n- [Original page](https://example.com/research)", updated)
        self.assertNotEqual(original, updated)


if __name__ == "__main__":
    unittest.main()
