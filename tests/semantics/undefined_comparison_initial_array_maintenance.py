#!/usr/bin/env python3
"""Only affected old SPACE/right and Boolean/left array entry expectations."""
import argparse
from pathlib import Path

from undefined_spaceship_array_resume_cases import CASES as SPACE
from undefined_spaceship_array_resume_protocol import checks as space_checks
from undefined_scalar_compare_array_resume_cases import CASES as BOOLEAN
from undefined_scalar_compare_array_resume_protocol import checks as boolean_checks
from undefined_comparison_initial_array_protocol import PREFIX
from undefined_spaceship_state import ROOT, run


def checks(program, path, name):
    space = name == 'old-space-right-array-entry'
    values = (space_checks(program, path, 'array-resume-missing-right-empty') if space else
              boolean_checks(program, path, 'boolean-array-equal-empty'))
    values = values[:values.index('PhpStep: S_resume ~> S_restored')]
    return values + [
        'S_entry = $unset_name(S_resume,$ptascii("missing"))',
        '$' + ('spaceship' if space else 'scalar_compare') + '_read_array(S_entry,perrorread)',
        'S_entry_front = S_entry[.TODO = ptask_original :: ptask_tail*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_entry_front) = (perrorread)', '$error_read_valid(S_entry_front,perrorread)',
        'S_entry_pause = $drive_steps(S_entry_front,1)', 'S_entry_pause.COMPLETION = BUDGET',
        'S_entry_warn = S_entry_pause[.COMPLETION = NORMAL]',
        'S_entry_warn = $prune_allocations($error_read_begin(S_entry_front))',
        'S_entry_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_again) :: ptask_tail*',
        'perrorcall_again.RESUME = ERROR_READ_RESULT perrorread',
        '$error_call_valid(S_entry_warn,perrorcall_again)', '$us_guard(S_entry_warn)',
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {'old-space-right-array-entry': SPACE['array-resume-missing-right-empty'],
                'old-boolean-left-array-entry': BOOLEAN['boolean-array-equal-empty']}
    watched = [*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_initial_array*.py')),
               *sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_array_resume*.py'))]
    run(selected, checks, PREFIX, args.output, extra_inputs=watched)
