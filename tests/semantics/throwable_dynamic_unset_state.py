#!/usr/bin/env python3
"""Check real deleted-history clone routes and typed aliases through final owners."""
import argparse
from pathlib import Path

from throwable_dynamic_unset_protocol import CASES, EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--case',choices=tuple(EXPECTED),action='append')
    args=parser.parse_args()
    run({name:CASES[name] for name in (args.case or EXPECTED)},checks,PREFIX,args.output,
        extra_inputs=[ROOT/'tests/semantics'/name for name in (
            'throwable_dynamic_unset_cases.py','throwable_dynamic_unset_order_cases.py','throwable_dynamic_unset_protocol.py','throwable_dynamic_unset_state.py',
            'throwable_dynamic_unset_peer_cases.py','throwable_dynamic_unset_peer_protocol.py',
            'throwable_uninitialized_protocol.py','throwable_uninitialized_peer_protocol.py',
            'throwable_empty_clone_protocol.py','throwable_interface_protocol.py',
            'throwable_previous_graph_protocol.py','throwable_builtin_previous_protocol.py')],timeout=600)
