#!/usr/bin/env python3
"""By-value CV references and their inverse preserve separate count families."""
import base64
import json

import array_literal_float_cv_ref_cycle_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as ARRAY_HELPERS, driven, payload, seek

HELPERS = ARRAY_HELPERS + r'''
def $list_warning_frontier(S, 20) = ($array_float_ref_key_plan(S) =/= eps)
def $list_warning_frontier(S, 21) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 23) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i
'''


def empty_biases(state):
    return [f'{state}.{field} = eps' for field in
            ('LITERALREFRETAINED', 'LITERALREFDEBTS', 'LITERALARRAYRETAINED', 'LITERALARRAYDEBTS')]


def cross_biases(state):
    return [f'{state}.LITERALREFRETAINED = eps', f'{state}.LITERALREFDEBTS = [n_new]',
            f'{state}.LITERALARRAYRETAINED = [n_old]', f'{state}.LITERALARRAYDEBTS = eps']


def conditions(name, program, path, stdout):
    array = name.endswith('-array')
    args = 'n_a, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_a n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_REF_RESULT n_b n_new poperand_inverse eps 19 n_bits_inverse 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', 'z = 12', 'i = 1', 'S.RESULT = poperand',
        '$lookup(S.ENV, $ptascii("q")) = (n_initial_q)',
        '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_initial_q =/= n_hold',
        'S.STORE[n_initial_q] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '~(n_initial_q <- S.REFCELLS)', '~(n_hold <- S.REFCELLS)', payload('S', 'n_old', 2),
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)', 'n_new =/= n_initial_q',
        '~(n_new <- S.REFCELLS)',
        '$array_float_key_value(S, poperand) = eps', '$array_float_key_plan(S) = eps',
        '$array_float_array_key_value(S, poperand) = (n_old)',
        '$array_float_array_key_item(S, poperand) = (DIRECT (PARRAY n_old))',
        '$array_float_array_key_ready(S, n_a, n_old, poperand)',
        '$array_float_array_key_source(S, ' + args + ')',
        '~$array_float_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_array_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_array_key_source(S, n_a, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '$array_float_array_key_plan(S[.REFCELLS = n_initial_q :: S.REFCELLS][.STORE[n_initial_q] = DEFINED (PSTRING eps)]) = eps',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
    ]
    if array:
        checks += ['S.STORE[n_new] = DEFINED (PARRAY n_payload)', 'n_payload =/= n_old',
                   payload('S', 'n_payload', 44), '$heap_owners($heap_graph(S), HARRAY n_payload) = 1']
    else:
        checks += ['S.STORE[n_new] = DEFINED (PINT 44)']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 12',
        '$error_call_valid(S_dispatch, perrorcall)', '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 13])',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_initial_q, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_resume.REFCELLS',
        '~((HCELL n_initial_q) <- S_resume.ALLOCATIONS)',
        '$array_float_array_key_value(S_resume, poperand) = eps',
        '$array_float_key_live_value(S_resume, poperand) = eps',
        '$array_float_array_key_item(S_resume, poperand) = (ALIAS n_new)',
        '$array_float_array_key_ready(S_resume, n_a, n_old, poperand)',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$propref_at(S_resume.PROPREFS, n_new) = eps',
        '$heap_owners($heap_graph(S_resume), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_resume), HARRAY n_old) = 2',
        'S_string = S_resume[.STORE[n_new] = DEFINED (PSTRING eps)]',
        '$array_float_array_key_item(S_string, poperand) = eps',
        '~$array_float_array_key_ready(S_string, n_a, n_old, poperand)',
        'S_typed = S_resume[.PROPREFS = [{CELL n_new, SOURCES eps}]]',
        '$array_float_array_key_item(S_typed, poperand) = eps',
        'S_builder = S_resume[.STORE[n_new] = DEFINED (PARRAY n_a)]',
        '$array_float_array_key_item(S_builder, poperand) = (ALIAS n_new)',
        '~$array_float_array_key_ready(S_builder, n_a, n_old, poperand)',
        '$error_read_discard(S_builder, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        'S_discard = $error_read_discard(S_resume, ' + marker + ')',
        'S_discard.STORE = S_resume.STORE', 'S_discard.ARRAYS = S_resume.ARRAYS',
    ] + cross_biases('S_discard') + [
        'PhpStep: S_resume ~> S_insert', 'S_insert.STORE = S_resume.STORE',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 1) = (ALIAS n_new)',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        '$heap_graph(S_insert).DEBTS = [HCELL n_new]',
        '$heap_owners($heap_graph(S_insert), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_insert)[.DEBTS = eps], HCELL n_new) = 3',
        '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
    ] + cross_biases('S_insert') + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("q")) = eps',
        '$lookup(S_read.ENV, $ptascii("replacement")) = (n_new)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 1) = (ALIAS n_new)',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        '$heap_owners($heap_graph(S_read), HCELL n_new) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HCELL n_new) = 2',
        '$heap_count(HCELL n_new, $machine_roots(S_read)) = 1',
        '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S_read[.LITERALARRAYRETAINED = eps]), HARRAY n_old) = 1',
        '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
    ] + cross_biases('S_read')
    if array:
        checks += [
            'S_read.STORE[n_new] = DEFINED (PARRAY n_live)', 'n_live =/= n_payload',
            payload('S_read', 'n_live', 66), payload('S_read', 'n_payload', 44),
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_payload))',
            'n_copy_payload =/= n_payload', 'n_copy_payload =/= n_live', payload('S_read', 'n_copy_payload', 55),
            '$lookup(S_read.ENV, $ptascii("snapshot")) = (n_snapshot_cell)',
            'S_read.STORE[n_snapshot_cell] = DEFINED (PARRAY n_payload)',
            '$node_children(S_read, HCELL n_new) = [HARRAY n_live]',
            '$heap_owners($heap_graph(S_read), HARRAY n_live) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_payload) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_payload) = 1',
        ]
    else:
        checks += ['S_read.STORE[n_new] = DEFINED (PINT 66)',
                   '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PINT 55))',
                   '$node_children(S_read, HCELL n_new) = eps']
    checks += seek('S_read', 20, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_b, n_new, poperand_inverse, eps, 19, n_bits_inverse, 3))',
        'poperand_inverse = VARIABLE ($ptascii("q")) 19',
        '$lookup(S_inverse.ENV, $ptascii("q")) = (n_new)',
        '$heap_owners($heap_graph(S_inverse), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_inverse), HARRAY n_old) = 2',
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse,
        '$error_call_valid(S_inverse_dispatch, perrorcall_inverse)',
        '$task_nodes(' + inverse + ') = [HARRAY n_b, HCELL n_new]',
        '$heap_owners($heap_graph(S_inverse_dispatch), HCELL n_new) = 3',
    ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 23, 'S_inverse_entered') + [
        'S_inverse_entered.FRAMES = pframe_inverse :: pframe_tail_inverse*',
        'pframe_inverse.TODO = (ERROR_HANDLER_RESULT perrorcall_inverse_entered) :: ptask_caller_inverse*',
        'perrorcall_inverse_entered.RESUME = ' + inverse,
    ] + seek('S_inverse_entered', 21, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_after_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_fresh_q)',
        'n_fresh_q =/= n_new', 'n_fresh_q =/= n_initial_q', '~(n_fresh_q <- S_inverse_resume.REFCELLS)',
        'S_inverse_resume.STORE[n_fresh_q] = DEFINED (PARRAY n_old)',
        '$array_float_key_value(S_inverse_resume, poperand_inverse) = eps',
        '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (DIRECT (PARRAY n_old))',
        '$array_float_ref_key_ready(S_inverse_resume, n_b, n_new, poperand_inverse)',
        '$array_float_ref_key_source(S_inverse_resume[.ENV = eps], n_b, n_new, poperand_inverse, eps, 19, n_bits_inverse, 3)',
        '$heap_owners($heap_graph(S_inverse_resume), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_old) = 3',
        'S_inverse_string = S_inverse_resume[.STORE[n_fresh_q] = DEFINED (PSTRING eps)]',
        '$array_float_ref_key_value(S_inverse_string, n_new, poperand_inverse) = eps',
        'S_inverse_typed = S_inverse_resume[.PROPREFS = [{CELL n_new, SOURCES eps}]]',
        '$array_float_ref_key_value(S_inverse_typed, n_new, poperand_inverse) = eps',
        'S_inverse_builder = S_inverse_resume[.STORE[n_fresh_q] = DEFINED (PARRAY n_b)]',
        '$array_float_ref_key_value(S_inverse_builder, n_new, poperand_inverse) = (DIRECT (PARRAY n_b))',
        '~$array_float_ref_key_ready(S_inverse_builder, n_b, n_new, poperand_inverse)',
        '$error_read_discard(S_inverse_builder, ' + inverse + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
        'S_inverse_discard = $error_read_discard(S_inverse_resume, ' + inverse + ')',
        'S_inverse_discard.STORE = S_inverse_resume.STORE', 'S_inverse_discard.ARRAYS = S_inverse_resume.ARRAYS',
    ] + empty_biases('S_inverse_discard') + [
        'PhpStep: S_inverse_resume ~> S_balance', 'S_balance.STORE = S_inverse_resume.STORE',
        '$entry_lookup(S_balance.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
        '$heap_graph(S_balance).DEBTS = eps',
        '$heap_owners($heap_graph(S_balance), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_balance), HARRAY n_old) = 3',
    ] + empty_biases('S_balance') + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_cow') + [
        '$lookup(S_cow.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_cow.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_a',
        '$entry_lookup(S_cow.ARRAYS[n_shared].ITEMS, KINT 1) = (ALIAS n_new)',
        '$entry_lookup(S_cow.ARRAYS[n_a].ITEMS, KINT 1) = (ALIAS n_new)',
        'S_cow.STORE[n_fresh_q] = DEFINED (PARRAY n_q_array)', 'n_q_array =/= n_old',
        payload('S_cow', 'n_q_array', 88), payload('S_cow', 'n_old', 2),
        '$entry_lookup(S_cow.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
        '$lookup(S_cow.ENV, $ptascii("balance_copy")) = (n_balance_copy_cell)',
        'S_cow.STORE[n_balance_copy_cell] = DEFINED (PARRAY n_balance_copy)', 'n_balance_copy =/= n_b',
        '$entry_lookup(S_cow.ARRAYS[n_balance_copy].ITEMS, KINT 3) = (DIRECT (PARRAY n_balance_copy_child))',
        'n_balance_copy_child =/= n_old', payload('S_cow', 'n_balance_copy_child', 99),
        '$heap_owners($heap_graph(S_cow), HCELL n_new) = 3',
        '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S_cow), HARRAY n_q_array) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_balance_copy_child) = 1',
    ] + empty_biases('S_cow')
    if array:
        checks += ['S_cow.STORE[n_new] = DEFINED (PARRAY n_live)', payload('S_cow', 'n_live', 77),
                   payload('S_cow', 'n_copy_payload', 55), payload('S_cow', 'n_payload', 44),
                   '$heap_owners($heap_graph(S_cow), HARRAY n_live) = 1']
    else:
        checks += ['S_cow.STORE[n_new] = DEFINED (PINT 77)',
                   '$entry_lookup(S_cow.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PINT 55))']
    retired = ['n_a', 'n_b', 'n_old', 'n_q_array', 'n_balance_copy_child', 'n_balance_copy', 'n_copy', 'n_shared']
    if array:
        retired += ['n_payload', 'n_live', 'n_copy_payload']
    checks += [
        'S_done = $drive_steps(S_cow, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
    ] + empty_biases('S_done') + [
        '~((HCELL n_new) <- S_done.ALLOCATIONS)', '~((HCELL n_fresh_q) <- S_done.ALLOCATIONS)',
        *[f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in retired],
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        'S_split_found = $drive_steps(S_cow, 1)', 'S_split_found.COMPLETION = BUDGET',
        '$drive_steps(S_split_found[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if not array:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
