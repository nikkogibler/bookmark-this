# Contributing

Bookmark This should remain portable, easy to install, and safe around existing bookmark libraries.

## Useful Contributions

- Reproducible installation fixes for a supported agentic platform
- Improvements to duplicate detection, URL safety, or validation
- Better setup questions that reduce effort without hiding consequential choices
- Visualizer accessibility, search, navigation, and performance improvements
- Additional examples that clarify an existing capability

## Before Opening A Change

- Keep the scope narrow.
- Preserve the user-owned Markdown data model.
- Do not add accounts, hosted services, analytics, or databases as defaults.
- Do not introduce platform-specific assumptions into the bookmark files.
- Keep scripts dependency-free unless a dependency has a clear operational benefit.
- Preserve uncertainty and the explicit inference label.
- Test setup, rebuild, visualization, and validation when your change affects them.

## Pull Requests

Explain:

- what changed
- why the change is useful
- which platforms or workflows it affects
- how you tested it
- any migration or compatibility implications

Do not include private bookmark libraries, credentials, browser exports, or personal paths in fixtures or screenshots.
