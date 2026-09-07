#!/usr/bin/env python3
"""Generate the eleven block diagrams of Chapter 34 (ch34-*.svg).

Every figure uses the shared language in blocks.py: model (rounded, blue),
tool (rectangle), evidence store (cylinder), human gate (diamond); solid
arrows carry data, dashed arrows carry a judgment. Run from anywhere:

    python3 figures/gen_ch34_figures.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from blocks import Diagram, BLUE, DIM, AMBER, GREEN, VIOLET, INK, GROUND, TRACE, SANS


def fig_model():
    d = Diagram(1400, 430, "The generative model beside a constrained-random generator")
    # left: generative model
    d.region(20, 20, 690, 380, "A generative model")
    ctx = d.store(50, 130, "Context", w=150, sub="prompt + tokens so far")
    m = d.model(240, 130, "Model", w=170, sub="next-token distribution")
    smp = d.tool(450, 130, "Sampler", w=150, sub="temperature, seed")
    out = d.store(450, 270, "Output", w=150, sub="one token")
    d.arrow(ctx, m); d.arrow(m, smp, label="P(next token)"); d.arrow(smp, out)
    d.arrow(out, ctx, label="append and repeat", sides=("l", "b"), bend=(-60, 60))
    d.caption(50, 370, "Fluent by construction. Correct only where the data and the prompt make it so. Different on every run unless the seed is fixed.")
    # right: constrained-random generator
    d.region(730, 20, 650, 380, "A constrained-random generator")
    cons = d.store(760, 130, "Constraints", w=150, sub="the legal space")
    slv = d.tool(950, 130, "Solver", w=150, sub="picks a point")
    smp2 = d.tool(1140, 130, "Sampler", w=150, sub="seed")
    st = d.store(1140, 270, "Stimulus", w=150, sub="one transaction")
    d.arrow(cons, slv); d.arrow(slv, smp2); d.arrow(smp2, st)
    d.arrow(st, cons, label="next transaction", sides=("l", "b"), bend=(-60, 60))
    d.caption(760, 370, "Same shape: a space, a sampler, a seed. The prompt is the constraint set.")
    d.legend(60, 405); d.save("ch34-model.svg")


def fig_prompt():
    d = Diagram(1400, 440, "Prompt anatomy, the instruction file, and the verification plan")
    d.region(20, 20, 800, 400, "The parts of a prompt")
    parts = ["Instruction\nwhat to do", "Examples\nwhat good looks like", "Constraints\nwhat not to do", "Output format\nwhat shape to return"]
    boxes = [d.store(50 + i*190, 110, p, w=170, h=76) for i, p in enumerate(parts)]
    asm = d.tool(300, 250, "Assembled prompt", w=240, sub="one call's context")
    for b in boxes: d.arrow(b, asm, sides=("b", "t"))
    m = d.model(600, 250, "Model", w=160)
    d.arrow(asm, m)
    inst = d.store(50, 300, "Instruction file", w=190, h=70, sub="versioned, checked in")
    d.arrow(inst, boxes[0], label="feeds every call", sides=("t", "b"))
    d.caption(50, 400, "A prompt is a specification, with every problem a specification has: ambiguity, omission, the reader's assumptions.")
    d.region(840, 20, 540, 400, "The verification counterpart")
    plan = d.store(870, 110, "Verification plan", w=200, h=76, sub="machine-readable, versioned")
    tb = d.tool(1130, 110, "Testbench", w=200, h=76, sub="stimulus, checker, coverage")
    d.arrow(plan, tb, label="what to verify,\nhow, and when done")
    reg = d.tool(1130, 260, "Regression", w=200, h=64)
    d.arrow(tb, reg, sides=("b", "t")); d.arrow(reg, plan, label="results reported\nagainst the plan", kind="judgment", sides=("l", "b"), bend=(-40, 60))
    d.caption(870, 400, "The plan is the testbench's instruction file.")
    d.save("ch34-prompt.svg")


def fig_grounding():
    d = Diagram(1400, 470, "Grounding: sources, the context assembler, and the model")
    d.region(20, 20, 300, 420, "Grounding sources (read-only)")
    srcs = [d.store(50, 60 + i*72, n, w=240, h=58) for i, n in enumerate(["Specification", "Verification plan", "RTL", "Logs and waveforms", "Regression history"])]
    asm = d.tool(430, 170, "Context assembler", w=260, h=110, sub="the design decision")
    d.parts.append(f'<rect x="430" y="170" width="260" height="110" rx="6" fill="none" stroke="{AMBER}" stroke-width="3"/>')
    for s in srcs: d.arrow(s, asm, sides=("r", "l"))
    ret = d.note(430, 40, "Retrieval: fetch passages by\nsimilarity, paste them in.", w=260)
    srch = d.note(430, 320, "Search: let the model look through\nthe repository the way an engineer does.\n(What won for code.)", w=260)
    m = d.model(780, 190, "Model", w=170, sub="sees only its context")
    d.arrow(asm, m, label="what fits, and nothing else")
    win = d.note(1000, 60, "Nominal window: very large.\nEffective attention: much smaller.\nWhat is included matters more\nthan how much.", w=320)
    out = d.store(1000, 300, "Answer, code, plan", w=240, h=64)
    d.arrow(m, out)
    d.caption(430, 455, "Nothing outside the context exists for the model. It will produce a plausible substitute for whatever it was not given.")
    d.save("ch34-grounding.svg")


def fig_tools():
    d = Diagram(1400, 470, "Tool use: model, harness, tool server, sandbox")
    m = d.model(40, 190, "Model", w=170, sub="emits a request")
    h = d.tool(280, 190, "Harness", w=180, sub="runs it, returns result")
    d.arrow(m, h, label="tool request\n(name, arguments)")
    d.arrow(h, m, label="result", sides=("b", "b"), bend=(0, 70))
    d.region(520, 40, 560, 400, "Sandbox: a place the agent can break")
    ts = d.tool(560, 110, "Tool server", w=200, h=70, sub="advertises name, schema")
    d.arrow(h, ts, label="call")
    sim = d.tool(800, 80, "Simulator", w=240, h=56, sub="compile, run seed, coverage")
    fe = d.tool(800, 160, "Formal engine", w=240, h=56, sub="prove, refute, vacuity")
    cov = d.store(800, 240, "Coverage DB", w=240, h=56)
    wav = d.store(800, 320, "Waveforms, logs", w=240, h=56)
    for t in (sim, fe, cov, wav): d.arrow(ts, t)
    d.note(560, 220, "Exposed: compile, run with a seed,\nfetch coverage, fetch failures,\nfetch a waveform slice.", w=210)
    d.note(560, 330, "Never exposed to a stimulus agent:\nthe checker's source, the coverage\nmodel, the reference model.", w=210)
    d.region(1100, 40, 280, 400, "Verification counterpart")
    mk = d.tool(1125, 110, "make lint | run", w=230, h=64, sub="three uniform targets")
    st = d.store(1125, 220, "status.json", w=230, h=64, sub="pass, fail, expect")
    d.arrow(mk, st, sides=("b", "t"))
    d.caption(1125, 330, "This book's build system is\nalready a tool interface.")
    d.caption(40, 400, "A simulation is an expensive tool call. The loop is designed around that cost.")
    d.save("ch34-tools.svg")


def fig_loop():
    d = Diagram(1400, 470, "The agent loop with its four failure points, beside the coverage-driven loop")
    d.region(20, 20, 680, 430, "The agent loop")
    pl = d.model(60, 80, "Plan", w=170, sub="what to do next")
    ac = d.tool(400, 80, "Act", w=170, sub="a tool call")
    ob = d.store(400, 260, "Observe", w=170, sub="the result")
    de = d.model(60, 260, "Stop?", w=170, sub="decide")
    d.arrow(pl, ac); d.arrow(ac, ob, sides=("b", "t")); d.arrow(ob, de); d.arrow(de, pl, sides=("t", "b"), label="no: loop")
    d.failure_mark(150, 150, 1); d.failure_mark(490, 150, 2); d.failure_mark(330, 300, 3); d.failure_mark(150, 330, 4)
    d.note(60, 380, "Failure points:  1 wrong plan  ·  2 wrong tool call  ·  3 misread result  ·  4 wrong stopping decision (the one that matters most)", w=600, size=12)
    d.region(720, 20, 660, 430, "The coverage-driven loop")
    ws = d.tool(760, 80, "Write stimulus", w=190, h=60)
    rn = d.tool(1100, 80, "Run", w=190, h=60, sub="simulator")
    cr = d.store(1100, 260, "Coverage report", w=190, h=60)
    en = d.model(760, 260, "Enough?", w=190, h=60, sub="stopping signal")
    d.arrow(ws, rn); d.arrow(rn, cr, sides=("b", "t")); d.arrow(cr, en); d.arrow(en, ws, sides=("t", "b"), label="no: another test")
    d.note(760, 370, "The stopping signal is coverage. The goal is bugs found. They are not the same,\nwhich is why coverage is a proxy the discipline learned not to trust.", w=580, size=12)
    d.save("ch34-loop.svg")


def fig_evaluation():
    d = Diagram(1400, 440, "Visible and hidden metrics, and the gap between them")
    g = d.model(40, 170, "Generator", w=180, sub="optimizes what it sees")
    art = d.store(280, 170, "Artifact", w=170, sub="code, test, stimulus")
    d.arrow(g, art)
    vis = d.tool(540, 70, "Visible metric", w=220, h=70, sub="the tests it can see")
    hid = d.tool(540, 270, "Hidden metric", w=220, h=70, sub="held-out tests, mutants")
    d.arrow(art, vis, kind="judgment", sides=("r", "l")); d.arrow(art, hid, kind="judgment", sides=("r", "l"))
    d.label(800, 105, "satisfied", 15, GREEN, "700"); d.label(800, 305, "not satisfied", 15, AMBER, "700")
    d.parts.append(f'<path d="M905,120 V290" stroke="{AMBER}" stroke-width="3" stroke-dasharray="8 6"/>')
    d.label(925, 210, "the gap: what the generator\nwas optimized against versus\nwhat mattered", 14, INK)
    d.region(40, 360, 1340, 70, "Verification counterpart", stroke=BLUE)
    d.label(60, 405, "Visible: coverage (a proxy).   Hidden: bug-finding power (mutants killed).   Measured on small designs: about 90 percent coverage against about 14 percent mutation detection.", 14, INK)
    d.save("ch34-evaluation.svg")


def fig_separation():
    d = Diagram(1400, 520, "Separation of generator and judge")
    d.region(20, 20, 600, 330, "Stimulus context", stroke=BLUE)
    sa = d.model(50, 80, "Stimulus agent", w=200, sub="writes tests, sequences")
    stim = d.store(320, 80, "Stimulus", w=200, sub="tests, constraints")
    d.arrow(sa, stim)
    d.note(50, 190, "May read: specification, plan, RTL,\ncoverage report, failures.\nMay write: stimulus only.", w=470)
    d.region(780, 20, 600, 330, "Oracle context", stroke=VIOLET)
    oa = d.model(810, 80, "Checker author", w=200, sub="human, or a separate agent")
    orc = d.store(1080, 80, "Oracle", w=260, sub="checker, reference model,\nassertions, coverage model")
    d.arrow(oa, orc)
    d.note(810, 190, "Written from the specification,\nwith the stimulus closed.\nApproved at a human gate.", w=470)
    d.parts.append(f'<rect x="676" y="30" width="48" height="310" fill="{GROUND}" stroke="{AMBER}" stroke-width="3"/>')
    for k, ln in enumerate(["no write access", "enforced by harness and repository", "never by the prompt"]):
        d.parts.append(f'<text x="{690 + k*10}" y="185" {SANS} font-size="11" font-weight="700" fill="#6B4A0E" text-anchor="middle" transform="rotate(-90 {690 + k*10} 185)">{ln}</text>')
    tc = d.tool(540, 400, "Toolchain: simulator, formal engine, coverage database", w=520, h=64, sub="the only judge")
    d.arrow(stim, tc, sides=("b", "t")); d.arrow(orc, tc, sides=("b", "t"))
    d.arrow(tc, sa, kind="judgment", sides=("l", "b"), bend=(-120, 40), label="pass, fail, coverage")
    d.arrow(tc, oa, kind="judgment", sides=("r", "b"), bend=(120, 40), label="proven, refuted, vacuous")
    d.caption(40, 500, "Whatever generates must not own what judges. In software the agent deleted the failing test when it could; here it cannot reach it.")
    d.save("ch34-separation.svg")


def fig_multiagent():
    d = Diagram(1400, 520, "A multi-agent flow and the path of a propagating wrong belief")
    orch = d.model(600, 40, "Orchestrator", w=200, sub="plans, delegates, believes")
    wa = d.model(120, 200, "Worker A", w=180, sub="stimulus")
    wb = d.model(610, 200, "Worker B", w=180, sub="coverage analysis")
    wc = d.model(1100, 200, "Worker C", w=180, sub="verifier")
    for w in (wa, wb, wc): d.arrow(orch, w, sides=("b", "t"))
    d.arrow(wa, orch, label="summary: 'done, all passing'", sides=("t", "b"), bend=(-80, -20))
    d.arrow(orch, wb, label="'A says done; analyze'", sides=("b", "t"), bend=(60, 0))
    d.parts.append(f'<path d="M210,200 Q400,90 600,72" fill="none" stroke="{AMBER}" stroke-width="4" stroke-dasharray="10 6"/>')
    d.parts.append(f'<path d="M700,104 Q700,150 700,200" fill="none" stroke="{AMBER}" stroke-width="4" stroke-dasharray="10 6"/>')
    d.label(330, 120, "a wrong belief travels\nas a confident summary", 13, AMBER, "700")
    shared = d.store(520, 330, "Shared prompt and summaries", w=360, h=64, sub="what every agent was told")
    ind = d.store(1000, 330, "Independent evidence", w=380, h=64, sub="simulator output, formal verdict, coverage DB")
    d.arrow(shared, wb, sides=("t", "b")); d.arrow(ind, wc, sides=("t", "b"), kind="judgment", label="what A did not hold")
    d.note(40, 420, "A verifier that shares the generator's evidence agrees with it. A verifier helps only when it holds evidence the generator does not: the toolchain's verdict, never a second reading of the same prompt.", w=1320, size=13)
    d.caption(40, 505, "Verification counterpart: designer, verifier, formal engineer and sign-off reviewer, whose value has always been their independence.")
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
    d.parts.append(f'<rect x="1570" y="700" width="0" height="0"/>')
    d.parts.append(f'<path d="M270,468 H310" stroke="{AMBER}" stroke-width="4"/><text x="290" y="500" {SANS} font-size="12" font-weight="700" fill="#6B4A0E" text-anchor="middle">no write</text>')
    if delegation:
        d.parts.append(f'<rect x="40" y="420" width="240" height="96" rx="10" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="3"/>')
        for x in (824, 1082, 1340): d.parts.append(f'<rect x="{x-14}" y="420" width="248" height="96" rx="10" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="3"/>')
        for x in (298, 556): d.parts.append(f'<rect x="{x-14}" y="420" width="248" height="96" rx="10" fill="{AMBER}" fill-opacity="0.10" stroke="{AMBER}" stroke-width="3"/>')
        d.parts.append(f'<rect x="640" y="170" width="300" height="96" rx="10" fill="{AMBER}" fill-opacity="0.10" stroke="{AMBER}" stroke-width="3"/>')
        d.parts.append(f'<rect x="1320" y="856" width="240" height="112" rx="10" fill="{AMBER}" fill-opacity="0.10" stroke="{AMBER}" stroke-width="3"/>')
        d.label(1200, 200, "Delegable today: the toolchain is the judge", 15, GREEN, "700")
        d.label(1200, 226, "Not yet: the output would become the judge", 15, AMBER, "700")
    d.legend(60, 970); d.save(name)


def fig_swimlane():
    d = Diagram(1600, 620, "Plan item FIFO-005 through the flow")
    lanes = ["Human gates", "Planner", "Stimulus agent", "Checker author (human)", "Simulator", "Debug agent"]
    lh = 88; x0 = 240
    for i, ln in enumerate(lanes):
        y = 40 + i*lh
        d.parts.append(f'<rect x="20" y="{y}" width="1560" height="{lh}" fill="{GROUND if i % 2 else "white"}" stroke="{DIM}" stroke-width="1"/>')
        d.label(30, y + lh/2 + 5, ln, 14, INK, "700")
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
    d.note(240, 570, "The stimulus agent reached the state. The checker, which it could not touch, found the bug. A stimulus agent measured on coverage alone would have reported success.", w=1300, size=13)
    d.save("ch34-swimlane.svg")


if __name__ == "__main__":
    fig_model(); fig_prompt(); fig_grounding(); fig_tools(); fig_loop(); fig_evaluation()
    fig_separation(); fig_multiagent(); fig_flow(); fig_flow(delegation=True); fig_swimlane()
