#!/usr/bin/env python3
"""Check source-reached selected aliases and initially undefined declared slots."""
from pathlib import Path
import argparse

from declared_undef_comparison_review_cases import CASES
from declared_undef_comparison_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert not args.output.exists(),args.output
    selected = {name:CASES[name] for name in ('selected-alias-property-unset','initial-typed-hole-filled')}
    run(selected,checks,PREFIX,args.output,
        extra_inputs=[*sorted((ROOT/'tests/semantics').glob('declared_undef_comparison*.py')),
                      ROOT/'tests/semantics/nonpublic_numeric_comparison_review_protocol.py'])
