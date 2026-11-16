"""mutate_src.py -- every source-level mutant of the repaired FIFO
(examples/ch09-temporal-properties/rtl/fifo_fixed.sv) under a fixed
operator set, one change per mutant, enumerated at every site.

Operators (the software names in brackets; the selective set of
Offutt et al. plus statement deletion and three HDL operators):
  LCR  && <-> ||                     (logical connector replacement)
  LNR  remove a unary !              (negation removal)
  CNG  if (c) -> if (!(c))           (condition negation)
  ROR  == -> != < <= > >=            (relational operator replacement)
  AOR  + <-> -                       (arithmetic operator replacement)
  CRP  1'b1 -> 2'd2; '0 -> '1        (constant replacement)
  CSW  swap the two case labels      (HDL: case item exchange)
  SDL  delete one assignment         (statement deletion)
  VSW  wr_ptr <-> rd_ptr in a use    (variable replacement)
  ARS  drop 'or negedge rst_n'       (HDL: async reset made sync)

Writes build/src/m<NN>.sv, one per mutant, and mutants.tsv: id,
operator, line, original text, mutated text. The first line of each
mutant file is a comment naming it.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import mutlib  # noqa: E402

os.chdir(mutlib.ROOT)
SRC = open(mutlib.FIXED).read().split("\n")
# Mutate the module body only: from the first 'wire' to 'endmodule'.
FIRST = next(i for i, l in enumerate(SRC) if l.lstrip().startswith("wire"))
OUT = sys.argv[1] if len(sys.argv) > 1 else "build/src"

ROR = ["!=", "<", "<=", ">", ">="]


def sites(line):
    """Yield (operator, new line) for every mutation of LINE."""
    code = line.split("//")[0]
    stmt = code.strip()
    for m in re.finditer(r"&&|\|\|", code):
        rep = "||" if m.group() == "&&" else "&&"
        yield "LCR", line[:m.start()] + rep + line[m.end():]
    for m in re.finditer(r"!(?!=)", code):
        yield "LNR", line[:m.start()] + line[m.end():]
    m = re.search(r"if \((.*)\) begin", code)
    if m:
        yield "CNG", line[:m.start(1)] + "!(" + m.group(1) + ")" + \
            line[m.end(1):]
    for m in re.finditer(r"==", code):
        for r in ROR:
            yield "ROR", line[:m.start()] + r + line[m.end():]
    for m in re.finditer(r"(?<=\S )([+-])(?= )", code):
        rep = "-" if m.group(1) == "+" else "+"
        yield "AOR", line[:m.start(1)] + rep + line[m.end(1):]
    for m in re.finditer(r"1'b1", code):
        yield "CRP", line[:m.start()] + "2'd2" + line[m.end():]
    for m in re.finditer(r"<= '0;", code):
        yield "CRP", line[:m.start()] + "<= '1;" + line[m.end():]
    if re.match(r"(default:\s*)?\w+(\[\w+\])?\s*<=.*;$", stmt) or \
            re.match(r"2'b\d\d:\s+\w+ <=", stmt):
        lab = re.match(r"(2'b\d\d:|default:)\s*", stmt)
        keep = lab.group(0) if lab else ""
        ind = line[:len(line) - len(line.lstrip())]
        yield "SDL", ind + keep + ";  // deleted: " + stmt[len(keep):]
    for m in re.finditer(r"\b(wr_ptr|rd_ptr)\b", code):
        if re.match(r"\s*(<=)", code[m.end():]):
            continue                      # the target, not a use
        rep = "rd_ptr" if m.group(1) == "wr_ptr" else "wr_ptr"
        yield "VSW", line[:m.start()] + rep + line[m.end():]
    if "or negedge rst_n" in code:
        yield "ARS", line.replace(" or negedge rst_n", "")


def case_swap(src):
    """The one CSW mutant: exchange the labels 2'b10 and 2'b01."""
    a = next(i for i, l in enumerate(src) if "2'b10:" in l)
    b = next(i for i, l in enumerate(src) if "2'b01:" in l)
    out = list(src)
    out[a] = src[a].replace("2'b10:", "2'b01:")
    out[b] = src[b].replace("2'b01:", "2'b10:")
    return a, out


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for i in range(FIRST, len(SRC)):
        for op, new in sites(SRC[i]):
            if new == SRC[i]:
                continue
            body = list(SRC)
            body[i] = new
            rows.append((op, i + 1, SRC[i].strip(), new.strip(), body))
    a, body = case_swap(SRC)
    rows.append(("CSW", a + 1, "2'b10: / 2'b01:", "labels exchanged",
                 body))
    with open(os.path.join(os.path.dirname(__file__), "mutants.tsv"),
              "w") as tsv:
        tsv.write("id\top\tline\toriginal\tmutated\n")
        for n, (op, ln, old, new, body) in enumerate(rows, 1):
            mid = f"m{n:02d}"
            with open(os.path.join(OUT, mid + ".sv"), "w") as f:
                f.write(f"// {mid}: {op} at line {ln} -- MUTANT of "
                        "fifo_fixed.sv\n")
                f.write("\n".join(body))
            tsv.write(f"{mid}\t{op}\t{ln}\t{old}\t{new}\n")
    print(f"{len(rows)} mutants written to {OUT}")


if __name__ == "__main__":
    main()
