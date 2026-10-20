#!/usr/bin/env python3
"""Run checked-left removal and surviving-alias spaceship states."""
import argparse
from pathlib import Path

from undefined_spaceship_checked_unset_cases import CASES
from undefined_spaceship_checked_unset_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('checked-left-unset-plain', 'checked-left-unset-reference')}
    run(selected, checks, PREFIX, args.output)
