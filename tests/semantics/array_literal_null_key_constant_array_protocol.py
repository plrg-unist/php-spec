#!/usr/bin/env python3
"""Constant literal pools survive repeated invocation and empty-array COW."""
import base64
import json

import array_literal_null_key_constant_array_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as BASE_HELPERS, driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = BASE_HELPERS + r'''
def $list_warning_task(ARRAY_KEY_NULL_CONST_RESULT n n_value phpType13* z) = true
def $list_warning_frontier(S, 20) = ($array_null_const_plan(S) =/= eps)
def $list_warning_frontier(S, 21) = true
  -- if S.TODO = (ARRAY_KEY_NULL_CONST_RESULT n n_value phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 23) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_NULL_CONST_RESULT n n_value phpType13* z
def $list_warning_frontier(S, 25) = $array_cv_review_echo(S, $ptascii("A:"))
'''


def conditions(name, program, path, stdout):
    repeated = name.endswith('repeated')
    args = 'n_a, n_value, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_CONST_RESULT n_a n_value phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 20, 'S') + [
        '$array_null_const_plan(S) = ((' + args + '))', f'z = {5 if repeated else 9}',
        'S.RESULT = KNOWN (PARRAY n_value)', 'n_a =/= n_value',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE ($ptascii("key")) z_key) phpType13* z) :: ptask_tail*',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        'S.STORE[n_key] = DEFINED PNULL', '~(n_key <- S.REFCELLS)',
        'S.ORIGIN = (PORIGIN n_unit pcpath)',
        '$array_float_key_item(S, phpType13*, z) = ((expression, VARIABLE ($ptascii("key")) z_key))',
        'expression = NExprArray (SEQUENCE phpType13_value*) metadata',
        f'$expression_line(expression) = {6 if repeated else 10}',
        '$code_at(S.CODE, n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS, pcpath ++ [PCFIELD 1]) = ((z, true))',
        '$compiled_read(S, PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PARRAY n_value)',
        '$array_null_const_source(S, ' + args + ')', '$array_null_const_ready(S, n_a, n_value)',
        '$array_null_key_plan(S) = eps', '$array_null_value_plan(S) = eps', '$array_null_tmp_plan(S) = eps',
        '~$array_float_key_input_source(S, expression, S.RESULT)',
        '$array_null_const_plan(S[.STORE[n_key] = DEFINED (PINT 9)]) = eps',
        '$array_null_const_plan(S[.STORE[n_key] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        '$array_null_const_plan(S[.REFCELLS = n_key :: S.REFCELLS]) = eps',
        '$array_null_const_plan(S[.RESULT = VARIABLE ($ptascii("key")) z_key]) = eps',
        '~$array_null_const_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_const_source(S, n_a, n_value, eps, z)',
        '~$array_null_const_source(S, n_a, n_a, phpType13*, z)',
        '~$array_null_const_source(S, n_a, n_value, phpType13*, $(z + 1))',
        'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$heap_count(HARRAY n_value, $pools_nodes(S.POOLS)) = 1',
        '$heap_count(HARRAY n_value, $machine_roots(S)) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_value) = 2',
        '$entries_nodes(S.ARRAYS[n_value].ITEMS) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    checks += [pair('S', 'n_value', 2, 7)] if repeated else ['S.ARRAYS[n_value].ITEMS = eps']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.SITE = PORIGIN n_unit eps])',
        '~$call_task_valid(S_dispatch, ARRAY_KEY_NULL_CONST_RESULT n_a n_value phpType13* $(z + 1))',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        '$heap_count(HCELL n_key, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 2',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_value, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_owners($heap_graph(S_entered), HARRAY n_value) = 2',
    ] + seek('S_entered', 21, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$array_null_const_source(S_resume, ' + args + ')', '$array_null_const_ready(S_resume, n_a, n_value)',
        'S_resume.ARRAYS[n_value] = S.ARRAYS[n_value]',
        '$heap_owners($heap_graph(S_resume), HARRAY n_value) = 2',
        '$error_read_discard(S_resume, ' + marker + ') = S_resume',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.STORE = S_resume.STORE', 'S_insert.ARRAYS[n_value] = S_resume.ARRAYS[n_value]',
        '$heap_count(HARRAY n_value, $machine_roots(S_insert)) = 1',
        '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 2',
    ] + empty_biases('S_insert') + driven('S_resume', 'S_insert', 'S_insert_driven')
    if repeated:
        checks += [
            'S.CURRENT = (pcallcontext)', 'S.FRAMES = pframe_main :: eps',
            'S_resume.STORE[n_key] = DEFINED PNULL',
        ] + seek('S_insert_driven', 25, 'S_first') + [
            'S_first.CURRENT = eps', 'S_first.FRAMES = eps',
            '$lookup(S_first.ENV, $ptascii("a")) = (n_a_cell)', 'S_first.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$entry_lookup(S_first.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_first))',
            'n_first =/= n_value', pair('S_first', 'n_first', 55, 7),
            '$lookup(S_first.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_first.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_first.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            'n_copy_value =/= n_first', pair('S_first', 'n_copy_value', 55, 77),
            '$heap_owners($heap_graph(S_first), HARRAY n_value) = 1',
            '$lookup(S_first.ENV, $ptascii("calls")) = (n_calls)', 'S_first.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_first.ENV, $ptascii("produced")) = (n_produced)', 'S_first.STORE[n_produced] = DEFINED (PINT 1)',
        ] + seek('S_first', 20, 'S_second') + [
            '$array_null_const_plan(S_second) = ((n_b, n_value, phpType13*, z))', 'n_b =/= n_a',
            'S_second.ORIGIN = S.ORIGIN', 'S_second.POOLS = S.POOLS',
            '$compiled_read(S_second, PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PARRAY n_value)',
            pair('S_second', 'n_value', 2, 7),
            '$heap_owners($heap_graph(S_second), HARRAY n_value) = 2',
            'S_second.STORE[n_calls] = DEFINED (PINT 1)', 'S_second.STORE[n_produced] = DEFINED (PINT 2)',
        ] + seek('S_second', 16, 'S_before_write') + [
            '$lookup(S_before_write.ENV, $ptascii("b")) = (n_b_cell)', 'S_before_write.STORE[n_b_cell] = DEFINED (PARRAY n_b)',
            '$entry_lookup(S_before_write.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
            pair('S_before_write', 'n_value', 2, 7),
            '$heap_owners($heap_graph(S_before_write), HARRAY n_value) = 2',
            'S_before_write.STORE[n_calls] = DEFINED (PINT 2)', 'S_before_write.STORE[n_produced] = DEFINED (PINT 2)',
        ] + seek('S_before_write', 15, 'S_read') + [
            '$entry_lookup(S_read.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_last))',
            'n_last =/= n_value', pair('S_read', 'n_last', 2, 88),
            pair('S_read', 'n_first', 55, 7), pair('S_read', 'n_copy_value', 55, 77),
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 4) = (DIRECT (PINT 66))',
            '$entry_lookup(S_read.ARRAYS[n_b].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        ]
    else:
        checks += [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S_resume.STORE[n_key] = DEFINED (PINT 9)',
        ] + seek('S_insert_driven', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_first))',
            'n_first =/= n_value', 'S_read.ARRAYS[n_first].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 66))]',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            'n_copy_value =/= n_value', 'n_copy_value =/= n_first',
            'S_read.ARRAYS[n_copy_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 55))]',
            '$lookup(S_read.ENV, $ptascii("empty")) = (n_empty_cell)', 'S_read.STORE[n_empty_cell] = DEFINED (PARRAY n_empty)',
            'S_read.ARRAYS[n_empty].ITEMS = eps',
            'S_read.ARRAYS[n_value].ITEMS = eps',
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 4) = (DIRECT (PINT 77))',
        ]
    checks += [
        'S_read.ARRAYS[n_value] = S.ARRAYS[n_value]',
        '$heap_owners($heap_graph(S_read), HARRAY n_value) = 1',
        '$heap_count(HARRAY n_value, $pools_nodes(S_read.POOLS)) = 1',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.ARRAYS[n_value] = S.ARRAYS[n_value]', '(HARRAY n_value) <- S_done.ALLOCATIONS',
        '$heap_owners($heap_graph(S_done), HARRAY n_value) = 1',
        '$heap_count(HARRAY n_value, $pools_nodes(S_done.POOLS)) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_done')
    for array in ('n_a', 'n_first', 'n_copy', 'n_copy_value', *(('n_b', 'n_last') if repeated else ())):
        checks.append(f'~((HARRAY {array}) <- S_done.ALLOCATIONS)')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
