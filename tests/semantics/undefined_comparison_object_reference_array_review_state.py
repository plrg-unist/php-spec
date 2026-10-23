#!/usr/bin/env python3
"""Strict-SL ARRAY-to-CELL-to-OBJECT ownership and real destructor ordering."""
import argparse
from pathlib import Path

from undefined_comparison_object_reference_array_review_cases import CASES
from undefined_comparison_object_reference_array_review_protocol import PREFIX, checks
from undefined_spaceship_state import ROOT, run

LIVE = 'peer-object-reference-array-greater-target-default'
# Retain all 202 original premises. Move the eight repeated execution/budget
# checks to a separate fixture, repeating only their reached-state definitions.
BUDGET = (186, 187, 196, 197, 198, 199, 200, 201)
SETUP = (*range(6), *range(57, 60), *range(71, 74), *range(91, 94),
         *range(100, 103), 119, 122, *range(164, 167), 178, 179, 181, 185)
GROUPS = {
    LIVE + '-state': tuple(i for i in range(202) if i not in BUDGET),
    LIVE + '-budget': tuple(sorted((*SETUP, *BUDGET))),
}


def partition_checks(program, path, name):
    if name not in GROUPS:
        return checks(program, path, name)
    conditions = checks(program, path, LIVE)
    assert len(conditions) == 202
    return [conditions[i] for i in GROUPS[name]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = {name: CASES[LIVE if name in GROUPS else name] for name in (
        'peer-object-reference-array-captured-shared-cow',
        LIVE + '-state', LIVE + '-budget',
        'peer-object-reference-array-captured-supplied-throw')}
    if args.case is not None:
        assert len(args.case) == len(set(args.case)) and set(args.case) <= selected.keys()
        selected = {name: source for name, source in selected.items() if name in args.case}
    run(selected, partition_checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_comparison_object_reference_array*.py')))
