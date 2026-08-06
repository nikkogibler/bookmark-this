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
---
```

Rules:

- `url` is the safe saved URL.
- `canonical_url` is the verified canonical URL when available; otherwise use the safe saved URL.
- Add `original_url` only when the configuration permits it and it contains no secret or sensitive token.
- Use one or more configured category slugs.
- Use 3–8 lowercase kebab-case tags by default.
- Derive a concise lowercase kebab-case filename from the verified title.

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

## Updates

When updating an existing note:

- preserve user-authored prose and unknown frontmatter fields;
- refresh stale factual metadata narrowly;
- do not replace a user's personal reason with an agent inference;
- keep old source links when they still support retained content.
