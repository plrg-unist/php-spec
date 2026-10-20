#!/usr/bin/env python3
"""Old distinct-CV fronts refuse forged same-name source metadata."""
import argparse
import base64
import json
from pathlib import Path

from undefined_scalar_compare_second_reversed_protocol import PREFIX
from undefined_spaceship_state import run


def checks(program, path, name):
    left = name.startswith('peer-')
    variable = 'n_left*' if left else 'n_right*'
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'perrorread.ORIGINAL = BINARY_RIGHT pbin (VARIABLE n_left* z_left) z',
        'perrorread.INPUT = VARIABLE n_right* z_right',
        'ptask_same = BINARY_RIGHT pbin (VARIABLE ' + variable + ' z_left) z',
        'poperand_same = VARIABLE ' + variable + ' z_right',
        '$scalar_compare_right_read_shape(ptask_same,poperand_same,perrorread.BASE) = (perrorread_same)',
        '$scalar_compare_missing_pair(S,perrorread_same)',
        '~$error_read_source(S,perrorread_same)', '~$error_read_valid(S,perrorread_same)',
        '$error_read_shape(ptask_same,poperand_same,perrorread.BASE) = (perrorread_old_left)',
        'perrorread_old_left =/= perrorread_same',
        '~$scalar_compare_missing_pair(S,perrorread_old_left)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'S_forced = S[.TODO = ptask_same :: ptask_tail*][.RESULT = poperand_same]',
        '$error_read_plan(S_forced) = eps',
    ]


if __name__ == '__main__':
    from undefined_scalar_compare_gt_ge_cases import CASES as SINGLE
    from undefined_scalar_compare_both_reversed_review_cases import CASES as BOTH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'ge-missing-right-false': SINGLE['ge-missing-right-false'],
         'peer-both-missing-greater-equal-left-bound-to-target-reference':
             BOTH['peer-both-missing-greater-equal-left-bound-to-target-reference']},
        checks, PREFIX, args.output,
        extra_inputs=sorted(Path(__file__).parent.glob('undefined_scalar_compare*.py')))
