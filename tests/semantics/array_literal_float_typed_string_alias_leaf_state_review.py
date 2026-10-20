#!/usr/bin/env python3
"""Typed string leaves share byte writes independently of outer count biases."""
import base64
import json

import array_literal_float_typed_string_alias_leaf_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import seek
from array_literal_float_ref_types_state_review import HELPERS as BASE_HELPERS
from array_literal_float_array_cv_state_review import driven as base_driven


HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 17) = $literal_deficit_review_echo(S, $ptascii("X:"))
'''


def string_cell(state, cell, tag, text):
    return [f'{state}.STORE[{cell}] = DEFINED pvalue_{tag}',
            f'$string_bytes(pvalue_{tag}) = ($ptascii("{text}"))']


def items(state, array, first, sibling):
    return (f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) ({first}), '
            f'ENTRY (KINT 1) (DIRECT (PINT {sibling}))]')


def driven(start, raw, result):
    return base_driven(start, raw, result) + [f'{result}.PROPREFS = {raw}.PROPREFS']


def typed_sources(state):
    return [
        f'$lookup({state}.ENV, $ptascii("left")) = (n_left_cell)',
        f'$lookup({state}.ENV, $ptascii("right")) = (n_right_cell)',
        f'{state}.STORE[n_left_cell] = DEFINED (POBJECT n_left)',
        f'{state}.STORE[n_right_cell] = DEFINED (POBJECT n_right)',
        'n_left =/= n_right',
        f'$propref_at({state}.PROPREFS, n_new_leaf) = (ppropref_leaf)',
        'ppropref_leaf.SOURCES = [OBJECT_PROP_SOURCE n_left ($ptascii("slot")) porigin_left, OBJECT_PROP_SOURCE n_right ($ptascii("slot")) porigin_right]',
        f'$propref_sources_valid({state}, n_new_leaf, ppropref_leaf.SOURCES)',
        f'(HOBJECT n_left) <- {state}.ALLOCATIONS',
        f'(HOBJECT n_right) <- {state}.ALLOCATIONS',
    ]


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, inverse_line, key = (17, 31, '1') if thrown else (15, 26, '$(-2)')
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps', 'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        f'z = {line}', f'i = {key}', 'poperand = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)', 'n_old =/= n_new',
        'S.STORE[n_old] = DEFINED (PARRAY n_old_array)', 'S.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        'n_old_array =/= n_new_array',
        items('S', 'n_old_array', 'ALIAS n_old_leaf', 7), items('S', 'n_new_array', 'ALIAS n_new_leaf', 8),
        'S.STORE[n_old_leaf] = DEFINED (PINT 2)',
    ] + string_cell('S', 'n_new_leaf', 'initial_leaf', 'new') + [
        'n_old_leaf =/= n_new_leaf', 'n_old <- S.REFCELLS', '~(n_new <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("old_leaf")) = eps',
        '$lookup(S.ENV, $ptascii("leaf")) = eps',
        '$literal_reference_plain_cell(S, n_old_leaf)', '~$literal_reference_plain_cell(S, n_new_leaf)',
        '$literal_reference_flat_cell(S, n_new_leaf)',
        '~$literal_reference_cell(S, n_new_leaf, S.ALLOCATIONS)',
        '~$literal_reference_plain_cell(S, n_old)', '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
        '$entries_nodes(S.ARRAYS[n_new_array].ITEMS) = [HCELL n_new_leaf]',
        '$literal_reference_flat_items(S, S.ARRAYS[n_new_array].ITEMS)',
        '$literal_reference_flat_array(S, n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S, n_new_array, [HARRAY n_new_array, HCELL n_new_leaf])',
        '~$literal_reference_flat_array(S[.STORE[n_new_leaf] = UNDEFINED], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_cell(S[.STORE[n_new_leaf] = DEFINED (PINT 55)], n_new_leaf)',
        '~$literal_reference_flat_cell(S[.STORE[n_new_leaf] = DEFINED (PSTRING ([256]))], n_new_leaf)',
        '~$literal_reference_flat_array(S[.STORE[n_new_leaf] = DEFINED (PARRAY n_new_array)], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.PROPREFS = [{CELL n_new_leaf, SOURCES eps}]], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.REFCELLS = eps], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.LITERALREFDEBTS = [n_new_leaf]], n_new_array, S.ALLOCATIONS)',
    ] + typed_sources('S') + [
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("new")]][.STORE[n_new_leaf] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("new")))]',
        '$literal_reference_flat_cell(S_request, n_new_leaf)',
        '~$literal_reference_cell(S_request, n_new_leaf, S_request.ALLOCATIONS)',
        '~$literal_reference_flat_cell(S[.STORE[n_new_leaf] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("new")))], n_new_leaf)',
        'S_duplicate = S[.PROPREFS = [ppropref_leaf[.SOURCES = ppropref_leaf.SOURCES ++ ppropref_leaf.SOURCES]]]',
        '~$literal_reference_flat_cell(S_duplicate, n_new_leaf)',
        '$literal_reference_flat_array(S, n_new_array, [HARRAY n_new_array, HCELL n_new_leaf, HOBJECT n_left, HOBJECT n_right])',
        '$literal_reference_flat_sources(S, S.ARRAYS[n_new_array].ITEMS, [HOBJECT n_left, HOBJECT n_right])',
        '~$literal_reference_flat_sources(S, S.ARRAYS[n_new_array].ITEMS, [HOBJECT n_left])',
        '~$literal_reference_flat_array(S, n_new_array, [HARRAY n_new_array, HCELL n_new_leaf, HOBJECT n_left])',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$array_float_ref_key_source(S, ' + args + ')',
        'H_initial = $heap_graph(S)', '$heap_valid(H_initial)',
        '$heap_owners(H_initial, HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners(H_initial, HARRAY n_old_array) = 1', '$heap_owners(H_initial, HARRAY n_new_array) = 1',
        '$heap_owners(H_initial, HCELL n_old_leaf) = 1',
        '$heap_owners(H_initial, HCELL n_new_leaf) = 3',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        'H_dispatch = $heap_graph(S_dispatch)',
        '$heap_owners(H_dispatch, HCELL n_old) = ' + ('4' if thrown else '3'),
        '$heap_owners(H_dispatch, HARRAY n_old_array) = 1', '$heap_owners(H_dispatch, HCELL n_old_leaf) = 1',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_old_leaf, $tasks_nodes(pframe.TODO)) = 0',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (ALIAS n_old)]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', '$lookup(S.ENV, $ptascii("later")) = (n_later)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps', 'S_start.ERRORHANDLER = S.ERRORHANDLER',
            'S_start.STORE[n_dest] = DEFINED (PINT 99)', 'S_start.STORE[n_later] = DEFINED (PINT 7)',
            '~((HARRAY n_builder) <- S_start.ALLOCATIONS)',
            'S_start.LITERALREFRETAINED = [n_old]', 'S_start.LITERALREFDEBTS = [n_new]',
            'H_start = $heap_graph(S_start)', '$heap_owners(H_start, HCELL n_new) = 1',
            '$heap_owners(H_start, HCELL n_new_leaf) = 3',
            '$literal_reference_debt_safe(S_start, H_start)',
        ]
    else:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_resume.REFCELLS',
            '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            items('S_resume', 'n_old_array', 'ALIAS n_old_leaf', 33),
            'PhpStep: S_resume ~> S_insert',
            'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT $(-2)) = (ALIAS n_new)',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
            'H_insert = $heap_graph(S_insert)', '$heap_owners(H_insert, HCELL n_old) = 2',
            '$heap_owners(H_insert, HCELL n_new) = 2', '$heap_owners(H_insert, HCELL n_new_leaf) = 3',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 17, 'S_x') + [
        '$lookup(S_x.ENV, $ptascii("q")) = eps',
        'S_x.LITERALREFRETAINED = [n_old]', 'S_x.LITERALREFDEBTS = [n_new]',
        'S_x.LITERALARRAYRETAINED = eps', 'S_x.LITERALARRAYDEBTS = eps',
        'S_x.STORE[n_old] = DEFINED (PARRAY n_old_array)', 'S_x.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        items('S_x', 'n_old_array', 'ALIAS n_old_leaf', 33), items('S_x', 'n_new_array', 'ALIAS n_new_leaf', 66),
        'S_x.STORE[n_old_leaf] = DEFINED (PINT 2)',
        '$lookup(S_x.ENV, $ptascii("probe")) = (n_probe_cell)', 'S_x.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
        '$lookup(S_x.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_x.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        'n_probe =/= n_copy', '$entry_lookup(S_x.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
        '$entry_lookup(S_x.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_new_array', items('S_x', 'n_copy_child', 'ALIAS n_new_leaf', 88),
        '$lookup(S_x.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S_x.STORE[n_snapshot] = DEFINED pvalue_snapshot', '$string_bytes(pvalue_snapshot) = ($ptascii("new"))',
        'H_x = $heap_graph(S_x)', 'H_x.DEBTS = [HCELL n_new]',
        '$heap_owners(H_x, HCELL n_new) = 1', '$heap_owners(H_x[.DEBTS = eps], HCELL n_new) = 2',
        '$heap_owners(H_x, HCELL n_old) = 2', '$heap_owners(H_x, HCELL n_old_leaf) = 1',
        '$heap_owners(H_x, HCELL n_new_leaf) = 4',
        '$heap_owners(H_x, HARRAY n_new_array) = 1', '$heap_owners(H_x, HARRAY n_copy_child) = 1',
        '$node_children(S_x, HCELL n_new_leaf) = eps',
        '$literal_reference_flat_array(S_x, n_new_array, S_x.ALLOCATIONS)',
        '$literal_reference_cell(S_x, n_new, S_x.ALLOCATIONS)', '$literal_reference_debt_safe(S_x, H_x)',
        '(HEDGE (HOBJECT n_left) (HCELL n_new_leaf)) <- H_x.EDGES',
        '(HEDGE (HOBJECT n_right) (HCELL n_new_leaf)) <- H_x.EDGES',
        '$heap_valid(H_x)', '$call_descriptors_valid(S_x)', '$class_state_valid(S_x)',
        '$lookup(S_x.ENV, $ptascii("e")) = eps',
        '$lookup(S_x.ENV, $ptascii("write_error")) = eps',
        'S_x.PROPREFS = S.PROPREFS',
        '$propref_sources_valid(S_x, n_new_leaf, ppropref_leaf.SOURCES)',
    ]
    checks += string_cell('S_x', 'n_new_leaf', 'x_leaf', 'Xew')
    checks += seek('S_x', 15, 'S_read') + string_cell('S_read', 'n_new_leaf', 'read_leaf', 'New') + [
        'S_read.STORE[n_snapshot] = DEFINED pvalue_snapshot',
        'S_read.ARRAYS = S_x.ARRAYS', 'S_read.PROPREFS = S_x.PROPREFS',
        'S_read.LITERALREFRETAINED = [n_old]', 'S_read.LITERALREFDEBTS = [n_new]',
    ]
    checks += seek('S_read', 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        '$heap_owners($heap_graph(S_inverse), HCELL n_new) = 2',
        'S_inverse.LITERALREFRETAINED = [n_old]', 'S_inverse.LITERALREFDEBTS = [n_new]',
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse, '$error_call_valid(S_inverse_dispatch, perrorcall_inverse)',
        '$heap_owners($heap_graph(S_inverse_dispatch), HCELL n_new) = 3',
    ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_after_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S_inverse_resume, n_balance, n_new, poperand_inverse)',
        'PhpStep: S_inverse_resume ~> S_balance',
        'S_balance.LITERALREFRETAINED = eps', 'S_balance.LITERALREFDEBTS = eps',
        '$entry_lookup(S_balance.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        'H_balance = $heap_graph(S_balance)', '$heap_owners(H_balance, HCELL n_new) = 2',
        '$heap_owners(H_balance, HCELL n_old) = 3', '$heap_owners(H_balance, HCELL n_new_leaf) = 4',
    ] + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        'S_shared.LITERALARRAYRETAINED = eps', 'S_shared.LITERALARRAYDEBTS = eps',
        'S_shared.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        items('S_shared', 'n_new_array', 'ALIAS n_new_leaf', 99), items('S_shared', 'n_copy_child', 'ALIAS n_new_leaf', 88),
        'S_shared.STORE[n_old_leaf] = DEFINED (PINT 2)',
        '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_probe',
        '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 0) = (ALIAS n_new)',
        'S_shared.STORE[n_snapshot] = DEFINED pvalue_snapshot', 'H_shared = $heap_graph(S_shared)',
        '$heap_owners(H_shared, HCELL n_new) = 3', '$heap_owners(H_shared, HCELL n_old) = 3',
        '$heap_owners(H_shared, HCELL n_new_leaf) = 4',
        '$heap_owners(H_shared, HARRAY n_new_array) = 1', '$heap_owners(H_shared, HARRAY n_copy_child) = 1',
        'S_shared.PROPREFS = S.PROPREFS',
        '$propref_sources_valid(S_shared, n_new_leaf, ppropref_leaf.SOURCES)',
    ] + string_cell('S_shared', 'n_new_leaf', 'shared_leaf', 'NYw') + [
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps', 'S_done.PROPREFS = eps',
    ]
    for node in ('HCELL n_old', 'HCELL n_new', 'HCELL n_old_leaf', 'HCELL n_new_leaf',
                 'HARRAY n_old_array', 'HARRAY n_new_array', 'HARRAY n_builder', 'HARRAY n_balance',
                 'HARRAY n_probe', 'HARRAY n_copy', 'HARRAY n_copy_child', 'HARRAY n_shared',
                 'HOBJECT n_left', 'HOBJECT n_right'):
        checks.append(f'~(({node}) <- S_done.ALLOCATIONS)')
    checks += [
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("replacement")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        '$drive_steps(S_shared, 1) = $drive_steps($drive_steps(S_shared, 0)[.COMPLETION = NORMAL], 1)',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
