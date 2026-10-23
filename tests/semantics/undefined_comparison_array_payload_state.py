#!/usr/bin/env python3
"""Check singleton child snapshots and outside aliases through strict SL."""
import argparse
from pathlib import Path

from undefined_comparison_array_payload_cases import CASES
from undefined_comparison_array_payload_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name + '-' + group: CASES[name] for name in (
        'array-payload-captured-singleton', 'array-payload-live-replacement')
        for group in ('state', 'budget')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_array_payload*.py')),
                      ROOT / 'tests/semantics/undefined_comparison_object_reference_array_review_protocol.py'])
