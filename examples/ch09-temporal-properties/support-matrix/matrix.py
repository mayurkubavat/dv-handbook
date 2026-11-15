#!/usr/bin/env python3
"""matrix.py -- which assertion constructs each open tool handles,
measured.

Every row of the chapter's support tables comes from running one probe
under two simulators and, through SymbiYosys, under the two front ends
of Yosys. A probe is judged by its verdict, not by whether it compiled:
each holds a design that satisfies its assertion and, with the parameter
BAD set, one that violates it, so an assertion that a tool accepts and
then ignores shows as a failure it did not report. The tables are
rewritten on every run, so they cannot say something the tools no
longer do.

In simulation both designs are instantiated side by side and the probe
counts failures in action blocks and prints a PROBE line. In formal the
probe's `dut` is the top module and sby runs twice, expecting PASS
without BAD and FAIL with it.

  runs     the right verdict on both designs
  wrong    built and ran, but a verdict was wrong (what the probe or
           sby reported is kept)
  no run   built, then failed at run time
  no build did not compile (the first line of the tool's error is kept)
  n/a      the column does not apply to the row (the reason is kept)

Each row of probes.txt is `label | file | options`; the options are
`key=value` separated by `;`:

  sim=n/a: why        no simulation columns
  sim=errlimit        count default failure messages over two runs
  iv=n/a: why         no Icarus column
  formal=n/a: why     no formal columns
  vflags=FLAGS        more Verilator flags, where a row needs them
  mode=, depth=, engine=, multiclock=, aigsmt=   the .sby file's settings
  expect=GOOD,BAD     sby statuses expected (default PASS,FAIL)
  sbyexpect=fail      add `expect fail` and judge by the exit status
  v54                 also run under the next Verilator release
"""
import concurrent.futures
import os
import pathlib
import re
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
# The release after the book's pin, for the rows whose behaviour it
# changes. The column is left out when the binary is not there.
VNEXT = os.environ.get("VERILATOR_NEXT",
                       "/opt/verilator-5.054/bin/verilator")
DEPTH = "12"
ENGINE = "smtbmc z3"
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


def icarus(probe, flag=None):
    vvp = BUILD / (probe.stem + (flag or "") + ".vvp")
    cmd = ["iverilog", "-g2012"] + ([flag] if flag else [])
    rc, out = run(cmd + ["-o", str(vvp), str(probe)])
    if rc != 0:
        return classify(out, False)
    rc, out = run(["vvp", str(vvp)], cwd=BUILD)
    return classify(out, True)


def verilator(probe, binary, tag, mode, extra):
    mdir = BUILD / (tag + "_" + probe.stem + "".join(extra))
    rc, out = run([binary] + VFLAGS + extra
                  + ["--Mdir", str(mdir), str(probe)])
    if rc != 0:
        return classify(out, False)
    warned = "; warns NEVERMATCH" if "NEVERMATCH" in out else ""
    exe = str(mdir / "Vtop")
    if mode == "errlimit":
        return error_limit(exe, mdir)
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


def sby_file(front, probe, opts, bad):
    mode = opts.get("mode", "bmc")
    lines = ["[options]", "mode " + mode]
    if mode != "live":
        lines.append("depth " + opts.get("depth", DEPTH))
    if "multiclock" in opts:
        lines.append("multiclock " + opts["multiclock"])
    if "sbyexpect" in opts:
        lines.append("expect " + opts["sbyexpect"])
    if "aigsmt" in opts:
        lines.append("aigsmt " + opts["aigsmt"])
    engine = opts.get("engine", ENGINE)
    if engine != "none":
        lines += ["", "[engines]", engine]
    lines += ["", "[script]"]
    if front == "native":
        lines += [f"read -formal {probe.name}",
                  f"hierarchy -top dut -chparam BAD {bad}"]
    else:
        lines += [f"read_slang -D FORMAL -G BAD={bad} --top dut "
                  f"{probe.name}"]
    lines += ["prep -top dut", "", "[files]", str(probe)]
    return "\n".join(lines) + "\n"


