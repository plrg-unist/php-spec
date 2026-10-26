#!/usr/bin/env python3
"""Check reached warmed Throwable slot comparisons under strict SL."""
import argparse
from pathlib import Path

from throwable_warm_comparison_cases import CASES
from throwable_warm_comparison_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=('cache-before-line', 'error-warm-tail'), action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or ('cache-before-line', 'error-warm-tail'))}, checks, PREFIX,
        args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_warm_comparison_cases.py',
                      ROOT / 'tests/semantics/throwable_warm_comparison_protocol.py',
                      ROOT / 'tests/semantics/throwable_warm_comparison_state.py'])
