#!/usr/bin/env python3
"""Run shared-CV forward Boolean warning fronts through strict SL."""
import argparse
from pathlib import Path

from undefined_scalar_compare_same_cases import CASES
from undefined_scalar_compare_same_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({name: CASES[name] for name in ('same-forward-equal-string', 'same-forward-less-equal-false')},
        checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
