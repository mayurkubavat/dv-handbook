---
title: "Research note: Cadence AI and agentic tooling for RTL and DV"
date: 2026-09-07
author: research-agent
status: draft
feeds: Appendix on the agent tool layer
---

# Cadence AI and agentic tooling for RTL and DV

Scope: Cadence's AI-branded verification stack (Verisium and its apps, the JedAI
data layer, Xcelium ML), Cerebrus as the design-side precedent, and Cadence's
public positioning on agentic AI. **Reachability caveat, which shapes this whole
note:** every `cadence.com` URL attempted returned HTTP 403 to automated
retrieval — product pages, newsroom and `community.cadence.com` alike — and the
Internet Archive was serving a site-wide outage page on the access date, its
availability and CDX APIs returning no snapshots for the Verisium page. Cadence's
*primary* press-release text was therefore taken from EEJournal's `industry_news`
section, which republishes vendor releases verbatim under their original
dateline; quoted dates below are the dateline inside the release body. No Cadence
datasheet or per-app product page could be read, so per-app detail comes from the
launch release. Design & Reuse, EE Times, Business Wire and the general search
engines were also unreachable. No Cadence-authored DVCon or CDNLive paper with
measured Verisium results was retrievable (see §7).

## 1. Verisium: the platform and its apps

