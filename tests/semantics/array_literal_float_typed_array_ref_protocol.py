#!/usr/bin/env python3
"""Typed outer wrappers shed constraints only in copies or after source removal."""
import base64
import json

import array_literal_float_typed_array_ref_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS as REF_HELPERS, seek, driven
from array_literal_float_ref_arrays_protocol import payload

HELPERS = REF_HELPERS + r'''
def $list_warning_frontier(S, 17) = $literal_deficit_review_echo(S, $ptascii("X:"))
'''


def conditions(name, program, path, stdout):
    detached = name.endswith('unset-source')
    line, inverse_line = (15, 21) if detached else (14, 22)
    box_name = 'newbox' if detached else 'box'
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', 'i = 1',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        'n_old <- S.REFCELLS', 'S.STORE[n_old] = DEFINED (PARRAY n_old_array)', payload('S', 'n_old_array', 2),
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)', 'n_new =/= n_old', 'n_new <- S.REFCELLS',
        'S.STORE[n_new] = DEFINED (PARRAY n_new_array)', payload('S', 'n_new_array', 44),
        '$lookup(S.ENV, $ptascii("' + box_name + '")) = (n_box_cell)', 'S.STORE[n_box_cell] = DEFINED (POBJECT n_box)',
        '$propref_at(S.PROPREFS, n_new) = (ppropref_new)',
        'ppropref_new.SOURCES = [OBJECT_PROP_SOURCE n_box ($ptascii("slot")) porigin_new_property]',
        '$propref_sources_valid(S, n_new, ppropref_new.SOURCES)',
        '~$literal_reference_plain_cell(S, n_new)', '$literal_reference_cell(S, n_new, S.ALLOCATIONS)',
        '$literal_reference_cell(S, n_new, [HCELL n_new, HARRAY n_new_array, HOBJECT n_box])',
        '~$literal_reference_cell(S, n_new, [HCELL n_new, HOBJECT n_box])',
        '~$literal_reference_cell(S, n_new, [HCELL n_new, HARRAY n_new_array])',
        '~$literal_reference_cell(S[.STORE[n_new] = DEFINED (PINT 99)], n_new, S.ALLOCATIONS)',
        '~$literal_reference_cell(S[.STORE[n_new] = DEFINED (PSTRING ($ptascii("text")))], n_new, S.ALLOCATIONS)',
        '~$literal_reference_cell(S[.PROPREFS = [{CELL n_new, SOURCES eps}]], n_new, S.ALLOCATIONS)',
        '~$literal_reference_cell(S[.PROPREFS = [ppropref_new[.SOURCES = ppropref_new.SOURCES ++ ppropref_new.SOURCES]]], n_new, S.ALLOCATIONS)',
        '$heap_owners($heap_graph(S), HCELL n_old) = ' + ('3' if detached else '2'),
        '$heap_owners($heap_graph(S), HCELL n_new) = 2', '$heap_owners($heap_graph(S), HARRAY n_new_array) = 1',
        '$node_children(S, HCELL n_new) = [HARRAY n_new_array]',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        '$array_float_ref_key_source(S, ' + args + ')', '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
    ]
    if detached:
        checks += [
            '$lookup(S.ENV, $ptascii("oldbox")) = (n_old_box_cell)', 'S.STORE[n_old_box_cell] = DEFINED (POBJECT n_old_box)',
            '$propref_at(S.PROPREFS, n_old) = (ppropref_old)',
            'ppropref_old.SOURCES = [OBJECT_PROP_SOURCE n_old_box ($ptascii("slot")) porigin_old_property]',
            '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
            '$lookup(S.ENV, $ptascii("old_snapshot")) = (n_old_snapshot)',
            'S.STORE[n_old_snapshot] = DEFINED (PARRAY n_old_array)', '$heap_owners($heap_graph(S), HARRAY n_old_array) = 2',
        ]
    else:
        checks += ['$propref_at(S.PROPREFS, n_old) = eps', '$heap_owners($heap_graph(S), HARRAY n_old_array) = 1']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)', '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = ' + ('4' if detached else '3'),
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old_array) = ' + ('2' if detached else '1'),
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_old_array, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)',
        'S_resume.STORE[n_old] = DEFINED (PARRAY n_old_live)', payload('S_resume', 'n_old_live', 33),
        'S_resume.STORE[n_new] = DEFINED (PARRAY n_new_array)', payload('S_resume', 'n_new_array', 44),
        'S_resume.PROPREFS = S.PROPREFS', '$literal_reference_cell(S_resume, n_new, S_resume.ALLOCATIONS)',
        '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
        'S_builder = S_resume[.STORE[n_new] = DEFINED (PARRAY n_builder)]',
        '$array_float_ref_key_source(S_builder, ' + args + ')',
        '$literal_reference_cell(S_builder, n_new, S_builder.ALLOCATIONS)',
        '$array_float_ref_key_value(S_builder, n_old, poperand) = (ALIAS n_new)',
        '$array_float_ref_key_builder_alias(S_builder, n_builder, ALIAS n_new)',
        '~$array_float_ref_key_ready(S_builder, n_builder, n_old, poperand)',
        '$error_read_discard(S_builder, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
        'PhpStep: S_resume ~> S_insert',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
        'S_insert.LITERALARRAYRETAINED = eps', 'S_insert.LITERALARRAYDEBTS = eps',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 1) = (ALIAS n_new)',
        '$heap_owners($heap_graph(S_insert), HCELL n_new) = 3',
        '$heap_owners($heap_graph(S_insert)[.DEBTS = eps], HCELL n_new) = 4',
        '$heap_owners($heap_graph(S_insert), HARRAY n_new_array) = 1',
        '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
    ]
    if detached:
        checks += ['n_old_live =/= n_old_array', payload('S_resume', 'n_old_array', 2)]
    else:
        checks += [
            'n_old_live = n_old_array', 'S_insert.GLOBALTABLE = eps',
            'S_lost = $unset_name(S_insert, $ptascii("box"))',
            'H_lost = $heap_graph(S_lost)', '$heap_valid(H_lost[.DEBTS = eps])',
            'H_live = $heap_prune(H_lost[.DEBTS = eps])',
            '~((HOBJECT n_box) <- H_live.NODES)', '(HCELL n_new) <- H_live.NODES', '(HARRAY n_new_array) <- H_live.NODES',
            '$heap_owners(H_live, HCELL n_new) = 3',
            '$literal_reference_flat_array(S_lost, n_new_array, H_live.NODES)',
            '~$literal_reference_cell(S_lost, n_new, H_live.NODES)',
            '~$literal_reference_debt_safe(S_lost, H_lost)',
            '$literal_reference_debt_check(S_lost).COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
        ]
    checks += driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15 if detached else 17, 'S_read') + [
        'S_read.LITERALREFRETAINED = [n_old]', 'S_read.LITERALREFDEBTS = [n_new]',
        '$lookup(S_read.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S_read.STORE[n_snapshot] = DEFINED (PARRAY n_new_array)',
        payload('S_read', 'n_new_array', 44),
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        'n_copy =/= n_builder', '$heap_owners($heap_graph(S_read), HCELL n_new) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HCELL n_new) = 2',
        '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
    ]
    if detached:
        checks += [
            '$lookup(S_read.ENV, $ptascii("q")) = (n_new)', '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
            '$propref_at(S_read.PROPREFS, n_new) = eps', '(HOBJECT n_box) <- S_read.ALLOCATIONS',
            'S_read.STORE[n_new] = DEFINED (PARRAY n_new_live)', 'n_new_live =/= n_new_array', payload('S_read', 'n_new_live', 66),
            '$literal_reference_cell(S_read, n_new, [HCELL n_new, HARRAY n_new_live])',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PINT 99))',
            '$heap_owners($heap_graph(S_read), HARRAY n_new_array) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_new_live) = 1',
        ]
    else:
        checks += [
            '$lookup(S_read.ENV, $ptascii("q")) = eps', '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
            'S_read.PROPREFS = S.PROPREFS', '$propref_sources_valid(S_read, n_new, ppropref_new.SOURCES)',
            'S_read.STORE[n_new] = DEFINED (PARRAY n_new_array)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_new_array', payload('S_read', 'n_copy_child', 55),
            '$heap_owners($heap_graph(S_read), HARRAY n_new_array) = 2',
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_child) = 1',
        ]
    checks += seek('S_read', 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
    ] + seek('S_inverse', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.LITERALREFRETAINED = eps', 'S_balanced.LITERALREFDEBTS = eps',
        'S_balanced.LITERALARRAYRETAINED = eps', 'S_balanced.LITERALARRAYDEBTS = eps',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_balanced), HCELL n_new) = ' + ('1' if detached else '2'),
        '$heap_owners($heap_graph(S_balanced), HCELL n_old) = ' + ('4' if detached else '3'),
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)', 'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)',
        'n_shared =/= n_builder', '$lookup(S_shared.ENV, $ptascii("bad")) = eps',
        '$entry_lookup(S_shared.ARRAYS[n_builder].ITEMS, KINT 1) = (ALIAS n_new)',
    ]
    if detached:
        checks += [
            'S_shared.STORE[n_new] = DEFINED (PINT 99)', '$propref_at(S_shared.PROPREFS, n_new) = eps',
            '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 1) = (DIRECT (PARRAY n_shared_child))',
            'n_shared_child =/= n_new_live', payload('S_shared', 'n_shared_child', 77),
            '~((HARRAY n_new_live) <- S_shared.ALLOCATIONS)',
            'S_shared.STORE[n_old] = DEFINED (PARRAY n_old_live)', payload('S_shared', 'n_old_live', 88),
            '$propref_at(S_shared.PROPREFS, n_old) = (ppropref_old)',
            '$propref_sources_valid(S_shared, n_old, ppropref_old.SOURCES)',
            payload('S_shared', 'n_old_array', 2), payload('S_shared', 'n_new_array', 44),
            '$heap_owners($heap_graph(S_shared), HCELL n_new) = 1',
        ]
    else:
        checks += [
            '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 1) = (ALIAS n_new)',
            '$entry_lookup(S_shared.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PINT 99))',
            'S_shared.STORE[n_new] = DEFINED (PARRAY n_after_array)', 'n_after_array =/= n_new_array', payload('S_shared', 'n_after_array', 66),
            payload('S_shared', 'n_new_array', 44), payload('S_shared', 'n_old_array', 33),
            '$propref_at(S_shared.PROPREFS, n_new) = (ppropref_new)',
            '$propref_sources_valid(S_shared, n_new, ppropref_new.SOURCES)',
            '$heap_owners($heap_graph(S_shared), HCELL n_new) = 3',
            '$heap_owners($heap_graph(S_shared), HARRAY n_after_array) = 1',
            '~((HARRAY n_copy_child) <- S_shared.ALLOCATIONS)',
        ]
    checks += [
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps', 'S_done.PROPREFS = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        '~((HCELL n_old) <- S_done.ALLOCATIONS)', '~((HCELL n_new) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_old_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_old_live) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_new_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_builder) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy) <- S_done.ALLOCATIONS)', '~((HARRAY n_shared) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_balance) <- S_done.ALLOCATIONS)', '~((HOBJECT n_box) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        '$drive_steps($drive_steps(S_read, 1)[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if detached:
        checks += ['~((HOBJECT n_old_box) <- S_done.ALLOCATIONS)', '~((HARRAY n_shared_child) <- S_done.ALLOCATIONS)']
    else:
        checks += ['~((HARRAY n_after_array) <- S_done.ALLOCATIONS)', '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
