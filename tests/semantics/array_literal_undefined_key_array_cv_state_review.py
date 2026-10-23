#!/usr/bin/env python3
"""Stable ARRAY transfer and throw/inverse accounting preserve physical owners."""
import base64
import json

import array_literal_undefined_key_array_cv_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair
from array_literal_undefined_key_warning_state_review import HELPERS as BASE_HELPERS, expected_stderr

HELPERS = BASE_HELPERS + r'''
def $list_warning_task(ARRAY_KEY_UNDEFINED_ARRAY_RESULT n n_old poperand n_key* phpType13* z) = true
def $list_warning_frontier(S, 60) = ($array_undefined_array_key_plan(S) =/= eps)
def $list_warning_frontier(S, 61) = true
  -- if S.TODO = (ARRAY_KEY_UNDEFINED_ARRAY_RESULT n n_old poperand n_key* phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 63) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_ARRAY_RESULT n n_old poperand n_key* phpType13* z
def $list_warning_frontier(S, 64) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_ARRAY_RESULT n_a n_old poperand n_key* phpType13* z
def $list_warning_frontier(S, 65) = $array_cv_review_echo(S, $ptascii("S:"))
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('throw-inverse')
    line = 20 if thrown else 13
    key = 'throw_key' if thrown else 'missing'
    args = 'n_a, n_old, poperand, n_key_name*, phpType13*, z'
    marker = 'ARRAY_KEY_UNDEFINED_ARRAY_RESULT n_a n_old poperand n_key_name* phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 60, 'S') + [
        '$array_undefined_array_key_plan(S) = ((' + args + '))', f'z = {line}',
        f'n_key_name* = $ptascii("{key}")', f'z_key = {line - 2}',
        'poperand = VARIABLE ($ptascii("q")) z', 'S.RESULT = poperand',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'S.BASE = BASE_VALUE (KNOWN PNULL)', 'S.CURRENT = eps', 'S.FRAMES = eps',
        '$lookup(S.ENV, n_key_name*) = eps', '$array_undefined_key_missing(S, n_key_name*)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PARRAY n_old)', '~(n_q <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        pair('S', 'n_old', 2, 7), '$heap_count(HARRAY n_old, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$array_undefined_array_key_source(S, ' + args + ')', '$array_undefined_array_key_ready(S, n_a, n_old, poperand)',
        '$array_undefined_key_plan(S) = eps', '~$array_undefined_key_ready(S, n_a, poperand)',
        '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps', '$array_null_key_plan(S) = eps',
        '~$array_undefined_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_undefined_array_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_undefined_array_key_source(S, n_a, n_a, poperand, n_key_name*, phpType13*, z)',
        '~$array_undefined_array_key_source(S, n_a, (|S.ARRAYS|), poperand, n_key_name*, phpType13*, z)',
        '~$array_undefined_array_key_source(S, n_a, n_old, poperand, n_key_name*, phpType13*, z_key)',
        '$array_undefined_array_key_plan(S[.RESULT = KNOWN (PARRAY n_old)]) = eps',
        'S_ref = S[.REFCELLS = n_q :: S.REFCELLS]', '$heap_valid($heap_graph(S_ref))',
        '$array_float_array_key_item(S_ref, poperand) = (ALIAS n_q)',
        '~$array_undefined_array_key_ready(S_ref, n_a, n_old, poperand)',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_old]',
        '$heap_count(HCELL n_q, $task_nodes(' + marker + ')) = 0', '$heap_owners($heap_graph(S), HCELL n_q) = 1',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*', 'perrorcall.RESUME = ' + marker,
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = z', 'perrorcall.MESSAGE = $ptascii("Undefined variable $") ++ n_key_name*',
        'perrorcall.EVENT = WARNING n_key_name* z', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])', '~$error_call_valid(S_dispatch, perrorcall[.LINE = z_key])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.RESULT = KNOWN PNULL',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3', '$heap_owners($heap_graph(S_dispatch), HCELL n_q) = 1',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 63, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*', 'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_q, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_owners($heap_graph(S_entered), HARRAY n_old) = 3',
    ]
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("left")) = (n_left_cell)', 'S.STORE[n_left_cell] = DEFINED (PARRAY n_old)',
            '$lookup(S.ENV, $ptascii("right")) = (n_right_cell)', 'S.STORE[n_right_cell] = DEFINED (PARRAY n_new)',
            'S.STORE[n_held_cell] = DEFINED (PARRAY n_new)', 'n_new =/= n_old', pair('S', 'n_new', 20, 8),
            '$heap_owners($heap_graph(S), HARRAY n_new) = 2',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', '$lookup(S.ENV, $ptascii("later")) = (n_later)',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ] + seek('S_entered', 64, 'S_discard') + [
            'S_discard.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_discard) :: ptask_pending*',
            'perrorcall_discard.RESUME = ' + marker, 'S_discard.STORE[n_q] = DEFINED (PARRAY n_new)',
            'S_discard.STORE[n_dest] = DEFINED (PINT 99)', 'S_discard.STORE[n_later] = DEFINED (PINT 7)',
            '$array_undefined_array_key_source(S_discard, ' + args + ')',
            '$array_undefined_array_key_ready(S_discard, n_a, n_old, poperand)',
            '$heap_owners($heap_graph(S_discard), HARRAY n_new) = 3',
            '$entry_lookup(S_discard.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 8))',
            'S_popped = S_discard[.TODO = (THROW_SEARCH n_second) :: ptask_pending*]',
            '$heap_owners($heap_graph(S_popped), HARRAY n_old) = 1',
            '$heap_owners($heap_graph(S_popped), HARRAY n_a) = 0',
            'S_accounted = $error_read_discard(S_popped, ' + marker + ')',
            'S_accounted = S_popped[.LITERALARRAYRETAINED = [n_old]][.LITERALARRAYDEBTS = [n_new]]',
            '$heap_owners($heap_graph(S_accounted), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_accounted), HARRAY n_new) = 2',
            'PhpStep: S_discard ~> S_released', 'S_released.STORE = S_discard.STORE',
            'S_released.LITERALARRAYRETAINED = [n_old]', 'S_released.LITERALARRAYDEBTS = [n_new]',
        ] + driven('S_discard', 'S_released', 'S_release_driven') + seek('S_release_driven', 14, 'S_catch') + [
            '~((HARRAY n_a) <- S_catch.ALLOCATIONS)', 'S_catch.STORE[n_dest] = DEFINED (PINT 99)',
            'S_catch.STORE[n_later] = DEFINED (PINT 7)', '$throwable_previous_id(S_catch, n_second) = eps',
            '$heap_owners($heap_graph(S_catch), HARRAY n_new) = 2',
        ] + seek('S_catch', 65, 'S_shared') + [
            'S_shared.STORE[n_q] = DEFINED (PINT 0)',
            'S_shared.STORE[n_right_cell] = DEFINED (PARRAY n_new)', 'S_shared.STORE[n_held_cell] = DEFINED (PARRAY n_new)',
            pair('S_shared', 'n_new', 55, 8), '$heap_owners($heap_graph(S_shared), HARRAY n_new) = 1',
            'S_shared.LITERALARRAYRETAINED = [n_old]', 'S_shared.LITERALARRAYDEBTS = [n_new]',
            '$heap_valid($heap_graph(S_shared))',
        ] + seek('S_shared', 60, 'S_inverse') + [
            '$array_undefined_array_key_plan(S_inverse) = ((n_b, n_new, poperand_inverse, n_key_inverse*, phpType13_inverse*, z_inverse))',
            'n_key_inverse* = $ptascii("inverse_key")', 'z_inverse = 32', 'n_b =/= n_a',
            '$heap_owners($heap_graph(S_inverse), HARRAY n_new) = 2',
        ] + seek('S_inverse', 61, 'S_inverse_resume') + [
            'S_inverse_resume.TODO = (ARRAY_KEY_UNDEFINED_ARRAY_RESULT n_b n_new poperand_inverse n_key_inverse* phpType13_inverse* z_inverse) :: ptask_inverse*',
            'S_inverse_resume.STORE[n_q] = DEFINED (PARRAY n_old)',
            'S_inverse_resume.LITERALARRAYRETAINED = [n_old]', 'S_inverse_resume.LITERALARRAYDEBTS = [n_new]',
            '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_new) = 2',
            '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_old) = 3',
            'PhpStep: S_inverse_resume ~> S_inverse_insert',
            '$entry_lookup(S_inverse_insert.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_old))',
            'S_inverse_insert.LITERALARRAYRETAINED = eps', 'S_inverse_insert.LITERALARRAYDEBTS = eps',
            '$heap_owners($heap_graph(S_inverse_insert), HARRAY n_new) = 2',
            '$heap_owners($heap_graph(S_inverse_insert), HARRAY n_old) = 3',
        ] + driven('S_inverse_resume', 'S_inverse_insert', 'S_inverse_driven') + seek('S_inverse_driven', 15, 'S_read') + [
            'S_read.STORE[n_q] = DEFINED (PARRAY n_old)', 'S_read.STORE[n_left_cell] = DEFINED (PARRAY n_old)',
            'S_read.STORE[n_right_cell] = DEFINED (PARRAY n_right_copy)', 'n_right_copy =/= n_new',
            '$lookup(S_read.ENV, $ptascii("b")) = (n_b_cell)', 'S_read.STORE[n_b_cell] = DEFINED (PARRAY n_b)',
            '$entry_lookup(S_read.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_b_copy))', 'n_b_copy =/= n_old',
            pair('S_read', 'n_old', 2, 7), pair('S_read', 'n_new', 55, 8),
            pair('S_read', 'n_right_copy', 66, 8), pair('S_read', 'n_b_copy', 2, 88),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2', '$heap_owners($heap_graph(S_read), HARRAY n_new) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_right_copy) = 1', '$heap_owners($heap_graph(S_read), HARRAY n_b_copy) = 1',
        ]
        retired = ['n_a', 'n_b', 'n_old', 'n_new', 'n_right_copy', 'n_b_copy']
    else:
        checks += ['S.STORE[n_held_cell] = DEFINED (PARRAY n_old)'] + seek('S_entered', 61, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*',
            'S_resume.STORE[n_q] = DEFINED (PARRAY n_old)',
            'S_resume.STORE[n_held_cell] = DEFINED (PARRAY n_held)', 'n_held =/= n_old',
            pair('S_resume', 'n_old', 2, 7), pair('S_resume', 'n_held', 44, 7),
            '$heap_owners($heap_graph(S_resume), HARRAY n_old) = 2',
            '$array_undefined_array_key_source(S_resume, ' + args + ')',
            '$array_undefined_array_key_ready(S_resume, n_a, n_old, poperand)',
            '$array_float_array_key_retain(S_resume, n_old, poperand) = S_resume',
            '$error_read_discard(S_resume, ' + marker + ') = S_resume',
            '$array_undefined_review_warnings(S_resume.EVENTS, n_key_name*, z) = 1',
            'PhpStep: S_resume ~> S_insert',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_old))',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
            'S_insert.STORE = S_resume.STORE', '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
        ] + empty_biases('S_insert') + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_old))',
            'S_read.STORE[n_q] = DEFINED (PARRAY n_q_copy)', 'n_q_copy =/= n_old',
            pair('S_read', 'n_old', 55, 7), pair('S_read', 'n_q_copy', 2, 77), pair('S_read', 'n_held', 44, 7),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_q_copy) = 1', '$heap_owners($heap_graph(S_read), HARRAY n_held) = 1',
            '$array_undefined_review_warnings(S_read.EVENTS, n_key_name*, z) = 1',
        ]
        retired = ['n_a', 'n_old', 'n_q_copy', 'n_held']
    checks += [
        '$array_undefined_review_deprecations(S_read.EVENTS) = 0', '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
    ] + empty_biases('S_read') + empty_biases('S_done')
    checks += [f'~((HARRAY {array}) <- S_done.ALLOCATIONS)' for array in retired]
    if thrown:
        checks.append('~((HOBJECT n_second) <- S_done.ALLOCATIONS)')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr) else 1)
