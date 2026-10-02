#!/usr/bin/env python3
"""matrix.py -- which functional-coverage constructs each open simulator
runs, measured.

Every row of the chapter's support tables comes from running a probe under
both simulators, with the flags the book's build uses plus `--coverage`
and `-Wno-fatal`, and checking the percentage the probe prints -- not only
whether it compiled. The tables are rewritten on every run, so they
cannot say something the tools no longer do.

  runs     compiled, ran, and printed the percentage the standard gives
  wrong    compiled and ran, but printed a percentage the probe did not
           expect (or, for an illegal bin, did not stop)
  no run   compiled, then failed at run time
  no build did not compile (the first line of the tool's error is kept)
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
# The book's flags, plus --coverage so the bins also reach coverage.dat,
# plus -Wno-fatal: a lint warning is not a refusal of the construct, and
# the table measures what the language support is, not whether a probe
# is lint-clean.
VERILATOR = ["verilator", "--binary", "--timing", "--timescale", "1ns/1ps",
             "-Wall", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "-Wno-fatal",
             "--coverage", "--top-module", "top"]


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def classify(rc, out, build_ok):
    if not build_ok:
        err = next((l for l in out.splitlines()
                    if ("error" in l.lower() or "sorry" in l.lower())
                    and "Exiting due" not in l), "")
        # Keep the message, not the path and line that precede it.
        err = re.sub(r"^.*?:\d+(:\d+)?:\s*", "", err.strip())
        err = re.sub(r"^(%Error(-\w+)?|error|sorry):\s*", "", err)
        # A compiler that prints a type's internals after a backtick has
        # said what matters before it.
        err = err.split("`")[0].rstrip(" :,")
        return "no build", err[:56]
    if re.search(r"PROBE .* PASS", out):
        return "runs", ""
    if re.search(r"PROBE .* FAIL", out):
        return "wrong", ""
    return "no run", ""


def icarus(probe):
    vvp = BUILD / (probe.stem + ".vvp")
    rc, out = run(["iverilog", "-g2012", "-o", str(vvp), str(probe)])
    if rc != 0:
        return classify(rc, out, False)
    rc, out = run(["vvp", str(vvp)], cwd=BUILD)
    return classify(rc, out, True)


def verilator(probe):
    mdir = BUILD / ("v_" + probe.stem)
    rc, out = run(VERILATOR + ["--Mdir", str(mdir), str(probe)])
    if rc != 0:
        return classify(rc, out, False)
    # Run inside the build directory so each probe's coverage.dat lands
    # there and not in the example's directory.
    rc, out = run([str(mdir / "Vtop")], cwd=mdir)
    return classify(rc, out, True)


def versions():
    v = run(["verilator", "--version"])[1].split()[1]
    i = run(["iverilog", "-V"])[1].splitlines()[0].split()[3]
    return v, i


def measure(listing):
    rows = []
    for line in (HERE / listing).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        label, file = [x.strip() for x in line.split("|")]
        probe = HERE / "probes" / file
        iv, iv_why = icarus(probe)
        vl, vl_why = verilator(probe)
        rows.append((label, iv, iv_why, vl, vl_why))
        print(f"{file[:3]} {label[:42]:42s} icarus: {iv:9s} verilator: {vl}")
    both = sum(1 for r in rows if r[1] == "runs" and r[3] == "runs")
    vonly = sum(1 for r in rows if r[1] != "runs" and r[3] == "runs")
    ionly = sum(1 for r in rows if r[1] == "runs" and r[3] != "runs")
    neither = len(rows) - both - vonly - ionly
    wrong = sum(1 for r in rows if r[3] == "wrong")
    print(f"{len(rows)} constructs: {both} run on both, {vonly} on "
          f"Verilator only, {ionly} on Icarus only, {neither} on neither; "
          f"{wrong} wrong on Verilator")
    return rows, (both, vonly, ionly, neither, wrong)


def table(rows, counts, vver, iver, what, label):
    both, vonly, ionly, neither, wrong = counts
    md = ["| Construct | Icarus " + iver + " | Verilator " + vver + " |",
          "|---|---|---|"]
    for lab, iv, iw, vl, vw in rows:
        md.append(f"| {lab} | {iv}{' — ' + iw if iw else ''} | "
                  f"{vl}{' — ' + vw if vw else ''} |")
    md.append("")
    md.append(f": What each open simulator does with {what}, measured by "
              "running one probe per row with the flags the book's build "
              "uses plus `--coverage` and `-Wno-fatal`, and checking the "
              "printed percentage against the one the standard gives. Of "
              f"{len(rows)} constructs, {both} run on both, {vonly} on "
              f"Verilator only, {ionly} on Icarus only and {neither} on "
              f"neither; {wrong} run on Verilator and print a wrong "
              "percentage. Regenerated from the probes on every run. "
              "{#" + label + "}")
    return md


def main():
    BUILD.mkdir(exist_ok=True)
    main_rows, main_counts = measure("probes.txt")
    x_rows, x_counts = measure("probes-x.txt")
    vver, iver = versions()
    md = table(main_rows, main_counts, vver, iver,
               "the functional-coverage constructs this chapter teaches",
               "tbl-ch08-support")
    md.append("")
    md += table(x_rows, x_counts, vver, iver,
                "the second set of functional-coverage probes: crosses "
                "judged through the group, and discriminating probes",
                "tbl-ch08-support-x")
    (HERE / "matrix.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
