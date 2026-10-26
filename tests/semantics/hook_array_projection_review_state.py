#!/usr/bin/env python3
"""Check raw singleton projections and snapshot-only final object release."""
from pathlib import Path
import argparse
from hook_array_projection_review_cases import CASES
from hook_array_projection_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), args.output
    selected = {name: CASES[name] for name in (
        'singleton-scalar-snapshot', 'singleton-object-snapshot-release')}
    run(selected, checks, PREFIX, args.output, extra_inputs=[
        *sorted((ROOT / 'tests/semantics').glob('hook_array_projection*.py')),
        ROOT / 'tests/semantics/nonpublic_numeric_comparison_review_protocol.py'])
