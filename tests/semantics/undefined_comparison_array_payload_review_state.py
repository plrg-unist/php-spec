#!/usr/bin/env python3
"""Check shared child COW and supplied-Exception transitive cleanup through SL."""
import argparse
from pathlib import Path

from undefined_comparison_array_payload_review_cases import CASES
from undefined_comparison_array_payload_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'child-alias-shared-inner-cow', 'child-alias-supplied-throw')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_array_payload*.py')),
                      ROOT / 'tests/semantics/undefined_comparison_object_reference_array_review_protocol.py'])
