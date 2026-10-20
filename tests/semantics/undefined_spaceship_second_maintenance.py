#!/usr/bin/env python3
"""Check only the changed old missing-right resume controls, without full replay."""
import argparse
import base64
import json
from pathlib import Path

from undefined_spaceship_protocol import PREFIX, text
from undefined_spaceship_state import run


def checks(program, path, name):
    right = {'missing-left-cv': 'y', 'both-spaceship-string': 'right',
             'same-spaceship-string': 'x'}[name]
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.INPUT = VARIABLE (' + text(right) + ') z_right',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_resume_found = $us_seek(S_warn,3,1200)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,' + text(right) + ') = (n_right)',
    ]
    removed = ('S_resume[.STORE = $set_cell(S_resume.STORE,n_right,UNDEFINED)]'
               if name == 'missing-left-cv' else '$unset_name(S_resume,' + text(right) + ')')
    values += [
        'S_removed = ' + removed, '$error_read_valid(S_removed,perrorread)',
        '~$spaceship_read_other(S_removed,perrorread)',
        '$spaceship_read_again(S_removed,perrorread)',
        'PhpStep: S_removed ~> S_restored',
        'S_restored = S_removed[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = (perrorread_second)',
        'perrorread_second.ORIGINAL = perrorread.TASK',
        'perrorread_second.NAME = ' + text(right),
        'perrorread_second.RESULT = KNOWN PNULL',
        '$error_read_valid(S_restored,perrorread_second)',
        '~$spaceship_read_again(S_restored,perrorread_second)',
        'S_second_pause = $drive_steps(S_restored,1)', 'S_second_pause.COMPLETION = BUDGET',
        'S_second = S_second_pause[.COMPLETION = NORMAL]', '$us_stage(S_second,1)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread_second',
        'perrorcall.MESSAGE = ' + text('Undefined variable $' + right),
        '$error_call_valid(S_second,perrorcall)', '$us_guard(S_second)',
        'S_second.EVENTS = S_restored.EVENTS',
        'S_second.CODE = S_initial.CODE', 'S_second.POOLS = S_initial.POOLS',
    ]
    return values


if __name__ == '__main__':
    from undefined_spaceship_cases import CASES as SINGLE
    from undefined_spaceship_both_cases import CASES as BOTH
    from undefined_spaceship_same_cases import CASES as SAME
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'missing-left-cv': SINGLE['missing-left-cv'],
         'both-spaceship-string': BOTH['both-spaceship-string'],
         'same-spaceship-string': SAME['same-spaceship-string']}, checks, PREFIX, args.output)