def sby_error(out, work):
    """The first error of an sby run, and whether the front end raised
    it (no build) or a later step did (no run)."""
    # read_slang reports through slang, whose diagnostics are in the
    # design log and not in what sby prints.
    log = work / "model" / "design.log"
    if log.exists():
        m = re.search(r"^\S+:\d+:\d+: error: (.*)$", log.read_text(),
                      re.M)
        if m:
            return "no build", m.group(1)[:NOTE]
    for l in out.splitlines():
        m = re.search(r"\] (\w+): (?:.*?(?:ERROR|error): )?(.*)", l)
        if m and "ERROR" in l:
            where = "no build" if m.group(1) == "base" else "no run"
            msg = re.sub(r"^.*?:\d+(:\d+)?:\s*", "", m.group(2))
            # An internal error names a source line of the tool itself.
            msg = re.sub(r" at \S*/(\w+\.cc:\d+).*", r" (\1)", msg)
            if msg == "COMMAND NOT FOUND. ERROR.":
                msg = "the engine's solver is not installed"
            return where, msg.split("`")[0].rstrip(" :,.")[:NOTE]
    m = re.search(r"ERROR: (.*)", out)
    return "no run", (m.group(1) if m else "")[:NOTE]


def formal(front, probe, opts):
    want = opts.get("expect", "PASS,FAIL").split(",")
    got, rcs = [], []
    for bad in (0, 1):
        work = BUILD / f"{front}_{probe.stem}_{bad}"
        sby = work.with_suffix(".sby")
        sby.write_text(sby_file(front, probe, opts, bad))
        rc, out = run(["sby", "-f", "-d", str(work), str(sby)])
        m = re.search(r"DONE \((\w+), rc=(\d+)\)", out)
        status = m.group(1) if m else "ERROR"
        # Under `expect fail` sby still names the status; without the
        # option an error is the end of the row.
        if status == "ERROR":
            return sby_error(out, work)
        got.append(status)
        rcs.append(rc)
    said = "/".join(got)
    if "sbyexpect" in opts:
        ok = got == want and rcs[0] != 0 and rcs[1] == 0
        return ("runs" if ok else "wrong"), f"exit {rcs[0]} and {rcs[1]}"
    if got == want:
        return "runs", (said if want != ["PASS", "FAIL"] else "")
    return "wrong", f"{said}, want {'/'.join(want)}"


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
                       if vnext and "v54" in opts else ("", ""))
        if "iv" in opts:
            cells["iv"], cells["ivs"] = na(opts["iv"]), ("", "")
        else:
            cells["iv"] = icarus(probe)
            # What the flag Icarus's own message suggests then does.
            cells["ivs"] = (icarus(probe, "-gsupported-assertions")
                            if cells["iv"][0] == "no build" else ("", ""))
    if opts.get("formal", "").startswith("n/a"):
        cells["yn"] = cells["ys"] = na(opts["formal"])
    else:
        cells["yn"] = formal("native", probe, opts)
        cells["ys"] = formal("slang", probe, opts)
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
        nxt = f" next: {c['vn'][0]:8s}" if c["vn"][0] else ""
        print(f"{file[:3]} {label[:34]:34s} verilator: {c['v'][0]:8s} "
              f"icarus: {c['iv'][0]:8s} native: {c['yn'][0]:8s} "
              f"slang: {c['ys'][0]:8s}{nxt}")
    return rows


COLS = (("v", "Verilator"), ("iv", "Icarus"), ("yn", "Yosys native"),
        ("ys", "Yosys `read_slang`"))


def count(rows, col):
    n = {}
    for _, _, c in rows:
        if c[col][0]:
            n[c[col][0]] = n.get(c[col][0], 0) + 1
    order = ("runs", "wrong", "no run", "no build", "n/a")
    return ", ".join(f"{n[k]} {k}" for k in order if k in n)


