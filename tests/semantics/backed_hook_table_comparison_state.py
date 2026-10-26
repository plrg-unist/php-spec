#!/usr/bin/env python3
"""Check real setters alongside raw backing-slot numeric comparisons."""
from pathlib import Path
import argparse
from backed_hook_table_comparison_cases import CASES
from backed_hook_table_comparison_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), args.output
    run(CASES, checks, PREFIX, args.output, extra_inputs=[
        *sorted((ROOT/'tests/semantics').glob('backed_hook_table_comparison*.py')),
        ROOT/'tests/semantics/nonpublic_numeric_comparison_review_protocol.py'])
