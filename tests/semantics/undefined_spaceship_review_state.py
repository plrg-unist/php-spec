#!/usr/bin/env python3
"""Run independent source-reached spaceship reference and value checks."""
import argparse
from pathlib import Path

from undefined_spaceship_review_cases import CASES
from undefined_spaceship_review_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-null-string-reference-rebind', 'peer-captured-right-expression')}
    run(selected, checks, PREFIX, args.output)
