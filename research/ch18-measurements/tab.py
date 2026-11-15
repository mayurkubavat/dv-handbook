"""tab.py -- turn one measurement output into a property-by-engine
table of verdict and seconds.

    python3 tab.py out/engines_book.out
"""
import re
import sys

sec, eng, rows, engines = "", "", {}, []
for line in open(sys.argv[1]):
    if line.startswith("==="):
        sec = line.strip("= \n")
    m = re.match(r"--- engine (\S+),", line)
    if m:
        eng = m.group(1)
        if eng not in engines:
            engines.append(eng)
    m = re.match(r"(\S+)\s+(assert|cover)\s+(\w+)\s*(.*)", line)
    if m and m.group(3) not in ("disabled", "unprocessed"):
        t = re.search(r"([0-9.]+) s$", line.strip())
        d = re.search(r"depth (\d+)", line)
        word = {"proven": "P", "cex": "C", "covered": "V",
                "unreachable": "U", "undetermined": "-",
                "error": "E"}[m.group(3)]
        cell = word + (d.group(1) if d else "") + \
            (" " + t.group(1) if t else "")
        rows.setdefault((sec, m.group(1).split(".")[-1]), {})[eng] = cell
print("| design | property | " + " | ".join(engines) + " |")
print("|" + " --- |" * (len(engines) + 2))
for (sec, name), cells in rows.items():
    print(f"| {sec} | {name} | " +
          " | ".join(cells.get(e, "") for e in engines) + " |")
