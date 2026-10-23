#!/usr/bin/env python3
"""Owned ARRAY acquisition and retarget debt balance across key diagnostics."""
import base64
import json

import array_literal_undefined_key_array_cv_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as BASE_HELPERS, driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = BASE_HELPERS + r'''
def $list_warning_task(ARRAY_KEY_UNDEFINED_ARRAY_RESULT n n_old poperand n_key* phpType13* z) = true
def $list_warning_frontier(S, 40) = ($array_undefined_array_key_plan(S) =/= eps)
def $list_warning_frontier(S, 41) = true
  -- if S.TODO = (ARRAY_KEY_UNDEFINED_ARRAY_RESULT n n_old poperand n_key* phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 43) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_ARRAY_RESULT n n_old poperand n_key* phpType13* z
def $list_warning_frontier(S, 45) = ($array_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 46) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) :: ptask_tail*
'''


def biases(state, retained, debts):
    return [f'{state}.LITERALREFRETAINED = eps', f'{state}.LITERALREFDEBTS = eps',
            f'{state}.LITERALARRAYRETAINED = {retained}', f'{state}.LITERALARRAYDEBTS = {debts}']


def conditions(name, program, path, stdout):
    scalar = name.endswith('scalar-inverse')
    args = 'n_a, n_old, poperand, n_key_name*, phpType13*, z'
    marker = 'ARRAY_KEY_UNDEFINED_ARRAY_RESULT n_a n_old poperand n_key_name* phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 40, 'S') + [
        '$array_undefined_array_key_plan(S) = ((' + args + '))', f'z = {16 if scalar else 18}',
        'poperand = VARIABLE ($ptascii("q")) z', 'S.RESULT = poperand',
        f'n_key_name* = $ptascii("{"missing" if scalar else "first_key"}")',
        '$lookup(S.ENV, n_key_name*) = eps',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PARRAY n_old)',
        '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_hold =/= n_q',
        'S.STORE[n_hold] = DEFINED (PARRAY n_old)', pair('S', 'n_old', 2, 7),
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S), HCELL n_q) = 1',
        '$array_undefined_array_key_source(S, ' + args + ')',
        '$array_undefined_array_key_ready(S, n_a, n_old, poperand)',
        '$array_undefined_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        '$heap_count(HARRAY n_old, $pools_nodes(S.POOLS)) = 0',
        '~$array_undefined_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_undefined_array_key_source(S, n_a, n_a, poperand, n_key_name*, phpType13*, z)',
        '~$array_undefined_array_key_source(S, n_a, (|S.ARRAYS|), poperand, n_key_name*, phpType13*, z)',
        '$array_undefined_array_key_plan(S[.STORE[n_q] = DEFINED (PINT 2)]) = eps',
        '$array_undefined_array_key_plan(S[.REFCELLS = n_q :: S.REFCELLS]) = eps',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        'perrorcall.EVENT = WARNING n_key_name* z', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_old]',
        '$heap_count(HCELL n_q, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_driven') + seek('S_driven', 43, 'S_entered') + [
        '$heap_owners($heap_graph(S_entered), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_entered), HCELL n_q) = 1',
    ] + seek('S_entered', 41, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$array_undefined_array_key_source(S_resume, ' + args + ')',
        '$array_undefined_array_key_ready(S_resume, n_a, n_old, poperand)',
        '$lookup(S_resume.ENV, n_key_name*) = (n_key)', 'S_resume.STORE[n_key] = DEFINED (PINT 9)',
        '~$array_undefined_key_missing(S_resume, n_key_name*)',
        '$heap_owners($heap_graph(S_resume), HARRAY n_old) = 2',
        'S_marked = S_resume[.REFCELLS = n_q :: S_resume.REFCELLS]',
        '$array_undefined_array_key_source(S_marked, ' + args + ')',
        '~$array_undefined_array_key_ready(S_marked, n_a, n_old, poperand)',
        '$heap_valid($heap_graph(S_marked))', '$call_descriptors_valid(S_marked)',
        '$error_read_discard(S_marked, ' + marker + ').COMPLETION = UNSUPPORTED "array literal undefined-key array CV during throw"',
        'PhpStep: S_marked ~> S_refused',
        'S_refused.COMPLETION = UNSUPPORTED "array literal undefined-key array CV after callback"',
        'S_refused.TODO = eps', 'S_refused.STORE = S_marked.STORE',
    ]
    if scalar:
        checks += ['S_resume.STORE[n_q] = DEFINED (PINT 44)']
    else:
        checks += [
            'S_resume.STORE[n_q] = DEFINED (PARRAY n_new)', 'n_new =/= n_old', pair('S_resume', 'n_new', 44, 7),
            '$lookup(S_resume.ENV, $ptascii("new_hold")) = (n_new_hold)',
            'S_resume.STORE[n_new_hold] = DEFINED (PARRAY n_new)',
            '$heap_owners($heap_graph(S_resume), HARRAY n_new) = 2',
        ]
    checks += [
        'PhpStep: S_resume ~> S_insert', 'S_insert.STORE = S_resume.STORE',
        '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
        '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
        '$call_descriptors_valid(S_insert)', '$heap_valid($heap_graph(S_insert))',
    ] + biases('S_insert', '[n_old]', 'eps' if scalar else '[n_new]') + driven('S_resume', 'S_insert', 'S_insert_driven')
    if scalar:
        checks += [
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 44))',
        ] + seek('S_insert_driven', 45, 'S_inverse') + [
            '$array_float_key_plan(S_inverse) = ((n_b, poperand_inverse, eps, z_inverse, 4609434218613702656, 1))',
            'z_inverse = 23', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
            'S_inverse.STORE[n_q] = DEFINED (PINT 44)',
        ] + seek('S_inverse', 46, 'S_inverse_resume') + [
            'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_RESULT n_b poperand_inverse eps z_inverse 4609434218613702656 1) :: ptask_inverse*',
            'S_inverse_resume.STORE[n_q] = DEFINED (PARRAY n_old)',
        ] + biases('S_inverse_resume', '[n_old]', 'eps') + [
            'PhpStep: S_inverse_resume ~> S_inverse_insert',
            '$entry_lookup(S_inverse_insert.ARRAYS[n_b].ITEMS, KINT 1) = (DIRECT (PARRAY n_old))',
        ]
        start = 'S_inverse_insert'
        retired = ['n_a', 'n_b', 'n_old']
    else:
        checks += [
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_new))',
            '$heap_owners($heap_graph(S_insert), HARRAY n_new) = 2',
        ] + seek('S_insert_driven', 40, 'S_inverse') + [
            '$array_undefined_array_key_plan(S_inverse) = ((n_b, n_new, poperand_inverse, n_inverse_key*, eps, z_inverse))',
            'z_inverse = 25', 'n_inverse_key* = $ptascii("second_key")',
            'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
            'S_inverse.STORE[n_q] = DEFINED (PARRAY n_new)', pair('S_inverse', 'n_new', 66, 7),
            'S_inverse.STORE[n_new_hold] = DEFINED (PARRAY n_new)',
            '$heap_owners($heap_graph(S_inverse), HARRAY n_new) = 1',
            '$entry_lookup(S_inverse.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_a_child))',
            'n_a_child =/= n_new', pair('S_inverse', 'n_a_child', 44, 55),
        ] + biases('S_inverse', '[n_old]', '[n_new]') + seek('S_inverse', 43, 'S_inverse_entered') + [
            '$heap_owners($heap_graph(S_inverse_entered), HARRAY n_new) = 2',
        ] + seek('S_inverse_entered', 41, 'S_inverse_resume') + [
            'S_inverse_resume.TODO = (ARRAY_KEY_UNDEFINED_ARRAY_RESULT n_b n_new poperand_inverse n_inverse_key* eps z_inverse) :: ptask_inverse*',
            'S_inverse_resume.STORE[n_q] = DEFINED (PARRAY n_old)',
            '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_old) = 3',
            '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_new) = 1',
        ] + biases('S_inverse_resume', '[n_old]', '[n_new]') + [
            'PhpStep: S_inverse_resume ~> S_inverse_insert',
            '$entry_lookup(S_inverse_insert.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_old))',
            '$heap_owners($heap_graph(S_inverse_insert), HARRAY n_new) = 1',
        ]
        start = 'S_inverse_insert'
        retired = ['n_a', 'n_b', 'n_old', 'n_new', 'n_a_child']
    checks += empty_biases(start) + [
        '$heap_owners($heap_graph(' + start + '), HARRAY n_old) = 3',
        'S_inverse_insert.STORE[n_q] = DEFINED (PARRAY n_old)',
    ] + seek(start, 15, 'S_read') + [
        '$heap_owners($heap_graph(S_read), HCELL n_q) = 1',
        '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_read') + empty_biases('S_done')
    checks += [f'~((HARRAY {array}) <- S_done.ALLOCATIONS)' for array in retired]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
