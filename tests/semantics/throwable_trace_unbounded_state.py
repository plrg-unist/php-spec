#!/usr/bin/env python3
"""Check source-reached finite captured paths with no fixed depth gate."""
import argparse
from pathlib import Path

from throwable_trace_unbounded_cases import CASES
from throwable_trace_unbounded_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=tuple(CASES), action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or CASES)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_trace_unbounded_cases.py',
            ROOT / 'tests/semantics/throwable_trace_unbounded_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_unbounded_state.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_recursion_protocol.py'], timeout=360)
