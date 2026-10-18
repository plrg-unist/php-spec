#!/usr/bin/env python3
"""Run source-reached live-left spaceship warning states."""
import argparse
from pathlib import Path

from undefined_spaceship_right_cases import CASES
from undefined_spaceship_right_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('right-live-plain', 'right-false-default')}
    run(selected, checks, PREFIX, args.output)
