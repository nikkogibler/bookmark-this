# Platform adaptation

The bookmark data must remain portable Markdown. The selected agentic platform affects only skill installation, available tools, setup wording, and example prompts.

## Rules

1. Record the user's platform choice in `agentic_platform`.
2. Detect whether the skill is already running natively. If it is, do not create a second installation.
3. Before installing or copying the skill, inspect the platform's current local instructions or discoverable global skill directory. Do not rely on a remembered path when a live check is cheap.
4. Explain the proposed destination and request permission before writing outside the user's stated workspace or configuration area.
5. Preserve the same `.bookmark-system/config.json`, Markdown schema, and hierarchy across platforms.
6. Tailor the closing examples to the platform's normal invocation style. Always include plain-language prompts that work without special syntax:
   - `Set up my bookmark system.`
   - `Bookmark this: <URL>`
   - `Show me my bookmarks about <topic>.`
7. If a platform cannot run the maintenance script, continue with Markdown-only capture and say which rebuild, validation, or visualizer capability is unavailable. Do not claim those steps ran.

## Platform choice is not lock-in

Never rewrite the library into a platform-specific database by default. A user should be able to switch agents while retaining the bookmark files, configuration, generated views, and optional static visualizer.
