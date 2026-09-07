#!/usr/bin/env python3
"""plan_report.py -- read a verification plan and report what has evidence.

Usage:  python3 plan_report.py [--plan fifo_plan.yaml]
                               [--status ../../status.json] [--verbose]

For every plan item the report says whether a test exists for it, whether
that test passed in the most recent check, and, if not, that the item has
no evidence. It deliberately reports *evidence*, not opinion: an item with
no test is "no evidence" no matter how confident anyone feels about it.
"""
import argparse
import json
import pathlib
import sys

try:
    import yaml
except ImportError:                          # keep the tool runnable anywhere
    sys.exit("plan_report.py needs PyYAML:  pip install pyyaml")

HERE = pathlib.Path(__file__).parent


def load_status(path):
    """Map example directory -> True (design passed), False (design failed).

    The status file records whether each *example* behaved as expected. An
    example marked ``expect: fail`` exists to expose a bug, so when it fails
    as expected the *design* has failed that item. The plan cares about the
    design, so the two views are inverted here.
    """
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    result = {}
    for entry in data.get("examples", []):
        name = entry["dir"].removeprefix("examples/")
        example_ok = entry["lint"] != "fail" and entry["run"].startswith("pass")
        expects_failure = entry.get("expect") == "fail"
        result[name] = example_ok != expects_failure
    return result


def item_status(item, status):
    """Classify one plan item from the evidence available."""
    tests = item.get("tests") or []
    if not tests:
        return "no evidence", []
    known = [(t, status.get(t)) for t in tests]
    if any(p is None for _, p in known):
        return "test missing", known
    if all(p for _, p in known):
        return "passing", known
    return "failing", known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=HERE / "fifo_plan.yaml", type=pathlib.Path)
    ap.add_argument("--status", default=HERE / "../../status.json", type=pathlib.Path)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    plan = yaml.safe_load(args.plan.read_text())
    status = load_status(args.status)

    print(f"Verification plan report: {plan['block']} (revision {plan['revision']})")
    print(f"{'item':<9} {'priority':<8} {'status':<12} feature")
    print("-" * 60)
    counts = {}
    for item in plan["items"]:
        state, known = item_status(item, status)
        counts[state] = counts.get(state, 0) + 1
        print(f"{item['id']:<9} {item['priority']:<8} {state:<12} {item['feature']}")
        if args.verbose:
            for name, passed in known:
                mark = {True: "pass", False: "FAIL", None: "not in status"}[passed]
                print(f"{'':<9} {'':<8} {'':<12}   {name}: {mark}")
            if not known:
                print(f"{'':<9} {'':<8} {'':<12}   closure: {item['closure']}")

    total = len(plan["items"])
    print("-" * 60)
    for state in ("passing", "failing", "test missing", "no evidence"):
        if counts.get(state):
            print(f"{state:<13} {counts[state]:>3} of {total}")
    must_open = [i["id"] for i in plan["items"]
                 if i["priority"] == "must" and item_status(i, status)[0] != "passing"]
    if must_open:
        print(f"must-have items without passing evidence: {', '.join(must_open)}")
        return 1
    print("every must-have item has passing evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
