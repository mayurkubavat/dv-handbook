"""Tests for the Chapter 3 tools on the book's own designs.

Each test states a fact the chapter prints, so a change to the design or
the tools that alters the fact fails here before it reaches the text.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from dvh import clocks, design, graph  # noqa: E402

RTL = ROOT / "examples" / "ch03-digital-design" / "rtl"
SOURCES = ("regblock.sv", "sync2.sv", "datapath.sv", "top.sv")
TWO_CLOCK = [str(RTL / f) for f in SOURCES]
FIFO = [str(ROOT / "examples" / "ch01-what-is-dv" / "rtl" / "fifo.sv")]


def _dom(tree, label):
    """Registers in the one domain whose readable name is `label`."""
    return [r for d, rs in tree["domains"].items()
            for r in rs if clocks._pretty(d) == label]


def test_two_clock_domains():
    tree = clocks.clock_tree(design.load_flat(TWO_CLOCK, "top"))
    labels = {clocks._pretty(d) for d in tree["domains"]}
    assert labels == {"bclk", "cclk"}
    assert len(_dom(tree, "bclk")) == 2          # en, cfg
    # cclk holds the synchronizer's two stages plus count, acc, last_cfg.
    assert len(_dom(tree, "cclk")) == 5
    assert not any(r["gated_or_muxed"] for r in tree["registers"].values())


def test_one_register_without_reset():
    resets = clocks.reset_tree(design.load_flat(TWO_CLOCK, "top"))
    assert [r["name"] for r in resets["no_reset"]] == ["last_cfg"]
    for name, r in resets["registers"].items():
        assert r["kind"] == "asynchronous" and r["active"] == "low", name
    assert resets["registers"]["acc"]["sources"] == ["crst_n"]


def test_crossings_found_and_classified():
    flat = design.load_flat(TWO_CLOCK, "top")
    x = clocks.crossings(flat)
    unsync = {(c["from"], c["to"]) for c in x["unrecognized"]}
    assert unsync == {("cfg_b", "acc"), ("cfg_b", "last_cfg")}
    sync = [c for c in x["crossings"] if c["shape_recognized"]]
    assert len(sync) == 1
    assert sync[0]["from"] == "en_b" and sync[0]["width"] == 1


def test_connection_graph_sees_parameterized_instance():
    mods = design.load_hier(TWO_CLOCK, "top")
    conn = graph.connections(mods, "top")
    assert set(conn["instances"]) == {"u_regs", "u_sync_en", "u_dp"}
    assert conn["instances"]["u_sync_en"]["module"] == "sync2"
    pairs = {(e["from"], e["to"]) for e in conn["edges"]}
    assert ("u_regs", "u_dp") in pairs and ("u_sync_en", "u_dp") in pairs


def test_single_clock_fifo_has_no_crossings():
    """The Chapter 1 FIFO is one clock domain, so there is nothing to cross."""
    flat = design.load_flat(FIFO, "fifo")
    tree = clocks.clock_tree(flat)
    assert {clocks._pretty(d) for d in tree["domains"]} == {"clk"}
    assert clocks.crossings(flat, tree)["crossings"] == []


def test_fifo_storage_array_reports_as_unreset_registers():
    """A storage array is registers with no reset, and the tool says so.

    The finding is correct and is not a bug: a FIFO's memory is not meant to
    reset. It is the reading of the report, not the report, that needs a
    person -- which is the chapter's point about what a tool can and cannot
    decide on its own.
    """
    resets = clocks.reset_tree(design.load_flat(FIFO, "fifo"))
    assert all(r["name"].startswith("mem[") for r in resets["no_reset"])
    assert len(resets["no_reset"]) == 16
    for name in ("wr_ptr", "rd_ptr", "count"):
        r = resets["registers"][name]
        assert r["kind"] == "asynchronous"
        assert r["active"] == "low"
        assert r["sources"] == ["rst_n"]


def test_report_text_is_exactly_what_the_chapter_prints():
    """The report is typeset into the book, so its text is part of the API.

    Sorted order matters as much as the wording: a netlist reader is free to
    hand back cells in any order, and a printed page that disagrees with the
    reader's own run is worse than no listing at all.
    """
    from dvh import cli                                    # noqa: PLC0415
    # A source location is reported relative to where the tool ran, which is
    # what a reader wants and what makes this text depend on the directory.
    # Pin it from the repository root so the expectation is one string.
    here = os.getcwd()
    os.chdir(ROOT)
    try:
        _assert_report_text(cli)
    finally:
        os.chdir(here)


def _assert_report_text(cli):
    flat = design.load_flat(TWO_CLOCK, "top")
    mods = design.load_hier(TWO_CLOCK, "top")
    tree = clocks.clock_tree(flat)
    report = cli._report(tree, clocks.reset_tree(flat),
                         clocks.crossings(flat, tree),
                         graph.connections(mods, "top"))
    assert report == "\n".join([
        "clock domains: 2",
        "  bclk: 2 registers",
        "  cclk: 5 registers",
        "registers without reset: 1",
        "  last_cfg  [examples/ch03-digital-design/rtl/datapath.sv:24]",
        "crossings: 3, shape not recognized: 2",
        "  CHECK cfg_b (bclk) -> acc (cclk), 8 bits, no synchronizer shape",
        "         [examples/ch03-digital-design/rtl/datapath.sv:14]",
        "  CHECK cfg_b (bclk) -> last_cfg (cclk), 8 bits, "
        "no synchronizer shape",
        "         [examples/ch03-digital-design/rtl/datapath.sv:24]",
        "  known en_b (bclk) -> u_sync_en.meta (cclk), 1 bit, "
        "two-flop synchronizer",
        "         [examples/ch03-digital-design/rtl/sync2.sv:13]",
        "instances: 3, connections: 15",
    ])


# ----------------------------------------------------------------------
# Limits the tools were once wrong about. Each of these designs defeated an
# earlier version of the walks, so each keeps its own file under tests/rtl.
# ----------------------------------------------------------------------
FIXTURE = pathlib.Path(__file__).parent / "rtl"

# Every design the repository ships: the tool's own regression fixtures, the
# chapter's two-clock example, and the FIFO Chapter 1 builds on. The claims
# the book makes about source locations are claims about all of these, so
# the tests that check those claims run over all of these.
EX = ROOT / "examples"
_EVERY_DESIGN = ([([str(f)], f.stem) for f in sorted(FIXTURE.glob("*.sv"))]
                 + [(TWO_CLOCK, "top"), (FIFO, "fifo"),
                    ([str(EX / "appF-counter" / "rtl" / "counter.sv")],
                     "counter"),
                    ([str(EX / "ch04-simulation" / "race" / "racy.sv")],
                     "racy"),
                    ([str(EX / "ch04-simulation" / "race" / "safe.sv")],
                     "safe"),
                    ([str(EX / "ch04-simulation" / "fourstate" /
                          "dut_unreset.sv")], "dut_unreset")])

# The clocks a specification would declare, for the fixtures whose gates
# the netlist alone cannot resolve.
_DECLARED = {"divided_blend": ("clk1", "clk2"),
             "per_bit_mixed_roots": ("aclk", "bclk"),
             "latch_destination": ("aclk", "bclk"),
             "kept_instance": ("aclk", "bclk"),
             "gated_clock": ("clk",),
             "shared_enable_clocks": ("aclk", "bclk"),
             "blended_clock": ("clk1", "clk2"),
             "gate_built_clock_mux": ("clk1", "clk2"),
             "per_bit_behind_gates": ("aclk", "bclk")}


def test_a_clock_gate_is_undecided_until_the_clocks_are_declared():
    """Which input of a gate is the clock is not in the netlist.

    `clk & en` and `clk1 & clk2` are the same gate: one input drives
    registers elsewhere and the other does not. The walk once read strong
    evidence for one input as evidence against the other, and so reported a
    *blended* clock -- two clocks combined to make a third -- as one clock
    gated differently, and passed the build on an unsynchronized crossing
    between two unrelated clocks.

    So undeclared, the gate is undecided and the path into it fails. Declare
    the clocks and the question does not arise: the enable is not one, the
    gated register is on the declared clock, and the design passes.
    """
    flat = design.load_flat([str(FIXTURE / "gated_clock.sv")], "gated_clock")
    tree = clocks.clock_tree(flat)
    assert tree["registers"]["q_gated"]["clock_ambiguous"]
    x = clocks.crossings(flat, tree)
    assert len(x["crossings"]) == 1
    assert not x["crossings"][0]["same_clock_source"]
    assert x["unrecognized"]

    told = clocks.clock_tree(flat, ("clk",))
    assert all(clocks._pretty(d) == "clk" for d in told["domains"])
    assert "gated by en" in told["registers"]["q_gated"]["through"]
    assert not told["registers"]["q_gated"]["clock_ambiguous"]
    y = clocks.crossings(flat, told, ("clk",))
    assert len(y["crossings"]) == 1
    assert y["crossings"][0]["same_clock_source"]
    assert not y["unrecognized"], "a gated design must not fail the gate"


def test_a_blended_clock_is_not_one_clock_gated_differently():
    """Two clocks combined to make a third, and a clock multiplexer built
    from gates rather than from a multiplexer cell.

    Both were reported as one clock gated differently and both passed the
    build on an eight-bit unsynchronized crossing. The multiplexer is the
    worse of the two, because the walk had a rule that selection never
    demotes an input -- and that rule keyed on a `$mux` cell, which a
    glitch-free clock multiplexer written out of gates never produces.
    """
    for top in ("blended_clock", "gate_built_clock_mux"):
        flat = design.load_flat([str(FIXTURE / f"{top}.sv")], top)
        tree = clocks.clock_tree(flat)
        x = clocks.crossings(flat, tree)
        assert len(x["crossings"]) == 1, top
        assert not x["crossings"][0]["same_clock_source"], top
        assert x["unrecognized"], top
        # And with the clocks declared, both are two domains rather than
        # one, so the crossing still fails -- it is a real one.
        told = clocks.crossings(flat, None, ("clk1", "clk2"))
        assert told["unrecognized"], top


def test_a_kept_submodule_does_not_hide_the_design():
    """`keep_hierarchy` stops `flatten`, and the top module then holds none
    of the registers. The report said the design had no clocks and no
    crossings, and the build passed on a design containing both."""
    flat = design.load_flat([str(FIXTURE / "kept_hierarchy.sv")],
                            "kept_hierarchy")
    assert len(list(design.registers(flat))) == 2
    x = clocks.crossings(flat)
    assert [c["from"] for c in x["crossings"]] == ["u_lane.a"]
    assert x["unrecognized"]


def test_per_bit_chains_behind_two_clock_gates_are_one_boundary():
    """One clock gated two ways is two domain keys and one boundary.

    The rule that demotes parallel one-bit chains grouped them by domain
    key, so two chains off one physical clock were two groups of one and
    neither rule fired: two bits of one value, synchronized separately,
    came back as two recognized synchronizers. The grouping is now the pair
    of clock nets, which is what the boundary physically is.
    """
    flat = design.load_flat([str(FIXTURE / "per_bit_behind_gates.sv")],
                            "per_bit_behind_gates")
    x = clocks.crossings(flat, None, ("aclk", "bclk"))
    assert len(x["crossings"]) == 2
    assert not any(c["shape_recognized"] for c in x["crossings"])
    assert "in parallel" in x["crossings"][0]["note"]
    assert len(x["unrecognized"]) == 2


def test_crossing_through_a_mux_select_is_found():
    """A foreign register steering a multiplexer is a control crossing.

    The clock walk rightly ignores a select, because a select is not a
    clock. A data cone must follow it, or this design reports as clean.
    """
    flat = design.load_flat([str(FIXTURE / "mux_select.sv")], "mux_select")
    x = clocks.crossings(flat)
    found = [(c["from"], c["to"]) for c in x["unrecognized"]]
    assert found == [("sel_b", "out")]


def test_parallel_per_bit_synchronizers_are_rejected():
    """Eight correct shapes are still a loss of data.

    Each chain matches the synchronizer rule on its own, so a structural
    test accepts all eight. The bits resolve independently, so the receiver
    can see a value the sender never sent.
    """
    files = [str(FIXTURE / "per_bit_sync.sv")]
    flat = design.load_flat(files, "per_bit_sync")
    x = clocks.crossings(flat)
    assert len(x["unrecognized"]) == 8
    assert all("read together" in c["note"] for c in x["unrecognized"])


def test_per_bit_anti_pattern_is_caught_without_a_shared_name():
    """Convergence is the signal, not the sending register's name.

    Here the eight sending flops are declared separately, so any check that
    grouped by name would pass this design. What gives it away is that one
    downstream register reads all eight synchronizer outputs.
    """
    files = [str(FIXTURE / "split_source_sync.sv")]
    flat = design.load_flat(files, "split_source_sync")
    x = clocks.crossings(flat)
    assert len(x["unrecognized"]) == 8
    assert all("read together" in c["note"] for c in x["unrecognized"])


def test_an_undecidable_clock_is_reported_not_suppressed():
    """When the walk cannot tell a clock from an enable, it must say so.

    With no register driven straight from a port there is no strong
    evidence for which gate input is the clock, so the enable lands in the
    domain name. An earlier version suppressed any crossing whose domain
    names shared a token, which silenced real crossings between two
    asynchronous clocks that happened to share one global enable. Failing
    loudly is the only safe behavior for a report a build gate trusts.
    """
    files = [str(FIXTURE / "two_clock_gates.sv")]
    flat = design.load_flat(files, "two_clock_gates")
    tree = clocks.clock_tree(flat)
    assert all(r["clock_ambiguous"] for r in tree["registers"].values())
    found = clocks.crossings(flat, tree)["unrecognized"]
    assert found and all("declare the clocks" in c["note"] for c in found)


def test_a_crossing_through_a_latch_is_still_reported():
    """A latch is state, so the path is not a synchronizer -- but stopping
    the walk at one would hide the crossing altogether, which is worse.

    Two findings, not one. The path *through* the latch to the receiving
    flip-flop is one; the latch itself is the other, because a latch is
    also a destination and its enable decides when the data is caught. Here
    the enable is a top-level port, so which domain opens the latch is not
    something the netlist says, and the report says that rather than
    assuming it.
    """
    files = [str(FIXTURE / "crossing_via_latch.sv")]
    flat = design.load_flat(files, "crossing_via_latch")
    x = clocks.crossings(flat)
    onto_latch = [c for c in x["unrecognized"] if c["to"] == "lat"]
    assert len(onto_latch) == 1
    assert "undecided enable" in onto_latch[0]["to_domain"]
    assert len(x["unrecognized"]) == 2


def test_bit_blasted_registers_are_not_collapsed():
    """Registers sharing a net must not overwrite each other by name.

    Yosys emits this design's synchronizers as one-bit cells, several to a
    net. Naming them all after the net would drop all but one, and the
    reported domain sizes would be net counts rather than register counts.
    """
    files = [str(FIXTURE / "per_bit_sync.sv")]
    flat = design.load_flat(files, "per_bit_sync")
    names = [n for n, _ in design.registers(flat)]
    assert len(names) == len(set(names))
    assert len(names) == len(clocks.clock_tree(flat)["registers"])


# ----------------------------------------------------------------------
# The published schemas are a contract with callers who are not this book,
# so a change to an output that the schema does not describe must fail here.
# ----------------------------------------------------------------------
def test_every_command_matches_its_published_schema():
    from dvh import schema                                # noqa: PLC0415
    flat = design.load_flat(TWO_CLOCK, "top")
    mods = design.load_hier(TWO_CLOCK, "top")
    payloads = {
        "clock-tree": clocks.clock_tree(flat),
        "reset-tree": clocks.reset_tree(flat),
        "crossings": clocks.crossings(flat),
        "connections": graph.connections(mods, "top"),
    }
    assert set(payloads) == set(schema.FOR_COMMAND)
    for command, payload in payloads.items():
        assert schema.validate(command, payload) == [], command


def test_the_schemas_reject_a_payload_that_is_wrong():
    """A validator that accepts everything is not a check.

    Each case below is a mistake a change to the tools could plausibly
    make: a dropped key, a renamed field, a wrong type.
    """
    from dvh import schema                                # noqa: PLC0415
    assert schema.validate("crossings", {"crossings": []})
    assert schema.validate("reset-tree", {"registers": {}, "no_reset": "none"})
    assert schema.validate("clock-tree", {
        "domains": {}, "registers": {"r": {"clock_sources": []}}})


def test_every_field_carries_a_description():
    """The appendix claims every field is described. Keep that true.

    A field name is not a definition, and a caller who is not this book has
    only the schema to read. `description` is the consumer-facing keyword;
    `$comment` is a note between schema authors and does not count.
    """
    from dvh import schema                                # noqa: PLC0415

    def walk(node, path):
        missing = []
        if not isinstance(node, dict):
            return missing
        for group in ("properties", "patternProperties", "$defs"):
            for name, sub in node.get(group, {}).items():
                where = f"{path}/{name}"
                if group != "$defs" and not sub.get("description"):
                    missing.append(where)     # absent or empty both count
                missing += walk(sub, where)
        for key in ("items", "additionalProperties", "contains"):
            if isinstance(node.get(key), dict):
                missing += walk(node[key], f"{path}/{key}")
        for key in ("allOf", "anyOf", "oneOf", "prefixItems"):
            for i, sub in enumerate(node.get(key, [])):
                missing += walk(sub, f"{path}/{key}[{i}]")
        return missing

    for command in schema.FOR_COMMAND:
        doc = schema.load(command)
        assert doc.get("description"), command
        assert walk(doc, command) == [], command


def test_every_fixture_validates_and_is_located():
    """Run every command on every design this repository ships.

    The narrow version of these checks ran on one design, which had no
    array, so a whole class of register could arrive with nowhere to point
    and the suite stayed green while the tool emitted output its own
    published schema rejected.
    """
    from dvh import schema                                # noqa: PLC0415
    seen = 0
    for rtl in sorted(FIXTURE.glob("*.sv")):
        top = rtl.stem
        flat = design.load_flat([str(rtl)], top)
        mods = design.load_hier([str(rtl)], top)
        tree = clocks.clock_tree(flat)
        payloads = {"clock-tree": tree,
                    "reset-tree": clocks.reset_tree(flat),
                    "crossings": clocks.crossings(flat, tree),
                    "connections": graph.connections(mods, top)}
        for command, payload in payloads.items():
            assert schema.validate(command, payload) == [], (top, command)
        seen += 1
    assert seen >= 12, seen


def test_every_finding_carries_a_real_source_location():
    """The book claims a finding names the RTL that produced it. Prove it.

    Schema conformance is not enough on its own: a blank string would once
    have satisfied it, so an extractor that stopped reading source locations
    would have left the claim silently false with a green build. Here the
    locations are checked for existence, for shape, and for pointing at a
    file that exists.
    """
    found = []
    for files, top in _EVERY_DESIGN:
        flat = design.load_flat(files, top)
        tree = clocks.clock_tree(flat)
        resets = clocks.reset_tree(flat)
        mods = design.load_hier(files, top)
        found += ([r["src"] for r in tree["registers"].values()]
                  + [r["src"] for r in resets["registers"].values()]
                  + [r["src"] for r in resets["no_reset"]]
                  + [c["src"] for c in
                     clocks.crossings(flat, tree)["crossings"]]
                  + [i["src"] for i in
                     graph.connections(mods, top)["instances"].values()])
    assert found, "no report carried a source location at all"
    for src in found:
        file, _, span = src.partition(":")
        assert span and span[0].isdigit(), src
        assert pathlib.Path(file).is_file(), file
        assert not pathlib.Path(file).is_absolute(), file


def test_the_source_location_points_at_the_right_line():
    """A location that is well formed but wrong is worse than none.

    Checked for every register and every instance, not a sample: a
    location is only worth printing if a reader who follows it lands on
    the construct it names.
    """
    # Every design the repository ships, and every report that carries a
    # location, not one design and one command. The narrow version ran on
    # the only design whose registers all come from an `always_ff` the
    # netlist kept a location for, so a register that had to borrow one
    # could point anywhere and this stayed green.
    checked = 0
    for files, top in _EVERY_DESIGN:
        flat = design.load_flat(files, top)
        tree = clocks.clock_tree(flat)
        for name, info in tree["registers"].items():
            checked += _names_the_construct(info["src"], _words(name), name)
        for r in clocks.reset_tree(flat)["no_reset"]:
            checked += _names_the_construct(r["src"], _words(r["name"]),
                                            r["name"])
        for c in clocks.crossings(flat, tree)["crossings"]:
            checked += _names_the_construct(c["src"], _words(c["to"]),
                                            c["to"])
        for name, inst in graph.connections(mods := design.load_hier(
                files, top), top)["instances"].items():
            checked += _names_the_construct(inst["src"], inst["module"], name)
        assert mods
    assert checked >= 8, checked


def _words(name: str) -> tuple:
    """What a register's location may name: the block it is written in, or
    its own declaration. An array lowered to flip-flops points at the line
    the array was declared on, which contains no procedural block at all."""
    return ("always_ff", "always", "assign",
            name.split(".")[-1].split("[")[0])


def _names_the_construct(src: str, keyword, name: str) -> int:
    """True if the reported span contains one of the keywords and, where the
    name survives into the netlist, the name.

    More than one keyword is allowed because a register does not have to
    come from an `always_ff`: an array lowered to flip-flops points at the
    line the array was declared on, which is where a reader wants to be
    sent and contains no procedural block at all.
    """
    words = (keyword,) if isinstance(keyword, str) else tuple(keyword)
    file, _, span = src.partition(":")
    first = int(span.split(".")[0])
    last = int(span.split("-")[-1].split(".")[0]) if "-" in span else first
    text = pathlib.Path(file).read_text().splitlines()
    block = "\n".join(text[first - 1:last])
    hit = [w for w in words if w in block]
    assert hit, (src, words, block[:80])
    return 1


def test_every_schema_is_versioned_by_url():
    """A consumer pins the $id, so every schema must carry one."""
    from dvh import schema                                # noqa: PLC0415
    for command in schema.FOR_COMMAND:
        doc = schema.load(command)
        assert doc["$id"].startswith("https://")
        assert doc["$id"].endswith("-1.json"), command
        assert doc["description"]


def test_a_shared_clock_enable_does_not_hide_a_crossing():
    """Two asynchronous clocks gated by one enable still cross.

    This is the shape that a name-based "same clock" rule silenced: the
    enable is in both domain names, so the names intersect, so the crossing
    vanished. A build gate trusting that exit code would have shipped it.
    """
    files = [str(FIXTURE / "shared_enable_clocks.sv")]
    flat = design.load_flat(files, "shared_enable_clocks")
    x = clocks.crossings(flat)
    assert len(x["unrecognized"]) == 1


def test_convergence_is_followed_through_a_third_flop():
    """The check follows the chain, not one link of it.

    Each bit here crosses through a three-flop synchronizer, so the register
    that reads all eight is two steps from the second stage rather than one.
    """
    files = [str(FIXTURE / "three_flop_per_bit.sv")]
    flat = design.load_flat(files, "three_flop_per_bit")
    x = clocks.crossings(flat)
    assert len(x["unrecognized"]) == 8
    assert all("read together" in c["note"] for c in x["unrecognized"])


def test_a_synchronous_reset_is_reported_as_a_reset():
    """`proc` alone leaves a synchronous reset as a multiplexer.

    Without `opt_dff` the netlist holds a plain flip-flop and every
    synchronously reset register in the design is reported as having no
    reset at all, which is the reset report's headline finding and would
    have been wrong for an entire common category.
    """
    files = [str(FIXTURE / "sync_reset.sv")]
    flat = design.load_flat(files, "sync_reset")
    resets = clocks.reset_tree(flat)
    assert resets["no_reset"] == []
    assert resets["registers"]["q"]["kind"] == "synchronous"
    assert resets["registers"]["q"]["active"] == "high"


def test_two_clock_muxes_over_one_pair_are_not_one_domain():
    """Equal source names are not the same clock network.

    Both muxes here select between the same two asynchronous clocks, on
    opposite selections, so the registers never share a clock. A domain
    keyed on source names merged them and dropped the crossing entirely.
    """
    files = [str(FIXTURE / "mux_selected_clocks.sv")]
    flat = design.load_flat(files, "mux_selected_clocks")
    tree = clocks.clock_tree(flat)
    assert len(tree["domains"]) == 2
    assert clocks.crossings(flat, tree)["unrecognized"]


def test_second_stages_sharing_a_name_are_both_counted():
    """Two second stages can be two bits of one declared register.

    Indexing the convergence rule by name kept one crossing per name and
    silently lost the other, so a two-bit value on per-bit chains passed as
    two recognized shapes.
    """
    files = [str(FIXTURE / "shared_second_stage.sv")]
    flat = design.load_flat(files, "shared_second_stage")
    x = clocks.crossings(flat)
    assert len(x["unrecognized"]) == 2
    assert all("read together" in c["note"] for c in x["unrecognized"])


def test_a_crossing_through_a_ram_is_reported():
    """An array is not registers until the memory passes run.

    Without them the write port is not a register, its clock is not a
    domain, and the read port stops the data walk, so a value crossing
    domains through a RAM is invisible with a clean exit.
    """
    files = [str(FIXTURE / "ram_crossing.sv")]
    flat = design.load_flat(files, "ram_crossing")
    tree = clocks.clock_tree(flat)
    assert len(tree["domains"]) == 2
    assert clocks.crossings(flat, tree)["unrecognized"]


def test_two_muxes_over_one_pair_are_not_one_gated_clock():
    """Equal source *sets* are not a single shared source.

    Both clocks here also drive registers directly, so nothing is
    ambiguous and the walk resolves both mux outputs to the same pair.
    Comparing sets marked that pair "one clock, gated differently" and let
    a real crossing past the build gate.
    """
    files = [str(FIXTURE / "two_strong_clock_muxes.sv")]
    flat = design.load_flat(files, "two_strong_clock_muxes")
    x = clocks.crossings(design.load_flat(files, "two_strong_clock_muxes"))
    assert x["unrecognized"], "a crossing between two clocks passed the gate"
    assert not any(c["same_clock_source"] for c in x["unrecognized"])


def test_a_scan_clock_mux_does_not_escape_the_build_gate():
    """Selection is not gating, and a test clock is still a clock.

    The test clock here reaches nothing but the multiplexer, so no evidence
    said it was a clock; it was classified as a gating enable and the
    crossing was excused as "one clock, gated differently", exit 0.
    """
    files = [str(FIXTURE / "scan_clock_mux.sv")]
    flat = design.load_flat(files, "scan_clock_mux")
    assert clocks.crossings(flat)["unrecognized"]


def test_a_crossing_on_a_latch_enable_is_reported():
    """A latch has inputs other than data, and a crossing can arrive on any."""
    files = [str(FIXTURE / "latch_enable_crossing.sv")]
    flat = design.load_flat(files, "latch_enable_crossing")
    assert len(clocks.crossings(flat)["unrecognized"]) == 1


def test_an_opposite_edge_second_stage_is_not_a_synchronizer():
    """Half a clock period is not the period the shape promises."""
    files = [str(FIXTURE / "opposite_edge_stage.sv")]
    flat = design.load_flat(files, "opposite_edge_stage")
    x = clocks.crossings(flat)
    assert not any(c["shape_recognized"] for c in x["crossings"])


def test_the_data_walk_takes_every_input_the_netlist_offers():
    """Assert the rule, not the design that last broke it.

    Three crossings were dropped one at a time, each by a hand-written list
    of port names that the next design outgrew: one arriving on a latch's
    enable, one folded onto a synchronous clear, one on an asynchronous
    load's value. A test naming the design that found the third would catch
    the fourth only after it shipped. This names the rule instead -- every
    input a register has except its clock is walked -- so a register type
    the list never anticipated fails here.
    """
    pins = set()
    for rtl in sorted(FIXTURE.glob("*.sv")):
        flat = design.load_flat([str(rtl)], rtl.stem)
        for _, cell in design.registers(flat):
            walked = set(clocks._data_inputs(cell))
            declared = {p for p, d in cell.dirs.items() if d == "input"}
            assert declared - walked == {"CLK"}, (rtl.stem, cell.type)
            pins |= declared
    # And the directory must keep exercising the pins that were missed, so
    # the rule above is asserted over something wider than a plain D.
    assert {"D", "SRST", "ARST", "ALOAD", "AD"} <= pins, sorted(pins)


def test_a_register_whose_reset_pin_is_unknown_says_so():
    """A register type nobody anticipated must fail loudly, not crash.

    `$aldff` was listed as a register with an asynchronous reset and has
    none -- it has an asynchronous load -- so every command that built a
    reset tree died with `KeyError: 'CLR'`, which a build gate cannot tell
    from a finding. The pin is now read off the cell, and a type that
    carries no pin the table knows names itself in the message.
    """
    for rtl in sorted(FIXTURE.glob("*.sv")):
        flat = design.load_flat([str(rtl)], rtl.stem)
        clocks.reset_tree(flat)                  # must not raise
        for _, cell in design.registers(flat):
            has = [p for p, _, _ in clocks.RESET_PINS if p in cell.conns]
            claims = cell.type in (design.ASYNC_RESET_TYPES
                                   | design.SYNC_RESET_TYPES)
            assert bool(has) == claims, (rtl.stem, cell.type, has)


def test_an_asynchronous_load_is_not_reported_as_a_reset():
    """It forces another signal's value, so calling it a reset misstates it."""
    flat = design.load_flat([str(FIXTURE / "async_load.sv")], "async_load")
    resets = clocks.reset_tree(flat)
    assert resets["registers"]["dout"]["kind"] == "asynchronous load"
    assert resets["registers"]["dout"]["sources"] == ["load"]
    # The loaded value crosses a clock boundary, and arrives on AD.
    x = clocks.crossings(flat)
    assert [c["from"] for c in x["crossings"]] == ["staged"]
    assert x["unrecognized"]


