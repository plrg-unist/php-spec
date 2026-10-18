#!/usr/bin/env python3
"""Mixed selected-cell/CV entry reuses the reached plain arithmetic protocol."""
import argparse
import hashlib
from pathlib import Path

import mixed_arithmetic_cases as cases
import plain_arithmetic_protocol as prior

shared = prior.shared
CASES = ('mixed-arithmetic-add-right-warning', 'mixed-arithmetic-power-deprecated-throw')
HELPERS = prior.HELPERS + r'''
dec $mixed_arithmetic_frontier(pstate, nat) : bool
def $mixed_arithmetic_frontier(S, 0) = ($arithmetic_mixed_plan(S) =/= eps)
def $mixed_arithmetic_frontier(S, n) = $plain_arithmetic_frontier(S, n) -- if n =/= 0
dec $mixed_arithmetic_seek(pstate, nat, nat) : pstate
def $mixed_arithmetic_seek(S, n_stage, n) = S -- if $mixed_arithmetic_frontier(S, n_stage)
def $mixed_arithmetic_seek(S, n_stage, n) = S
  -- if ~$mixed_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $mixed_arithmetic_seek(S, n_stage, n) = S
  -- if ~$mixed_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $mixed_arithmetic_seek(S, n_stage, n) = $mixed_arithmetic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mixed_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    quiet = name == CASES[0]
    checks = (prior.quiet_conditions(prior.CASES[0], program, path, stdout) if quiet
              else prior.power_conditions(prior.CASES[2], program, path, stdout))
    # Preserve the old protocol. Only its entry, selected LEFT and owner count differ.
    result = []
    for check in checks:
        check = (check.replace('$plain_arithmetic_seek(', '$mixed_arithmetic_seek(')
                 .replace('$plain_arithmetic_frontier(', '$mixed_arithmetic_frontier(')
                 .replace('$arithmetic_cv_operation(', '$arithmetic_mixed_operation(')
                 .replace('$arithmetic_cv_plan(', '$arithmetic_mixed_plan(')
                 .replace('pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
                          'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left')
                 .replace('~(n_left <- S_entry.REFCELLS)', 'n_left <- S_entry.REFCELLS')
                 .replace('$arithmetic_mixed_operation(S_entry[.REFCELLS = [n_left]]) = eps',
                          '$arithmetic_mixed_operation(S_entry[.REFCELLS = eps]) = eps'))
        if 'HCELL n_left) = 1' in check:
            check = check.replace('HCELL n_left) = 1', 'HCELL n_left) = 2')
        result.append(check)
    result += [
        '$arithmetic_mixed_valid(S_entry, pintegeroperation)',
        '$arithmetic_mixed_pointers(pintegeroperation.LEFTPOINTER, pintegeroperation.RIGHTPOINTER)',
        '$arithmetic_cv_operation(S_entry) = eps', '$arithmetic_cv_plan(S_entry) = eps',
        '$lookup(S_entry.ENV, $ptascii("selectedAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("selectedAlias")) = (n_left)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 2',
        '$arithmetic_cv_value(S_entry, pintegeroperation.LEFTPOINTER) = ' + ('(PINT 12)' if quiet else '(pvalue_left)'),
    ]
    if quiet:
        result += [
            'n_left <- S_entry.REFCELLS', '~(n_right <- S_entry.REFCELLS)',
            '$arithmetic_add_plan(S_entry) = eps',
            '~$arithmetic_mixed_pointers(INTEGER_CV ($ptascii("left")), INTEGER_CV ($ptascii("right")))',
            '~$arithmetic_mixed_pointers(INTEGER_CELL n_left, INTEGER_CELL n_right)',
            '~$arithmetic_mixed_pointers(INTEGER_CV ($ptascii("left")), INTEGER_COPY (PINT 5))',
            '~$arithmetic_mixed_valid(S_entry, pintegeroperation[.OP = MULTIPLY])',
            '~$arithmetic_mixed_valid(S_entry, pintegeroperation[.SWAPPED = true])',
            '~$arithmetic_mixed_valid(S_entry, pintegeroperation[.LINE = 24])',
            '~$arithmetic_mixed_valid(S_entry, pintegeroperation[.LEFT = pintegeroperation.RIGHT])',
            '~$arithmetic_mixed_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
            '$arithmetic_cv_value(S_entry[.REFCELLS = eps], INTEGER_CELL n_left) = eps',
            '$arithmetic_cv_value(S_entry[.ALLOCATIONS = eps], INTEGER_CELL n_left) = eps',
            '$arithmetic_cv_value(S_entry[.STORE[n_left] = DEFINED PUNDEFINED], INTEGER_CELL n_left) = eps',
            '$arithmetic_cv_value(S_entry[.STORE[n_left] = DEFINED (PARRAY 0)], INTEGER_CELL n_left) = eps',
            '$arithmetic_cv_value(S_entry[.REFCELLS = [n_left, n_right]], INTEGER_CV ($ptascii("right"))) = eps',
            '$arithmetic_mixed_plan(S_entry[.REFCELLS = [n_left, n_right]]) = eps',
            '$arithmetic_cv_value(S_entry, INTEGER_CV ($ptascii("left"))) = eps',
            '$arithmetic_cv_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 2',
        ]
    else:
        result += [
            '$power_conversion_warning_plan(S_entry) = eps',
            '$lookup(S_throw.ENV, $ptascii("selectedAlias")) = (n_left)',
            '$arithmetic_cv_value(S_late, pintegeroperation.LEFTPOINTER) = (PINT 88)',
            '$arithmetic_cv_value(S_throw, pintegeroperation.LEFTPOINTER) = (PINT 77)',
        ]
    assert len(result) == len(set(result))
    return result


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(prior.__file__),
               Path(prior.prior.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
