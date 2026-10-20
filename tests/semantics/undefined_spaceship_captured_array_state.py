#!/usr/bin/env python3
"""Two source-reached captured-array continuations through strict SL."""
import argparse
from pathlib import Path

from undefined_spaceship_captured_array_cases import CASES
from undefined_spaceship_captured_array_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'captured-left-assignment-empty', 'captured-right-runtime-array')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_spaceship_captured_array*.py')))