def test_two_clocks_on_one_vector_port_are_two_clocks():
    """Names collide; nets do not, so identity is the net.

    Every bit of `input logic [1:0] lane_clk` carries the port's name, so a
    comparison of clock source *names* found one clock here and excused an
    eight-bit unsynchronized crossing between two asynchronous clocks from
    the build gate. A multi-lane block receiving one clock per lane on one
    port is ordinary, and it was the shape the tool was least able to see.
    """
    flat = design.load_flat([str(FIXTURE / "vector_clock.sv")],
                            "vector_clock")
    tree = clocks.clock_tree(flat)
    regs = tree["registers"]
    assert regs["stage"]["clock_sources"] == regs["dout"]["clock_sources"]
    assert regs["stage"]["root_bits"] != regs["dout"]["root_bits"]
    x = clocks.crossings(flat, tree)
    assert len(x["crossings"]) == 1
    assert not x["crossings"][0]["same_clock_source"]
    assert x["unrecognized"], "an asynchronous crossing must fail the gate"


def test_two_clocks_out_of_one_black_box_are_two_clocks():
    """The same collapse by the other route the chapter's definition names.

    A primary clock is a design input or the output of a block the netlist
    cannot see into. Both forms can carry two clocks on one net name, so
    fixing only the port half would have left the gate passing here.
    """
    flat = design.load_flat([str(FIXTURE / "blackbox_clocks.sv")],
                            "blackbox_clocks")
    tree = clocks.clock_tree(flat)
    regs = tree["registers"]
    assert regs["a"]["clock_sources"] == regs["b"]["clock_sources"]
    assert regs["a"]["root_bits"] != regs["b"]["root_bits"]
    x = clocks.crossings(flat, tree)
    assert not x["crossings"][0]["same_clock_source"]
    assert x["unrecognized"]


