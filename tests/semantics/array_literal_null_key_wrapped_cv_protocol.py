#!/usr/bin/env python3
"""NULL-key reset targets the captured reference payload after CV rebinding."""
import base64
import json

import array_literal_null_key_wrapped_cv_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_null_key_warning_protocol import HELPERS
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair


def conditions(name, program, path, stdout):
    array = name.endswith('array')
    line = 12 if array else 11
    args = 'n_a, n_capture, poperand, pvalue, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_RESULT n_a n_capture poperand pvalue phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_null_key_plan(S) = ((' + args + '))', f'z = {line}',
        'poperand = REFERENCE n_capture', 'S.RESULT = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_capture)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_capture)',
        'S.STORE[n_capture] = DEFINED pvalue', 'n_capture <- S.REFCELLS',
        '$propref_at(S.PROPREFS, n_capture) = eps',
        '$reference_coercion_at(S.REFCOERCIONS, n_capture) = eps',
        '$parameter_backing_at(S.PARAMETERBACKINGS, n_capture) = eps',
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'n_other =/= n_capture',
        'S.STORE[n_other] = DEFINED (PINT 99)', '~(n_other <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'n_key_cell =/= n_capture',
        'S.STORE[n_key_cell] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'n_key_name* = $ptascii("key")', 'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$array_float_key_value(S, VARIABLE n_key_name* z_key) = (PNULL)',
        'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$array_null_key_slot(S, n_capture, poperand) = (pvalue)',
        '$array_null_key_slot(S, n_capture, S.RESULT) = eps',
        '$array_null_key_source(S, ' + args + ')',
        '$array_null_key_ready(S, n_a, n_capture, poperand, pvalue)',
        '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        '$array_null_key_plan(S[.RESULT = KNOWN pvalue]) = eps',
        '$array_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 9)]) = eps',
        '~$array_null_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_null_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_null_key_source(S, n_a, n_capture, poperand, pvalue, phpType13*, $(z + 1))',
        '~$array_null_key_source(S, n_a, n_capture, REFERENCE n_other, pvalue, phpType13*, z)',
        '~$array_null_key_source(S, n_a, (|S.STORE|), REFERENCE (|S.STORE|), pvalue, phpType13*, z)',
        '~$array_null_key_ready(S, n_a, n_capture, poperand, PARRAY n_a)',
        '$heap_owners($heap_graph(S), HCELL n_capture) = 2',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
    ]
    if array:
        checks += [
            'pvalue = PARRAY n_old',
            '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)',
            'S.STORE[n_hold] = DEFINED (PARRAY n_old)', 'n_hold =/= n_capture',
            pair('S', 'n_old', 2, 7), '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
            '$array_null_key_slot(S[.LITERALARRAYDEBTS = [n_old]], n_capture, poperand) = eps',
        ]
    else:
        checks += [
            'pvalue = PINT 2', '$lookup(S.ENV, $ptascii("initial")) = (n_initial)',
            'n_initial =/= n_capture', 'S.STORE[n_initial] = DEFINED (PINT 2)',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '$task_nodes(' + marker + ') = ' + ('[HARRAY n_a, HARRAY n_old, HARRAY n_old]' if array else '[HARRAY n_a]'),
        '$heap_count(HCELL n_capture, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_capture) = 2',
    ] + empty_biases('S_dispatch')
    if array:
        checks += ['$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 4']
    checks += driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_capture, $tasks_nodes(pframe.TODO)) = 0',
    ]
    if array:
        checks += ['$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 2']
    checks += seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_other)',
        '$lookup(S_resume.ENV, $ptascii("outside")) = (n_capture)',
        'S_resume.STORE[n_other] = DEFINED (PINT 99)', 'n_other <- S_resume.REFCELLS',
        'n_capture <- S_resume.REFCELLS',
        '$heap_owners($heap_graph(S_resume), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_resume), HCELL n_other) = 2',
        '$array_null_key_slot(S_resume, n_capture, VARIABLE ($ptascii("q")) z) = eps',
        '$array_null_key_source(S_resume, ' + args + ')', '$call_task_valid(S_resume, ' + marker + ')',
        '$array_null_key_ready(S_resume, n_a, n_capture, poperand, pvalue)',
        'S_resume.STORE[n_key_cell] = DEFINED (PINT 9)',
        'S_resume.STORE[n_tail] = DEFINED (PINT 66)', 'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.GLOBALTABLE = eps',
        'S_lost = $unset_name(S_resume, $ptascii("outside"))',
        'H_lost = $heap_prune($heap_graph(S_lost)[.DEBTS = eps])',
        '~((HCELL n_capture) <- H_lost.NODES)', '(HCELL n_capture) <- S_lost.ALLOCATIONS',
        '$array_null_key_source(S_lost, ' + args + ')', '$call_task_valid(S_lost, ' + marker + ')',
        '~$array_null_key_ready(S_lost, n_a, n_capture, poperand, pvalue)',
        '$error_read_discard(S_lost, ' + marker + ').COMPLETION = UNSUPPORTED "array literal null-key value reset during throw"',
        'S_string = S_resume[.STORE[n_capture] = DEFINED (PSTRING eps)]',
        '~$array_null_key_ready(S_string, n_a, n_capture, poperand, pvalue)',
        'S_typed = S_resume[.PROPREFS = [{CELL n_capture, SOURCES eps}]]',
        '~$array_null_key_ready(S_typed, n_a, n_capture, poperand, pvalue)',
        'S_unmarked = S_resume[.REFCELLS = $literal_reference_delete(S_resume.REFCELLS, n_capture)]',
        '~$array_null_key_ready(S_unmarked, n_a, n_capture, poperand, pvalue)',
        'S_cell_debt = S_resume[.LITERALREFDEBTS = [n_capture]]',
        '~$array_null_key_ready(S_cell_debt, n_a, n_capture, poperand, pvalue)',
        'S_builder = S_resume[.STORE[n_capture] = DEFINED (PARRAY n_a)]',
        '~$array_null_key_ready(S_builder, n_a, n_capture, poperand, pvalue)',
    ] + empty_biases('S_resume')
    if array:
        checks += [
            'S_resume.STORE[n_capture] = DEFINED (PARRAY n_changed)', 'n_changed =/= n_old',
            pair('S_resume', 'n_changed', 55, 88), pair('S_resume', 'n_old', 2, 7),
            '$lookup(S_resume.ENV, $ptascii("changed")) = (n_changed_cell)',
            'S_resume.STORE[n_changed_cell] = DEFINED (PARRAY n_held_changed)',
            'n_held_changed =/= n_changed', pair('S_resume', 'n_held_changed', 44, 88),
            '$heap_owners($heap_graph(S_resume), HARRAY n_old) = 3',
            '$heap_owners($heap_graph(S_resume), HARRAY n_changed) = 1',
            '$heap_owners($heap_graph(S_resume), HARRAY n_held_changed) = 1',
        ]
    else:
        checks += ['S_resume.STORE[n_capture] = DEFINED (PINT 44)', '$array_null_key_slot(S_resume, n_capture, poperand) = (PINT 44)']
    checks += [
        'PhpStep: S_resume ~> S_insert',
        'S_insert.STORE[n_capture] = DEFINED pvalue',
        'S_insert.STORE[n_other] = DEFINED (PINT 99)',
        '$lookup(S_insert.ENV, $ptascii("q")) = (n_other)',
        '$lookup(S_insert.ENV, $ptascii("outside")) = (n_capture)',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT pvalue)',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.STORE[n_key_cell] = DEFINED (PINT 9)', 'S_insert.RESULT = KNOWN PNULL',
    ] + empty_biases('S_insert')
    if array:
        checks += ['$heap_owners($heap_graph(S_insert), HARRAY n_old) = 3', '$heap_owners($heap_graph(S_insert), HARRAY n_changed) = 0']
    checks += driven('S_resume', 'S_insert', 'S_insert_driven')
    if array:
        checks += ['~((HARRAY n_changed) <- S_insert_driven.ALLOCATIONS)', '(HARRAY n_held_changed) <- S_insert_driven.ALLOCATIONS']
    checks += seek('S_insert_driven', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT pvalue)',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        'S_read.STORE[n_capture] = DEFINED pvalue', 'S_read.STORE[n_other] = DEFINED (PINT 99)',
        '$lookup(S_read.ENV, $ptascii("q")) = (n_other)',
    ] + empty_biases('S_read')
    if array:
        checks += [
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_old', pair('S_read', 'n_copy_child', 66, 7), pair('S_read', 'n_old', 2, 7),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 3',
        ]
    else:
        checks += ['$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PINT 55))', 'S_read.STORE[n_initial] = DEFINED (PINT 2)']
    checks += seek('S_read', 16, 'S_cow') + [
        '$lookup(S_cow.ENV, $ptascii("q")) = (n_other)',
        'S_cow.STORE[n_other] = DEFINED (PINT 88)',
    ] + empty_biases('S_cow')
    if array:
        checks += [
            'S_cow.STORE[n_capture] = DEFINED (PARRAY n_outside_child)', 'n_outside_child =/= n_old',
            pair('S_cow', 'n_outside_child', 77, 7),
            '$entry_lookup(S_cow.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_entry_child))',
            'n_entry_child =/= n_old', pair('S_cow', 'n_entry_child', 2, 99),
            pair('S_cow', 'n_old', 2, 7), pair('S_cow', 'n_copy_child', 66, 7),
            pair('S_cow', 'n_held_changed', 44, 88), '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 1',
        ]
    else:
        checks += ['S_cow.STORE[n_capture] = DEFINED (PINT 77)', '$entry_lookup(S_cow.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 2))']
    checks += [
        '$drive_steps(S_cow, 0) = S_cow[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_cow, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~((HCELL n_capture) <- S_done.ALLOCATIONS)', '~((HCELL n_other) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_a) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
    ] + empty_biases('S_done')
    if array:
        checks += [f'~((HARRAY {n}) <- S_done.ALLOCATIONS)' for n in ('n_old', 'n_changed', 'n_held_changed', 'n_copy_child', 'n_outside_child', 'n_entry_child')]
    else:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
