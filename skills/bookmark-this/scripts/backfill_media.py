#!/usr/bin/env python3
"""Backfill preview and playable-media metadata across a Bookmark This library."""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("extract_page_metadata", SCRIPT_DIR / "extract_page_metadata.py")
media = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(media)

FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", re.MULTILINE)
MEDIA_FIELDS = ("preview_image", "preview_image_url", "preview_image_alt", "media_type", "embed_url", "video_url", "ticker", "chart_provider")


def frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    head, marker, body = text[4:].partition("\n---\n")
    if not marker:
        raise ValueError("unclosed YAML frontmatter")
    return head, body


def scalar_fields(head: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for match in FIELD_RE.finditer(head):
        raw = (match.group(2) or "").strip()
        if raw and not raw.startswith("["):
            try:
                values[match.group(1)] = str(json.loads(raw)) if raw.startswith('"') else raw.strip("'\"")
            except json.JSONDecodeError:
                values[match.group(1)] = raw.strip("'\"")
    return values


def set_scalars(head: str, updates: dict[str, str]) -> str:
    lines = head.splitlines()
    positions = {match.group(1): index for index, line in enumerate(lines) if (match := re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):", line))}
    for key, value in updates.items():
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
        if key in positions:
            lines[positions[key]] = line
        else:
            lines.append(line)
    return "\n".join(lines)


def relative_preview(root: Path, raw: str) -> str:
    path = Path(raw)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return ""


def inspect_note(path: Path, root: Path, image_dir: Path | None, overwrite: bool) -> dict:
    text = path.read_text(encoding="utf-8")
    head, _ = frontmatter(text)
    fields = scalar_fields(head)
    url = fields.get("url", "")
    if not url.startswith(("http://", "https://")):
        return {"path": path, "status": "skipped", "reason": "no public HTTP URL"}
    if not overwrite and (fields.get("preview_image") or fields.get("preview_image_url") or fields.get("media_type") in {"video", "stock"}):
        return {"path": path, "status": "skipped", "reason": "media already present"}
    try:
        result = media.extract(url, fields.get("ticker", ""), image_dir)
    except Exception as exc:
        return {"path": path, "status": "failed", "reason": f"{type(exc).__name__}: {exc}"}
    updates = {key: str(result[key]) for key in MEDIA_FIELDS if result.get(key)}
    if updates.get("preview_image"):
        updates["preview_image"] = relative_preview(root, updates["preview_image"])
        if not updates["preview_image"]:
            updates.pop("preview_image")
    if not updates or updates.get("media_type") == "none":
        return {"path": path, "status": "no-media", "reason": "page exposed no supported preview metadata"}
    updates["media_checked"] = date.today().isoformat()
    return {"path": path, "status": "ready", "updates": updates, "text": text}


def write_result(result: dict) -> dict:
    if result["status"] != "ready":
        return {key: str(value) if isinstance(value, Path) else value for key, value in result.items() if key not in {"text", "updates"}}
    path: Path = result["path"]
    head, body = frontmatter(result["text"])
    updated = "---\n" + set_scalars(head, result["updates"]) + "\n---\n" + body
    path.write_text(updated, encoding="utf-8")
    return {"path": str(path), "status": "updated", "fields": sorted(result["updates"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--cache-images", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    config_path = root / ".bookmark-system" / "config.json"
    if not config_path.is_file():
        print(f"ERROR: missing configuration: {config_path}", file=sys.stderr)
        return 2
    config = json.loads(config_path.read_text(encoding="utf-8"))
    notes_dir = root / config["paths"]["bookmarks"]
    asset_dir = root / config["paths"].get("assets", "bookmark-assets") if args.cache_images else None
    notes = sorted(notes_dir.rglob("*.md"))
    notes = notes[max(0, args.offset):]
    if args.limit is not None:
        notes = notes[: max(0, args.limit)]
    workers = max(1, min(args.workers, 24))
    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(inspect_note, path, root, asset_dir, args.overwrite) for path in notes]
        for future in concurrent.futures.as_completed(futures):
            results.append(write_result(future.result()))
    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    report = {"root": str(root), "examined": len(notes), "counts": counts, "results": sorted(results, key=lambda item: item["path"])}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"examined": len(notes), "counts": counts}, indent=2))
    return 1 if counts.get("failed", 0) == len(notes) and notes else 0


if __name__ == "__main__":
    raise SystemExit(main())
