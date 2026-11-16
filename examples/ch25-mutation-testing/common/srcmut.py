"""srcmut.py -- every source-level mutant of the repaired FIFO, made
when the example runs from examples/ch09-temporal-properties/rtl/
fifo_fixed.sv as it stands, under a fixed operator set: one change
for each mutant, at every site in the module body.

Operators (the software names in brackets):
  LCR  && <-> ||                     (logical connector replacement)
  LNR  remove a unary !              (negation removal)
  CNG  if (c) -> if (!(c))           (condition negation)
  ROR  == -> != < <= > >=            (relational operator replacement)
  AOR  + <-> -                       (arithmetic operator replacement)
  CRP  1'b1 -> 2'd2; '0 -> '1        (constant replacement)
  CSW  exchange the two case labels  (HDL: case item exchange)
  SDL  delete one assignment         (statement deletion)
  VSW  wr_ptr <-> rd_ptr in a use    (variable replacement)
  ARS  drop 'or negedge rst_n'       (HDL: asynchronous reset made
                                      synchronous)

mutants() lists them as Mutant records, m01 to m44 in the order of
the file. single(m) is the file with that one change; schema() is
one file holding every change behind a run-time select, read from
+mut=K (0, the default, is the design unchanged), so that each
testbench is built once and run once per mutant: the mutant schemata
of Untch, Offutt and Harrold, at the source level. How each kind of
line becomes a selection is written beside schema_line below.
"""
import collections
import re

from mutlib import FIXED, ROOT

Mutant = collections.namedtuple("Mutant", "id op line old new body")
ROR = ["!=", "<", "<=", ">", ">="]


def source():
    return (ROOT / FIXED).read_text().split("\n")


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
        yield "CNG", (line[:m.start(1)] + "!(" + m.group(1) + ")"
                      + line[m.end(1):])
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


def mutants():
    """Every mutant, in file order, the case-label exchange last."""
    src = source()
    first = next(i for i, x in enumerate(src)
                 if x.lstrip().startswith("wire"))
    rows = []
    for i in range(first, len(src)):
        for op, new in sites(src[i]):
            if new == src[i]:
                raise SystemExit(f"edit at line {i + 1} changed nothing")
            body = list(src)
            body[i] = new
            rows.append((op, i + 1, src[i].strip(), new.strip(), body))
    a = next(i for i, x in enumerate(src) if "2'b10:" in x)
    b = next(i for i, x in enumerate(src) if "2'b01:" in x)
    body = list(src)
    body[a] = src[a].replace("2'b10:", "2'b01:")
    body[b] = src[b].replace("2'b01:", "2'b10:")
    rows.append(("CSW", a + 1, "2'b10: / 2'b01:", "labels exchanged",
                 body))
    return [Mutant(f"m{n:02d}", *r) for n, r in enumerate(rows, 1)]


def single(m, module="fifo"):
    """The text of mutant M, module renamed MODULE, with a first line
    that names it."""
    text = "\n".join(m.body)
    if module != "fifo":
        text = re.sub(r"^module fifo ", f"module {module} ", text,
                      flags=re.M)
    return (f"// {m.id}: {m.op} at line {m.line} -- MUTANT of "
            f"fifo_fixed.sv, made when the example ran\n" + text)


def diff(m):
    """One line: the mutant as a change of one line of the file."""
    if m.op == "CSW":
        return f"{m.id} {m.op} line {m.line}: case labels 2'b10 and " \
               "2'b01 exchanged"
    return f"{m.id} {m.op} line {m.line}: {m.old}  ->  {m.new}"


def _rhs(line):
    """(left part up to and with ' = ', expression without ';')."""
    code = line.split("//")[0].rstrip()
    k = code.index(" = ")
    return code[:k + 3], code[k + 3:].rstrip(";").strip()


def _stmt(line):
    """(indentation and case label, statement) of a statement line; a
    deleted statement becomes the empty statement ';'."""
    s = line.strip()
    lab = re.match(r"(2'b\d\d:|default:)\s*", s)
    keep = lab.group(0) if lab else ""
    body = s[len(keep):].split("//")[0].strip()
    ind = line[:len(line) - len(line.lstrip())]
    return ind + keep, body


