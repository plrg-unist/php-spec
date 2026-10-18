#!/usr/bin/env python3
"""Reached quiet MUL source authority and raw versus driven TypeError."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import quiet_multiply_cases as cases
import arithmetic_warning_protocol as shared

CASES = ('quiet-multiply-return-cv',)
HELPERS = r'''
dec $quiet_multiply_frontier(pstate) : bool
def $quiet_multiply_frontier(S) = true
  -- if S.TODO = (BINARY_RIGHT MULTIPLY poperand_left z) :: ptask_tail*
  -- if poperand_right = S.RESULT
  -- if $integer_pointer_select(S, poperand_left) = (pintegerpointer_left)
  -- if $integer_pointer_select(S, poperand_right) = (pintegerpointer_right)
  -- if $integer_pointer_value(S, pintegerpointer_left) = (pvalue_left)
  -- if $integer_pointer_value(S, pintegerpointer_right) = (pvalue_right)
  -- if $quiet_multiply_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z)
def $quiet_multiply_frontier(S) = false -- otherwise
dec $quiet_multiply_seek(pstate, nat) : pstate
def $quiet_multiply_seek(S, n) = S -- if $quiet_multiply_frontier(S)
def $quiet_multiply_seek(S, n) = S
  -- if ~$quiet_multiply_frontier(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_multiply_seek(S, 0) = S
  -- if ~$quiet_multiply_frontier(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_multiply_seek(S, n) = $quiet_multiply_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$quiet_multiply_frontier(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $quiet_multiply_output(pevent) : bool
def $quiet_multiply_output(OUTPUT n*) = true
def $quiet_multiply_output(pevent) = false -- otherwise
dec $quiet_multiply_outputs(pevent*) : ptbytes
def $quiet_multiply_outputs(eps) = eps
def $quiet_multiply_outputs((OUTPUT n*) :: pevent_tail*) = n* ++ $quiet_multiply_outputs(pevent_tail*)
def $quiet_multiply_outputs(pevent :: pevent_tail*) = $quiet_multiply_outputs(pevent_tail*) -- if ~$quiet_multiply_output(pevent)
'''


def conditions(name, program, path, stdout):
    message = '$ptascii("Unsupported operand types: int * string")'
    invoke = '$quiet_multiply_error(S_entry, poperand_left, poperand_right, pvalue_left, pvalue_right, 25)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $quiet_multiply_seek(S_initial, 5000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$quiet_multiply_frontier(S_entry)',
        'S_entry.TODO = (BINARY_RIGHT MULTIPLY poperand_left 25) :: ptask_tail*',
        'S_entry.RESULT = poperand_right', 'S_entry.ORIGIN = (porigin)',
        'poperand_left = KNOWN pvalue_left', 'poperand_right = VARIABLE ($ptascii("right")) 25',
        '$integer_slot_rank(S_entry, porigin, [PCFIELD 0], poperand_left) = (4)',
        '$integer_slot_rank(S_entry, porigin, [PCFIELD 1], poperand_right) = (8)',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 0], poperand_left)',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 1], poperand_right)',
        '$operand_nodes(poperand_left) = eps', '$operand_nodes(poperand_right) = eps',
        '$integer_pointer_select(S_entry, poperand_left) = (INTEGER_COPY pvalue_left)',
        '$integer_pointer_select(S_entry, poperand_right) = (INTEGER_CV ($ptascii("right")))',
        '$string_bytes(pvalue_left) = ($ptascii("bad5"))',
        '$string_carrier_valid(S_entry, pvalue_left)', '$string_plain(pvalue_left) =/= pvalue_left',
        'pvalue_right = PINT 3', '$coerce_number(pvalue_left) = BADNUMBER',
        '$coerce_number(pvalue_right) = COERCED (NINT 3) false', invoke,
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("evaluations")) = (n_evaluations)',
        'S_entry.STORE[n_right] = DEFINED pvalue_right',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_evaluations] = DEFINED (PINT 1)',
        'S_entry.FRAMES = eps', 'S_entry.CURRENT = eps', 'S_entry.HELD = eps',
        '$quiet_multiply_outputs(S_entry.EVENTS) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '~' + invoke.replace('S_entry,', 'S_entry[.ORIGIN = eps],', 1),
        '~' + invoke.replace('S_entry,', 'S_entry[.CODE = eps],', 1),
        '~' + invoke.replace('S_entry,', 'S_entry[.STRINGDATA = eps],', 1),
        '~' + invoke.replace('S_entry,', 'S_entry[.ENV = eps],', 1),
        '~' + invoke.replace('S_entry,', 'S_entry[.STORE[n_right] = UNDEFINED],', 1),
        '~' + invoke.replace(', 25)', ', 26)'),
        '~' + invoke.replace('poperand_right, pvalue_left', 'VARIABLE ($ptascii("missing")) 25, pvalue_left'),
        '~' + invoke.replace('poperand_left, poperand_right, pvalue_left, pvalue_right', 'poperand_right, poperand_left, pvalue_right, pvalue_left'),
        '~' + invoke.replace('pvalue_left, pvalue_right, 25)', 'pvalue_left, PINT 4, 25)'),
        '~$quiet_multiply_error(S_entry, KNOWN (PINT 2), poperand_right, PINT 2, pvalue_right, 25)',
        '~$quiet_multiply_error(S_entry, KNOWN (PSTRING ($ptascii("12tail"))), poperand_right, PSTRING ($ptascii("12tail")), pvalue_right, 25)',
        '$quiet_multiply_scalar(S_entry, PNULL)', '$quiet_multiply_scalar(S_entry, PBOOL false)',
        '$quiet_multiply_scalar(S_entry, PINT 3)', '$quiet_multiply_scalar(S_entry, PFLOAT 4612811918334230528)',
        '~$quiet_multiply_scalar(S_entry, PUNDEFINED)', '~$quiet_multiply_scalar(S_entry, PARRAY 0)',
        '~$quiet_multiply_scalar(S_entry, POBJECT 0)', '~$quiet_multiply_scalar(S_entry, PINT 9223372036854775808)',
        '~$quiet_multiply_scalar(S_entry, PFLOAT 18446744073709551616)',
        '~$quiet_multiply_scalar(S_entry, PSTRING ($ptascii("5tail")))',
        '$integer_operator_plan(S_entry) = eps', '$arithmetic_add_plan(S_entry) = eps',
        '$arithmetic_div_plan(S_entry) = eps', '$submul_warning_plan(S_entry) = eps',
        '$power_conversion_warning_plan(S_entry) = eps', '$arithmetic_cv_plan(S_entry) = eps',
        '$arithmetic_mixed_plan(S_entry) = eps', '$arithmetic_copy_plan(S_entry) = eps',
        '$arithmetic_owned_plan(S_entry) = eps', '$power_warning_plan(S_entry) = eps',
        'PhpStep: S_entry ~> S_raw',
        'S_raw = S_entry[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_right][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = THROWN "TypeError" (' + message + ') 25]',
        'S_error_budget = $drive_steps(S_entry, 1)', 'S_error_budget.COMPLETION = BUDGET',
        'S_error = S_error_budget[.COMPLETION = NORMAL]',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_error.RESULT = KNOWN PNULL',
        'n_error = |S_entry.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_error.OBJECTS = S_entry.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (porigin)',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = (' + message + ')',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_entry.STORE', 'S_error.ENV = S_entry.ENV',
        'S_error.REFCELLS = S_entry.REFCELLS', 'S_error.EVENTS = S_entry.EVENTS',
        'S_error.STRINGDATA = S_entry.STRINGDATA',
        'S_error.ARRAYS[0:|S_entry.ARRAYS|] = S_entry.ARRAYS',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 5000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)',
        'S_done.STORE[n_done_v] = DEFINED (PINT 7)',
        'S_done.STORE[n_calls] = DEFINED (PINT 0)', 'S_done.STORE[n_evaluations] = DEFINED (PINT 1)',
        '$quiet_multiply_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]', '$drive_steps(S_entry, 7000) = S_done',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
