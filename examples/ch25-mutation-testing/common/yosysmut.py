"""yosysmut.py -- the netlist fault model of MCY, run with Yosys alone.

After `prep`, Yosys's `mutate -list N` lists single-bit mutations of
the netlist's cell ports. With N above the population it lists every
one (and warns how many it could make): that list is the population.
With `-ctrl mutsel 14 K` each listed command puts its mutation behind
value K of a 14-bit select input, value 0 being the unmutated design,
so a netlist holding many mutations is built once and each run picks
one: the schema idea of Untch, Offutt and Harrold, as MCY applies it.

Yosys runs from the repository root and reads fifo_fixed.sv by its
path from there, because the cell names in the list carry that path:
the committed population file names mutations by their number in this
list, and the list must come out the same on every machine.

  population(work)          the list: [command] with [0] the 'none'
                            entry, and Yosys's warning line
  parse(cmd)                (mode, source line, cell type)
  uniform(N, n, seed)       mutation numbers of a uniform sample
  select_netlist(cmds, out) a netlist, module fifo_mut, with the
                            given mutations behind mutsel
  single_netlist(cmd, out)  one mutation applied, module fifo_m
"""
import random
import re
import subprocess

from mutlib import FIXED, ROOT, rel

READ = f"read_verilog -sv {FIXED}; prep -top fifo"


def yosys(script):
    p = subprocess.run(["yosys", "-q", "-p", script], cwd=ROOT,
                       capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("yosys failed:\n" + (p.stdout + p.stderr)[-2000:])
    return p.stdout + p.stderr


def population(work):
    """Every mutation `mutate -list` makes of the prepped FIFO."""
    out = work / "list.txt"
    log = yosys(f"{READ}; mutate -list 100000 -seed 1 -none -ctrl "
                f"mutsel 14 0 -o {rel(out)}")
    warn = [x for x in log.splitlines() if "mutations requested" in x]
    cmds = out.read_text().splitlines()
    assert "-mode none" in cmds[0]
    return cmds, warn[0] if warn else ""


def parse(cmd):
    """(mode, source line, cell type) of one `mutate` command; '-'
    where the command has no source tag or no cell."""
    mode = re.search(r"-mode (\w+)", cmd).group(1)
    src = re.search(r"-src \S*?:(\d+)\.", cmd)
    cell = re.search(r"-cell \$(\w+)\$", cmd)
    return (mode, src.group(1) if src else "-",
            cell.group(1) if cell else "-")


def uniform(N, n, seed):
    """Mutation numbers (1..N) of a uniform sample of n without
    replacement, from Python's generator at SEED. For a fixed seed
    the first k numbers of a sample of n are the sample of k, for the
    sizes used here (random.sample draws them one at a time), so the
    samples at 30, 100, 300 and 1000 are nested."""
    return [j + 1 for j in random.Random(seed).sample(range(N), n)]


def select_netlist(cmds, out):
    """Write OUT, module fifo_mut: the FIFO with the mutations CMDS
    (commands from the list, numbers kept) behind mutsel."""
    ys = out.with_suffix(".ys")
    body = [f"read_verilog -sv {FIXED}", "prep -top fifo",
            "rename fifo fifo_mut"]
    body += [c.replace("-module fifo ", "-module fifo_mut ")
             for c in cmds]
    body += ["opt_clean", f"write_verilog -noattr {rel(out)}"]
    ys.write_text("\n".join(body) + "\n")
    p = subprocess.run(["yosys", "-q", "-s", rel(ys)], cwd=ROOT,
                       capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("yosys failed:\n" + (p.stdout + p.stderr)[-2000:])
    return out


def single_netlist(cmd, out):
    """Write OUT, module fifo_m: the FIFO with the one mutation CMD
    applied directly (no select)."""
    cmd = re.sub(r"-ctrl mutsel 14 \d+ ", "", cmd.strip())
    yosys(f"{READ}; {cmd}; rename fifo fifo_m; "
          f"write_verilog -noattr {rel(out)}")
    return out


# Verilator flags for a Yosys netlist: its style draws lint warnings
# that say nothing about the design, so they are not fatal; and
# --no-assert-case, because Yosys writes each $pmux as a casez marked
# "synopsys parallel_case", which Verilator turns into an assertion: a
# mutation of a select bit would then fail in any testbench, a kill by
# the harness (harness-pitfalls/). Concurrent assertions, the
# temporal-properties chapter's checker among them, stay on.
NET_FLAGS = ["-Wno-fatal", "-Wno-lint", "-Wno-style", "--no-assert-case"]
# The coverage chapter's testbench is built with --coverage-user, not
# --coverage: its covergroups report the same percentages, and line
# and toggle points over a large netlist slow every run.
NET_TB_FLAGS = {"ch08-coverage": ["--coverage-user"]}


def build_netlist(bdir, netlist, names, tbs=None, flags=NET_FLAGS):
    """Build each testbench of NAMES against NETLIST (module fifo_mut)
    and common/fifo_wrap.sv. Returns {name: build directory}."""
    import mutlib
    from mutlib import HERE
    design = [netlist, HERE / "fifo_wrap.sv"]
    tbs = tbs or mutlib.TBS

    def one(tb):
        own = tbs[tb][2]
        fl = NET_TB_FLAGS.get(tb, own)
        return mutlib.build(tb, design, bdir / tb, flags, fl, tbs=tbs)
    res = mutlib.pmap(one, names)
    for tb, (ok, _, log) in zip(names, res):
        if not ok:
            raise SystemExit(f"netlist build of {tb} failed:\n"
                             + log[-2000:])
    return {tb: bdir / tb for tb in names}


def run_netlist(dirs, ids, tbs=None, workers=4):
    """{(id, tb): verdict} for every mutation number in IDS."""
    import mutlib
    jobs = [(k, tb) for k in ids for tb in dirs]
    out = mutlib.pmap(lambda j: mutlib.run(j[1], dirs[j[1]],
                                           [f"+mut={j[0]}"], tbs=tbs)[0],
                      jobs, workers)
    return dict(zip(jobs, out))
