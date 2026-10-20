#!/usr/bin/env python3
"""Reached owning-reference protection transfers into scalar-retarget owners."""
import base64
import json

import array_literal_float_ref_array_scalar_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS as BASE_HELPERS, seek, driven

HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 17) = $literal_deficit_review_echo(S, $ptascii("G:"))
def $list_warning_frontier(S, 18) = $literal_deficit_review_echo(S, $ptascii("C:"))
'''


def item(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def conditions(name, program, path, stdout):
    thrown = name.endswith('throw')
    line = 13 if thrown else 11
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', 'i = 1',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_old)', 'n_old <- S.REFCELLS',
        'S.STORE[n_old] = DEFINED (PARRAY n_old_array)', item('S', 'n_old_array', 2),
        '$literal_reference_cell(S, n_old, S.ALLOCATIONS)',
        '$literal_reference_flat_array(S, n_old_array, S.ALLOCATIONS)',
        '$heap_count(HARRAY n_old_array, $pools_nodes(S.POOLS)) = 0',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$heap_owners($heap_graph(S), HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners($heap_graph(S), HARRAY n_old_array) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LINE = z', 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = ' + ('4' if thrown else '3'),
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old_array) = 1',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_old_array, $tasks_nodes(pframe.TODO)) = 0',
        '$call_descriptors_valid(S_entered)',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_old)]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps',
            'S_start.ERRORHANDLER = S.ERRORHANDLER',
            'S_start.STORE[n_dest] = DEFINED (PINT 99)', 'S_start.STORE[n_later] = DEFINED (PINT 7)',
            '~((HARRAY n_builder) <- S_start.ALLOCATIONS)',
            '$lookup(S_start.ENV, $ptascii("q")) = (n_current)', 'n_current =/= n_old',
            '~(n_current <- S_start.REFCELLS)', 'S_start.STORE[n_current] = DEFINED (PINT 44)',
            'S_start.STORE[n_old] = DEFINED (PARRAY n_old_array)', item('S_start', 'n_old_array', 33),
            'S_start.LITERALREFRETAINED = [n_old]', 'S_start.LITERALREFDEBTS = eps',
            '$heap_owners($heap_graph(S_start), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_start), HARRAY n_old_array) = 1',
            '$call_descriptors_valid(S_start)', '$heap_valid($heap_graph(S_start))',
        ]
    else:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_current)', 'n_current =/= n_old',
            '~(n_current <- S_resume.REFCELLS)', 'S_resume.STORE[n_current] = DEFINED (PINT 44)',
            'S_resume.STORE[n_old] = DEFINED (PARRAY n_old_array)', item('S_resume', 'n_old_array', 33),
            'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (8, [PRECISIONLOSS])',
            '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (DIRECT (PINT 44))',
            '$array_float_ref_key_old_payload(S_resume, n_builder, n_old, DIRECT (PINT 44))',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
            'S_owning = S_resume[.STORE[n_current] = DEFINED (PSTRING eps)]',
            '$call_task_valid(S_owning, ' + marker + ')',
            '$array_float_ref_key_value(S_owning, n_old, poperand) = eps',
            '~$array_float_ref_key_ready(S_owning, n_builder, n_old, poperand)',
            '$error_read_discard(S_owning, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
            '~$array_float_ref_key_ready(S_resume[.STORE[n_old] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
            'S_nested = S_resume[.ARRAYS[n_old_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_array))]]',
            '~$array_float_ref_key_ready(S_nested, n_builder, n_old, poperand)',
            '$error_read_discard(S_nested, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
            'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
            'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = eps',
            'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (DIRECT (PINT 44))]',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 8) = eps',
            '$heap_owners($heap_graph(S_insert), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old_array) = 1',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_read') + [
        'S_read.LITERALREFRETAINED = [n_old]', 'S_read.LITERALREFDEBTS = eps',
        'S_read.STORE[n_old] = DEFINED (PARRAY n_old_array)', item('S_read', 'n_old_array', 33),
        '$heap_owners($heap_graph(S_read), HCELL n_old) = 2',
        '$heap_owners($heap_graph(S_read), HARRAY n_old_array) = 1',
    ]
    if not thrown:
        checks += [
            'S_read.STORE[n_current] = DEFINED (PINT 55)',
            'S_read.STORE[n_dest] = DEFINED (PARRAY n_builder)',
            'S_read.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 1) (DIRECT (PINT 44)), ENTRY (KINT 4) (DIRECT (PINT 66))]',
        ]
    checks += seek('S_read', 17, 'S_ghost') + [
        '$lookup(S_ghost.ENV, $ptascii("q")) = eps', '$lookup(S_ghost.ENV, $ptascii("outside")) = eps',
        '$lookup(S_ghost.ENV, $ptascii("probe")) = (n_probe_cell)',
        '$lookup(S_ghost.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_ghost.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
        'S_ghost.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_probe =/= n_copy',
        '$entry_lookup(S_ghost.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_old)',
        '$entry_lookup(S_ghost.ARRAYS[n_copy].ITEMS, KINT 0) = (ALIAS n_old)',
        'S_ghost.STORE[n_old] = DEFINED (PARRAY n_old_array)', item('S_ghost', 'n_old_array', 55),
        'S_ghost.LITERALREFRETAINED = [n_old]', 'S_ghost.LITERALREFDEBTS = eps',
        '$heap_count(HCELL n_old, $machine_roots(S_ghost)) = 1',
        '$heap_owners($heap_graph(S_ghost), HCELL n_old) = 3',
        '$heap_owners($heap_graph(S_ghost), HARRAY n_old_array) = 1',
    ] + seek('S_ghost', 16 if thrown else 18, 'S_cow') + [
        '$lookup(S_cow.ENV, $ptascii("direct")) = (n_direct_cell)',
        'S_cow.STORE[n_direct_cell] = DEFINED (PARRAY n_old_array)',
        'S_cow.STORE[n_old] = DEFINED (PARRAY n_child)', 'n_child =/= n_old_array',
        item('S_cow', 'n_old_array', 55), item('S_cow', 'n_child', 66),
        '$entry_lookup(S_cow.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_old)',
        '$entry_lookup(S_cow.ARRAYS[n_copy].ITEMS, KINT 0) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_cow), HCELL n_old) = 3',
        '$heap_owners($heap_graph(S_cow), HARRAY n_old_array) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_child) = 1',
        'S_cow.LITERALREFRETAINED = [n_old]', 'S_cow.LITERALREFDEBTS = eps',
        'S_done = $drive_steps(S_cow, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = [n_old]', 'S_done.LITERALREFDEBTS = eps',
        'S_done.STORE[n_old] = DEFINED (PARRAY n_child)', item('S_done', 'n_child', 66),
        '(HCELL n_old) <- S_done.ALLOCATIONS', '(HARRAY n_child) <- S_done.ALLOCATIONS',
        '$heap_count(HCELL n_old, $machine_roots(S_done)) = 1',
        '$heap_owners($heap_graph(S_done), HCELL n_old) = 1',
        '$heap_owners($heap_graph(S_done), HARRAY n_child) = 1',
        '~((HARRAY n_old_array) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_probe) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$literal_reference_retained_valid(S_done, S_done.LITERALREFRETAINED)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_cow, 1) = $drive_steps($drive_steps(S_cow, 0)[.COMPLETION = NORMAL], 1)',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
