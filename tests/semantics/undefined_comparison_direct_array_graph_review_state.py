#!/usr/bin/env python3
"""Run shared-DAG COW and supplied-Exception core/cut-budget fixtures."""
import argparse
from pathlib import Path

from undefined_comparison_direct_array_graph_review_cases import CASES
from undefined_comparison_direct_array_graph_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = {name + '-' + group: CASES[name] for name in (
        'direct-dag-captured-cow','direct-dag-supplied-throw') for group in ('state','budget')}
    if args.case is not None:
        assert len(args.case) == len(set(args.case)) and set(args.case) <= selected.keys()
        selected = {name: source for name, source in selected.items() if name in args.case}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_direct_array_graph*.py')),
                      ROOT / 'tests/semantics/undefined_comparison_object_reference_array_review_protocol.py'])
