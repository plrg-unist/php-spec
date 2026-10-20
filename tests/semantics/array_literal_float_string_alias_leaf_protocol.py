#!/usr/bin/env python3
"""Reached table debt, string reference leaves and copied bytes stay distinct."""
import base64
import json

import array_literal_float_string_alias_leaf_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_protocol import HELPERS as BASE_HELPERS, driven
from array_literal_float_ref_deficit_state_review import seek

HELPERS = BASE_HELPERS + r'''
dec $string_alias_leaf_value(pstate, nat, nat*) : bool
def $string_alias_leaf_value(S, n, n_bytes*) = true
  -- if S.STORE[n] = DEFINED pvalue
  -- if $string_bytes(pvalue) = (n_bytes*)
  -- if $literal_reference_flat_cell(S, n)
  -- if $operand_nodes(KNOWN pvalue) = eps
def $string_alias_leaf_value(S, n, n_bytes*) = false -- otherwise
'''


def aliased(state, table, leaf, value, sibling):
    return [
        f'{state}.ARRAYS[{table}].ITEMS = [ENTRY (KINT 0) (ALIAS {leaf}), ENTRY (KINT 1) (DIRECT (PINT {sibling}))]',
        f'$string_alias_leaf_value({state}, {leaf}, $ptascii({json.dumps(value)}))',
        f'$literal_reference_flat_cell({state}, {leaf})',
        f'~$literal_reference_plain_cell({state}, {leaf})',
        f'$literal_reference_flat_array({state}, {table}, {state}.ALLOCATIONS)',
    ]


