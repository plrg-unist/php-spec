#!/usr/bin/env python3
"""Check real deleted-history tables, key order and surviving physical owners."""
import argparse
import hashlib
from pathlib import Path

from throwable_dynamic_unset_peer_cases import CASES
from throwable_dynamic_unset_peer_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

SOURCE_SHA256={
    'dynamic-unset-count-key-reinsert-cow':'9dbf9038e22569f3aea1f510ad1612f968b843a2938de1dcf48d9b5b95ddb7cf',
    'dynamic-unset-alias-cycle-owners-v2':'aa2ba0515070b1b7a4316098c81474396133d27bc8f82c0afc48e0a33d82ddd5',
}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--case',choices=tuple(EXPECTED),action='append')
    args=parser.parse_args()
    selected={name:CASES[name] for name in (args.case or EXPECTED)}
    assert all(hashlib.sha256(source).hexdigest()==SOURCE_SHA256[name]
               for name,source in selected.items())
    run(selected,checks,PREFIX,args.output,
        extra_inputs=[ROOT/'tests/semantics'/name for name in (
            'throwable_dynamic_unset_peer_cases.py','throwable_dynamic_unset_peer_protocol.py',
            'throwable_dynamic_unset_peer_state.py','throwable_uninitialized_peer_protocol.py',
            'throwable_empty_clone_protocol.py','throwable_interface_protocol.py',
            'throwable_previous_graph_protocol.py','throwable_trace_recursion_protocol.py',
            'throwable_builtin_previous_protocol.py')],timeout=600)
