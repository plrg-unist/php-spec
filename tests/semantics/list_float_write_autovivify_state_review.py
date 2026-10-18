#!/usr/bin/env python3
"""Reached scalar source initialization, detached holds and later reference COW."""
import base64
import hashlib
import json
from pathlib import Path

import list_float_write_autovivify_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($list_float_write_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_FLOAT_WRITE_RESULT n_source n_array n expression phpType13* z n_bits i 0) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = LIST_KEY_FLOAT_WRITE_RESULT n_source n_array n expression phpType13* z n_bits i 0
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression true phpType13* z) :: ptask_tail*
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def conditions(name, program, path, stdout):
    held = name.endswith('null-detached-hold')
    line, integer = (17, -2) if held else (14, 0)
    origin_args = 'n_source, 0, expression, phpType13*, z, n_bits, i'
    args = 'n_source, n_array, 0, expression, phpType13*, z, n_bits, i'
    marker = lambda phase: f'LIST_KEY_FLOAT_WRITE_RESULT n_source n_array 0 expression phpType13* z n_bits i {phase}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$list_float_write_key_plan(S) = ((n_source, 0, expression, phpType13*, z, n_bits, i))',
        'S.TODO = (LIST_FETCH (REFERENCE n_source) 0 expression true phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {integer}', 'S.ORIGIN = (porigin)',
        f'S.RESULT = VARIABLE ($ptascii("key")) {line}',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'n_source <- S.REFCELLS',
        'S.STORE[n_source] = DEFINED PNULL' if held else 'S.STORE[n_source] = DEFINED (PBOOL false)',
        '$list_missing_array(S, REFERENCE n_source) = eps',
        '$list_float_write_key_container(S, n_source)',
        '$list_float_write_key_origin(S, ' + origin_args + ')',
        '$list_float_write_key_pending(S)', '$list_float_key_plan(S) = eps', '$list_float_ref_key_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)',
        '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("hold")) = (n_hold)', 'S.STORE[n_hold] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_source) = 2',
        '$list_float_write_key_plan(S[.RESULT = KNOWN (PFLOAT n_bits)]) = eps',
        '$list_float_write_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_source] = UNDEFINED]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_source] = DEFINED (PBOOL true)]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_source] = DEFINED (PINT 7)]) = eps',
        '~$list_float_write_key_origin(S[.REFCELLS = eps], ' + origin_args + ')',
        '~$list_float_write_key_origin(S[.ORIGIN = eps], ' + origin_args + ')',
        '~$list_float_write_key_origin(S[.SOURCES = eps], ' + origin_args + ')',
        '~$list_float_write_key_origin(S, n_source, 0, expression, phpType13*, $(z + 1), n_bits, i)',
        '~$list_float_write_key_origin(S, n_source, 0, expression, eps, z, n_bits, i)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if held:
        checks += [
            '$lookup(S.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S.ENV, $ptascii("key_replacement")) = (n_key_replacement)',
        ]
    else:
        checks += ['$lookup(S.ENV, $ptascii("outside")) = (n_x)']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'S_dispatch.STORE[n_source] = DEFINED (PARRAY n_array)',
        'S_dispatch.ARRAYS[n_array].ITEMS = eps', '~((HARRAY n_array) <- S.ALLOCATIONS)',
        '(HARRAY n_array) <- S_dispatch.ALLOCATIONS', 'S_dispatch.ENV = S.ENV',
        'S_dispatch.STORE[n_x] = S.STORE[n_x]', 'S_dispatch.STORE[n_tail] = S.STORE[n_tail]',
        'S_dispatch.STORE[n_calls] = DEFINED (PINT 0)',
        '$list_float_write_key_source(S_dispatch, ' + args + ', 0)',
        '$task_nodes(' + marker(0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_source]',
        '$heap_count(HARRAY n_array, $pools_nodes(S_dispatch.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        '~$list_float_write_key_source(S_dispatch, ' + args + ', 2)',
        '~$list_float_write_key_source(S_dispatch[.ALLOCATIONS = eps], ' + args + ', 0)',
        'S_dispatch_driven_found = $drive_steps(S, 1)', 'S_dispatch_driven_found.COMPLETION = BUDGET',
        'S_dispatch_driven = S_dispatch_driven_found[.COMPLETION = NORMAL]',
        'S_dispatch_driven.STORE = S_dispatch.STORE', 'S_dispatch_driven.ARRAYS = S_dispatch.ARRAYS',
        'S_dispatch_driven.TODO = S_dispatch.TODO', 'S_dispatch_driven.RESULT = S_dispatch.RESULT',
    ] + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
        '$list_float_write_key_source(S_resume, ' + args + ', 0)',
        'S_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.STORE[n_hold] = DEFINED (PARRAY n_array)', 'S_resume.ARRAYS[n_array].ITEMS = eps',
    ]
    if held:
        checks += [
            '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
            '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
            '$lookup(S_resume.ENV, $ptascii("key")) = (n_key_replacement)',
            '$lookup(S_resume.ENV, $ptascii("a")) = (n_replacement)', 'n_replacement =/= n_source',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_saved)', 'n_saved =/= n_array',
            '$entry_lookup(S_resume.ARRAYS[n_saved].ITEMS, KINT $(-2)) = (DIRECT (PINT 22))',
            '$entry_lookup(S_resume.ARRAYS[n_saved].ITEMS, KINT 1) = (DIRECT (PINT 44))',
            'S_resume.STORE[n_replacement] = DEFINED (PARRAY n_live)', 'n_live =/= n_saved',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT $(-2)) = (DIRECT (PINT 88))',
            'S_resume.STORE[n_key_replacement] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 2',
        ]
    else:
        checks += [
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_array)',
            'S_resume.STORE[n_key_cell] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (2, [PRECISIONLOSS])',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 3',
        ]
    checks += [
        'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
        'S_release.ALLOCATIONS = S_resume.ALLOCATIONS',
        'S_phase_found = $drive_steps(S_resume, 1)', 'S_phase_found.COMPLETION = BUDGET',
        'S_phase = S_phase_found[.COMPLETION = NORMAL]',
        'S_phase.TODO = S_release.TODO', 'S_phase.STORE = S_release.STORE', 'S_phase.ARRAYS = S_release.ARRAYS',
        '(HARRAY n_array) <- S_phase.ALLOCATIONS', '$list_float_write_key_source(S_phase, ' + args + ', 1)',
        '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 1' if held else '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 2',
        'PhpStep: S_phase ~> S_acquired',
        'S_acquired.TODO = (AT porigin_x (LIST_STORE expression (REFERENCE n_slot) true z_x)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
        'S_acquired.STORE[n_slot] = DEFINED PNULL', 'n_slot <- S_acquired.REFCELLS', 'n_slot =/= n_x',
        'S_acquired.EVENTS = S_phase.EVENTS',
    ]
    if held:
        checks += [
            '$entry_lookup(S_acquired.ARRAYS[n_array].ITEMS, KINT $(-2)) = (ALIAS n_slot)',
            '$entry_lookup(S_acquired.ARRAYS[n_saved].ITEMS, KINT $(-2)) = (DIRECT (PINT 22))',
            '$heap_owners($heap_prune($heap_graph(S_acquired)), HCELL n_slot) = 2',
        ]
    else:
        checks += ['S_acquired.ARRAYS = S_phase.ARRAYS', '$heap_owners($heap_prune($heap_graph(S_acquired)), HCELL n_slot) = 1']
    checks += [
        'S_acquired_driven_found = $drive_steps(S_phase, 1)', 'S_acquired_driven_found.COMPLETION = BUDGET',
        'S_acquired_driven = S_acquired_driven_found[.COMPLETION = NORMAL]',
        'S_acquired_driven.TODO = S_acquired.TODO', 'S_acquired_driven.STORE = S_acquired.STORE',
        'S_acquired_driven.ARRAYS = S_acquired.ARRAYS',
        'S_target_found = $drive_steps(S_acquired_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
        'S_target = S_target_found[.COMPLETION = NORMAL]',
        'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("x")) = (n_slot)',
        '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_x) = 0' if held else '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_x) = 1',
        'S_bound_found = $drive_steps(S_target, 1)', 'S_bound_found.COMPLETION = BUDGET',
        'S_bound = S_bound_found[.COMPLETION = NORMAL]',
        '~((HCELL n_x) <- S_bound.ALLOCATIONS)' if held else 'S_bound.STORE[n_x] = DEFINED (PINT 99)',
    ] + seek('S_bound', 14, 'S_next') + [
        'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_tail true eps z_tail) :: ptask_next*',
        f'z_tail = {line + 1}',
        'S_next.RESULT = KNOWN (PINT 1)' if held else f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}',
        '~$list_float_write_key_pending(S_next)',
        'PhpStep: S_next ~> S_tail_acquired',
        'S_tail_acquired.TODO = (AT porigin_tail (LIST_STORE expression_tail (REFERENCE n_tail_slot) true z_tail_target)) :: ptask_after*',
        'S_tail_acquired.STORE[n_source] = DEFINED (PARRAY n_tail_array)', 'n_tail_array =/= n_array',
        '$entry_lookup(S_tail_acquired.ARRAYS[n_tail_array].ITEMS, KINT 1) = (ALIAS n_tail_slot)',
        'S_tail_acquired.STORE[n_tail_slot] = DEFINED (PINT 44)' if held else 'S_tail_acquired.STORE[n_tail_slot] = DEFINED PNULL',
        'n_tail_slot =/= n_slot', '$heap_owners($heap_prune($heap_graph(S_tail_acquired)), HCELL n_tail_slot) = 2',
        '$entry_lookup(S_tail_acquired.ARRAYS[n_array].ITEMS, KINT $(-2)) = (ALIAS n_slot)' if held else 'S_tail_acquired.ARRAYS[n_array].ITEMS = eps',
        'S_tail_acquired_driven_found = $drive_steps(S_next, 1)', 'S_tail_acquired_driven_found.COMPLETION = BUDGET',
        'S_tail_acquired_driven = S_tail_acquired_driven_found[.COMPLETION = NORMAL]',
        'S_tail_acquired_driven.TODO = S_tail_acquired.TODO', 'S_tail_acquired_driven.STORE = S_tail_acquired.STORE',
        'S_tail_acquired_driven.ARRAYS = S_tail_acquired.ARRAYS',
        'S_tail_target_found = $drive_steps(S_tail_acquired_driven, 1)', 'S_tail_target_found.COMPLETION = BUDGET',
        'S_tail_target = S_tail_target_found[.COMPLETION = NORMAL]',
        'PhpStep: S_tail_target ~> S_tail_bound_raw', '$lookup(S_tail_bound_raw.ENV, $ptascii("tail")) = (n_tail_slot)',
        '$heap_owners($heap_prune($heap_graph(S_tail_bound_raw)), HCELL n_tail) = 0',
        'S_tail_bound_found = $drive_steps(S_tail_target, 1)', 'S_tail_bound_found.COMPLETION = BUDGET',
        'S_tail_bound = S_tail_bound_found[.COMPLETION = NORMAL]', '~((HCELL n_tail) <- S_tail_bound.ALLOCATIONS)',
        'S_done = $drive_steps(S_tail_bound, 2000)',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_tail_array) <- S_done.ALLOCATIONS)', '~((HCELL n_slot) <- S_done.ALLOCATIONS)',
        '~((HCELL n_tail_slot) <- S_done.ALLOCATIONS)', '~((HCELL n_x) <- S_done.ALLOCATIONS)',
        '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_resume, 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
