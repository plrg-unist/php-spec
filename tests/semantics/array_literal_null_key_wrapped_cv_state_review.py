#!/usr/bin/env python3
"""NULL-key reset restores a captured wrapped slot after its CV rebinds."""
import base64
import json

import array_literal_null_key_wrapped_cv_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_null_key_warning_state_review import HELPERS
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line = 13 if thrown else 11
    args = 'n_a, n_capture, poperand, pvalue_snapshot, phpType13*, z'
    ready = 'n_a, n_capture, poperand, pvalue_snapshot'
    marker = 'ARRAY_KEY_NULL_RESULT n_a n_capture poperand pvalue_snapshot phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 20, 'S') + [
        '$array_null_key_plan(S) = ((' + args + '))', f'z = {line}',
        'poperand = REFERENCE n_capture', 'S.RESULT = VARIABLE ($ptascii("q")) z',
        'pvalue_snapshot = PARRAY n_old', 'n_a =/= n_old',
        '$lookup(S.ENV, $ptascii("q")) = (n_capture)',
        'S.STORE[n_capture] = DEFINED pvalue_snapshot', 'n_capture <- S.REFCELLS',
        '$lookup(S.ENV, $ptascii("outside")) = (n_capture)',
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'n_other =/= n_capture',
        'S.STORE[n_other] = DEFINED (PINT 99)', '~(n_other <- S.REFCELLS)',
        '$heap_count(HCELL n_capture, $machine_roots(S)) = 2',
        '$propref_at(S.PROPREFS, n_capture) = eps',
        '$reference_coercion_at(S.REFCOERCIONS, n_capture) = eps',
        '$parameter_backing_at(S.PARAMETERBACKINGS, n_capture) = eps',
        '$lookup(S.ENV, $ptascii("seed")) = eps',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'n_key =/= n_capture',
        'S.STORE[n_key] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        pair('S', 'n_old', 2, 7),
        '$array_null_key_payload(S, pvalue_snapshot, S.ALLOCATIONS)',
        '$array_null_key_slot(S, n_capture, poperand) = (pvalue_snapshot)',
        '$array_null_key_source(S, ' + args + ')', '$array_null_key_ready(S, ' + ready + ')',
        '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 1',
        '$heap_count(HARRAY n_old, $machine_roots(S)) = 0',
        '~$array_null_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_null_key_source(S, n_a, n_capture, poperand, pvalue_snapshot, phpType13*, $(z + 1))',
        '$array_null_key_plan(S[.STORE[n_key] = DEFINED (PINT 9)]) = eps',
        '$array_null_key_slot(S[.REFCELLS = eps], n_capture, poperand) = eps',
        '$array_null_key_slot(S, n_capture, VARIABLE ($ptascii("q")) z) = eps',
        '$array_null_key_slot(S, n_capture, REFERENCE n_other) = eps',
        '~$array_null_key_source(S, n_a, n_capture, REFERENCE n_other, pvalue_snapshot, phpType13*, z)',
        '$array_null_key_slot(S[.PROPREFS = [{CELL n_capture, SOURCES eps}]], n_capture, poperand) = eps',
        '$array_null_key_slot(S[.STORE[n_capture] = UNDEFINED], n_capture, poperand) = eps',
        '$array_null_key_slot(S[.STORE[n_capture] = DEFINED (PSTRING eps)], n_capture, poperand) = eps',
        '$array_null_key_slot(S[.LITERALREFDEBTS = [n_capture]], n_capture, poperand) = eps',
        '~$array_null_key_payload(S, pvalue_snapshot, [HCELL n_capture])',
        '~$array_null_key_payload(S[.LITERALARRAYDEBTS = [n_old]], pvalue_snapshot, S.ALLOCATIONS)',
        '~$array_null_key_source(S, n_a, n_capture, poperand, PARRAY n_a, phpType13*, z)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_old, HARRAY n_old]',
        '$heap_count(HCELL n_capture, $task_nodes(' + marker + ')) = 0',
        '$heap_count(HARRAY n_old, $machine_roots(S_dispatch)) = 2',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 3',
        '$call_descriptors_valid(S_dispatch)',
        'S_lost_initial = S_dispatch[.ENV = $unbind($unbind(S_dispatch.ENV, $ptascii("q")), $ptascii("outside"))]',
        'H_lost_initial = $heap_prune($heap_graph(S_lost_initial)[.DEBTS = eps])',
        '~((HCELL n_capture) <- H_lost_initial.NODES)', '(HARRAY n_old) <- H_lost_initial.NODES',
        '$heap_owners(H_lost_initial, HARRAY n_old) = 2',
        '$array_null_key_source(S_lost_initial, ' + args + ')',
        '$call_task_valid(S_lost_initial, ' + marker + ')', '$error_call_valid(S_lost_initial, perrorcall)',
        '~$array_null_key_ready(S_lost_initial, ' + ready + ')',
        'S_retired = S_lost_initial[.ALLOCATIONS = H_lost_initial.NODES][.REFCELLS = $literal_reference_delete(S_lost_initial.REFCELLS, n_capture)]',
        '$array_null_key_source(S_retired, ' + args + ')', '$error_call_valid(S_retired, perrorcall)',
        '~$array_null_key_ready(S_retired, ' + ready + ')',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 2',
        '$heap_count(HCELL n_capture, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 17, 'S_changed') + [
        'S_changed.STORE[n_capture] = DEFINED (PARRAY n_changed)', 'n_changed =/= n_old',
        '$lookup($global_table_view(S_changed).ENV, $ptascii("q")) = (n_other)',
        '$lookup($global_table_view(S_changed).ENV, $ptascii("outside")) = (n_capture)',
        'S_changed.STORE[n_other] = DEFINED (PINT 99)', 'n_other <- S_changed.REFCELLS',
        'n_capture <- S_changed.REFCELLS',
        '$heap_count(HCELL n_capture, $machine_roots(S_changed)) = 1',
        '$heap_count(HCELL n_other, $machine_roots(S_changed)) = 2',
        pair('S_changed', 'n_old', 2, 7), pair('S_changed', 'n_changed', 55, 88),
        'S_changed.STORE[n_key] = DEFINED (PINT 9)', 'S_changed.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_graph(S_changed), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S_changed), HARRAY n_changed) = 1',
        '$array_null_key_slot(S_changed[.LITERALARRAYDEBTS = [n_changed]], n_capture, poperand) = eps',
        '$call_descriptors_valid(S_changed)', '$heap_valid($heap_graph(S_changed))',
    ] + empty_biases('S_changed')
    if thrown:
        checks += [
            'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KSTRING eps) (DIRECT (PINT 8))]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', '$lookup(S.ENV, $ptascii("later")) = (n_later)',
        ] + seek('S_changed', 24, 'S_discard') + [
            'S_discard.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_discard) :: ptask_pending*',
            'perrorcall_discard.RESUME = ' + marker,
            'S_discard.STORE[n_capture] = DEFINED (PARRAY n_changed)',
            '$array_null_key_ready(S_discard, ' + ready + ')',
            '$heap_owners($heap_graph(S_discard), HARRAY n_old) = 2',
            '$entry_lookup(S_discard.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 8))',
            'S_popped = S_discard[.TODO = (THROW_SEARCH n_second) :: ptask_pending*]',
            '$heap_owners($heap_graph(S_popped), HARRAY n_old) = 0',
            '$array_null_key_ready(S_popped, ' + ready + ')',
            '$error_read_discard(S_popped, ' + marker + ') = S_popped[.STORE[n_capture] = DEFINED pvalue_snapshot]',
            'S_object = S_discard[.STORE[n_capture] = DEFINED (POBJECT n_second)]',
            '$array_null_key_source(S_object, ' + args + ')',
            '~$array_null_key_ready(S_object, ' + ready + ')',
            '$error_read_discard(S_object, ' + marker + ') = S_object[.COMPLETION = UNSUPPORTED "array literal null-key value reset during throw"]',
            'PhpStep: S_discard ~> S_released',
            'S_released.STORE[n_capture] = DEFINED pvalue_snapshot',
            'S_released.STORE[n_other] = DEFINED (PINT 99)',
            '$lookup(S_released.ENV, $ptascii("q")) = (n_other)',
            '$lookup(S_released.ENV, $ptascii("outside")) = (n_capture)',
            'S_released.STORE[n_dest] = DEFINED (PINT 99)', 'S_released.STORE[n_later] = DEFINED (PINT 7)',
            '$heap_owners($heap_graph(S_released), HARRAY n_old) = 1',
            '$entry_lookup(S_released.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 8))',
        ] + driven('S_discard', 'S_released', 'S_release_driven') + seek('S_release_driven', 14, 'S_read') + [
            'S_read.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_after*',
            '$throwable_previous_id(S_read, n_second) = eps',
            'S_read.STORE[n_capture] = DEFINED pvalue_snapshot', pair('S_read', 'n_old', 2, 7),
            '~((HARRAY n_a) <- S_read.ALLOCATIONS)', '~((HARRAY n_changed) <- S_read.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 1',
            'S_read.STORE[n_dest] = DEFINED (PINT 99)', 'S_read.STORE[n_later] = DEFINED (PINT 7)',
        ] + seek('S_read', 15, 'S_end') + [
            '$lookup(S_end.ENV, $ptascii("e")) = eps',
            'S_end.STORE[n_capture] = DEFINED pvalue_snapshot',
            'S_end.STORE[n_other] = DEFINED (PINT 99)',
            '$lookup(S_end.ENV, $ptascii("q")) = (n_other)',
            '$lookup(S_end.ENV, $ptascii("outside")) = (n_capture)',
        ]
    else:
        checks += ['S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_changed', 21, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*',
            'S_resume.STORE[n_capture] = DEFINED (PARRAY n_changed)',
            '$array_null_key_slot(S_resume, n_capture, poperand) = (PARRAY n_changed)',
            '$array_null_key_source(S_resume, ' + args + ')', '$array_null_key_ready(S_resume, ' + ready + ')',
            '$error_read_discard(S_resume, ' + marker + ') = S_resume[.STORE[n_capture] = DEFINED pvalue_snapshot]',
            'S_resume.GLOBALTABLE = eps',
            'S_lost = S_resume[.ENV = $unbind(S_resume.ENV, $ptascii("outside"))]',
            'H_lost = $heap_prune($heap_graph(S_lost)[.DEBTS = eps])',
            '~((HCELL n_capture) <- H_lost.NODES)', '(HARRAY n_old) <- H_lost.NODES',
            '$heap_owners(H_lost, HARRAY n_old) = 2',
            '$array_null_key_source(S_lost, ' + args + ')', '~$array_null_key_ready(S_lost, ' + ready + ')',
            '$error_read_discard(S_lost, ' + marker + ') = S_lost[.COMPLETION = UNSUPPORTED "array literal null-key value reset during throw"]',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.STORE[n_capture] = DEFINED pvalue_snapshot',
            '$lookup(S_insert.ENV, $ptascii("q")) = (n_other)',
            '$lookup(S_insert.ENV, $ptascii("outside")) = (n_capture)',
            'S_insert.STORE[n_other] = DEFINED (PINT 99)',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT pvalue_snapshot)',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
            '$heap_count(HARRAY n_old, $machine_roots(S_insert)) = 0',
        ] + empty_biases('S_resume') + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 15, 'S_read') + [
            '~((HARRAY n_changed) <- S_read.ALLOCATIONS)',
            'S_read.STORE[n_capture] = DEFINED pvalue_snapshot', pair('S_read', 'n_old', 2, 7),
            '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            'n_copy_value =/= n_old', pair('S_read', 'n_copy_value', 66, 99),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_read), HARRAY n_copy_value) = 1',
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        ] + seek('S_read', 16, 'S_end') + [
            '$lookup(S_end.ENV, $ptascii("outside")) = eps', '$lookup(S_end.ENV, $ptascii("copy")) = eps',
            '$lookup(S_end.ENV, $ptascii("q")) = (n_other)',
            '$lookup(S_end.ENV, $ptascii("other")) = (n_other)',
            'S_end.STORE[n_other] = DEFINED (PINT 99)',
            '~((HCELL n_capture) <- S_end.ALLOCATIONS)',
            '~((HARRAY n_old) <- S_end.ALLOCATIONS)', '~((HARRAY n_copy) <- S_end.ALLOCATIONS)',
            '~((HARRAY n_copy_value) <- S_end.ALLOCATIONS)',
            'S_end.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 4) (DIRECT (PINT 66))]',
        ]
    checks += [
        'S_end.CURRENT = eps', 'S_end.FRAMES = eps', '$heap_valid($heap_graph(S_end))',
        '$call_descriptors_valid(S_end)',
        '$drive_steps(S_end, 0) = S_end[.COMPLETION = BUDGET]',
        'S_split_found = $drive_steps(S_end, 1)', 'S_split_found.COMPLETION = BUDGET',
        'S_split = S_split_found[.COMPLETION = NORMAL]',
        'S_done = $drive_steps(S_split, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HARRAY n_old) <- S_done.ALLOCATIONS)', '~((HARRAY n_changed) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_a) <- S_done.ALLOCATIONS)', '~((HCELL n_capture) <- S_done.ALLOCATIONS)',
        '~((HCELL n_other) <- S_done.ALLOCATIONS)',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_end') + empty_biases('S_done')
    if thrown:
        checks.append('~((HOBJECT n_second) <- S_done.ALLOCATIONS)')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
