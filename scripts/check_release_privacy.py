#!/usr/bin/env python3
"""Fail a release audit when private bookmark material enters the public repo."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".html", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml",
}
ALLOWED_URL_HOSTS = {
    "127.0.0.1",
    "code.claude.com",
    "developers.openai.com",
    "docs.openclaw.ai",
    "example.com",
    "github.com",
    "hermes-agent.nousresearch.com",
    "i.ytimg.com",
    "localhost",
    "player.vimeo.com",
    "s.tradingview.com",
    "www.instagram.com",
    "www.youtube-nocookie.com",
    "youtu.be",
}
FORBIDDEN_MARKERS = {
    "/Users/": "absolute macOS home path",
    "\\Users\\": "absolute Windows home path",
    "Second Brain/web-bookmarks": "private bookmark-library path",
    "BEGIN PRIVATE KEY": "private key",
    "api_key=": "inline API key",
    "access_token=": "inline access token",
}
EXPECTED_PUBLIC_IMAGE_HASHES = {
    "images/bookmark-this-hero.jpg": "101a298f78875f239a7fefda0c7f8cc50820b4588e4d79a8a88ea95dcda832f8",
    "images/visualizer-preview.jpg": "2d1f413a642c20115032da9c53364bc0f5d3b8efda61e239519775c6f7d15530",
    "skills/bookmark-this/assets/visualizer-background.jpg": "75cbd4d7028dcd17fdcb64e643df61b750286a35c659c71a339b0d2d353f44f2",
    "skills/bookmark-this/assets/interzekt-logo.png": "daae7f4d900f87a6b8e2cf3fd7ed32515ee51c9b206fb8421a026a753707ae68",
    "skills/bookmark-this/assets/interzekt-logo-light.png": "8605b6abe0a6bde4cda9224b14e0299d224b486268e3b5d1fe28a4c1f92a6024",
}
URL_RE = re.compile(r"https?://[^\s\"'<>\])]+")
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")


def text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
    ]


def audit() -> list[str]:
    failures: list[str] = []
    for path in text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for marker, label in FORBIDDEN_MARKERS.items():
            if marker in text:
                failures.append(f"{relative}: contains {label}")
        for match in EMAIL_RE.finditer(text):
            failures.append(f"{relative}: contains email address {match.group(0)!r}")
        for raw_url in URL_RE.findall(text):
            parsed = urlsplit(raw_url)
            host = (parsed.hostname or "").lower()
            if host and host not in ALLOWED_URL_HOSTS:
                failures.append(f"{relative}: URL host is not release-approved: {host}")
            if host == "github.com" and not parsed.path.startswith("/nikkogibler/bookmark-this"):
                failures.append(f"{relative}: GitHub URL is outside the public Bookmark This repository")

    example = (ROOT / "examples" / "example-bookmark.md").read_text(encoding="utf-8")
    if "https://example.com/" not in example:
        failures.append("examples/example-bookmark.md: example must use the reserved example.com domain")

    preview_source = (ROOT / "tests" / "test_bookmark_system.py").read_text(encoding="utf-8")
    if 'REPO_ROOT / "examples" / "example-bookmark.md"' not in preview_source:
        failures.append("tests/test_bookmark_system.py: public visualizer fixture is no longer tied to the generic example")
    for relative, expected in EXPECTED_PUBLIC_IMAGE_HASHES.items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
        if actual != expected:
            failures.append(f"{relative}: public image changed; review it for private content before approving a new hash")
    return failures


def main() -> int:
    failures = audit()
    if failures:
        print("Release privacy check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Release privacy check passed: text and approved public images match the privacy manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
