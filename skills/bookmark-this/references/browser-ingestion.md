# Browser and folder ingestion

Use this workflow when setup includes existing bookmarks or the user later asks for a roundup.

## Supported inputs

- Chrome, Chromium, Brave, Edge, and other Chromium bookmark JSON files
- Firefox bookmark exports or a bookmarks backup; prefer a native export over reading a live places database
- Safari bookmarks or a native Safari bookmark export
- Netscape-format bookmark HTML exported by a browser
- Existing Markdown bookmark folders approved by the user
- Other structured bookmark files after inspecting their format read-only

Do not treat browser history, cookies, credentials, autofill, reading lists, or open tabs as bookmarks unless the user separately and explicitly puts them in scope.

## Safe sequence

1. Confirm the browsers, profiles, exports, and folders in scope.
2. Locate only standard bookmark stores or user-supplied paths with read-only checks.
3. If direct access is blocked, request the smallest relevant permission or ask for a native bookmark export. Do not request broad browser data when an export will work.
4. Parse folders recursively and retain source, profile, original title, original folder path, and original saved date when available.
5. Sanitize URLs and group duplicates by canonical or safely normalized URL. Preserve meaningful query parameters; remove fragments and common tracking parameters. Never retain credentials or secret tokens.
6. Compare the inventory with existing bookmark-note frontmatter.
7. Report totals, duplicate groups, destination overlap, non-web entries, inaccessible inputs, and the proposed category mapping.
8. Import only the accepted scope. Merge provenance when the same URL appears in several sources. Never overwrite user-authored prose.
9. Mark pages that were not opened and verified as `imported-unverified` in an additional metadata field while keeping the schema-compatible bookmark status.
10. Rebuild navigation and the visualizer, validate the result, and report failures or items still awaiting enrichment.

## Import quality

An inventory is not full enrichment. For large libraries, make the distinction explicit:

- **Imported:** safely deduplicated, searchable, categorized, tagged, and traceable to its old browser folder.
- **Verified:** the live page was opened and its current title, canonical URL, description, and caveats were checked.
- **Enriched:** the note contains source-grounded key details and, when enabled, a context-grounded personal-relevance inference.

Import the whole accepted library first, then enrich progressively or in user-approved batches. Do not pretend hundreds of links were individually verified when only browser metadata was available.

## Reversibility

- Never delete, reorder, or rewrite bookmarks in a browser.
- Never delete exports after use.
- Keep a local migration report with source counts, merge counts, skipped items, and errors.
- A rerun should update matching notes or merge new provenance, not create duplicates.
