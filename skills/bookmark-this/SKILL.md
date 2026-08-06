---
name: bookmark-this
description: Set up and operate a user-owned Markdown bookmark system that can import browser bookmarks, verify and capture URLs, prevent duplicates, write structured notes, generate navigable indexes, and run an editable local visualizer. Use when a user says "set up my bookmark system," "bookmark this," or "save this link"; asks to import, organize, rebuild, or validate bookmarks; or wants to edit tags, filter records out, restore them, or remove them through the visualizer.
---

# Bookmark This

Build a portable bookmark library around the user's own goals, folders, taxonomy, and privacy choices. Keep facts distinct from the agent's explicitly labelled inference about why a link matters.

## Choose the mode

- **Setup:** No valid `.bookmark-system/config.json` exists, or the user asks to set up, configure, reorganize, or migrate their bookmark system.
- **Capture:** A valid configuration exists and the user supplies one or more URLs to save.
- **Maintain:** The user asks to rebuild navigation, check links or metadata, repair the hierarchy, or change preferences.

Never assume a personal path, name, taxonomy, note-taking app, or project context. Personal context is opt-in: use only the conversation, scopes, and files the user explicitly approves.

## Setup

Read [setup-interview.md](references/setup-interview.md) and conduct the interview in small rounds. Ask at most three questions at once. Prefer proposing editable defaults over making the user design a taxonomy from scratch. When adapting installation or invocation to Codex, Claude, Hermes, OpenClaw, or another platform, read [platform-adaptation.md](references/platform-adaptation.md).

After the interview:

1. Summarize the preferred agentic platform, browser-ingestion choice, approved source paths, proposed root, hierarchy, categories, visualizer choice, rich-media/privacy choices, capture depth, inference policy, approved context sources, and migration scope.
2. Resolve the root to an absolute path. If it does not exist, ask before creating it only when the location is ambiguous or outside the user's stated scope.
3. Create the structure defined in [system-contract.md](references/system-contract.md). Preserve existing files and directories; never replace an existing system silently.
4. Write `.bookmark-system/config.json` using the schema in that reference. Store no secrets.
5. Create `index.md`, the configured bookmark directory, `views/categories/`, `views/tags/`, and `collections/`. When preview caching is enabled, also create the configured asset folder, defaulting to `bookmark-assets/`.
6. If browser ingestion is enabled, follow [browser-ingestion.md](references/browser-ingestion.md): locate only approved sources, inventory them read-only, present totals and conflicts, and import only after the migration scope is accepted.
7. Run `python3 scripts/bookmark_system.py rebuild <root>`. If the visualizer is enabled, run `python3 scripts/bookmark_system.py visualize <root>`.
8. Run `python3 scripts/bookmark_system.py validate <root>`.
9. Report the created hierarchy, configuration choices, ingestion result, validation result, visualizer path when enabled, and three platform-appropriate example prompts.

Do not capture a URL during setup unless the user also supplied one. If they did, finish setup first and then use Capture mode.

## Capture

### 1. Load the system

Find the configuration in this order:

1. A root or config path stated by the user.
2. `.bookmark-system/config.json` in the current directory or its parents.
3. A location established earlier in the conversation.

If none is found, switch to Setup. Do not invent a destination.

### 2. Verify the URL

- Open the page. If retrieval fails, search the exact URL, title, domain, or distinctive slug.
- Prefer the page and first-party sources. Use reputable secondary sources only to fill gaps.
- Do not invent unavailable details. Record verification limits.
- Remove credentials, sensitive tokens, and non-identifying tracking parameters from the saved URL. Preserve an unsanitized original only when it is safe and the configuration requests it.
- Record the capture date in the configured timezone.
- When rich media is enabled, run the extractor from the bookmark root with `python3 <skill-directory>/scripts/extract_page_metadata.py <url> --image-dir <configured-assets-folder>` or perform an equivalent verified extraction. Prefer the page's Open Graph image, then Twitter Card image. Store the returned cached path root-relative in the note.
- Detect supported video providers or direct HTTPS video files. Record only allowlisted provider embeds or verified direct video URLs. Preserve the preview image and ordinary source link when playback is blocked or unsupported.
- Treat a page as a stock chart only when the user supplied a ticker or the page unambiguously identifies an exchange-qualified symbol. Record the ticker; never guess from a company name.

### 3. Prevent duplicates

Search existing bookmark frontmatter for both the canonical URL and safe original URL. Update the existing note when either matches. Preserve personal notes and user-authored sections. Never create a duplicate merely because the title or slug changed.

### 4. Write the note

Follow [bookmark-schema.md](references/bookmark-schema.md). Choose categories from the configured list. Add 3–8 specific lowercase kebab-case tags unless the configuration says otherwise.

Keep the personal-relevance section only when enabled. Prefix agent-generated reasoning with the configured label, defaulting to `**Inference, not confirmed:**`. Do not imply knowledge of the user that is not present in the conversation, configuration, or local context they authorized.

When context use is enabled, read only the approved sources needed for the current inference. Record readable source labels in `context_basis`; do not copy private context into frontmatter or expose sensitive paths. If the configured source is missing or unavailable, continue with the remaining approved context and state the limitation rather than widening access.

### 5. Rebuild and validate

Run:

```bash
python3 <skill-directory>/scripts/bookmark_system.py rebuild <root>
python3 <skill-directory>/scripts/bookmark_system.py visualize <root>  # when enabled
python3 <skill-directory>/scripts/bookmark_system.py validate <root>
```

Fix failures before reporting success. Report whether the note was created or updated and link to it and the central index.

## Maintain

- Use `rebuild` after category, tag, title, or path changes. It replaces only files marked as generated by this skill.
- Use `validate` before claiming the system is healthy.
- Use `visualize` to create or refresh the optional local visualizer. Direct HTML use is dependency-free and read-only.
- Use `python3 <skill-directory>/scripts/bookmark_system.py serve <root>` when the user wants to edit tags, persistently filter records out, restore filtered records, or remove a bookmark from the visualizer. The workspace binds only to localhost, writes approved frontmatter fields back to Markdown, and regenerates views after each change.
- Treat Markdown as the single source of truth. Do not introduce CSV or SQLite merely to support visualizer mutations.
- Make deletion recoverable: move removed Markdown notes to `.bookmark-system/trash/`; never permanently erase them from the visualizer.
- Refresh cached Open Graph artwork when the source changes or an image disappears. Remote video players and stock charts remain optional online enhancements; the Markdown note and cached image are the durable record.
- Use `python3 <skill-directory>/scripts/backfill_media.py <root> --report <report.json>` to enrich an existing library. Start with `--limit` on a representative batch, review failures and storage impact, then run the accepted full scope. Add `--cache-images` only when the user accepts the local storage cost.
- Change configuration narrowly and rebuild afterward.
- For taxonomy changes, update note metadata first, then rebuild views. Avoid moving bookmark files unless the user explicitly chose category folders during setup.
- For migration, inventory first, show mapping and conflicts, then make reversible edits. Never delete source bookmarks automatically.
- Offer browser roundup again when a user initially declined it, adds a browser later, or asks why saved links are missing. Follow [browser-ingestion.md](references/browser-ingestion.md).

## Safety and quality

- Keep the library local and user-owned unless the user explicitly asks to sync or publish it.
- Treat health, legal, financial, and safety-sensitive pages as reference material, not professional advice.
- Preserve uncertainty and distinguish source claims, verified facts, and inference.
- Do not copy large passages from sources.
- Do not mutate task managers, CRMs, browsers, or other external systems as a side effect of bookmarking.
