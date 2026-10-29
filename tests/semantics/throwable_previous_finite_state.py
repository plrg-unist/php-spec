#!/usr/bin/env python3
"""Check source-reached canonical paths and deep root-context guards."""
import argparse
from pathlib import Path

from throwable_previous_finite_cases import CASES
from throwable_previous_finite_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=tuple(CASES), action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or CASES)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_previous_finite_cases.py',
            ROOT / 'tests/semantics/throwable_previous_finite_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_finite_state.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_recursion_protocol.py'], timeout=900)
