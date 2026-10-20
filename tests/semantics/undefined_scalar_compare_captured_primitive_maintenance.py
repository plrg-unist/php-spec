#!/usr/bin/env python3
"""Affected second-Warning NULL records, stopping after their raw comparison."""
import argparse
from pathlib import Path

from undefined_scalar_compare_second_cases import CASES as FORWARD
from undefined_scalar_compare_second_protocol import checks as forward_checks
from undefined_scalar_compare_second_reversed_cases import CASES as REVERSED
from undefined_scalar_compare_second_reversed_protocol import checks as reversed_checks
from undefined_scalar_compare_second_same_cases import CASES as SAME
from undefined_scalar_compare_second_same_protocol import checks as same_checks
from undefined_spaceship_protocol import PREFIX as COMMON
from undefined_spaceship_state import ROOT, run

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = GREATER')
SELECTED = {
    'old-forward-second-null': (FORWARD, forward_checks, 'second-forward-equal'),
    'old-reversed-second-null': (REVERSED, reversed_checks, 'second-reversed-greater'),
    'old-same-second-null': (SAME, same_checks, 'same-second-equal'),
}


def checks(program, path, name):
    _, builder, old_name = SELECTED[name]
    values = builder(program, path, old_name)
    front = values[:values.index('S_done = $drive_steps(S_compared,4000)')]
    start = next(i for i, value in enumerate(values) if value.startswith('perrorread_nonnull = '))
    owning = values[start:start + 4]
    assert all('perrorread_nonnull' in condition for condition in owning)
    primitive = [condition.replace('perrorread_nonnull', 'perrorread_primitive')
                 .replace('KNOWN PUNDEFINED', 'KNOWN (PINT 1)').lstrip('~')
                 for condition in owning]
    return front + owning + primitive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: cases[old_name] for name, (cases, _, old_name) in SELECTED.items()}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=sorted((ROOT / 'tests/semantics').glob('undefined_scalar_compare*.py')))
