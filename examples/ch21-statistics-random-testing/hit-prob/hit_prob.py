"""hit_prob.py -- one bin, one probability. The seeds needed to hit a
bin of per-seed probability p with confidence 1 - delta, exact and by
the ln(1/delta)/p rule; the FIFO's bug-trigger probability from the
exact chain, against run length and push mix; and the chance that the
constrained-random chapter's 64-packet run never draws its rarest
kind. Python only; deterministic (no random draws); under a second."""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "common"))
import statlib as S  # noqa: E402
import fifo_chain as F  # noqa: E402

C = S.Checks()
print("== 1. seeds to hit one bin: n >= ln(delta) / ln(1 - p) ==")
print("%7s %8s | %8s %8s %8s | %s" % ("p", "mean 1/p", "90%", "95%",
                                      "99%", "99% by ln(100)/p"))
for p in (0.5, 0.25, 0.1, 0.01, 0.001):
    ns = [S.seeds_to_hit(p, d) for d in (0.1, 0.05, 0.01)]
    print("%7g %8.0f | %8d %8d %8d | %.1f" % (p, 1 / p, *ns,
                                              math.log(100) / p))
C.pin("seeds for a 1% bin at 95%", S.seeds_to_hit(0.01, 0.05), 299)
C.pin("seeds for a 0.27 bin at 99%", S.seeds_to_hit(0.27, 0.01), 15)
C.near("ln rule against exact at p = 0.001, 99%",
       math.log(100) / 0.001, S.seeds_to_hit(0.001, 0.01), 3)

print("\n== 2. the FIFO's bug trigger, exact chain (full shown at 15) ==")
print("push and pop each requested with probability 1/2 per cycle:")
po = {30: 8.45e-5, 40: 9.0e-4, 60: 8.9e-3, 200: 0.2421}
for n in (30, 35, 40, 45, 50, 60, 100, 200, 400):
    p = F.p_trigger(0.5, 0.5, n)
    print("  %3d cycles: P(push while full) = %.3g;"
          " seeds for 95%%: %d" % (n, p, S.seeds_to_hit(p, 0.05)))
    if n in po:
        C.rel("chain at %d cycles" % n, p, po[n], 0.01)
pp = F.p_trigger(0.9, 0.25, 200)
print("push-biased (+bias=push: push 0.90, pop 0.25), 200 cycles: %.6f"
      % pp)
C.holds("push-biased generator triggers almost surely", pp > 0.9999)
fixed = F.p_trigger(0.5, 0.5, 200, full_at=16)
print("repaired FIFO (full at 16), even mix, 200 cycles: %.4f" % fixed)

print("\n== 3. the packet stream's rarest kind ==")
p2 = 0.9 ** 64
print("kind 2 drawn with probability 0.1 per packet: P(none in 64) = "
      "0.9^64 = %.5f" % p2)
print("packets for a 99%% chance of at least one kind 2: %d"
      % S.seeds_to_hit(0.1, 0.01))
C.near("0.9^64", p2, 0.00118, 0.000005)

print("\n== 4. a per-cycle rate is not a per-seed rate ==")
pc = 0.0113
iid = 1 - (1 - pc) ** 200
print("a bin hit in %.2f%% of cycles: independent 200-cycle seeds would"
      % (100 * pc))
print("hit it with probability 1 - (1 - %.4f)^200 = %.3f" % (pc, iid))
C.near("iid prediction for 1.13% per cycle", iid, 0.897, 0.0005)
C.report()
print("verdict: chain gives %.4f for 200 even cycles, %.3g for 30"
      % (F.p_trigger(0.5, 0.5, 200), F.p_trigger(0.5, 0.5, 30)))
