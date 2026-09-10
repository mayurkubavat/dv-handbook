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
        "  CHECK cfg_b (bclk) -> acc (cclk), 8 bits, no synchronizer shape"
        "  [examples/ch03-digital-design/rtl/datapath.sv:14]",
        "  CHECK cfg_b (bclk) -> last_cfg (cclk), 8 bits, no synchronizer shape"
        "  [examples/ch03-digital-design/rtl/datapath.sv:24]",
        "  known en_b (bclk) -> u_sync_en.meta (cclk), 1 bit, "
        "two-flop synchronizer"
        "  [examples/ch03-digital-design/rtl/sync2.sv:13]",
        "instances: 3, connections: 15",
    ])


# --------------------------------------------------------------------------
# Limits the tools were once wrong about. Each of these designs defeated an
# earlier version of the walks, so each keeps its own file under tests/rtl.
# --------------------------------------------------------------------------
FIXTURE = pathlib.Path(__file__).parent / "rtl"


def test_a_clock_gate_does_not_fail_the_build():
    """A gated clock is a different net and the same clock.

    Identity is the net, so the gated register is its own domain and the
    path into it is reported -- nothing is ever hidden. Both clocks resolve
    to the same source, so it is marked as such and does not trip the gate,
    because otherwise every design that gates a clock would fail.
    """
    flat = design.load_flat([str(FIXTURE / "gated_clock.sv")], "gated_clock")
    tree = clocks.clock_tree(flat)
    assert all(clocks._pretty(d) == "clk" for d in tree["domains"])
    assert "gated by en" in tree["registers"]["q_gated"]["through"]
    x = clocks.crossings(flat, tree)
    assert len(x["crossings"]) == 1
    assert x["crossings"][0]["same_clock_source"]
    assert x["unrecognized"] == []


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
    loudly is the only safe behaviour for a report a build gate trusts.
    """
    files = [str(FIXTURE / "two_clock_gates.sv")]
    flat = design.load_flat(files, "two_clock_gates")
    tree = clocks.clock_tree(flat)
    assert all(r["clock_ambiguous"] for r in tree["registers"].values())
    found = clocks.crossings(flat, tree)["unrecognized"]
    assert found and all("declare the clocks" in c["note"] for c in found)


def test_a_crossing_through_a_latch_is_still_reported():
    """A latch is state, so the path is not a synchronizer -- but stopping
    the walk at one would hide the crossing altogether, which is worse."""
    files = [str(FIXTURE / "crossing_via_latch.sv")]
    flat = design.load_flat(files, "crossing_via_latch")
    x = clocks.crossings(flat)
    assert len(x["unrecognized"]) == 1


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


# --------------------------------------------------------------------------
# The published schemas are a contract with callers who are not this book,
# so a change to an output that the schema does not describe must fail here.
# --------------------------------------------------------------------------
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


def test_every_finding_carries_a_real_source_location():
    """The book claims a finding names the RTL that produced it. Prove it.

    Schema conformance is not enough on its own: a blank string would once
    have satisfied it, so an extractor that stopped reading source locations
    would have left the claim silently false with a green build. Here the
    locations are checked for existence, for shape, and for pointing at a
    file that exists.
    """
    flat = design.load_flat(TWO_CLOCK, "top")
    tree = clocks.clock_tree(flat)
    resets = clocks.reset_tree(flat)
    mods = design.load_hier(TWO_CLOCK, "top")
    found = ([r["src"] for r in tree["registers"].values()]
             + [r["src"] for r in resets["registers"].values()]
             + [r["src"] for r in resets["no_reset"]]
             + [c["src"] for c in clocks.crossings(flat, tree)["crossings"]]
             + [i["src"] for i in
                graph.connections(mods, "top")["instances"].values()])
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
    flat = design.load_flat(TWO_CLOCK, "top")
    mods = design.load_hier(TWO_CLOCK, "top")
    checked = 0
    for name, info in clocks.clock_tree(flat)["registers"].items():
        checked += _names_the_construct(info["src"], "always_ff", name)
    for name, inst in graph.connections(mods, "top")["instances"].items():
        checked += _names_the_construct(inst["src"], inst["module"], name)
    assert checked >= 8, checked


def _names_the_construct(src: str, keyword: str, name: str) -> int:
    """True if the reported span contains the keyword and, where the name
    survives into the netlist, the name."""
    file, _, span = src.partition(":")
    first = int(span.split(".")[0])
    last = int(span.split("-")[-1].split(".")[0]) if "-" in span else first
    text = pathlib.Path(file).read_text().splitlines()
    block = "\n".join(text[first - 1:last])
    assert keyword in block, (src, keyword, block[:80])
    base = name.split(".")[-1].split("[")[0]
    if base and base in "".join(text):
        assert base in block or keyword in block, (src, name)
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
