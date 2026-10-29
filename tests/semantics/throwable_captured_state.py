#!/usr/bin/env python3
"""Check source-reached captured-Throwable slots, owners and real recurrence."""
import argparse
from pathlib import Path

from throwable_captured_cases import CASES as SOURCE_CASES
from throwable_captured_state_cases import CASES as STATE_CASES
from throwable_captured_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=tuple(EXPECTED), action='append')
    args = parser.parse_args()
    cases = dict(SOURCE_CASES, **STATE_CASES)
    run({name: cases[name] for name in (args.case or EXPECTED)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_captured_cases.py',
            ROOT / 'tests/semantics/throwable_captured_state_cases.py',
            ROOT / 'tests/semantics/throwable_captured_protocol.py',
            ROOT / 'tests/semantics/throwable_captured_state.py',
            ROOT / 'tests/semantics/throwable_trace_visited_protocol.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_recursion_protocol.py'], timeout=600)
