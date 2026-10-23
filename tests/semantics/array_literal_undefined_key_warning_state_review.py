#!/usr/bin/env python3
"""Undefined ARRAY keys preserve live primitive CVs through default and throw."""
import base64
import json

import array_literal_undefined_key_warning_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import HELPERS as BASE_HELPERS, driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases

HELPERS = BASE_HELPERS + r'''
def $list_warning_task(ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z) = true
def $list_warning_frontier(S, 20) = ($array_undefined_key_plan(S) =/= eps)
def $list_warning_frontier(S, 21) = true
  -- if S.TODO = (ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 23) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_RESULT n poperand n_key* phpType13* z
def $list_warning_frontier(S, 24) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_UNDEFINED_RESULT n_a poperand n_key* phpType13* z
dec $array_undefined_review_warning(pevent, nat*, int) : nat
def $array_undefined_review_warning(WARNING n_key* z, n_key*, z) = 1
def $array_undefined_review_warning(WARNING_SOURCE n_source n_key* z, n_key*, z) = 1
def $array_undefined_review_warning(pevent, n_key*, z) = 0 -- otherwise
dec $array_undefined_review_warnings(pevent*, nat*, int) : nat
def $array_undefined_review_warnings(eps, n_key*, z) = 0
def $array_undefined_review_warnings(pevent :: pevent_tail*, n_key*, z) = $($array_undefined_review_warning(pevent, n_key*, z) + $array_undefined_review_warnings(pevent_tail*, n_key*, z))
dec $array_undefined_review_deprecated(pevent) : nat
def $array_undefined_review_deprecated(DIAGNOSTIC "Deprecated" n_message* z) = 1
def $array_undefined_review_deprecated(DIAGNOSTIC_SOURCE n_source "Deprecated" n_message* z) = 1
def $array_undefined_review_deprecated(DIAGNOSTIC_STACK "Deprecated" n_message* z n_trace*) = 1
def $array_undefined_review_deprecated(DIAGNOSTIC_STACK_SOURCE n_source "Deprecated" n_message* z n_trace*) = 1
def $array_undefined_review_deprecated(pevent) = 0 -- otherwise
dec $array_undefined_review_deprecations(pevent*) : nat
def $array_undefined_review_deprecations(eps) = 0
def $array_undefined_review_deprecations(pevent :: pevent_tail*) = $($array_undefined_review_deprecated(pevent) + $array_undefined_review_deprecations(pevent_tail*))
'''


