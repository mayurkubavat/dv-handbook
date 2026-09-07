"""Tests for the Chapter 3 tools on the book's own designs.

Each test states a fact the chapter prints, so a change to the design or
the tools that alters the fact fails here before it reaches the text.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from dvh import clocks, design, graph  # noqa: E402

RTL = ROOT / "examples" / "ch03-digital-design" / "rtl"
SOURCES = ("regblock.sv", "sync2.sv", "datapath.sv", "top.sv")
TWO_CLOCK = [str(RTL / f) for f in SOURCES]
FIFO = [str(ROOT / "examples" / "ch01-what-is-dv" / "rtl" / "fifo.sv")]


def test_two_clock_domains():
    tree = clocks.clock_tree(design.load_flat(TWO_CLOCK, "top"))
    assert set(tree["domains"]) == {"bclk", "cclk"}
    assert len(tree["domains"]["bclk"]) == 2          # en, cfg
    # cclk holds the synchronizer's two stages plus count, acc, last_cfg.
    assert len(tree["domains"]["cclk"]) == 5
    assert not any(r["gated_or_muxed"] for r in tree["registers"].values())


def test_one_register_without_reset():
    resets = clocks.reset_tree(design.load_flat(TWO_CLOCK, "top"))
    assert resets["no_reset"] == ["last_cfg"]
    for name, r in resets["registers"].items():
        assert r["kind"] == "asynchronous" and r["active"] == "low", name
    assert resets["registers"]["acc"]["sources"] == ["crst_n"]


def test_crossings_found_and_classified():
    flat = design.load_flat(TWO_CLOCK, "top")
    x = clocks.crossings(flat)
    unsync = {(c["from"], c["to"]) for c in x["unsynchronized"]}
    assert unsync == {("cfg_b", "acc"), ("cfg_b", "last_cfg")}
    sync = [c for c in x["crossings"] if c["synchronized"]]
    assert len(sync) == 1
    assert sync[0]["from"] == "en_b" and sync[0]["width"] == 1


def test_connection_graph_sees_parameterized_instance():
    mods = design.load_hier(TWO_CLOCK, "top")
    conn = graph.connections(mods, "top")
    assert set(conn["instances"]) == {"u_regs", "u_sync_en", "u_dp"}
    assert conn["instances"]["u_sync_en"] == "sync2"
    pairs = {(e["from"], e["to"]) for e in conn["edges"]}
    assert ("u_regs", "u_dp") in pairs and ("u_sync_en", "u_dp") in pairs


def test_single_clock_fifo_has_no_crossings():
    """The Chapter 1 FIFO is one clock domain, so there is nothing to cross."""
    flat = design.load_flat(FIFO, "fifo")
    tree = clocks.clock_tree(flat)
    assert list(tree["domains"]) == ["clk"]
    assert clocks.crossings(flat, tree)["crossings"] == []


def test_fifo_storage_array_reports_as_unreset_registers():
    """A storage array is registers with no reset, and the tool says so.

    The finding is correct and is not a bug: a FIFO's memory is not meant to
    reset. It is the reading of the report, not the report, that needs a
    person -- which is the chapter's point about what a tool can and cannot
    decide on its own.
    """
    resets = clocks.reset_tree(design.load_flat(FIFO, "fifo"))
    assert all(n.startswith("mem[") for n in resets["no_reset"])
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
        "  last_cfg",
        "crossings: 3, unsynchronized: 2",
        "  BUG  cfg_b (bclk) -> acc (cclk), 8 bits, no synchronizer",
        "  BUG  cfg_b (bclk) -> last_cfg (cclk), 8 bits, no synchronizer",
        "  ok   en_b (bclk) -> u_sync_en.meta (cclk), 1 bit, synchronizer",
        "instances: 3, connections: 15",
    ])


# --------------------------------------------------------------------------
# Limits the tools were once wrong about. Each of these designs defeated an
# earlier version of the walks, so each keeps its own file under tests/rtl.
# --------------------------------------------------------------------------
FIXTURE = pathlib.Path(__file__).parent / "rtl"


def test_clock_gate_does_not_create_a_domain():
    """A gate's enable is control, not a clock source.

    Treating it as a source puts the gated register in a domain of its own
    and then reports the ordinary synchronous path into it as a crossing,
    which would fail any real design that gates its clocks.
    """
    flat = design.load_flat([str(FIXTURE / "gated_clock.sv")], "gated_clock")
    tree = clocks.clock_tree(flat)
    assert list(tree["domains"]) == ["clk"]
    assert sorted(tree["domains"]["clk"]) == ["q_free", "q_gated"]
    assert "gated by en" in tree["registers"]["q_gated"]["through"]
    assert clocks.crossings(flat, tree)["unsynchronized"] == []


def test_crossing_through_a_mux_select_is_found():
    """A foreign register steering a multiplexer is a control crossing.

    The clock walk rightly ignores a select, because a select is not a
    clock. A data cone must follow it, or this design reports as clean.
    """
    flat = design.load_flat([str(FIXTURE / "mux_select.sv")], "mux_select")
    x = clocks.crossings(flat)
    found = [(c["from"], c["to"]) for c in x["unsynchronized"]]
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
    assert len(x["unsynchronized"]) == 8
    assert all("parallel one-bit synchronizers" in c["reason"]
               for c in x["unsynchronized"])


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
