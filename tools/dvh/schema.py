"""schema.py -- the JSON Schema for every tool output, and a check against it.

The schemas are the contract. A caller that is not this book -- another
team's script, an editor plugin, a model given tool access -- needs to know
what a field means and what it may contain without reading the code that
produced it, and needs to be told when that changes.

They are versioned in their `$id` rather than by a field in the payload, so
a consumer pins a URL and a producer that changes a field's meaning must
publish a new one. `validate` is used by the tests, so a change to an output
that the schema does not describe fails in continuous integration rather
than in somebody else's parser.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).parent / "schema"

# Command name -> the schema its output must satisfy.
FOR_COMMAND = {
    "clock-tree": "clock-tree.schema.json",
    "reset-tree": "reset-tree.schema.json",
    "crossings": "crossings.schema.json",
    "connections": "connections.schema.json",
}


def load(command: str) -> dict:
    """The schema for one command's output."""
    return json.loads((HERE / FOR_COMMAND[command]).read_text())


def validate(command: str, payload: dict) -> list[str]:
    """Every way `payload` fails its schema, as messages a person can read.

    Returns an empty list when the payload conforms. Missing the validator
    is reported rather than passed over: a check that silently does nothing
    is worse than no check.
    """
    try:
        import jsonschema                              # noqa: PLC0415
    except ImportError:
        return ["jsonschema is not installed, so the output was not checked"]
    errors = jsonschema.Draft202012Validator(load(command)).iter_errors(payload)
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in sorted(errors, key=lambda e: list(e.path))]
