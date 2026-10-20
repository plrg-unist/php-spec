#!/usr/bin/env python3
"""Strict-SL initial array roots, current scalar references and quiet removal."""
import argparse
from pathlib import Path

from undefined_comparison_initial_array_review_cases import CASES
from undefined_comparison_initial_array_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-initial-array-spaceship-rebound-reference',
        'peer-initial-array-checked-left-unset-default')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_comparison_initial_array*.py')))
