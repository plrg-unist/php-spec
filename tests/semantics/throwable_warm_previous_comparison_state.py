#!/usr/bin/env python3
"""Check source-reached warm caches within previous chains under strict SL."""
import argparse
from pathlib import Path

from throwable_warm_previous_comparison_cases import CASES
from throwable_warm_previous_comparison_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=('root-cache-collision', 'child-cache-collision'), action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or ('root-cache-collision', 'child-cache-collision'))},
        checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_warm_previous_comparison_cases.py',
                      ROOT / 'tests/semantics/throwable_warm_previous_comparison_protocol.py',
                      ROOT / 'tests/semantics/throwable_warm_previous_comparison_state.py'])