Verisium was announced in a press release datelined **September 19, 2022**
[[EEJournal (Cadence press release), 2022-09-19](https://www.eejournal.com/industry_news/cadence-revolutionizes-verification-productivity-with-the-verisium-ai-driven-verification-platform/)]
**[vendor]**. The release describes it as "a suite of applications leveraging big
data and AI to optimize verification workloads, boost coverage and accelerate
root cause analysis of bugs," and states that "The Verisium platform is built on
the new Cadence Joint Enterprise Data and AI (JedAI) Platform and is natively
integrated with the Cadence verification engines."

The mechanism Cadence claims is data unification first, models second: "By
deploying the Verisium platform, all verification data, including waveforms,
coverage, reports and log files, are brought together in the Cadence JedAI
Platform. Machine learning (ML) models are built and other proprietary metrics
are mined from this data." Cadence frames this as "a generational shift from
single-run, single-engine algorithms in electronic design automation (EDA) to
algorithms that leverage big data and AI to optimize multiple runs of multiple
engines" — the multi-run framing is the actual architectural claim.

The six apps, quoted from the same release **[vendor]**:

- **AutoTriage** — "Builds ML models that help automate the repetitive task of
  regression failure triage by predicting and classifying test failures with
  common root causes."
- **SemanticDiff** — "Provides an algorithmic solution to compare multiple source
  code revisions of an IP or SoC, classify these revisions and rank which updates
  are most disruptive to the system's behavior to help pinpoint potential bug
  hotspots." Note this one is described as *algorithmic*, not ML.
- **WaveMiner** — "Applies powerful AI engines to analyze waveforms from multiple
  runs and determine which signals, at which times, are most likely to represent
  the root cause of a test failure."
- **PinDown** — "Integrates with the Cadence JedAI Platform and industry-standard
  revision control systems to build ML models of source code changes, test
  reports and log files to predict which source code check-ins are most likely to
  have introduced failures."
- **Debug** — "Delivers a holistic debug solution from IP to SoC and from
  single-run to multi-run … with waveform, schematic, driver tracing and SmartLog
  technologies," with "simultaneous automatic comparison of passing and failing
  tests."
- **Manager** — verification planning, job scheduling and multi-engine coverage
  moved "natively onto the Cadence JedAI Platform," extended "to support AI-driven
  testsuite optimization to improve compute farm efficiency."

Trade-press coverage adds two operational details worth having, both attributed
to a Cadence briefing rather than to a measurement
[[SemiWiki, Bernard Murphy, 2022-09-20](https://semiwiki.com/artificial-intelligence/318147-finally-a-serious-attack-on-debug-productivity/)]
**[vendor claim, reported by trade press]**: "AutoTriage requires 2-3 regressions
worth of data to start to become productive. PinDown bug prediction needs a
significant history in the revision control system, but if that history exists,
can train in a few hours." The same article asserts that "debug now accounts for
almost half of verification engineer hours on a typical design" — stated without
a source, so it must not be printed as a fact (see §7).

## 2. JedAI: the data layer underneath

JedAI was announced separately and slightly earlier, datelined **September 13,
2022**
[[EEJournal (Cadence press release), 2022-09-13](https://www.eejournal.com/industry_news/new-cadence-joint-enterprise-data-and-ai-platform-dramatically-accelerates-ai-driven-chip-design-development/)]
**[vendor]**. Cadence describes it as "a critical big data analytics
infrastructure that unifies massive data sets across all Cadence computational
software," and states that it unifies analytics "across its AI platforms —
Verisium™ verification, Cadence Cerebrus™ implementation, and Optimality™ system
optimization — as well as third-party silicon lifecycle management systems."

It stores three declared categories, quoted:

- "**Design data** such as waveforms and coverage in functional verification,
  physical layout shapes, timing/power/voltage/variation analysis reports, design
  RTL, netlist and SDC specifications in design implementation"
- "**Workload data** such as runtime, memory usage and disk space usage, as well
  as metadata about the inputs to each job and dependencies between them"
- "**Workflow data** such as the tools and methodology used to create a design"

Two points are pedagogically useful. First, it is openly queryable: Cadence states
it "offers open industry-standard user interfaces such as Python, Jupyter Notebook
and REST APIs, enabling designers to create custom analytics applications."
Second, the stated motivation is retention of data that used to be thrown away —
Venkat Thanvantri, VP of AI R&D at Cadence: "Previously, we saw that once a chip
design project was completed, the valuable data was deleted to make way for the
next project."

## 3. Regression and coverage: Xcelium ML

Xcelium ML predates the Verisium branding by two years, datelined **August 12,
2020**
[[EEJournal (Cadence press release), 2020-08-12](https://www.eejournal.com/industry_news/cadence-delivers-machine-learning-optimized-xcelium-logic-simulation-with-up-to-5x-faster-regressions/)]
**[vendor]**. Cadence states that it "enables up to 5X faster verification closure
on randomized regressions," and describes the mechanism concretely: "a proprietary
machine learning technology that directly interfaces to the simulation kernel,
Xcelium ML learns iteratively over an entire simulation regression. It analyzes
patterns hidden in the verification environment and guides the Xcelium
randomization kernel on subsequent regression runs to achieve matching coverage
with reduced simulation cycles." The important qualifier is *matching coverage
with fewer cycles* — this is regression compaction, not coverage improvement.

A customer figure appears in the same release: Kazunari Horikawa, senior manager,
Design Technology Innovation Division at Kioxia, is quoted saying "we've seen a 4X
shorter turnaround time in our fully random regression runs to reach 99% function
coverage of original." Note both qualifiers — 99% *of original* coverage, and
"plan to use this technology in production designs," i.e. this was a pilot at the
time of the release.

## 4. Agentic offerings

Cadence's agentic messaging is, on the public record found here, a **design-side**
story, not yet a verification one. Reporting on Anirudh Devgan's CadenceLIVE
Silicon Valley 2025 keynote
[[SemiWiki, Bernard Murphy, 2025-05-29](https://semiwiki.com/eda/cadence/356323-anirudh-keynote-at-cadencelive-2025-reveals-millennium-m2000/)]
**[trade press reporting a vendor keynote]** describes "a moonshot towards full
autonomy in chip design exploiting agentic AI," graded on an SAE-style scale:
Cadence positions much of its current offering "already at levels 2 or 3," with
announced advances stretching "to levels 3 and 4, thanks in part to a big
investment in agentic AI which makes more complex chains of reasoning possible."
Level 5 "he acknowledges is a moonshot."

The load-bearing sentence for a DV textbook is the scope statement: "Now Agentic
AI is available in Integrity 3D-IC, Cerebrus AI Studio and Virtuoso Studio" —
followed immediately by the author's own aside, "I'm looking forward to seeing
applications in functional verification – maybe next year?" As of May 2025,
therefore, Cadence had **not** announced an agentic functional-verification
product; the stated route toward autonomy in verification was generative rather
than agentic — "generating testbenches, both UVM and Perspec," AI-generated C fed
through C-to-RTL, and RAG-assisted RTL generation.

Cadence's verification GM does engage publicly with agentic-LLM engineering
questions — a co-authored review of research on LLM model routing for agentic
cost control appeared
[[SemiWiki "Innovation in Verification", Bernard Murphy with Paul Cunningham
(GM, Verification at Cadence) and Raúl Camposano,
2026-08-31](https://semiwiki.com/artificial-intelligence/372524-exploiting-agentic-automation-cost-effectively-innovation-in-verification/)]
**[trade press / research commentary]** — but that is commentary on third-party
research, not a product claim.

The design-side precedent, for context: Cerebrus Intelligent Chip Explorer,
datelined **July 22, 2021**
[[EEJournal (Cadence press release), 2021-07-22](https://www.eejournal.com/industry_news/cadence-extends-digital-design-leadership-with-revolutionary-ml-based-cerebrus-delivering-best-in-class-productivity-and-quality-of-results/)]
**[vendor]**, uses reinforcement learning to drive the RTL-to-signoff flow;
Cadence states it delivers "up to 10X productivity and 20% PPA improvements for
implementation," with a "re-usable and transportable reinforced learning model
that increases effectiveness with each use."

## 5. Measured results, as distinct from claims

| Claim | Figure | Who says it | Venue | Vendor or measured |
|---|---|---|---|---|
| Verisium apps improve debug productivity | "up to 6X" (headline adds "for specific bugs") | Noriaki Sakamoto, president, Renesas Design Vietnam | Cadence press release, [2023-03-09](https://www.eejournal.com/industry_news/cadence-verisium-ai-driven-verification-platform-accelerates-debug-productivity-for-renesas/) | **Vendor channel**; customer-attributed, no method disclosed |
| Verisium Debug waveform format improves probing | "improve simulation probing performance by 2X" | Noriaki Sakamoto, Renesas | Same release, 2023-03-09 | **Vendor channel**; customer-attributed |
| Xcelium ML regression closure | "up to 5X faster verification closure on randomized regressions" | Cadence | Cadence press release, [2020-08-12](https://www.eejournal.com/industry_news/cadence-delivers-machine-learning-optimized-xcelium-logic-simulation-with-up-to-5x-faster-regressions/) | **Vendor** |
| Xcelium ML turnaround | "4X shorter turnaround time … to reach 99% function coverage of original" | Kazunari Horikawa, Kioxia | Same release, 2020-08-12 | **Vendor channel**; customer-attributed, pilot |
| Xcelium ML coverage | "up to 5X faster coverage with the same CPU usage" | Paul Cunningham, Cadence | 60th DAC Pavilion talk, reported [2023-08-07](https://semiwiki.com/eda/332886-cadence-and-ai-at-60dac/) | **Vendor**, restated at a conference pavilion |
| Cerebrus deployment | "used on more than 180 tapeouts"; "one engineer to do the work of 10 previous engineers" | Paul Cunningham, Cadence | 60DAC Pavilion, reported 2023-08-07 | **Vendor** |
| Jasper AI property generation | "about 30% more properties versus a manual approach" | Paul Cunningham, Cadence | 60DAC Pavilion, reported 2023-08-07 | **Vendor** |
| Cerebrus implementation | "up to 10X productivity and 20% PPA improvements" | Cadence | Press release, [2021-07-22](https://www.eejournal.com/industry_news/cadence-extends-digital-design-leadership-with-revolutionary-ml-based-cerebrus-delivering-best-in-class-productivity-and-quality-of-results/) | **Vendor** |
| Cerebrus at a customer | "more than an 8% power reduction … in just a few days versus many months of manual effort" | Sangyun Kim, VP, Samsung Foundry | Same release, 2021-07-22 | **Vendor channel**; customer-attributed |
| Debug share of effort | "almost half of verification engineer hours" | Bernard Murphy | [SemiWiki, 2022-09-20](https://semiwiki.com/artificial-intelligence/318147-finally-a-serious-attack-on-debug-productivity/) | **Unsourced assertion** — do not print |

Endorsement-only claims (no figures) from the Verisium launch release: MediaTek
(Chinh Tran, Deputy GM, Silicon Product Development) on "groundbreaking ability to
automatically accelerate the effort to root cause bugs"; Samsung (S. Brian Choi,
Corporate VP) on "impressive results to automatically triage and root cause bugs";
STMicroelectronics (Mirella Negro Marcigaglia, STM32 Digital Verification Manager)
on "a significant boost to functional verification productivity, leveraging
Verisium AutoTriage, SemanticDiff and WaveMiner." **None of these carry a number**,
and all are quotes selected by the vendor for its own release.

**There are no independently measured results in this note.** Every figure above
originates in a Cadence-controlled channel.

## 6. Suggested BibTeX entries

| Key | Citation | Supports |
|---|---|---|
| `cadence-verisium-pr-2022` | Cadence Design Systems, "Cadence Revolutionizes Verification Productivity with the Verisium AI-Driven Verification Platform," press release, 19 September 2022. Republished by EEJournal, https://www.eejournal.com/industry_news/cadence-revolutionizes-verification-productivity-with-the-verisium-ai-driven-verification-platform/ (accessed 7 September 2026). | Verisium platform definition; the six app descriptions; multi-run framing |
| `cadence-jedai-pr-2022` | Cadence Design Systems, "New Cadence Joint Enterprise Data and AI Platform Dramatically Accelerates AI-Driven Chip Design Development," press release, 13 September 2022. Republished by EEJournal, https://www.eejournal.com/industry_news/new-cadence-joint-enterprise-data-and-ai-platform-dramatically-accelerates-ai-driven-chip-design-development/ (accessed 7 September 2026). | JedAI data categories; Python/Jupyter/REST access; data-retention motivation |
| `cadence-renesas-verisium-2023` | Cadence Design Systems, "Cadence Verisium AI-Driven Verification Platform Accelerates Debug Productivity for Renesas," press release, 9 March 2023. Republished by EEJournal, https://www.eejournal.com/industry_news/cadence-verisium-ai-driven-verification-platform-accelerates-debug-productivity-for-renesas/ (accessed 7 September 2026). | The 6X debug and 2X probing figures, and their qualifiers |
| `cadence-xcelium-ml-2020` | Cadence Design Systems, "Cadence Delivers Machine Learning-Optimized Xcelium Logic Simulation with up to 5X Faster Regressions," press release, 12 August 2020. Republished by EEJournal, https://www.eejournal.com/industry_news/cadence-delivers-machine-learning-optimized-xcelium-logic-simulation-with-up-to-5x-faster-regressions/ (accessed 7 September 2026). | Regression-compaction mechanism; 5X claim; Kioxia 4X |
| `cadence-cerebrus-pr-2021` | Cadence Design Systems, "Cadence Extends Digital Design Leadership with Revolutionary ML-based Cerebrus," press release, 22 July 2021. Republished by EEJournal, https://www.eejournal.com/industry_news/cadence-extends-digital-design-leadership-with-revolutionary-ml-based-cerebrus-delivering-best-in-class-productivity-and-quality-of-results/ (accessed 7 September 2026). | Design-side RL precedent; 10X/20% claims |
| `semiwiki-verisium-2022` | B. Murphy, "Finally, a Serious Attack on Debug Productivity," SemiWiki, 20 September 2022, https://semiwiki.com/artificial-intelligence/318147-finally-a-serious-attack-on-debug-productivity/ (accessed 7 September 2026). | Training-data requirements for AutoTriage and PinDown |
| `semiwiki-cadence-60dac-2023` | D. Payne, "Cadence and AI at #60DAC," SemiWiki, 7 August 2023, https://semiwiki.com/eda/332886-cadence-and-ai-at-60dac/ (accessed 7 September 2026). | Cunningham's DAC-pavilion figures; JedAI as EDA 2.0 framing |
| `semiwiki-cadencelive-2025` | B. Murphy, "Anirudh Keynote at CadenceLIVE 2025 Reveals Millennium M2000," SemiWiki, 29 May 2025, https://semiwiki.com/eda/cadence/356323-anirudh-keynote-at-cadencelive-2025-reveals-millennium-m2000/ (accessed 7 September 2026). | Agentic AI scope (Integrity 3D-IC, Cerebrus AI Studio, Virtuoso Studio); SAE autonomy framing; absence of agentic DV |
| `bendhaou-2025-survey` | I. Ben Dhaou, S. Larguech (Cadence Design Systems), S. R. Rajendran, R. S. Chakraborty, H. Tenhunen and A. Abdelgawad, "Deep Learning and Generative AI for Monolithic and Chiplet SoC Design and Verification: A Survey," *Foundations and Trends in Electronic Design Automation*, 2025. DOI 10.1561/1000000063-1 (accessed 7 September 2026). | The one peer-reviewed, Cadence-co-authored survey located; background, not product results |

## 7. Confidence notes and gaps

**Could not be verified.** All `cadence.com` pages returned HTTP 403 on
2026-09-07 — Verisium platform and per-app pages, newsroom, and
`community.cadence.com` — and the Internet Archive was down, so no archived copy
could be substituted. Consequently **no Verisium datasheet, no per-app product
page and no Cadence blog post was read.** The app list here is as of the 2022
launch; Cadence may have added or renamed apps since, so a human should open the
product pages in a browser and confirm before the appendix names them.

**Conference papers — the notable miss.** No Cadence-authored DVCon, DAC or
CDNLive paper reporting measured Verisium or Xcelium ML results was found. The
DVCon Proceedings Archive is reachable but its public search index is partial (its
faceted full-archive search is JavaScript-driven and its API route was not
available), and a sweep of the indexed subset for *Cadence*, *Verisium*,
*triage*, *LLM*, *agentic*, *Xcelium* and related terms returned only unrelated
papers. An OpenAlex query restricted to Cadence-affiliated authors, 2020–2026,
surfaced no verification-AI measurement paper — only the survey listed above.
**This should be treated as "not found," not as "does not exist";** DVCon and
CDNLive papers are frequently un-indexed, and CDNLive proceedings are behind
Cadence login in any case. This is the highest-value remaining gap.

**Numbers that must never be printed as results.** The 6X Renesas debug figure,
the 2X probing figure, the 5X Xcelium ML figure, the Kioxia 4X figure, the 10X/20%
Cerebrus figures, the Samsung 8% power and 50% timing figures, the "180 tapeouts,"
the "one engineer doing the work of 10," and the Jasper "30% more properties" are
**all vendor claims**, published in Cadence press releases or spoken by a Cadence
executive at a vendor pavilion. Several are customer-attributed, which is stronger
than a bare vendor assertion but is still vendor-selected, method-undisclosed
testimony: no baseline, no design, no sample size, no counterfactual. In the book
they must be written as "Cadence states…" or "Renesas is quoted in a Cadence press
release as reporting…," never as measured outcomes, and the Renesas headline
qualifier "for specific bugs" should be preserved wherever the 6X is mentioned.

The "debug is almost half of verification engineer hours" line is an unsourced
assertion in a trade-press article and should not be used at all; if the book needs
a debug-effort figure, take it from the Wilson Research Group functional
verification study instead.

**One dating caution.** The press-release texts above are republications. Their
datelines are internally consistent (the release body carries the SAN JOSE
dateline), but the canonical `cadence.com/newsroom` URLs could not be confirmed,
so each BibTeX entry cites the republication URL and states the release date from
the dateline.
