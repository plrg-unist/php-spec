#!/usr/bin/env python3
"""Check reached builtin previous-chain comparisons through strict SL."""
import argparse
from pathlib import Path

from throwable_builtin_previous_cases import CASES
from throwable_builtin_previous_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

SELECTED = ('previous-before-severity', 'severity-after-equal-previous',
            'previous-trace-array', 'mixed-previous-skips-cyclic-trace',
            'shared-previous-all-root-kinds', 'previous-object-trace-control')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=SELECTED, action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or SELECTED)}, checks, PREFIX,
        args.output, extra_inputs=[
            ROOT / 'tests/semantics/throwable_builtin_previous_cases.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_protocol.py',
            ROOT / 'tests/semantics/throwable_builtin_previous_state.py'])
