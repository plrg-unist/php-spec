#!/usr/bin/env python3
"""Check source-reached NULL-previous builtin Throwable trace comparisons."""
import argparse
from pathlib import Path

from throwable_null_trace_cases import CASES
from throwable_null_trace_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=tuple(EXPECTED), action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or EXPECTED)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_null_trace_cases.py',
            ROOT / 'tests/semantics/throwable_null_trace_protocol.py',
            ROOT / 'tests/semantics/throwable_null_trace_state.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_recursion_protocol.py'], timeout=360)
