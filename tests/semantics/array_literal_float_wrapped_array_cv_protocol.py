#!/usr/bin/env python3
"""Captured wrapped-CV payload slots are borrowed while array owners transfer."""
import base64
import json

import array_literal_float_wrapped_array_cv_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS, driven, seek


def empty_biases(state):
    return [f'{state}.{field} = eps' for field in
            ('LITERALREFRETAINED', 'LITERALREFDEBTS', 'LITERALARRAYRETAINED', 'LITERALARRAYDEBTS')]


def table(state, array, *values):
    entries = ', '.join(f'ENTRY (KINT {i}) (DIRECT (PINT {value}))' for i, value in enumerate(values))
    return f'{state}.ARRAYS[{array}].ITEMS = [{entries}]'


def conditions(name, program, path, stdout):
    stable = name.endswith('-stable')
    line = 11 if stable else 13
    old = (2,) if stable else (2, 7)
    args = 'n_a, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_a n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_b n_new poperand eps 20 n_inverse_bits 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        'poperand = REFERENCE n_capture', f'z = {line}', 'i = 1',
        'S.RESULT = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_capture)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_capture)',
        '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_hold =/= n_capture',
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'n_other =/= n_capture',
        'n_capture <- S.REFCELLS', '~(n_hold <- S.REFCELLS)', '~(n_other <- S.REFCELLS)',
        'S.STORE[n_capture] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        'S.STORE[n_other] = DEFINED (PINT 99)', table('S', 'n_old', *old),
        '$array_float_key_value(S, S.RESULT) = eps', '$array_float_key_plan(S) = eps',
        '$array_float_array_key_value(S, S.RESULT) = eps',
        '$array_float_array_key_reference(S, n_capture) = (n_old)',
        '$array_float_array_key_item(S, poperand) = (DIRECT (PARRAY n_old))',
        '$array_float_array_key_source(S, ' + args + ')',
        '$array_float_array_key_ready(S, n_a, n_old, poperand)',
        '~$array_float_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_array_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_array_key_source(S, n_a, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_array_key_source(S, n_a, n_old, REFERENCE (|S.STORE|), phpType13*, z, n_bits, i)',
        '$array_float_array_key_plan(S[.STORE[n_capture] = DEFINED (PSTRING eps)]) = eps',
        '$heap_owners($heap_graph(S), HCELL n_capture) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
    ]
    if not stable:
        checks += [
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            'S.STORE[n_replacement] = DEFINED (PARRAY n_new)', 'n_new =/= n_old',
            table('S', 'n_new', 44, 8), '$heap_owners($heap_graph(S), HARRAY n_new) = 1',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', f'perrorcall.LINE = {line}',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_old]',
        '$heap_count(HCELL n_capture, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_capture) = 2',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_capture, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_other)',
        '$lookup(S_resume.ENV, $ptascii("outside")) = (n_capture)',
        'n_other <- S_resume.REFCELLS', 'n_capture <- S_resume.REFCELLS',
        'S_resume.STORE[n_other] = DEFINED (PINT 99)',
        'S_resume.STORE[n_capture] = DEFINED (PARRAY n_current)',
        '$array_float_array_key_item(S_resume, poperand) = (DIRECT (PARRAY n_current))',
        '$array_float_array_key_value(S_resume, poperand) = eps',
        '$array_float_key_live_value(S_resume, poperand) = eps',
        '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_array_key_ready(S_resume, n_a, n_old, poperand)',
        '$heap_owners($heap_graph(S_resume), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_resume), HCELL n_other) = 2',
        'S_resume.GLOBALTABLE = eps',
        'S_unrooted = $unset_name(S_resume, $ptascii("outside"))',
        '(HCELL n_capture) <- S_unrooted.ALLOCATIONS',
        'H_unrooted = $heap_prune($heap_graph(S_unrooted)[.DEBTS = eps])',
        '~((HCELL n_capture) <- H_unrooted.NODES)', '(HARRAY n_current) <- H_unrooted.NODES',
        '$array_float_array_key_source(S_unrooted, ' + args + ')',
        '$call_task_valid(S_unrooted, ' + marker + ')',
        '$array_float_array_key_reference(S_unrooted, n_capture) = eps',
        '$array_float_array_key_item(S_unrooted, poperand) = eps',
        '~$array_float_array_key_ready(S_unrooted, n_a, n_old, poperand)',
        '$error_read_discard(S_unrooted, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        'S_cell_debt = S_resume[.LITERALREFDEBTS = [n_capture]]',
        '$array_float_array_key_reference(S_cell_debt, n_capture) = eps',
        'S_typed = S_resume[.PROPREFS = [{CELL n_capture, SOURCES eps}]]',
        '$array_float_array_key_reference(S_typed, n_capture) = eps',
        'S_string = S_resume[.STORE[n_capture] = DEFINED (PSTRING eps)]',
        '$array_float_array_key_item(S_string, poperand) = eps',
        '~$array_float_array_key_ready(S_string, n_a, n_old, poperand)',
        'S_builder = S_resume[.STORE[n_capture] = DEFINED (PARRAY n_a)]',
        '$array_float_array_key_item(S_builder, poperand) = (DIRECT (PARRAY n_a))',
        '~$array_float_array_key_ready(S_builder, n_a, n_old, poperand)',
        '$error_read_discard(S_builder, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key array CV during throw"',
        'PhpStep: S_resume ~> S_insert', 'S_insert.STORE = S_resume.STORE',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT (PARRAY n_current))',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.LITERALREFRETAINED = eps', 'S_insert.LITERALREFDEBTS = eps',
    ]
    if stable:
        checks += [
            'n_current = n_old', 'S_insert.LITERALARRAYRETAINED = eps', 'S_insert.LITERALARRAYDEBTS = eps',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 3',
        ]
    else:
        checks += [
            'n_current = n_new', 'S_insert.LITERALARRAYRETAINED = [n_old]',
            'S_insert.LITERALARRAYDEBTS = [n_new]',
            '$heap_owners($heap_graph(S_insert), HARRAY n_new) = 2',
            '$heap_owners($heap_graph(S_insert)[.DEBTS = eps], HARRAY n_new) = 3',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
        ]
    checks += driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_current',
        'S_read.STORE[n_capture] = DEFINED (PARRAY n_live)',
        '$heap_owners($heap_graph(S_read), HCELL n_capture) = 1',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
    ]
    if stable:
        checks += [
            'n_live =/= n_old', table('S_read', 'n_live', 55),
            table('S_read', 'n_old', 2), table('S_read', 'n_copy_child', 66),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_read), HARRAY n_live) = 1',
        ] + empty_biases('S_read')
        start = 'S_read'
    else:
        checks += [
            '$lookup(S_read.ENV, $ptascii("replacement")) = eps', 'n_live = n_new',
            table('S_read', 'n_new', 55, 8), table('S_read', 'n_copy_child', 66, 8),
            '$node_children(S_read, HCELL n_capture) = [HARRAY n_new]',
            '$heap_owners($heap_graph(S_read), HARRAY n_new) = 1',
            '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_new) = 2',
            'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_new]',
            '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        ] + seek('S_read', 10, 'S_inverse') + [
            '$array_float_array_key_plan(S_inverse) = ((n_b, n_new, poperand, eps, 20, n_inverse_bits, 3))',
            '$lookup(S_inverse.ENV, $ptascii("q")) = (n_capture)',
            '$array_float_array_key_reference(S_inverse, n_capture) = (n_new)',
            '$heap_owners($heap_graph(S_inverse), HARRAY n_new) = 1',
            'PhpStep: S_inverse ~> S_inverse_dispatch',
            'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
            'perrorcall_inverse.RESUME = ' + inverse,
            '$task_nodes(' + inverse + ') = [HARRAY n_b, HARRAY n_new]',
            '$heap_owners($heap_graph(S_inverse_dispatch), HARRAY n_new) = 2',
            '$heap_owners($heap_graph(S_inverse_dispatch), HCELL n_capture) = 2',
        ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 11, 'S_inverse_resume') + [
            'S_inverse_resume.TODO = (' + inverse + ') :: ptask_inverse_after*',
            '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_other)',
            'S_inverse_resume.STORE[n_capture] = DEFINED (PARRAY n_old)',
            '$array_float_array_key_item(S_inverse_resume, poperand) = (DIRECT (PARRAY n_old))',
            '$array_float_array_key_ready(S_inverse_resume, n_b, n_new, poperand)',
            '$array_float_array_key_source(S_inverse_resume, n_b, n_new, poperand, eps, 20, n_inverse_bits, 3)',
            'S_discard = $error_read_discard(S_inverse_resume, ' + inverse + ')',
        ] + empty_biases('S_discard') + [
            'PhpStep: S_inverse_resume ~> S_balanced',
            '$entry_lookup(S_balanced.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
            '$heap_owners($heap_graph(S_balanced), HARRAY n_old) = 3',
            '$heap_owners($heap_graph(S_balanced), HARRAY n_new) = 1',
        ] + empty_biases('S_balanced') + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven')
        start = 'S_balanced_driven'
    checks += seek(start, 16, 'S_cow') + [
        '$lookup(S_cow.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_cow.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)', 'n_shared =/= n_a',
        '$entry_lookup(S_cow.ARRAYS[n_shared].ITEMS, KINT 1) = (DIRECT (PARRAY n_shared_child))',
        'n_shared_child =/= n_current', 'n_shared_child =/= n_copy_child',
        'S_cow.STORE[n_capture] = DEFINED (PARRAY n_outside)',
        'S_cow.STORE[n_other] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_cow), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_cow), HCELL n_other) = 2',
        '$heap_owners($heap_graph(S_cow), HARRAY n_shared_child) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_copy_child) = 1',
    ] + empty_biases('S_cow')
    if stable:
        checks += [
            'n_outside = n_live', table('S_cow', 'n_live', 55),
            table('S_cow', 'n_old', 2), table('S_cow', 'n_copy_child', 66), table('S_cow', 'n_shared_child', 77),
            'S_cow.STORE[n_hold] = DEFINED (PARRAY n_hold_cow)', 'n_hold_cow =/= n_old',
            table('S_cow', 'n_hold_cow', 88), '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 1',
        ]
        retired = ['n_hold_cow']
    else:
        checks += [
            'n_outside =/= n_old', table('S_cow', 'n_outside', 88, 7),
            table('S_cow', 'n_new', 55, 8), table('S_cow', 'n_copy_child', 66, 8),
            table('S_cow', 'n_shared_child', 77, 8), table('S_cow', 'n_old', 2, 7),
            '$lookup(S_cow.ENV, $ptascii("balance_copy")) = (n_balance_copy_cell)',
            'S_cow.STORE[n_balance_copy_cell] = DEFINED (PARRAY n_balance_copy)', 'n_balance_copy =/= n_b',
            '$entry_lookup(S_cow.ARRAYS[n_balance_copy].ITEMS, KINT 3) = (DIRECT (PARRAY n_balance_copy_child))',
            'n_balance_copy_child =/= n_old', table('S_cow', 'n_balance_copy_child', 99, 7),
            '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 2',
        ]
        retired = ['n_b', 'n_balance_copy', 'n_balance_copy_child', 'n_new']
    checks += [
        'S_done = $drive_steps(S_cow, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HCELL n_capture) <- S_done.ALLOCATIONS)', '~((HCELL n_other) <- S_done.ALLOCATIONS)',
        *[f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in
          ['n_a', 'n_old', 'n_copy', 'n_copy_child', 'n_shared', 'n_shared_child', 'n_live', 'n_outside', *retired]],
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        'S_split_found = $drive_steps(S_cow, 1)', 'S_split_found.COMPLETION = BUDGET',
        '$drive_steps(S_split_found[.COMPLETION = NORMAL], 2000) = S_done',
    ] + empty_biases('S_done')
    if stable:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