def conditions(name, program, path, stdout):
    singleton = name.endswith('singleton')
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_balance n_current poperand_inverse eps 18 n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 30, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', 'z = 12', 'i = 1', 'S.RESULT = poperand',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)',
        'n_q =/= n_hold', 'S.STORE[n_q] = DEFINED (PARRAY n_old)',
        'S.STORE[n_hold] = DEFINED (PARRAY n_old)', '~(n_q <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("old_leaf")) = (n_old_leaf)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_current)', 'n_old =/= n_current',
        '$entry_lookup(S.ARRAYS[n_current].ITEMS, KINT 0) = (ALIAS n_current_leaf)',
        'n_old_leaf =/= n_current_leaf',
        '$lookup(S.ENV, $ptascii("new_leaf")) = ' + ('eps' if singleton else '(n_current_leaf)'),
    ] + aliased('S', 'n_old', 'n_old_leaf', 'old', 7) + aliased('S', 'n_current', 'n_current_leaf', 'new', 8) + [
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S), HCELL n_old_leaf) = 2',
        '$heap_owners($heap_graph(S), HCELL n_current_leaf) = ' + ('1' if singleton else '2'),
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$literal_reference_cell(S, n_current_leaf, S.ALLOCATIONS)',
        '~$array_float_key_scalar(S, PSTRING ($ptascii("cv")))',
        'S_string_cv = S[.STORE[n_q] = DEFINED (PSTRING ($ptascii("cv")))]',
        '$array_float_key_plan(S_string_cv) = eps', '$array_float_array_key_plan(S_string_cv) = eps',
        'S_request = $string_request(S, $ptascii("request"))',
        'S_request.RESULT = KNOWN pvalue_request', '$string_carrier_valid(S_request, pvalue_request)',
        '$literal_reference_flat_cell(S_request[.STORE[n_current_leaf] = DEFINED pvalue_request], n_current_leaf)',
        '$literal_reference_flat_cell(S[.STORE[n_current_leaf] = DEFINED (PSTRING eps)], n_current_leaf)',
        '~$literal_reference_flat_cell(S[.STORE[n_current_leaf] = DEFINED (PSTRING ([256]))], n_current_leaf)',
        '$array_float_array_key_source(S, ' + args + ')',
        '$array_float_array_key_ready(S, n_builder, n_old, poperand)',
        '~$array_float_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_array_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 12',
        '$error_call_valid(S_dispatch, perrorcall)', '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 13])',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old_leaf) = 2',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 32, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_old_leaf, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 31, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.STORE[n_q] = DEFINED (PARRAY n_current)',
        '$array_float_array_key_value(S_resume, poperand) = (n_current)',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_array_key_ready(S_resume, n_builder, n_old, poperand)',
        '$literal_reference_flat_array(S_resume, n_current, [HARRAY n_current, HCELL n_current_leaf])',
        '~$literal_reference_flat_array(S_resume, n_current, [HARRAY n_current])',
        '$entries_nodes(S_resume.ARRAYS[n_current].ITEMS) = [HCELL n_current_leaf]',
        'S_unmarked = S_resume[.REFCELLS = $literal_reference_delete(S_resume.REFCELLS, n_current_leaf)]',
        '~$literal_reference_flat_items(S_unmarked, S_unmarked.ARRAYS[n_current].ITEMS)',
        'S_leaf_debt = S_resume[.LITERALREFDEBTS = [n_current_leaf]]',
        '$array_float_array_key_source(S_leaf_debt, ' + args + ')',
        '~$literal_reference_flat_items(S_leaf_debt, S_leaf_debt.ARRAYS[n_current].ITEMS)',
        '~$array_float_array_key_ready(S_leaf_debt, n_builder, n_old, poperand)',
        '$error_read_discard(S_leaf_debt, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        '~$literal_reference_flat_items(S_resume[.STORE[n_current_leaf] = DEFINED (PARRAY n_builder)], S_resume.ARRAYS[n_current].ITEMS)',
        '~$literal_reference_flat_items(S_resume[.STORE[n_current_leaf] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_resume.STRINGDATA|)) ($ptascii("leaf")))], S_resume.ARRAYS[n_current].ITEMS)',
        '~$literal_reference_flat_items(S_resume[.PROPREFS = [{CELL n_current_leaf, SOURCES eps}]], S_resume.ARRAYS[n_current].ITEMS)',
        'PhpStep: S_resume ~> S_insert',
        'S_insert.STORE = S_resume.STORE',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 1) = (DIRECT (PARRAY n_current))',
        'S_insert.LITERALARRAYRETAINED = [n_old]', 'S_insert.LITERALARRAYDEBTS = [n_current]',
        '$heap_graph(S_insert).DEBTS = [HARRAY n_current]',
        '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S_insert), HARRAY n_current) = 2',
        '$heap_owners($heap_graph(S_insert), HCELL n_current_leaf) = ' + ('1' if singleton else '2'),
    ] + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
        '$lookup(S_read.ENV, $ptascii("snapshot")) = (n_snapshot)',
        'S_read.STORE[n_snapshot] = DEFINED pvalue_snapshot',
        '$string_bytes(pvalue_snapshot) = ($ptascii("new"))',
        '$operand_nodes(KNOWN pvalue_snapshot) = eps',
        'S_read.STORE[n_q] = DEFINED (PARRAY n_current)',
        'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_current]',
        '$heap_owners($heap_graph(S_read), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_current) = 2',
        '$heap_prune($heap_graph(S_read)).NODES = $heap_prune($heap_graph(S_read)[.DEBTS = eps]).NODES',
        '$heap_prune($heap_graph(S_read)).EDGES = $heap_prune($heap_graph(S_read)[.DEBTS = eps]).EDGES',
        '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
    ] + aliased('S_read', 'n_current', 'n_current_leaf', 'New', 55) + seek('S_read', 30, 'S_inverse') + [
        '$array_float_array_key_plan(S_inverse) = ((n_balance, n_current, poperand_inverse, eps, 18, n_inverse_bits, 3))',
        'poperand_inverse = VARIABLE ($ptascii("q")) 18',
    ] + seek('S_inverse', 31, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_inverse*',
        '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = (n_old)',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.LITERALARRAYRETAINED = eps', 'S_balanced.LITERALARRAYDEBTS = eps',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
        '$heap_owners($heap_graph(S_balanced), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_balanced), HARRAY n_current) = 1',
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_final') + [
        'S_final.STORE[n_q] = DEFINED (PARRAY n_q_child)', 'n_q_child =/= n_old',
        '$lookup(S_final.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_final.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_builder',
        '$entry_lookup(S_final.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_current',
        '$heap_owners($heap_graph(S_final), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S_final), HARRAY n_q_child) = 1',
        '$heap_owners($heap_graph(S_final), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S_final), HARRAY n_copy_child) = 1',
        '$heap_owners($heap_graph(S_final), HCELL n_old_leaf) = 3',
        '$heap_owners($heap_graph(S_final), HCELL n_current_leaf) = ' + ('1' if singleton else '3'),
    ] + aliased('S_final', 'n_old', 'n_old_leaf', 'Old', 7) + aliased('S_final', 'n_q_child', 'n_old_leaf', 'Old', 99) + aliased(
        'S_final', 'n_current', 'n_current_leaf', 'New' if singleton else 'NYw', 55)
    if singleton:
        checks += [
            'S_final.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_copy_string), ENTRY (KINT 1) (DIRECT (PINT 77))]',
            '$string_bytes(pvalue_copy_string) = ($ptascii("NYw"))',
            '$literal_reference_flat_leaf(S_final, pvalue_copy_string)',
            '$entries_nodes(S_final.ARRAYS[n_copy_child].ITEMS) = eps',
        ]
    else:
        checks += aliased('S_final', 'n_copy_child', 'n_current_leaf', 'NYw', 77)
    checks += [
        '$call_descriptors_valid(S_final)', '$heap_valid($heap_graph(S_final))',
        'S_final.STORE[n_snapshot] = DEFINED pvalue_snapshot',
        'S_done = $drive_steps(S_final, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        *[f'~((HARRAY {n}) <- S_done.ALLOCATIONS)' for n in
          ('n_old', 'n_current', 'n_builder', 'n_balance', 'n_q_child', 'n_copy', 'n_copy_child')],
        '~((HCELL n_old_leaf) <- S_done.ALLOCATIONS)', '~((HCELL n_current_leaf) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 1) = $drive_steps($drive_steps(S_final, 0)[.COMPLETION = NORMAL], 1)',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
