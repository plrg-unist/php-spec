#!/usr/bin/env python3
"""Check reached same-kind severity and nested trace orders in strict SL."""
import argparse
from pathlib import Path

from throwable_builtin_same_cases import CASES as SOURCE_CASES
from throwable_builtin_same_state_cases import CASES as STATE_CASES
from throwable_builtin_same_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'state-severity': STATE_CASES['state-severity'],
         'type-trace-arrays': SOURCE_CASES['type-trace-arrays']},
        checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_builtin_same_cases.py',
                      ROOT / 'tests/semantics/throwable_builtin_same_state_cases.py',
                      ROOT / 'tests/semantics/throwable_builtin_same_protocol.py',
                      ROOT / 'tests/semantics/throwable_builtin_same_state.py'])
