#!/usr/bin/env python3
"""Existing primitive-entry contracts with the reached-state validator argument."""
import argparse
from pathlib import Path

from undefined_spaceship_array_resume_cases import CASES as CURRENT
from undefined_spaceship_array_resume_protocol import checks as current_checks
from undefined_spaceship_captured_array_cases import CASES as CAPTURED
from undefined_spaceship_captured_array_protocol import checks as captured_checks
from undefined_comparison_object_array_protocol import PREFIX
from undefined_spaceship_state import ROOT, run

SELECTED = {
    'old-current-primitive-array-entry-contract': (CURRENT, current_checks, 'array-resume-missing-right-empty'),
    'old-captured-primitive-array-entry-contract': (CAPTURED, captured_checks, 'captured-left-assignment-empty'),
}


def checks(program, path, name):
    _, builder, old_name = SELECTED[name]
    values = builder(program, path, old_name)
    prefix = values[:values.index('PhpStep: S_resume ~> S_restored')]
    entries = [condition for condition in values
               if condition.startswith(('$spaceship_read_array_entries(', '~$spaceship_read_array_entries('))]
    return prefix + entries


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: cases[old_name] for name, (cases, _, old_name) in SELECTED.items()}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_object_array*.py')),
                      *sorted((ROOT / 'tests/semantics').glob('undefined_spaceship*.py'))])
