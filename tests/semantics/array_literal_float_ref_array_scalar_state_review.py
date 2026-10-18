#!/usr/bin/env python3
"""Reached array-to-scalar transfers cancel debt or retain repeated old owners."""
import base64
import json

import array_literal_float_ref_array_scalar_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS as BASE_HELPERS, seek, driven

HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 17) = $literal_deficit_review_echo(S, $ptascii("G:"))
'''


def payload(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def conditions(name, program, path, stdout):
    cancel = name.endswith('cancel-debt')
    line1, line2, key2 = (19, 23, 3) if cancel else (15, 19, 2)
    old2 = 'n_new' if cancel else 'n_old'
    value1 = 'ALIAS n_new' if cancel else 'DIRECT (PINT 41)'
    value2 = 99 if cancel else 42
    debts1 = '[n_new]' if cancel else 'eps'
    retained2 = '[n_old]' if cancel else '[n_old, n_old]'
    marker1 = 'ARRAY_KEY_FLOAT_REF_RESULT n_a n_old poperand_one phpType13* z_one n_bits_one 1'
    marker2 = f'ARRAY_KEY_FLOAT_REF_RESULT n_b {old2} poperand_two eps z_two n_bits_two {key2}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps', 'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S_one') + [
        '$array_float_ref_key_plan(S_one) = ((n_a, n_old, poperand_one, phpType13*, z_one, n_bits_one, 1))',
        f'z_one = {line1}', 'poperand_one = VARIABLE ($ptascii("q")) z_one',
        '$lookup(S_one.ENV, $ptascii("q")) = (n_old)', '$lookup(S_one.ENV, $ptascii("outside")) = (n_old)',
        'n_old <- S_one.REFCELLS', '$heap_owners($heap_graph(S_one), HCELL n_old) = 2',
        '$lookup(S_one.ENV, $ptascii("key")) = (n_key)', 'S_one.STORE[n_key] = DEFINED (PFLOAT n_bits_one)',
        '$array_float_ref_key_source(S_one, n_a, n_old, poperand_one, phpType13*, z_one, n_bits_one, 1)',
        '~$array_float_ref_key_source(S_one[.ORIGIN = eps], n_a, n_old, poperand_one, phpType13*, z_one, n_bits_one, 1)',
        '~$array_float_ref_key_source(S_one[.CODE = eps], n_a, n_old, poperand_one, phpType13*, z_one, n_bits_one, 1)',
        'PhpStep: S_one ~> S_one_dispatch',
        'S_one_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_one) :: ptask_tail_one*',
        'perrorcall_one.RESUME = ' + marker1, 'perrorcall_one.LEVEL = 8192', 'perrorcall_one.LINE = z_one',
        '$error_call_valid(S_one_dispatch, perrorcall_one)',
        '~$error_call_valid(S_one_dispatch, perrorcall_one[.LINE = $(z_one + 1)])',
        '$task_nodes(' + marker1 + ') = [HARRAY n_a, HCELL n_old]',
    ]
    if cancel:
        checks += [
            'S_one.STORE[n_old] = DEFINED (PINT 2)', '$lookup(S_one.ENV, $ptascii("replacement")) = (n_new)',
            'S_one.STORE[n_new] = DEFINED (PARRAY n_original)', payload('S_one', 'n_original', 44),
            '~(n_new <- S_one.REFCELLS)',
        ]
    else:
        checks += ['S_one.STORE[n_old] = DEFINED (PARRAY n_original)', payload('S_one', 'n_original', 2)]
    checks += driven('S_one', 'S_one_dispatch', 'S_one_driven') + seek('S_one_driven', 13, 'S_one_entered') + [
        'S_one_entered.FRAMES = pframe_one :: pframe_tail_one*',
        'pframe_one.TODO = (ERROR_HANDLER_RESULT perrorcall_entered_one) :: ptask_caller_one*',
        'perrorcall_entered_one.RESUME = ' + marker1,
    ] + seek('S_one_entered', 11, 'S_one_resume') + [
        'S_one_resume.TODO = (' + marker1 + ') :: ptask_after_one*',
        '$array_float_ref_key_value(S_one_resume, n_old, poperand_one) = (' + value1 + ')',
        '$array_float_ref_key_ready(S_one_resume, n_a, n_old, poperand_one)',
    ]
    if cancel:
        checks += ['S_one_resume.STORE[n_old] = DEFINED (PINT 33)',
                   '$lookup(S_one_resume.ENV, $ptascii("q")) = (n_new)',
                   'S_one_resume.STORE[n_new] = DEFINED (PARRAY n_original)']
    else:
        checks += [payload('S_one_resume', 'n_original', 31),
                   '$lookup(S_one_resume.ENV, $ptascii("q")) = (n_current_one)',
                   'S_one_resume.STORE[n_current_one] = DEFINED (PINT 41)', '~(n_current_one <- S_one_resume.REFCELLS)']
    checks += [
        'PhpStep: S_one_resume ~> S_one_insert',
        'S_one_insert.LITERALREFRETAINED = [n_old]', 'S_one_insert.LITERALREFDEBTS = ' + debts1,
        '$entry_lookup(S_one_insert.ARRAYS[n_a].ITEMS, KINT 1) = (' + value1 + ')',
        '$heap_owners($heap_graph(S_one_insert), HARRAY n_original) = 1',
    ] + driven('S_one_resume', 'S_one_insert', 'S_first') + seek('S_first', 10, 'S_two') + [
        f'$array_float_ref_key_plan(S_two) = ((n_b, {old2}, poperand_two, eps, z_two, n_bits_two, {key2}))',
        f'z_two = {line2}', 'poperand_two = VARIABLE ($ptascii("q")) z_two', 'n_b =/= n_a',
        'S_two.LITERALREFRETAINED = [n_old]', 'S_two.LITERALREFDEBTS = ' + debts1,
        f'S_two.STORE[{old2}] = DEFINED (PARRAY n_original)',
        '$heap_owners($heap_graph(S_two), HCELL ' + old2 + ') = ' + ('2' if cancel else '3'),
        '$heap_owners($heap_graph(S_two), HARRAY n_original) = ' + ('2' if cancel else '1'),
        'PhpStep: S_two ~> S_two_dispatch',
        'S_two_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_two) :: ptask_tail_two*',
        'perrorcall_two.RESUME = ' + marker2, 'perrorcall_two.LEVEL = 8192', 'perrorcall_two.LINE = z_two',
        '$error_call_valid(S_two_dispatch, perrorcall_two)',
        '$task_nodes(' + marker2 + ') = [HARRAY n_b, HCELL ' + old2 + ']',
    ] + driven('S_two', 'S_two_dispatch', 'S_two_driven') + seek('S_two_driven', 13, 'S_two_entered') + [
        'S_two_entered.FRAMES = pframe_two :: pframe_tail_two*',
        'pframe_two.TODO = (ERROR_HANDLER_RESULT perrorcall_entered_two) :: ptask_caller_two*',
        'perrorcall_entered_two.RESUME = ' + marker2,
    ] + seek('S_two_entered', 11, 'S_two_resume') + [
        'S_two_resume.TODO = (' + marker2 + ') :: ptask_after_two*',
        '$lookup(S_two_resume.ENV, $ptascii("q")) = (n_current_two)', f'n_current_two =/= {old2}',
        '~(n_current_two <- S_two_resume.REFCELLS)', f'S_two_resume.STORE[n_current_two] = DEFINED (PINT {value2})',
        f'$array_float_ref_key_value(S_two_resume, {old2}, poperand_two) = (DIRECT (PINT {value2}))',
        f'$array_float_ref_key_ready(S_two_resume, n_b, {old2}, poperand_two)',
        f'$array_float_ref_key_source(S_two_resume[.ENV = eps], n_b, {old2}, poperand_two, eps, z_two, n_bits_two, {key2})',
        f'~$array_float_ref_key_ready(S_two_resume[.STORE[{old2}] = DEFINED (PARRAY n_b)], n_b, {old2}, poperand_two)',
        'S_owning = S_two_resume[.STORE[n_current_two] = DEFINED (PARRAY n_original)]',
        f'$array_float_ref_key_value(S_owning, {old2}, poperand_two) = eps',
        f'~$array_float_ref_key_ready(S_owning, n_b, {old2}, poperand_two)',
        '$error_read_discard(S_owning, ' + marker2 + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
    ]
    if cancel:
        checks += ['S_two_resume.STORE[n_new] = DEFINED (PARRAY n_live)', 'n_live =/= n_original',
                   payload('S_two_resume', 'n_live', 66), payload('S_two_resume', 'n_original', 44),
                   'S_two_resume.LITERALREFDEBTS = [n_new]',
                   '$heap_owners($heap_graph(S_two_resume), HARRAY n_live) = 1',
                   '$heap_owners($heap_graph(S_two_resume), HARRAY n_original) = 1']
        live = 'n_live'
    else:
        checks += [payload('S_two_resume', 'n_original', 32),
                   '~((HCELL n_current_one) <- S_two_resume.ALLOCATIONS)']
        live = 'n_original'
    checks += [
        'PhpStep: S_two_resume ~> S_two_insert',
        'S_two_insert.STORE = S_two_resume.STORE', 'S_two_insert.LITERALREFRETAINED = ' + retained2,
        'S_two_insert.LITERALREFDEBTS = eps',
        f'$entry_lookup(S_two_insert.ARRAYS[n_b].ITEMS, KINT {key2}) = (DIRECT (PINT {value2}))',
        '$heap_owners($heap_graph(S_two_insert), HCELL ' + old2 + ') = ' + ('2' if cancel else '3'),
        f'$heap_owners($heap_graph(S_two_insert), HARRAY {live}) = 1',
        '$heap_graph(S_two_insert).DEBTS = eps',
    ] + driven('S_two_resume', 'S_two_insert', 'S_second') + seek('S_second', 15, 'S_read') + [
        'S_read.LITERALREFRETAINED = ' + retained2, 'S_read.LITERALREFDEBTS = eps',
        f'$entry_lookup(S_read.ARRAYS[n_b].ITEMS, KINT {key2}) = (DIRECT (PINT {value2}))',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
    ]
    if cancel:
        checks += [
            'S_read.STORE[n_new] = DEFINED (PARRAY n_live)', payload('S_read', 'n_live', 66),
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 1) = (ALIAS n_new)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_live', payload('S_read', 'n_copy_child', 55),
            '$lookup(S_read.ENV, $ptascii("snapshot")) = (n_snapshot_cell)',
            'S_read.STORE[n_snapshot_cell] = DEFINED (PARRAY n_original)', payload('S_read', 'n_original', 44),
            '$heap_owners($heap_graph(S_read), HCELL n_new) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_live) = 1',
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_child) = 1',
        ] + seek('S_read', 17, 'S_final_front') + [
            'S_final_front.STORE[n_old] = DEFINED (PINT 77)',
            '$heap_owners($heap_graph(S_final_front), HCELL n_old) = 3',
            'S_final_front.LITERALREFRETAINED = [n_old]', 'S_final_front.LITERALREFDEBTS = eps',
        ]
    else:
        checks += [
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT (PINT 41))',
            '$lookup(S_read.ENV, $ptascii("probe")) = (n_probe_cell)',
            'S_read.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
            '$entry_lookup(S_read.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_old)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 0) = (ALIAS n_old)',
            'n_copy =/= n_probe', payload('S_read', 'n_original', 66),
            '$heap_owners($heap_graph(S_read), HCELL n_old) = 4',
            '$heap_owners($heap_graph(S_read), HARRAY n_original) = 1',
            '$heap_count(HCELL n_old, $literal_reference_retained_nodes(S_read.LITERALREFRETAINED)) = 2',
            '$lookup(S_read.ENV, $ptascii("outside")) = eps',
            'S_final_front = S_read',
        ]
    checks += [
        'S_done = $drive_steps(S_final_front, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = ' + retained2, 'S_done.LITERALREFDEBTS = eps',
        '(HCELL n_old) <- S_done.ALLOCATIONS',
        '$heap_owners($heap_graph(S_done), HCELL n_old) = ' + ('1' if cancel else '2'),
        '~((HARRAY n_a) <- S_done.ALLOCATIONS)', '~((HARRAY n_b) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("outside")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_two, 0) = S_two[.COMPLETION = BUDGET]',
        '$drive_steps(S_second, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if cancel:
        checks += ['~((HCELL n_new) <- S_done.ALLOCATIONS)', '~((HARRAY n_original) <- S_done.ALLOCATIONS)',
                   '~((HARRAY n_live) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy_child) <- S_done.ALLOCATIONS)',
                   'S_done.STORE[n_old] = DEFINED (PINT 77)']
    else:
        checks += ['(HARRAY n_original) <- S_done.ALLOCATIONS', payload('S_done', 'n_original', 66),
                   '$heap_owners($heap_graph(S_done), HARRAY n_original) = 1',
                   '$heap_count(HARRAY n_original, $machine_roots(S_done)) = 0',
                   '~((HARRAY n_probe) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
