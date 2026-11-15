#!/usr/bin/env python3
"""matrix.py -- which assertion constructs each open tool handles,
measured.

Every row of the chapter's support tables comes from running one probe
under two simulators, on two releases of one of them, and under the
formal tool InFormal. A probe is judged by its verdict, not by whether
it compiled: each holds a design that satisfies its assertion and, with
the parameter BAD set, one that violates it, so an assertion that a
tool accepts and then ignores shows as a failure it did not report.
The tables are rewritten on every run, so they cannot say something
the tools no longer do.

In simulation both designs are instantiated side by side and the probe
counts failures in action blocks and prints a PROBE line. Under
InFormal the probe's `dut` is the top module and the same file is read
twice with FORMAL defined (which compiles out the simulation top and
the failure counters), with BAD 0 and with BAD 1: every assertion
must be proven in the first and at least one refuted in the second
(for a cover row: every cover reached in the first, one unreachable in
the second). The tool has no depth bound, so where a probe has the
tick counter `t` the script assumes `t < 14`, which ends every trace
where the simulation's fourteen ticks end.

  runs     the right verdict on both designs
  wrong    built and ran, but a verdict was wrong (what the probe or
           the tool reported is kept)
  no run   built, then failed at run time
  no build did not compile, or the tool named the construct as one it
           does not support (the first line of its message is kept)
  n/a      the column does not apply to the row (the reason is kept)

Each row of probes.txt is `label | file | options`; the options are
`key=value` separated by `;`:

  sim=n/a: why        no simulation columns
  sim=errlimit        count default failure messages over two runs
  sim=status          one failure with no action block: was it printed,
                      did the run go on, and what was the exit status
  iv=n/a: why         no Icarus column
  formal=n/a: why     no InFormal column
  vflags=FLAGS        more Verilator flags, where a row needs them
  mode=cover          judge the covers, not the assertions
  mode=live           a liveness row: no assumption that ends the trace
  engine=NAME         the InFormal engine (default informal-kind)
"""
import concurrent.futures
import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
# The book's flags, plus --assert (the default since 5.038, stated so
# that the table does not depend on it), plus -Wno-fatal: a lint warning
# is not a refusal of the construct, and the table measures what the
# language support is, not whether a probe is lint-clean.
VFLAGS = ["--binary", "--timing", "--timescale", "1ns/1ps",
          "-Wall", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "-Wno-fatal",
          "--assert", "--top-module", "top"]
VERILATOR = "verilator"
# The release after the book's pin. The tables need every column, so
# the run stops, and leaves matrix.md alone, when a tool is missing.
VNEXT = os.environ.get("VERILATOR_NEXT",
                       "/opt/verilator-5.054/bin/verilator")
# InFormal: one engine for each run and a time limit, so that two runs
# give the same cells. The engine list is the book's (it names no
# external engine).
INFORMAL = shutil.which("informal")
ENGINES = HERE.parents[1] / "mk" / "informal-engines.toml"
ENGINE = "informal-kind"
LIMIT = "20s"
LAST_TICK = "14"
NOTE = 56


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def first_error(out):
    err = next((l for l in out.splitlines()
                if ("error" in l.lower() or "sorry" in l.lower())
                and "Exiting due" not in l
                and "not runnable" not in l), "")
    # Keep the message, not the path and line that precede it.
    err = re.sub(r"^.*?:\d+(:\d+)?:\s*", "", err.strip())
    err = re.sub(r"^(%Error(-\w+)?|ERROR|Error|error|sorry):\s*", "", err)
    err = re.sub(r"^.*?:\d+(:\d+)?:\s*", "", err)
    # A compiler that prints a type's internals after a backtick has
    # said what matters before it.
    err = err.split("`")[0].rstrip(" :,")
    return err[:NOTE]


def classify(out, build_ok):
    if not build_ok:
        return "no build", first_error(out)
    m = re.search(r"PROBE \w+ (PASS|FAIL) ?(.*)", out)
    if not m:
        return "no run", first_error(out)
    return ("runs" if m.group(1) == "PASS" else "wrong"), m.group(2)[:NOTE]