def test_same_clock_source_is_only_ever_claimed_of_one_net():
    """The flag that keeps a crossing out of the build gate, over everything.

    It is the only route by which a reported crossing is excused, so it is
    asserted across the whole directory rather than on the design that last
    broke it: it may be true only where both ends reached one identical
    clock net.
    """
    checked = 0
    for rtl in sorted(FIXTURE.glob("*.sv")):
        flat = design.load_flat([str(rtl)], rtl.stem)
        # With the clocks declared, because the flag can only ever be true
        # of a design whose gates resolved -- which is the point of
        # declaring them.
        tree = clocks.clock_tree(flat, _DECLARED.get(rtl.stem, ()))
        declared = _DECLARED.get(rtl.stem, ())
        for c in clocks.crossings(flat, tree, declared)["crossings"]:
            if not c["same_clock_source"]:
                continue
            ends = [tree["registers"][c["to"]]["root_bits"],
                    tree["registers"][c["from"]]["root_bits"]]
            assert len(ends[0]) == 1 and ends[0] == ends[1], (rtl.stem, c)
            checked += 1
    assert checked, "no fixture exercises the flag that excuses a crossing"


def test_a_crossing_onto_a_synchronous_clear_is_reported():
    """`opt_dff` folds `if (flag) q <= 0;` onto $sdff's SRST pin.

    That is the pass the tool runs so a synchronous reset is not missed, and
    it moved an ordinary one-bit control crossing off the data pins. Whether
    the tool saw a real crossing then depended on whether the receiving
    register happened to have an asynchronous reset as well.
    """
    flat = design.load_flat([str(FIXTURE / "sync_reset_crossing.sv")],
                            "sync_reset_crossing")
    x = clocks.crossings(flat)
    assert [c["from"] for c in x["crossings"]] == ["flag"]
    assert x["unrecognized"]


