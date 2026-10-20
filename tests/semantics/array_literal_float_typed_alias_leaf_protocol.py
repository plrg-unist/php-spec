#!/usr/bin/env python3
"""Reached typed leaves preserve constraints until explicit property unset."""
import base64
import json

import array_literal_float_typed_alias_leaf_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_protocol import HELPERS, driven
from array_literal_float_ref_deficit_state_review import seek


def items(state, table, leaf, value, sibling):
    return [
        f'{state}.ARRAYS[{table}].ITEMS = [ENTRY (KINT 0) (ALIAS {leaf}), ENTRY (KINT 1) (DIRECT (PINT {sibling}))]',
        f'{state}.STORE[{leaf}] = DEFINED (PINT {value})',
        f'$literal_reference_flat_array({state}, {table}, {state}.ALLOCATIONS)',
    ]


def conditions(name, program, path, stdout):
    detached = name.endswith('unset-property')
    line_inverse = 20 if detached else 21
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_builder n_old poperand phpType13* z n_bits i'
    inverse = f'ARRAY_KEY_FLOAT_ARRAY_RESULT n_balance n_current poperand_inverse eps {line_inverse} n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 30, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', 'z = 13', 'i = 1',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)',
        'S.STORE[n_q] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '~(n_q <- S.REFCELLS)', '$lookup(S.ENV, $ptascii("old_leaf")) = (n_old_leaf)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_current)', 'n_old =/= n_current',
        '$entry_lookup(S.ARRAYS[n_current].ITEMS, KINT 0) = (ALIAS n_typed)',
        '$lookup(S.ENV, $ptascii("leaf")) = eps',
        '$lookup(S.ENV, $ptascii("box")) = (n_box_cell)', 'S.STORE[n_box_cell] = DEFINED (POBJECT n_box)',
        '$propref_at(S.PROPREFS, n_typed) = (ppropref_typed)',
        'ppropref_typed.SOURCES = [OBJECT_PROP_SOURCE n_box ($ptascii("slot")) porigin_property]',
        '$propref_sources_valid(S, n_typed, ppropref_typed.SOURCES)',
        '$literal_reference_flat_cell(S, n_typed)', '~$literal_reference_plain_cell(S, n_typed)',
        '$literal_reference_cell(S, n_typed, S.ALLOCATIONS)',
        '$literal_reference_flat_sources(S, S.ARRAYS[n_current].ITEMS, [HARRAY n_current, HCELL n_typed, HOBJECT n_box])',
        '~$literal_reference_flat_sources(S, S.ARRAYS[n_current].ITEMS, [HARRAY n_current, HCELL n_typed])',
        '~$literal_reference_flat_array(S, n_current, [HARRAY n_current, HCELL n_typed])',
        '~$literal_reference_flat_cell(S[.STORE[n_typed] = DEFINED (PSTRING ($ptascii("typed")))], n_typed)',
        '~$literal_reference_flat_cell(S[.STORE[n_typed] = DEFINED (PARRAY n_builder)], n_typed)',
    ] + items('S', 'n_old', 'n_old_leaf', 33, 7) + items('S', 'n_current', 'n_typed', 44, 8) + [
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        'S.LITERALARRAYRETAINED = eps', 'S.LITERALARRAYDEBTS = eps',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2', '$heap_owners($heap_graph(S), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S), HCELL n_typed) = 2',
        '$array_float_array_key_source(S, ' + args + ')', '$array_float_array_key_ready(S, n_builder, n_old, poperand)',
        '~$array_float_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_array_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 13',
        '$error_call_valid(S_dispatch, perrorcall)', '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 14])',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_typed) = 2',
        'S_dispatch.PROPREFS = S.PROPREFS',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 32, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HOBJECT n_box, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 31, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.STORE[n_q] = DEFINED (PARRAY n_current)',
        '$propref_at(S_resume.PROPREFS, n_typed) = (ppropref_typed)',
        '$array_float_array_key_value(S_resume, poperand) = (n_current)',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_array_key_ready(S_resume, n_builder, n_old, poperand)',
        'S_indebted_leaf = S_resume[.LITERALREFDEBTS = [n_typed]]',
        '$array_float_array_key_source(S_indebted_leaf, ' + args + ')',
        '~$array_float_array_key_ready(S_indebted_leaf, n_builder, n_old, poperand)',
        '$error_read_discard(S_indebted_leaf, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 1) = (DIRECT (PARRAY n_current))',
        'S_insert.LITERALARRAYRETAINED = [n_old]', 'S_insert.LITERALARRAYDEBTS = [n_current]',
        'S_insert.PROPREFS = S_resume.PROPREFS',
        '$heap_owners($heap_graph(S_insert), HARRAY n_current) = 2',
        '$heap_owners($heap_graph(S_insert), HCELL n_typed) = 2',
        'S_lost_box = $unset_name(S_insert, $ptascii("box"))',
        'H_lost_box = $heap_graph(S_lost_box)', '$heap_valid(H_lost_box)',
        'H_live = $heap_prune(H_lost_box[.DEBTS = eps])',
        '~((HOBJECT n_box) <- H_live.NODES)', '(HCELL n_typed) <- H_live.NODES',
        '$heap_owners(H_live, HCELL n_typed) = 1',
        '$literal_reference_flat_items(S_lost_box, S_lost_box.ARRAYS[n_current].ITEMS)',
        '~$literal_reference_flat_sources(S_lost_box, S_lost_box.ARRAYS[n_current].ITEMS, H_live.NODES)',
        '~$literal_reference_debt_safe(S_lost_box, H_lost_box)',
    ] + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
        'S_read.STORE[n_q] = DEFINED (PARRAY n_current)',
        'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_current]',
        '$heap_owners($heap_graph(S_read), HARRAY n_current) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_current) = 2',
        '(HOBJECT n_box) <- S_read.ALLOCATIONS', '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
    ] + items('S_read', 'n_current', 'n_typed', 44 if detached else 55, 55)
    if detached:
        checks += [
            '$propref_at(S_read.PROPREFS, n_typed) = eps', '$literal_reference_plain_cell(S_read, n_typed)',
            '$heap_owners($heap_graph(S_read), HCELL n_typed) = 1',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            'n_copy =/= n_builder', '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_current',
            'S_read.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_free), ENTRY (KINT 1) (DIRECT (PINT 77))]',
            '$string_bytes(pvalue_free) = ($ptascii("free"))', '$entries_nodes(S_read.ARRAYS[n_copy_child].ITEMS) = eps',
        ]
    else:
        checks += [
            '$propref_at(S_read.PROPREFS, n_typed) = (ppropref_typed)',
            '$propref_sources_valid(S_read, n_typed, ppropref_typed.SOURCES)',
            '$heap_owners($heap_graph(S_read), HCELL n_typed) = 2',
            '$lookup(S_read.ENV, $ptascii("bad")) = eps', '$lookup(S_read.ENV, $ptascii("copy")) = eps',
        ]
    checks += seek('S_read', 30, 'S_inverse') + [
        f'$array_float_array_key_plan(S_inverse) = ((n_balance, n_current, poperand_inverse, eps, {line_inverse}, n_inverse_bits, 3))',
        f'poperand_inverse = VARIABLE ($ptascii("q")) {line_inverse}',
    ] + seek('S_inverse', 31, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_inverse*',
        '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = (n_old)',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.LITERALARRAYRETAINED = eps', 'S_balanced.LITERALARRAYDEBTS = eps',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_final') + [
        '$lookup(S_final.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_final.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        '$entry_lookup(S_final.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_current', 'S_final.STORE[n_q] = DEFINED (PARRAY n_old)',
        '$heap_owners($heap_graph(S_final), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_final), HARRAY n_current) = 1',
        '(HOBJECT n_box) <- S_final.ALLOCATIONS',
    ] + items('S_final', 'n_old', 'n_old_leaf', 33, 7) + items('S_final', 'n_current', 'n_typed', 44 if detached else 66, 55)
    if detached:
        checks += [
            '$propref_at(S_final.PROPREFS, n_typed) = eps', '$heap_owners($heap_graph(S_final), HCELL n_typed) = 1',
            'S_final.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_free), ENTRY (KINT 1) (DIRECT (PINT 77))]',
            '$lookup(S_final.ENV, $ptascii("balanced")) = (n_after_cell)', 'S_final.STORE[n_after_cell] = DEFINED (PARRAY n_after)',
            '$entry_lookup(S_final.ARRAYS[n_after].ITEMS, KINT 1) = (DIRECT (PARRAY n_after_child))',
            'n_after_child =/= n_current',
            'S_final.ARRAYS[n_after_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 66)), ENTRY (KINT 1) (DIRECT (PINT 99))]',
        ]
    else:
        checks += items('S_final', 'n_copy_child', 'n_typed', 66, 77) + [
            '$propref_at(S_final.PROPREFS, n_typed) = (ppropref_typed)',
            '$propref_sources_valid(S_final, n_typed, ppropref_typed.SOURCES)',
            '$heap_owners($heap_graph(S_final), HCELL n_typed) = 3',
        ]
    checks += [
        '$call_descriptors_valid(S_final)', '$heap_valid($heap_graph(S_final))',
        'S_done = $drive_steps(S_final, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        '$propref_at(S_done.PROPREFS, n_typed) = eps',
        *[f'~(({node}) <- S_done.ALLOCATIONS)' for node in
          ['HCELL n_typed', 'HCELL n_old_leaf', 'HOBJECT n_box', 'HARRAY n_old', 'HARRAY n_current', 'HARRAY n_builder',
           'HARRAY n_balance', 'HARRAY n_copy', 'HARRAY n_copy_child'] + (['HARRAY n_after', 'HARRAY n_after_child'] if detached else [])],
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 1) = $drive_steps($drive_steps(S_final, 0)[.COMPLETION = NORMAL], 1)',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
