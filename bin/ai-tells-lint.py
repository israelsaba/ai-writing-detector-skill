#!/usr/bin/env python3
"""ai-tells-lint: detects AI-generated fingerprints in a text file.

Part of the `anti-ai-tells` OpenCode skill. Run through the bundled shell
wrapper in `bin/ai-tells-lint`.

Checks for:
  - em-dash (—) usage — hard fail
  - forbidden pt-BR and English phrases (opener cliches, mechanical
    connectors, LinkedIn-motivational vocabulary, AI-flavored adjectives)
  - suspicious unicode quotation marks mixed with straight quotes
  - low burstiness (sentence-length variance too uniform)

Usage:
    ai-tells-lint <file> [--strict] [--format text|json]

Exit codes:
    0 = clean (or non-strict mode)
    1 = HARD violations found with --strict

See the bundled `reference.md` for the evidence trail.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


# Each pattern: (regex, category, severity, language)
# severity: 'hard' = must not appear in human-facing copy; 'soft' = use with care
PATTERNS: list[tuple[str, str, str, str]] = [
    # punctuation
    (r'—', 'em-dash (travessão)', 'hard', 'any'),
    (r'[\u201c\u201d\u2018\u2019\u201a\u201e]', 'unicode quote (suspicious)', 'soft', 'any'),

    # pt-BR cliche openers
    (r'\bno cenário atual\b', 'cliche opener (pt-BR)', 'hard', 'pt'),
    (r'\bem um mundo cada vez mais\b', 'cliche opener (pt-BR)', 'hard', 'pt'),
    (r'\bnos dias de hoje\b', 'cliche opener (pt-BR)', 'hard', 'pt'),
    (r'\bvivemos em uma época\b', 'cliche opener (pt-BR)', 'hard', 'pt'),
    (r'\bnessa era digital\b', 'cliche opener (pt-BR)', 'hard', 'pt'),

    # pt-BR mechanical connectors
    (r'\bvale ressaltar\b', 'mechanical connector (pt-BR)', 'hard', 'pt'),
    (r'\bvale destacar\b', 'mechanical connector (pt-BR)', 'hard', 'pt'),
    (r'\bvale mencionar\b', 'mechanical connector (pt-BR)', 'hard', 'pt'),
    (r'\bdessa forma\b', 'mechanical connector (pt-BR)', 'soft', 'pt'),
    (r'\bdesse modo\b', 'mechanical connector (pt-BR)', 'soft', 'pt'),
    (r'\bnesse contexto\b', 'mechanical connector (pt-BR)', 'hard', 'pt'),
    (r'\bnesse sentido\b', 'mechanical connector (pt-BR)', 'hard', 'pt'),
    (r'\bé fundamental\b', 'empty intensifier (pt-BR)', 'soft', 'pt'),
    (r'\bé importante mencionar\b', 'empty intensifier (pt-BR)', 'hard', 'pt'),
    (r'\bé importante destacar\b', 'empty intensifier (pt-BR)', 'hard', 'pt'),

    # pt-BR antithesis
    (r'\bnão apenas .{1,60}? mas também\b', 'balanced antithesis (pt-BR)', 'hard', 'pt'),
    (r'\bnão se trata apenas de .{1,60}? mas\b', 'balanced antithesis (pt-BR)', 'hard', 'pt'),

    # pt-BR cliche closers
    (r'\bem conclusão\b', 'cliche closer (pt-BR)', 'hard', 'pt'),
    (r'\bem suma\b', 'cliche closer (pt-BR)', 'hard', 'pt'),
    (r'\bem última análise\b', 'cliche closer (pt-BR)', 'hard', 'pt'),

    # pt-BR AI-flavored adjectives
    (r'\brobusto\b', 'AI-flavored adjective (pt-BR)', 'soft', 'pt'),
    (r'\bmultifacetad[ao]\b', 'AI-flavored adjective (pt-BR)', 'hard', 'pt'),
    (r'\binovador\b', 'AI-flavored adjective (pt-BR)', 'soft', 'pt'),
    (r'\btransformador\b', 'AI-flavored adjective (pt-BR)', 'soft', 'pt'),
    (r'\bholístic[ao]\b', 'AI-flavored adjective (pt-BR)', 'hard', 'pt'),
    (r'\bexponencial\b', 'AI-flavored adjective (pt-BR)', 'soft', 'pt'),

    # pt-BR LinkedIn-motivational vocab
    (r'\bvisionári[ao]\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bdisrupt(or|ivo|iva|ivos|ivas|ores|oras)?\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bmente brilhante\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bapaixonad[ao] por\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\breferência no mercado\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bmindset\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bgamechanger\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bgame[- ]changer\b', 'LinkedIn-motivational (pt-BR)', 'hard', 'pt'),
    (r'\bvasta experiência\b', 'empty sentence (pt-BR)', 'hard', 'pt'),
    (r'\bsólida trajetória\b', 'empty sentence (pt-BR)', 'hard', 'pt'),
    (r'\bampla experiência\b', 'empty sentence (pt-BR)', 'hard', 'pt'),

    # English ChatGPT buzzword bingo
    (r'\bdelve\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\btapestry\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bnavigate the (landscape|complexities|nuances)\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bin the realm of\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bstands as a testament\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bembark on (a |an )?journey\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bin today\'?s fast-paced world\b', 'AI cliche opener (EN)', 'hard', 'en'),
    (r'\bever-evolving\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bcutting-edge\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bgame-changing\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bseamless(ly)?\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bfoster\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bunderscore\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bnuanced\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bpivotal\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\belevate\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bbolster\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bmyriad\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bmeticulous(ly)?\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bmultifaceted\b', 'AI buzzword (EN)', 'hard', 'en'),
    (r'\bholistic\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bleverag(e|es|ing)\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bresonate(s|d)?\b', 'AI buzzword (EN)', 'soft', 'en'),
    (r'\bprovenance\b', 'AI buzzword (EN)', 'hard', 'en'),
]


def count_words(text: str) -> int:
    return len(re.findall(r'\w+', text))


def sentence_lengths(text: str) -> list[int]:
    """Words per sentence; a proxy for burstiness."""
    sentences = re.split(r'[.!?]+\s+', text.strip())
    return [count_words(s) for s in sentences if count_words(s) > 0]


def burstiness(lengths: list[int]) -> float:
    """Coefficient of variation (std/mean) of sentence lengths.
    Human writing typically > 0.40; below 0.35 signals LLM."""
    if not lengths:
        return 0.0
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0
    var = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    return (var ** 0.5) / mean


def check(text: str) -> dict:
    hits_hard: list[dict] = []
    hits_soft: list[dict] = []
    for pat, cat, sev, lang in PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hit = {
                'category': cat,
                'match': m.group(0),
                'language': lang,
                'pattern': pat,
                'position': m.start(),
            }
            (hits_hard if sev == 'hard' else hits_soft).append(hit)
    lengths = sentence_lengths(text)
    return {
        'hits_hard': hits_hard,
        'hits_soft': hits_soft,
        'word_count': count_words(text),
        'sentence_count': len(lengths),
        'sentence_lengths': lengths,
        'burstiness': round(burstiness(lengths), 3),
    }


def print_text_report(result: dict, filename: str) -> None:
    print(f'== ai-tells-lint — {filename} ==')
    print(f'Words: {result["word_count"]}')
    print(f'Sentences: {result["sentence_count"]}')
    print(f'Sentence lengths: {result["sentence_lengths"]}')
    print(f'Burstiness (CV): {result["burstiness"]} (target > 0.40, danger < 0.35)')
    print()
    if result['hits_hard']:
        print(f'HARD violations ({len(result["hits_hard"])}):')
        for h in result['hits_hard']:
            print(f'  [{h["category"]}] "{h["match"]}"')
    else:
        print('No HARD violations.')
    if result['hits_soft']:
        print()
        print(f'SOFT warnings ({len(result["hits_soft"])}):')
        for h in result['hits_soft']:
            print(f'  [{h["category"]}] "{h["match"]}"')
    else:
        if not result['hits_hard']:
            print('No SOFT warnings.')


def main() -> None:
    ap = argparse.ArgumentParser(
        description='Detect AI-generated fingerprints in a text file.',
        epilog='See the skill directory for the full guidance.',
    )
    ap.add_argument('file', type=Path, help='Path to the file to lint')
    ap.add_argument('--strict', action='store_true',
                    help='Exit 1 if any HARD violation is found')
    ap.add_argument('--format', choices=['text', 'json'], default='text',
                    help='Output format (default text)')
    args = ap.parse_args()

    if not args.file.exists():
        print(f'File not found: {args.file}', file=sys.stderr)
        sys.exit(2)

    text = args.file.read_text(encoding='utf-8')
    result = check(text)

    if args.format == 'json':
        print(json.dumps({'file': str(args.file), **result}, ensure_ascii=False, indent=2))
    else:
        print_text_report(result, args.file.name)

    if args.strict and result['hits_hard']:
        sys.exit(1)


if __name__ == '__main__':
    main()
