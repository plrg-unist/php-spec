#!/usr/bin/env python3
"""Check reached builtin kind mismatch before physical Throwable slots."""
import argparse
from pathlib import Path

from throwable_builtin_kind_cases import CASES
from throwable_builtin_kind_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = ('severity-warm-previous', 'cyclic-tail-skip')
    run({name: CASES[name] for name in selected}, checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_builtin_kind_cases.py',
                      ROOT / 'tests/semantics/throwable_builtin_kind_protocol.py',
                      ROOT / 'tests/semantics/throwable_builtin_kind_state.py'])