def icarus(probe, flag=None, mode="run"):
    vvp = BUILD / (probe.stem + (flag or "") + ".vvp")
    cmd = ["iverilog", "-g2012"] + ([flag] if flag else [])
    rc, out = run(cmd + ["-o", str(vvp), str(probe)])
    if rc != 0:
        return classify(out, False)
    if mode == "status":
        return exit_status(["vvp", str(vvp)], BUILD)
    rc, out = run(["vvp", str(vvp)], cwd=BUILD)
    return classify(out, True)


def verilator(probe, binary, tag, mode, extra):
    mdir = BUILD / (tag + "_" + probe.stem + "".join(extra))
    # Built from nothing every time: Verilator skips an unchanged input
    # and then prints no warnings, and a warning is part of the cell.
    shutil.rmtree(mdir, ignore_errors=True)
    rc, out = run([binary] + VFLAGS + extra
                  + ["--Mdir", str(mdir), str(probe)])
    if rc != 0:
        return classify(out, False)
    warned = "; warns NEVERMATCH" if "NEVERMATCH" in out else ""
    exe = str(mdir / "Vtop")
    if mode == "errlimit":
        return error_limit(exe, mdir)
    if mode == "status":
        return exit_status([exe], mdir)
    rc, out = run([exe], cwd=mdir)
    verdict, why = classify(out, True)
    return verdict, (why + warned).lstrip("; ")


def error_limit(exe, mdir):
    """Two assertions fail: how many does a run report, and does it
    reach its end, by default and with the limit raised to 10?"""
    seen = []
    for args in ([], ["+verilator+error+limit+10"]):
        rc, out = run([exe] + args, cwd=mdir)
        seen.append((out.count("Assertion failed"),
                     "PROBE" in out, rc != 0))
    why = (f"default {seen[0][0]} reported, "
           f"{'stops' if not seen[0][1] else 'runs on'}; "
           f"limit 10: {seen[1][0]}, "
           f"{'stops' if not seen[1][1] else 'runs on'}")
    ok = seen[0][:2] == (1, False) and seen[1][:2] == (2, True)
    return ("runs" if ok else "wrong"), why


def exit_status(cmd, cwd):
    """One assertion with no action block fails: was the failure
    printed, did the run reach its end, and what was the exit status?"""
    rc, out = run(cmd, cwd=cwd)
    told = re.search(r"Assertion failed|^ERROR:", out, re.M) is not None
    why = (f"failure {'printed' if told else 'not printed'}, run "
           f"{'goes on' if 'PROBE' in out else 'stops'}, exit status {rc}")
    return ("runs" if told else "wrong"), why


def informal_run(probe, opts, bad):
    """One InFormal run of a probe; returns (rows, error). A row is
    (name, kind, status, detail) from the report's table."""
    work = BUILD / f"informal_{probe.stem}_{bad}"
    work.mkdir(exist_ok=True)
    lines = [f"analyze -sv12 +define+FORMAL {probe}",
             f"elaborate -top dut -parameter BAD {bad}",
             "clock clk", "reset -none"]
    if opts.get("mode") != "live":
        lines.append("catch {assume -name End_M {t < 4'd" + LAST_TICK + "}}")
    lines += ["informal::set_engines " + opts.get("engine", ENGINE),
              "set_prove_time_limit " + LIMIT, "prove -all"]
    script = work / "probe.tcl"
    script.write_text("\n".join(lines) + "\n")
    rc, out = run([INFORMAL, "shell", "--engines", str(ENGINES),
                   "--workdir", str(work), str(script)])
    if rc != 0:
        return [], first_error(out)
    rows = []
    for line in out.splitlines():
        m = re.match(r"(\S+)\s+(assert|cover)\s+(\w+)\s*(.*)", line)
        if m:
            rows.append(m.groups())
    return rows, ""


