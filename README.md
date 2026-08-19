---
type: knowledge_bundle_index
title: AI Writing Detector and Human-Sounding Copy Skill
description: An Agent Skill for reviewing AI writing signals and revising English or Brazilian Portuguese copy to sound specific, natural, and human-edited.
tags:
  [
    agent-skills,
    ai-writing-detector,
    ai-content-detector,
    humanize-ai-text,
    copy-editing,
    writing-quality,
  ]
timestamp: 2026-08-19T00:00:00-03:00
---

# AI Writing Detector and Human-Sounding Copy Skill

```
 (`-')  _   _                     _             (`-')      (`-')  _   (`-')
 (OO ).-/  (_)           <-.     (_)      <-.   ( OO).->   ( OO).-/<-.(OO )
 / ,---.   ,-(`-')    (`-')-----.,-(`-'),--. )  /    '._  (,------.,------,)
 | \ /`.\  | ( OO)    (OO|(_\---'| ( OO)|  (`-')|'--...__) |  .---'|   /`. '
 '-'|_.' | |  |  )     / |  '--. |  |  )|  |OO )`--.  .--'(|  '--. |  |_.' |
(|  .-.  |(|  |_/      \_)  .--'(|  |_/(|  '__ |   |  |    |  .--' |  .   .'
 |  | |  | |  |'->      `|  |_)  |  |'->|     |'   |  |    |  `---.|  |\  \
 `--' `--' `--'          `--'    `--'   `-----'    `--'    `------'`--' '--'
```

This repository publishes the `anti-ai-tells` Agent Skill. It reviews AI writing signals such as formulaic phrasing, suspicious punctuation, repeated structures, and low sentence-length variation, then proposes concrete edits for English and Brazilian Portuguese.

The name targets the common search intent "AI writing detector" while the scope stays honest: stylistic signals are not proof of authorship, and no detector can reliably establish whether a person or model wrote text from style alone.

## Install The Skill

Copy the full repository directory into the agent's skill directory. Keep `SKILL.md`, `reference.md`, the CLI, and the MCP files together:

```bash
git clone --depth 1 https://github.com/israelsaba/ai-writing-detector-skill.git
mkdir -p ~/.config/opencode/skills/anti-ai-tells
cp -R ai-writing-detector-skill/. ~/.config/opencode/skills/anti-ai-tells/
```

The directory can also be copied to `~/.hermes/skills/anti-ai-tells/`, `~/.claude/skills/anti-ai-tells/`, or `~/.codex/skills/anti-ai-tells/`. Start a new agent session after installation.

## Safe Permissions

The core review runs locally and needs read access only to the draft the user names. It does not need network, browser, credential, or elevated permissions. Allow writes only when the user asks for a saved rewrite. The optional MCP server needs permission to read its own skill files and run the configured Python process, not unrestricted shell or filesystem access. Do not send drafts to external detectors without explicit approval.

## Use It

Ask the agent to use `anti-ai-tells` when drafting, reviewing, or revising public-facing copy. For a local CLI check:

```bash
"$SKILL_DIR/bin/ai-tells-lint" README.md
"$SKILL_DIR/bin/ai-tells-lint" --format json --strict README.md
```

The OpenCode MCP server is optional. If enabled, configure its command with the installed `start-mcp.sh` path and install the Python `mcp` package in an isolated environment. Restart OpenCode after changing its MCP configuration.

## What It Checks

- AI writing signals in English and Brazilian Portuguese.
- Em-dashes, suspicious quotation patterns, cliches, and mechanical connectors.
- Triadic phrasing, antithesis, repeated sentence openings, and low burstiness.
- Concrete rewrites that preserve meaning instead of claiming detector evasion.

Do not use this skill to misrepresent authorship, evade academic integrity systems, conceal fraud, or make unsupported claims about detector scores. Use it for editorial quality, transparency, and human review.

## Contributing

Contributions are welcome through pull requests. Preserve the `SKILL.md` entry point and evidence references, explain the writing-quality benefit, add or update tests and examples when rules change, and describe the checks performed. Discuss larger rule changes in an issue before opening a PR.

Use issues for reproducible false positives or false negatives, unclear guidance, language coverage, installation problems, and focused proposals. Include the skill version or commit, language, a minimal redacted example, expected behavior, actual behavior, and the rule involved. Do not post private drafts, confidential text, or security concerns publicly; follow [SECURITY.md](SECURITY.md).

## Releases

Stable releases use `vMAJOR.MINOR.PATCH` tags and GitHub release notes. Install a reviewed release or commit when reproducibility matters.

## Sources

| Source                                                            | Claim supported                                             |
| ----------------------------------------------------------------- | ----------------------------------------------------------- |
| [`SKILL.md`](SKILL.md)                                            | Operational rules, trigger conditions, and limitations      |
| [`reference.md`](reference.md)                                    | Evidence trail and rule rationale maintained with the skill |
| [OpenCode skills documentation](https://opencode.ai/docs/skills/) | Agent skill discovery and `SKILL.md` conventions            |

## License

MIT. See [LICENSE](LICENSE).
