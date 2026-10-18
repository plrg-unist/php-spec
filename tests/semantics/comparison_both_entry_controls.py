#!/usr/bin/env python3
"""Check only maintained both-missing entry assertions after ingress extensions."""
import argparse
from pathlib import Path

from undefined_scalar_compare_cases import CASES as LEFT
from undefined_scalar_compare_right_cases import CASES as RIGHT
from undefined_scalar_compare_gt_ge_cases import CASES as REVERSED
from undefined_scalar_compare_protocol import PREFIX as COMMON, checks as left_checks
from undefined_scalar_compare_right_protocol import checks as right_checks
from undefined_scalar_compare_gt_ge_protocol import checks as reversed_checks
from undefined_spaceship_state import ROOT, run

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS', r'pbin = EQUAL \/ pbin = GREATER')
CASES = {
    'forward-left': LEFT['equal-live-plain'],
    'forward-right': RIGHT['right-equal-live-plain'],
    'reversed-left': REVERSED['gt-missing-left'],
}


def checks(program, path, name):
    builder, case, entry, selected, missing = {
        'forward-left': (left_checks, 'equal-live-plain', 'S_missing_entry', 'perrorread', 'x'),
        'forward-right': (right_checks, 'right-equal-live-plain', 'S_entry_missing', 'perrorread_left', 'left'),
        'reversed-left': (reversed_checks, 'gt-missing-left', 'S_missing_entry', 'perrorread_right', 'right'),
    }[name]
    values = builder(program, path, case)
    # Keep the actual checked program and authentic initial continuation, then
    # select just the affected maintained constructed-state assertion.
    result = values[:values.index('S_warn_pause = $drive_steps(S,1)')]
    begin = next(i for i, condition in enumerate(values) if condition.startswith(entry + ' = '))
    end = values.index('$error_read_plan(' + entry + ') = (' + selected + ')')
    result += values[begin:end + 1]
    result += [
        '$us_guard(' + entry + ')',
        '$error_read_valid(' + entry + ',' + selected + ')',
        '$scalar_compare_missing_pair(' + entry + ',' + selected + ')',
        selected + '.NAME = $ptascii("' + missing + '")',
        selected + '.LINE = 10',
    ]
    if name != 'forward-left':
        result += ['~$scalar_compare_missing_pair(' + entry + ',perrorread)',
                   selected + ' =/= perrorread']
    result += [
        'PhpStep: ' + entry + ' ~> S_entry_warn',
        'S_entry_warn = $prune_allocations($error_read_begin(' + entry + '))',
        'S_entry_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_entry) :: ptask_tail*',
        'perrorcall_entry.RESUME = ERROR_READ_RESULT ' + selected,
        'perrorcall_entry.MESSAGE = $ptascii("Undefined variable $' + missing + '")',
        'perrorcall_entry.LINE = 10',
        '$error_call_valid(S_entry_warn,perrorcall_entry)',
        'S_entry_warn.EVENTS = ' + entry + '.EVENTS', '$us_guard(S_entry_warn)',
    ]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(CASES, checks, PREFIX, args.output,
        extra_inputs=[Path(__file__), *sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare*.py'))])
