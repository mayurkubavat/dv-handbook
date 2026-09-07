#!/usr/bin/env python3
"""Run the tool layer's pytest suite (tools/dvh/tests) as an example."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).parent
TESTS = HERE.parents[2] / "tools" / "dvh" / "tests"
sys.exit(pytest.main(["-q", str(TESTS)]))
