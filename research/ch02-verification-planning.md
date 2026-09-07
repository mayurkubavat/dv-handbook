---
title: "Research note: Verification Planning (specification → features → plan → coverage model → sign-off)"
date: 2026-09-06
author: research-agent
status: draft
feeds: Ch. 2
---

# Research note: Verification Planning

Scope: what a verification plan is according to canonical and standards sources, how features are extracted from a specification and traced to tests and coverage, how the coverage model is derived from the plan, what tools and formats exist (with OpenTitan as the open primary example), sign-off criteria, known failure modes with survey evidence, and the state of AI-assisted planning. Labels used throughout: **[methodology]** for textbook/cookbook guidance, **[standard]** for normative documents, **[primary/open]** for open-source project artefacts, **[vendor]** for marketing or product documentation, **[survey]** for industry studies, **[research]** for peer-reviewed or preprint results.

Note on method: web search quota was exhausted partway through this run, so sources were reached by direct URL fetch. Gaps are flagged in the final section rather than filled by guesswork.

## 1. What a verification plan is (canonical sources)

### 1.1 Textbooks

- **Bergeron, *Writing Testbenches* (2003)** [methodology]. Bergeron's chapter on the verification plan frames it as the document that answers, before any testbench is written, *what* will be verified, *how* (which feature by which method: simulation, formal, emulation), and *when the job is done*. The chapter argues for writing the plan from the specification rather than from the implementation, for listing features in priority order, and for identifying which features are "must-have" for first silicon. Cite as `bergeron2003testbenches`. Publisher page: [Springer, Writing Testbenches, 2003](https://link.springer.com/book/10.1007/978-1-4615-0302-6). (The 2006 SystemVerilog edition repeats the same chapter structure: [Springer, 2006](https://link.springer.com/book/10.1007/b135575).) *Confidence: moderate; chapter structure confirmed from publisher table of contents, page numbers not verified in this run.*
- **Wile, Goss, Roesner, *Comprehensive Functional Verification* (2005)** [methodology]. Chapter 3 "Fundamentals of Simulation-Based Verification" and the "verification plan" material treat the plan as a joint product of design, verification and architecture teams, structured around: functions to be verified per level of hierarchy (designer, unit, chip, system), the verification environment per level, coverage requirements, and the "done" criteria. Cite as `wile2005cfv`. Publisher page: [Elsevier / ScienceDirect](https://www.sciencedirect.com/book/9780127518039/comprehensive-functional-verification). *Confidence: moderate; from publisher table of contents.*
- **Piziali, *Functional Verification Coverage Measurement and Analysis* (2004)** [methodology]. The standard reference for deriving a *coverage model* from a plan: feature identification from the specification, attribute/value selection, "coverage model design" as a top-down process, and the distinction between implicit (code) coverage and explicit (functional) coverage. New key `piziali2004coverage`. [Springer](https://link.springer.com/book/10.1007/b117979).

### 1.2 Verification Academy / UVM Cookbook

The Siemens Verification Academy Coverage Cookbook (already cited as `va-coverage-cookbook`) is the most widely used free methodology text on planning. Its "Specification to Testplan" and "Testplan to Functional Coverage" articles argue for an **executable testplan**: a spreadsheet or XML document in which each row is a requirement or feature, with columns linking that row to the coverage items (covergroups, coverpoints, crosses, assertions, or directed tests) that measure it, so that coverage tools can annotate the plan with results automatically. See section 4 for details and URLs fetched in this run.

### 1.3 IEEE 1012 (V&V plan)

IEEE Std 1012-2024 (existing key `ieee1012-2024`) [standard] is a software/system/hardware V&V standard rather than a silicon-specific one, but it is the only IEEE standard that defines the *contents* of a V&V plan (VVP). It requires the plan to specify V&V activities per life-cycle process, the integrity level of the item, the tasks, inputs and outputs, and the acceptance criteria; it also requires the plan to be maintained through the life cycle rather than written once. Standards page: [IEEE SA, 1012-2024](https://standards.ieee.org/ieee/1012/7324/). *Use it in the chapter as the "formal" definition of a V&V plan; industry DV plans are looser than IEEE 1012's VVP outline.*

### 1.4 UCIS 1.0 (coverage interchange)

Accellera's Unified Coverage Interoperability Standard, Version 1.0, was approved in June 2012 [standard]. Accellera describes it as "a first step towards the creation of an application interface (API) that allows for interoperability of verification coverage data across multiple tools from multiple vendors" and as "a standardized way to model and access information among different tools to achieve full verification closure" [Accellera, UCIS page, 2012-06](https://www.accellera.org/downloads/standards/ucis). Relevance to planning: UCIS defines the database and API through which a plan-tracking tool can merge coverage from several simulators and formal tools; it does **not** itself define a verification-plan format. New key `ucis2012`. *Gap: the UCIS data model's test-record/history-node objects were not verified from the PDF in this run.*

