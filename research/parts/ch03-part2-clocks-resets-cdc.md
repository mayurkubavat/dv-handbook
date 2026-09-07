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

### 2.3 Multi-bit crossings and the correct structures

**Why per-bit synchronizers are wrong.** The primary statement:

> "Note that the synchronizer doesn't synchronize the data — rather, it
> synchronizes the control signals. Attempts to synchronize the data bit by bit
> usually lead to catastrophic results; even if all data lines toggle
> simultaneously, some bits might pass through after one cycle, while others
> might take two cycles because of metastability. Beware: that's a complete loss
> of data."
> — [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf) p. 30

The same failure stated structurally: "if some bits of a bus have separate
multi-flop synchronizers, it cannot be guaranteed that all these synchronizers
require a strictly identical latency to output a stable value"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.2.3
("Bus Incoherency"). And in control terms: "If both the load and enable signals
are driven on the same sending clock edge, there is a chance that a small skew
between the control signals could cause the two signals to be synchronized into
different clock cycles within the receiving clock domain. Under these
conditions, the data would not be loaded into the register"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§5.3. Cummings is blunt about the tempting fix: "Simply using synchronizers on
all of the CDC bits is not always good enough" (§5.2).

A related structural hazard, worth a callout because it survives correct
per-signal synchronization: **convergence**. "Whenever two signals converge on a
combinational gate, a transient inconsistent value (glitch) may appear. While on
a synchronous path, static timing analysis ensures that this glitch is resolved
within a clock period, in the context of a CDC, the glitch may be captured and
its value propagated ... To guarantee that a glitch cannot appear on this gate,
the two input signals should never toggle in the same cycle"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.2.2.

**The correct structures.** Cummings' taxonomy (§5.1) is three strategies, and
his summary (§8.2) is four bullets, verbatim:

> "Consolidate — first attempt to combine multiple signals into a 1-bit
> representation in the sending clock domain before synchronizing the signal
> into the receiving domain. Use Multi-Cycle Path (MCP) formulations to pass
> multiple signals across clock domains. Use FIFOs to pass multi-bit buses,
> either data or control buses. Use gray code counters."

