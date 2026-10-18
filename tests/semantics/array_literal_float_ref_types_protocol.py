#!/usr/bin/env python3
"""Reached typed singleton copies, source constraints, and throw cleanup."""
import base64
import json

import array_literal_float_ref_types_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS, seek


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in
              ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'PROPREFS',
               'LITERALREFRETAINED', 'LITERALREFDEBTS')]]


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, inverse_line, source_name, source_key, final_value = (
        (20, 30, 'probe', 0, 66) if thrown else (15, 21, 'a', 1, 55))
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', 'i = 1',
        'S.RESULT = KNOWN PNULL', 'S.CELL = n_old',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)',
        'n_old =/= n_new', 'n_old <- S.REFCELLS', 'n_new <- S.REFCELLS',
        'S.STORE[n_old] = DEFINED (PINT 2)', 'S.STORE[n_new] = DEFINED (PINT 44)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$lookup(S.ENV, $ptascii("box")) = (n_box_cell)',
        'S.STORE[n_box_cell] = DEFINED (POBJECT n_box)',
        '$propref_at(S.PROPREFS, n_old) = eps',
        '$propref_at(S.PROPREFS, n_new) = (ppropref_new)',
        'ppropref_new.SOURCES = [OBJECT_PROP_SOURCE n_box ($ptascii("slot")) porigin_slot]',
        '$propref_sources_valid(S, n_new, ppropref_new.SOURCES)',
        '$literal_reference_plain_cell(S, n_old)', '~$literal_reference_plain_cell(S, n_new)',
        '$literal_reference_cell(S, n_new, S.ALLOCATIONS)',
        '$literal_reference_property_sources(S, n_new, ppropref_new.SOURCES, S.ALLOCATIONS)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S), HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners($heap_graph(S), HCELL n_new) = 2',
        '$class_state_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LINE = z', 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.PROPREFS = S.PROPREFS',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = ' + ('4' if thrown else '3'),
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_builder, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_old)]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
            'S.STORE[n_dest] = DEFINED (PINT 100)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps',
            'S_start.ERRORHANDLER = S.ERRORHANDLER', 'S_start.STORE[n_dest] = DEFINED (PINT 99)',
            'S_start.STORE[n_later] = DEFINED (PINT 7)',
            '~((HARRAY n_builder) <- S_start.ALLOCATIONS)',
            '$lookup(S_start.ENV, $ptascii("q")) = (n_new)',
            'S_start.STORE[n_old] = DEFINED (PINT 33)', 'S_start.STORE[n_new] = DEFINED (PINT 44)',
            'S_start.LITERALREFRETAINED = [n_old]', 'S_start.LITERALREFDEBTS = [n_new]',
            'S_start.PROPREFS = S.PROPREFS',
            '$heap_owners($heap_graph(S_start), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_start), HCELL n_new) = 2',
            '$literal_reference_debt_safe(S_start, $heap_graph(S_start))',
            '$class_state_valid(S_start)', '$call_descriptors_valid(S_start)',
        ]
    else:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)',
            'S_resume.STORE[n_old] = DEFINED (PINT 33)', 'S_resume.STORE[n_new] = DEFINED (PINT 44)',
            'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            'S_resume.PROPREFS = S.PROPREFS',
            'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
            'S_insert.STORE = S_resume.STORE', 'S_insert.PROPREFS = S_resume.PROPREFS',
            'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
            'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (ALIAS n_new)]',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
            '$heap_owners($heap_graph(S_insert), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HCELL n_new) = 3',
            '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_copy') + [
        'S_copy.LITERALREFRETAINED = [n_old]', 'S_copy.LITERALREFDEBTS = [n_new]',
        '$lookup(S_copy.ENV, $ptascii("q")) = eps',
        '$lookup(S_copy.ENV, $ptascii("replacement")) = eps',
        'S_copy.STORE[n_new] = DEFINED (PINT 44)', 'S_copy.STORE[n_old] = DEFINED (PINT 33)',
        '$lookup(S_copy.ENV, $ptascii("' + source_name + '")) = (n_source_cell)',
        '$lookup(S_copy.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_copy.STORE[n_source_cell] = DEFINED (PARRAY n_source)',
        'S_copy.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_source =/= n_copy',
        '$entry_lookup(S_copy.ARRAYS[n_source].ITEMS, KINT ' + str(source_key) + ') = (ALIAS n_new)',
        '$entry_lookup(S_copy.ARRAYS[n_copy].ITEMS, KINT ' + str(source_key) + ') = (DIRECT pvalue_free)',
        '$string_bytes(pvalue_free) = ($ptascii("free"))',
        '$heap_count(HCELL n_new, $machine_roots(S_copy)) = 0',
        '$heap_owners($heap_graph(S_copy), HCELL n_new) = 1',
        '$heap_owners($heap_graph(S_copy)[.DEBTS = eps], HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_copy), HCELL n_old) = 2',
        'S_copy.PROPREFS = S.PROPREFS',
        '$propref_at(S_copy.PROPREFS, n_new) = (ppropref_new)',
        '$propref_sources_valid(S_copy, n_new, ppropref_new.SOURCES)',
        '~$literal_reference_plain_cell(S_copy, n_new)',
        '$literal_reference_cell(S_copy, n_new, S_copy.ALLOCATIONS)',
        '~$literal_reference_cell(S_copy, n_new, [HCELL n_new])',
        '~$literal_reference_property_sources(S_copy, n_new, ppropref_new.SOURCES, [HCELL n_new])',
        '~$literal_reference_cell(S_copy[.STORE[n_new] = DEFINED (PARRAY n_source)], n_new, S_copy.ALLOCATIONS)',
        '$literal_reference_debt_safe(S_copy, $heap_graph(S_copy))',
        '$class_state_valid(S_copy)', '$call_descriptors_valid(S_copy)', '$heap_valid($heap_graph(S_copy))',
    ]
    if not thrown:
        checks += ['n_source = n_builder']
    checks += seek('S_copy', 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        '$lookup(S_inverse.ENV, $ptascii("q")) = (n_new)',
        'S_inverse.LITERALREFRETAINED = [n_old]', 'S_inverse.LITERALREFDEBTS = [n_new]',
        '$heap_owners($heap_graph(S_inverse), HCELL n_new) = 2',
    ] + seek('S_inverse', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3) :: ptask_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S_inverse_resume, n_balance, n_new, poperand_inverse)',
        'S_inverse_resume.PROPREFS = S.PROPREFS',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.TODO = (ARRAY_NEXT n_balance eps) :: ptask_inverse*',
        'S_balanced.LITERALREFRETAINED = eps', 'S_balanced.LITERALREFDEBTS = eps',
        'S_balanced.PROPREFS = S_inverse_resume.PROPREFS',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_balanced), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_balanced), HCELL n_old) = 3',
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        'S_shared.STORE[n_new] = DEFINED (PINT ' + str(final_value) + ')',
        'S_shared.STORE[n_old] = DEFINED (PINT 33)',
        '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)',
        'n_shared =/= n_source', 'n_shared =/= n_copy',
        '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT ' + str(source_key) + ') = (ALIAS n_new)',
        '$entry_lookup(S_shared.ARRAYS[n_source].ITEMS, KINT ' + str(source_key) + ') = (ALIAS n_new)',
        '$entry_lookup(S_shared.ARRAYS[n_copy].ITEMS, KINT ' + str(source_key) + ') = (DIRECT pvalue_free)',
        '$entry_lookup(S_shared.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$propref_at(S_shared.PROPREFS, n_new) = (ppropref_new)',
        '$propref_sources_valid(S_shared, n_new, ppropref_new.SOURCES)',
        '$heap_owners($heap_graph(S_shared), HCELL n_new) = 3',
        '$heap_owners($heap_graph(S_shared), HCELL n_old) = 3',
        '$class_state_valid(S_shared)',
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps', 'S_done.PROPREFS = eps',
        '~((HCELL n_old) <- S_done.ALLOCATIONS)', '~((HCELL n_new) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_box) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_balance) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_shared) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
        '$drive_steps(S_balanced_driven, 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