def summary(rows, vnext):
    for col, name in COLS + ((("vn", "Verilator next"),) if vnext else ()):
        print(f"  {name}: {count(rows, col)}")
    skipped = [c["ivs"] for _, _, c in rows if c["ivs"][0]]
    if skipped:
        n = sum(1 for s in skipped if s[0] != "no build")
        w = sum(1 for s in skipped if s[0] == "wrong")
        print(f"  Icarus with -gsupported-assertions, on its {len(skipped)}"
              f" no-build rows: {n} build, {w} of them wrong")


def cell(c):
    verdict, why = c
    if not verdict:
        return "—"
    return verdict + (" — " + why.replace("|", "\\|") if why else "")


def table(rows, vers, vnext, what, label):
    head = [f"Verilator {vers['v']}"]
    cols = ["v"]
    if vnext:
        head.append(f"Verilator {vers['vn']}")
        cols.append("vn")
    head += [f"Icarus {vers['iv']}", f"Yosys {vers['y']} native",
             f"Yosys {vers['y']} `read_slang`"]
    cols += ["iv", "yn", "ys"]
    md = ["| Construct | " + " | ".join(head) + " |",
          "|---|" + "---|" * len(head)]
    for lab, _, c in rows:
        # A pipe ends a table cell even inside a code span.
        md.append(f"| {lab.replace('|', chr(92) + '|')} | "
                  + " | ".join(cell(c[k]) for k in cols) + " |")
    counts = "; ".join(f"{h}: {count(rows, k)}"
                       for h, k in zip(head, cols))
    md.append("")
    md.append(f": What each open tool does with {what}, measured by "
              "running one probe per row: under the simulators with the "
              "flags the book's build uses plus `--assert` and "
              "`-Wno-fatal` (Icarus with `-g2012`), and under SymbiYosys "
              f"{vers['sby']} through `read -formal` and through "
              f"`read_slang`, bounded model checking to depth {DEPTH} "
              "with `smtbmc z3` unless the row names another mode. Each "
              "probe holds a design that satisfies its assertion and one "
              "that violates it, and a row runs only if both verdicts "
              "are right. A dash is a row the newer Verilator was not "
              f"asked about. {counts}. Regenerated from the probes on "
              "every run. {#" + label + "}")
    return md


def versions(vnext):
    vers = {"v": run([VERILATOR, "--version"])[1].split()[1],
            "iv": run(["iverilog", "-V"])[1].splitlines()[0].split()[3],
            "y": run(["yosys", "-V"])[1].split()[1],
            "sby": run(["sby", "--version"])[1].split()[-1].lstrip("v")}
    if vnext:
        vers["vn"] = run([vnext, "--version"])[1].split()[1]
    return vers


def main():
    BUILD.mkdir(exist_ok=True)
    vnext = VNEXT if pathlib.Path(VNEXT).exists() else ""
    vers = versions(vnext)
    slang = "read_slang" in run(["yosys", "-h", "read_slang"])[1]
    print("verilator " + vers["v"] + ", icarus " + vers["iv"] + ", yosys "
          + vers["y"] + (" with" if slang else " without")
          + " read_slang, sby " + vers["sby"]
          + (", verilator " + vers["vn"] if vnext else ""))
    main_rows = measure("probes.txt", vnext)
    print(f"{len(main_rows)} constructs")
    summary(main_rows, vnext)
    x_rows = measure("probes-x.txt", vnext)
    print(f"{len(x_rows)} more")
    summary(x_rows, vnext)
    md = table(main_rows, vers, vnext,
               "the assertion constructs this chapter teaches",
               "tbl-ch09-support")
    md.append("")
    md += table(x_rows, vers, vnext,
                "the second set of assertion probes: the forms the "
                "native Yosys front end documents, and discriminating "
                "probes", "tbl-ch09-support-x")
    (HERE / "matrix.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
