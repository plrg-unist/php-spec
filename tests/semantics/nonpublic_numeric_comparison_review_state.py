#!/usr/bin/env python3
"""Check reached non-public physical keys and normal numeric continuations."""
from pathlib import Path
import argparse

from nonpublic_numeric_comparison_review_cases import CASES
from nonpublic_numeric_comparison_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in
        ('private-shadow-physical-key','protected-reversed-live-slots')}
    assert not args.output.exists(), args.output
    run(selected,checks,PREFIX,args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('nonpublic_numeric_comparison_review_*.py')))