def schema_line(orig, alts):
    """The schema form of one line of the file, ORIG, that the
    mutants ALTS [(number, new line)] change.

    wire / assign   a chain of ?: on the select, the original last
    if (c) begin    if ((mut == k) ? c' : c) begin
    a statement     if (mut == k) s' else ... else s, where s' may be
                    the empty statement of a deletion
    always_ff       the sensitivity list keeps its edge, on rst_a:
                    rst_n, except that it is held at 1 when mut == 5
                    (ARS) selects the synchronous form; the body still
                    tests rst_n, so a reset is then seen at the clock
                    edge only, as in the mutant
    if (!rst_n)     the condition chosen by the select, as for any if
    """
    code = orig.split("//")[0]
    if re.match(r"\s*(wire|assign) ", code):
        lhs, e = _rhs(orig)
        expr = e
        for k, new in reversed(alts):
            expr = f"(mut == {k}) ? {_rhs(new)[1]} : {expr}"
        return [f"{lhs}{expr};"]
    if code.lstrip().startswith("always_ff"):
        (k, new), = alts
        assert "or negedge rst_n" in code and "negedge" not in new
        ind = orig[:len(orig) - len(orig.lstrip())]
        return [f"{ind}wire rst_a = (mut == {k}) ? 1'b1 : rst_n;",
                orig.replace("negedge rst_n", "negedge rst_a")]
    m = re.search(r"if \((.*)\) begin", code)
    if m:
        cond = m.group(1)
        for k, new in reversed(alts):
            c2 = re.search(r"if \((.*)\) begin", new).group(1)
            cond = f"(mut == {k}) ? ({c2}) : ({cond})"
        return [orig[:m.start(1)] + cond + orig[m.end(1):]]
    ind, s = _stmt(orig)
    out = ind
    for k, new in alts:
        out += f"if (mut == {k}) {_stmt(new)[1]} else "
    return [out + s]


def schema():
    """The schema: module fifo with every mutant behind +mut=K."""
    src = source()
    ms = mutants()
    by_line = collections.defaultdict(list)
    csw = None
    for n, m in enumerate(ms, 1):
        if m.op == "CSW":
            csw = n
            continue
        i = m.line - 1
        by_line[i].append((n, m.body[i]))
    out = ["// fifo schema -- fifo_fixed.sv with every source mutant of",
           "// srcmut.py behind a select read from +mut=K (0: unchanged),",
           "// made when the example ran. Not a design: a test harness."]
    for i, line in enumerate(src):
        if line.startswith("  localparam int PTR_W"):
            out += [line,
                    "  int unsigned mut;",
                    "  initial if (!$value$plusargs(\"mut=%d\", mut))"
                    " mut = 0;"]
            continue
        if "case ({do_write, do_read})" in line:
            # CSW: exchanging the labels 2'b10 and 2'b01 is the same
            # as exchanging the two bits the case selects on.
            out.append(line.replace(
                "case ({do_write, do_read})",
                f"case ((mut == {csw}) ? {{do_read, do_write}}"
                " : {do_write, do_read})"))
            continue
        out += schema_line(line, by_line[i]) if i in by_line else [line]
    return "\n".join(out) + "\n"


def build_schema(bdir, names, extra=(), tbs=None, workers=4):
    """Write the schema to BDIR/fifo_schema.sv and build each
    testbench of NAMES against it, in parallel. -Wno-fatal: the schema
    holds every mutant's line, and seven of them draw warnings the
    book's -Wall makes fatal; source-mutants/ reports those as lint
    kills, mutant by mutant. Returns {name: build directory} and the
    sorted warning names the builds printed."""
    import mutlib
    import os
    import pathlib
    bdir = pathlib.Path(bdir)
    os.makedirs(bdir, exist_ok=True)
    sv = bdir / "fifo_schema.sv"
    sv.write_text(schema())
    res = mutlib.pmap(
        lambda tb: (tb,) + mutlib.build(tb, [sv], bdir / tb,
                                        ["-Wno-fatal"] + list(extra),
                                        tbs=tbs),
        names, workers)
    warn = set()
    for tb, ok, _, log in res:
        if not ok:
            raise SystemExit(f"schema build of {tb} failed:\n{log}")
        warn |= set(re.findall(r"%Warning-([A-Z]+):", log))
    return {tb: bdir / tb for tb in names}, sorted(warn)


def run_schema(dirs, ids, plus=(), tbs=None, workers=4):
    """Run every testbench of DIRS once for each mutant number in IDS
    (0: the design unchanged). Returns {(id, tb): verdict}."""
    import mutlib
    jobs = [(k, tb) for k in ids for tb in dirs]
    out = mutlib.pmap(
        lambda j: mutlib.run(j[1], dirs[j[1]],
                             [f"+mut={j[0]}"] + list(plus), tbs=tbs)[0],
        jobs, workers)
    return dict(zip(jobs, out))


def describe(m):
    """One short line: the mutant, its operator and the line it
    leaves (spaces collapsed), or what it deleted or exchanged."""
    if m.op == "CSW":
        new = "case labels 2'b10 and 2'b01 exchanged"
    elif m.op == "SDL":
        new = "deleted: " + re.sub(r"\s+", " ", m.old)
    else:
        new = re.sub(r"\s+", " ", m.new)
    return f"{m.id} {m.op} {m.line:3d}  {new}"
