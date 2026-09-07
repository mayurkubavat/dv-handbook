# Research index

One file per topic. Each note: header (title, date, author, status), findings with inline citations, key sources, confidence notes.
Link every note from `STATUS.md` → "Research references" with what it feeds.

| File | Topic | Status | Feeds |
|---|---|---|---|
| `genai-agentic-flows.md` | Generative AI & agentic flows (general) | done (2026-09-05, ~3.6k words) | Ch. 34, design §6 |
| `sw-engineering-ai-era.md` | Modern SW engineering practices, AI era | done (2026-09-05, ~3.1k words) | Ch. 27–29, 32, 34 |
| `ai-in-dv-state-of-the-art.md` | AI/ML/LLM/agents applied to DV & EDA | done (2026-09-06, ~3.4k words) | Ch. 33–35 |
| `dv-adaptation-synthesis.md` | Synthesis: adapting SW/GenAI practice to DV | done (2026-09-06, ~4.3k words) | Ch. 34, book workflow |
| `ch01-cost-gap-lifecycle.md` | Survey figures, cost of bugs, escapes, definitions, lifecycle, sign-off | done (2026-09-06, ~3k words) | Ch. 1 |
| `ch02-verification-planning.md` | Plan definitions, feature extraction, traceability, coverage model, OpenTitan plan format + sign-off stages, failure modes, AI-generated plans | done (2026-09-06, ~4.5k words) | Ch. 2 |
| `ch34-concept-sources.md` | Primary sources for generative-AI concepts, SW-practice parallels, governance | done (2026-09-06, 43 bib entries) | Ch. 34 |
| `tooling-landscape-software.md` | Catalogue of tools/protocols AI coding agents use in SW engineering (LSP, tree-sitter, SARIF, test/coverage/mutation/fuzz, build/CI/sandbox, DAP/rr/OTel, formal, MCP/A2A/AGENTS.md, docs/requirements, eval gates) + 14 HW gaps | draft (2026-09-07, ~10.7k words, 244 URLs verified) | tooling catalogue, Ch. 34 follow-up |

## Conventions
- Cite as `[Source, YYYY-MM-DD](URL)`; separate vendor claims from peer-reviewed results.
- Mark unverified claims in a "Confidence notes" section.
- When a note is used in a chapter, add the chapter number to "Feeds" and cite in `refs.bib`.
| `tooling-landscape-hardware.md` | Open (and labelled vendor) RTL/DV/debug tools an agent could call: parsers, sims, coverage, waveforms, formal, MCP servers, spec tooling, CI; gaps | done (2026-09-07, ~120 rows) | tooling catalogue, Ch. 34 follow-up |
