#!/usr/bin/env python3
"""Only old coherent foreign-source same-name entry assertions."""
import argparse
import base64
import json
from pathlib import Path

from undefined_spaceship_protocol import PREFIX as COMMON
from undefined_spaceship_state import run

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = SPACESHIP')


def checks(program, path, name):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        '$scalar_compare_missing_pair(S,perrorread)', 'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = BINARY_RIGHT pbin (VARIABLE n_left* z_left) z',
        'perrorread.INPUT = VARIABLE n_right* z_right',
        '$error_read_shape(BINARY_RIGHT EQUAL (VARIABLE n_left* z_left) z,VARIABLE n_left* z_right,perrorread.BASE) = (perrorread_same)',
        '$scalar_compare_missing_pair(S,perrorread_same)', '~$error_read_source(S,perrorread_same)',
        '~$error_read_valid(S,perrorread_same)',
        'S_forced = S[.TODO = perrorread_same.ORIGINAL :: ptask_tail*][.RESULT = perrorread_same.INPUT]',
        '$error_read_plan(S_forced) = eps',
    ]


if __name__ == '__main__':
    from undefined_scalar_compare_both_cases import CASES as FORWARD
    from undefined_spaceship_same_cases import CASES as SPACESHIP
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'equal-both-init': FORWARD['equal-both-init'],
         'same-spaceship-string': SPACESHIP['same-spaceship-string']}, checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
