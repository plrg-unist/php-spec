#!/usr/bin/env python3
"""Check source-reached captured-array COW and shared-DAG comparisons."""
import argparse
from pathlib import Path

from throwable_trace_array_comparison_cases import CASES
from throwable_trace_array_comparison_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({name: CASES[name] for name in ('cow-and-tail', 'shared-dag')}, checks, PREFIX,
        args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_trace_array_comparison_cases.py',
                      ROOT / 'tests/semantics/throwable_trace_array_comparison_protocol.py',
                      ROOT / 'tests/semantics/throwable_trace_array_comparison_state.py'])
