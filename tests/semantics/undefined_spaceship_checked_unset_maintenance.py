#!/usr/bin/env python3
"""Affected old resume fronts, without renewing their complete source campaigns."""
import argparse
import base64
import json
from pathlib import Path

from undefined_spaceship_protocol import PREFIX as COMMON, text
from undefined_spaceship_state import run

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = SPACESHIP \\/ pbin = EQUAL')


def checks(program, path, name):
    single = name == 'right-live-plain'
    boolean = name == 'second-forward-equal'
    left = 'y' if single else 'left'
    shape = '$scalar_compare_right_read_shape' if boolean else '$spaceship_right_read_shape'
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
        shape + '(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_right)',
        '$error_read_valid(S_resume,perrorread_right)',
        'perrorread_right.TASK = BINARY_RIGHT pbin (VARIABLE (' + text(left) + ') z_left) 10',
        'perrorread_right.RESULT = KNOWN PNULL',
        'S_removed = $unset_name(S_resume,' + text(left) + ')[.TODO = (ERROR_READ_RESULT perrorread_right) :: ptask_tail*]',
        '$error_read_valid(S_removed,perrorread_right)', '$us_guard(S_removed)',
        '~$spaceship_read_again(S_removed,perrorread_right)',
        '~$scalar_compare_read_again(S_removed,perrorread_right)',
        'PhpStep: S_removed ~> S_restored',
    ]
    if boolean:
        return values + [
            '~$spaceship_checked_missing(S_removed,perrorread_right)',
            'S_restored = S_removed[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed left operand"]',
            'S_restored.EVENTS = S_removed.EVENTS',
        ]
    return values + [
        '$spaceship_checked_missing(S_removed,perrorread_right)',
        'S_restored = S_removed[.TODO = (BINARY_RIGHT SPACESHIP (KNOWN PNULL) 10) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_right.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 0)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_removed.EVENTS', '$us_guard(S_compared)',
    ]


if __name__ == '__main__':
    from undefined_spaceship_right_cases import CASES as RIGHT
    from undefined_spaceship_second_cases import CASES as SECOND
    from undefined_scalar_compare_second_cases import CASES as FORWARD
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'right-live-plain': RIGHT['right-live-plain'],
         'second-spaceship-string': SECOND['second-spaceship-string'],
         'second-forward-equal': FORWARD['second-forward-equal']},
        checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
