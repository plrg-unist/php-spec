#!/usr/bin/env python3
"""Check reached builtin previous-node graph effects through strict SL."""
import argparse
from pathlib import Path

from throwable_previous_graph_cases import CASES
from throwable_previous_graph_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

SELECTED = ('std-live-cow-warm-tail', 'array-cell-retarget',
            'trace-before-link-and-severity')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=SELECTED, action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or SELECTED)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_previous_graph_cases.py',
            ROOT / 'tests/semantics/throwable_previous_graph_protocol.py',
            ROOT / 'tests/semantics/throwable_previous_graph_state.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py'])
