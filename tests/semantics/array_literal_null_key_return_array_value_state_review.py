#!/usr/bin/env python3
"""Sole-owned returned arrays keep two pending NULL owners, then transfer or retire."""
import base64
import json

import array_literal_null_key_return_array_value_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as BASE_HELPERS, driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = BASE_HELPERS + r'''
def $list_warning_task(ARRAY_KEY_NULL_VALUE_RESULT n n_value phpType13* z) = true
def $list_warning_frontier(S, 20) = ($array_null_value_plan(S) =/= eps)
def $list_warning_frontier(S, 21) = true
  -- if S.TODO = (ARRAY_KEY_NULL_VALUE_RESULT n n_value phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 23) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_NULL_VALUE_RESULT n n_value phpType13* z
def $list_warning_frontier(S, 17) = $array_cv_review_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 24) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_NULL_VALUE_RESULT n n_value phpType13* z
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line = 16 if thrown else 14
    args = 'n_a, n_value, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_VALUE_RESULT n_a n_value phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 20, 'S') + [
        '$array_null_value_plan(S) = ((' + args + '))', f'z = {line}',
        'S.RESULT = KNOWN (PARRAY n_value)', 'n_a =/= n_value',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'S.CURRENT = eps', 'S.FRAMES = eps',
        '$array_null_key_plan(S) = eps', '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        'S.ORIGIN = (PORIGIN n_unit pcpath)',
        '$array_float_key_item(S, phpType13*, z) = ((expression, VARIABLE n_key_name* z_key))',
        'expression = NExprFuncCall name (SEQUENCE eps) metadata',
        '$code_at(S.CODE, n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS, pcpath ++ [PCFIELD 1]) = ((z, false))',
        '$code_name(pcode.NAMES, pcpath ++ [PCFIELD 1]) = ((n_name*, eps))',
        '$call_target(S, n_name*, eps) = (pfunction)',
        '~pfunction.SIGNATURE.BYREF', 'pfunction.SIGNATURE.PARAMETERS = eps',
        '$array_float_key_input_source(S, expression, KNOWN (PARRAY n_value))',
        '$array_null_value_source(S, ' + args + ')', '$array_null_value_ready(S, n_a, n_value)',
        '~$array_null_value_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_value_source(S[.CODE = eps], ' + args + ')',
        '~$array_null_value_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_null_value_source(S, n_a, n_value, phpType13*, $(z + 1))',
        '~$array_null_value_source(S, n_a, (|S.ARRAYS|), phpType13*, z)',
        '~$array_null_value_ready(S, n_a, n_a)',
        '$array_null_value_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$array_null_value_plan(S[.BASE = BASE_VALUE (KNOWN (PINT 0))]) = eps',
        '$lookup(S.ENV, $ptascii("made")) = (n_made)', 'S.STORE[n_made] = DEFINED (PINT 1)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$lookup(S.ENV, $ptascii("seed")) = (n_seed)', 'S.STORE[n_seed] = DEFINED (PINT 2)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED PNULL',
        '$array_null_value_plan(S[.STORE[n_key_cell] = DEFINED (PINT 9)]) = eps',
        pair('S', 'n_value', 2, 8),
        '$array_null_key_payload(S, PARRAY n_value, S.ALLOCATIONS)',
        '(HARRAY n_value) <- S.ALLOCATIONS', '~$array_immutable(S, n_value)',
        '$heap_count(HARRAY n_value, $pools_nodes(S.POOLS)) = 0',
        '$heap_count(HARRAY n_value, $machine_roots(S)) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_value) = 1',
        'S_alias = S[.REFCELLS = n_seed :: S.REFCELLS][.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed)]]',
        '$heap_valid($heap_graph(S_alias))',
        '~$array_null_value_ready(S_alias, n_a, n_value)',
        'S_deeper = S[.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_a))]]',
        '~$array_null_value_ready(S_deeper, n_a, n_value)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE z])',
        'S_dispatch.RESULT = KNOWN PNULL',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value, HARRAY n_value]',
        '$heap_count(HCELL n_seed, $task_nodes(' + marker + ')) = 0',
        '$heap_count(HARRAY n_value, $machine_roots(S_dispatch)) = 2',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 2',
        'S_debt = S_dispatch[.LITERALARRAYDEBTS = [n_value]]',
        '$heap_owners($heap_graph(S_debt), HARRAY n_value) = 1',
        '~$array_null_value_ready(S_debt, n_a, n_value)',
        '$call_descriptors_valid(S_dispatch)',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_value, $tasks_nodes(pframe.TODO)) = 2',
        '$heap_count(HCELL n_seed, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_owners($heap_graph(S_entered), HARRAY n_value) = 2',
        '$call_descriptors_valid(S_entered)',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KSTRING eps) (DIRECT (PINT 8))]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
            'S_object = S[.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_second))]]',
            '$array_null_value_source(S_object, ' + args + ')',
            '~$array_null_value_ready(S_object, n_a, n_value)',
            '$error_read_discard(S_object, ' + marker + ') = S_object[.COMPLETION = UNSUPPORTED "array literal null-key returned array during throw"]',
        ] + seek('S_entered', 24, 'S_discard') + [
            'S_discard.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_discard) :: ptask_pending*',
            'perrorcall_discard.RESUME = ' + marker,
            'S_discard.STORE[n_seed] = DEFINED (PINT 99)', 'S_discard.STORE[n_key_cell] = DEFINED (PINT 9)',
            '$heap_owners($heap_graph(S_discard), HARRAY n_value) = 2',
            '$entry_lookup(S_discard.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 8))',
            'S_popped = S_discard[.TODO = (THROW_SEARCH n_second) :: ptask_pending*]',
            '$heap_owners($heap_graph(S_popped), HARRAY n_value) = 0',
            '(HARRAY n_value) <- S_popped.ALLOCATIONS',
            '$array_null_value_source(S_popped, ' + args + ')', '$array_null_value_ready(S_popped, n_a, n_value)',
            '$error_read_discard(S_popped, ' + marker + ') = S_popped',
            'PhpStep: S_discard ~> S_released',
            'S_released.STORE = S_discard.STORE', '$heap_owners($heap_graph(S_released), HARRAY n_value) = 0',
        ] + driven('S_discard', 'S_released', 'S_release_driven') + seek('S_release_driven', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_after*',
            '$throwable_previous_id(S_start, n_second) = eps', 'S_start.ERRORHANDLER = S.ERRORHANDLER',
            'S_start.STORE[n_dest] = DEFINED (PINT 99)', 'S_start.STORE[n_later] = DEFINED (PINT 7)',
            'S_start.STORE[n_seed] = DEFINED (PINT 99)', 'S_start.STORE[n_made] = DEFINED (PINT 1)',
            'S_start.STORE[n_calls] = DEFINED (PINT 1)',
            '~((HARRAY n_a) <- S_start.ALLOCATIONS)', '~((HARRAY n_value) <- S_start.ALLOCATIONS)',
            '$call_descriptors_valid(S_start)', '$heap_valid($heap_graph(S_start))',
        ] + empty_biases('S_start')
    else:
        checks += [
            'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
            '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 7)',
        ] + seek('S_entered', 21, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*',
            '$array_null_value_source(S_resume, ' + args + ')', '$array_null_value_ready(S_resume, n_a, n_value)',
            '$array_null_value_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_null_value_ready(S_resume[.ENV = eps], n_a, n_value)',
            pair('S_resume', 'n_value', 2, 8),
            'S_resume.STORE[n_seed] = DEFINED (PINT 99)', 'S_resume.STORE[n_made] = DEFINED (PINT 1)',
            'S_resume.STORE[n_calls] = DEFINED (PINT 1)', 'S_resume.STORE[n_tail] = DEFINED (PINT 66)',
            '$heap_owners($heap_graph(S_resume), HARRAY n_value) = 2',
            '$error_read_discard(S_resume, ' + marker + ') = S_resume',
            'PhpStep: S_resume ~> S_insert',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
            'S_insert.RESULT = KNOWN PNULL', 'S_insert.STORE = S_resume.STORE',
            '$heap_count(HARRAY n_value, $machine_roots(S_insert)) = 0',
            '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 1',
        ] + empty_biases('S_resume') + empty_biases('S_insert') + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 17, 'S_copied') + [
            '$lookup(S_copied.ENV, $ptascii("a")) = (n_a_cell)', 'S_copied.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$lookup(S_copied.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_copied.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
            '$entry_lookup(S_copied.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
            '$entry_lookup(S_copied.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            'n_copy_value =/= n_value', pair('S_copied', 'n_value', 2, 8), pair('S_copied', 'n_copy_value', 66, 99),
            '$entry_lookup(S_copied.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
            '$entry_lookup(S_copied.ARRAYS[n_copy].ITEMS, KINT 4) = (DIRECT (PINT 66))',
            '$heap_owners($heap_graph(S_copied), HARRAY n_value) = 1',
            '$heap_owners($heap_graph(S_copied), HARRAY n_copy_value) = 1',
            '$call_descriptors_valid(S_copied)', '$heap_valid($heap_graph(S_copied))',
        ] + empty_biases('S_copied') + seek('S_copied', 15, 'S_start') + [
            '$lookup(S_start.ENV, $ptascii("copy")) = eps',
            '$lookup(S_start.ENV, $ptascii("a")) = (n_a_cell)', 'S_start.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            'S_start.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 4) (DIRECT (PINT 66))]',
            '~((HARRAY n_value) <- S_start.ALLOCATIONS)', '~((HARRAY n_copy) <- S_start.ALLOCATIONS)',
            '~((HARRAY n_copy_value) <- S_start.ALLOCATIONS)',
        ]
    checks += seek('S_start', 15, 'S_read') + [
        'S_read.CURRENT = eps', 'S_read.FRAMES = eps', 'S_read.GLOBALTABLE = eps',
        'S_read.STORE[n_seed] = DEFINED (PINT 99)', 'S_read.STORE[n_made] = DEFINED (PINT 1)',
        'S_read.STORE[n_calls] = DEFINED (PINT 1)', 'S_read.STORE[n_key_cell] = DEFINED (PINT 9)',
        '~((HARRAY n_value) <- S_read.ALLOCATIONS)',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
    ] + empty_biases('S_read')
    if thrown:
        checks += [
            'S_read.STORE[n_dest] = DEFINED (PINT 99)', 'S_read.STORE[n_later] = DEFINED (PINT 7)',
            '$lookup(S_read.ENV, $ptascii("e")) = eps', '~((HARRAY n_a) <- S_read.ALLOCATIONS)',
            '(HOBJECT n_second) <- S_read.ALLOCATIONS',
        ]
    checks += [
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split_found = $drive_steps(S_read, 1)', 'S_split_found.COMPLETION = BUDGET',
        'S_split = S_split_found[.COMPLETION = NORMAL]',
        'S_done = $drive_steps(S_split, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HARRAY n_value) <- S_done.ALLOCATIONS)', '~((HARRAY n_a) <- S_done.ALLOCATIONS)',
        '~((HCELL n_seed) <- S_done.ALLOCATIONS)', '~((HCELL n_made) <- S_done.ALLOCATIONS)',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_done')
    if thrown:
        checks.append('~((HOBJECT n_second) <- S_done.ALLOCATIONS)')
    else:
        checks += ['~((HARRAY n_copy) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy_value) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