def test_per_bit_synchronizers_leaving_through_ports_are_rejected():
    """The convergence test was one register wide.

    Eight one-bit chains carrying one value were demoted only when some
    register downstream read them together, so a bus reassembled by whatever
    instantiates the block met no reader and all eight were reported as
    recognized synchronizers. The rule is now the boundary, not the reader.
    """
    flat = design.load_flat([str(FIXTURE / "parallel_bit_sync.sv")],
                            "parallel_bit_sync")
    x = clocks.crossings(flat)
    assert len(x["crossings"]) == 8
    assert not any(c["shape_recognized"] for c in x["crossings"])
    assert len(x["unrecognized"]) == 8
    assert "in parallel" in x["crossings"][0]["note"]


def test_a_lowered_array_points_at_its_declaration():
    """Not at the line its clock port was declared on.

    `memory_map` gives the registers it synthesizes no attributes at all, so
    each one borrowed a location from a net it touched, and the first net it
    found was the clock: sixteen registers all pointing at a port list. The
    location now comes from the array itself, recovered before the memory
    passes run, and it survives flattening, which prefixes the instance path
    onto every cell name.
    """
    for top, want in (("ram_crossing", {"mem": "logic [7:0] mem [16];"}),
                      ("sub_array",
                       {"u_store.ram": "logic [7:0] ram [16];"}),
                      # Two modules declaring an array of the same name are
                      # kept apart by the instance path, not merged into one
                      # ambiguous key and then dropped. Each register must
                      # land on the declaration in *its own* module, which
                      # is why the two expected lines differ only by the
                      # value assigned three lines below them.
                      ("two_arrays_one_name",
                       {"u_a.mem": "8'hAA", "u_b.mem": "8'hBB"})):
        flat = design.load_flat([str(FIXTURE / f"{top}.sv")], top)
        regs = clocks.reset_tree(flat)["no_reset"]
        lowered = [r for r in regs if "[" in r["name"]]
        assert lowered, top
        for r in lowered:
            key = r["name"].split("[")[0]
            assert key in want, (top, r)
            file, _, span = r["src"].partition(":")
            text = pathlib.Path(file).read_text().splitlines()
            first = int(span.split(".")[0]) - 1
            # The array declaration, or the three lines under it that say
            # which of the two modules this is.
            block = "\n".join(text[first:first + 4])
            assert want[key] in block, (top, r, block)


