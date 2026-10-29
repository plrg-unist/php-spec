#!/usr/bin/env python3
"""Check private keys, protected overrides, caches and source-owned lifetimes."""
import argparse
import hashlib
from pathlib import Path

from throwable_nonpublic_peer_cases import CASES
from throwable_nonpublic_peer_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

SOURCE_SHA256 = {
    'private-same-name-cache-owners': '34ba2862c46a43f3255cf39e01b4b15ac7cdbd9a52dca47a7df44c997c2bcc78',
    'protected-override-alias-recursion': 'f69ea3bd476ccdaa699aee72609f2ff8088b50aacce72e6ab1582d495d8b4bd5',
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=tuple(EXPECTED), action='append')
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (args.case or EXPECTED)}
    assert all(hashlib.sha256(source).hexdigest() == SOURCE_SHA256[name]
               for name, source in selected.items())
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/' / name for name in (
            'throwable_nonpublic_peer_cases.py', 'throwable_nonpublic_peer_protocol.py',
            'throwable_nonpublic_peer_state.py', 'throwable_empty_clone_protocol.py',
            'throwable_interface_protocol.py', 'throwable_previous_graph_protocol.py',
            'throwable_trace_recursion_protocol.py', 'throwable_builtin_previous_protocol.py')],
        timeout=600)
