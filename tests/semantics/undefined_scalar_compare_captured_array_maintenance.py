#!/usr/bin/env python3
"""Only affected old captured-array source/domain assertions."""
import argparse
from pathlib import Path

from undefined_comparison_initial_array_review_cases import CASES as INITIAL
from undefined_comparison_initial_array_review_protocol import PREFIX, checks as initial_checks
from undefined_spaceship_captured_array_cases import CASES as SPACE
from undefined_spaceship_captured_array_protocol import checks as space_checks
from undefined_spaceship_state import ROOT, run


def checks(program, path, name):
    if name == 'old-initial-equal-known-array':
        values = initial_checks(program, path, 'peer-initial-array-checked-left-unset-default')
        front = values[:values.index('S_warn_pause = $drive_steps(S,1)')]
        captured = values[values.index('ptask_known = BINARY_RIGHT EQUAL (KNOWN (PARRAY n_initial)) 15'):]
        return front + captured + [
            'S_known_pause = $drive_steps(S_known,1)', 'S_known_pause.COMPLETION = BUDGET',
            'S_known_warn = S_known_pause[.COMPLETION = NORMAL]',
            'S_known_warn = $prune_allocations($error_read_begin(S_known))',
            'S_known_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_known) :: ptask_tail*',
            'perrorcall_known.RESUME = ERROR_READ_RESULT perrorread_known',
            '$error_call_valid(S_known_warn,perrorcall_known)', '$us_guard(S_known_warn)',
        ]
    old_name = 'captured-left-assignment-empty' if name == 'old-space-left-foreign-array' else 'captured-right-runtime-array'
    values = space_checks(program, path, old_name)
    front = values[:values.index('S_warn_pause = $drive_steps(S,1)')]
    foreign = values[values.index(next(v for v in values if v.startswith('perrorread_foreign = '))):]
    foreign = foreign[:foreign.index('$error_read_plan(S[.TODO = perrorread_foreign.ORIGINAL :: ptask_tail*][.RESULT = perrorread_foreign.INPUT][.BASE = perrorread_foreign.BASE]) = eps') + 1]
    return front + foreign


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {
        'old-space-left-foreign-array': SPACE['captured-left-assignment-empty'],
        'old-space-right-foreign-array': SPACE['captured-right-runtime-array'],
        'old-initial-equal-known-array': INITIAL['peer-initial-array-checked-left-unset-default'],
    }
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_initial_array*.py')),
                      *sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_captured_array*.py'))])
