#!/usr/bin/env python3
"""Run authentic forward/reversed Boolean array continuations through strict SL."""
import argparse
from pathlib import Path

from undefined_scalar_compare_array_resume_cases import CASES
from undefined_scalar_compare_array_resume_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'boolean-array-equal-empty', 'boolean-array-greater-nonempty')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_array_resume*.py')))
