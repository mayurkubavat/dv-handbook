---
title: "Research note: Synopsys AI and agentic tooling for RTL and DV"
date: 2026-09-07
author: research-agent
status: draft
feeds: Appendix on the agent tool layer
---

# Synopsys AI and agentic tooling for RTL and DV

Scope: Synopsys products and published material that apply machine learning,
generative AI or agentic/LLM techniques to RTL design and functional
verification, from the DSO.ai precedent (2020) through Synopsys.ai (2023) and
the AgentEngineer agentic line (2025-2026). **Reachability.** Synopsys product,
blog, glossary and press pages were reachable and are quoted directly. Two
guessed URLs returned 404 (`synopsys.com/verification/ai.html`,
`synopsys.com/ai/agentengineer.html`); the correct slug for the March 2023
Synopsys.ai launch release was recovered through the Wayback CDX index after the
obvious slugs 404'd. The DVCon Proceedings archive was searched (five queries,
below) and returned **no Synopsys-authored AI-verification paper**. SNUG
proceedings sit behind a SolvNetPlus login and could not be opened, so the one
detailed customer result in this note (NVIDIA, SNUG Silicon Valley 2024) survives
only as a Synopsys blog retelling of a customer presentation, not as a paper.
The VSO.ai and CDC white papers are gated behind download forms; only their
landing pages were read. The consequence for the book is stark: **almost
everything Synopsys publishes about AI in verification is vendor material.**

## 1. Synopsys.ai: the umbrella

