#!/usr/bin/env python3
"""Typed outer CELL counts control unwrapping, constraints and child ownership."""
import base64
import json

import array_literal_float_typed_array_ref_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_types_state_review import HELPERS
from array_literal_float_ref_deficit_state_review import seek
from array_literal_float_typed_alias_leaf_state_review import driven, items
from array_literal_float_array_alias_leaf_state_review import child


def typed_sources(state, owners):
    sources = [f'OBJECT_PROP_SOURCE n_{name} ($ptascii("slot")) porigin_{name}' for name in owners]
    checks = [f'$propref_at({state}.PROPREFS, n_new) = (ppropref_new)',
              'ppropref_new.SOURCES = [' + ', '.join(sources) + ']',
              f'$propref_sources_valid({state}, n_new, ppropref_new.SOURCES)']
    for name, source in zip(owners, sources):
        checks += [
            f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{name}_cell)',
            f'{state}.STORE[n_{name}_cell] = DEFINED (POBJECT n_{name})',
            f'$node_children({state}, HOBJECT n_{name}) = [HCELL n_new]',
            f'$propref_descriptor({state}, {source}) = (ppropertydesc_{name})',
            f'ppropertydesc_{name}.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]',
        ]
    return checks


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, inverse_line, key = (17, 30, '1') if thrown else (15, 23, '$(-2)')
    owners = ('left', 'right') if thrown else ('box',)
    live_objects = ', '.join('HOBJECT n_' + name for name in owners)
    live = '[HCELL n_new, HARRAY n_new_array, HARRAY n_new_payload, ' + live_objects + ']'
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3'
    read_owners, balanced_owners, shared_owners = (3, 4, 5) if thrown else (1, 2, 3)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        f'z = {line}', f'i = {key}', 'poperand = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)', 'n_old =/= n_new',
        'S.STORE[n_old] = DEFINED (PARRAY n_old_array)', 'S.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        'n_old_array =/= n_new_array',
        items('S', 'n_old_array', 'DIRECT (PARRAY n_old_payload)', 7),
        items('S', 'n_new_array', 'DIRECT (PARRAY n_new_payload)', 8),
        child('S', 'n_old_payload', 2), child('S', 'n_new_payload', 44),
        'n_old_payload =/= n_new_payload',
        '$lookup(S.ENV, $ptascii("old_child")) = eps', '$lookup(S.ENV, $ptascii("new_child")) = eps',
        'n_old <- S.REFCELLS', 'n_new <- S.REFCELLS',
        '$propref_at(S.PROPREFS, n_old) = eps',
        '$node_children(S, HCELL n_new) = [HARRAY n_new_array]',
        '$node_children(S, HARRAY n_new_array) = [HARRAY n_new_payload]',
        '$node_children(S, HARRAY n_new_payload) = eps',
        '~$literal_reference_plain_cell(S, n_new)', '~$literal_reference_flat_cell(S, n_new)',
        '$literal_reference_cell(S, n_new, S.ALLOCATIONS)',
        '$literal_reference_cell(S, n_new, ' + live + ')',
        '~$literal_reference_cell(S, n_new, [HCELL n_new, HARRAY n_new_array, HARRAY n_new_payload])',
        '~$literal_reference_cell(S, n_new, [HCELL n_new, ' + live_objects + '])',
        '~$literal_reference_cell(S, n_new, [HCELL n_new, HARRAY n_new_array, ' + live_objects + '])',
        '$literal_reference_flat_array(S, n_new_array, [HARRAY n_new_array, HARRAY n_new_payload])',
        '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
    ] + typed_sources('S', owners) + [
        '~$literal_reference_cell(S[.STORE[n_new] = DEFINED (PINT 55)], n_new, S.ALLOCATIONS)',
        '~$literal_reference_cell(S[.STORE[n_new] = DEFINED (PSTRING ($ptascii("text")))], n_new, S.ALLOCATIONS)',
        'S_duplicate = S[.PROPREFS = [ppropref_new[.SOURCES = ppropref_new.SOURCES ++ ppropref_new.SOURCES]]]',
        '~$literal_reference_cell(S_duplicate, n_new, S_duplicate.ALLOCATIONS)',
        '~$literal_reference_cell(S[.PROPREFS = [{CELL n_new, SOURCES eps}]], n_new, S.ALLOCATIONS)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$array_float_ref_key_source(S, ' + args + ')',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        'H_initial = $heap_graph(S)', '$heap_valid(H_initial)',
        '$heap_owners(H_initial, HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners(H_initial, HCELL n_new) = ' + ('3' if thrown else '2'),
        '$heap_owners(H_initial, HARRAY n_old_array) = 1', '$heap_owners(H_initial, HARRAY n_new_array) = 1',
        '$heap_owners(H_initial, HARRAY n_old_payload) = 1', '$heap_owners(H_initial, HARRAY n_new_payload) = 1',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = ' + ('4' if thrown else '3'),
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_new_payload) = 1',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_new_payload, $tasks_nodes(pframe.TODO)) = 0',
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
            '$heap_owners($heap_graph(S_start), HCELL n_new) = 3',
            '$literal_reference_debt_safe(S_start, $heap_graph(S_start))',
        ]
    else:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)',
            '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT $(-2)) = (ALIAS n_new)',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
            '$heap_owners($heap_graph(S_insert), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HCELL n_new) = 3',
            '$heap_owners($heap_graph(S_insert), HARRAY n_new_payload) = 1',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("q")) = eps', '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
        'S_read.PROPREFS = S.PROPREFS',
        'S_read.LITERALREFRETAINED = [n_old]', 'S_read.LITERALREFDEBTS = [n_new]',
        'S_read.LITERALARRAYRETAINED = eps', 'S_read.LITERALARRAYDEBTS = eps',
        'S_read.STORE[n_old] = DEFINED (PARRAY n_old_array)', 'S_read.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        items('S_read', 'n_old_array', 'DIRECT (PARRAY n_old_payload)', 33),
        items('S_read', 'n_new_array', 'DIRECT (PARRAY n_live_payload)', 66),
        child('S_read', 'n_old_payload', 2), child('S_read', 'n_new_payload', 44), child('S_read', 'n_live_payload', 66),
        'n_live_payload =/= n_new_payload',
        '$lookup(S_read.ENV, $ptascii("probe")) = (n_probe_cell)', 'S_read.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        'n_probe =/= n_copy', '$entry_lookup(S_read.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
    ]
    if thrown:
        checks += [
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 0) = (ALIAS n_new)',
            '$lookup(S_read.ENV, $ptascii("detached")) = (n_detached_cell)',
            'S_read.STORE[n_detached_cell] = DEFINED (PARRAY n_copy_child)',
        ]
    else:
        checks += [
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_child))',
            '$lookup(S_read.ENV, $ptascii("free")) = (n_free_cell)', 'S_read.STORE[n_free_cell] = DEFINED (PARRAY n_free)',
            'S_read.ARRAYS[n_free].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 99))]',
        ]
    checks += [
        'n_copy_child =/= n_new_array', items('S_read', 'n_copy_child', 'DIRECT (PARRAY n_copy_payload)', 88),
        'n_copy_payload =/= n_live_payload', 'n_copy_payload =/= n_new_payload', child('S_read', 'n_copy_payload', 55),
        '$lookup(S_read.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S_read.STORE[n_snapshot] = DEFINED (PARRAY n_new_payload)',
        'H_read = $heap_graph(S_read)', 'H_read.DEBTS = [HCELL n_new]',
        f'$heap_owners(H_read, HCELL n_new) = {read_owners}',
        f'$heap_owners(H_read[.DEBTS = eps], HCELL n_new) = {read_owners+1}',
        '$heap_owners(H_read, HCELL n_old) = 2',
        '$heap_owners(H_read, HARRAY n_new_array) = 1', '$heap_owners(H_read, HARRAY n_copy_child) = 1',
        '$heap_owners(H_read, HARRAY n_old_payload) = 1', '$heap_owners(H_read, HARRAY n_new_payload) = 1',
        '$heap_owners(H_read, HARRAY n_live_payload) = 1', '$heap_owners(H_read, HARRAY n_copy_payload) = 1',
        'H_logical = $heap_prune(H_read[.DEBTS = eps])', 'H_biased = $heap_prune(H_read)',
        'H_biased.NODES = H_logical.NODES', 'H_biased.EDGES = H_logical.EDGES',
        '$literal_reference_cell(S_read, n_new, H_logical.NODES)', '$literal_reference_debt_safe(S_read, H_read)',
        '$propref_sources_valid(S_read, n_new, ppropref_new.SOURCES)',
        '$heap_valid(H_read)', '$call_descriptors_valid(S_read)', '$class_state_valid(S_read)',
    ]
    if thrown:
        checks += [
            'H_unrooted = H_read[.ROOTS = $literal_types_remove(H_read.ROOTS, HCELL n_right_cell)]',
            '$heap_valid(H_unrooted)', 'H_missing = $heap_prune(H_unrooted[.DEBTS = eps])',
            '(HOBJECT n_left) <- H_missing.NODES', '~((HOBJECT n_right) <- H_missing.NODES)',
            '(HCELL n_new) <- H_missing.NODES', '(HARRAY n_new_array) <- H_missing.NODES',
            '(HARRAY n_live_payload) <- H_missing.NODES', '$heap_owners(H_missing, HCELL n_new) = 3',
            '$literal_reference_flat_array(S_read, n_new_array, H_missing.NODES)',
            '~$literal_reference_cell(S_read, n_new, H_missing.NODES)',
            '~$literal_reference_debt_safe(S_read, H_unrooted)',
        ]
    checks += seek('S_read', 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        f'$heap_owners($heap_graph(S_inverse), HCELL n_new) = {read_owners+1}',
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse, '$error_call_valid(S_inverse_dispatch, perrorcall_inverse)',
    ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_after_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S_inverse_resume, n_balance, n_new, poperand_inverse)',
        'PhpStep: S_inverse_resume ~> S_balance',
        'S_balance.LITERALREFRETAINED = eps', 'S_balance.LITERALREFDEBTS = eps',
        '$entry_lookup(S_balance.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        f'$heap_owners($heap_graph(S_balance), HCELL n_new) = {balanced_owners}',
        '$heap_owners($heap_graph(S_balance), HCELL n_old) = 3',
    ] + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_shared') + [
        'S_shared.PROPREFS = S.PROPREFS',
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        'S_shared.LITERALARRAYRETAINED = eps', 'S_shared.LITERALARRAYDEBTS = eps',
        'S_shared.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        items('S_shared', 'n_new_array', 'DIRECT (PARRAY n_live_payload)', 99),
        items('S_shared', 'n_copy_child', 'DIRECT (PARRAY n_copy_payload)', 88),
        child('S_shared', 'n_live_payload', 77), child('S_shared', 'n_copy_payload', 55),
        child('S_shared', 'n_old_payload', 2), child('S_shared', 'n_new_payload', 44),
        '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)',
        '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 0) = (ALIAS n_new)',
        f'$heap_owners($heap_graph(S_shared), HCELL n_new) = {shared_owners}',
        '$heap_owners($heap_graph(S_shared), HCELL n_old) = 3',
        '$propref_sources_valid(S_shared, n_new, ppropref_new.SOURCES)',
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        '$propref_at(S_done.PROPREFS, n_new) = eps',
    ]
    nodes = ['HCELL n_old', 'HCELL n_new', 'HARRAY n_old_array', 'HARRAY n_new_array',
             'HARRAY n_builder', 'HARRAY n_balance', 'HARRAY n_probe', 'HARRAY n_copy', 'HARRAY n_shared',
             'HARRAY n_copy_child', 'HARRAY n_old_payload', 'HARRAY n_new_payload',
             'HARRAY n_live_payload', 'HARRAY n_copy_payload']
    nodes += ['HOBJECT n_' + name for name in owners]
    if not thrown:
        checks += ['S_shared.ARRAYS[n_free].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 99))]']
        nodes += ['HARRAY n_free']
    checks += [f'~(({node}) <- S_done.ALLOCATIONS)' for node in nodes]
    checks += [
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("replacement")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        '$drive_steps(S_shared, 1) = $drive_steps($drive_steps(S_shared, 0)[.COMPLETION = NORMAL], 1)',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
