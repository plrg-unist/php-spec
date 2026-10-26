#!/usr/bin/env python3
"""Check reached mixed property-table snapshots and externally held cells."""
from pathlib import Path
import argparse

from mixed_property_table_comparison_review_cases import CASES
from mixed_property_table_comparison_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert not args.output.exists(),args.output
    selected = {name:CASES[name] for name in ('left-copy-live-private-slot','old-table-cell-after-dynamic-unset')}
    run(selected,checks,PREFIX,args.output,
        extra_inputs=[*sorted((ROOT/'tests/semantics').glob('mixed_property_table_comparison*.py')),
                      ROOT/'tests/semantics/nonpublic_numeric_comparison_review_protocol.py'])