def test_a_tool_failure_is_not_reported_as_a_finding():
    """Three exit codes, kept apart: 0 clean, 1 findings, 2 cannot answer.

    A project that gates its build on this has to tell them apart, and an
    earlier version could not: an unreadable file and a register type the
    code had not anticipated both arrived as a Python traceback and exit 1,
    which is the code a crossing uses.
    """
    from dvh import cli                                    # noqa: PLC0415
    assert cli.main(["read", "nope", str(FIXTURE / "no_such_file.sv")]) == 2
    assert cli.main(["read", "gated_clock", "--clock", "clk",
                     str(FIXTURE / "gated_clock.sv")]) == 0
    assert cli.main(["read", "vector_clock",
                     str(FIXTURE / "vector_clock.sv")]) == 1


def test_a_clock_blended_with_a_divided_clock_is_two_clocks():
    """A register clocked by a clock is itself a clock, to any depth.

    The evidence heuristic counted a divider as a clock only where its
    output drove a clock pin with no logic between, which excludes every
    divider that feeds a gate -- so a clock blended with a divided clock
    scored as one clock gated differently and the crossing was excused.
    With the clocks declared the question is settled by definition, and the
    answer is that the gate has two clocks on it.
    """
    flat = design.load_flat([str(FIXTURE / "divided_blend.sv")],
                            "divided_blend")
    for declared in ((), ("clk1", "clk2")):
        x = clocks.crossings(flat, clocks.clock_tree(flat, declared),
                             declared)
        assert len(x["crossings"]) == 1, declared
        assert not x["crossings"][0]["same_clock_source"], declared
        assert x["unrecognized"], declared


