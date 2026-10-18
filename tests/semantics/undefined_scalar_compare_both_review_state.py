#!/usr/bin/env python3
"""Strict-SL both-missing comparisons with fresh reference-cell ownership."""
import argparse
from pathlib import Path

from undefined_scalar_compare_both_review_cases import CASES
from undefined_scalar_compare_both_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-both-missing-equal-right-reference-created',
        'peer-both-missing-less-right-bound-to-target-reference')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare*.py')))