def expected_stderr(name, path):
    if name.endswith('default'):
        return b'Warning: Undefined variable $missing in ' + bytes(path) + b' on line 13\n'
    return b''


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    key = 'offset' if thrown else 'missing'
    line = 15 if thrown else 13
    args = 'n_a, poperand, n_key_name*, phpType13*, z'
    marker = 'ARRAY_KEY_UNDEFINED_RESULT n_a poperand n_key_name* phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 20, 'S') + [
        '$array_undefined_key_plan(S) = ((' + args + '))', f'z = {line}',
        f'n_key_name* = $ptascii("{key}")', f'z_key = {line - 2}',
        'poperand = VARIABLE ($ptascii("value")) z', 'S.RESULT = poperand',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'S.BASE = BASE_VALUE (KNOWN PNULL)', 'S.CURRENT = eps', 'S.FRAMES = eps',
        '$array_float_key_item(S, phpType13*, z) = ((expression, VARIABLE n_key_name* z_key))',
        '$array_undefined_key_source(S, ' + args + ')', '$array_undefined_key_ready(S, n_a, poperand)',
        '$lookup(S.ENV, n_key_name*) = eps', '$array_undefined_key_missing(S, n_key_name*)',
        '$lookup(S.ENV, $ptascii("value")) = (n_value)', 'S.STORE[n_value] = DEFINED (PINT 2)',
        '~(n_value <- S.REFCELLS)', '$array_undefined_key_value(S, poperand) = (PINT 2)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$array_null_key_plan(S) = eps', '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        '~$array_undefined_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_undefined_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_undefined_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_undefined_key_source(S, n_a, poperand, ($ptascii("value")), phpType13*, z)',
        '~$array_undefined_key_source(S, n_a, poperand, n_key_name*, phpType13*, z_key)',
        '$array_undefined_key_plan(S[.RESULT = KNOWN (PINT 2)]) = eps',
        '$array_undefined_key_plan(S[.STORE[n_value] = UNDEFINED]) = eps',
        '$array_undefined_key_plan(S[.REFCELLS = n_value :: S.REFCELLS]) = eps',
        '$heap_count(HCELL n_value, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S), HCELL n_value) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_a) = 1',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $") ++ n_key_name*',
        'perrorcall.EVENT = WARNING n_key_name* z', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = z_key])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE z])',
        '$task_nodes(' + marker + ') = [HARRAY n_a]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_dispatch.RESULT = KNOWN PNULL',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_value) = 1',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_a) = 1',
        '$array_undefined_review_warnings(S_dispatch.EVENTS, n_key_name*, z) = 0',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_value, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_count(HARRAY n_a, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_owners($heap_graph(S_entered), HCELL n_value) = 1',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KSTRING eps) (DIRECT (PINT 8))]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
            'S_object = S[.ARRAYS[n_a].ITEMS = [ENTRY (KSTRING eps) (DIRECT (POBJECT n_second))]]',
            '$heap_valid($heap_graph(S_object))', '~$array_undefined_key_ready(S_object, n_a, poperand)',
            '$error_read_discard(S_object, ' + marker + ') = S_object[.COMPLETION = UNSUPPORTED "array literal undefined-key value during throw"]',
        ] + seek('S_entered', 24, 'S_discard') + [
            'S_discard.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_discard) :: ptask_pending*',
            'perrorcall_discard.RESUME = ' + marker,
            'S_discard.STORE[n_value] = DEFINED (PINT 44)', 'S_discard.STORE[n_dest] = DEFINED (PINT 99)',
            'S_discard.STORE[n_later] = DEFINED (PINT 7)',
            '$lookup(S_discard.ENV, n_key_name*) = (n_key)', 'S_discard.STORE[n_key] = DEFINED (PINT 9)',
            '~$array_undefined_key_missing(S_discard, n_key_name*)',
            '$array_undefined_key_source(S_discard, ' + args + ')', '$array_undefined_key_ready(S_discard, n_a, poperand)',
            'S_popped = S_discard[.TODO = (THROW_SEARCH n_second) :: ptask_pending*]',
            '$heap_owners($heap_graph(S_popped), HARRAY n_a) = 0',
            '$error_read_discard(S_popped, ' + marker + ') = S_popped',
            'PhpStep: S_discard ~> S_released',
            'S_released.STORE = S_discard.STORE', 'S_released.ARRAYS = S_discard.ARRAYS',
        ] + driven('S_discard', 'S_released', 'S_release_driven') + seek('S_release_driven', 14, 'S_catch') + [
            'S_catch.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_after*',
            '~((HARRAY n_a) <- S_catch.ALLOCATIONS)',
            'S_catch.STORE[n_value] = DEFINED (PINT 44)', 'S_catch.STORE[n_dest] = DEFINED (PINT 99)',
            'S_catch.STORE[n_later] = DEFINED (PINT 7)', '$throwable_previous_id(S_catch, n_second) = eps',
            '$array_undefined_review_warnings(S_catch.EVENTS, n_key_name*, z) = 0',
        ] + seek('S_catch', 15, 'S_read') + [
            '~((HARRAY n_a) <- S_read.ALLOCATIONS)', 'S_read.STORE[n_dest] = DEFINED (PINT 99)',
            'S_read.STORE[n_later] = DEFINED (PINT 7)', '$lookup(S_read.ENV, $ptascii("e")) = eps',
        ]
    else:
        checks += ['S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]'] + seek('S_entered', 21, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*',
            'S_resume.STORE[n_value] = DEFINED (PINT 44)', '$array_undefined_key_value(S_resume, poperand) = (PINT 44)',
            '$lookup(S_resume.ENV, n_key_name*) = (n_key)', 'S_resume.STORE[n_key] = DEFINED (PINT 9)',
            '~$array_undefined_key_missing(S_resume, n_key_name*)',
            '$array_undefined_key_source(S_resume, ' + args + ')', '$array_undefined_key_ready(S_resume, n_a, poperand)',
            '$array_undefined_key_source(S_resume[.ENV = eps], ' + args + ')',
            '~$array_undefined_key_ready(S_resume[.ENV = eps], n_a, poperand)',
            '$array_undefined_review_warnings(S_resume.EVENTS, n_key_name*, z) = 1',
            '$array_undefined_review_deprecations(S_resume.EVENTS) = 0',
            'S_defined = S_resume[.TODO = S.TODO][.RESULT = S.RESULT]', '$array_undefined_key_plan(S_defined) = eps',
            'S_null = S_defined[.STORE[n_key] = DEFINED PNULL]', '$array_undefined_key_plan(S_null) = eps',
            '$array_null_key_plan(S_null) =/= eps',
            'S_slot = S_defined[.STORE[n_key] = UNDEFINED]', '$array_undefined_key_missing(S_slot, n_key_name*)',
            '$heap_valid($heap_graph(S_slot))',
            '$array_undefined_key_plan(S_slot) = ((' + args + '))',
            '~$array_undefined_key_missing(S_slot[.REFCELLS = n_key :: S_slot.REFCELLS], n_key_name*)',
            'S_created = $allocate_array(S_resume, $array_empty())', 'S_created.RESULT = KNOWN (PARRAY n_payload)',
            'S_array = S_created[.RESULT = S_resume.RESULT][.STORE[n_value] = DEFINED (PARRAY n_payload)]',
            '$heap_valid($heap_graph(S_array))', '$array_undefined_key_source(S_array, ' + args + ')',
            '$call_descriptors_valid(S_array)',
            '~$array_undefined_key_ready(S_array, n_a, poperand)',
            'PhpStep: S_array ~> S_unsupported',
            'S_unsupported.COMPLETION = UNSUPPORTED "array literal undefined-key value after callback"',
            'S_unsupported.STORE = S_array.STORE', 'S_unsupported.TODO = eps',
            'PhpStep: S_resume ~> S_insert',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 44))',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
            'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
            '$heap_owners($heap_graph(S_insert), HCELL n_value) = 1',
        ] + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            'S_read.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KSTRING eps) (DIRECT (PINT 44)), ENTRY (KINT 9) (DIRECT (PINT 66)), ENTRY (KINT 4) (DIRECT (PINT 44))]',
            '$heap_owners($heap_graph(S_read), HARRAY n_a) = 1',
        ]
    checks += [
        'S_read.STORE[n_value] = DEFINED (PINT 44)', 'S_read.STORE[n_key] = DEFINED (PINT 9)',
        'S_read.STORE[n_calls] = DEFINED (PINT 1)', '$heap_owners($heap_graph(S_read), HCELL n_value) = 1',
        f'$array_undefined_review_warnings(S_read.EVENTS, n_key_name*, z) = {0 if thrown else 1}',
        '$array_undefined_review_deprecations(S_read.EVENTS) = 0', '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~((HARRAY n_a) <- S_done.ALLOCATIONS)',
        '~((HCELL n_value) <- S_done.ALLOCATIONS)', '~((HCELL n_key) <- S_done.ALLOCATIONS)',
        '$array_undefined_review_deprecations(S_done.EVENTS) = 0',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
    ] + empty_biases('S_done')
    if thrown:
        checks.append('~((HOBJECT n_second) <- S_done.ALLOCATIONS)')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr) else 1)
