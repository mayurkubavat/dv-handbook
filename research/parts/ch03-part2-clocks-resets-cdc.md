---
title: "Research note: Chapter 3, part 2 — clocks, resets and crossings"
date: 2026-09-07
author: research-agent
status: draft
feeds: Ch. 3
---

# Chapter 3 research, part 2: clocks, resets and crossings

Scope: clock domains, metastability and synchronizers, resets, and the limits of
static clock/reset analysis. Citation convention: `[Source, YYYY-MM-DD](URL)`,
where the date is the source's own publication date when it has one and the
access date (2026-09-07) otherwise. Sources are labelled **[standard]**,
**[primary]**, **[vendor]**, **[research]** or **[industry paper]**. Vendor
claims are kept separate from peer-reviewed or measured results.

**Fetch note.** `sunburst-design.com` now issues a 301 to
`paradigm-works.com`, whose technical library serves only metadata and requires
registration for the PDFs. All Cummings papers below were therefore read from
the Internet Archive's captures of the original `sunburst-design.com` files, and
the archive URL is the one cited. `verilab.com/files/sva_cdc_paper_dvcon2006.pdf`
returns 404 and was likewise read from the Internet Archive. Ginosar's ASYNC
2003 paper could not be retrieved in full text from any reachable host; it is
cited by DOI only and **nothing is quoted from it**.

## 1. Clocks and clock domains

