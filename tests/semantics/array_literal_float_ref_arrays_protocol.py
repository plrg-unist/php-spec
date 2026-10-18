#!/usr/bin/env python3
"""Reached flat-array payloads separate wrapper and child-table ownership."""
import base64
import json

import array_literal_float_ref_arrays_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS, seek, driven


def payload(state, array, value, mixed=False):
    tail = (', ENTRY (KINT 4) (DIRECT PNULL), ENTRY (KINT 6) (DIRECT (PBOOL false)), '
            'ENTRY (KINT 8) (DIRECT (PFLOAT n_payload_bits))' if mixed else '')
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value})){tail}]'


def conditions(name, program, path, stdout):
    stable = name.endswith('same-cell')
    line, key = (11, 2) if stable else (14, 1)
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', f'i = {key}',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_old)', 'n_old <- S.REFCELLS',
        'S.STORE[n_old] = DEFINED (PARRAY n_old_array)', payload('S', 'n_old_array', 2, stable),
        '$lookup(S.ENV, $ptascii("seed")) = (n_seed)', 'S.STORE[n_seed] = DEFINED (PINT 2)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$propref_at(S.PROPREFS, n_old) = eps',
        '~$literal_reference_plain_cell(S, n_old)', '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
        '$literal_reference_flat_array(S, n_old_array, S.ALLOCATIONS)',
        '~$literal_reference_flat_array(S, n_old_array, eps)',
        '$heap_count(HARRAY n_old_array, $pools_nodes(S.POOLS)) = 0',
        '~$array_immutable(S, n_old_array)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$heap_owners($heap_graph(S), HCELL n_old) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_old_array) = 1',
        'S_immutable = S[.ARRAYS[n_old_array] = $array_empty()][.GC.IMMUTABLE = S.GC.IMMUTABLE ++ [n_old_array]]',
        '$array_immutable(S_immutable, n_old_array)',
        '$literal_reference_flat_items(S_immutable, S_immutable.ARRAYS[n_old_array].ITEMS)',
        '~$literal_reference_flat_array(S_immutable, n_old_array, S_immutable.ALLOCATIONS)',
        '~$array_float_ref_key_ready(S_immutable, n_builder, n_old, poperand)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
    ]
    if stable:
        checks += [
            '$float_long(n_payload_bits, true) = (1, [PRECISIONLOSS])',
            '$pools_nodes(S.POOLS) = (HARRAY n_pool) :: pnode_pool_tail*',
            '(HARRAY n_pool) <- S.ALLOCATIONS',
            'S_pool = S[.ARRAYS[n_pool] = S.ARRAYS[n_old_array]]',
            '~$array_immutable(S_pool, n_pool)',
            '$literal_reference_flat_items(S_pool, S_pool.ARRAYS[n_pool].ITEMS)',
            '~$literal_reference_flat_array(S_pool, n_pool, S_pool.ALLOCATIONS)',
        ]
    else:
        checks += [
            '$lookup(S.ENV, $ptascii("replacement")) = (n_new)',
            'n_new =/= n_old', '~(n_new <- S.REFCELLS)',
            'S.STORE[n_new] = DEFINED (PARRAY n_new_array)', 'n_new_array =/= n_old_array',
            payload('S', 'n_new_array', 44),
            '$heap_owners($heap_graph(S), HARRAY n_new_array) = 1',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LINE = z', 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = 3',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old_array) = 1',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_old_array, $tasks_nodes(pframe.TODO)) = 0',
        '$call_descriptors_valid(S_entered)',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.STORE[n_old] = DEFINED (PARRAY n_old_array)',
        payload('S_resume', 'n_old_array', 33, stable),
        'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
        '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
        '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
        'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
    ]
    if stable:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_old)',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_old)',
        ]
    else:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_resume.REFCELLS',
            'S_resume.STORE[n_new] = DEFINED (PARRAY n_new_array)', payload('S_resume', 'n_new_array', 44),
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
            'S_scalar = S_resume[.ENV = (BIND ($ptascii("q")) n_seed) :: $unbind(S_resume.ENV, $ptascii("q"))]',
            '$call_task_valid(S_scalar, ' + marker + ')',
            '$array_float_ref_key_value(S_scalar, n_old, poperand) = (DIRECT (PINT 2))',
            '~$array_float_ref_key_ready(S_scalar, n_builder, n_old, poperand)',
            '$error_read_discard(S_scalar, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
            'S_builder = S_resume[.STORE[n_new] = DEFINED (PARRAY n_builder)]',
            '$array_float_ref_key_value(S_builder, n_old, poperand) = (ALIAS n_new)',
            '$array_float_ref_key_builder_alias(S_builder, n_builder, ALIAS n_new)',
            '~$array_float_ref_key_ready(S_builder, n_builder, n_old, poperand)',
            '$error_read_discard(S_builder, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
            '~$array_float_ref_key_ready(S_builder[.STORE[n_old] = DEFINED (PINT 33)], n_builder, n_old, poperand)',
        ]
    inserted_cell = 'n_old' if stable else 'n_new'
    retained, debts = ('eps', 'eps') if stable else ('[n_old]', '[n_new]')
    checks += [
        'PhpStep: S_resume ~> S_insert',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        'S_insert.STORE = S_resume.STORE',
        'S_insert.LITERALREFRETAINED = ' + retained, 'S_insert.LITERALREFDEBTS = ' + debts,
        'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT ' + str(key) + ') (ALIAS ' + inserted_cell + ')]',
        '$heap_owners($heap_graph(S_insert), HARRAY n_old_array) = 1',
    ] + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        'S_read.LITERALREFRETAINED = ' + retained, 'S_read.LITERALREFDEBTS = ' + debts,
        payload('S_read', 'n_old_array', 33, stable),
    ]
    if stable:
        checks += [
            '$lookup(S_read.ENV, $ptascii("q")) = (n_old)',
            '$heap_owners($heap_graph(S_read), HCELL n_old) = 3',
        ] + seek('S_read', 16, 'S_shared') + [
            '$lookup(S_shared.ENV, $ptascii("q")) = eps', '$lookup(S_shared.ENV, $ptascii("outside")) = eps',
            '$lookup(S_shared.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_shared.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_builder',
            '$entry_lookup(S_shared.ARRAYS[n_builder].ITEMS, KINT 2) = (ALIAS n_old)',
            '$entry_lookup(S_shared.ARRAYS[n_copy].ITEMS, KINT 2) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_old_array', payload('S_shared', 'n_old_array', 33, True),
            payload('S_shared', 'n_copy_child', 55, True),
            '$heap_owners($heap_graph(S_shared), HCELL n_old) = 1',
            '$heap_count(HCELL n_old, $machine_roots(S_shared)) = 0',
            '$heap_owners($heap_graph(S_shared), HARRAY n_old_array) = 1',
            '$heap_owners($heap_graph(S_shared), HARRAY n_copy_child) = 1',
            'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        ]
        final_start = 'S_start'
    else:
        checks += [
            '$lookup(S_read.ENV, $ptascii("q")) = eps',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_builder',
            '$entry_lookup(S_read.ARRAYS[n_builder].ITEMS, KINT 1) = (ALIAS n_new)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_new_array', payload('S_read', 'n_copy_child', 55),
            payload('S_read', 'n_new_array', 44),
            '$heap_owners($heap_graph(S_read), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_read), HCELL n_new) = 1',
            '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HCELL n_new) = 2',
            '$heap_owners($heap_graph(S_read), HARRAY n_new_array) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_child) = 1',
            '$heap_graph(S_read).DEBTS = [HCELL n_new]',
            '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        ] + seek('S_read', 10, 'S_inverse') + [
            '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, 20, n_inverse_bits, 3))',
            'poperand_inverse = VARIABLE ($ptascii("q")) 20',
        ] + seek('S_inverse', 11, 'S_inverse_resume') + [
            'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps 20 n_inverse_bits 3) :: ptask_inverse*',
            '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
            '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
            'PhpStep: S_inverse_resume ~> S_balanced',
            'S_balanced.LITERALREFRETAINED = eps', 'S_balanced.LITERALREFDEBTS = eps',
            '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
            '$heap_owners($heap_graph(S_balanced), HCELL n_new) = 2',
            '$heap_owners($heap_graph(S_balanced), HCELL n_old) = 3',
        ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_shared') + [
            '$lookup(S_shared.ENV, $ptascii("shared")) = (n_shared_cell)',
            'S_shared.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_builder',
            '$entry_lookup(S_shared.ARRAYS[n_shared].ITEMS, KINT 1) = (ALIAS n_new)',
            payload('S_shared', 'n_new_array', 77), payload('S_shared', 'n_copy_child', 55),
            payload('S_shared', 'n_old_array', 33),
            '$heap_owners($heap_graph(S_shared), HCELL n_new) = 3',
            '$heap_owners($heap_graph(S_shared), HARRAY n_new_array) = 1',
            'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        ]
        final_start = 'S_balanced_driven'
    checks += [
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        '~((HCELL n_old) <- S_done.ALLOCATIONS)', '~((HARRAY n_old_array) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy_child) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(' + final_start + ', 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if not stable:
        checks += ['~((HCELL n_new) <- S_done.ALLOCATIONS)', '~((HARRAY n_new_array) <- S_done.ALLOCATIONS)',
                   '~((HARRAY n_balance) <- S_done.ALLOCATIONS)', '~((HARRAY n_shared) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
