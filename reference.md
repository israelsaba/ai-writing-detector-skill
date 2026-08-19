# Reference: AI writing tells (evidence base)

This document holds the research trail that backs the `anti-ai-tells` skill. Load it when you need to argue for a specific rule, cite a source, or explain to the user why a particular phrase should be cut.

Last updated: April 2026.

---

## 1. The em-dash epidemic

The em-dash (`—`) is the most widely cited AI tell in 2024 to 2026.

**Evidence:**
- OpenAI community forum: repeated threads from late 2024 through 2026 where users complain that ChatGPT inserts em-dashes even when explicitly told not to. OpenAI eventually shipped a custom-instructions setting to reduce em-dash frequency, which itself confirms the pattern was real. See: techgig.com/openai-control-chatgpt-em-dash-overuse-setting (2025); opentools.ai/news/openai-fixes-em-dash-saga (2025).
- Reddit r/ChatGPT, comparative threads (late 2024): users benchmarking GPT vs Gemini vs LLaMA agree GPT family has the strongest em-dash bias.
- Documented false positives: human writers who naturally use em-dashes now get flagged as AI by auto-detectors, as noted in yornerdybestfriend.com/can-you-spot-ai-generated-content (March 2025).

**Rule:** zero em-dashes in any human-simulated copy. Alternatives by function:
- pause or emphasis: comma or period
- aposition or parenthetical: parentheses or commas
- explanation or expansion: colon
- two balanced clauses of equal weight: semicolon

## 2. Vocabulary tells in English

The Kobak et al. 2024 PubMed study, followed by replications in 2025, documented a statistically significant post-ChatGPT spike in the frequency of certain words in academic abstracts and web text. The core offender list:

delve, delve into, tapestry, navigate (especially "navigate the landscape" or "navigate the complexities"), foster, underscore, nuanced, pivotal, elevate, realm (especially "in the realm of"), bolster, grapple, myriad, testament ("stands as a testament to"), comprehensive, seamless, embark ("embark on a journey"), crucial, meticulous, robust.

Model-specific quirks logged in yornerdybestfriend.com (2025): ChatGPT favors "comprehensive"; DeepSeek over-uses "based", "yes", "step", "here", "creating", "title"; Gemini favors italics over bold.

**Sources:**
- arxiv.org/html/2604.14111v1 (stylometric analysis LLM vs human, 2025)
- techxplore.com/news/2025-12-reveals-ai-fully-human (December 2025)
- oliviacal.com/post/ai-writing-tells (editorial synthesis, 2025)

## 3. Vocabulary tells in Brazilian Portuguese

Mapped in hastewire.com/pt/blog/texto-gerado-por-ia-em-portugues (2025), plusai.com/br/blog/the-most-overused-chatgpt-words (2025), catai.com.br/o-prompt-que-faz-o-chatgpt-escrever-com-naturalidade (2024 to 2025) and editorial observation:

### Cliche openings (to cut)
- "no cenário atual"
- "em um mundo cada vez mais"
- "nos dias de hoje"
- "vivemos em uma época"
- "nessa era digital"
- "atualmente, a tecnologia..."
- "a inteligência artificial tem revolucionado"

### Mechanical connectors (soft-to-hard)
- "vale ressaltar", "vale destacar", "vale mencionar"
- "por isso", "dessa forma", "desse modo"
- "nesse contexto", "nesse sentido"
- "por fim", "em suma", "em conclusão"
- "é fundamental", "é importante mencionar", "é importante destacar"
- "não apenas X, mas também Y" (balanced antithesis, very strong tell)
- "não se trata apenas de X, mas de Y"

### AI-flavored adjectives
- robusto, multifacetado, inovador, transformador, promissor, desafiador, fascinante, exponencial, revolucionário, holístico

### Cliche closers
- "em conclusão", "em suma", "portanto", "dessa forma" (at paragraph start), "em última análise"

## 4. Structural tells

### Tricolon / rule of three
Three coordinated terms when one or two would do. Example: "fast, precise and effective"; "building, scaling and sustaining". One occurrence per text is fine. Three texts in a row with tricolons is AI signature.

### "Not X but Y" / "not just A but B"
Balanced rhetorical antithesis. Example: "not just security, but trust". Extremely high flag.

### Mirrored paragraphs
Same length, same cadence, same syntactic opener across multiple paragraphs. Human writing varies rhythm deliberately.

### Rhetorical question answered immediately
"Why does this matter? Because...". Very common in AI transitions.

### Parenthetical apposition framed by two em-dashes
"It was at that crossroads — risk, performance and accountability — that he worked." Double tell: em-dash plus triadic apposition.

## 5. Formatting tells

- Bullet lists in short responses where prose would be more natural
- Random bold in the middle of sentences
- Headers or subheaders inside short texts
- Triple-asterisk italics, emoji bullets

