#!/usr/bin/env python3
"""Check source-reached live property reference graphs in strict SL."""
import argparse
from pathlib import Path

from throwable_trace_property_alias_cases import CASES
from throwable_trace_property_alias_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({name: CASES[name] for name in ('cell-type-retarget', 'shared-cell-dag')},
        checks, PREFIX, args.output,
        extra_inputs=[ROOT / 'tests/semantics/throwable_trace_property_alias_cases.py',
                      ROOT / 'tests/semantics/throwable_trace_property_alias_protocol.py',
                      ROOT / 'tests/semantics/throwable_trace_property_alias_state.py'])
