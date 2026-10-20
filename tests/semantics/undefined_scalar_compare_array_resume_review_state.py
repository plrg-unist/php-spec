#!/usr/bin/env python3
"""Strict-SL forward/reversed array predicates with references and COW."""
import argparse
from pathlib import Path

from undefined_scalar_compare_array_resume_review_cases import CASES
from undefined_scalar_compare_array_resume_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-boolean-array-equal-fresh-reference-cow',
        'peer-boolean-array-greater-rebound-reference-default')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_array_resume*.py')))
