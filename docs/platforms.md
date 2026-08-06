# Platform Installation

Bookmark This keeps its data portable. Platform-specific installation changes where the skill folder lives and how you invoke it, not the bookmark schema.

## Codex

Personal installation:

```bash
cp -R skills/bookmark-this ~/.codex/skills/
```

Start a new task after installation and use:

```text
Use $bookmark-this to set up my bookmark system.
```

Reference: [OpenAI — Build skills](https://developers.openai.com/codex/skills/)

## Claude Code

Personal installation for all projects:

```bash
cp -R skills/bookmark-this ~/.claude/skills/
```

Project-only installation:

```bash
cp -R skills/bookmark-this <project>/.claude/skills/
```

Invoke `/bookmark-this` or describe the task naturally.

Reference: [Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills)

## Hermes

Install directly from the GitHub repository path:

```bash
hermes skills install nikkogibler/bookmark-this/skills/bookmark-this
```

Hermes stores installed skills under `~/.hermes/skills/` and supports referenced files under `references/`, `scripts/`, and other standard skill directories.

Reference: [Nous Research — Hermes skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)

## OpenClaw

Install a local clone into the active workspace:

```bash
openclaw skills install ./skills/bookmark-this
```

Install for all local agents:

```bash
openclaw skills install ./skills/bookmark-this --global
```

OpenClaw installs workspace skills under the active `skills/` directory and global skills under `~/.openclaw/skills/` by default.

Reference: [OpenClaw — Skills](https://docs.openclaw.ai/tools/skills)

## Other Agents

Keep the entire `skills/bookmark-this/` folder together. Point the agent or prompt system at `SKILL.md`, allow it to read the adjacent `references/`, and make Python 3 available if you want generated navigation, validation, and the optional visualizer.

The bookmark library itself does not depend on any one platform.
