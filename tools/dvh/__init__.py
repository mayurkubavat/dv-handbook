"""dvh -- the book's tool layer over elaborated designs, testbenches and logs.

Chapter 3 adds design.py, clocks.py and graph.py: clock tree, reset tree,
crossing report and the instance connection graph. Later chapters add the
testbench and evidence models. Everything is deterministic and runs in CI.
"""
__all__ = ["design", "clocks", "graph"]
