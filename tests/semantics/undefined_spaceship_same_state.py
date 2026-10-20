#!/usr/bin/env python3
"""Strict-SL same missing CV spaceship warning continuations."""
import argparse
from pathlib import Path

from undefined_spaceship_same_cases import CASES
from undefined_spaceship_same_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('same-spaceship-string', 'same-spaceship-false')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare*.py')))
