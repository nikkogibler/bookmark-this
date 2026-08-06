# Bookmark note schema

## Frontmatter

Every note must include:

```yaml
---
title: Example page
type: web-bookmark
url: https://example.com/page
canonical_url: https://example.com/page
domain: example.com
captured: 2026-08-06
tags:
  - example-tag
categories:
  - research
status: bookmarked
context_basis:
  - Current session
keywords:
  - example topic
source_profiles:
  - Example Browser
legacy_folders:
  - Bookmarks / Research
enrichment_status: verified
preview_image: bookmark-assets/example-page-og.jpg
preview_image_url: https://example.com/og.jpg
preview_image_alt: Example page preview
media_type: image
---
```

Rules:

- `url` is the safe saved URL.
- `canonical_url` is the verified canonical URL when available; otherwise use the safe saved URL.
- Add `original_url` only when the configuration permits it and it contains no secret or sensitive token.
- Use one or more configured category slugs.
- Use 3–8 lowercase kebab-case tags by default.
- Derive a concise lowercase kebab-case filename from the verified title.
- `context_basis` is optional. When present, list only readable labels for context the user approved; never copy private text or expose a sensitive path.
- `keywords` is optional. Use short, factual concepts that improve retrieval without duplicating every tag.
- `source_profiles` and `legacy_folders` preserve browser-import provenance. Use readable labels, never browser profile paths.
- `enrichment_status` distinguishes imported, verified, and enriched records without changing the durable `status: bookmarked` contract.
- `preview_image` is the root-relative path to a safely cached Open Graph or equivalent preview image. Prefer it over remote hotlinking.
- `preview_image_url` preserves the public source URL for refreshes and provenance. It must not contain credentials or sensitive tokens.
- `preview_image_alt` comes from verified page metadata when available; otherwise write a concise factual description or leave it empty.
- `media_type` may be `none`, `image`, `video`, or `stock`.
- For playable video, add `embed_url` only for an approved provider URL or `video_url` for a direct HTTPS video file. An embed is a convenience, not a guarantee that the publisher permits playback.
- For a market bookmark, add an explicit exchange-qualified `ticker`, such as `NASDAQ:AAPL`, and `chart_provider`. Do not infer a ticker from an ambiguous company name.

## Body

Adapt detail to the configured capture depth while keeping these semantics:

```markdown
# Example page

**URL:** https://example.com/page
**Captured:** 2026-08-06

## What it is

A concise, source-grounded description.

## Key details

- Important facts, claims, people, dates, or ideas.

## Why it may be useful

Practical reasons to return to the page.

## Caveats

Verification gaps, source limitations, conflicts, compatibility concerns, or marketing claims.

## Why I may have saved it

**Inference, not confirmed:** A cautious explanation grounded in available user context.

## Sources

- [Original page](https://example.com/page)
```

For `quick` depth, omit `Key details` and `Caveats` only when there is nothing material to preserve. For `deep` depth, add corroborating sources and distinguish their claims. Omit the personal-relevance section when disabled.

The inference should be specific enough to be useful but must not claim motives as fact. If no approved context supports a personal connection, say so or omit the section instead of generating a generic personality reading.

## Updates

When updating an existing note:

- preserve user-authored prose and unknown frontmatter fields;
- refresh stale factual metadata narrowly;
- do not replace a user's personal reason with an agent inference;
- keep old source links when they still support retained content.
