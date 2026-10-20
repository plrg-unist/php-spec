#!/usr/bin/env python3
"""Preserve allocationless-array refusals at authentic old Boolean fronts."""
import argparse
from pathlib import Path

from undefined_scalar_compare_cases import CASES as LEFT
from undefined_scalar_compare_protocol import PREFIX, checks as left_checks
from undefined_scalar_compare_right_cases import CASES as RIGHT
from undefined_scalar_compare_right_protocol import checks as right_checks
from undefined_spaceship_state import ROOT, run


def checks(program, path, name):
    values = (left_checks(program, path, 'equal-live-plain') if name == 'old-boolean-left-array-refusal'
              else right_checks(program, path, 'right-equal-live-plain'))
    front = values[:values.index('PhpStep: S_resume ~> S_restored')]
    start = next(i for i, value in enumerate(values) if value.startswith('S_array = S_resume'))
    end = next(i for i in range(start, len(values)) if values[i].startswith('S_array_refused = ')) + 1
    return front + [
        '~((HARRAY 0) <- S_resume.ALLOCATIONS)',
        '~$scalar_compare_read_array(S_resume,perrorread)',
    ] + values[start:end] + ['~$scalar_compare_read_array(S_array,perrorread)']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {'old-boolean-left-array-refusal': LEFT['equal-live-plain'],
                'old-boolean-right-array-refusal': RIGHT['right-equal-live-plain']}
    watched = [*sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare_array_resume*.py')),
               *[ROOT / 'tests/semantics' / name for name in (
                   'undefined_scalar_compare_cases.py', 'undefined_scalar_compare_protocol.py',
                   'undefined_scalar_compare_right_cases.py', 'undefined_scalar_compare_right_protocol.py')]]
    run(selected, checks, PREFIX, args.output, extra_inputs=watched)
