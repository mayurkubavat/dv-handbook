#!/usr/bin/env python3
"""Run every tests/sv design of the InFormal repository through the installed
binary and compare with the answers in its comments (//% command, //= prop
status, //! expected error text)."""
import pathlib, re, subprocess, sys
src = pathlib.Path(sys.argv[1]); here = pathlib.Path(__file__).resolve().parent.parent
ok = bad = 0
for sv in sorted(src.glob("*.sv")):
    cmds, exp, err = [], {}, []
    for l in sv.read_text().splitlines():
        if l.startswith("//% "): cmds.append(l[4:])
        elif l.startswith("//= "): n, s = l[4:].split()[:2]; exp[n] = s
        elif l.startswith("//! "): err.append(l[4:].strip())
    own_elab = any(c.startswith("elaborate") for c in cmds)
    tcl = ["clear -all", f"analyze -sv12 {sv}"] + ([] if own_elab else [f"elaborate -top {sv.stem}"])
    tcl += ["set_prove_time_limit 30s"] + cmds
    if not err:
        tcl += ["prove -all", "foreach p [get_property_list] {puts \"STATUS $p [get_status $p]\"}"]
    t = here / "build" / "known.tcl"; t.write_text("\n".join(tcl) + "\n")
    r = subprocess.run(["informal", "shell", "--flavor", "jg", "--engines", str(here / "config/engines.toml"),
                        "--workdir", str(here / "build/known"), str(t)], capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    got = dict(m.groups() for m in re.finditer(r"^STATUS (\S+) (\S+)$", out, re.M))
    if err:
        good = all(e in out for e in err); detail = "" if good else out.strip().splitlines()[0][:150]
    else:
        diff = {n: (s, got.get(n)) for n, s in exp.items() if got.get(n) != s}
        good = not diff; detail = str(diff) if diff else ""
        if not good and not got: detail += " | " + out.strip()[:200].replace("\n", " / ")
    ok += good; bad += not good
    print(("ok   " if good else "DIFF ") + sv.name, detail)
print(f"{ok} agree, {bad} differ")