- *Gray codes.* "Gray codes only allow one bit to change for each clock
  transition, eliminating the problem associated with trying to synchronize
  multiple changing CDC bits across a clock domain"
  [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
  §5.7.2; the code is Frank Gray's, US Patent 2,632,058 (1953), per the same
  paper's reference [4]. Gray coding is what the CDC checker can then assert:
  "Coherency: stable(DATA_CDC) or onehot(DATA_CDC xor prev(DATA_CDC))"
  [Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2.

- *MCP / data-with-valid ("MUX recirculation").* "An MCP formulation refers to
  sending unsynchronized data to a receiving clock domain paired with a
  synchronized control signal. The data and control signals are sent
  simultaneously allowing the data to setup on the inputs of the destination
  register while the control signal is synchronized for two receiving clock
  cycles before it arrives at the load input of the destination register" —
  and therefore "Because the unsynchronized data is passed and held stable for
  multiple clock cycles before being sampled, there is no danger that the sampled
  value will go metastable"
  [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
  §5.6. The checkable property is stability: "EN -> stable(DATA_CDC)"
  [Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2.

- *Handshake (req/ack).* "The sender sends req ..., req is synchronized by the
  top synchronization circuits, the receiver sends ack ..., ack is synchronized
  by the sender, and only then is the sender allowed to change req again. This
  round-trip handshake is the key to correct synchronization"
  [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
  p. 30. Cost: "It may take two cycles of the receiver clock to receive req, two
  more cycles of the sender clock to receive ack, and possibly one more on each
  side ... If req and ack must be lowered before new data can be transferred,
  consider another penalty of 3 + 3 cycles" (ibid.).

- *Asynchronous FIFO.* "The most common fast synchronizer uses a two-clock FIFO
  buffer ... the write pointer has to be synchronized with rclk (read clock) when
  compared ... That's where the synchronization is; it's applied to the pointers,
  rather than to the data ... Incidentally, the pointers are usually maintained
  in Gray code so that only a single bit at a time changes in the synchronizer"
  [Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
  p. 31. The practitioner reference design is
  [Cummings, *Simulation and Synthesis Techniques for Asynchronous FIFO Design*, SNUG San Jose 2002 (archived capture 2020)](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2002SJ_FIFO1.pdf)
  **[industry paper]**, which is also Ginosar's cited practical reference
  (his ref. 19). Cummings' own warning about FIFOs is the sharpest sentence in
  the paper: "Most incorrectly implemented FIFO designs still function properly
  90% of the time. Most almost-correct FIFO designs function properly 99%+ of the
  time" (§1.0).

- *1-deep / 2-register FIFO.* A cheap multi-bit crossing where "the gray code
  counters used to detect full and empty are simple toggle flip-flops"
  [Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
  §5.8.2.

Ginosar's caution for FIFO users is worth a Pitfall callout: "The key question
for the user of a library FIFO buffer is how large the RAM should be ... an FPGA
has occasionally failed in mission because of a too-short FIFO buffer"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 31.

### 2.4 Why simulation does not reproduce this class of bug

This is the chapter's motivating argument, so five independent sources are given.

1. **The direct statement.** "The issues are related to analogue effects in the
   real-world transistor-level circuits and do not typically manifest themselves
   in standard RTL simulation flows"
   [Litterick, DVCon 2006](http://web.archive.org/web/2018id_/http://www.verilab.com/files/sva_cdc_paper_dvcon2006.pdf)
   §1 **[industry paper]**.

2. **What the simulator does instead — with the mechanism.** Litterick's Figure 3
   walks three cases where zero-delay RTL simulation and silicon disagree, in
   *both* directions: "if the signal changes just before the clock edge (a
   setup-time violation) then the simulation will propagate the new value, but
   the real circuit might become metastable and decay to original low value";
   and for a two-cycle pulse, "the simulation will propagate a 2-clock wide pulse
   but the real circuit may filter it out completely" (§4.2). So RTL simulation
   is not merely optimistic; it is a *different* circuit.

3. **CDC jitter is invisible.** "Even when all signals are properly synchronized
   into the destination clock domain, the actual arrival time in real life is
   subject to uncertainty if the signal goes metastable in the first stage
   synchronizing flip-flop ... Normally this jitter would not show up on a
   simulation but must be considered to conclude the analysis" (§6, ibid.).

4. **The FIFO case, from the designer's side.** "Testing a FIFO design for subtle
   design problems is nearly impossible to do. The problem is rooted in the fact
   that FIFO pointers in an RTL simulation behave ideally, even though, if
   incorrectly implemented, they can cause catastrophic failures if used in a
   real design. In an RTL simulation, if binary-count FIFO pointers are included
   in the design all of the FIFO pointer bits will change simultaneously; there
   is no chance to observe synchronization and comparison problems"
   [Cummings, SNUG San Jose 2002](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2002SJ_FIFO1.pdf)
   §2.4. He adds that gate-level simulation only helps a little, and less as
   speeds rise: "the probability of detecting problems also diminishes" (ibid.).

5. **Peer-reviewed restatements.** "CDC issues are by nature very rare since they
   depend on physical timing constraints ... A simulation environment, even with
   good coverage, is then very likely to miss a glitch or metastability.
   Consequently, in the functional verification of CDC, using model checking
   prevails"
   [Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2. And,
   for CDC and RDC together: "We need to take precautions at the RTL level even
   though our simulator is unable to verify or observe these problems"
   [Sundriyal & Gupta, *Clock & Reset Domain Crossing Issues and Verification Techniques for SoC Design*, ASIANCON, 2024-08-23](https://doi.org/10.1109/ASIANCON62057.2024.10837784)
   **[research]** (abstract).

**What gate-level simulation shows, and why teams suppress it.** "Digital
simulation models typically generate X's when synchronizers recognize setup and
hold time violations on CDC signals. This can frequently cause gate-level
simulations to fail"; ASIC libraries "typically model flip-flops to drive X's
(unknowns) on the flip-flop outputs when a timing violation occurs ... These
X-values propagate to the rest of the design"
[Cummings SNUG 2008](http://web.archive.org/web/20201112023511id_/http://www.sunburst-design.com/papers/CummingsSNUG2008Boston_CDC.pdf)
§7.0–7.1. Section 7.2 then lists the standard countermeasures — turn off timing
checks, zero the setup/hold times, edit the flip-flop models, use multiple SDF
files — i.e. the industry's usual response is to *remove* the one signal a
simulator does give. This is a strong Pitfall for the chapter.

**What simulation can be made to do.** The accepted substitute is to replace the
synchronizer with a randomized-latency model: "we can facilitate logic
verification by replacing the synchronizer with a special synchronous delay block
that inserts a delay of either k or k + 1 cycles at random. Although this
approach leads to a design space of at least 2^n cases if there are n
synchronization circuits, it is still widely used and is effective in detecting
many logic errors (but not all of them — it wouldn't have helped the J spacecraft
designers, for instance)"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 33. Litterick's concrete RTL implementation of the same idea uses `randcase`
to pick between `$past(d_in)` and `d_in`, and between `m2` and `m3`, so that
"the jitter emulation can cause the d_out transition to randomly appear one clock
early ..., at the nominal position, or one clock late ... This circuit is also
capable of filtering one and two-clock wide pulses"
[Litterick, DVCon 2006](http://web.archive.org/web/2018id_/http://www.verilab.com/files/sva_cdc_paper_dvcon2006.pdf)
§6. Note the honest limit both authors state: this covers *logic* consequences of
jitter, not the metastability event itself.

## 3. Resets

The reference for §3.1–§3.3 is
[Cummings & Mills, *Asynchronous & Synchronous Reset Design Techniques — Part Deux*, SNUG Boston 2003, rev 1.3 (archived capture 2020)](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2003Boston_Resets.pdf)
**[industry paper]** unless noted.

### 3.1 Synchronous vs asynchronous

*Synchronous reset, what it costs and assumes.* "Synchronous reset logic will
synthesize to smaller flip-flops, particularly if the reset is gated with the
logic generating the d-input. But in such a case, the combinational logic gate
count grows, so the overall gate count savings may not be that significant"
(§4.2). The honest verdict on area in modern nodes, from the same paragraph: "in
today's technology of huge die sizes, the savings of a gate or two per flip-flop
is generally irrelevant". The real advantages are behavioral: "Synchronous resets
insure that reset can only occur at an active clock edge. The clock works as a
filter for small reset glitches" (§4.2), and where reset is generated internally,
"A synchronous reset is recommended for these types of designs because it will
filter the logic equation glitches between clocks" (§4.2).

Its environmental assumptions are the disadvantages: "Synchronous resets may need
a pulse stretcher to guarantee a reset pulse width wide enough to ensure reset is
present during an active edge of the clock" (§4.3); "By its very nature, a
synchronous reset will require a clock in order to reset the circuit ... if you
have a gated clock to save power, the clock may be disabled coincident with the
assertion of reset. Only an asynchronous reset will work in this situation"
(§4.3); and for internal tristate buses, "In order to prevent bus contention on
an internal tristate bus when a chip is powered up, the chip should have a
power-on asynchronous reset" (§4.3).

*Asynchronous reset.* "The biggest advantage to using asynchronous resets is
that, as long as the vendor library has asynchronously reset-able flip-flops, the
data path is guaranteed to be clean. Designs that are pushing the limit for data
path timing, can not afford to have added gates and additional net delays in the
data path" (§5.3); and "the circuit can be reset with or without a clock present"
(§5.3). The cost: "The biggest problem with asynchronous resets is that they are
asynchronous, both at the assertion and at the de-assertion of the reset. The
assertion is a non issue, the de-assertion is the issue. If the asynchronous
reset is released at or near the active clock edge of a flip-flop, the output of
the flip-flop could go metastable and thus the reset state of the ASIC could be
lost" (§5.4). Also: DFT — "if the asynchronous reset is not directly driven from
an I/O pin, then the reset net from the reset driver must be disabled for DFT
scanning and testing" (§5.4) — and timing: "The reset tree must be timed for both
synchronous and asynchronous resets to ensure that the release of the reset can
occur within one clock period" (§5.4).

*Recovery and removal.* "Reset recovery time refers to the time between when
reset is de-asserted and the time that the clock signal goes high again. The
Verilog-2001 Standard has three built-in commands to model and test recovery time
and signal removal timing checks: `$recovery`, `$removal` and `$recrem` (the
latter is a combination of recovery and removal timing checks)" (§6.1); "Recovery
time is also referred to as a t_su setup time of the form, 'PRE or CLR inactive
setup time before CLK↑'" (§6.1, crediting the TI *ALS/AS Logic Data Book*, 1986,
p. 2-78). The second, distinct hazard is skew: "When reset removal is
asynchronous to the rising clock edge, slight differences in propagation delays
in either or both the reset signal and the clock signal can cause some registers
or flip-flops to exit the reset state before others" (§6.2). *(The `$recovery` /
`$removal` / `$recrem` system timing checks are normative in IEEE Std 1364 and
carried into IEEE Std 1800 **[standard]**; the LRM itself is paywalled and was
not fetched — see §7.)*

### 3.2 Reset synchronizers and release ordering

The rule, in the paper's own capitals: "Guideline: EVERY ASIC USING AN
ASYNCHRONOUS RESET SHOULD INCLUDE A RESET SYNCHRONIZER CIRCUIT!! Without a reset
synchronizer, the usefulness of the asynchronous reset in the final system is
void even if the reset works during simulation" (§7.0).

Mechanism — asynchronous assert, synchronous de-assert: "An external reset signal
asynchronously resets a pair of master reset flip-flops, which in turn drive the
master reset signal asynchronously through the reset buffer tree ... Reset removal
is accomplished by de-asserting the reset signal, which then permits the d-input
of the first master reset flip-flop (which is tied high) to be clocked through a
reset synchronizer. It typically takes two rising clock edges after reset removal
to synchronize removal of the master reset" (§7.0). These flops must be kept off
the scan chain (§7.0).

A point worth a Pitfall, because it is a common misconception: the second stage
is *not* at risk. "The second flip-flop of the reset synchronizer is not subject
to recovery time metastability because the input and output of the flip-flop are
both low when reset is removed. There is no logic differential between the input
and output of the flip-flop so there is no chance that the output would oscillate"
(§7.1). And the assertion edge is never the problem: "There is no reset
metastability issue when reset is asserted because the reset signal bypasses the
clock signal in a flip-flop circuit to cleanly force the output low. The
metastability issue is always related to reset removal" (§7.3).

*Reset domains and ordering.* "For a multi-clock design, a separate asynchronous
reset synchronizer circuit and reset distribution tree should be used for each
clock domain. This is done to insure that reset signals can indeed be guaranteed
to meet the reset recovery time for each register in each clock domain ... The
problem is graceful removal of reset and synchronized startup of all logic after
reset is removed" (§11.0). Two legitimate schemes follow. Non-coordinated:
"exactly when reset is removed within one clock domain compared to when it is
removed in another clock domain is not important. Typically in these designs, any
control signals crossing clock boundaries are passed through some type of
request-acknowledge handshaking sequence" (§11.1). Sequenced: "For some
multi-clock designs, reset removal must be ordered ... only the highest priority
asynchronous reset synchronizer input is tied high. The other asynchronous reset
synchronizer inputs are tied to the master resets from higher priority clock
domains" (§11.2). Which of the two applies is a **specification** question, and
therefore a question the verifier must ask.

The reset trailing edge is a clock-domain crossing like any other: "The trailing
edge of the reset signal and of any asynchronous inputs to flip-flops are
typically synchronized to each clock domain in a chip"
[Ginosar 2011](https://webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf)
p. 30.

An open-source house convention that matches all of this, useful as a real-world
example: "Chip wide all resets are defined as active low and asynchronous. Thus
they are defined as tied to the asynchronous reset input of the associated
standard cell registers. The default name is `rst_n`. If they must be
distinguished by their clock, the clock name should be included in the reset name
like `rst_domain_n`"
[lowRISC Verilog Coding Style Guide, accessed 2026-09-07](https://raw.githubusercontent.com/lowRISC/style-guides/master/VerilogCodingStyle.md)
**[primary]** ("Resets"). The same guide requires clock names to carry the domain:
"If a module contains multiple clocks, the clocks that are not the system clock
should be named with a unique identifier, preceded by the `clk_` prefix ... Note
that this prefix will be used to identify other signals in that clock domain"
(ibid., "Clocks") — the same naming-as-metadata idea as Cummings §6.1.

### 3.3 Registers without a reset

The legitimate case named in the literature is the follower flip-flop: "a designer
should not mix resetable flip-flops with follower flip-flops (flops with no
resets) in the same procedural block or process. Follower flip-flops are
flip-flops that are simple data shift registers" (§3.1). Mixing them has a
concrete cost: in the bad-style example "the second stage is a follower flip-flop
and is not reset, but because the two flip-flops were inferred in the same
procedural block/process, the reset signal `rst_n` will be used as a data enable
for the second flop. This coding style will generate extraneous logic" (§3.1).

That reset-less sequential elements are numerous enough to be treated as a class
is confirmed, as a vendor statement, by the "Low-Noise Methodology" bullet "Skip
the reset-less sequential elements"
[Synopsys, VC SpyGlass RDC product page, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-rdc.html)
**[vendor]**. The broader engineering rationale the chapter will want — datapath
pipeline stages and storage arrays need no reset because their contents are
qualified by a valid bit or by a reset control path — is **not** directly quoted
in any source fetched here; see §5, row 4.

### 3.4 Reset-domain crossing

The definition, and the reason it is a distinct class:

> "A well known source of metastability is caused by clock domain crossings;
> however, asynchronous reset crossings within the same clock domain can also
> cause metastability."
> — [Synopsys VC SpyGlass RDC, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-rdc.html) **[vendor]**

That sentence is the crux: an RDC path can lie entirely **inside one clock
domain** — a flop reset by `rst_a_n` feeding a flop reset by `rst_b_n`, both on
`clk`. A structural analysis that enumerates crossings by comparing the *clocks*
of source and destination registers sees no crossing at all. The peer-reviewed
framing of the problem:

> "Reset architecture of a digital design can be quite complex. Typically, SoC
> designs have multiple sources of reset, such as power-on reset, hardware
> resets, debug resets, software resets, and watchdog timer reset. These multiple
> reset domains make the design potentially exposed to metastability issues, so
> the designer must perform the reset domain crossing (RDC) analysis and resolve
> any RDC issues in the early stages of designing. This can quite be challenging,
> because of the effort needed for this analysis and how noisy it can be."
> — [Fawzy, Elgohary & Ibrahim, *Noise Reduction in Reset Domain Crossings Verification Using Formal Verification*, IEEE EWDTS, 2020-09](https://doi.org/10.1109/EWDTS50664.2020.9224763) **[research]** (abstract)

Also peer-reviewed, and confirming that RDC is treated as its own RTL-quality
check alongside CDC: "The goal of this paper is to check for RTL Quality checks
such as CDC and RDC to ensure such faults do not occur at later stages of chip
development"
[Sundriyal & Gupta, ASIANCON, 2024-08-23](https://doi.org/10.1109/ASIANCON62057.2024.10837784)
**[research]**. A further peer-reviewed venue treatment, not fetched in full:
Yeung & Mandel, *Multi-Domain Verification of Power, Clock and Reset Domains*,
LNCS 9434 (HVC 2015), DOI
[10.1007/978-3-319-26287-1_15](https://doi.org/10.1007/978-3-319-26287-1_15)
**[research]** — see §7.

### 3.5 Reset tests that blocks usually lack

"Reset testing is a crucial element of functional sign-off for any chip", but
"There has been no standard method for making scoreboards, drivers and monitors
enter and exit reset states cleanly, or kill complex stimulus generation processes
gracefully; it is common to see reset testing that does not achieve self-checking
autonomy forcing engineers to rely on inefficient techniques such as visual
inspection"
[Hunter, Chen & Lipon, *Reset Testing Made Simple with UVM Phases*, SNUG 2013 (archived capture 2020)](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/HunterSNUGSV_UVM_Resets_paper.pdf)
**[industry paper]**, abstract. That paper is also the source for the four test
classes the chapter should name:

- **Idle reset.** "The simplest form of reset testing is idle testing. When all
  stimulus has drained out of the device, all scoreboards are quiet, and
  everything has quiesced, send the device back into reset and do it all over
  again ... the manner in which the DUT reacts should be highly predictable."
- **Active reset** (mid-traffic). "Applying a reset signal while stimulus traffic
  is flying throughout the DUT is also fairly straightforward ... The complexity
  lies in how each UVM component reacts to reset."
- **Soft reset** (partial). "typically it involves register writes that are meant
  to clear the device under test in some way ... Perhaps packets that are in
  flight continue to their completion; or interrupts continue to be serviced; or
  state machines are forced to idle but buffers are not emptied. There are so many
  ways that a soft reset might differentiate itself from a hard reset that it is
  impossible to provide a foolproof design pattern for all occasions."
- **Multi-domain reset.** "Just as the RTL can have multiple reset domains, so too
  can testbench components. By establishing different domains and assigning them
  to different components, you can jump one domain's phases without changing
  others."

Reset with the clock stopped is sourced indirectly, from the design side: a
gated clock "may be disabled coincident with the assertion of reset. Only an
asynchronous reset will work in this situation, as the reset might be removed
prior to the resumption of the clock"
[Cummings & Mills, SNUG Boston 2003](http://web.archive.org/web/2020id_/http://www.sunburst-design.com/papers/CummingsSNUG2003Boston_Resets.pdf)
§4.3 — i.e. the clock-stopped case is a real design scenario, so it is a real test
scenario; but no source fetched here states "test reset with the clock stopped" as
a testbench guideline (see §5, row 5).

Two testbench guidelines the chapter can quote directly. First: "In a simulation,
if reset is removed on a posedge clock, there is usually no guarantee what the
simulation result will be. Even if the RTL code behaves as expected, the
gate-level simulation may behave differently due to event scheduling race
conditions and different IEEE-Verilog compliant simulators may even yield
different RTL simulation results ... Guideline: In general, change the testbench
reset signal on the inactive clock edge using blocking assignments" (§7.4).
Second, on time-zero initialization: "making the first testbench assignment to
reset using a nonblocking assignment ... forces all procedural blocks to become
active before the reset signal is asserted, which means all reset-sensitive
procedural blocks are guaranteed to trigger at time 0 (no Verilog race issues)"
(§7.4). Note the tension the chapter should flag: this guideline deliberately
keeps the testbench *away* from the recovery-time corner, which is exactly the
corner that fails in silicon — one more reason the bug is not a simulation bug.

## 4. What a static tool can and cannot decide

**What is structurally easy.** "From a netlist design, it is fairly easy to
structurally detect two registers receiving different clocks, and even to detect
a multi-flop"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.1
**[research]**. That is the whole of what an RTL-only derivation can honestly
claim.

**Where structural recognition breaks down.** "In contrast, for complex FIFO
protocols, identifying the correct control logic is non-trivial. If a single
synchronizer structure was used, it could be stored in a pattern library and
identified by a proper pattern matching. Unfortunately, in industry, many
designers create their own synchronizing structures, and the structural library
used for pattern matching would never be exhaustive on complex structures such as
FIFOs" (ibid.). And the decisive limit: "a structural approach cannot check
protocols and assumptions on the control signal. A functional check must then be
run" (ibid.). Industrial tools bridge this by generating formal properties from
recognized patterns — coherency (Gray one-hot) and stability (enable implies
stable data), quoted in §2.3 above — "In practice, most industrial CDC tools
reuse structural information to run functional checks" (§1.3.2).

**Constraints are not derivable from RTL.** This is the point the chapter's own
tool must concede. "reusing predefined modules, designers do not know the exact
clock configuration components. Thus, they typically miss some assumptions on
configuration signals. As a consequence, the design is verified in a pessimistic
mixed-mode, where controls toggle incoherently and unrealistically. With this
incomplete setup, protocols may behave spuriously, leading to worthless
verification results. The verification of protocols then requires a realistic and
complete clock setup"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §3.1.1. He
quantifies the cost on one FIFO overflow property: with the clock-gate enables
constrained, "a model checker takes 13 seconds to guarantee that the FIFO cannot
overflow"; with the assumption removed, "The same overflow property now takes 192
seconds to be proven (15 times more)" — and "When we consider that modern designs
include thousands of clock-gating structures along with complex clock switching,
running formal checks with an incomplete setup sounds intractable" (ibid.). His
own contribution explicitly targets "verification of so-called generated clocks in
the Synopsys Design Constraints (SDC) format" (§3.5), i.e. the clock declarations
come from outside the RTL.

The corollary for the chapter's tool: **domains derived from RTL alone give you
the crossing list, not the sign-off.** They cannot tell you which mode the chip
is in, which mux select is constant in mission mode, which of two clocks are
declared asynchronous, or what the intended ratio is. Say so.

**Vendor claims (labelled, not adopted).** A commercial CDC product page claims
"Comprehensive CDC analysis using formal and simulation-based solutions",
"Support for UPF and SDC based CDC analysis", "Synchronizers and auto-detection
of quasi-static signals for lower false violations", "Protocol-Independent
Analysis", and "VC SpyGlass CDC correlates control and data signals resulting in
a good understanding of the design intent for the lowest possible noise"
[Synopsys, VC SpyGlass CDC product page, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-cdc.html)
**[vendor]**. The corresponding RDC page claims coverage of "intricate reset
relationships, reset to clock relationships, RDC qualifiers", a "Low-Noise
Methodology" that skips "the reset-less sequential elements", and "SDC support for
RDC analysis" and "Constraints-Driven CDC and RDC Verification Including UPF Aware
Analysis"
[Synopsys, VC SpyGlass RDC product page, accessed 2026-09-07](https://www.synopsys.com/verification/static-and-formal-verification/vc-spyglass/vc-spyglass-rdc.html)
**[vendor]**. These are marketing statements, not measurements; the chapter must
present them as claims. Their evidentiary value here is narrow but real: two
independent product pages both foreground *noise* and *false violations* as the
thing they compete on, and both list SDC/UPF constraint input as a required
feature — corroborating Plassan on constraints and Fawzy et al. on noise.

**The noise problem, from a peer-reviewed source.** "the designer must perform
the reset domain crossing (RDC) analysis and resolve any RDC issues in the early
stages of designing. This can quite be challenging, because of the effort needed
for this analysis and how noisy it can be. In this paper, we present some of the
challenges in the existing methodology for RDC analysis and propose a new
methodology to reduce RDC results noisiness and achieve more accurate results.
This leads to faster verification closure"
[Fawzy, Elgohary & Ibrahim, EWDTS, 2020-09](https://doi.org/10.1109/EWDTS50664.2020.9224763)
**[research]** (abstract). On the CDC side, the equivalent statement is about
false violations from metastability-injection flows: "This approach, however
correct, combines a pessimistic random generation of X-value, and an
over-approximating ternary execution. Many false violations are then expected to
be reported by this methodology"
[Plassan 2018](https://theses.hal.science/tel-01870205/document) §1.3.2.

**I could not source a published waiver *count*.** No paper reachable in this
session gives a number for waivers per design or a percentage of CDC violations
waived. Do not assert one — see §5, row 6, and §7.

## 5. Commonly repeated but unsourced claims

| Claim | Where it is repeated | Status |
|---|---|---|
| "A gated clock is not a new clock domain, but a muxed clock may be." | Design lore; CDC training material | **Inference, not quoted.** Follows from Plassan's gating vs selection definitions (§1) but no source states it. Present as the book's reasoning, or drop the aphorism and give the definitions. |
| "No fan-out from the first synchronizer stage." | Universal coding rule; lint rules | **Partly sourced.** Ginosar (p. 30) forbids *two parallel synchronizers on the same input* (divergence). The narrower "stage-1 Q may feed only stage-2" is standard but not quoted in any source fetched here. |
| "Two flip-flops give an adequate MTBF." | Very widely | **Sourced but conditional.** Ginosar shows the same structure giving 4x10^29 years and ~1 minute depending on tau, T_W, S (§2.1). Never state it unconditionally. |
| "Datapath pipeline stages and RAM/register arrays legitimately have no reset." | Design guidelines | **Not sourced.** Only the follower-flip-flop case is quoted (Cummings §3.1) plus a vendor bullet acknowledging reset-less elements exist. Needs a further source before the chapter asserts the general rule. |
| "Blocks are rarely tested with reset asserted mid-traffic, with the clock stopped, or with partial reset." | Verification folklore | **Half-sourced.** Hunter et al. name idle/active/soft/multi-domain reset testing and say reset testing often lacks self-checking autonomy; nobody fetched here measures how many blocks skip these, and no source gives a clock-stopped reset test guideline. |
| "CDC sign-off produces thousands of violations, most of them waived." | Conference hallways, tool marketing | **Not sourced numerically.** Noise/false-violation *existence* is sourced (Fawzy et al.; Plassan; two vendor pages). No count was found. Do not put a number in the chapter. |
| "Reset removal must be synchronized to every clock domain separately." | Reset design lore | **Sourced.** Cummings & Mills §11.0, verbatim. |
| "RTL simulation cannot reproduce an unsynchronized CDC." | The chapter's motivating argument | **Sourced five ways** (§2.4). Phrase it as "does not model metastability, and diverges from silicon in both directions", not "always misses it" — Litterick's Figure 3 shows simulation can also propagate values silicon would filter. |

## 6. Suggested BibTeX keys

| Key | Citation | Used by |
|---|---|---|
| `ginosar2011metastability` | R. Ginosar, "Metastability and Synchronizers: A Tutorial," *IEEE Design & Test of Computers*, vol. 28, no. 5, Sept/Oct 2011, pp. 23–35. DOI 10.1109/MDT.2011.113. PDF: webee.technion.ac.il/~ran/papers/Metastability-and-Synchronizers.IEEEDToct2011.pdf (accessed 2026-09-07). | §1, §2.1–§2.4, §3.2 |
| `ginosar2003fourteen` | R. Ginosar, "Fourteen Ways to Fool Your Synchronizer," *Proc. 9th IEEE Int'l Symp. Asynchronous Circuits and Systems (ASYNC 03)*, IEEE CS Press, 2003, pp. 89–96. DOI 10.1109/ASYNC.2003.1199169. | §2.2 (cite only; full text not obtained — see §7) |
| `cummings2008cdc` | C. E. Cummings, "Clock Domain Crossing (CDC) Design & Verification Techniques Using SystemVerilog," SNUG Boston, 2008, rev 1.0. | §1, §2.1–§2.4 |
| `cummings2002fifo` | C. E. Cummings, "Simulation and Synthesis Techniques for Asynchronous FIFO Design," SNUG San Jose, 2002, rev 1.2. | §2.3, §2.4 |
| `cummings2003resets` | C. E. Cummings and D. Mills, "Asynchronous & Synchronous Reset Design Techniques — Part Deux," SNUG Boston, 2003, rev 1.3. | §3.1–§3.3, §3.5 |
| `litterick2006cdcsva` | M. Litterick, "Pragmatic Simulation-Based Verification of Clock Domain Crossing Signals and Jitter using SystemVerilog Assertions," DVCon, 2006. | §2.2, §2.4 |
| `hunter2013resettesting` | B. Hunter, B. Chen (Cavium) and R. Lipon (Synopsys), "Reset Testing Made Simple with UVM Phases," SNUG, 2013. | §3.5 |
| `plassan2018cdc` | G. Plassan, "Conclusive formal verification of clock domain crossing properties," PhD thesis, Université Grenoble Alpes, 2018. HAL tel-01870205. | §1, §2.3, §2.4, §4 |
| `fawzy2020rdcnoise` | M. Fawzy, A. Elgohary and H. Ibrahim, "Noise Reduction in Reset Domain Crossings Verification Using Formal Verification," *IEEE East-West Design & Test Symposium (EWDTS)*, 2020. DOI 10.1109/EWDTS50664.2020.9224763. | §3.4, §4 |
| `sundriyal2024cdcrdc` | A. Sundriyal and V. Gupta, "Clock & Reset Domain Crossing Issues and Verification Techniques for SoC Design," *4th Asian Conf. on Innovation in Technology (ASIANCON)*, 2024. DOI 10.1109/ASIANCON62057.2024.10837784. | §2.4, §3.4 |
| `yeung2015multidomain` | P. Yeung and E. Mandel, "Multi-Domain Verification of Power, Clock and Reset Domains," *LNCS* 9434 (HVC 2015), Springer. DOI 10.1007/978-3-319-26287-1_15. | §3.4 (metadata only — see §7) |
| `lowrisc-verilog-style` | lowRISC, *Verilog Coding Style Guide*, GitHub `lowRISC/style-guides`, accessed 2026-09-07. | §3.2 |
| `dally1998digital` | W. J. Dally and J. W. Poulton, *Digital Systems Engineering*, Cambridge University Press, 1998. | §2.1 (Cummings' MTBF and synchronizer definitions come from here; the book itself was not consulted — see §7) |
| `ieee1800` | IEEE Std 1800, *IEEE Standard for SystemVerilog*, IEEE. | §3.1 ($recovery/$removal/$recrem — not fetched) |
| `synopsys-vcspyglass-cdc` / `synopsys-vcspyglass-rdc` | Synopsys VC SpyGlass CDC and RDC product pages, accessed 2026-09-07. **Vendor.** | §4 |

## 7. Confidence notes and gaps

**High confidence.** The MTBF formula and every variable in it, the two worked
numeric cases, the multi-bit prohibition, the four correct multi-bit structures,
the reset-synchronizer mechanism, recovery/removal definitions, per-domain reset
synchronizers, and the four reset-test classes. All are verbatim from primary or
practitioner sources read in full.

**The motivating claim is safe, with one wording caution.** "An unsynchronized CDC
is a bug that ordinary RTL simulation cannot reliably reproduce" is supported by
Litterick (analogue effects "do not typically manifest themselves in standard RTL
simulation flows"), Cummings 2002 (RTL FIFO pointers "behave ideally"), Plassan
("very likely to miss a glitch or metastability"), Sundriyal & Gupta ("our
simulator is unable to verify or observe these problems"), and Ginosar (the
random k / k+1 delay substitute is "effective in detecting many logic errors (but
not all of them)"). Caution: do **not** write "simulation always passes a broken
crossing". Litterick's Figure 3 shows simulation diverging from silicon in both
directions — it can also propagate a pulse the real circuit filters away.

**Gaps the chapter must not paper over.**

1. **No waiver or false-positive *numbers*.** Noise is sourced qualitatively only.
   If the chapter wants "CDC sign-off is dominated by waivers", it needs a fresh
   source — likely a DVCon paper behind a proceedings site that was unreachable
   here. State the problem qualitatively or cite nothing.
2. **Ginosar's ASYNC 2003 "Fourteen Ways" was not obtained.** Every reachable copy
   404s and web.archive.org is not fetchable through the standard fetch path
   (it was reachable only via `curl` for other files). The DOI is verified via
   Crossref; nothing is quoted from it. If the chapter wants its taxonomy of
   synchronizer mistakes, someone must obtain the paper. The 2011 tutorial covers
   the same ground and is quoted here instead.
3. **RDC rests on a thinner evidence base than CDC.** The clean definitional
   sentence ("asynchronous reset crossings within the same clock domain can also
   cause metastability") is **vendor**. The peer-reviewed sources (Fawzy et al.;
   Sundriyal & Gupta) confirm RDC exists, matters and is noisy, but the abstracts
   are all that was obtained; neither full text was read. Yeung & Mandel (HVC
   2015) is the most promising academic treatment and was not obtained at all.
   The chapter's explanation of *why* CDC tools miss RDC (the path can lie inside
   a single clock domain, so a clock-comparison structural analysis finds no
   crossing) is the book's own reasoning built on the vendor sentence — flag it
   as such or get the Yeung & Mandel paper.
4. **Standards not fetched.** IEEE Std 1800 / 1364 for `$recovery`, `$removal`,
   `$recrem` are paywalled; the definitions here are Cummings' restatement of
   Verilog-2001. Dally & Poulton (1998) is the ultimate source of the
   synchronizer definition and MTBF analysis Cummings leans on, and was not
   consulted; Ginosar's formula is used instead and is self-contained.
5. **`sunburst-design.com` is effectively gone.** Cite the archive URLs. If the
   book prefers live links, the redirect target requires registration, which is
   worse for readers.
