#!/usr/bin/env python3
"""Typed array leaves preserve child COW and detach sources on explicit unset."""
import base64
import json

import array_literal_float_typed_array_alias_leaf_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_protocol import HELPERS, driven as base_driven
from array_literal_float_ref_deficit_state_review import seek
from array_literal_float_array_alias_leaf_protocol import payload
from array_literal_float_typed_string_alias_leaf_state_review import items


def driven(start, raw, result):
    return base_driven(start, raw, result) + [f'{result}.PROPREFS = {raw}.PROPREFS']


def conditions(name, program, path, stdout):
    detached = name.endswith('unset-property')
    inverse_line = 21 if detached else 23
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = f'ARRAY_KEY_FLOAT_ARRAY_RESULT n_balance n_current poperand_inverse eps {inverse_line} n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 30, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', 'z = 15', 'i = 1',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)',
        'S.STORE[n_q] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '~(n_q <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("old_leaf")) = (n_old_leaf)',
        'S.STORE[n_old_leaf] = DEFINED (PARRAY n_old_payload)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_current)', 'n_old =/= n_current',
        '$entry_lookup(S.ARRAYS[n_current].ITEMS, KINT 0) = (ALIAS n_typed)',
        'S.STORE[n_typed] = DEFINED (PARRAY n_payload)',
        '$lookup(S.ENV, $ptascii("box")) = (n_box_cell)', 'S.STORE[n_box_cell] = DEFINED (POBJECT n_box)',
        '$lookup(S.ENV, $ptascii("new_leaf")) = eps',
        '$lookup(S.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S.STORE[n_snapshot] = DEFINED (PARRAY n_payload)',
        '$lookup(S.ENV, $ptascii("old_snapshot")) = (n_old_snapshot)', 'S.STORE[n_old_snapshot] = DEFINED (PARRAY n_old_payload)',
        '$propref_at(S.PROPREFS, n_typed) = (ppropref_typed)',
        'ppropref_typed.SOURCES = [OBJECT_PROP_SOURCE n_box ($ptascii("slot")) porigin_property]',
        '$propref_sources_valid(S, n_typed, ppropref_typed.SOURCES)',
        '$literal_reference_flat_cell(S, n_typed)', '~$literal_reference_plain_cell(S, n_typed)',
        '~$literal_reference_cell(S, n_typed, [HCELL n_typed, HOBJECT n_box])',
        '$literal_reference_child_array(S, n_payload, S.ALLOCATIONS)',
        items('S', 'n_current', 'ALIAS n_typed', 8), items('S', 'n_old', 'ALIAS n_old_leaf', 7),
        payload('S', 'n_payload', 44), payload('S', 'n_old_payload', 33),
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2', '$heap_owners($heap_graph(S), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S), HCELL n_typed) = 2', '$heap_owners($heap_graph(S), HARRAY n_payload) = 2',
        '$literal_reference_flat_array(S, n_current, [HARRAY n_current, HCELL n_typed, HARRAY n_payload, HOBJECT n_box])',
        '~$literal_reference_flat_array(S, n_current, [HARRAY n_current, HCELL n_typed, HOBJECT n_box])',
        '~$literal_reference_flat_array(S, n_current, [HARRAY n_current, HCELL n_typed, HARRAY n_payload])',
        '$literal_reference_flat_sources(S, S.ARRAYS[n_current].ITEMS, [HARRAY n_payload, HOBJECT n_box])',
        '~$literal_reference_flat_sources(S, S.ARRAYS[n_current].ITEMS, [HOBJECT n_box])',
        '~$literal_reference_flat_sources(S, S.ARRAYS[n_current].ITEMS, [HARRAY n_payload])',
        '~$literal_reference_flat_cell(S[.STORE[n_typed] = DEFINED (PINT 99)], n_typed)',
        '~$literal_reference_flat_cell(S[.PROPREFS = [{CELL n_typed, SOURCES eps}]], n_typed)',
        '~$literal_reference_flat_cell(S[.LITERALARRAYDEBTS = [n_payload]], n_typed)',
        '~$literal_reference_flat_array(S[.LITERALREFDEBTS = [n_typed]], n_current, S.ALLOCATIONS)',
        '~$literal_reference_flat_cell(S[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]], n_typed)',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        '$array_float_array_key_source(S, ' + args + ')', '$array_float_array_key_ready(S, n_builder, n_old, poperand)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 15',
        '$error_call_valid(S_dispatch, perrorcall)', '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_typed) = 2',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 31, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.STORE[n_q] = DEFINED (PARRAY n_current)', 'S_resume.PROPREFS = S.PROPREFS',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_array_key_value(S_resume, poperand) = (n_current)',
        '$array_float_array_key_ready(S_resume, n_builder, n_old, poperand)',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 1) = (DIRECT (PARRAY n_current))',
        'S_insert.LITERALARRAYRETAINED = [n_old]', 'S_insert.LITERALARRAYDEBTS = [n_current]',
        'S_insert.PROPREFS = S.PROPREFS',
        '$heap_owners($heap_graph(S_insert), HARRAY n_current) = 2',
        '$heap_owners($heap_graph(S_insert), HCELL n_typed) = 2',
        '$heap_owners($heap_graph(S_insert), HARRAY n_payload) = 2',
    ] + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
        'S_read.STORE[n_q] = DEFINED (PARRAY n_current)',
        'S_read.STORE[n_typed] = DEFINED (PARRAY n_live_payload)', 'n_live_payload =/= n_payload',
        payload('S_read', 'n_live_payload', 66 if detached else 55), payload('S_read', 'n_payload', 44),
        'S_read.STORE[n_snapshot] = DEFINED (PARRAY n_payload)',
        items('S_read', 'n_current', 'ALIAS n_typed', 55),
        'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_current]',
        '$heap_owners($heap_graph(S_read), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_current) = 2',
        '$heap_owners($heap_graph(S_read), HARRAY n_live_payload) = 1',
        '$heap_owners($heap_graph(S_read), HARRAY n_payload) = 1',
        '$node_children(S_read, HCELL n_typed) = [HARRAY n_live_payload]',
        '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        '(HOBJECT n_box) <- S_read.ALLOCATIONS',
    ]
    if detached:
        checks += [
            '$propref_at(S_read.PROPREFS, n_typed) = eps',
            '~$propref_source_valid(S_read, n_typed, OBJECT_PROP_SOURCE n_box ($ptascii("slot")) porigin_property)',
            '$heap_owners($heap_graph(S_read), HCELL n_typed) = 1',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_current', items('S_read', 'n_copy_child', 'DIRECT (PARRAY n_copy_payload)', 77),
            'n_copy_payload =/= n_live_payload', 'n_copy_payload =/= n_payload', payload('S_read', 'n_copy_payload', 55),
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_payload) = 1',
            '$literal_reference_flat_cell(S_read, n_typed)',
        ]
    else:
        checks += [
            'S_read.PROPREFS = S.PROPREFS', '$propref_sources_valid(S_read, n_typed, ppropref_typed.SOURCES)',
            '$heap_owners($heap_graph(S_read), HCELL n_typed) = 2',
            '$lookup(S_read.ENV, $ptascii("e")) = eps',
        ]
    checks += seek('S_read', 30, 'S_inverse') + [
        f'$array_float_array_key_plan(S_inverse) = ((n_balance, n_current, poperand_inverse, eps, {inverse_line}, n_inverse_bits, 3))',
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
        '$lookup(S_final.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_final.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        '$entry_lookup(S_final.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_current',
        'S_final.STORE[n_old_leaf] = DEFINED (PARRAY n_old_changed)', 'n_old_changed =/= n_old_payload',
        payload('S_final', 'n_old_changed', 88), payload('S_final', 'n_old_payload', 33),
        'S_final.STORE[n_old_snapshot] = DEFINED (PARRAY n_old_payload)',
        items('S_final', 'n_q_child', 'ALIAS n_old_leaf', 99), items('S_final', 'n_old', 'ALIAS n_old_leaf', 7),
        '$heap_owners($heap_graph(S_final), HCELL n_old_leaf) = 3',
        '$heap_owners($heap_graph(S_final), HARRAY n_old_changed) = 1',
        'S_final.STORE[n_snapshot] = DEFINED (PARRAY n_payload)', payload('S_final', 'n_payload', 44),
        '$heap_owners($heap_graph(S_final), HARRAY n_payload) = 1',
    ]
    if detached:
        checks += [
            'S_final.STORE[n_typed] = DEFINED (PINT 99)', 'S_final.PROPREFS = eps',
            '~((HARRAY n_live_payload) <- S_final.ALLOCATIONS)',
            items('S_final', 'n_current', 'ALIAS n_typed', 55),
            items('S_final', 'n_copy_child', 'DIRECT (PARRAY n_copy_payload)', 77),
            payload('S_final', 'n_copy_payload', 77),
            '$heap_owners($heap_graph(S_final), HCELL n_typed) = 1',
            '$heap_owners($heap_graph(S_final), HARRAY n_copy_payload) = 1',
        ]
    else:
        checks += [
            'S_final.STORE[n_typed] = DEFINED (PARRAY n_live_payload)', payload('S_final', 'n_live_payload', 66),
            items('S_final', 'n_current', 'ALIAS n_typed', 55), items('S_final', 'n_copy_child', 'ALIAS n_typed', 77),
            'S_final.PROPREFS = S.PROPREFS', '$propref_sources_valid(S_final, n_typed, ppropref_typed.SOURCES)',
            '$heap_owners($heap_graph(S_final), HCELL n_typed) = 3',
            '$heap_owners($heap_graph(S_final), HARRAY n_live_payload) = 1',
        ]
    checks += [
        '$call_descriptors_valid(S_final)', '$heap_valid($heap_graph(S_final))', '$class_state_valid(S_final)',
        'S_done = $drive_steps(S_final, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps', 'S_done.PROPREFS = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        *[f'~(({node}) <- S_done.ALLOCATIONS)' for node in ('HCELL n_typed', 'HCELL n_old_leaf', 'HOBJECT n_box')],
        *[f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in
          ('n_old', 'n_current', 'n_builder', 'n_balance', 'n_q_child', 'n_copy', 'n_copy_child', 'n_payload', 'n_old_payload', 'n_old_changed', 'n_live_payload')],
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))', '$class_state_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 1) = $drive_steps($drive_steps(S_final, 0)[.COMPLETION = NORMAL], 1)',
    ]
    if detached:
        checks += ['~((HARRAY n_copy_payload) <- S_done.ALLOCATIONS)']
    else:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
