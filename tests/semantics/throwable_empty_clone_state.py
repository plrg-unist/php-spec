#!/usr/bin/env python3
"""Check reached empty-cache clone storage, owners and one-sided comparison."""
import argparse
import hashlib
from pathlib import Path

from throwable_empty_clone_cases import CASES
from throwable_empty_clone_protocol import EXPECTED, PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert hashlib.sha256(CASES['empty-cached-clone-owners']).hexdigest() == \
        'a90b8377c1165283eabb0d6da0a5aed28e5f0272d8a40ec517c499d895c4f691'
    run({name: CASES[name] for name in EXPECTED}, checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/' / name for name in (
            'throwable_empty_clone_cases.py', 'throwable_empty_clone_protocol.py',
            'throwable_empty_clone_state.py', 'throwable_interface_protocol.py',
            'throwable_previous_graph_protocol.py', 'throwable_builtin_previous_protocol.py')],
        timeout=600)
