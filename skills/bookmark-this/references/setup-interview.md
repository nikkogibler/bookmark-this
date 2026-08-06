# Setup interview

The goal is to learn enough to create a useful first hierarchy without turning setup into a questionnaire. Ask in rounds and adapt to answers.

## Round 1: start here

Ask:

1. Which agentic platform should this work with: Codex, Claude, Hermes, OpenClaw, another platform, or no preference?
2. Should setup round up existing bookmarks from their browsers and bookmark folders? Offer Chrome, Safari, Firefox, Edge, Brave, an exported bookmarks HTML file, named folders, `all available sources`, or `not now`. Let them say `I don't know` so the agent can locate likely sources with read-only checks.
3. Do they want a local bookmark visualizer generated now, available later, or disabled? If enabled, should it be browse-only or also allow localhost-only tag editing, persistent filtering, and recoverable removal?

Explain the practical effect in one sentence: the platform choice shapes installation and prompt examples; browser roundup consolidates existing saves into the Markdown source of truth; the optional visualizer adds searchable, filterable cards and can run as a localhost-only editing workspace without replacing the Markdown files.

## Round 1A: browser and folder sources

When roundup is enabled, read [browser-ingestion.md](browser-ingestion.md). Ask which browser profiles are in scope when more than one exists, and whether named Markdown or export folders should also be included. Locate standard bookmark files with read-only checks; do not inspect browser history, cookies, passwords, autofill, open tabs, or unrelated profile data.

If macOS or another operating system blocks direct browser-bookmark access, explain the exact limitation and offer the browser's native bookmark-export workflow. Treat the exported file as an input, never as the source of truth.

Show a compact inventory before importing: source, total entries, unique web URLs, duplicate groups, non-web entries, overlap with the destination, and inaccessible sources. Preserve browser/profile and legacy-folder provenance in imported notes. Never delete or rewrite browser bookmarks.

## Round 1B: personal context, asked immediately after Round 1

Ask whether the skill may use any existing context to improve its explicitly labelled `Why I may have saved it` inference. Offer concrete choices without implying that access is required:

1. the current conversation or session only;
2. approved project context such as `AGENTS.md`, `CLAUDE.md`, project notes, or other files they name;
3. approved global context or memory such as `MEMORY.md` or another file they identify;
4. no personal context.

Explain why this matters: the skill works without personal context, but this is where it becomes substantially more useful. Approved context lets it connect a saved page to recurring goals, preferences, projects, and decisions instead of producing a generic reason to revisit it.

Make the privacy boundary explicit:

- access is opt-in and limited to the scopes or paths the user approves;
- choosing no context must not block setup or bookmarking;
- store source labels and approved paths in configuration, not copied memory contents or conversation transcripts;
- never inspect browser history, credentials, private messages, or unrelated folders as a substitute;
- the user may change or disable context use later;
- personal-relevance text remains labelled as inference, not fact.

## Round 1C: previews and live media

When the visualizer is enabled, ask whether it should:

1. extract and locally cache Open Graph preview images for saved pages;
2. offer playable video for supported providers and direct video files;
3. offer online market charts when a bookmark represents an explicit ticker symbol.

Explain that locally cached preview images remain private and work offline. Remote video players and market charts contact third-party providers, can share the user's IP address and browser data, require internet access, and may be blocked by the publisher. Offer `ask before loading` as the privacy-first default, `always allow`, or `disable`.

Never promise universal playback. YouTube, Vimeo, supported Instagram posts, and direct video URLs can be embedded when the provider permits it. News sites and other publishers may block embedding; preserve their Open Graph image and source link as the fallback. Market data may be live or provider-delayed depending on the exchange and chart provider.

## Round 2: home and purpose

Ask:

1. Where should the new bookmark system live? Offer to use one of the source folders, an existing notes folder, or a new folder.
2. What do they mainly save links for? Ask for two or three real examples.
3. Which app will read the Markdown: Obsidian, another notes app, a code editor, plain files, or mainly the visualizer?

If the user does not know a path, help them choose one. Do not assume a home-directory or cloud-sync location.

## Round 3: propose the hierarchy

Infer 4–8 broad categories from the stated uses. Present them with one-line meanings and ask the user to approve, rename, add, or remove them.

Use these only as fallback seeds: `work`, `learning`, `tools`, `research`, `creative`, `life`, `shopping`, `reference`.

Prefer:

- broad, durable categories over short-lived projects;
- tags for specific technologies, people, themes, or formats;
- collections for hand-curated reading lists, projects, or decisions;
- stable bookmark file locations plus generated views for navigation.

Ask whether existing bookmarks or folders must be preserved or migrated.

## Round 4: capture behavior

Ask only choices not already implied:

1. **Capture depth:** quick (description + relevance), standard (key details + caveats), or deep (additional source verification).
2. **Personal relevance:** include an explicitly labelled inference about why the link may matter, include only when requested, or omit it.
3. **Privacy and URLs:** strip tracking parameters by default; ask whether safe original URLs should also be retained.

Confirm the timezone when capture dates could differ from the system timezone.

## Defaults when the user delegates the choices

- Stable flat storage in `bookmarks/`
- Generated category and tag views
- Manual `collections/`
- Record the current agentic platform without coupling the data to it
- Visualizer available later but not generated unless requested
- Local visualizer editing enabled when the user asks for the visualizer; direct HTML use remains read-only
- Cache Open Graph preview images when the visualizer is enabled
- Ask before loading remote video players or market charts
- Standard capture depth
- Explicit personal-relevance inference enabled
- Current-session context only until the user approves additional sources
- Offer read-only browser roundup during setup; default to `not now` if the user does not opt in
- `**Inference, not confirmed:**` label
- Strip common tracking parameters and do not retain sensitive originals
- Wikilinks for Obsidian; relative Markdown links otherwise

## Completion summary

Before writing, show a compact summary:

- root path;
- preferred agentic platform, browser-ingestion choice, and approved source bookmark paths;
- physical folders and generated navigation;
- visualizer choice;
- approved categories;
- capture depth and inference policy;
- approved personal-context mode and source labels;
- URL/privacy policy;
- migration scope.

Proceed after the user has answered the required location question and accepted or delegated the remaining choices.
