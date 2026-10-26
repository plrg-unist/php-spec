#!/usr/bin/env python3
"""Check the actual protected pre-unwrapped cell and normal comparison result."""
from pathlib import Path
import argparse

from nonpublic_numeric_comparison_cases import CASES
from nonpublic_numeric_comparison_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), args.output
    run({'protected-table-retained-cell': CASES['protected-table-retained-cell']},
        checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('nonpublic_numeric_comparison*.py')))
