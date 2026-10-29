#!/usr/bin/env python3
"""Check reached early graph decisions and visited-cycle refusal in strict SL."""
import argparse
from pathlib import Path

from throwable_trace_visited_cases import CASES as SOURCE_CASES
from throwable_trace_visited_state_cases import CASES as STATE_CASES
from throwable_trace_visited_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

SELECTED = ('array-count-skips-cycle', 'object-identity-skips-cycle',
            'same-nan-cell-before-cycle', 'plain-inline-leaf-skips-cycle',
            'visited-cell-cycle-control', 'active-cycle-before-count-control')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=SELECTED, action='append')
    args = parser.parse_args()
    cases = dict(SOURCE_CASES, **STATE_CASES)
    run({name: cases[name] for name in (args.case or SELECTED)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_trace_visited_cases.py',
            ROOT / 'tests/semantics/throwable_trace_visited_state_cases.py',
            ROOT / 'tests/semantics/throwable_trace_visited_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_recursion_protocol.py',
            ROOT / 'tests/semantics/throwable_trace_visited_state.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_cases.py'])
