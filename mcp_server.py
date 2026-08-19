#!/usr/bin/env python3
"""MCP server for the `anti-ai-tells` OpenCode skill.

Exposes three tools to an MCP client (like OpenCode) so the agent can
detect AI-generated fingerprints in text without shelling out.

Tools:
    lint_text(text, strict=False)  -> structured report
    lint_file(path, strict=False)  -> structured report
    describe_rules()               -> human-readable rule catalog

The detection engine is imported from the sibling `bin/ai-tells-lint.py`,
which is the authoritative implementation used by the CLI too.

Uses FastMCP (from the `mcp` Python SDK) over stdio, matching the transport
OpenCode expects for local MCP servers.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


SKILL_DIR = Path(__file__).resolve().parent


def _load_linter_module():
    """Dynamically load the linter module from bin/ai-tells-lint.py.

    The file has a non-identifier name, so regular import doesn't work.
    We use importlib.util to load it from its path.
    """
    linter_path = SKILL_DIR / 'bin' / 'ai-tells-lint.py'
    if not linter_path.exists():
        raise FileNotFoundError(f'linter not found at {linter_path}')
    spec = importlib.util.spec_from_file_location('ai_tells_linter', str(linter_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f'failed to build spec for {linter_path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


linter = _load_linter_module()


mcp = FastMCP(
    name='anti-ai-tells',
    instructions=(
        "Detects AI-generated fingerprints in text (em-dashes, cliche openers, "
        "mechanical connectors, LinkedIn-motivational vocabulary, balanced "
        "antithesis patterns, triadic phrasing, low burstiness). Supports "
        "Brazilian Portuguese and English. Call `lint_text` with inline text "
        "or `lint_file` with a path. Use `describe_rules` to read the rule "
        "catalog before writing copy. Read the sibling skill's SKILL.md and "
        "reference.md for the full evidence base."
    ),
)


def _summarize(result: dict[str, Any]) -> dict[str, Any]:
    """Add a one-line verdict and a human-readable summary to the raw result."""
    hard = len(result.get('hits_hard', []))
    soft = len(result.get('hits_soft', []))
    burst = result.get('burstiness', 0.0)
    if hard == 0 and burst >= 0.40:
        verdict = 'ships_clean'
    elif hard < 5 and burst >= 0.30:
        verdict = 'needs_cleanup_pass'
    else:
        verdict = 'rewrite_recommended'
    summary = (
        f'{result.get("word_count", 0)} words, '
        f'{result.get("sentence_count", 0)} sentences, '
        f'burstiness={burst:.2f} (target >= 0.40). '
        f'{hard} HARD, {soft} SOFT violations. verdict={verdict}'
    )
    return {**result, 'verdict': verdict, 'summary': summary}


@mcp.tool()
def lint_text(text: str, strict: bool = False) -> dict[str, Any]:
    """Lint a text snippet for AI-generated fingerprints.

    Args:
        text: The text to analyze. Supports English and Brazilian Portuguese.
        strict: If True, raise when any HARD violation is found (for pipelines).

    Returns:
        A structured report with keys:
          - hits_hard: list of must-fix violations (em-dash, cliche phrases)
          - hits_soft: list of warnings (suspicious punctuation, soft cliches)
          - word_count, sentence_count, sentence_lengths
          - burstiness (coefficient of variation of sentence lengths)
          - verdict: 'ships_clean' | 'needs_cleanup_pass' | 'rewrite_recommended'
          - summary: one-line human-readable verdict
    """
    if not isinstance(text, str):
        raise ValueError('text must be a string')
    result = linter.check(text)
    enriched = _summarize(result)
    if strict and enriched['hits_hard']:
        raise ValueError(
            f'strict=True and {len(enriched["hits_hard"])} HARD violations found'
        )
    return enriched


@mcp.tool()
def lint_file(path: str, strict: bool = False) -> dict[str, Any]:
    """Lint a file on disk for AI-generated fingerprints.

    Args:
        path: Absolute or home-relative path to the file to analyze.
        strict: If True, raise when any HARD violation is found (for pipelines).

    Returns:
        A structured report (see `lint_text` for the schema), plus a `file` field
        with the resolved path.
    """
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f'file not found: {p}')
    if not p.is_file():
        raise ValueError(f'not a file: {p}')
    text = p.read_text(encoding='utf-8')
    result = linter.check(text)
    enriched = _summarize(result)
    enriched['file'] = str(p)
    if strict and enriched['hits_hard']:
        raise ValueError(
            f'strict=True and {len(enriched["hits_hard"])} HARD violations in {p}'
        )
    return enriched


@mcp.tool()
def describe_rules() -> dict[str, Any]:
    """Return the rule catalog used by the linter.

    Useful for the agent to learn WHAT the linter checks for without loading
    the full skill. Returns a dict with rule counts per category and a pointer
    to the skill's reference.md for the full evidence base.
    """
    hard: dict[str, int] = {}
    soft: dict[str, int] = {}
    for _pat, category, severity, _lang in linter.PATTERNS:
        bucket = hard if severity == 'hard' else soft
        bucket[category] = bucket.get(category, 0) + 1
    return {
        'hard_categories': hard,
        'soft_categories': soft,
        'total_hard_rules': sum(hard.values()),
        'total_soft_rules': sum(soft.values()),
        'skill_path': str(SKILL_DIR),
        'reference_path': str(SKILL_DIR / 'reference.md'),
        'skill_md_path': str(SKILL_DIR / 'SKILL.md'),
        'burstiness_target': {
            'good': '>= 0.40',
            'acceptable': '0.35 - 0.40',
            'danger_llm_signal': '< 0.35',
        },
        'supported_languages': ['pt-BR', 'en'],
        'notes': (
            'Load the full skill via the `skill` tool with name="anti-ai-tells" '
            'to get SKILL.md (rules and usage) and reference.md (evidence and '
            'citations) before writing copy that must read as human.'
        ),
    }


def main() -> None:
    # FastMCP.run() picks up stdio by default when executed as a subprocess,
    # which is exactly what OpenCode's local MCP wiring uses.
    mcp.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
