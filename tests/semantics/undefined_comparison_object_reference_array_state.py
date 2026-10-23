#!/usr/bin/env python3
"""Source-reached object reference COW and current-cell ownership."""
import argparse
from pathlib import Path

from undefined_comparison_object_reference_array_cases import CASES
from undefined_comparison_object_reference_array_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'object-reference-array-captured-singleton', 'object-reference-array-live-replacement')}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_comparison_object_reference_array*.py')))
