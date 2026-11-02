#!/usr/bin/env python3
"""Check declared holes and a separate INITIAL-cache callback boundary."""
import argparse
import hashlib
from pathlib import Path

from throwable_uninitialized_peer_cases import CASES
from throwable_uninitialized_peer_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

SOURCE_SHA256 = {
    'initial-hole-inline-cache-clone': '578035868e12e8431c437e2365ca85ca22876af6a52ccc99f887d13599d6ef58',
    'private-hole-alias-cycle-owners': '119a0441d32746e9578aaa9cf6ea2d1936ad4b2b873e24eac80a4d921caeab6b',
    'initial-hole-stringable-control': '8758ddd937938e3e8be788d511da22b9ec8625e6a43c232b930369687a3b03d5',
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--case',choices=tuple(EXPECTED),action='append')
    args = parser.parse_args()
    selected = {name:CASES[name] for name in (args.case or EXPECTED)}
    assert all(hashlib.sha256(source).hexdigest() == SOURCE_SHA256[name]
               for name,source in selected.items())
    run(selected,checks,PREFIX,args.output,
        extra_inputs=[ROOT/'tests/semantics'/name for name in (
            'throwable_uninitialized_peer_cases.py','throwable_uninitialized_peer_protocol.py',
            'throwable_uninitialized_peer_state.py','throwable_empty_clone_protocol.py',
            'throwable_interface_protocol.py','throwable_previous_graph_protocol.py',
            'throwable_trace_recursion_protocol.py','throwable_builtin_previous_protocol.py')],
        timeout=600)
