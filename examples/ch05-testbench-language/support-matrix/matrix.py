#!/usr/bin/env python3
"""matrix.py -- which testbench constructs each open simulator runs, measured.

Every row of the chapter's support table comes from running a probe under
both simulators, with the flags the book's build uses, and checking the
values the probe prints -- not only whether it compiled. The table is
rewritten on every run, so it cannot say something the tools no longer do.

  runs     compiled, ran, and printed the values the probe expected
  wrong    compiled and ran, but printed a value the probe did not expect
  no run   compiled, then failed at run time
  no build did not compile (the first line of the tool's error is kept)
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
# The book's flags, plus -Wno-fatal: a lint warning is not a refusal of the
# construct, and the table measures what the language support is, not
# whether a probe is lint-clean.
VERILATOR = ["verilator", "--binary", "--timing", "--timescale", "1ns/1ps",
             "-Wall", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "-Wno-fatal",
             "--top-module", "top"]


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
    rc, out = run(["vvp", str(vvp)])
    return classify(rc, out, True)


def verilator(probe):
    mdir = BUILD / ("v_" + probe.stem)
    rc, out = run(VERILATOR + ["--Mdir", str(mdir), str(probe)])
    if rc != 0:
        return classify(rc, out, False)
    rc, out = run([str(mdir / "Vtop")])
    return classify(rc, out, True)


def versions():
    v = run(["verilator", "--version"])[1].split()[1]
    i = run(["iverilog", "-V"])[1].splitlines()[0].split()[3]
    return v, i


def main():
    BUILD.mkdir(exist_ok=True)
    rows = []
    for line in (HERE / "probes.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        label, file = [x.strip() for x in line.split("|")]
        probe = HERE / "probes" / file
        iv, iv_why = icarus(probe)
        vl, vl_why = verilator(probe)
        rows.append((label, iv, iv_why, vl, vl_why))
        print(f"{label:46s} icarus: {iv:9s} verilator: {vl}")
    vver, iver = versions()
    both = sum(1 for r in rows if r[1] == "runs" and r[3] == "runs")
    vonly = sum(1 for r in rows if r[1] != "runs" and r[3] == "runs")
    ionly = sum(1 for r in rows if r[1] == "runs" and r[3] != "runs")
    neither = len(rows) - both - vonly - ionly
    print(f"{len(rows)} constructs: {both} run on both, {vonly} on "
          f"Verilator only, {ionly} on Icarus only, {neither} on neither")
    md = ["| Construct | Icarus " + iver + " | Verilator " + vver + " |",
          "|---|---|---|"]
    for label, iv, iw, vl, vw in rows:
        md.append(f"| {label} | {iv}{' — ' + iw if iw else ''} | "
                  f"{vl}{' — ' + vw if vw else ''} |")
    md.append("")
    md.append(": What each open simulator does with the testbench-language "
              "constructs of this Part, measured by running one probe per row with "
              "the flags the book's build uses and checking the printed "
              f"values. Of {len(rows)} constructs, {both} run on both, "
              f"{vonly} on Verilator only, {ionly} on Icarus only and "
              f"{neither} on neither. Regenerated from the probes on every "
              "run. {#tbl-ch05-support}")
    (HERE / "matrix.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
