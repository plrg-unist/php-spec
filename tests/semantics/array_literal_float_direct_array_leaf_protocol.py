#!/usr/bin/env python3
"""Direct child owners remain independent of parent debt and entry multiplicity."""
import base64
import json

import array_literal_float_direct_array_leaf_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_protocol import HELPERS, driven
from array_literal_float_ref_deficit_state_review import seek
from array_literal_float_array_alias_leaf_protocol import payload


def children(state, table, names, sibling):
    entries = [f'ENTRY (KINT {i}) (DIRECT (PARRAY {name}))' for i, name in enumerate(names)]
    entries.append(f'ENTRY (KINT {len(names)}) (DIRECT (PINT {sibling}))')
    return f'{state}.ARRAYS[{table}].ITEMS = [' + ', '.join(entries) + ']'


def conditions(name, program, path, stdout):
    repeated = name.endswith('repeated-child')
    initial_children = ('n_payload', 'n_payload') if repeated else ('n_payload',)
    read_children = ('n_live', 'n_payload') if repeated else ('n_live',)
    copied_children = ('n_copied', 'n_copied_second') if repeated else ('n_copied',)
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_balance n_current poperand_inverse eps 19 n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 30, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', 'z = 13', 'i = 1',
        '$array_float_key_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)',
        'S.STORE[n_q] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '~(n_q <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_current)', 'n_old =/= n_current',
        children('S', 'n_old', ('n_old_payload',), 7), children('S', 'n_current', initial_children, 8),
        payload('S', 'n_old_payload', 33), payload('S', 'n_payload', 44), 'n_payload =/= n_old_payload',
        '$lookup(S.ENV, $ptascii("old_inner")) = eps', '$lookup(S.ENV, $ptascii("new_inner")) = eps',
        '$lookup(S.ENV, $ptascii("old_snapshot")) = (n_old_snapshot)',
        'S.STORE[n_old_snapshot] = DEFINED (PARRAY n_old_payload)',
        '$node_children(S, HARRAY n_old) = [HARRAY n_old_payload]',
        '$node_children(S, HARRAY n_current) = [' + ', '.join('HARRAY '+n for n in initial_children) + ']',
        '$node_children(S, HARRAY n_payload) = eps',
        '$entries_nodes(S.ARRAYS[n_current].ITEMS) = [' + ', '.join('HARRAY '+n for n in initial_children) + ']',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2', '$heap_owners($heap_graph(S), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_old_payload) = 2', '$heap_owners($heap_graph(S), HARRAY n_payload) = 2',
        '$literal_reference_child_array(S, n_payload, S.ALLOCATIONS)',
        '$literal_reference_flat_items(S, S.ARRAYS[n_current].ITEMS)',
        '~$literal_reference_flat_leaf(S, PARRAY n_payload)',
        '$literal_reference_flat_array(S, n_current, [HARRAY n_current, HARRAY n_payload])',
        '~$literal_reference_flat_array(S, n_current, [HARRAY n_current])',
        '$literal_reference_flat_sources(S, S.ARRAYS[n_current].ITEMS, eps)',
        '$array_float_array_key_value(S[.REFCELLS = S.REFCELLS ++ [n_q]], poperand) = eps',
        'S_string = S[.STORE[n_q] = DEFINED (PSTRING ($ptascii("text")))]',
        '$array_float_key_value(S_string, poperand) = eps', '$array_float_array_key_value(S_string, poperand) = eps',
        'S.PROPREFS = eps', 'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        '$array_float_array_key_source(S, ' + args + ')', '$array_float_array_key_ready(S, n_builder, n_old, poperand)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 13',
        '$error_call_valid(S_dispatch, perrorcall)', '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old_payload) = 2',
    ]
    if repeated:
        checks += ['$lookup(S.ENV, $ptascii("snapshot")) = eps']
    else:
        checks += ['$lookup(S.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S.STORE[n_snapshot] = DEFINED (PARRAY n_payload)']
    checks += driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 32, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_old_payload, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 31, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.STORE[n_q] = DEFINED (PARRAY n_current)',
        '$array_float_array_key_value(S_resume, poperand) = (n_current)',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_array_key_ready(S_resume, n_builder, n_old, poperand)',
        'S_child_debt = S_resume[.LITERALARRAYDEBTS = [n_payload]]',
        '$array_float_array_key_source(S_child_debt, ' + args + ')',
        '~$literal_reference_flat_items(S_child_debt, S_child_debt.ARRAYS[n_current].ITEMS)',
        '~$array_float_array_key_ready(S_child_debt, n_builder, n_old, poperand)',
        '$error_read_discard(S_child_debt, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        '~$literal_reference_child_array(S_resume[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (ALIAS n_q)]], n_payload, S_resume.ALLOCATIONS)',
        '~$literal_reference_child_array(S_resume[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_payload))]], n_payload, S_resume.ALLOCATIONS)',
        '~$literal_reference_flat_array(S_resume[.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_current))]], n_current, S_resume.ALLOCATIONS)',
        '~$literal_reference_flat_items(S_resume[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ([256])))]], S_resume.ARRAYS[n_current].ITEMS)',
        'S_immutable = S_resume[.ARRAYS[n_payload] = $array_empty()][.GC.IMMUTABLE = S_resume.GC.IMMUTABLE ++ [n_payload]]',
        '$array_immutable(S_immutable, n_payload)', '~$literal_reference_flat_items(S_immutable, S_immutable.ARRAYS[n_current].ITEMS)',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 1) = (DIRECT (PARRAY n_current))',
        'S_insert.LITERALARRAYRETAINED = [n_old]', 'S_insert.LITERALARRAYDEBTS = [n_current]',
        '$heap_owners($heap_graph(S_insert), HARRAY n_current) = 2',
        '$heap_owners($heap_graph(S_insert), HARRAY n_payload) = 2',
    ] + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
        'S_read.STORE[n_q] = DEFINED (PARRAY n_current)',
        children('S_read', 'n_current', read_children, 55),
        payload('S_read', 'n_live', 66), payload('S_read', 'n_payload', 44), 'n_live =/= n_payload',
        '$node_children(S_read, HARRAY n_current) = [' + ', '.join('HARRAY '+n for n in read_children) + ']',
        'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_current]',
        'H_read = $heap_graph(S_read)', '$heap_owners(H_read, HARRAY n_current) = 1',
        '$heap_owners(H_read[.DEBTS = eps], HARRAY n_current) = 2',
        '$heap_owners(H_read, HARRAY n_live) = 1', '$heap_owners(H_read, HARRAY n_payload) = 1',
        'H_logical = $heap_prune(H_read[.DEBTS = eps])', 'H_biased = $heap_prune(H_read)',
        'H_biased.NODES = H_logical.NODES', 'H_biased.EDGES = H_logical.EDGES',
        '$literal_reference_flat_array(S_read, n_current, H_logical.NODES)', '$literal_reference_debt_safe(S_read, H_read)',
    ]
    if not repeated:
        checks += ['S_read.STORE[n_snapshot] = DEFINED (PARRAY n_payload)']
    checks += seek('S_read', 30, 'S_inverse') + [
        '$array_float_array_key_plan(S_inverse) = ((n_balance, n_current, poperand_inverse, eps, 19, n_inverse_bits, 3))',
    ] + seek('S_inverse', 31, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_inverse*',
        '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = (n_old)',
        'PhpStep: S_inverse_resume ~> S_balance',
        'S_balance.LITERALARRAYRETAINED = eps', 'S_balance.LITERALARRAYDEBTS = eps',
        '$entry_lookup(S_balance.ARRAYS[n_balance].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
        '$heap_owners($heap_graph(S_balance), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_balance), HARRAY n_old_payload) = 2',
    ] + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_final') + [
        'S_final.STORE[n_q] = DEFINED (PARRAY n_q_table)', 'n_q_table =/= n_old',
        children('S_final', 'n_q_table', ('n_old_changed',), 99), children('S_final', 'n_old', ('n_old_payload',), 7),
        payload('S_final', 'n_old_changed', 22), payload('S_final', 'n_old_payload', 33),
        'n_old_changed =/= n_old_payload', 'S_final.STORE[n_old_snapshot] = DEFINED (PARRAY n_old_payload)',
        children('S_final', 'n_current', read_children, 55), payload('S_final', 'n_live', 66),
        '$lookup(S_final.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_final.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        '$entry_lookup(S_final.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_current', children('S_final', 'n_copy_child', copied_children, 99 if repeated else 88),
        payload('S_final', 'n_copied', 77), 'n_copied =/= n_live',
        '$heap_owners($heap_graph(S_final), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S_final), HARRAY n_live) = 1', '$heap_owners($heap_graph(S_final), HARRAY n_copied) = 1',
        '$heap_owners($heap_graph(S_final), HARRAY n_old_payload) = 2',
        '$heap_owners($heap_graph(S_final), HARRAY n_old_changed) = 1',
    ]
    if repeated:
        checks += [payload('S_final', 'n_payload', 44), payload('S_final', 'n_copied_second', 88),
                   'n_copied_second =/= n_payload', '$heap_owners($heap_graph(S_final), HARRAY n_payload) = 1',
                   '$heap_owners($heap_graph(S_final), HARRAY n_copied_second) = 1']
    else:
        checks += ['S_final.STORE[n_snapshot] = DEFINED (PARRAY n_payload)', payload('S_final', 'n_payload', 44)]
    checks += [
        '$heap_valid($heap_graph(S_final))', '$call_descriptors_valid(S_final)',
        'S_done = $drive_steps(S_final, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        *[f'~((HARRAY {n}) <- S_done.ALLOCATIONS)' for n in
          ('n_old','n_current','n_builder','n_balance','n_old_payload','n_payload','n_live','n_copied','n_old_changed','n_q_table','n_copy','n_copy_child')],
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 1) = $drive_steps($drive_steps(S_final, 0)[.COMPLETION = NORMAL], 1)',
    ]
    if repeated:
        checks += ['~((HARRAY n_copied_second) <- S_done.ALLOCATIONS)']
    else:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
