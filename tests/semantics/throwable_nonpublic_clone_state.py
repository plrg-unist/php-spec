#!/usr/bin/env python3
"""Check real nonpublic clone tables and final per-copy property type sources."""
import argparse
import hashlib
from pathlib import Path

from throwable_nonpublic_clone_cases import CASES
from throwable_nonpublic_clone_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert hashlib.sha256(CASES['nonpublic-cached-clone-types']).hexdigest() == \
        '1c1f7565c48bd14481f8190fb770be8b6654b14ecd5aeeda16bc0068fa2f1537'
    run({name: CASES[name] for name in EXPECTED}, checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/' / name for name in (
            'throwable_nonpublic_clone_cases.py', 'throwable_nonpublic_clone_protocol.py',
            'throwable_nonpublic_clone_state.py', 'throwable_empty_clone_protocol.py',
            'throwable_interface_protocol.py', 'throwable_previous_graph_protocol.py',
            'throwable_builtin_previous_protocol.py')], timeout=600)
