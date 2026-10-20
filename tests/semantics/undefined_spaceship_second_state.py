#!/usr/bin/env python3
"""Run source-reached two-Warning spaceship continuations through strict SL."""
import argparse
from pathlib import Path

from undefined_spaceship_second_cases import CASES
from undefined_spaceship_second_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({name: CASES[name] for name in ('second-spaceship-string', 'second-spaceship-same-false')},
        checks, PREFIX, args.output)
