#!/usr/bin/env python3
"""Borrowed scalar slots acquire no owner while array deficits survive cleanup."""
import base64
import json

import array_literal_float_wrapped_mixed_cv_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as ARRAY_HELPERS, seek
from array_literal_float_typed_alias_leaf_state_review import driven

HELPERS = ARRAY_HELPERS + r'''
def $list_warning_frontier(S, 20) = ($array_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 21) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 23) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i
'''


def pair(state, array, first, second):
    return (f'{state}.ARRAYS[{array}].ITEMS = '
            f'[ENTRY (KINT 0) (DIRECT (PINT {first})), ENTRY (KINT 1) (DIRECT (PINT {second}))]')


def empty_biases(state):
    return [f'{state}.{field} = eps' for field in
            ('LITERALREFRETAINED', 'LITERALREFDEBTS', 'LITERALARRAYRETAINED', 'LITERALARRAYDEBTS')]


def debt(state):
    return [f'{state}.LITERALREFRETAINED = eps', f'{state}.LITERALREFDEBTS = eps',
            f'{state}.LITERALARRAYRETAINED = eps', f'{state}.LITERALARRAYDEBTS = [n_new]']


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, inverse_line, key = (15, 24, '1') if thrown else (13, 20, '$(-2)')
    args = 'n_a, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_RESULT n_a poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_b n_new poperand_inverse eps z_inverse n_bits_inverse 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 20, 'S') + [
        '$array_float_key_plan(S) = ((' + args + '))',
        f'z = {line}', f'i = {key}', 'S.RESULT = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_capture)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_capture)',
        'poperand = BORROWED (ROOT n_capture)', 'n_capture <- S.REFCELLS',
        'S.STORE[n_capture] = DEFINED pvalue_initial',
        '$lookup(S.ENV, $ptascii("initial")) = (n_snapshot)',
        'S.STORE[n_snapshot] = DEFINED pvalue_initial', 'n_snapshot =/= n_capture',
        '~(n_snapshot <- S.REFCELLS)', '$array_float_key_scalar(S, pvalue_initial)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_new)', '~(n_replacement <- S.REFCELLS)',
        pair('S', 'n_new', 44, 8),
        '$lookup(S.ENV, $ptascii("unrelated")) = (n_unrelated)',
        'n_unrelated =/= n_capture', 'S.STORE[n_unrelated] = DEFINED (PINT 99)',
        '$array_float_key_value(S, S.RESULT) = eps',
        '$array_float_key_live_value(S, poperand) = eps', '$array_float_array_key_plan(S) = eps',
        '$array_float_key_source(S, ' + args + ')', '$array_float_key_ready(S, n_a, poperand)',
        '$operand_nodes(poperand) = eps', '$node_children(S, HCELL n_capture) = eps',
        '$heap_owners($heap_graph(S), HCELL n_capture) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_new) = 1',
        '~$array_float_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_key_source(S, n_a, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_key_source(S, n_a, BORROWED (ROOT (|S.STORE|)), phpType13*, z, n_bits, i)',
        '$array_float_key_plan(S[.STORE[n_capture] = DEFINED (PSTRING eps)]) = eps',
        '$array_float_key_plan(S[.LITERALREFDEBTS = [n_capture]]) = eps',
    ]
    if thrown:
        checks += ['pvalue_initial = PFLOAT n_initial_bits', '$float_long(n_initial_bits, true) = (2, [PRECISIONLOSS])']
    else:
        checks += ['pvalue_initial = PBOOL false']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(' + marker + ') = [HARRAY n_a]',
        '$heap_count(HCELL n_capture, $task_nodes(' + marker + ')) = 0',
        '$heap_count(HARRAY n_new, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_capture) = 2',
        'S_lost = S_dispatch[.ENV = $unbind($unbind(S_dispatch.ENV, $ptascii("q")), $ptascii("outside"))]',
        'H_lost = $heap_prune($heap_graph(S_lost)[.DEBTS = eps])',
        '(HCELL n_capture) <- S_lost.ALLOCATIONS', '~((HCELL n_capture) <- H_lost.NODES)',
        '(HARRAY n_new) <- H_lost.NODES', '$array_float_key_source(S_lost, ' + args + ')',
        '$call_task_valid(S_lost, ' + marker + ')', '$error_call_valid(S_lost, perrorcall)',
        '~$array_float_key_ready(S_lost, n_a, poperand)',
        '$error_read_discard(S_lost, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key element during throw"',
        'S_retired = S_lost[.ALLOCATIONS = H_lost.NODES][.REFCELLS = $literal_reference_delete(S_lost.REFCELLS, n_capture)]',
        '$array_float_key_source(S_retired, ' + args + ')', '$error_call_valid(S_retired, perrorcall)',
        '~$array_float_key_ready(S_retired, n_a, poperand)',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_capture, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_count(HARRAY n_new, $tasks_nodes(pframe.TODO)) = 0',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (DIRECT (PINT 8))]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps',
            'S_start.ERRORHANDLER = S.ERRORHANDLER', 'S_start.STORE[n_dest] = DEFINED (PINT 99)',
            'S_start.STORE[n_later] = DEFINED (PINT 7)', '~((HARRAY n_a) <- S_start.ALLOCATIONS)',
            'S_start.STORE[n_capture] = DEFINED (PARRAY n_new)',
            '$heap_owners($heap_graph(S_start), HCELL n_capture) = 1',
            '$heap_owners($heap_graph(S_start), HARRAY n_new) = 1',
            '$heap_owners($heap_graph(S_start)[.DEBTS = eps], HARRAY n_new) = 2',
            '$literal_reference_debt_safe(S_start, $heap_graph(S_start))',
        ] + debt('S_start')
    else:
        checks += ['S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 21, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_unrelated)',
            'n_unrelated <- S_resume.REFCELLS', 'S_resume.STORE[n_unrelated] = DEFINED (PINT 99)',
            '$lookup(S_resume.ENV, $ptascii("outside")) = (n_capture)',
            'S_resume.STORE[n_capture] = DEFINED (PARRAY n_new)',
            '$array_float_key_live_value(S_resume, poperand) = eps',
            '$array_float_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_key_ready(S_resume, n_a, poperand)',
            'S_builder = S_resume[.STORE[n_capture] = DEFINED (PARRAY n_a)]',
            '~$array_float_key_ready(S_builder, n_a, poperand)',
            '$error_read_discard(S_builder, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key element during throw"',
            'S_discard = $error_read_discard(S_resume, ' + marker + ')',
            'S_discard.STORE = S_resume.STORE', 'S_discard.ARRAYS = S_resume.ARRAYS',
        ] + debt('S_discard') + [
            'PhpStep: S_resume ~> S_insert', 'S_insert.STORE = S_resume.STORE',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT $(-2)) = (DIRECT (PARRAY n_new))',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
            '$heap_graph(S_insert).DEBTS = [HARRAY n_new]',
            '$heap_owners($heap_graph(S_insert), HCELL n_capture) = 1',
            '$heap_owners($heap_graph(S_insert), HARRAY n_new) = 2',
            '$heap_owners($heap_graph(S_insert)[.DEBTS = eps], HARRAY n_new) = 3',
            '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
        ] + debt('S_insert') + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_read') + debt('S_read') + [
        'S_read.GLOBALTABLE = eps', 'S_read.FRAMES = eps', 'S_read.CURRENT = eps',
        '$lookup(S_read.ENV, $ptascii("q")) = (n_unrelated)',
        '$lookup(S_read.ENV, $ptascii("outside")) = (n_capture)',
        'S_read.STORE[n_capture] = DEFINED (PARRAY n_new)', pair('S_read', 'n_new', 55, 66),
        '$lookup(S_read.ENV, $ptascii("replacement")) = (n_replacement)',
        'S_read.STORE[n_replacement] = DEFINED (PARRAY n_new)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_new',
        pair('S_read', 'n_copy', 66, 88), 'S_read.STORE[n_snapshot] = DEFINED pvalue_initial',
        '$node_children(S_read, HCELL n_capture) = [HARRAY n_new]',
        '$heap_owners($heap_graph(S_read), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_read), HCELL n_unrelated) = 2',
        '$heap_owners($heap_graph(S_read), HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_new) = 2',
        '$heap_owners($heap_graph(S_read), HARRAY n_copy) = 1',
        '$heap_count(HCELL n_capture, $machine_roots(S_read)) = 1',
        '$heap_count(HARRAY n_new, $machine_roots(S_read)) = 0',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        'S_zero = S_read[.ENV = $unbind(S_read.ENV, $ptascii("replacement"))]',
        'H_zero = $heap_graph(S_zero)', 'H_zero_live = $heap_prune(H_zero[.DEBTS = eps])',
        '$heap_owners(H_zero_live, HARRAY n_new) = 1',
        '(HCELL n_capture) <- H_zero_live.NODES', '(HARRAY n_new) <- H_zero_live.NODES',
        '~$literal_reference_debt_safe(S_zero, H_zero)',
        '(S_blocked, H_blocked) = $prune_allocations_observed(S_zero)',
        'S_blocked.COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
        'S_blocked.ALLOCATIONS = S_zero.ALLOCATIONS', 'H_blocked = H_zero',
        '$drive_steps(S_blocked, 50) = S_blocked',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_read_split_found = $drive_steps(S_read, 1)', 'S_read_split_found.COMPLETION = BUDGET',
        'S_read_split = S_read_split_found[.COMPLETION = NORMAL]',
    ] + seek('S_read_split', 10, 'S_inverse') + [
        '$array_float_array_key_plan(S_inverse) = ((n_b, n_new, poperand_inverse, eps, z_inverse, n_bits_inverse, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = REFERENCE n_capture',
        'S_inverse.RESULT = VARIABLE ($ptascii("q")) z_inverse',
        '$lookup(S_inverse.ENV, $ptascii("q")) = (n_capture)',
        'n_b =/= n_a', '$array_float_array_key_reference(S_inverse, n_capture) = (n_new)',
        '$heap_owners($heap_graph(S_inverse), HCELL n_capture) = 2',
        '$heap_owners($heap_graph(S_inverse), HARRAY n_new) = 1',
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse,
        '$error_call_valid(S_inverse_dispatch, perrorcall_inverse)',
        '$task_nodes(' + inverse + ') = [HARRAY n_b, HARRAY n_new]',
        '$heap_owners($heap_graph(S_inverse_dispatch), HCELL n_capture) = 2',
        '$heap_owners($heap_graph(S_inverse_dispatch), HARRAY n_new) = 2',
    ] + debt('S_inverse') + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 13, 'S_inverse_entered') + [
        'S_inverse_entered.FRAMES = pframe_inverse :: pframe_tail_inverse*',
        'pframe_inverse.TODO = (ERROR_HANDLER_RESULT perrorcall_inverse_entered) :: ptask_inverse_caller*',
        'perrorcall_inverse_entered.RESUME = ' + inverse,
        '$heap_count(HCELL n_capture, $tasks_nodes(pframe_inverse.TODO)) = 0',
    ] + seek('S_inverse_entered', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_after_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_unrelated)',
        '$lookup(S_inverse_resume.ENV, $ptascii("outside")) = (n_capture)',
        'S_inverse_resume.STORE[n_capture] = DEFINED pvalue_balance',
        'pvalue_balance = PINT 44' if thrown else 'pvalue_balance = PNULL',
        '$array_float_key_scalar(S_inverse_resume, pvalue_balance)',
        '$array_float_array_key_reference(S_inverse_resume, n_capture) = eps',
        '$array_float_array_key_item(S_inverse_resume, poperand_inverse) = (DIRECT pvalue_balance)',
        '$array_float_array_key_ready(S_inverse_resume, n_b, n_new, poperand_inverse)',
        '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_new) = 1',
        'S_inverse_discard = $error_read_discard(S_inverse_resume, ' + inverse + ')',
        'S_inverse_discard.STORE = S_inverse_resume.STORE',
        'S_inverse_discard.ARRAYS = S_inverse_resume.ARRAYS',
    ] + empty_biases('S_inverse_discard') + [
        'PhpStep: S_inverse_resume ~> S_balance', 'S_balance.STORE = S_inverse_resume.STORE',
        '$entry_lookup(S_balance.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT pvalue_balance)',
        '$heap_graph(S_balance).DEBTS = eps',
        '$heap_owners($heap_graph(S_balance), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_balance), HARRAY n_new) = 1',
    ] + empty_biases('S_balance') + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_cow') + [
        'S_cow.STORE[n_capture] = DEFINED (PINT 77)', '$node_children(S_cow, HCELL n_capture) = eps',
        '$entry_lookup(S_cow.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT pvalue_balance)',
        'S_cow.STORE[n_replacement] = DEFINED (PARRAY n_new)', pair('S_cow', 'n_new', 77, 66),
        'S_cow.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', pair('S_cow', 'n_copy', 66, 88),
        '$lookup(S_cow.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_cow.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_new',
        pair('S_cow', 'n_shared', 88, 99), 'S_cow.STORE[n_snapshot] = DEFINED pvalue_initial',
        '$heap_owners($heap_graph(S_cow), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_cow), HCELL n_unrelated) = 2',
        '$heap_owners($heap_graph(S_cow), HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_copy) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_shared) = 1',
        'S_done = $drive_steps(S_cow, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
    ] + empty_biases('S_cow') + empty_biases('S_done') + [
        '~((HCELL n_capture) <- S_done.ALLOCATIONS)', '~((HCELL n_unrelated) <- S_done.ALLOCATIONS)',
        *[f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in ('n_a', 'n_b', 'n_new', 'n_copy', 'n_shared')],
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("outside")) = eps',
        '$lookup(S_done.ENV, $ptascii("replacement")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_balanced, 0) = S_balanced[.COMPLETION = BUDGET]',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
