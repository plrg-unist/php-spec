#!/usr/bin/env python3
"""Two source-reached captured primitive snapshots through strict SL."""
import argparse
from pathlib import Path

from undefined_scalar_compare_captured_primitive_cases import CASES
from undefined_scalar_compare_captured_primitive_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'captured-equal-right-zero', 'captured-greater-left-string')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_captured_primitive*.py')))