def formal(probe, opts):
    kind = "cover" if opts.get("mode") == "cover" else "assert"
    want = (("covered", "unreachable") if kind == "cover"
            else ("proven", "cex"))
    said = []
    for bad in (0, 1):
        rows, err = informal_run(probe, opts, bad)
        if err:
            return "no build", err
        mine = [r for r in rows if r[1] == kind]
        if not mine:
            return "wrong", f"no {kind} in the report, and no message"
        refused = [r for r in mine if r[2] == "error"]
        if refused:
            why = re.sub(r"^not supported yet: ", "", refused[0][3])
            return "no build", ("not supported yet: " + why)[:NOTE]
        status = [r[2] for r in mine]
        if bad == 0:
            said.append(want[0] if all(x == want[0] for x in status)
                        else next(x for x in status if x != want[0]))
        else:
            said.append(want[1] if want[1] in status else status[0])
    if tuple(said) == want:
        return "runs", ""
    return "wrong", f"{'/'.join(said)}, want {'/'.join(want)}"


def options(text):
    opts = {}
    for item in text.split(";"):
        key, _, value = item.strip().partition("=")
        if key:
            opts[key] = value.strip()
    return opts


def na(value):
    return ("n/a", value.partition(":")[2].strip())


def probe_row(label, file, opts, vnext):
    probe = HERE / "probes" / file
    sim = opts.get("sim", "run")
    cells = {}
    if sim.startswith("n/a"):
        cells["v"] = cells["vn"] = cells["iv"] = na(sim)
        cells["ivs"] = ("", "")
    else:
        extra = opts.get("vflags", "").split()
        cells["v"] = verilator(probe, VERILATOR, "v", sim, extra)
        cells["vn"] = (verilator(probe, vnext, "vn", sim, extra)
                       if vnext else ("", ""))
        if "iv" in opts:
            cells["iv"], cells["ivs"] = na(opts["iv"]), ("", "")
        else:
            cells["iv"] = icarus(probe, mode=sim)
            # What the flag Icarus's own message suggests then does.
            cells["ivs"] = (icarus(probe, "-gsupported-assertions")
                            if cells["iv"][0] == "no build" else ("", ""))
    if opts.get("formal", "").startswith("n/a"):
        cells["f"] = na(opts["formal"])
    else:
        cells["f"] = formal(probe, opts) if INFORMAL else ("", "")
    return label, file, cells


def measure(listing, vnext):
    todo = []
    for line in (HERE / listing).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split(" | ")]
        todo.append((parts[0], parts[1],
                     options(parts[2] if len(parts) > 2 else "")))
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as pool:
        rows = list(pool.map(lambda t: probe_row(*t, vnext), todo))
    for label, file, c in rows:
        print(f"{file[:3]} {label[:30]:30s} verilator: {c['v'][0]:8s} "
              f"next: {c['vn'][0]:8s} icarus: {c['iv'][0]:8s} "
              f"informal: {c['f'][0]:8s}".rstrip())
    return rows


def columns(vnext):
    cols = [("v", "Verilator")]
    if vnext:
        cols.append(("vn", "Verilator next"))
    cols.append(("iv", "Icarus"))
    if INFORMAL:
        cols.append(("f", "InFormal"))
    return cols


def count(rows, col):
    n = {}
    for _, _, c in rows:
        if c[col][0]:
            n[c[col][0]] = n.get(c[col][0], 0) + 1
    order = ("runs", "wrong", "no run", "no build", "n/a")
    return ", ".join(f"{n[k]} {k}" for k in order if k in n)


def flag_counts(rows):
    """What Icarus's -gsupported-assertions does with the rows it
    refused: how many were tried, how many build, how many are wrong."""
    tried = [c["ivs"] for _, _, c in rows if c["ivs"][0]]
    n = sum(1 for s in tried if s[0] != "no build")
    w = sum(1 for s in tried if s[0] == "wrong")
    return len(tried), n, w


