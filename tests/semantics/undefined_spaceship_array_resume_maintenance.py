#!/usr/bin/env python3
"""Retain old allocationless array refusals at two authentic scalar fronts."""
import argparse
from pathlib import Path

from undefined_spaceship_cases import CASES as LEFT
from undefined_spaceship_protocol import PREFIX, checks as left_checks
from undefined_spaceship_right_cases import CASES as RIGHT
from undefined_spaceship_right_protocol import checks as right_checks
from undefined_spaceship_state import run


def checks(program, path, name):
    left = name == 'old-left-array-refusal'
    values = (left_checks(program, path, 'missing-left-cv') if left else
              right_checks(program, path, 'right-live-plain'))
    front = values[:values.index('PhpStep: S_resume ~> S_restored')]
    variable, refused = ('S_changed', 'S_refused') if left else ('S_array', 'S_array_refused')
    start = next(i for i, value in enumerate(values) if value.startswith(variable + ' = S_resume'))
    end = next(i for i in range(start, len(values)) if values[i].startswith(refused + ' = ')) + 1
    return front + [
        '~((HARRAY 0) <- S_resume.ALLOCATIONS)',
        '~$spaceship_read_array(S_resume,perrorread)',
    ] + values[start:end] + ['~$spaceship_read_array(' + variable + ',perrorread)']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {'old-left-array-refusal': LEFT['missing-left-cv'],
                'old-right-array-refusal': RIGHT['right-live-plain']}
    run(selected, checks, PREFIX, args.output)
