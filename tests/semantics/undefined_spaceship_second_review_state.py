#!/usr/bin/env python3
"""Strict-SL independent two-Warning spaceship references and raw restores."""
import argparse
from pathlib import Path

from undefined_spaceship_second_review_cases import CASES
from undefined_spaceship_second_review_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-second-warning-spaceship-fresh-reference',
        'peer-second-warning-spaceship-unset-right-target-reference')}
    run(selected, checks, PREFIX, args.output)
