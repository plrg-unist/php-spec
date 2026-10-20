#!/usr/bin/env python3
"""Affected captured-source controls; live domain does not authenticate source."""
import argparse
from pathlib import Path

from undefined_comparison_captured_object_cases import CASES as AUTHOR
from undefined_comparison_captured_object_protocol import checks as author_checks
from undefined_comparison_captured_object_review_cases import CASES as PEER
from undefined_comparison_captured_object_review_protocol import checks as peer_checks
from undefined_comparison_live_object_review_protocol import PREFIX
from undefined_spaceship_state import ROOT, run

SELECTED = {
    'old-captured-object-equal-variable-control': (AUTHOR, author_checks, 'captured-object-equal-right'),
    'old-captured-object-returned-variable-controls': (PEER, peer_checks, 'peer-captured-object-equal-returned'),
}


def checks(program, path, name):
    _, builder, old_name = SELECTED[name]
    values = builder(program, path, old_name)
    front = values[:values.index('S_warn_pause = $drive_steps(S,1)')]
    start = next(i for i, condition in enumerate(values)
                 if condition.startswith('$error_read_shape(BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) 1)'))
    if builder is author_checks:
        stop = start + 4
    else:
        stop = next(i for i, condition in enumerate(values) if condition.startswith('perrorread_undefined = '))
    return front + values[start:stop]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: cases[old_name] for name, (cases, _, old_name) in SELECTED.items()}
    run(selected, checks, PREFIX, args.output,
        extra_inputs=[*sorted((ROOT / 'tests/semantics').glob('undefined_comparison_captured_object*.py')),
                      *sorted((ROOT / 'tests/semantics').glob('undefined_comparison_live_object*.py'))])