def test_a_declaration_is_all_or_nothing():
    """A clock left out is reclassified as control, which can only remove
    findings, so a partial declaration was quieter than none at all -- and a
    misspelled one was the safest of the three. Both are now refused."""
    from dvh import cli                                    # noqa: PLC0415
    rtl = str(FIXTURE / "divided_blend.sv")
    assert cli.main(["read", "divided_blend", "--clock", "clk1", rtl]) == 2
    assert cli.main(["read", "divided_blend", "--clock", "nope", rtl]) == 2
    assert cli.main(["read", "divided_blend", rtl]) == 1
    assert cli.main(["read", "divided_blend", "--clock", "clk1",
                     "--clock", "clk2", rtl]) == 1
    assert clocks.clock_ports(
        design.load_flat([rtl], "divided_blend")) == {"clk1", "clk2"}


def test_per_bit_chains_with_different_clock_roots_are_one_boundary():
    """A gate whose enable the netlist cannot see into scored as highly as
    the clock beside it, so two chains off one clock reported different
    roots and the rule that groups them by boundary split them in two."""
    flat = design.load_flat([str(FIXTURE / "per_bit_mixed_roots.sv")],
                            "per_bit_mixed_roots")
    undeclared = clocks.crossings(flat)
    assert len(undeclared["crossings"]) == 2
    assert undeclared["unrecognized"], "an unresolved gate must be reported"
    told = clocks.crossings(flat, None, ("aclk", "bclk"))
    assert len(told["crossings"]) == 2
    assert not any(c["shape_recognized"] for c in told["crossings"])
    assert "in parallel" in told["crossings"][0]["note"]