def summary(rows, vnext):
    for col, name in columns(vnext):
        print(f"  {name}: {count(rows, col)}")
    tried, n, w = flag_counts(rows)
    if tried:
        print(f"  Icarus with -gsupported-assertions, on its {tried}"
              f" no-build rows: {n} build, {w} of them wrong")


def cell(c):
    verdict, why = c
    return verdict + (" — " + why.replace("|", "\\|") if why else "")


def table(rows, vers, vnext, what, label):
    names = {"v": f"Verilator {vers['v']}",
             "vn": f"Verilator {vers.get('vn', '')}",
             "iv": f"Icarus {vers['iv']}",
             "f": f"InFormal {vers.get('f', '')}"}
    cols = [k for k, _ in columns(vnext)]
    head = [names[k] for k in cols]
    md = ["| Construct | " + " | ".join(head) + " |",
          "|---|" + "---|" * len(head)]
    for lab, _, c in rows:
        # A pipe ends a table cell even inside a code span.
        md.append(f"| {lab.replace('|', chr(92) + '|')} | "
                  + " | ".join(cell(c[k]) for k in cols) + " |")
    counts = "; ".join(f"{h}: {count(rows, k)}"
                       for h, k in zip(head, cols))
    tried, n, w = flag_counts(rows)
    if tried:
        counts += (f". With `-gsupported-assertions`, tried on its {tried}"
                   f" no-build rows, Icarus builds {n}, and {w} of those"
                   " give a wrong verdict")
    md.append("")
    md.append(f": What each tool does with {what}, measured by "
              "running one probe per row: under the simulators with the "
              "flags the book's build uses plus `--assert` and "
              "`-Wno-fatal` (Icarus with `-g2012`), and under InFormal "
              f"with the engine `{ENGINE}` (`informal-ic3` on the two "
              f"liveness rows), a limit of {LIMIT[:-1]} s for each "
              "property, no reset, and the probe's tick counter assumed "
              f"to stay below {LAST_TICK}. Each probe holds a design that "
              "satisfies its assertion and one that violates it, and a "
              "row runs only if both verdicts are right. "
              f"{counts}. Regenerated from the probes on every run. "
              "{#" + label + "}")
    return md


def versions(vnext):
    vers = {"v": run([VERILATOR, "--version"])[1].split()[1],
            "iv": run(["iverilog", "-V"])[1].splitlines()[0].split()[3]}
    if vnext:
        vers["vn"] = run([vnext, "--version"])[1].split()[1]
    if INFORMAL:
        vers["f"] = run([INFORMAL, "--version"])[1].split()[1]
    return vers


def missing(vnext):
    gone = [t for t in (VERILATOR, "iverilog", "vvp") if not shutil.which(t)]
    return gone + ([] if vnext else [VNEXT]) + ([] if INFORMAL
                                                else ["informal"])


def main():
    BUILD.mkdir(exist_ok=True)
    vnext = VNEXT if pathlib.Path(VNEXT).exists() else ""
    if missing(vnext):
        print("matrix.py: not measured, and matrix.md left as it is: "
              "missing " + ", ".join(missing(vnext)), file=sys.stderr)
        return 1
    vers = versions(vnext)
    print("verilator " + vers["v"] + ", icarus " + vers["iv"]
          + (", verilator " + vers["vn"] if vnext else "")
          + (", informal " + vers["f"] if INFORMAL else ""))
    main_rows = measure("probes.txt", vnext)
    print(f"{len(main_rows)} constructs")
    summary(main_rows, vnext)
    x_rows = measure("probes-x.txt", vnext)
    print(f"{len(x_rows)} more")
    summary(x_rows, vnext)
    md = table(main_rows, vers, vnext,
               "the assertion constructs this chapter names",
               "tbl-ch09-support")
    md.append("")
    md += table(x_rows, vers, vnext,
                "the second set of assertion probes: the clocked "
                "immediate forms, and discriminating probes",
                "tbl-ch09-support-x")
    (HERE / "matrix.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
