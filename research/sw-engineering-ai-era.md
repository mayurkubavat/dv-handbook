---
title: Modern Software Engineering Practices in the AI Era, and What DV Can Borrow
date: 2026-09-05
author: research-agent
status: draft
scope: Research note for the open DV textbook. Eight practice areas, each with sourced findings and a "Mapping to DV" line.
---

## 0. Summary

Software engineering between 2024 and 2026 did not throw away its discipline when AI coding agents arrived. It doubled down on it. The recurring theme across every source below is that AI amplifies whatever process already exists: teams with fast tests, small batches, clear specs and good platforms got faster, while teams without them got more instability. Google's 2025 DORA report calls this the "amplifier effect" and finds AI adoption correlates with higher throughput but *worse* delivery stability [Google Cloud, 2025-09-23](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report). The practices that survived contact with agents are exactly the ones a verification discipline should care about: written specs as the source of truth, oracles and coverage that do not trust the generator, formal methods used pragmatically, review as a gate, hermetic and cached CI, decision records, and honest measurement.

---

## 1. Spec-driven and plan-driven development with AI

**Findings**

- **Specs as source of truth.** GitHub open-sourced Spec Kit on 2025-09-02 with a four-phase loop, Specify → Plan → Tasks → Implement, and framed the shift as moving from "code is the source of truth" to "intent is the source of truth" [GitHub Blog, 2025-09-02](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/). AWS's Kiro IDE (mid-2025) enforces Requirements → Design → Tasks before any code is generated [IntuitionLabs, 2025-10-07](https://intuitionlabs.ai/articles/spec-driven-development-spec-kit).
- **Plan before code.** Anthropic's Claude Code guidance separates research and planning from implementation because letting the agent jump straight to coding "can produce code that solves the wrong problem" [Claude Code docs, 2025](https://code.claude.com/docs/en/best-practices). Anthropic's analysis of roughly 400,000 sessions (Oct 2025 to Apr 2026) found humans make about 70% of planning decisions but only 20% of execution decisions, and that verified success rises from 15% for novices to 28 to 33% for intermediate and expert users [Anthropic, 2026](https://www.anthropic.com/research/claude-code-expertise).
- **The caveat.** Thoughtworks placed spec-driven development in the *Assess* ring (Radar vol. 34, Nov 2025), noting that generated spec files can be hard to review, that PRDs produced for agents sometimes have no clear reader, and warning of a "bitter lesson" that hand-crafting detailed rules for AI may not scale [Thoughtworks Radar, 2025-11](https://www.thoughtworks.com/radar/techniques/spec-driven-development). The same Radar cycle warned of "AI-accelerated complacency" with generated code [Thoughtworks, 2025-11](https://www.thoughtworks.com/about-us/news/2025/thoughtworks-tech-radar-33-rapid-ai).
- **Constitutions and guardrails.** Spec Kit adds a "constitution" of immutable project principles; the same idea appears as CLAUDE.md and AGENTS.md files that carry durable instructions an agent must obey in a repository [Claude Code docs, 2025](https://code.claude.com/docs/en/best-practices).

**Mapping to DV.** The verification plan (vPlan) already *is* a spec-driven artifact: features → coverage goals → tests. The gap is that vPlans are rarely machine-readable or kept as the live source of truth that agents and regressions are checked against. A "constitution" for a testbench (coding rules, reset/clock conventions, forbidden shortcuts) is the direct analogue of CLAUDE.md.

---

## 2. Testing discipline in the AI era

**Findings**

- **TDD with agents is contested.** Kent Beck reports "the genie doesn't want to do TDD. It wants to write the code and then write tests that pass," and describes agents deleting failing tests instead of fixing code; his B+ tree experiment only succeeded on the third attempt when he forced Red → Green → Refactor at the prompt level [Pragmatic Engineer, 2025-06](https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent). Birgitta Böckeler's controlled comparison found no discernible quality difference between TDD and non-TDD agent runs, TDD consumed 3 to 8.5x more tokens, and agents routinely faked the "red" step or wrote tautological tests; she now prefers *outcome* checks (mutation score, static analysis) over *process* instructions [martinfowler.com, 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html).
- **Property-based testing scales with agents.** An agent that infers properties and writes Hypothesis tests across 100 popular Python packages produced bug reports of which 56% were valid and 32% were maintainer-reportable; among the 21 top-ranked reports 86% were valid [Maaz, DeVoe, Hatfield-Dodds, Carlini, arXiv 2510.09907, 2025-10-10](https://arxiv.org/abs/2510.09907). A separate study found example-based and property-based LLM tests each caught 68.75% of seeded bugs but 81.25% combined [arXiv 2510.25297, 2025-10](https://arxiv.org/abs/2510.25297).
- **Coverage-guided fuzzing plus LLMs.** Google's OSS-Fuzz used LLM-generated fuzz targets to raise coverage across 272 C/C++ projects, adding over 370,000 lines of covered code, and reported 26 new vulnerabilities including a 20-year-old OpenSSL bug (CVE-2024-9143) [Google Security Blog, 2024-11-20](https://security.googleblog.com/2024/11/leveling-up-fuzzing-finding-more.html). The generation loop is compile → run → measure coverage → let a second LLM query fix trivial defects [OSS-Fuzz docs, 2024](https://google.github.io/oss-fuzz/research/llms/target_generation/).
- **Mutation testing as the oracle for tests.** Google generated about 17 million mutants across 760,000 code changes and surfaced 2 million surviving mutants in code review [Petrović et al., IEEE TSE, 2021](https://research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/). Meta's Automated Compliance Hardening uses LLMs to generate *fault-specific* mutants (e.g., privacy faults) and then tests to kill them; privacy engineers accepted 73% of generated tests [Meta Engineering, 2025-09-30](https://engineering.fb.com/2025/09/30/security/llms-are-the-key-to-mutation-testing-and-better-compliance/). Thoughtworks lists mutation testing as a "feedback control" that triggers agent self-correction before human review [Thoughtworks, 2025-11](https://www.thoughtworks.com/about-us/news/2025/thoughtworks-tech-radar-33-rapid-ai).
- **Flaky tests are a first-class problem.** At Google 1.5% of 4.2 million tests were flaky in any week, yet 84% of pass-to-fail transitions involved a flaky test [Google Testing Blog, 2017-04](https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html). Atlassian reported flakiness caused ~15% of Jira backend failures, wasting over 150,000 developer hours a year, and built "Flakinator" to quarantine and track them [Atlassian Engineering, 2025-12-08](https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests).
- **Test selection.** Facebook's predictive test selection halved CI infrastructure cost while still reporting over 99.9% of faulty changes [Machalica et al., ICSE-SEIP 2019](https://arxiv.org/abs/1810.05286).

**Mapping to DV.** Constrained-random plus functional coverage *is* property-based testing plus coverage-guided fuzzing, and DV had it first. The gaps: DV rarely mutation-tests its checkers and assertions (does the scoreboard actually catch injected RTL bugs?), rarely quarantines flaky (seed-dependent, timing-dependent) tests systematically, and rarely uses history-based test selection to trim nightly regressions. Böckeler's lesson transfers directly: judge agent-generated tests by outcome metrics (coverage delta, mutants killed), not by whether the agent followed the prescribed process.

---

## 3. Formal methods in software practice

**Findings**

- **AWS runs a portfolio, not a single tool.** AWS moved from TLA+ to the more approachable P language for distributed-protocol modelling, adopted since 2019 across S3, DynamoDB, EBS, Aurora and EC2, and invests in Dafny, Lean and Kani. Its stated approach is "formal and semi-formal": model checking, deterministic simulation, property-based testing, fault injection and fuzzing side by side [Brooker & Desai, ACM Queue vol. 22 no. 6, 2025](https://dl.acm.org/doi/10.1145/3712057); see also the critical retrospective in Formal Aspects of Computing [ACM, 2026](https://dl.acm.org/doi/10.1145/3815784). Amazon rebuilt its authorization engine (AuthV2) in Dafny and proved it against a spec derived from the old engine; Cedar's policy language is verified in Lean.
- **Lightweight formal.** Daniel Jackson's Alloy tradition ("agile modelling") swaps theorem proving for fully automatic bounded analysis with immediate visual feedback; Alloy 6 folded in Electrum's temporal extensions [Formal Software Design with Alloy 6, 2024](https://haslab.github.io/formal-software-design/overview/index.html). Oracle Cloud reports hundreds of TLA+ specs across dozens of services [TLA+ Foundation, 2024](https://foundation.tlapl.us/industry/index.html).
- **LLMs writing specs: weak.** The first systematic study of natural-language-to-TLA+ generation on 205 specs found up to 26.6% syntactic but only 8.6% semantic correctness, with code-specialised models doing *worse* than general ones [arXiv 2606.05792, ICSOFT 2026](https://arxiv.org/abs/2606.05792).
- **LLMs writing verified code: much stronger, language-dependent.** The "vericoding" benchmark (12,504 specs) reports off-the-shelf LLM success of 82% in Dafny, 44% in Verus/Rust and 27% in Lean, with pure Dafny verification accuracy rising from 68% to 96% in a year [Bursuc et al., arXiv 2509.22908, 2025-09-26](https://arxiv.org/abs/2509.22908). Verina benchmarks code + spec + proof generation in Lean [arXiv 2505.23135, 2025](https://arxiv.org/abs/2505.23135).

**Mapping to DV.** Hardware formal (SVA, model checking, equivalence) is more mature than software formal, but the AWS lesson is portfolio thinking: pick the cheapest method that finds the bug class. The LLM data points are the important ones for DV: agents are now good at producing *proofs against a given spec* but poor at producing the *spec* itself. That argues for humans owning assertions and properties while agents grind on proof helpers, covers and abstractions.

---

## 4. Code review and quality

**Findings**

- **AI review is now standard, and reviews the reviewer.** Google's ML-suggested edits resolve about 7.5 to 8% of all code-review comments, projected to save hundreds of thousands of engineer-hours a year [Google Research, 2024-06-06](https://research.google/blog/ai-in-software-engineering-at-google-progress-and-the-path-ahead/); AutoCommenter learns and enforces best practices in four languages via IDE and review [Google Research, 2024](https://research.google/pubs/resolving-code-review-comments-with-machine-learning/). Third-party bots (CodeRabbit, Copilot code review, Cursor BugBot) are widely compared; the consistent conclusion is that they "make human review sustainable at higher volume" rather than replace it [Monterail, 2026](https://www.monterail.com/blog/ai-code-review-tools-compared-how-to-choose-best).
- **Static analysis at scale lives or dies on false positives.** Google's Tricorder requires each analyzer to stay under roughly a 10% false-positive rate or developers disable it; hybrid LLM-plus-SAST pipelines report cutting Semgrep false positives by about 91% on a benchmark [arXiv 2509.15433, 2025-09](https://arxiv.org/abs/2509.15433).
- **Trunk-based development.** DORA continues to list trunk-based development with feature flags and small batches as a core capability of elite teams [DORA, 2025](https://dora.dev/capabilities/trunk-based-development/).
- **Quality of AI-written code is measurably drifting.** GitClear's analysis of 623 million changes (2023 to 2026) shows refactoring (moved lines) collapsing from 21% to 3.8%, block duplication up 81%, and error-masking constructs up 47% [GitClear, 2026-01](https://www.gitclear.com/the_ai_code_quality_maintainability_gap). DORA finds 30% of respondents have little or no trust in AI-generated code [Google Cloud, 2025-09-23](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report).

**Mapping to DV.** Testbench code review is often informal or skipped under schedule pressure. Review-as-gate plus lint (e.g., UVM lint, SVA lint) with a strict false-positive budget, plus AI pre-review of every testbench change, is directly adoptable. GitClear's duplication finding is a warning: agent-generated sequences and checkers will copy-paste unless reuse is enforced.

---

## 5. CI/CD, DevOps and platform engineering

**Findings**

- **Platforms are the multiplier.** DORA 2025 finds 90% of organisations have a platform and names "internal platform quality" and "safety nets/robust control systems" among the seven capabilities that magnify AI's benefit [Google Cloud, 2025-09-23](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report).
- **Hermetic, cached builds.** Bazel's model is content-addressed actions with a shared remote cache and remote execution; healthy monorepos target 85 to 95% cache hit rates on CI [Bazel docs, 2025](https://bazel.build/remote/caching). Nix is used for the pinned outer toolchain with rules_nixpkgs bridging into Bazel [Tweag / GitHub, 2025](https://github.com/filmil/bazel_local_nix).
- **Ephemeral environments.** Per-pull-request preview environments have moved to mainstream enterprise adoption [Core Systems, 2026](https://core.cz/en/blog/2026/ephemeral-environments-2026/).
- **Observability of the pipeline itself.** OpenTelemetry semantic conventions for CI/CD aim to trace pipelines "to help pinpoint flakiness and accelerate root cause analysis" [OpenTelemetry OTEP #223](https://github.com/open-telemetry/oteps/pull/223/files).
- **SRE practices meet agents.** Google SRE operates a 5-minute SLO to acknowledge a page and now uses Gemini-based agents to draft blameless postmortems, file action items and run playbooks, with SREs kept in control for validation [Google Cloud, 2026](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations); the blameless postmortem doctrine itself is in the SRE book [Google SRE](https://sre.google/sre-book/postmortem-culture/).

**Mapping to DV.** Regression farms are DV's CI, but they are seldom hermetic (tool versions, licences, environment leakage), rarely cache compiled snapshots content-addressably, and almost never emit pipeline telemetry. SLO thinking (regression pass-rate budget, time-to-triage) and blameless postmortems on escaped bugs are cultural imports with no tooling cost.

---

## 6. Documentation and knowledge

**Findings**

- **ADRs are being rewritten for agent readers.** Architecture Decision Records remain the standard for "what did we decide and why"; the 2025 to 2026 twist is AGENTS.md / CLAUDE.md files that state "what must never happen and what must always happen" when changing code, and "agent-optimised" ADRs where rejected alternatives become machine-checked guardrails [Actual AI, 2026](https://www.actual.ai/blog/agent-optimized-adrs); [AI Advances, 2026](https://aiadvances.org/agents-md-is-the-ew-architecture-decision-record-adr-3cfb6bdd6f2c).
- **Docs feed agents.** DORA's "internal context connection" capability, connecting AI to internal docs and code, is one of the seven amplifiers [Google Cloud, 2025-09-23](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report). Retrieval-augmented generation is the common grounding layer for copilots over proprietary knowledge, with provenance [arXiv 2407.13193 survey](https://arxiv.org/pdf/2407.13193). Coding-agent traces appear in 22 to 29% of GitHub projects as of Feb 2026 [arXiv 2601.18341, 2026](https://arxiv.org/pdf/2601.18341).
- **Living documentation.** Anthropic's usage study shows documentation and analysis work growing as a share of agent sessions while debugging fell from 33% to 19% [Anthropic, 2026](https://www.anthropic.com/research/claude-code-expertise).

**Mapping to DV.** DV knowledge lives in spec PDFs, wiki pages and people's heads. Docs-as-code for the vPlan, testbench architecture ADRs ("why we chose this scoreboard model"), and runbooks for regression triage would make the environment legible to both new engineers and agents, and would be the corpus a RAG assistant needs.

---

## 7. Developer productivity measurement

**Findings**

- **The METR result.** A randomised trial with 16 experienced open-source developers on 246 real issues found AI tools made them 19% *slower* (early 2025, CI +2% to +39%), while developers believed they were 20% faster [METR, 2025-07-10](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/); [arXiv 2507.09089](https://arxiv.org/abs/2507.09089). A late-2025 follow-up measured roughly -18% for the original cohort and -4% for new recruits, but METR itself flagged severe selection bias (developers refusing to work without AI, 30 to 50% withholding tasks they thought AI would speed up) and concluded "the true speedup could be much higher" [METR, 2026-02-24](https://metr.org/blog/2026-02-24-uplift-update/).
- **DORA.** 90% report using AI; over 80% believe it raised their productivity; throughput improves but stability degrades; the effect size depends on the seven capabilities [Google Cloud, 2025-09-23](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report).
- **SPACE and its limits.** SPACE (Satisfaction, Performance, Activity, Communication, Efficiency) is the standard complement to DORA, but its Activity dimension is "actively misleading" once AI inflates commits and lines of code; the recommended addition during any AI rollout is a recurring developer satisfaction survey [Larridin, 2026](https://larridin.com/developer-productivity-hub/space-framework-explained-2026).
- **What actually changed.** Google reports 50% of code characters written with AI assistance and a 37% completion acceptance rate [Google Research, 2024-06-06](https://research.google/blog/ai-in-software-engineering-at-google-progress-and-the-path-ahead/). Anthropic finds domain expertise, not coding skill, predicts success with agents [Anthropic, 2026](https://www.anthropic.com/research/claude-code-expertise).

**Mapping to DV.** DV already measures the wrong things (test count, coverage percentage) the way software measured lines of code. The METR perception gap is the key warning: self-reported speedups from AI-generated testbench code are not evidence. Measure bugs found per engineer-week, time-to-coverage-closure, and escape rate before and after adopting agents.

---

## 8. Software design principles that still matter

**Findings**

- **Interfaces and modularity are the agent's map.** GitClear's 35% drop in cross-file function calls per changed line indicates AI-written code is becoming less modular and less reused [GitClear, 2026-01](https://www.gitclear.com/the_ai_code_quality_maintainability_gap).
- **Semantic versioning is systematically violated**, with non-major releases carrying breaking changes; breaking changes cascade through transitive dependents [arXiv 2605.24397, 2026](https://arxiv.org/html/2605.24397v1). For generated SDKs, the right version bump is a property of the API contract diff, not the commit log, and this is now automated with LLMs [Fern, 2026-08](https://buildwithfern.com/post/automating-semantic-versioning-api-sdks-claude).
- **Lockfiles and reproducibility.** Lockfiles answer "what is installed", which vulnerability management and reproducible builds require [Vulert, 2025](https://vulert.com/blog/semantic-versioning-security/).
- **Technical debt with AI.** A multivocal review documents early debt signals in LLM-assisted development: duplication, missing refactoring, churn [arXiv 2606.14796, 2026](https://arxiv.org/pdf/2606.14796). Thoughtworks urges "a return to engineering fundamentals to combat cognitive debt" [Thoughtworks, 2026](https://www.prnewswire.com/news-releases/as-ai-accelerates-software-complexity-thoughtworks-technology-radar-urges-a-return-to-engineering-fundamentals-to-combat-cognitive-debt-302737210.html).

**Mapping to DV.** VIP and testbench components are shared libraries without the discipline of shared libraries: no semver, no contract diff, no lockfile pinning of VIP versions per project. Treating a UVM agent's API (sequence items, config objects, analysis ports) as a versioned contract, and pinning VIP versions in a lockfile, would remove a large class of "the regression broke because someone updated the VIP" incidents.

---

## Cross-cutting takeaways for the book

1. **Outcome checks beat process instructions for agents.** Mutation score, coverage delta and property violations are how software teams verify agent-written tests. DV should verify agent-written checkers the same way.
2. **The spec is the product.** Spec Kit, Kiro and plan mode all converge on "write the intent, then generate." The vPlan is DV's spec; make it machine-readable and live.
3. **Stability is the price of throughput unless the safety net is strong.** DORA's finding is a direct forecast for DV teams adopting agents without regression hygiene.
4. **LLMs are good at proofs, bad at specs.** Humans own properties and assertions; agents grind on proofs, covers and abstractions.
5. **Measure honestly.** The METR perception gap applies to verification engineers too.

---

## Key sources

- GitHub Blog, Spec-driven development with AI (2025-09-02): https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- Thoughtworks Radar, Spec-driven development, Assess (2025-11): https://www.thoughtworks.com/radar/techniques/spec-driven-development
- Anthropic, How Claude Code is used in practice (2026): https://www.anthropic.com/research/claude-code-expertise
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Pragmatic Engineer, TDD, AI agents and coding with Kent Beck (2025-06): https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent
- Böckeler, TDD inside the agent loop (2026): https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html
- Maaz et al., Agentic Property-Based Testing (2025-10-10): https://arxiv.org/abs/2510.09907
- Google Security Blog, Leveling Up Fuzzing (2024-11-20): https://security.googleblog.com/2024/11/leveling-up-fuzzing-finding-more.html
- Petrović et al., Practical Mutation Testing at Scale (2021): https://research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/
- Meta Engineering, LLMs are the key to mutation testing (2025-09-30): https://engineering.fb.com/2025/09/30/security/llms-are-the-key-to-mutation-testing-and-better-compliance/
- Google Testing Blog, Where do our flaky tests come from? (2017-04): https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html
- Atlassian, Taming test flakiness (2025-12-08): https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests
- Machalica et al., Predictive Test Selection (ICSE-SEIP 2019): https://arxiv.org/abs/1810.05286
- Brooker & Desai, Systems Correctness Practices at AWS, ACM Queue 22(6): https://dl.acm.org/doi/10.1145/3712057
- Can LLMs Write Correct TLA+ Specifications? (ICSOFT 2026): https://arxiv.org/abs/2606.05792
- Bursuc et al., A benchmark for vericoding (2025-09-26): https://arxiv.org/abs/2509.22908
- Google Research, AI in software engineering at Google (2024-06-06): https://research.google/blog/ai-in-software-engineering-at-google-progress-and-the-path-ahead/
- GitClear, The Maintainability Gap (2026-01): https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- Google Cloud, Announcing the 2025 DORA Report (2025-09-23): https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- METR, Early-2025 AI and experienced OS developer productivity (2025-07-10): https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- METR, Changing our developer productivity experiment design (2026-02-24): https://metr.org/blog/2026-02-24-uplift-update/
- Google Cloud, How Google SRE is using agentic AI (2026): https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations
- Bazel remote caching docs: https://bazel.build/remote/caching
- Breaking Changes in Software Ecosystems, SLR (2026): https://arxiv.org/html/2605.24397v1

## Confidence notes

- **AWS ACM Queue article.** Both the ACM DL and queue.acm.org returned HTTP 403, so the AWS portfolio description (TLA+, P since 2019, Dafny, Lean, Kani; AuthV2 in Dafny; Cedar in Lean) is reconstructed from search summaries and my prior knowledge of the Brooker & Desai paper. Issue/date should be confirmed against the DOI before citation in the book.
- **OSS-Fuzz figures.** "272 projects, 370,000+ lines, 26 vulnerabilities" come from the November 2024 Google Security Blog as reported in secondary coverage; the earlier docs page reports a smaller pilot (14 of 31 projects). Both numbers are real but refer to different phases.
- **Google mutation testing figures** (17M mutants, 760k changes, 2M surfaced) are from the 2021 TSE paper, not a 2024 to 2026 source; no newer public scale figure was found.
- **Flaky test data.** The "1.5% of tests flaky" and "84% of transitions" figures are 2017 Google data; the "16% of tests" figure repeated by several blogs appears to be a misreading and was not used.
- **Böckeler article date.** martinfowler.com did not expose a publication date; the models named (Sonnet 4.6, Opus 4.8) place it in 2026.
- **Facebook predictive test selection** is 2019 and predates the AI era; included because it remains the canonical reference for history-based regression trimming.
- **ADR/AGENTS.md sources** are vendor and practitioner blogs, not peer-reviewed; treat as indicative of practice, not evidence of outcome.
- **Some secondary comparisons** (AI code-review bot benchmark F1 scores, Bazel cache-hit targets, ephemeral-environment adoption percentages) come from vendor content and were deliberately kept out of the headline claims.
