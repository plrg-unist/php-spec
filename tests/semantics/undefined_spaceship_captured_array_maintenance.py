#!/usr/bin/env python3
"""Only the affected old initial-array captured-result entry assertion."""
import argparse
from pathlib import Path

from undefined_comparison_initial_array_review_cases import CASES
from undefined_comparison_initial_array_review_protocol import PREFIX, checks as old_checks
from undefined_spaceship_state import ROOT, run


def checks(program, path, name):
    values = old_checks(program, path, name)
    prefix = values[:values.index('S_warn_pause = $drive_steps(S,1)')]
    captured = values[values.index('S_captured = S[.RESULT = KNOWN (PARRAY n_initial)]'):]
    return prefix + captured + [
        'S_captured_pause = $drive_steps(S_captured,1)',
        'S_captured_pause.COMPLETION = BUDGET',
        'S_captured_warn = S_captured_pause[.COMPLETION = NORMAL]',
        'S_captured_warn = $prune_allocations($error_read_begin(S_captured))',
        'S_captured_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_captured) :: ptask_tail*',
        'perrorcall_captured.RESUME = ERROR_READ_RESULT perrorread_captured',
        '$error_call_valid(S_captured_warn,perrorcall_captured)', '$us_guard(S_captured_warn)',
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-initial-array-spaceship-rebound-reference',)}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_comparison_initial_array*.py')))
