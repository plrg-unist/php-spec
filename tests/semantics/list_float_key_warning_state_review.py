#!/usr/bin/env python3
"""Reached frozen float keys, delayed ALIAS reads and two-handler ordering."""
import base64
import hashlib
import json
from pathlib import Path

import list_float_key_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(LIST_KEY_FLOAT_RESULT n_array n expression phpType13* z n_bits i) = true
def $list_warning_frontier(S, 10) = ($list_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_FLOAT_RESULT n_array n expression phpType13* z n_bits i) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    present = name.endswith('present-negative-retire')
    line, integer, q_key = (19, -2, '$(-2)') if present else (21, 0, '1')
    args = 'n_array, 0, expression, phpType13*, z, n_bits, i'
    marker = 'LIST_KEY_FLOAT_RESULT n_array 0 expression phpType13* z n_bits i'
    missing = 'LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 0 expression phpType13* z (KINT i)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 10, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        'S_entry.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 0 expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {integer}', 'S_entry.ORIGIN = (porigin)',
        'S_entry.RESULT = VARIABLE ($ptascii("key")) z',
        '$lookup(S_entry.ENV, $ptascii("key")) = (n_key_cell)',
        'S_entry.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)',
        '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$list_float_key_plan(S_entry) = ((n_array, 0, expression, phpType13*, z, n_bits, i))',
        '$list_float_key_pending(S_entry)', '$list_missing_plan(S_entry) = eps',
        '$list_float_key_source(S_entry, ' + args + ')',
        '~$list_float_key_source(S_entry, n_array, 0, expression, phpType13*, z, n_bits, $(i + 1))',
        '~$list_float_key_source(S_entry, n_array, 1, expression, phpType13*, z, n_bits, i)',
        '~$list_float_key_source(S_entry, n_array, 0, expression, phpType13*, $(z + 1), n_bits, i)',
        '~$list_float_key_source(S_entry, n_array, 0, expression, eps, z, n_bits, i)',
        '~$list_float_key_source(S_entry, n_array, 0, expression, phpType13*, z, 18446744073709551616, i)',
        '~$list_float_key_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_float_key_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_float_key_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_float_key_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        '$list_float_key_plan(S_entry[.RESULT = KNOWN (PFLOAT n_bits)]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = DEFINED (PINT 2)]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 9218868437227405312)]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$list_float_key_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 18446744073709551616)]) = eps',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        'S_entry.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S_entry.ENV, $ptascii("next")) = (n_next_cell)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'S_entry.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)', 'S_entry.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)', 'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)', 'S_entry.STORE[n_q] = DEFINED (PINT 2)',
        f'$entry_lookup(S_entry.ARRAYS[n_array].ITEMS, KINT {q_key}) = (ALIAS n_q)',
        '$heap_count(HARRAY n_array, $pools_nodes(S_entry.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
        '$task_nodes(' + marker + ') = [HARRAY n_array]',
        '$call_task_valid(S_entry, ' + marker + ')', '$heap_valid($heap_graph(S_entry))',
    ]
    if present:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_key_cell) = 2',
            '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S_entry.ENV, $ptascii("other")) = (n_other)',
        ]
    else:
        checks += ['$entry_lookup(S_entry.ARRAYS[n_array].ITEMS, KINT 0) = eps']
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        'S_dispatch.STORE = S_entry.STORE', 'S_dispatch.ARRAYS = S_entry.ARRAYS',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HARRAY n_array]',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]',
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe_float :: pframe_float_tail*',
        'pframe_float.TODO = (ERROR_HANDLER_RESULT perrorcall_float_entered) :: ptask_tail*',
        'perrorcall_float_entered.RESUME = ' + marker, 'perrorcall_float_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_resume_found = $list_warning_seek(S_entered, 11, 2000)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        '$list_float_key_source(S_resume, ' + args + ')',
        'S_resume.STORE[n_y] = DEFINED (PINT 8)', 'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
        'S_resume.STORE[n_a] = DEFINED (PARRAY n_live_array)',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
    ]
    if present:
        checks += [
            'S_resume.ERRORHANDLER = S_entry.ERRORHANDLER',
            '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
            '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
            '$lookup(S_resume.ENV, $ptascii("key")) = (n_replacement)',
            'S_resume.STORE[n_replacement] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_other)',
            'S_resume.STORE[n_other] = DEFINED (PINT 44)', 'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            'n_live_array =/= n_array',
            '$entry_lookup(S_resume.ARRAYS[n_live_array].ITEMS, KINT $(-2)) = (DIRECT (PINT 22))',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
            'S_resume.STORE[n_x] = DEFINED (PINT 99)',
            'PhpStep: S_resume ~> S_lookup',
            'S_lookup.TODO = (AT porigin_x (LIST_STORE expression (KNOWN (PINT 33)) false z_x)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 1 phpType13* z_next) :: ptask_tail*',
            'S_lookup.STORE = S_resume.STORE', 'S_lookup.ARRAYS = S_resume.ARRAYS',
            'S_lookup.EVENTS = S_resume.EVENTS',
            'S_lookup_driven_found = $drive_steps(S_resume, 1)', 'S_lookup_driven_found.COMPLETION = BUDGET',
            'S_lookup_driven = S_lookup_driven_found[.COMPLETION = NORMAL]',
            'S_lookup_driven.TODO = S_lookup.TODO', 'S_lookup_driven.STORE = S_lookup.STORE',
            'S_lookup_driven.ARRAYS = S_lookup.ARRAYS',
            'S_after = S_lookup_driven',
        ]
    else:
        checks += [
            'S_resume.ERRORHANDLER =/= S_entry.ERRORHANDLER',
            'S_resume.STORE[n_key_cell] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (3, [PRECISIONLOSS])',
            'S_resume.STORE[n_x] = DEFINED (PINT 77)', 'n_live_array = n_array',
            'PhpStep: S_resume ~> S_warning_dispatch',
            'S_warning_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
            'perrorcall_warning.RESUME = ' + missing,
            'perrorcall_warning.LEVEL = 2', 'perrorcall_warning.LINE = z',
            'perrorcall_warning.MESSAGE = $ptascii("Undefined array key 0")',
            '$error_call_valid(S_warning_dispatch, perrorcall_warning)',
            'S_warning_dispatch.STORE = S_resume.STORE', 'S_warning_dispatch.ARRAYS = S_resume.ARRAYS',
            'S_warning_entered_found = $list_warning_seek(S_warning_dispatch, 3, 2000)',
            r'S_warning_entered_found.COMPLETION = NORMAL \/ S_warning_entered_found.COMPLETION = BUDGET',
            'S_warning_entered = S_warning_entered_found[.COMPLETION = NORMAL]',
            'S_warning_entered.FRAMES = pframe_warning :: pframe_warning_tail*',
            'pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall_warning_entered) :: ptask_tail*',
            'perrorcall_warning_entered.RESUME = ' + missing, 'perrorcall_warning_entered.TARGET =/= eps',
            'S_warning_entered.ERRORHANDLER.CALLBACK = eps',
            'S_warning_resume_found = $list_warning_seek(S_warning_entered, 2, 2000)',
            r'S_warning_resume_found.COMPLETION = NORMAL \/ S_warning_resume_found.COMPLETION = BUDGET',
            'S_warning_resume = S_warning_resume_found[.COMPLETION = NORMAL]',
            'S_warning_resume.TODO = (' + missing + ') :: ptask_tail*',
            'S_warning_resume.ERRORHANDLER = S_resume.ERRORHANDLER',
            'S_warning_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_warning_resume.STORE[n_y] = DEFINED (PINT 88)',
            'S_warning_resume.STORE[n_q] = DEFINED (PINT 33)',
            'S_warning_resume.STORE[n_a] = DEFINED (PARRAY n_written_array)', 'n_written_array =/= n_array',
            '$entry_lookup(S_warning_resume.ARRAYS[n_written_array].ITEMS, KINT 0) = (DIRECT (PINT 77))',
            '$entry_lookup(S_warning_resume.ARRAYS[n_array].ITEMS, KINT 0) = eps',
            '$list_missing_source(S_warning_resume, KNOWN (PARRAY n_array), 0, expression, phpType13*, z, KINT 0)',
            '$heap_owners($heap_prune($heap_graph(S_warning_resume)), HCELL n_q) = 3',
            '$call_descriptors_valid(S_warning_resume)', '$heap_valid($heap_graph(S_warning_resume))',
            'PhpStep: S_warning_resume ~> S_null_store',
            'S_null_store.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 1 phpType13* z_next) :: ptask_tail*',
            'S_null_store.STORE = S_warning_resume.STORE', 'S_null_store.ARRAYS = S_warning_resume.ARRAYS',
            'S_after = S_warning_resume',
        ]
    checks += [
        'S_next_found = $list_warning_seek(S_after, 4, 2000)',
        r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
        'S_next = S_next_found[.COMPLETION = NORMAL]',
        'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_next false eps z_later) :: ptask_tail*',
        f'z_later = {line + 1}', f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}',
        'S_next.STORE[n_x] = DEFINED (PINT 33)' if present else 'S_next.STORE[n_x] = DEFINED PNULL',
        'S_next.STORE[n_next_cell] = DEFINED (PINT 4)' if present else 'S_next.STORE[n_next_cell] = DEFINED (PINT 1)',
        'PhpStep: S_next ~> S_read',
        'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT 6)) false z_y)) :: ptask_after*' if present else 'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT 33)) false z_y)) :: ptask_after*',
        'S_read_driven_found = $drive_steps(S_next, 1)', 'S_read_driven_found.COMPLETION = BUDGET',
        'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]',
        'S_read_driven.TODO = S_read.TODO', 'S_read_driven.STORE = S_read.STORE',
        'S_read_driven.ARRAYS = S_read.ARRAYS', 'S_done = $drive_steps(S_read_driven, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_y] = DEFINED (PINT 6)' if present else 'S_done.STORE[n_y] = DEFINED (PINT 55)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_entry, 2000) = S_done', '$drive_steps(S_resume, 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
