"""fifolog.py -- read the RUN lines written by tb_fifo_log.sv."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = ["idle", "push", "pop", "both"]


def bin_name(i):
    return "occ%02d_%s" % (i // 4, OPS[i % 4])


def read(name):
    runs = []
    with open(os.path.join(HERE, "out", name)) as f:
        for line in f:
            if not line.startswith("RUN"):
                continue
            d = {}
            for tok in line.split()[1:]:
                k, v = tok.split("=", 1)
                d[k] = v
            d["grid"] = [int(x) for x in d["grid"].split(",")]
            for k in ("seed", "pw", "pr", "n", "exposed", "first"):
                d[k] = int(d[k])
            runs.append(d)
    return runs
