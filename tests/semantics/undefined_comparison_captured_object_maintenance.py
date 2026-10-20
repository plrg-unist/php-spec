#!/usr/bin/env python3
"""Affected source-certificate controls without historical full-body renewal."""
import argparse
from pathlib import Path

import undefined_scalar_compare_captured_primitive_maintenance as second
from undefined_scalar_compare_captured_primitive_cases import CASES as PRIMITIVES
from undefined_scalar_compare_captured_primitive_protocol import checks as primitive_checks
from undefined_spaceship_state import ROOT, run

PREFIX = second.PREFIX
SELECTED = dict(second.SELECTED)
SELECTED.update({
    'old-captured-equal-excluded-payload': (PRIMITIVES, primitive_checks, 'captured-equal-right-zero'),
    'old-captured-greater-excluded-payload': (PRIMITIVES, primitive_checks, 'captured-greater-left-string'),
})


def checks(program, path, name):
    if name in second.SELECTED:
        return second.checks(program, path, name)
    _, builder, old_name = SELECTED[name]
    values = builder(program, path, old_name)
    front = values[:values.index('S_warn_pause = $drive_steps(S,1)')]
    start = next(i for i, value in enumerate(values) if value.startswith('perrorread_object = '))
    stop = next(i for i, value in enumerate(values) if value.startswith('perrorread_null = '))
    excluded = values[start:stop]
    equal = old_name == 'captured-equal-right-zero'
    unavailable = ('[.INPUT = KNOWN (POBJECT (|S.OBJECTS|))][.RESULT = KNOWN (POBJECT (|S.OBJECTS|))]'
                   if equal else '[.ORIGINAL = BINARY_RIGHT GREATER (KNOWN (POBJECT (|S.OBJECTS|))) 14][.TASK = BINARY_RIGHT GREATER (KNOWN (POBJECT (|S.OBJECTS|))) 14]')
    return front + excluded + [
        'perrorread_unallocated = perrorread' + unavailable,
        '$error_read_shape(perrorread_unallocated.ORIGINAL,perrorread_unallocated.INPUT,perrorread_unallocated.BASE) = (perrorread_unallocated)',
        '$error_read_source(S,perrorread_unallocated)', '$error_read_valid(S,perrorread_unallocated)',
        '~$comparison_read_object(S,perrorread_unallocated)',
        '~$scalar_compare_read_other(S,perrorread_unallocated)',
        '$error_read_plan(S[.TODO = perrorread_unallocated.ORIGINAL :: ptask_tail*][.RESULT = perrorread_unallocated.INPUT]) = eps',
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: cases[old_name] for name, (cases, _, old_name) in SELECTED.items()}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare*.py')),
                      *sorted((ROOT / 'tests/semantics').glob('undefined_comparison_captured_object*.py'))])
