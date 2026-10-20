#!/usr/bin/env python3
"""Reached outer deficits keep primitive leaf aliases and child COW distinct."""
import base64
import json

import array_literal_float_alias_leaf_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS, seek
from array_literal_float_array_cv_state_review import driven


def items(state, array, first, sibling):
    return (f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) ({first}), '
            f'ENTRY (KINT 1) (DIRECT (PINT {sibling}))]')


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, inverse_line, key = (15, 25, '1') if thrown else (13, 21, '$(-2)')
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3'
    leaf_owners = '3' if thrown else '1'
    copy_first = 'ALIAS n_new_leaf' if thrown else 'DIRECT (PINT 55)'
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
        'S.STORE[n_old_leaf] = DEFINED (PINT 2)', 'S.STORE[n_new_leaf] = DEFINED (PINT 44)',
        'n_old_leaf =/= n_new_leaf', 'n_old <- S.REFCELLS', '~(n_new <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("old_leaf")) = eps',
        '$lookup(S.ENV, $ptascii("new_leaf")) = ' + ('(n_new_leaf)' if thrown else 'eps'),
        '$literal_reference_plain_cell(S, n_old_leaf)', '$literal_reference_plain_cell(S, n_new_leaf)',
        '~$literal_reference_plain_cell(S, n_old)', '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
        '$entries_nodes(S.ARRAYS[n_new_array].ITEMS) = [HCELL n_new_leaf]',
        '$literal_reference_flat_items(S, S.ARRAYS[n_new_array].ITEMS)',
        '$literal_reference_flat_array(S, n_new_array, [HARRAY n_new_array, HCELL n_new_leaf])',
        '~$literal_reference_flat_array(S, n_new_array, [HARRAY n_new_array])',
        '~$literal_reference_flat_array(S[.STORE[n_new_leaf] = UNDEFINED], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.STORE[n_new_leaf] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("invalid")))], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.STORE[n_new_leaf] = DEFINED (PARRAY n_new_array)], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.PROPREFS = [{CELL n_new_leaf, SOURCES eps}]], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.REFCELLS = eps], n_new_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S[.LITERALREFDEBTS = [n_new_leaf]], n_new_array, S.ALLOCATIONS)',
        '$literal_reference_flat_array(S[.ARRAYS[n_new_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("bytes"))))]], n_new_array, [HARRAY n_new_array])',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '~$array_float_ref_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        'H_initial = $heap_graph(S)', '$heap_valid(H_initial)',
        '$heap_owners(H_initial, HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners(H_initial, HARRAY n_old_array) = 1', '$heap_owners(H_initial, HARRAY n_new_array) = 1',
        '$heap_owners(H_initial, HCELL n_old_leaf) = 1',
        '$heap_owners(H_initial, HCELL n_new_leaf) = ' + ('2' if thrown else '1'),
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
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
            '$heap_owners(H_start, HCELL n_new_leaf) = 2',
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
            '$heap_owners(H_insert, HCELL n_new) = 2', '$heap_owners(H_insert, HCELL n_new_leaf) = 1',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("q")) = eps',
        'S_read.LITERALREFRETAINED = [n_old]', 'S_read.LITERALREFDEBTS = [n_new]',
        'S_read.LITERALARRAYRETAINED = eps', 'S_read.LITERALARRAYDEBTS = eps',
        'S_read.STORE[n_old] = DEFINED (PARRAY n_old_array)', 'S_read.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        items('S_read', 'n_old_array', 'ALIAS n_old_leaf', 33), items('S_read', 'n_new_array', 'ALIAS n_new_leaf', 66),
        'S_read.STORE[n_old_leaf] = DEFINED (PINT 2)',
        'S_read.STORE[n_new_leaf] = DEFINED (PINT ' + ('55' if thrown else '44') + ')',
        '$lookup(S_read.ENV, $ptascii("probe")) = (n_probe_cell)', 'S_read.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        'n_probe =/= n_copy', '$entry_lookup(S_read.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
        '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_new_array', items('S_read', 'n_copy_child', copy_first, 88),
        '$lookup(S_read.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S_read.STORE[n_snapshot] = DEFINED (PINT 44)',
        'H_read = $heap_graph(S_read)', 'H_read.DEBTS = [HCELL n_new]',
        '$heap_owners(H_read, HCELL n_new) = 1', '$heap_owners(H_read[.DEBTS = eps], HCELL n_new) = 2',
        '$heap_owners(H_read, HCELL n_old) = 2', '$heap_owners(H_read, HCELL n_old_leaf) = 1',
        '$heap_owners(H_read, HCELL n_new_leaf) = ' + leaf_owners,
        '$heap_owners(H_read, HARRAY n_new_array) = 1', '$heap_owners(H_read, HARRAY n_copy_child) = 1',
        'H_logical = $heap_prune(H_read[.DEBTS = eps])', 'H_biased = $heap_prune(H_read)',
        'H_biased.NODES = H_logical.NODES', 'H_biased.EDGES = H_logical.EDGES',
        '(HCELL n_new_leaf) <- H_logical.NODES',
        '$heap_owners(H_biased, HCELL n_new_leaf) = ' + leaf_owners,
        '$literal_reference_flat_array(S_read, n_new_array, H_logical.NODES)',
        '$literal_reference_cell(S_read, n_new, H_logical.NODES)', '$literal_reference_debt_safe(S_read, H_read)',
        '$heap_valid(H_read)', '$call_descriptors_valid(S_read)',
    ] + seek('S_read', 10, 'S_inverse') + [
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
        '$heap_owners(H_balance, HCELL n_old) = 3', '$heap_owners(H_balance, HCELL n_new_leaf) = ' + leaf_owners,
    ] + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        'S_shared.LITERALARRAYRETAINED = eps', 'S_shared.LITERALARRAYDEBTS = eps',
        'S_shared.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        items('S_shared', 'n_new_array', 'ALIAS n_new_leaf', 99), items('S_shared', 'n_copy_child', copy_first, 88),
        'S_shared.STORE[n_new_leaf] = DEFINED (PINT 77)', 'S_shared.STORE[n_old_leaf] = DEFINED (PINT 2)',
        '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_probe',
        '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 0) = (ALIAS n_new)',
        'S_shared.STORE[n_snapshot] = DEFINED (PINT 44)', 'H_shared = $heap_graph(S_shared)',
        '$heap_owners(H_shared, HCELL n_new) = 3', '$heap_owners(H_shared, HCELL n_old) = 3',
        '$heap_owners(H_shared, HCELL n_new_leaf) = ' + leaf_owners,
        '$heap_owners(H_shared, HARRAY n_new_array) = 1', '$heap_owners(H_shared, HARRAY n_copy_child) = 1',
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
    ]
    for node in ('HCELL n_old', 'HCELL n_new', 'HCELL n_old_leaf', 'HCELL n_new_leaf',
                 'HARRAY n_old_array', 'HARRAY n_new_array', 'HARRAY n_builder', 'HARRAY n_balance',
                 'HARRAY n_probe', 'HARRAY n_copy', 'HARRAY n_copy_child', 'HARRAY n_shared'):
        checks.append(f'~(({node}) <- S_done.ALLOCATIONS)')
    checks += [
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("replacement")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        '$drive_steps(S_shared, 1) = $drive_steps($drive_steps(S_shared, 0)[.COMPLETION = NORMAL], 1)',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
