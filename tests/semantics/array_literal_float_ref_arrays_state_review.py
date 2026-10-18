#!/usr/bin/env python3
"""Reached wrapper deficits preserve separate child-table COW and cleanup."""
import base64
import json

import array_literal_float_ref_arrays_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS as BASE_HELPERS, seek, driven

HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 17) = $literal_deficit_review_echo(S, $ptascii("M:"))
'''


def item(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, converted, inverse_line = (22, '1', 33) if thrown else (20, '$(-2)', 29)
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', f'i = {converted}',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)', 'n_old =/= n_new',
        'S.STORE[n_old] = DEFINED (PARRAY n_old_array)',
        'S.STORE[n_new] = DEFINED (PARRAY n_new_array)', 'n_old_array =/= n_new_array',
        item('S', 'n_old_array', 2), item('S', 'n_new_array', 44),
        'n_old <- S.REFCELLS', '~(n_new <- S.REFCELLS)',
        '~$array_immutable(S, n_old_array)', '~$array_immutable(S, n_new_array)',
        '$heap_count(HARRAY n_old_array, $pools_nodes(S.POOLS)) = 0',
        '$heap_count(HARRAY n_new_array, $pools_nodes(S.POOLS)) = 0',
        '~$literal_reference_plain_cell(S, n_old)',
        '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
        '~$literal_reference_cell(S, n_old, eps)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
        'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S), HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners($heap_graph(S), HARRAY n_old_array) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_new_array) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$array_float_ref_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_ref_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, VARIABLE ($ptascii("outside")) z, phpType13*, z, n_bits, i)',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PINT 2)]) = eps',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LINE = z', 'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old_array) = 1',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = ' + ('4' if thrown else '3'),
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_old_array, $tasks_nodes(pframe.TODO)) = 0',
        '$call_descriptors_valid(S_entered)',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_old)]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)',
            'S.STORE[n_later] = DEFINED (PINT 7)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps',
            'S_start.ERRORHANDLER = S.ERRORHANDLER',
            'S_start.STORE[n_dest] = DEFINED (PINT 99)',
            'S_start.STORE[n_later] = DEFINED (PINT 7)',
            '~((HARRAY n_builder) <- S_start.ALLOCATIONS)',
            '$lookup(S_start.ENV, $ptascii("q")) = (n_new)',
            'S_start.STORE[n_old] = DEFINED (PARRAY n_old_array)',
            'S_start.STORE[n_new] = DEFINED (PARRAY n_new_array)',
            item('S_start', 'n_old_array', 33), item('S_start', 'n_new_array', 44),
            'S_start.LITERALREFRETAINED = [n_old]', 'S_start.LITERALREFDEBTS = [n_new]',
            '$heap_owners($heap_graph(S_start), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_start), HCELL n_new) = 1',
            '$heap_owners($heap_graph(S_start), HARRAY n_old_array) = 1',
            '$heap_owners($heap_graph(S_start), HARRAY n_new_array) = 1',
            '$literal_reference_debt_safe(S_start, $heap_graph(S_start))',
            '$call_descriptors_valid(S_start)', '$heap_valid($heap_graph(S_start))',
        ]
    else:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_resume.REFCELLS',
            'S_resume.STORE[n_old] = DEFINED (PARRAY n_old_array)',
            'S_resume.STORE[n_new] = DEFINED (PARRAY n_new_array)',
            item('S_resume', 'n_old_array', 33), item('S_resume', 'n_new_array', 44),
            'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
            'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
            '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            '~$array_float_ref_key_ready(S_resume[.STORE[n_new] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
            '~$array_float_ref_key_ready(S_resume[.STORE[n_old] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
            '~$literal_reference_cell(S_resume[.PROPREFS = [{CELL n_new, SOURCES eps}]], n_new, S_resume.ALLOCATIONS)',
            '~$literal_reference_cell(S_resume[.ARRAYS[n_new_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_old)]], n_new, S_resume.ALLOCATIONS)',
            '~$literal_reference_cell(S_resume[.ARRAYS[n_new_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_new_array))]], n_new, S_resume.ALLOCATIONS)',
            '~$literal_reference_cell(S_resume[.ARRAYS[n_new_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("bad"))))]], n_new, S_resume.ALLOCATIONS)',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
            'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
            'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
            'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT $(-2)) (ALIAS n_new)]',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
            '$heap_graph(S_insert).DEBTS = [HCELL n_new]',
            '$heap_owners($heap_graph(S_insert), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HCELL n_new) = 2',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old_array) = 1',
            '$heap_owners($heap_graph(S_insert), HARRAY n_new_array) = 1',
            '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_copy') + [
        'S_copy.LITERALREFRETAINED = [n_old]', 'S_copy.LITERALREFDEBTS = [n_new]',
        '$lookup(S_copy.ENV, $ptascii("q")) = eps',
        'S_copy.STORE[n_new] = DEFINED (PARRAY n_new_array)',
        'S_copy.STORE[n_old] = DEFINED (PARRAY n_old_array)',
        item('S_copy', 'n_old_array', 33), item('S_copy', 'n_new_array', 44),
        '$lookup(S_copy.ENV, $ptascii("probe")) = (n_probe_cell)',
        '$lookup(S_copy.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_copy.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
        'S_copy.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_probe =/= n_copy',
        '$entry_lookup(S_copy.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
        '$entry_lookup(S_copy.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_new_array', item('S_copy', 'n_copy_child', 55),
        '$heap_owners($heap_graph(S_copy), HCELL n_new) = 1',
        '$heap_owners($heap_graph(S_copy)[.DEBTS = eps], HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_copy), HCELL n_old) = 2',
        '$heap_owners($heap_graph(S_copy), HARRAY n_new_array) = 1',
        '$heap_owners($heap_graph(S_copy), HARRAY n_copy_child) = 1',
        '$heap_graph(S_copy).DEBTS = [HCELL n_new]',
        'H_logical = $heap_prune($heap_graph(S_copy)[.DEBTS = eps])',
        'H_biased = $heap_prune($heap_graph(S_copy))', 'H_biased.NODES = H_logical.NODES',
        '(HCELL n_new) <- H_biased.NODES', '(HARRAY n_new_array) <- H_biased.NODES',
        '$literal_reference_cell(S_copy, n_new, H_logical.NODES)',
        '$literal_reference_debt_safe(S_copy, $heap_graph(S_copy))',
        '$call_descriptors_valid(S_copy)', '$heap_valid($heap_graph(S_copy))',
    ]
    if not thrown:
        checks += [
            'S_copy.STORE[n_dest] = DEFINED (PARRAY n_builder)',
            'S_copy.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
            'S_exhausted = S_copy[.LITERALREFDEBTS = [n_new, n_new]]',
            '$heap_owners($heap_graph(S_exhausted), HCELL n_new) = 0',
            '~$literal_reference_debt_safe(S_exhausted, $heap_graph(S_exhausted))',
            'S_refused = $prune_allocations(S_exhausted)',
            'S_refused.COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
            'S_refused.ALLOCATIONS = S_exhausted.ALLOCATIONS', 'S_refused.ARRAYS = S_exhausted.ARRAYS',
            '$drive_steps(S_refused, 2000) = S_refused',
        ] + seek('S_copy', 17, 'S_mutated') + [
            'S_mutated.LITERALREFRETAINED = [n_old]', 'S_mutated.LITERALREFDEBTS = [n_new]',
            'S_mutated.STORE[n_new] = DEFINED (PARRAY n_live_array)',
            'n_live_array =/= n_new_array', 'n_live_array =/= n_copy_child',
            '$lookup(S_mutated.ENV, $ptascii("direct")) = (n_direct_cell)',
            'S_mutated.STORE[n_direct_cell] = DEFINED (PARRAY n_new_array)',
            item('S_mutated', 'n_live_array', 66), item('S_mutated', 'n_new_array', 44),
            item('S_mutated', 'n_copy_child', 55),
            '$entry_lookup(S_mutated.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
            '$heap_owners($heap_graph(S_mutated), HCELL n_new) = 1',
            '$heap_owners($heap_graph(S_mutated), HARRAY n_new_array) = 1',
            '$heap_owners($heap_graph(S_mutated), HARRAY n_live_array) = 1',
            '$heap_graph(S_mutated).DEBTS = [HCELL n_new]',
            '$literal_reference_debt_safe(S_mutated, $heap_graph(S_mutated))',
            '~$literal_reference_cell(S_mutated, n_new, [HCELL n_new])',
        ]
        inverse_start = 'S_mutated'
        live_array = 'n_live_array'
    else:
        inverse_start = 'S_copy'
        live_array = 'n_new_array'
    checks += seek(inverse_start, 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        f'S_inverse.STORE[n_new] = DEFINED (PARRAY {live_array})',
        'S_inverse.LITERALREFRETAINED = [n_old]', 'S_inverse.LITERALREFDEBTS = [n_new]',
        '$heap_owners($heap_graph(S_inverse), HCELL n_new) = 2',
    ] + seek('S_inverse', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3) :: ptask_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S_inverse_resume, n_balance, n_new, poperand_inverse)',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.TODO = (ARRAY_NEXT n_balance eps) :: ptask_inverse*',
        'S_balanced.LITERALREFRETAINED = eps', 'S_balanced.LITERALREFDEBTS = eps',
        'S_balanced.STORE = S_inverse_resume.STORE',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_balanced), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_balanced), HCELL n_old) = 3',
        f'$heap_owners($heap_graph(S_balanced), HARRAY {live_array}) = 1',
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        f'S_shared.STORE[n_new] = DEFINED (PARRAY {live_array})',
        item('S_shared', live_array, 77), item('S_shared', 'n_old_array', 33),
        item('S_shared', 'n_copy_child', 55),
        '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_probe',
        '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 0) = (ALIAS n_new)',
        '$heap_owners($heap_graph(S_shared), HCELL n_new) = 3',
        '$heap_owners($heap_graph(S_shared), HCELL n_old) = 3',
        f'$heap_owners($heap_graph(S_shared), HARRAY {live_array}) = 1',
        '$call_descriptors_valid(S_shared)', '$heap_valid($heap_graph(S_shared))',
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        '~((HCELL n_old) <- S_done.ALLOCATIONS)', '~((HCELL n_new) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_old_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_new_array) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_builder) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_balance) <- S_done.ALLOCATIONS)', '~((HARRAY n_probe) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy) <- S_done.ALLOCATIONS)', '~((HARRAY n_shared) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("outside")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_balanced_driven, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if not thrown:
        checks += [item('S_shared', 'n_new_array', 44), '~((HARRAY n_live_array) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
