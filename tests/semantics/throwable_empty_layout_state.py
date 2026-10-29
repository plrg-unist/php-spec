#!/usr/bin/env python3
"""Check empty inline zero, actual property caches and source-owned graphs."""
import argparse
from pathlib import Path

from throwable_empty_layout_cases import CASES
from throwable_empty_layout_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=tuple(EXPECTED), action='append')
    args = parser.parse_args()
    run({name: CASES[name] for name in (args.case or EXPECTED)}, checks, PREFIX,
        args.output, extra_inputs=[ROOT / 'tests/semantics/' / name for name in (
            'throwable_empty_layout_cases.py', 'throwable_empty_layout_protocol.py',
            'throwable_empty_layout_state.py', 'throwable_interface_protocol.py',
            'throwable_builtin_previous_protocol.py', 'throwable_previous_graph_protocol.py',
            'throwable_trace_recursion_protocol.py')], timeout=600)