**Rule for human copy:** running prose in 2 to 4 paragraphs. No bullets, no bold, no headers. Emphasis through word choice and placement, not markup. If you must italicize, at most once per paragraph.

## 6. Burstiness

Human text has high burstiness (high variance of sentence length). LLM text trends toward uniform rhythm. Measured as the coefficient of variation (standard deviation divided by mean) of sentence word counts.

- Below 0.35: strong AI signal
- 0.40 to 0.55: human-like
- Above 0.55: creative writing territory

The `ai-tells-lint` CLI reports this score on every run.

## 7. Anti-example gallery

### Bad (English): TED-talk opener
> In today's fast-paced world, artificial intelligence is transforming every industry — and visionaries like X are navigating this unprecedented landscape, leveraging cutting-edge technology to foster innovation and elevate outcomes.

Why bad: "in today's fast-paced world", em-dash, "visionaries", "navigating", "unprecedented landscape", "leveraging cutting-edge", "foster", "elevate". Eight tells in one sentence.

### Good (English): factual rewrite
> X has shipped AI systems in regulated industries for eight years. Two of them now serve millions of transactions a day. Tonight she explains what broke, what held, and what she would build differently.

### Bad (pt-BR): release corporativo
> Com vasta experiência e sólida trajetória, Israel Saba é uma referência em inteligência artificial, apaixonado por transformar negócios com tecnologia de ponta.

Why bad: "vasta experiência", "sólida trajetória", "referência em", "apaixonado por", "transformar negócios", "tecnologia de ponta". Six tells in fifteen words.

### Good (pt-BR): direto
> Formado em Engenharia Mecatrônica na USP, Israel Saba trabalha há anos na interseção entre engenharia de software, arquitetura de sistemas e segurança aplicada à IA.

## 8. Detection tools (to test your output)

| Tool | Best for | Open source | Notes |
|---|---|---|---|
| GPTZero (gptzero.me) | general-purpose, pt-BR support | partial (github.com/burhanultayyab/gptzero) | perplexity plus burstiness |
| Binoculars | research-grade, high precision | yes (github.com/ahans30/Binoculars) | arxiv.org/abs/2401.12070; >90% detection at 0.01% false-positive |
| Originality.ai | paid, publishing use-case | no | integrates plagiarism detection |
| Copyleaks | paid, education | no | claims 99% accuracy |
| Pangram | paid, phrase highlighting | no | shows which exact phrases triggered |
| Evernote AI Detector | free, pt-BR | no | consumer tool |

All detectors have false positives on proficient human writers, especially non-native English speakers. Use detectors as one signal, not as final verdict.

## 9. Anti-tell pipeline integration

### Vale linter (recommended for repo-level enforcement)
Vale (vale.sh, github.com/errata-ai/vale) supports custom styles. Create `~/.config/vale/styles/AntiAITells/` with individual `.yml` rule files, one per tell category. Add `AntiAITells = YES` to `.vale.ini`. Runs in CI as `vale <file>` and fails on violations.

### LanguageTool with custom rules
Self-hosted LanguageTool supports custom XML rules. Slower than Vale but better for grammar-sensitive languages like Portuguese.

### The `ai-tells-lint` CLI (shipped with this skill)
The bundled `bin/ai-tells-lint` wrapper reports HARD and SOFT violations plus burstiness score. See the skill's main `SKILL.md` for usage.

### Prompt-level negative constraints (for agents that generate)
Documented in catai.com.br and aijourn.com: explicit "never use these words" lists in the system prompt outperform generic "write naturally" instructions. Include:
1. Full forbidden-word list (do not summarize).
2. Explicit ban on the em-dash character.
3. Burstiness rule with concrete numbers.
4. Self-review step before delivery.
5. Bad-example plus good-example pairs.

Temperature adjustments do not fix tells. They change surface but preserve underlying patterns. Structural negative constraints do the work.

## 10. Key sources (URLs)

- techgig.com/openai-control-chatgpt-em-dash-overuse-setting (2025)
- opentools.ai/news/openai-fixes-em-dash-saga (2025)
- arxiv.org/abs/2401.12070 (Binoculars detector)
- arxiv.org/html/2604.14111v1 (LLM vs human stylometry)
- techxplore.com/news/2025-12-reveals-ai-fully-human (December 2025)
- oliviacal.com/post/ai-writing-tells (editorial synthesis)
- hastewire.com/pt/blog/texto-gerado-por-ia-em-portugues (pt-BR tells)
- plusai.com/br/blog/the-most-overused-chatgpt-words (pt-BR overused words)
- catai.com.br/o-prompt-que-faz-o-chatgpt-escrever-com-naturalidade (pt-BR prompting)
- vale.sh (Vale linter)
- community.openai.com/t/excessive-used-of-bold-formatting/1110099 (formatting complaints)