A clock, for analysis purposes, is "a periodic binary signal, used to indicate
the sampling point of sequential operators. It is characterized by a period,
duty cycle and phase"
[Plassan, *Conclusive formal verification of clock domain crossing properties*, PhD thesis, Université Grenoble Alpes, 2018-06](https://theses.hal.science/tel-01870205/document)
**[research]**, §3.1.2. Between the primary clock inputs and the flip-flops sits
a network that the same source decomposes into exactly four operations
(§3.1.2, verbatim):

> "Selection: choosing to propagate one clock or another; Blending: combining
> two clocks to generate a new one; Gating: propagating or stopping a clock;
> Shaping: modifying the period, duty cycle or phase of a clock."

and it names the two kinds of node the verifier must tell apart: "A clock is
called a primary clock when it is a primary input of the design or an output of
internal analog modules (e.g. a PLL or a crystal, which is then seen as a
blackbox) ... the signals after selection, blending, gating or shaping, are
called derived clocks" (§3.1.2). The same section warns that "'clock tree' is
misleading, as its formal representation is a directed graph" (footnote 1).

**Gating and glitch hazards.** A clock gate is built sequentially for a reason:
"Note that the gating stage of this example is sequential as it includes a
latch. This is a common clock-gate structure which avoids propagating a glitch
on the clock rising edge (indeed, here the clock can only be disabled when it is
low). Using two clock-gates with inverted control signals, a sequential mux
could easily be implemented (with the same intent of glitch avoidance)"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §3.1.2. The
enable itself is a crossing: "Clock-gating signals are synchronized to eliminate
clock glitches when the clocks are gated or when a domain switches from one
clock to another"
[Ginosar, *Metastability and Synchronizers: A Tutorial*, IEEE Design & Test of Computers, 2011-09](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
(DOI [10.1109/MDT.2011.113](https://doi.org/10.1109/MDT.2011.113))
**[primary]**, p. 30.

The distinction the chapter wants — a gated clock does not create a new domain,
a muxed clock may — follows from those definitions rather than from a sentence
in either source: gating only propagates or stops one source clock, so the
derived clock keeps that source's period and phase, whereas selection can hand
the same derived node the timing of either input. See §5, row 1: the reasoning
is sound but the exact claim is not quoted anywhere and should be stated as the
book's own inference.

**Scale.** On the OpenSPARC case study, the clock/reset control module drives
"the whole system among its 38 primary clocks and 17 primary resets ... The
clock propagation leads to a global clock path of 450 sequential elements (most
of them covered by 2 mission clocks). 134 configuration signals are identified"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §3.5.3. Crucially
for the verifier's reading: "Because this control module was reused from previous
projects, and because an exhaustive specification was not available, the clock
configurations and clock tree components were not perfectly understood by the
verification engineers" (ibid.).

**Domain relationships the specification must state.** Ginosar's tutorial names
them: two *mesochronous* domains "tick to the same frequency, but their relative
phase is unknown in advance"; drift makes them *multisynchronous* — "domains
operating at the same frequency but at slowly changing relative phases";
*periodic* clocks "are unrelated to each other — they are neither mesochronous
nor are their frequencies an integral multiple of each other"; and for *rational*
clocks "the two frequencies are related by a ratio known at design time (e.g.
1:3 or 5:6)"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf),
pp. 31–33. These are the categories a verifier should demand from the spec,
because the correct synchronizer differs for each.

**Partitioning.** The practitioner guideline is one clock per module: "Guideline:
Only allow one clock per module ... Reason: Static timing analysis and creating
synthesis scripts is more easily accomplished on single-clock modules ...
Exception: The top-level module that connects together the signals from all of
the different clock domains will naturally have all of the clocks as inputs"
[Cummings, *Clock Domain Crossing (CDC) Design & Verification Techniques Using SystemVerilog*, SNUG Boston 2008 (archived capture 2020-11-12)](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
**[industry paper]**, §6.3.

## 2. Metastability and synchronizers

### 2.1 The physics and the MTBF formula

All of §2.1 is from
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
**[primary]**, pp. 24–28, unless noted.

Metastability is indecision, not oscillation: "In flip-flops, metastability
means indecision as to whether the output should be 0 or 1" (p. 24), and "one
popular definition says that if the output of a flip-flop changes later than the
nominal clock-to-Q propagation delay [it was metastable]" (p. 24). The tutorial
is explicit that the folk picture is wrong: the claim that the two nodes "get
stuck in the middle and would eventually get out of there by some random
process ... should be taken lightly" (p. 27); probabilistically, "if a latch is
metastable at time zero, the probability it will remain metastable at time
t > 0 is e^(−t/τ), which diminishes exponentially fast" (p. 27).

*Entering.* "We can define a short window T_W around the clock's sampling edge
(sort of 'setup-and-hold time') such that if data changes during that window,
the latch could become metastable" (p. 25). If the data changes at rate F_D,
"the rate of entering metastability becomes Rate = F_D·F_C·T_W. For instance, if
F_C = 1 GHz, F_D = 100 MHz, and T_W = 20 ps, then Rate = 2,000,000 times/sec"
(p. 25).

*Failing.* "Failure means that a flip-flop became metastable after the clock's
sampling edge, and that it is still metastable S time later. The two events are
independent, so we can multiply their probabilities" (p. 28):

```
p(failure)      = p(enter MS) x p(time to exit > S) = T_W * F_C * e^(-S/tau)
Rate(failures)  = T_W * F_C * F_D * e^(-S/tau)

                    e^(S/tau)
MTBF          =  ---------------
                 T_W * F_C * F_D
```

Variables, as the source names them: **T_W** is the window around the sampling
edge inside which a data change can drive the latch metastable; **F_C** is the
clock (sampling) frequency; **F_D** is the rate at which the data input changes;
**S** is the synchronization (resolution) period allowed before the value is
sampled again; **τ** is the resolution time constant of the latch, estimated as
τ = C/g_m, where C is the capacitive load on the master-latch nodes and g_m the
inverter transconductance — "higher capacitive load on the master nodes and
lower inverter gain impede the resolution of metastability" (p. 27).

*Worked numbers, both directions.* For 28 nm high-performance CMOS with
τ = 10 ps, T_W = 20 ps, F_C = 1 GHz, data changing every ten clock cycles and
S = T_C, the tutorial obtains "4 × 10^29 years. (This figure should be quite safe
— the universe is believed to be only 10^10 years old.)" (p. 28). But at low
voltage and high temperature, with S = T_C, F_C = 1 GHz, F_D = 1 kHz,
τ = 100 ps and T_W = 200 ps, "the MTBF is about one minute. Three flip-flops ...
would increase the MTBF a bit, to about one month. But if we use four flip-flops,
S = 3·T_C and the MTBF jumps to 1,000 years" (p. 30). This pair of results is the
single most useful teaching fact in the note: the same two-flop structure is
either astronomically safe or fails in a minute depending on τ, T_W and S.

*Budgeting S.* "Actually, any logic and wire delays along the path from FF1 to
FF2 are subtracted from the resolution time: S = T_C − t_pCQ(FF1) − t_SETUP(FF2)
− t_PD(wire), and so on" (p. 28) — hence "the two flip-flops should be placed
near each other, or else the wire delay between them would detract from the
resolution time S. Missing this seemingly minor detail has made quite a few
synchronizers fail unexpectedly" (p. 29).

*System budget.* "MTBF decreases roughly linearly with the number of
synchronizers. Thus, if your system uses 1,000 synchronizers, you should be sure
to design each one for MBTF [sic] at least three orders of magnitude higher than
your reliability target for the entire system" (p. 30).

### 2.2 The two-flop synchronizer and its rules

The structure: "The first flip-flop samples the asynchronous input signal into
the new clock domain and waits for a full clock cycle to permit any metastability
on the stage-1 output signal to decay, then the stage-1 signal is sampled by the
same clock into a second stage flip-flop"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§3.2. What it buys: "The bottom line is that Q2 is never metastable (except,
maybe, once every MTBF years) ... The synchronization circuit exchanges the
'analog' uncertainty of metastability ... for a simpler 'digital' uncertainty ...
of whether the output switches one or two cycles later"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 29. Where two stages are not enough, "a third flop is added to increase the
MTBF"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§3.4.

The three rules the chapter states, each with its source:

1. **Register in the source domain — no combinational logic driving the
   crossing.** "the combinational output from the sending clock domain could
   experience combinational settling at the CDC boundary. This combinational
   settling effectively increases the data-change frequency potentially creating
   small bursts of oscillating data and thereby increasing the number of edges
   that could be sampled while changing"
   [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
   §3.5. The paper's own summary rule is "register the signal in the sending
   clock domain to remove combinational settling" (§8.1). Note the mechanism is
   the F_D term of the MTBF formula, not a separate effect.

2. **No fan-out from the first stage — one synchronizer per signal.** "Another
   forbidden practice is to synchronize the same asynchronous input by two
   different parallel synchronizers; one might resolve to 1 while the other
   resolves to 0, leading to an inconsistent state. In fact, that was the problem
   that grounded the J spacecraft"
   [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
   p. 30. See §5, row 2: this sources the *divergence* rule; the narrower
   statement "the first stage must not fan out to anything but the second stage"
   is a stricter, standard formulation not quoted verbatim in these sources
   (Litterick, below, gives the equivalent design rule: instantiate synchronizer
   modules so that "metastable nets are not abused").

3. **Single bit only.** See §2.3.

Litterick adds the assumption a verifier should check when nothing is known
about the two clocks: "If no assumptions are made about the relationship between
the source and destination clock domains ... input data values must be stable
for three destination clock edges"
[Litterick, *Pragmatic Simulation-Based Verification of Clock Domain Crossing Signals and Jitter using SystemVerilog Assertions*, Verilab & DVCon 2006 (archived capture 2018)](http://web.archive.org/web/2018id_/http://www.verilab.com/files/sva_cdc_paper_dvcon2006.pdf)
**[industry paper]**, §4.2 — the "three edge" idea also appears as Cummings'
§4.1.1 "three edge requirement".
