#!/usr/bin/env python3
"""Generate the eleven block diagrams of Chapter 34 (ch34-*.svg).

Every figure uses the shared language in blocks.py: model (rounded, blue),
tool (rectangle), evidence store (cylinder), human gate (diamond); solid
arrows carry data, dashed arrows carry a judgment.

Layout rule: page-width figures are at most 1000 px wide so that their type
prints at 7 pt or larger in the 7 x 10 in trim; the three wide ones (flow,
delegation, swim-lane) are placed sideways on a full page by the chapter.

    python3 figures/gen_ch34_figures.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from blocks import Diagram, BLUE, DIM, AMBER, GREEN, VIOLET, INK, GROUND, TRACE, SANS


def fig_model():
    d = Diagram(1000, 840, "The generative model beside a constrained-random generator")
    d.region(20, 20, 960, 380, "A generative model")
    ctx = d.store(50, 120, "Context", w=200, sub="prompt + tokens so far")
    m = d.model(310, 120, "Model", w=240, sub="next-token distribution")
    smp = d.tool(610, 120, "Sampler", w=200, sub="temperature, seed")
    out = d.store(610, 270, "Output", w=200, sub="one token")
    d.arrow(ctx, m); d.arrow(m, smp, label="P(next token)"); d.arrow(smp, out)
    d.arrow(out, ctx, label="append and repeat", sides=("l", "b"), bend=(-80, 70))
    d.caption(50, 372, "Fluent by construction; correct only where data and prompt make it so;\ndifferent on every run unless the seed is fixed.", size=15)
    d.region(20, 420, 960, 380, "A constrained-random generator")
    cons = d.store(50, 520, "Constraints", w=200, sub="the legal space")
    slv = d.tool(310, 520, "Solver", w=240, sub="picks a point")
    smp2 = d.tool(610, 520, "Sampler", w=200, sub="seed")
    st = d.store(610, 670, "Stimulus", w=200, sub="one transaction")
    d.arrow(cons, slv); d.arrow(slv, smp2); d.arrow(smp2, st)
    d.arrow(st, cons, label="next transaction", sides=("l", "b"), bend=(-80, 70))
    d.caption(50, 772, "Same shape: a space, a sampler, a seed. The prompt is the constraint set.", size=15)
    d.legend(40, 812); d.save("ch34-model.svg")


def fig_prompt():
    d = Diagram(1000, 820, "Prompt anatomy, the instruction file, and the verification plan")
    d.region(20, 20, 960, 420, "The parts of a prompt")
    parts = ["Instruction\nwhat to do", "Examples\nwhat good looks like", "Constraints\nwhat not to do", "Output format\nwhat shape to return"]
    boxes = [d.store(50 + i*232, 90, p, w=210, h=80) for i, p in enumerate(parts)]
    asm = d.tool(300, 250, "Assembled prompt", w=270, sub="one call's context")
    for b in boxes: d.arrow(b, asm, sides=("b", "t"))
    m = d.model(650, 250, "Model", w=200)
    d.arrow(asm, m)
    inst = d.store(50, 330, "Instruction file", w=210, h=76, sub="versioned, checked in")
    d.arrow(inst, boxes[0], label="feeds every call", sides=("t", "b"))
    d.caption(300, 400, "A prompt is a specification, with a specification's problems:\nambiguity, omission, the reader's assumptions.", size=15)
    d.region(20, 460, 960, 340, "The verification counterpart")
    plan = d.store(50, 540, "Verification plan", w=260, h=80, sub="machine-readable, versioned")
    tb = d.tool(400, 540, "Testbench", w=260, h=80, sub="stimulus, checker, coverage")
    reg = d.tool(750, 540, "Regression", w=200, h=80)
    d.arrow(plan, tb, label="what to verify, how,\nand when done", label_dy=-28); d.arrow(tb, reg)
    d.arrow(reg, plan, label="results reported against the plan", kind="judgment", sides=("b", "b"), bend=(0, 110), label_dy=30)
    d.caption(50, 770, "The plan is the testbench's instruction file.", size=15)
    d.save("ch34-prompt.svg")


def fig_grounding():
    d = Diagram(1000, 760, "Grounding: sources, the context assembler, and the model")
    d.region(20, 20, 300, 480, "Grounding sources (read-only)")
    srcs = [d.store(45, 70 + i*82, n, w=250, h=64) for i, n in enumerate(["Specification", "Verification plan", "RTL", "Logs and waveforms", "Regression history"])]
    asm = d.tool(400, 200, "Context assembler", w=260, h=120, sub="the design decision")
    d.parts.append(f'<rect x="400" y="200" width="260" height="120" rx="6" fill="none" stroke="{AMBER}" stroke-width="3"/>')
    for s in srcs: d.arrow(s, asm, sides=("r", "l"))
    d.note(400, 40, "Retrieval: fetch passages by\nsimilarity, paste them in.", w=260)
    d.note(400, 360, "Search: let the model look through\nthe repository as an engineer would.", w=260)
    m = d.model(730, 215, "Model", w=240, sub="sees only its context")
    d.arrow(asm, m, label="what fits,\nnothing else", label_dy=-30)
    out = d.store(730, 380, "Answer, code, plan", w=240, h=70)
    d.arrow(m, out, sides=("b", "t"))
    d.note(40, 530, "Nominal window: very large. Effective attention: much smaller.\nWhat is included matters more than how much.", w=930)
    d.caption(40, 640, "Nothing outside the context exists for the model. It produces a plausible\nsubstitute for whatever it was not given.", size=15)
    d.save("ch34-grounding.svg")


def fig_tools():
    d = Diagram(1000, 900, "Tool use: model, harness, tool server, sandbox")
    m = d.model(80, 60, "Model", w=220, sub="emits a request")
    h = d.tool(80, 220, "Harness", w=220, sub="runs it, returns result")
    d.arrow(m, h, sides=("b", "t"), label="tool request\n(name, arguments)", label_dy=-26)
    d.arrow(h, m, sides=("l", "l"), bend=(-60, 0), label="result", label_dy=0)
    d.region(320, 20, 660, 520, "Sandbox: a place the agent can break")
    ts = d.tool(350, 80, "Tool server", w=260, h=76, sub="advertises name, schema")
    d.arrow(h, ts, label="call", sides=("r", "l"), bend=(0, -60))
    sim = d.tool(680, 60, "Simulator", w=270, h=64, sub="compile, run seed, coverage")
    fe = d.tool(680, 150, "Formal engine", w=270, h=64, sub="prove, refute, vacuity")
    cov = d.store(680, 240, "Coverage DB", w=270, h=64)
    wav = d.store(680, 330, "Waveforms, logs", w=270, h=64)
    for t in (sim, fe, cov, wav): d.arrow(ts, t)
    d.note(350, 200, "Exposed: compile, run with a seed,\nfetch coverage, fetch failures,\nfetch a waveform slice.", w=300)
    d.note(350, 330, "Never exposed to a stimulus agent:\nthe checker's source, the coverage\nmodel, the reference model.", w=300)
    d.note(350, 450, "A simulation is an expensive tool call.\nThe loop is designed around that cost.", w=600)
    d.region(20, 570, 960, 300, "Verification counterpart: this book's build system is already a tool interface")
    mk = d.tool(60, 650, "make lint | run | clean", w=360, h=76, sub="three uniform targets")
    st = d.store(540, 650, "examples/status.json", w=380, h=76, sub="pass, fail, expect")
    d.arrow(mk, st, label="writes")
    d.caption(60, 800, "A harness that calls these two has everything a stimulus agent needs, and nothing it must not have.", size=15)
    d.save("ch34-tools.svg")


def fig_loop():
    d = Diagram(1000, 900, "The agent loop with its four failure points, beside the coverage-driven loop")
    d.region(20, 20, 960, 420, "The agent loop")
    pl = d.model(60, 80, "Plan", w=220, sub="what to do next")
    ac = d.tool(640, 80, "Act", w=220, sub="a tool call")
    ob = d.store(640, 250, "Observe", w=220, sub="the result")
    de = d.model(60, 250, "Stop?", w=220, sub="decide")
    d.arrow(pl, ac); d.arrow(ac, ob, sides=("b", "t")); d.arrow(ob, de); d.arrow(de, pl, sides=("t", "b"), label="no: loop")
    d.failure_mark(170, 150, 1); d.failure_mark(750, 150, 2); d.failure_mark(460, 300, 3); d.failure_mark(170, 320, 4)
    d.note(60, 350, "1 wrong plan  ·  2 wrong tool call  ·  3 misread result  ·  4 wrong stopping decision (the one that matters most)", w=890)
    d.region(20, 460, 960, 420, "The coverage-driven loop")
    ws = d.tool(60, 520, "Write stimulus", w=220, h=64)
    rn = d.tool(640, 520, "Run", w=220, h=64, sub="simulator")
    cr = d.store(640, 690, "Coverage report", w=220, h=64)
    en = d.model(60, 690, "Enough?", w=220, h=64, sub="stopping signal")
    d.arrow(ws, rn); d.arrow(rn, cr, sides=("b", "t")); d.arrow(cr, en); d.arrow(en, ws, sides=("t", "b"), label="no: another test")
    d.note(60, 790, "The stopping signal is coverage. The goal is bugs found. They are not the same,\nwhich is why coverage is a proxy the discipline learned not to trust.", w=890)
    d.save("ch34-loop.svg")


def fig_evaluation():
    d = Diagram(1000, 640, "Visible and hidden metrics, and the gap between them")
    g = d.model(40, 200, "Generator", w=230, sub="optimizes what it sees")
    art = d.store(330, 200, "Artifact", w=200, sub="code, test, stimulus")
    d.arrow(g, art)
    vis = d.tool(620, 60, "Visible metric", w=260, h=80, sub="the tests it can see")
    hid = d.tool(620, 340, "Hidden metric", w=260, h=80, sub="held-out tests, mutants")
    d.arrow(art, vis, kind="judgment", sides=("r", "l")); d.arrow(art, hid, kind="judgment", sides=("r", "l"))
    d.label(640, 175, "satisfied", 18, GREEN, "700"); d.label(640, 455, "not satisfied", 18, AMBER, "700")
    d.parts.append(f'<path d="M760,150 V335" stroke="{AMBER}" stroke-width="3" stroke-dasharray="8 6"/>')
    d.label(780, 235, "the gap: what the generator was\noptimized against, versus what\nmattered", 15, INK)
    d.region(20, 500, 960, 120, "Verification counterpart", stroke=BLUE)
    d.label(40, 555, "Visible: coverage (a proxy).   Hidden: bug-finding power (mutants killed).\nMeasured on small designs: coverage near 90 percent; fault detection near 14 percent.", 15, INK)
    d.save("ch34-evaluation.svg")


def fig_separation():
    d = Diagram(1100, 860, "Separation of generator and judge")
    d.region(110, 20, 960, 250, "Stimulus context", stroke=BLUE)
    sa = d.model(140, 80, "Stimulus agent", w=250, sub="writes tests, sequences")
    stim = d.store(450, 80, "Stimulus", w=220, sub="tests, constraints")
    d.arrow(sa, stim)
    d.note(710, 70, "May read: specification, plan,\nRTL, coverage report, failures.\nMay write: stimulus only.", w=340)
    d.parts.append(f'<rect x="120" y="280" width="940" height="52" fill="{GROUND}" stroke="{AMBER}" stroke-width="3"/>')
    d.label(590, 312, "no write access across this line: enforced by the harness and the repository, never by the prompt", 16, "#6B4A0E", "700", anchor="middle")
    d.region(110, 340, 960, 250, "Oracle context", stroke=VIOLET)
    oa = d.model(140, 400, "Checker author", w=250, sub="human, or a separate agent")
    orc = d.store(450, 400, "Oracle", w=220, h=76, sub="checker, reference model,\nassertions, coverage model")
    d.arrow(oa, orc)
    d.note(710, 390, "Written from the specification,\nwith the stimulus closed.\nApproved at a human gate.", w=340)
    tc = d.tool(250, 680, "Toolchain: simulator, formal engine, coverage database", w=600, h=70, sub="the only judge")
    # data into the judge: stimulus travels down the right margin, oracle straight down
    d.arrow(stim, tc, sides=("r", "r"), bend=(400, 60))
    d.arrow(orc, tc, sides=("b", "t"))
    # judgments back out along the left margin, outside both regions
    d.arrow(tc, sa, kind="judgment", sides=("l", "l"), bend=(-320, 0), label="pass, fail, coverage", label_dy=-160)
    d.arrow(tc, oa, kind="judgment", sides=("l", "l"), bend=(-200, 0), label="proven, refuted,\nvacuous", label_dy=40)
    d.caption(130, 830, "Whatever generates must not own what judges.", size=15)
    d.save("ch34-separation.svg")


def fig_multiagent():
    d = Diagram(1000, 720, "A multi-agent flow and the path of a propagating wrong belief")
    orch = d.model(370, 40, "Orchestrator", w=260, sub="plans, delegates, believes")
    wa = d.model(40, 230, "Worker A", w=220, sub="stimulus")
    wb = d.model(390, 230, "Worker B", w=220, sub="coverage analysis")
    wc = d.model(740, 230, "Worker C", w=220, sub="verifier")
    for w in (wa, wb, wc): d.arrow(orch, w, sides=("b", "t"))
    d.parts.append(f'<path d="M150,230 Q250,100 380,80" fill="none" stroke="{AMBER}" stroke-width="4" stroke-dasharray="10 6" marker-end="url(#ah)"/>')
    d.parts.append(f'<path d="M520,104 Q540,170 520,230" fill="none" stroke="{AMBER}" stroke-width="4" stroke-dasharray="10 6" marker-end="url(#ah)"/>')
    d.label(150, 130, "'done, all passing'", 15, AMBER, "700"); d.label(560, 175, "'A says done;\nanalyze'", 15, AMBER, "700")
    shared = d.store(230, 420, "Shared prompt and summaries", w=360, h=70, sub="what every agent was told")
    ind = d.store(620, 420, "Independent evidence", w=360, h=70, sub="simulator output, formal verdict")
    d.arrow(shared, wb, sides=("t", "b")); d.arrow(ind, wc, sides=("t", "b"), kind="judgment", label="what A did not hold", label_dy=-30)
    d.note(40, 540, "A verifier that shares the generator's evidence agrees with it. A verifier helps only when\nit holds evidence the generator does not: the toolchain's verdict, never a second reading\nof the same prompt.", w=930)
    d.caption(40, 690, "Counterpart: designer, verifier, formal engineer, sign-off reviewer, valued for their independence.", size=15)
    d.save("ch34-multiagent.svg")


def fig_flow(delegation=False):
    name = "ch34-delegation.svg" if delegation else "ch34-flow.svg"
    d = Diagram(1600, 1000, "The agentic verification flow with three human gates" if not delegation else "The delegation boundary on the agentic flow")
    d.region(20, 20, 1560, 120, "Grounding sources (read-only)")
    spec = d.store(60, 55, "Specification", w=220, h=64); plan = d.store(420, 55, "Verification plan", w=220, h=64, sub="as code")
    rtl = d.store(780, 55, "RTL", w=220, h=64); logs = d.store(1140, 55, "Logs, history", w=300, h=64)
    pl = d.model(660, 180, "Planner", w=260, sub="task graph, never code")
    for s in (spec, plan, rtl): d.arrow(s, pl, sides=("b", "t"))
    g1 = d.gate(700, 275, "Gate 1\nplan approval", w=180, h=76)
    d.arrow(pl, g1, sides=("b", "t"))
    d.region(20, 380, 1560, 200, "Agent roles, each in an isolated context")
    roles = {}
    for i, (n, sub) in enumerate([("Stimulus", "tests, sequences"), ("Checker", "scoreboards, SVA"), ("Coverage\nanalyst", "gaps, model"),
                                  ("Debug", "ranked hypotheses"), ("Formal", "prove, reject vacuous"), ("Reviewer", "mutants, held-out")]):
        roles[n] = d.model(50 + i*258, 430, n, w=220, h=76, sub=sub)
    for n in roles: d.arrow(g1, roles[n], sides=("b", "t"))
    g2 = d.gate(1000, 600, "Gate 2\noracle approval", w=190, h=80)
    d.arrow(roles["Checker"], g2, sides=("b", "t"), bend=(120, 0)); d.arrow(roles["Coverage\nanalyst"], g2, sides=("b", "t"), bend=(60, 0))
    d.arrow(roles["Formal"], g2, kind="judgment", sides=("b", "t"), label="proven, refuted, vacuous")
    d.region(20, 700, 1560, 130, "Tool layer, sandboxed")
    tools = {}
    for i, (n, sub) in enumerate([("Simulator", ""), ("Coverage DB", ""), ("Waveform", ""), ("Formal engine", ""), ("Lint", ""), ("Repository", "worktree per agent")]):
        tools[n] = d.tool(50 + i*258, 740, n, w=220, h=64, sub=sub or None)
    d.arrow(roles["Stimulus"], tools["Simulator"], sides=("b", "t")); d.arrow(roles["Stimulus"], tools["Lint"], sides=("b", "t"), bend=(200, -60))
    d.arrow(tools["Simulator"], tools["Coverage DB"]); d.arrow(tools["Coverage DB"], roles["Coverage\nanalyst"], sides=("t", "b"), kind="judgment")
    d.arrow(roles["Coverage\nanalyst"], roles["Stimulus"], kind="judgment", label="gap report", sides=("t", "t"), bend=(0, -70), label_dy=-30)
    d.arrow(tools["Simulator"], roles["Debug"], sides=("t", "b"), kind="judgment", label="failures", bend=(100, 0))
    d.arrow(roles["Debug"], tools["Waveform"], sides=("b", "t")); d.arrow(roles["Formal"], tools["Formal engine"], sides=("b", "t"))
    d.arrow(roles["Reviewer"], tools["Repository"], sides=("b", "t")); d.arrow(roles["Reviewer"], tools["Simulator"], sides=("b", "t"), bend=(-300, 120))
    g3 = d.gate(1340, 870, "Gate 3\nsign-off", w=200, h=84)
    d.arrow(roles["Reviewer"], g3, kind="judgment", label="mutation kill rate", sides=("b", "t"), bend=(90, 40), label_dy=-70)
    d.arrow(roles["Debug"], g3, kind="judgment", label="ranked hypotheses", sides=("r", "l"), bend=(200, 210), label_dy=60)
    d.arrow(g2, g3, kind="judgment", sides=("b", "l"), bend=(60, 120), label="coverage against plan", label_dy=40)
    d.parts.append(f'<path d="M270,468 H310" stroke="{AMBER}" stroke-width="4"/><text x="290" y="500" {SANS} font-size="14" font-weight="700" fill="#6B4A0E" text-anchor="middle">no write</text>')
    if delegation:
        d.parts.append(f'<rect x="40" y="420" width="240" height="96" rx="10" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="3"/>')
        for x in (824, 1082, 1340): d.parts.append(f'<rect x="{x-14}" y="420" width="248" height="96" rx="10" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="3"/>')
        for x in (298, 556): d.parts.append(f'<rect x="{x-14}" y="420" width="248" height="96" rx="10" fill="{AMBER}" fill-opacity="0.10" stroke="{AMBER}" stroke-width="3"/>')
        d.parts.append(f'<rect x="640" y="170" width="300" height="96" rx="10" fill="{AMBER}" fill-opacity="0.10" stroke="{AMBER}" stroke-width="3"/>')
        d.parts.append(f'<rect x="1320" y="856" width="240" height="112" rx="10" fill="{AMBER}" fill-opacity="0.10" stroke="{AMBER}" stroke-width="3"/>')
        d.label(1150, 200, "Delegable today: the toolchain is the judge", 18, GREEN, "700")
        d.label(1150, 228, "Not yet: the output would become the judge", 18, AMBER, "700")
    d.legend(60, 970); d.save(name)


def fig_swimlane():
    d = Diagram(1600, 620, "Plan item FIFO-005 through the flow")
    lanes = ["Human gates", "Planner", "Stimulus agent", "Checker author (human)", "Simulator", "Debug agent"]
    lh = 88; x0 = 240
    for i, ln in enumerate(lanes):
        y = 40 + i*lh
        d.parts.append(f'<rect x="20" y="{y}" width="1560" height="{lh}" fill="{GROUND if i % 2 else "white"}" stroke="{DIM}" stroke-width="1"/>')
        d.label(30, y + lh/2 + 5, ln, 16, INK, "700")
    def at(lane, col, text, kind="tool", w=200):
        x = x0 + col*230; y = 40 + lane*lh + 12
        return {"tool": d.tool, "model": d.model, "store": d.store, "gate": d.gate}[kind](x, y, text, w=w, h=lh-24)
    s1 = at(1, 0, "FIFO-005: full only\nat 16 entries", "model")
    g1 = at(0, 1, "Gate 1: item\napproved", "gate", w=150)
    s2 = at(2, 2, "Random test with\nwrite pressure", "model")
    s3 = at(3, 2, "Model: full ==\n(occupancy == 16)", "store")
    g2 = at(0, 3, "Gate 2: checker\napproved", "gate", w=150)
    s4 = at(4, 4, "Run seed 1:\nfull=1 at 15", "tool")
    s5 = at(5, 5, "Hypothesis: counter\nwidth off by one", "model")
    g3 = at(0, 5, "Human confirms;\nbug filed", "gate", w=150)
    d.arrow(s1, g1); d.arrow(g1, s2, sides=("b", "t")); d.arrow(g1, s3, sides=("b", "t"), bend=(0, 80))
    d.arrow(s3, g2, sides=("r", "b"), bend=(0, -60)); d.arrow(s2, s4, sides=("b", "t")); d.arrow(s3, s4, sides=("b", "t"), kind="judgment", label="compares")
    d.arrow(s4, s5, sides=("b", "t"), kind="judgment", label="failure"); d.arrow(s5, g3, sides=("t", "b"), kind="judgment")
    d.note(240, 570, "The stimulus agent reached the state. The checker, which it could not touch, found the bug. A stimulus agent measured on coverage alone would have reported success.", w=1300)
    d.save("ch34-swimlane.svg")


if __name__ == "__main__":
    fig_model(); fig_prompt(); fig_grounding(); fig_tools(); fig_loop(); fig_evaluation()
    fig_separation(); fig_multiagent(); fig_flow(); fig_flow(delegation=True); fig_swimlane()
