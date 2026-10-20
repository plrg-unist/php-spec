#!/usr/bin/env python3
"""Affected old same-CV removals only through the second invocation."""
import argparse
import base64
import json
from pathlib import Path

from undefined_spaceship_protocol import PREFIX as COMMON
from undefined_spaceship_state import run

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if ' + r'pbin = EQUAL \/ pbin = LESSEQUAL')


def checks(program, path, name):
    return [
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
        'S_removed = $unset_name(S_resume,$ptascii("x"))',
        '$error_read_valid(S_removed,perrorread)',
        '~$scalar_compare_read_other(S_removed,perrorread)',
        '$scalar_compare_read_again(S_removed,perrorread)',
        'PhpStep: S_removed ~> S_restored',
        'S_restored = S_removed[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = (perrorread_second)',
        'perrorread_second.ORIGINAL = perrorread.TASK',
        'perrorread_second.NAME = $ptascii("x")',
        'perrorread_second.RESULT = KNOWN PNULL',
        'perrorread_second.NAME = perrorread.NAME',
        '$error_read_valid(S_restored,perrorread_second)',
        '$error_read_source(S_restored,perrorread_second)',
        '~$scalar_compare_read_again(S_restored,perrorread_second)',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        'S_second_pause = $drive_steps(S_restored,1)', 'S_second_pause.COMPLETION = BUDGET',
        'S_second = S_second_pause[.COMPLETION = NORMAL]', '$us_stage(S_second,1)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread_second',
        '$error_call_valid(S_second,perrorcall)', '$us_guard(S_second)',
        'S_second.EVENTS = S_restored.EVENTS',
    ]


if __name__ == '__main__':
    from undefined_scalar_compare_same_cases import CASES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({name: CASES[name] for name in ('same-forward-equal-string', 'same-forward-less-equal-false')},
        checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
