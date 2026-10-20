#!/usr/bin/env python3
"""Run both source-reached array spaceship continuation shapes through strict SL."""
import argparse
from pathlib import Path

from undefined_spaceship_array_resume_cases import CASES
from undefined_spaceship_array_resume_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('array-resume-missing-left-empty', 'array-resume-missing-right-empty')}
    run(selected, checks, PREFIX, args.output)
