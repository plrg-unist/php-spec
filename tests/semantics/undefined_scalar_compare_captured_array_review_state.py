#!/usr/bin/env python3
"""Strict-SL captured Boolean snapshots and abrupt owner release."""
import argparse
from pathlib import Path

from undefined_scalar_compare_captured_array_review_cases import CASES
from undefined_scalar_compare_captured_array_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-captured-equal-returned-empty',
        'peer-captured-greater-equal-right-default',
        'peer-captured-less-supplied-throw')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_captured_array*.py')))
