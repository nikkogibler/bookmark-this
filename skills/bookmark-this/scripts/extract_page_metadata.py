#!/usr/bin/env python3
"""Extract safe preview and playable-media metadata from one public URL."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urljoin, urlsplit
from urllib.request import Request, urlopen


USER_AGENT = "BookmarkThis/0.2 (+https://github.com/nikkogibler/bookmark-this)"
MAX_HTML_BYTES = 3_000_000
MAX_IMAGE_BYTES = 8_000_000
VIDEO_EXTENSIONS = {".mp4", ".webm", ".m4v", ".mov"}


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "meta":
            key = (values.get("property") or values.get("name") or "").lower()
            content = values.get("content", "").strip()
            if key and content and key not in self.meta:
                self.meta[key] = content
        elif tag.lower() == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical = values.get("href", "").strip()
        elif tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def fetch(url: str, max_bytes: int = MAX_HTML_BYTES, metadata_only: bool = False) -> tuple[bytes, str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,image/*;q=.8,*/*;q=.5"})
    with urlopen(request, timeout=18) as response:
        content_type = response.headers.get_content_type()
        final_url = response.geturl()
        payload = b"" if metadata_only and content_type not in {"text/html", "application/xhtml+xml"} else response.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ValueError(f"response exceeded {max_bytes} bytes")
    return payload, content_type, final_url


def youtube_embed(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower().removeprefix("www.")
    video_id = ""
    if host == "youtu.be":
        video_id = parts.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com"}:
        if parts.path == "/watch":
            video_id = parse_qs(parts.query).get("v", [""])[0]
        else:
            match = re.match(r"^/(?:shorts|embed|live)/([A-Za-z0-9_-]{6,})", parts.path)
            video_id = match.group(1) if match else ""
    return f"https://www.youtube-nocookie.com/embed/{video_id}" if re.fullmatch(r"[A-Za-z0-9_-]{6,}", video_id) else ""


def provider_embed(url: str) -> str:
    youtube = youtube_embed(url)
    if youtube:
        return youtube
    parts = urlsplit(url)
    host = (parts.hostname or "").lower().removeprefix("www.")
    if host == "vimeo.com":
        match = re.search(r"/(\d{5,})", parts.path)
        if match:
            return f"https://player.vimeo.com/video/{match.group(1)}"
    if host == "instagram.com":
        match = re.match(r"^/(p|reel|tv)/([A-Za-z0-9_-]+)", parts.path)
        if match:
            return f"https://www.instagram.com/{match.group(1)}/{match.group(2)}/embed/"
    return ""


def safe_absolute(base: str, raw: str) -> str:
    value = urljoin(base, raw.strip())
    return value if urlsplit(value).scheme in {"http", "https"} else ""


def choose(meta: dict[str, str], *keys: str) -> str:
    for key in keys:
        if meta.get(key):
            return meta[key].strip()
    return ""


def download_image(url: str, directory: Path) -> Path:
    payload, content_type, final_url = fetch(url, MAX_IMAGE_BYTES)
    if not content_type.startswith("image/"):
        raise ValueError(f"preview URL returned {content_type}, not an image")
    suffix = mimetypes.guess_extension(content_type) or Path(urlsplit(final_url).path).suffix.lower() or ".img"
    if suffix == ".jpe":
        suffix = ".jpg"
    digest = hashlib.sha256(final_url.encode("utf-8")).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"preview-{digest}{suffix}"
    if not target.exists():
        target.write_bytes(payload)
    return target


def extract(url: str, ticker: str, image_dir: Path | None) -> dict[str, str]:
    known_embed = provider_embed(url)
    try:
        payload, content_type, final_url = fetch(url, metadata_only=True)
    except (HTTPError, URLError, TimeoutError, OSError):
        if not known_embed:
            raise
        result = {"source_url": url, "resolved_url": url, "media_type": "video", "embed_url": known_embed}
        youtube_id = known_embed.rsplit("/", 1)[-1] if "youtube-nocookie.com/embed/" in known_embed else ""
        if youtube_id:
            image_url = f"https://i.ytimg.com/vi/{quote(youtube_id)}/hqdefault.jpg"
            result["preview_image_url"] = image_url
            if image_dir:
                try:
                    result["preview_image"] = str(download_image(image_url, image_dir))
                except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
                    result["preview_image_error"] = str(exc)
        return result
    result: dict[str, str] = {"source_url": url, "resolved_url": final_url, "content_type": content_type}
    direct_suffix = Path(urlsplit(final_url).path).suffix.lower()
    if content_type.startswith("video/") or direct_suffix in VIDEO_EXTENSIONS:
        result.update({"media_type": "video", "video_url": final_url})
        return result
    if content_type.startswith("image/"):
        result.update({"media_type": "image", "preview_image_url": final_url})
        if image_dir:
            result["preview_image"] = str(download_image(final_url, image_dir))
        return result
    if "html" not in content_type and "xhtml" not in content_type:
        return result

    parser = MetadataParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    meta = parser.meta
    title = choose(meta, "og:title", "twitter:title") or re.sub(r"\s+", " ", "".join(parser.title_parts)).strip()
    description = choose(meta, "og:description", "twitter:description", "description")
    image_url = safe_absolute(final_url, choose(meta, "og:image:secure_url", "og:image", "twitter:image", "twitter:image:src"))
    image_alt = choose(meta, "og:image:alt", "twitter:image:alt")
    video_candidate = safe_absolute(final_url, choose(meta, "og:video:secure_url", "og:video:url", "og:video"))
    video_url = ""
    video_type = choose(meta, "og:video:type")
    embed_url = provider_embed(final_url)
    if video_candidate:
        video_suffix = Path(urlsplit(video_candidate).path).suffix.lower()
        if video_type.startswith("video/") or video_suffix in VIDEO_EXTENSIONS:
            video_url = video_candidate
        elif video_type.startswith("text/html") and not embed_url:
            embed_url = provider_embed(video_candidate)
    canonical = safe_absolute(final_url, parser.canonical or choose(meta, "og:url")) or final_url
    result.update({"title": title, "description": description, "canonical_url": canonical})
    if image_url:
        result["preview_image_url"] = image_url
        result["preview_image_alt"] = image_alt
        if image_dir:
            try:
                result["preview_image"] = str(download_image(image_url, image_dir))
            except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
                result["preview_image_error"] = str(exc)
    if embed_url or video_url:
        result["media_type"] = "video"
        if embed_url:
            result["embed_url"] = embed_url
        if video_url:
            result["video_url"] = video_url
    elif image_url:
        result["media_type"] = "image"
    else:
        result["media_type"] = "none"
    if ticker:
        normalized = ticker.strip().upper()
        if not re.fullmatch(r"[A-Z0-9._:-]{1,24}", normalized):
            raise ValueError("ticker must contain only letters, digits, dot, underscore, colon, or hyphen")
        result["media_type"] = "stock"
        result["ticker"] = normalized
        result["chart_provider"] = "tradingview"
    return {key: value for key, value in result.items() if value != ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--ticker", default="", help="Explicit exchange-qualified symbol, for example NASDAQ:AAPL")
    parser.add_argument("--image-dir", type=Path, help="Download the Open Graph image into this directory")
    args = parser.parse_args()
    if urlsplit(args.url).scheme not in {"http", "https"}:
        print("ERROR: URL must use http or https", file=sys.stderr)
        return 2
    try:
        print(json.dumps(extract(args.url, args.ticker, args.image_dir), indent=2, ensure_ascii=False))
        return 0
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