def test_a_latch_at_the_end_of_a_crossing_is_reported():
    """A latch has no clock, so the domain that decides when the data is
    captured is its enable's. Eight bits leaving one domain into a latch
    held open by another's enable reported as a clean design, because the
    loop that asks about destinations only visited flip-flops."""
    flat = design.load_flat([str(FIXTURE / "latch_destination.sv")],
                            "latch_destination")
    x = clocks.crossings(flat, None, ("aclk", "bclk"))
    onto = [c for c in x["crossings"] if c["from"] == "a"]
    assert len(onto) == 1
    assert onto[0]["width"] == 8
    assert "latch" in onto[0]["note"]
    assert not onto[0]["shape_recognized"]
    assert x["unrecognized"]


def test_a_reset_net_is_walked_as_a_reset_not_as_a_clock():
    """Yosys builds an ordinary set/reset flop's SET and CLR nets out of
    multiplexers whose select carries the reset, and the clock walk skips a
    select because a select is not a clock. The reported reset source was a
    pair of constants, and neither reset signal was ever named."""
    flat = design.load_flat([str(FIXTURE / "set_reset_flop.sv")],
                            "set_reset_flop")
    reg = clocks.reset_tree(flat)["registers"]["q"]
    by_pin = {c["pin"]: c for c in reg["controls"]}
    assert by_pin["CLR"]["sources"] == ["r"]
    assert "s" in by_pin["SET"]["sources"]
    for c in reg["controls"]:
        assert not any("clock" in t for t in c["through"]), c


def test_a_register_with_only_an_asynchronous_load_has_no_reset():
    """It forces another signal's value, not a constant. The JSON said so
    and the human report said the design had no unreset registers."""
    flat = design.load_flat([str(FIXTURE / "async_load_only.sv")],
                            "async_load_only")
    resets = clocks.reset_tree(flat)
    assert [r["name"] for r in resets["no_reset"]] == ["q"]
    assert resets["registers"]["q"]["kind"] == "asynchronous load"


def test_keep_hierarchy_on_an_instance_is_stripped_too():
    """`-mod` reaches a module's attribute; the bare form reaches a cell's,
    and `flatten` honors either."""
    flat = design.load_flat([str(FIXTURE / "kept_instance.sv")],
                            "kept_instance")
    assert len(list(design.registers(flat))) == 2
    x = clocks.crossings(flat, None, ("aclk", "bclk"))
    assert [c["from"] for c in x["crossings"]] == ["u_lane.a"]
    assert x["unrecognized"]
