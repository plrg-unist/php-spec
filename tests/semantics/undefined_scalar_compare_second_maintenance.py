#!/usr/bin/env python3
"""Affected old forward restore plus reversed and spaceship boundaries only."""
import argparse
import base64
import json
from pathlib import Path

from undefined_spaceship_protocol import PREFIX as COMMON
from undefined_spaceship_state import run

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = GREATER \\/ pbin = SPACESHIP')


def checks(program, path, name):
    reversed = name == 'gt-missing-left'
    spaceship = name == 'both-spaceship-string'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_resume_found = $us_seek(S_warn,3,1200)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("right")) = (n_right)',
        'S_removed = S_resume[.STORE = $set_cell(S_resume.STORE,n_right,UNDEFINED)]',
        '$error_read_valid(S_removed,perrorread)',
    ]
    if reversed:
        return values + [
            '~$scalar_compare_read_other(S_removed,perrorread)',
            '~$scalar_compare_read_again(S_removed,perrorread)',
            'PhpStep: S_removed ~> S_refused',
            'S_refused = S_removed[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
            'S_refused.EVENTS = S_removed.EVENTS',
        ]
    values += [
        ('$spaceship_read_again' if spaceship else '$scalar_compare_read_again') + '(S_removed,perrorread)',
        ('$spaceship_read_again' if not spaceship else '$scalar_compare_read_again') + '(S_removed,perrorread) = false',
        'PhpStep: S_removed ~> S_restored',
        'S_restored = S_removed[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = (perrorread_second)',
        'perrorread_second.ORIGINAL = perrorread.TASK',
        'perrorread_second.NAME = $ptascii("right")', 'perrorread_second.RESULT = KNOWN PNULL',
        '$error_read_valid(S_restored,perrorread_second)',
        'S_second_pause = $drive_steps(S_restored,1)', 'S_second_pause.COMPLETION = BUDGET',
        'S_second = S_second_pause[.COMPLETION = NORMAL]', '$us_stage(S_second,1)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread_second',
        '$error_call_valid(S_second,perrorcall)', '$us_guard(S_second)',
        'S_second.EVENTS = S_restored.EVENTS',
    ]
    return values


if __name__ == '__main__':
    from undefined_scalar_compare_cases import CASES as FORWARD
    from undefined_scalar_compare_gt_ge_cases import CASES as REVERSED
    from undefined_spaceship_both_cases import CASES as SPACESHIP
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'equal-live-plain': FORWARD['equal-live-plain'],
         'gt-missing-left': REVERSED['gt-missing-left'],
         'both-spaceship-string': SPACESHIP['both-spaceship-string']}, checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
