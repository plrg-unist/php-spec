#!/usr/bin/env python3
"""Strict-SL missing-right scalar comparison continuations."""
import argparse
from pathlib import Path

from undefined_spaceship_state import ROOT, run
from undefined_scalar_compare_right_cases import CASES
from undefined_scalar_compare_right_protocol import PREFIX, checks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('right-equal-live-plain', 'right-less-false-default')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare*.py')))
