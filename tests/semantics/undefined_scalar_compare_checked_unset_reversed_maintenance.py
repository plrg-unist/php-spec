#!/usr/bin/env python3
"""Only affected old greater resume fronts, without old full-body renewal."""
import argparse
import base64
import json
from pathlib import Path

from undefined_scalar_compare_second_maintenance import PREFIX, checks as previous_checks
from undefined_spaceship_state import run


def checks(program, path, name):
    if name == 'gt-missing-left':
        return previous_checks(program, path, name)
    return [
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
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_left)',
        'perrorread_left =/= perrorread', '$error_read_valid(S_resume,perrorread_left)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread_left)',
        '$lookup(S_resume.ENV,$ptascii("right")) = (n_right)',
        'S_removed = S_resume[.STORE = $set_cell(S_resume.STORE,n_right,UNDEFINED)][.TODO = (ERROR_READ_RESULT perrorread_left) :: ptask_tail*]',
        '$error_read_valid(S_removed,perrorread_left)', '$us_guard(S_removed)',
        '$scalar_compare_checked_right_missing(S_removed,perrorread_left)',
        '~$scalar_compare_read_again(S_removed,perrorread_left)',
        '~$scalar_compare_checked_missing(S_removed,perrorread_left)',
        'PhpStep: S_removed ~> S_restored',
        'S_restored = S_removed[.TODO = perrorread_left.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_left.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_removed.EVENTS', '$us_guard(S_compared)',
    ]


if __name__ == '__main__':
    from undefined_scalar_compare_gt_ge_cases import CASES as SINGLE
    from undefined_scalar_compare_second_reversed_cases import CASES as SECOND
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'gt-missing-left': SINGLE['gt-missing-left'],
         'second-reversed-greater': SECOND['second-reversed-greater']},
        checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
