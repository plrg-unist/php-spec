#!/usr/bin/env python3
"""Strict-SL live-array references, COW copies and append history."""
import argparse
from pathlib import Path

from undefined_spaceship_array_resume_review_cases import CASES
from undefined_spaceship_array_resume_review_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-array-left-missing-fresh-reference-cow',
        'peer-array-right-missing-rebound-reference-default')}
    run(selected, checks, PREFIX, args.output)
