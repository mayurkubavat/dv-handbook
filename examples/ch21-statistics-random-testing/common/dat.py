"""dat.py -- covergroup bins from Verilator coverage databases, as a
seed-by-bin table.

A coverage record in a .dat file reads C '<key>' <count>, where the key
is a sequence of \\001<tag>\\002<value> fields. Covergroup records carry
the tag t with value "covergroup", and the tag h with the bin's path
<group>.<point>.<bin>. This is the record format the coverage chapter's
runner reads with awk, read here in Python. Group names lose the prefix
Verilator gives an anonymous covergroup's class.
"""
import re

_KEY = re.compile(r"^C '(.*)' (\d+)$")


def read(path):
    """{"<group>.<point>.<bin>": count} for one .dat, in file order."""
    out = {}
    with open(path, encoding="latin-1") as f:
        for line in f:
            if "\x01t\x02covergroup" not in line:
                continue
            m = _KEY.match(line.rstrip("\n"))
            if not m:
                continue
            fields = dict(x.split("\x02", 1) for x in
                          m.group(1).split("\x01") if "\x02" in x)
            name = fields["h"].replace("__vlAnonCG_", "")
            out[name] = out.get(name, 0) + int(m.group(2))
    return out


def table(paths):
    """(bin names, rows): one row of counts per .dat, in the order of
    paths; the bin order is the first file's."""
    rows, names = [], None
    for p in paths:
        d = read(p)
        if names is None:
            names = list(d)
        assert list(d) == names, "%s has a different bin list" % p
        rows.append([d[n] for n in names])
    return names, rows


def write_tsv(path, names, rows, seeds, comment):
    """A seed-by-bin count table another example can read by path."""
    with open(path, "w") as f:
        f.write("# %s\n" % comment)
        f.write("seed\t" + "\t".join(names) + "\n")
        for s, r in zip(seeds, rows):
            f.write("%d\t" % s + "\t".join(map(str, r)) + "\n")


def read_tsv(path):
    """(bin names, rows) from write_tsv's format."""
    with open(path) as f:
        lines = [x.rstrip("\n") for x in f if not x.startswith("#")]
    names = lines[0].split("\t")[1:]
    rows = [[int(v) for v in x.split("\t")[1:]] for x in lines[1:]]
    return names, rows
