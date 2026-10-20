#!/usr/bin/env python3
"""Reached ordinary CV arrays separate acquired table counts from cell identity."""
import base64
import json

import array_literal_float_array_cv_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS as BASE_HELPERS, seek

HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 30) = ($array_float_array_key_plan(S) =/= eps)
def $list_warning_frontier(S, 31) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_ARRAY_RESULT n n_old poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 32) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_ARRAY_RESULT n n_old poperand phpType13* z n_bits i
'''


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET', f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in
              ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'LITERALARRAYRETAINED', 'LITERALARRAYDEBTS')]]


def item(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def conditions(name, program, path, stdout):
    stable = name.endswith('same-table')
    line, key, seed = (10, 2, 44) if stable else (12, 1, 2)
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALARRAYRETAINED = eps', 'S_initial.LITERALARRAYDEBTS = eps',
    ] + seek('S_initial', 30, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', f'i = {key}',
        'S.RESULT = poperand', '$lookup(S.ENV, $ptascii("q")) = (n_q)',
        '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_q =/= n_hold',
        'S.STORE[n_q] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '~(n_q <- S.REFCELLS)', '~(n_hold <- S.REFCELLS)', item('S', 'n_old', seed),
        '$array_float_array_key_value(S, poperand) = (n_old)',
        '$array_float_array_key_source(S, ' + args + ')',
        '$array_float_array_key_ready(S, n_builder, n_old, poperand)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$array_float_array_key_plan(S[.REFCELLS = S.REFCELLS ++ [n_q]]) = eps',
        '~$array_float_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_array_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_array_key_source(S, n_builder, n_builder, poperand, phpType13*, z, n_bits, i)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
        'S_dispatch.LITERALARRAYRETAINED = eps', 'S_dispatch.LITERALARRAYDEBTS = eps',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 32, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_q, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 31, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_current_cell)', '~(n_current_cell <- S_resume.REFCELLS)',
        'S_resume.STORE[n_current_cell] = DEFINED (PARRAY n_current)',
        '$array_float_array_key_value(S_resume, poperand) = (n_current)',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_array_key_ready(S_resume, n_builder, n_old, poperand)',
        'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
        '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
        'S_resume.LITERALARRAYRETAINED = eps', 'S_resume.LITERALARRAYDEBTS = eps',
        'S_wrapped = S_resume[.REFCELLS = S_resume.REFCELLS ++ [n_current_cell]][.STORE[n_current_cell] = DEFINED (PSTRING eps)]',
        '$call_task_valid(S_wrapped, ' + marker + ')',
        '$array_float_array_key_value(S_wrapped, poperand) = eps',
        '~$array_float_array_key_ready(S_wrapped, n_builder, n_old, poperand)',
        '$error_read_discard(S_wrapped, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        '~$array_float_array_key_ready(S_resume[.STORE[n_current_cell] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
        '~$array_float_array_key_ready(S_resume[.STORE[n_current_cell] = DEFINED (PSTRING eps)], n_builder, n_old, poperand)',
        'PhpStep: S_resume ~> S_insert',
        'S_insert.STORE = S_resume.STORE',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        f'$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT {key}) = (DIRECT (PARRAY n_current))',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
    ]
    if stable:
        checks += [
            'n_current = n_old', 'n_current_cell =/= n_q', '~((HCELL n_q) <- S_resume.ALLOCATIONS)',
            'S_insert.LITERALARRAYRETAINED = eps', 'S_insert.LITERALARRAYDEBTS = eps',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 3',
        ]
    else:
        checks += [
            'n_current =/= n_old', 'n_current_cell = n_q', item('S_resume', 'n_old', 2), item('S_resume', 'n_current', 44),
            'S_insert.LITERALARRAYRETAINED = [n_old]', 'S_insert.LITERALARRAYDEBTS = [n_current]',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HARRAY n_current) = 2',
        ]
    checks += driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        'S_read.LITERALREFRETAINED = eps', 'S_read.LITERALREFDEBTS = eps',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
    ]
    if stable:
        checks += [
            'S_read.LITERALARRAYRETAINED = eps', 'S_read.LITERALARRAYDEBTS = eps',
            'S_read.STORE[n_current_cell] = DEFINED (PARRAY n_q_child)', 'n_q_child =/= n_old',
            item('S_read', 'n_q_child', 55), item('S_read', 'n_old', 44),
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_builder',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 2) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_old', item('S_read', 'n_copy_child', 77),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_read), HARRAY n_q_child) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_child) = 1',
            'S_final = S_read',
        ]
    else:
        checks += [
            '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
            'S_read.STORE[n_q] = DEFINED (PARRAY n_current)', item('S_read', 'n_current', 55),
            '$entry_lookup(S_read.ARRAYS[n_builder].ITEMS, KINT 1) = (DIRECT (PARRAY n_current))',
            '$entry_lookup(S_read.ARRAYS[n_builder].ITEMS, KINT 4) = (DIRECT (PINT 66))',
            'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_current]',
            '$heap_graph(S_read).DEBTS = [HARRAY n_current]',
            '$heap_owners($heap_graph(S_read), HARRAY n_current) = 1',
            '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_current) = 2',
            '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
            'H_debt = {NODES ([HARRAY 0, HARRAY 1, HARRAY 2]), EDGES ([HEDGE (HARRAY 0) (HARRAY 2), HEDGE (HARRAY 1) (HARRAY 2)]), ROOTS ([HARRAY 1, HARRAY 2]), DEBTS ([HARRAY 2])}',
            '$heap_valid(H_debt)', '$heap_owners(H_debt, HARRAY 2) = 2',
            'H_pruned = $heap_prune(H_debt)', 'H_pruned.NODES = [HARRAY 1, HARRAY 2]',
            'H_pruned.EDGES = [HEDGE (HARRAY 1) (HARRAY 2)]', '$heap_owners(H_pruned, HARRAY 2) = 1',
        ] + seek('S_read', 30, 'S_inverse') + [
            '$array_float_array_key_plan(S_inverse) = ((n_balance, n_current, poperand_inverse, eps, 19, n_inverse_bits, 3))',
            'poperand_inverse = VARIABLE ($ptascii("q")) 19',
            'S_inverse.LITERALARRAYRETAINED = [n_old]', 'S_inverse.LITERALARRAYDEBTS = [n_current]',
        ] + seek('S_inverse', 31, 'S_inverse_resume') + [
            'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_ARRAY_RESULT n_balance n_current poperand_inverse eps 19 n_inverse_bits 3) :: ptask_inverse*',
            '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = (n_old)',
            'PhpStep: S_inverse_resume ~> S_balanced',
            'S_balanced.LITERALARRAYRETAINED = eps', 'S_balanced.LITERALARRAYDEBTS = eps',
            '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
            '$heap_owners($heap_graph(S_balanced), HARRAY n_old) = 3',
            '$heap_owners($heap_graph(S_balanced), HARRAY n_current) = 1',
        ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_final') + [
            'S_final.STORE[n_q] = DEFINED (PARRAY n_q_child)', 'n_q_child =/= n_old',
            item('S_final', 'n_q_child', 66), item('S_final', 'n_current', 77), item('S_final', 'n_old', 2),
            '$heap_owners($heap_graph(S_final), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_final), HARRAY n_current) = 1',
        ]
    checks += [
        'S_done = $drive_steps(S_final, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        '~((HARRAY n_old) <- S_done.ALLOCATIONS)', '~((HARRAY n_current) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_q_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_builder) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 1) = $drive_steps($drive_steps(S_final, 0)[.COMPLETION = NORMAL], 1)',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if stable:
        checks += [
            '~((HARRAY n_copy) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy_child) <- S_done.ALLOCATIONS)',
            'P = $ppstart(0, ' + program + ', $base64(' + json.dumps(base64.b64encode(bytes(path)).decode()) + '))',
            'P.COMPLETION = PPCNORMAL', '$ppimage(P, false) =/= eps',
            '$ppimage(P[.FOLD.MEMORY.LITERALARRAYRETAINED = [n_old]], false) = eps',
            '$ppimage(P[.FOLD.MEMORY.LITERALARRAYDEBTS = [n_old]], false) = eps',
        ]
    else:
        checks += ['~((HARRAY n_balance) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
