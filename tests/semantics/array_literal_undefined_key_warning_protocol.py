#!/usr/bin/env python3
"""Undefined-key Warning keeps live values and stays distinct from NULL reset."""
import base64
import json

import array_literal_undefined_key_warning_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as BASE_HELPERS, driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases

HELPERS = BASE_HELPERS + r'''
def $list_warning_task(ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z) = true
def $list_warning_frontier(S, 40) = ($array_undefined_key_plan(S) =/= eps)
def $list_warning_frontier(S, 41) = true
  -- if S.TODO = (ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 43) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z
def $list_warning_frontier(S, 44) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 45) = ($array_null_key_plan(S) =/= eps)
def $list_warning_frontier(S, 46) = true
  -- if S.TODO = (ARRAY_KEY_NULL_RESULT n n_capture poperand pvalue phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 47) = $array_cv_review_echo(S, $ptascii("A:"))
'''


def conditions(name, program, path, stdout):
    mixed = name.endswith('then-null')
    args = 'n_a, poperand, n_key_name*, phpType13*, z'
    marker = 'ARRAY_KEY_UNDEFINED_RESULT n_a poperand n_key_name* phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 40, 'S') + [
        '$array_undefined_key_plan(S) = ((' + args + '))', f'z = {16 if mixed else 12}',
        'n_key_name* = $ptascii("key")',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'z_key = $(z - 1)', 'S.RESULT = poperand', 'poperand = VARIABLE ($ptascii("q")) z',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$lookup(S.ENV, n_key_name*) = eps', '$array_undefined_key_missing(S, n_key_name*)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S), HCELL n_q) = 1',
        '$array_undefined_key_value(S, poperand) = (PINT 2)',
        '$array_undefined_key_source(S, ' + args + ')', '$array_undefined_key_ready(S, n_a, poperand)',
        '$array_null_key_plan(S) = eps', '$array_float_key_plan(S) = eps',
        '~$array_undefined_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_undefined_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_undefined_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_undefined_key_source(S, n_a, poperand, $ptascii("other"), phpType13*, z)',
        '~$array_undefined_key_source(S, n_a, poperand, n_key_name*, phpType13*, z_key)',
        '~$array_undefined_key_source(S, n_a, KNOWN (PINT 2), n_key_name*, phpType13*, z)',
        '~$array_undefined_key_ready(S, (|S.ARRAYS|), poperand)',
        'S_bound = $ensure(S, n_key_name*)', '$lookup(S_bound.ENV, n_key_name*) = (n_key_cell)',
        'S_bound.STORE[n_key_cell] = UNDEFINED', '$array_undefined_key_plan(S_bound) = ((' + args + '))',
        '~$array_undefined_key_missing(S_bound[.STORE[n_key_cell] = DEFINED PNULL], n_key_name*)',
        '~$array_undefined_key_missing(S_bound[.ALLOCATIONS = eps], n_key_name*)',
        '$array_undefined_key_plan(S_bound[.STORE[n_key_cell] = DEFINED (PINT 9)]) = eps',
        'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $key")', 'perrorcall.EVENT = WARNING n_key_name* z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = z_key])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE z])',
        '$task_nodes(' + marker + ') = [HARRAY n_a]',
        '$heap_count(HCELL n_q, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_q) = 1',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ] + driven('S', 'S_dispatch', 'S_driven') + seek('S_driven', 43, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_q, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_owners($heap_graph(S_entered), HCELL n_q) = 1',
    ] + seek('S_entered', 41, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$lookup(S_resume.ENV, n_key_name*) = (n_key)',
        'S_resume.STORE[n_key] = DEFINED ' + ('PNULL' if mixed else '(PINT 9)'),
        '~$array_undefined_key_missing(S_resume, n_key_name*)',
        '$array_undefined_key_source(S_resume, ' + args + ')', '$array_undefined_key_ready(S_resume, n_a, poperand)',
        '$array_undefined_key_value(S_resume, poperand) = (PINT 44)', 'S_resume.STORE[n_q] = DEFINED (PINT 44)',
        '$heap_owners($heap_graph(S_resume), HCELL n_q) = 1',
        '$error_read_discard(S_resume, ' + marker + ') = S_resume',
        'S_array_new = $allocate_array(S_resume, $array_empty())',
        'S_array_new.RESULT = KNOWN (PARRAY n_callback_array)',
        'S_array = S_array_new[.STORE[n_q] = DEFINED (PARRAY n_callback_array)][.RESULT = KNOWN PNULL]',
        '$heap_valid($heap_graph(S_array))', '$call_descriptors_valid(S_array)',
        '$array_float_key_live_value(S_array, poperand) = (PARRAY n_callback_array)',
        '~$array_undefined_key_ready(S_array, n_a, poperand)',
        '$error_read_discard(S_array, ' + marker + ') = S_array[.COMPLETION = UNSUPPORTED "array literal undefined-key value during throw"]',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 44))',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
    ] + driven('S_resume', 'S_insert', 'S_insert_driven')
    if mixed:
        checks += seek('S_insert_driven', 47, 'S_first') + [
            'S_first.STORE[n_q] = DEFINED (PINT 44)', 'S_first.STORE[n_key] = DEFINED PNULL',
        ] + seek('S_first', 45, 'S_null') + [
            '$array_null_key_plan(S_null) = ((n_b, n_q, poperand_null, PINT 44, eps, z_null))',
            'z_null = 22', 'poperand_null = VARIABLE ($ptascii("q")) z_null',
            '$array_undefined_key_plan(S_null) = eps',
        ] + seek('S_null', 46, 'S_null_resume') + [
            'S_null_resume.TODO = (ARRAY_KEY_NULL_RESULT n_b n_q poperand_null (PINT 44) eps z_null) :: ptask_null*',
            'S_null_resume.STORE[n_q] = DEFINED (PINT 55)',
            'PhpStep: S_null_resume ~> S_null_insert',
            'S_null_insert.STORE[n_q] = DEFINED (PINT 44)',
            '$entry_lookup(S_null_insert.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PINT 44))',
        ] + driven('S_null_resume', 'S_null_insert', 'S_null_driven') + seek('S_null_driven', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("warnings")) = (n_warnings)', 'S_read.STORE[n_warnings] = DEFINED (PINT 1)',
            '$lookup(S_read.ENV, $ptascii("deprecated")) = (n_deprecated)', 'S_read.STORE[n_deprecated] = DEFINED (PINT 1)',
        ]
        retired = ('n_a', 'n_b')
    else:
        checks += seek('S_insert_driven', 15, 'S_read') + [
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 9) = (DIRECT (PINT 66))',
        ]
        retired = ('n_a',)
    checks += [
        'S_read.STORE[n_q] = DEFINED (PINT 44)', 'S_read.STORE[n_key] = DEFINED (PINT 9)',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_done')
    checks += [f'~((HARRAY {array}) <- S_done.ALLOCATIONS)' for array in retired]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