Synopsys.ai was announced on **2023-03-29** as "the industry's first full-stack,
AI-driven EDA suite" [[Synopsys, 2023-03-29](https://news.synopsys.com/2023-03-29-Synopsys-ai-Unveiled-as-Industrys-First-Full-Stack,-AI-Driven-EDA-Suite-for-Chipmakers)] **[vendor]**.
That release describes the suite by function — "digital design space
optimization," "analog design automation," "verification coverage closure,"
"automated test generation," "manufacturing" — rather than by product name; the
brand names DSO.ai / VSO.ai / TSO.ai attach to those slots on the current
product pages. The suite was extended with data analytics on **2023-09-06**
[[Synopsys, 2023-09-06](https://news.synopsys.com/2023-09-06-Synopsys-Extends-Synopsys-ai-EDA-Suite-with-Industrys-First-Full-Stack-Big-Data-Analytics-Solution)] **[vendor]**.

The current umbrella page lists DSO.ai, ASO.ai, VSO.ai, 3DSO.ai, TSO.ai,
Design.da and Silicon.da, and claims "Unlock up to 30% productivity gains across
the silicon lifecycle" and "Speed development cycles and innovation for
next-generation chips by 5X" [[Synopsys.ai](https://www.synopsys.com/ai.html),
accessed 2026-09-07] **[vendor]**. The page carries **no date and no baseline**
for either figure.

The generative-AI layer arrived on **2023-11-15** as Synopsys.ai Copilot, built
with Microsoft Azure OpenAI Service and described as "the first in a planned line
of generative AI capability from Synopsys"
[[Synopsys, 2023-11-15](https://news.synopsys.com/2023-11-15-Synopsys-Announces-Synopsys-ai-Copilot,-Breakthrough-GenAI-Capability-to-Accelerate-Chip-Design)] **[vendor]**.
A follow-on release on **2023-11-27** collected endorsements from AMD, Intel and
Microsoft; all three are **qualitative, with no numbers** — Microsoft's is
"plan to apply its generative AI to workflows like formal verification to
increase accessibility and reduce the time from ideation to design"
[[Synopsys, 2023-11-27](https://news.synopsys.com/2023-11-27-Market-Leaders-Collaborate-with-Synopsys-to-Realize-Gains-of-Generative-AI-Across-Synopsys-ai-Full-EDA-Stack)] **[vendor]**.

On **2026-04-29** Synopsys described five commercial assistants and attached a
number to each: Knowledge Assistant, "up to 70% faster time-to-answers";
Workflow Assistant, "up to 60% faster time-to-solution for most use cases and up
to 20× faster time-to-solution for specific use cases"; Code Advisor, RTL
generation from natural language with "up to 30% improvement in productivity";
Formal Advisor, "a 4-5× productivity boost"; and Lint Advisor. Fujitsu's Toshio
Yoshida is quoted: "We achieved a 10–30% productivity boost in RTL code
generation with Synopsys.ai Code Advisor." The blog summarizes customer
experience as "2–5× faster chip design productivity," qualified as "Based on
initial feedback"
[[Synopsys blog, 2026-04-29](https://www.synopsys.com/blogs/chip-design/synopsys-ai-copilots-chip-design.html)] **[vendor]**.

Separately, trade press reported that "Microsoft's silicon team has used this to
create formal testbenches, including generating System Verilog Assertions (SVAs),
auxiliary logic, TCL scripts, properties and bind files," achieving "over 80%
syntax accuracy and 70% functional accuracy for most properties"
[[Electronic Specifier, 2025-05-21](https://www.electronicspecifier.com/products/artificial-intelligence/microsoft-and-synopsys-realise-benefits-of-ai-for-chip-design/)] **[vendor, restated by trade press]**.
No named person is credited with those percentages in the article and no
methodology is given — this is the most frequently repeated SVA-accuracy figure
in the trade press and it is **not** a measured result.

## 2. VSO.ai: verification space optimization

VSO.ai is the verification-side analogue of DSO.ai. The product page calls it
"the industry's first AI-driven verification solution to help verification teams
achieve coverage closure faster and with higher quality," and describes the
mechanism precisely enough to teach from: "Machine learning technologies are used
to identify and eliminate redundancies in regressions, automate coverage root
cause analysis, and infer coverage from RTL and stimulus to identify coverage
gaps." It "operates within the simulator to expertly target and improve coverage
at the constraint solver, test, and test-option levels" and "easily integrates
into existing VCS®-regression environments without any code changes in the design
or testbench" [[Synopsys VSO.ai](https://www.synopsys.com/ai/ai-powered-eda/vso-ai.html),
accessed 2026-09-07] **[vendor]**. The page is **undated**. The mechanism
description is confirmed verbatim on the coverage-closure webinar page, presented
by Will Chen and Taruna Reddy of Synopsys
[[Synopsys webinar](https://www.synopsys.com/webinars/accelerate-coverage-closure-vso-ai.html),
accessed 2026-09-07, undated] **[vendor]**.

The headline numbers — "Up to 10x Verification Productivity Boost" and "up to 10x
improvement in reducing functional coverage holes and up to 30% increase in IP
verification productivity" — originate in the **2023-03-29** launch release,
where they are a customer quotation from Takahiro Ikenobe of Renesas, describing
"AI-driven verification with Synopsys VCS®, part of the Synopsys.ai EDA suite"
[[Synopsys, 2023-03-29](https://news.synopsys.com/2023-03-29-Synopsys-ai-Unveiled-as-Industrys-First-Full-Stack,-AI-Driven-EDA-Suite-for-Chipmakers)] **[vendor]**.
No design, coverage model, regression size or baseline flow accompanies them.

**The strongest verification result found in this search** is a Synopsys blog
account of an NVIDIA presentation at SNUG Silicon Valley 2024. NVIDIA applied
VSO.ai late in a design referred to only as "Project C," on "a constrained random
testbench compliant with the Universal Verification Methodology (UVM)," and
reported: "33% more functional coverage in the same number of test runs," a "5X"
reduction in regression suite size, a "20% improvement" in code and assertion
coverage, and "16X regression compression over the baseline"
[[Synopsys blog by Taruna Reddy, 2024-09-04](https://www.synopsys.com/blogs/chip-design/vso-ai-nvidia.html)] **[vendor blog reporting an industry presentation]**.
This is the closest thing to a measured, baselined result on the Synopsys side:
a named customer, a named methodology, a stated baseline ("same number of test
runs," "over the baseline"), and a conference venue. The underlying SNUG paper
is not publicly retrievable, so the numbers cannot be independently checked and
the design is anonymized.

## 3. Debug and formal: Verdi, VC Formal, VCS

This layer is the thinnest in public documentation.

- **Verdi.** "AI-driven debug and new root cause analysis engines designed to
  speed-up bug finding," presented by Robert Ruiz and Myles Glisson of Synopsys
  [[Synopsys webinar](https://www.synopsys.com/webinars/ai-driven-debug-verdi.html),
  accessed 2026-09-07, **undated**] **[vendor]**. No algorithm, no numbers.
- **VC Formal.** The only AI language on the product page is "Leveraging the
  latest formal technologies and Machine Learning techniques, Synopsys VC
  Formal™ has the capacity, speed and flexibility to exhaustively verify some of
  the most complex SoC designs"
  [[Synopsys VC Formal](https://www.synopsys.com/verification/static-and-formal-verification/vc-formal.html),
  accessed 2026-09-07] **[vendor]**. No named feature (engine selection, proof
  orchestration), no numbers, no date. The concrete formal AI claim lives with
  **Formal Advisor**, "a 4-5× productivity boost" (§1, 2026-04-29).
- **VC SpyGlass CDC.** A white-paper landing page describes "machine
  learning-based root cause analysis (ML-RCA) technology" for CDC violations and
  claims "10X faster CDC analysis and RTL signoff," motivated by "millions of
  clock domain crossing (CDC) violations at the SoC level"
  [[Synopsys white paper](https://www.synopsys.com/verification/resources/whitepapers/10x-cdc-debug-ml.html),
  accessed 2026-09-07] **[vendor]**. **No baseline design is named and the page
  is undated**; the PDF is gated. This is nevertheless a useful teaching example
  of ML applied to a static-analysis noise problem rather than to stimulus.
- **VCS.** The VCS page names Intelligent Coverage Optimization (ICO), Dynamic
  Performance Optimization (DPO), Dynamic Test Loading (DTL) and constraint
  solver optimization, but **does not characterize them as AI or ML** and gives
  no numbers [[Synopsys VCS](https://www.synopsys.com/verification/simulation/vcs.html),
  accessed 2026-09-07] **[vendor]**. VSO.ai is the AI layer above VCS, not a VCS
  feature.

## 4. Agentic offerings

Synopsys defines a five-level autonomy scale — "basic, assistive automation (L1)
to collaborative, partially autonomous agents (L2–L4), and ultimately to highly
autonomous, self-directed agents (L5)" — and claims to be "the first company to
deliver GenAI agents and define the future of Agentic AI through its L1–L5
framework." AgentEngineer™ is "a new class of AI-powered agents capable of
reasoning, planning, learning, and executing engineering tasks both individually
and in coordinated multi-agent teams"
[[Synopsys glossary, Rob van Blommestein, 2025-11-06](https://www.synopsys.com/glossary/what-is-eda-agentic-ai.html)] **[vendor]**.
The scale is self-defined and aligns with no standard and with no other vendor's
scale.

**2026-03-11.** Synopsys announced an "Industry-first L4 agentic workflow for
design and verification" powered by AgentEngineer, "the new adaptive learning,
multi-agent orchestrated system." It can "generate Register Transfer Level (RTL)
code from natural language and formal specification, run Lint checks to ensure
clean RTL, generate unit-level testbenches, and finally iteratively run
verification," against a task the release says "typically takes a team of
verification engineers four to six months for a large SoC design." The claim:
"Already helping customers improve productivity by 2x, with improvements as high
as 5x observed in select cases." No customer is named and no production date is
given — Synopsys "is currently engaging with customers"
[[Synopsys, 2026-03-11](https://news.synopsys.com/2026-03-11-Synopsys-Outlines-Vision-for-Engineering-the-Future)] **[vendor]**.

**DAC 2026 (announced 2026-07-26).** An autonomous verification closure agent
covering "test planning to coverage closure and debug," claiming "50× faster RTL
validation, +20% higher coverage"
[[Synopsys agentic AI page](https://www.synopsys.com/ai/agentic-ai.html),
accessed 2026-09-07] **[vendor]**. Trade coverage adds the runtime stack — "the
NVIDIA Agent Toolkit, the Nemotron 3 Ultra open model, and a sandboxing layer
NVIDIA calls the OpenShell runtime" — a mixed-signal claim of "up to 3x
productivity," and availability "planned for the second half of 2026." Crucially,
the same article records the footnote: results are compared to "traditional
verification workflows not powered by AgentEngineer technology," with **no
design, process node, or engineer-hours disclosed**, and observes that the jump
from March's 2x to July's 50x means customers should demand "before-and-after
figures before treating it as settled"
[[Unite.AI, 2026-07-26](https://www.unite.ai/synopsys-hands-chip-verification-to-autonomous-ai-agents/)] **[trade press, critical]**.

## 5. Measured results, as distinct from claims

| Claim | Figure | Who says it | Venue | Vendor or measured |
|---|---|---|---|---|
| VSO.ai coverage-hole reduction | up to 10x | Takahiro Ikenobe, Renesas, quoted by Synopsys | Press release, 2023-03-29 | **Vendor** (customer quote, no baseline) |
| VSO.ai IP verification productivity | up to 30% | same | same | **Vendor** |
| VSO.ai on a UVM CR testbench | +33% functional coverage at equal test count; 5X smaller regression; +20% code/assertion coverage; 16X regression compression | NVIDIA engineers, retold by Synopsys | SNUG Silicon Valley 2024, blog 2024-09-04 | **Closest to measured**; baseline stated, paper not public |
| Copilot formal testbench generation | >80% syntax, 70% functional accuracy | Unattributed; Microsoft silicon team's work | Trade article, 2025-05-21 | **Vendor**, restated |
| Formal Advisor | 4-5x productivity | Synopsys | Blog, 2026-04-29 | **Vendor** |
| Code Advisor | up to 30%; Fujitsu 10-30% | Synopsys; Toshio Yoshida, Fujitsu | Blog, 2026-04-29 | **Vendor** (customer quote) |
| Knowledge / Workflow Assistant | 70% faster answers; 60%, up to 20x faster solutions | Synopsys | Blog, 2026-04-29 | **Vendor** |
| ML-RCA for CDC | 10X faster CDC analysis and signoff | Synopsys | White-paper page, undated | **Vendor**, no baseline |
| AgentEngineer L4 workflow | 2x typical, up to 5x select | Synopsys | Press release, 2026-03-11 | **Vendor**, unnamed customers |
| Verification closure agent | 50x faster validated RTL, +20% coverage | Synopsys | DAC 2026 / product page, 2026-07-26 | **Vendor**, footnote discloses no baseline |
| Synopsys.ai suite | 30% lifecycle productivity, 5X cycles | Synopsys | Product page, undated | **Vendor** |
| DSO.ai adoption | 100 commercial tape-outs by Jan 2023 | Synopsys | Press release, 2023-02-07 | **Vendor**, but a countable fact |

Note the pattern the book should point out: **the one entry with a stated
baseline is also the one presented at a users' conference by the customer.**

## 6. Suggested BibTeX entries

| Key | Citation | Supports |
|---|---|---|
| `synopsys-ai-suite-2023` | Synopsys, "Synopsys.ai Unveiled as Industry's First Full-Stack, AI-Driven EDA Suite for Chipmakers," press release, 2023-03-29. https://news.synopsys.com/2023-03-29-Synopsys-ai-Unveiled-as-Industrys-First-Full-Stack,-AI-Driven-EDA-Suite-for-Chipmakers (accessed 2026-09-07) | Umbrella launch date; Renesas 10x/30% quote |
| `synopsys-tapeouts-2023` | Synopsys, "AI-designed Chips Reach Scale with First 100 Commercial Tape-outs Using Synopsys Technology," press release, 2023-02-07. https://news.synopsys.com/2023-02-07-AI-designed-Chips-Reach-Scale-with-First-100-Commercial-Tape-outs-Using-Synopsys-Technology (accessed 2026-09-07) | DSO.ai adoption scale |
| `synopsys-dso-ai` | Synopsys, "DSO.ai: Design Space Optimization AI," product page. https://www.synopsys.com/ai/ai-powered-eda/dso-ai.html (accessed 2026-09-07) | 2020 launch; reinforcement learning for PPA; the precedent VSO.ai is modeled on |
| `synopsys-vso-ai` | Synopsys, "VSO.ai: Verification Space Optimization," product page, undated. https://www.synopsys.com/ai/ai-powered-eda/vso-ai.html (accessed 2026-09-07) | What VSO.ai does; the 10x/30% vendor claim |
| `synopsys-vso-nvidia-2024` | T. Reddy, "NVIDIA accelerates coverage closure with VSO.ai," Synopsys blog, 2024-09-04, reporting a SNUG Silicon Valley 2024 presentation. https://www.synopsys.com/blogs/chip-design/vso-ai-nvidia.html (accessed 2026-09-07) | The one baselined coverage result |
| `synopsys-copilot-2023` | Synopsys, "Synopsys Announces Synopsys.ai Copilot," press release, 2023-11-15. https://news.synopsys.com/2023-11-15-Synopsys-Announces-Synopsys-ai-Copilot,-Breakthrough-GenAI-Capability-to-Accelerate-Chip-Design (accessed 2026-09-07) | GenAI layer date; Azure OpenAI partnership |
| `synopsys-copilots-2026` | Synopsys, "Synopsys.ai Copilots for chip design," blog, 2026-04-29. https://www.synopsys.com/blogs/chip-design/synopsys-ai-copilots-chip-design.html (accessed 2026-09-07) | Five commercial assistants; Formal Advisor 4-5x; Fujitsu quote |
| `synopsys-agentengineer-2026` | Synopsys, "Synopsys Outlines Vision for Engineering the Future," press release, 2026-03-11. https://news.synopsys.com/2026-03-11-Synopsys-Outlines-Vision-for-Engineering-the-Future (accessed 2026-09-07) | L4 multi-agent design/verification workflow; 2x-5x claim |
| `synopsys-agentic-ai-page` | Synopsys, "Agentic AI," product page. https://www.synopsys.com/ai/agentic-ai.html (accessed 2026-09-07) | Autonomous verification closure agent; 50x/+20% claim |
| `vanblommestein-eda-agentic-2025` | R. van Blommestein, "What is EDA Agentic AI?," Synopsys glossary, 2025-11-06. https://www.synopsys.com/glossary/what-is-eda-agentic-ai.html (accessed 2026-09-07) | The L1-L5 autonomy scale as a vendor taxonomy |
| `uniteai-synopsys-agents-2026` | Unite.AI, "Synopsys hands chip verification to autonomous AI agents," 2026-07-26. https://www.unite.ai/synopsys-hands-chip-verification-to-autonomous-ai-agents/ (accessed 2026-09-07) | DAC 2026 agent; NVIDIA runtime stack; the missing-baseline critique |
| `electronicspecifier-msft-synopsys-2025` | Electronic Specifier, "Microsoft and Synopsys realise benefits of AI for chip design," 2025-05-21. https://www.electronicspecifier.com/products/artificial-intelligence/microsoft-and-synopsys-realise-benefits-of-ai-for-chip-design/ (accessed 2026-09-07) | The 80%/70% SVA accuracy figure, as a vendor-derived claim |
| `synopsys-cdc-ml-rca` | Synopsys, "10X Faster CDC Debug with Machine Learning," white paper landing page, undated. https://www.synopsys.com/verification/resources/whitepapers/10x-cdc-debug-ml.html (accessed 2026-09-07) | ML root-cause analysis applied to CDC violation triage |
| `synopsys-vc-formal` | Synopsys, "VC Formal," product page. https://www.synopsys.com/verification/static-and-formal-verification/vc-formal.html (accessed 2026-09-07) | That ML in formal is asserted but unspecified |

## 7. Confidence notes and gaps

**Never print as a result.** Every figure in §5 marked **Vendor** must appear in
the book, if at all, as "Synopsys states...", "the press release claims..." or
"Renesas is quoted as reporting...". Specifically: the **10x coverage-hole
reduction and 30% IP verification productivity** (VSO.ai); the **50x faster
validated RTL and +20% coverage** (verification closure agent) — the vendor's own
footnote concedes no design, node or engineer-hours; the **2x-5x** AgentEngineer
productivity; the **4-5x** Formal Advisor boost; the **70% / 60% / 20x**
assistant figures; the **10X** CDC ML-RCA claim; and the suite-level **30%** and
**5X**. The **>80% syntax / 70% functional SVA accuracy** figure deserves
particular care: it is widely repeated, is attributed to no named person, states
no benchmark or property set, and reaches the reader through a trade article, not
through Microsoft or Synopsys directly.

**Undated pages.** The VSO.ai product page, the VSO.ai and CDC white-paper
landing pages, the VC Formal page, the Verdi AI-debug webinar page and the
Synopsys.ai umbrella page carry no publication date. Cite them with an access
date only; do not infer a release year from them. The VSO.ai "production since
2023" framing is inferred from the March 2023 launch release, not stated on the
product page.

**Conference papers: a genuine negative result.** The DVCon Proceedings archive
was searched for "VSO.ai", "Verification Space Optimization", "Synopsys AI",
"machine learning coverage Synopsys" and "AI driven verification coverage
regression". No Synopsys-authored paper on AI-assisted verification was found.
The nearest hits are not Synopsys work: "Functional Coverage Closure in SoC
Interconnect Verification with Iterative Machine Learning" (DVCon 2025, Kwon et
al.) and "Accelerate Functional Coverage Closure Using Machine-Learning-Based
Test Selection" (DVCon Europe 2023, Pluciński et al.); affiliations were not
displayed on the archive pages and were not confirmed. Absence in this archive
is not proof of absence overall — DVCon India and SNUG are indexed elsewhere —
but it does mean **no peer-reviewed or archived Synopsys measurement of VSO.ai
or AgentEngineer was located**. SNUG proceedings require SolvNetPlus
authentication and were not opened.

**Gated PDFs.** The VSO.ai white paper ("Accelerating Coverage Closure with
AI-Based Verification Space Optimization") and the CDC ML-RCA white paper are
behind download forms. Their landing-page abstracts are quoted; their bodies were
not read, so any number inside them is unverified here.

**The NVIDIA result needs a caveat if used.** It is the best datapoint in this
note — named customer, UVM constrained-random baseline, four consistent figures —
but the primary source is a Synopsys blog summarizing a customer talk, the design
is anonymized as "Project C", and the SNUG slides are not public. Present it as
"NVIDIA engineers reported at SNUG Silicon Valley 2024, as summarized by
Synopsys," never as an independent measurement.

**Not found.** No Synopsys DAC or DVCon paper with measured AI-verification
results; no third-party benchmark of VSO.ai or AgentEngineer; no disclosed
baseline for any Synopsys agentic claim; no public description of the algorithms
behind Verdi's "root cause analysis engines" or VC Formal's "Machine Learning
techniques".
