# Setup interview

The goal is to learn enough to create a useful first hierarchy without turning setup into a questionnaire. Ask in rounds and adapt to answers.

## Round 1: start here

Ask:

1. Which agentic platform should this work with: Codex, Claude, Hermes, OpenClaw, another platform, or no preference?
2. Do they know where their bookmarks live now? Ask them to point to one or more folders, paste paths, or say `I don't know` so the agent can help locate likely folders with read-only searches.
3. Do they want a simple local bookmark visualizer generated now, available later, or disabled?

Explain the practical effect in one sentence: the platform choice shapes installation and prompt examples; source folders shape preservation or migration; the optional visualizer adds searchable cards and category/tag filters without replacing the Markdown files.

If the user does not know their bookmark locations, search only likely user-approved note or project roots. Show candidate folders and ask which ones are in scope before migration. Do not scan an entire home directory or browser profile by default.

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
- Standard capture depth
- Explicit personal-relevance inference enabled
- `**Inference, not confirmed:**` label
- Strip common tracking parameters and do not retain sensitive originals
- Wikilinks for Obsidian; relative Markdown links otherwise

## Completion summary

Before writing, show a compact summary:

- root path;
- preferred agentic platform and source bookmark folders;
- physical folders and generated navigation;
- visualizer choice;
- approved categories;
- capture depth and inference policy;
- URL/privacy policy;
- migration scope.

Proceed after the user has answered the required location question and accepted or delegated the remaining choices.
