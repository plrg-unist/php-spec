#!/usr/bin/env python3
"""Check source-reached early class mismatch and aggregate tail skip."""
import argparse
from pathlib import Path

from throwable_cross_kind_cases import CASES
from throwable_cross_kind_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'state-skip': CASES['state-skip']}, checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_cross_kind_cases.py',
                      ROOT / 'tests/semantics/throwable_cross_kind_protocol.py',
                      ROOT / 'tests/semantics/throwable_cross_kind_state.py'])
