#!/usr/bin/env python3
"""Run source-reached forward quiet folds and surviving reference aliases."""
import argparse
from pathlib import Path

from undefined_scalar_compare_checked_unset_cases import CASES
from undefined_scalar_compare_checked_unset_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('checked-equal-left-unset', 'checked-lessequal-reference-unset')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
