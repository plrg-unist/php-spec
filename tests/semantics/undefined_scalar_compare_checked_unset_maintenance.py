#!/usr/bin/env python3
"""Affected forward quiet restores and the preserved reversed retry front."""
import argparse
import base64
import json
from pathlib import Path

from undefined_spaceship_protocol import PREFIX as COMMON
from undefined_spaceship_checked_unset_maintenance import checks as previous_checks
from undefined_spaceship_state import run

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = GREATEREQUAL')


def checks(program, path, name):
    if name == 'second-forward-equal':
        return previous_checks(program, path, name) + [
            '$scalar_compare_checked_missing(S_removed,perrorread_right)',
        ]
    reversed = name == 'ge-both-init'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_resume_found = $us_seek(S_warn,3,1200)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_right)',
        '$error_read_valid(S_resume,perrorread_right)',
        'perrorread_right.TASK = BINARY_RIGHT pbin (VARIABLE ($ptascii("left")) z_left) 10',
        'perrorread_right.RESULT = KNOWN PNULL',
        'S_removed = $unset_name(S_resume,$ptascii("left"))[.TODO = (ERROR_READ_RESULT perrorread_right) :: ptask_tail*]',
        '$error_read_valid(S_removed,perrorread_right)', '$us_guard(S_removed)',
        '~$spaceship_checked_missing(S_removed,perrorread_right)',
        'PhpStep: S_removed ~> S_restored',
    ]
    if reversed:
        return values + [
            '~$scalar_compare_checked_missing(S_removed,perrorread_right)',
            '$scalar_compare_read_again(S_removed,perrorread_right)',
            'S_restored = S_removed[.TODO = perrorread_right.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_right.BASE]',
            '$error_read_plan(S_restored) = (perrorread_later)',
            '$error_read_valid(S_restored,perrorread_later)',
            'perrorread_later.NAME = $ptascii("left")',
            'perrorread_later.INPUT = KNOWN PNULL',
            'S_later_pause = $drive_steps(S_restored,1)', 'S_later_pause.COMPLETION = BUDGET',
            'S_later = S_later_pause[.COMPLETION = NORMAL]', '$us_stage(S_later,1)',
            'S_later.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ERROR_READ_RESULT perrorread_later',
            '$error_call_valid(S_later,perrorcall)', 'S_later.EVENTS = S_removed.EVENTS',
        ]
    return values + [
        '$scalar_compare_checked_missing(S_removed,perrorread_right)',
        '~$scalar_compare_read_again(S_removed,perrorread_right)',
        'S_restored = S_removed[.TODO = (BINARY_RIGHT EQUAL (KNOWN PNULL) 10) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_right.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_removed.EVENTS', '$us_guard(S_compared)',
    ]


if __name__ == '__main__':
    from undefined_scalar_compare_right_cases import CASES as RIGHT
    from undefined_scalar_compare_second_cases import CASES as SECOND
    from undefined_scalar_compare_both_reversed_cases import CASES as REVERSED
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'right-equal-live-plain': RIGHT['right-equal-live-plain'],
         'second-forward-equal': SECOND['second-forward-equal'],
         'ge-both-init': REVERSED['ge-both-init']}, checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
