#!/usr/bin/env python3
"""Reached writable empty-key ownership, detached binding and later fresh keys."""
import base64
import hashlib
import json
from pathlib import Path

import list_null_write_key_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($list_null_write_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_NULL_WRITE_RESULT n_source n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = LIST_KEY_NULL_WRITE_RESULT n_source n_array n expression phpType13* z 0
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
  -- if $(n > 0)
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) 0 expression true eps z) :: ptask_tail*
  -- if S.RESULT = VARIABLE n_key* z_key
  -- if $lookup(S.ENV, n_key*) = (n_source)
  -- if S.STORE[n_source] = DEFINED PNULL
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ('STORE', 'ARRAYS', 'TODO', 'RESULT')]]


def alias_conditions(program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 15, 'S') + [
        'S.TODO = (LIST_FETCH (REFERENCE n_source) 0 expression true eps z) :: ptask_tail*',
        'S.RESULT = VARIABLE ($ptascii("key")) 7', 'z = 7',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)',
        '$lookup(S.ENV, $ptascii("key")) = (n_source)',
        'S.STORE[n_source] = DEFINED PNULL', 'n_source <- S.REFCELLS',
        '$list_null_write_key_origin(S, n_source, 0, expression, eps, z)',
        '$list_float_write_key_container(S, n_source)',
        '$list_null_write_key_plan(S) = eps', '~$list_null_write_key_pending(S)',
        '$list_float_write_key_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("x")) = (n_old_target)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_old_target)',
        'S.STORE[n_old_target] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        'S.EVENTS = eps', 'S.FRAMES = eps', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_error',
        'S_error.COMPLETION = THROWN "TypeError" ($ptascii("Cannot access offset of type array on array")) z',
        'S_error.TODO = eps', 'S_error.ENV = S.ENV',
        'S_error.STORE[n_source] = DEFINED (PARRAY n_array)', 'n_array = |S.ARRAYS|',
        'S_error.ARRAYS[n_array].ITEMS = eps', '~$array_immutable(S_error, n_array)',
        '(HARRAY n_array) <- S_error.ALLOCATIONS',
        'S_error.STORE[n_old_target] = DEFINED (PINT 7)', 'S_error.STORE[n_dest] = DEFINED (PINT 100)',
        'S_error.EVENTS = S.EVENTS', 'S_error.FRAMES = S.FRAMES', 'S_error.ERRORHANDLER = S.ERRORHANDLER',
        '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        '~((HCELL n_old_target) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]


def conditions(name, program, path, stdout):
    if name == 'list-null-write-review-key-source-alias':
        return alias_conditions(program, path, stdout)
    held = name.endswith('detached-sole-hold')
    index, line = (0, 18) if held else (1, 15)
    args = f'n_source, n_array, {index}, expression, phpType13*, z'
    marker = lambda phase: f'LIST_KEY_NULL_WRITE_RESULT n_source n_array {index} expression phpType13* z {phase}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        f'$list_null_write_key_plan(S) = ((n_source, {index}, expression, phpType13*, z))',
        f'S.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression true phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)',
        f'S.RESULT = VARIABLE ($ptascii("key")) {line}',
        '$list_null_write_key_pending(S)', '$list_null_key_plan(S) = eps',
        '$list_float_write_key_plan(S) = eps', '$list_undefined_key_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'n_source <- S.REFCELLS',
        'S.STORE[n_source] = DEFINED (PARRAY n_original)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', '$lookup(S.ENV, $ptascii("outside")) = (n_x)',
        'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("hold")) = (n_hold)', 'S.STORE[n_hold] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        '$heap_count(HARRAY n_original, $pools_nodes(S.POOLS)) = 0',
        '$list_null_write_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$list_null_write_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 0)]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PBOOL false)]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_source] = DEFINED (PBOOL true)]) = eps',
        f'$list_null_write_key_plan(S[.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*]) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if held:
        checks += [
            '$lookup(S.ENV, $ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_original)',
            '$lookup(S.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S.ENV, $ptascii("key_replacement")) = (n_key_replacement)',
            '$entry_lookup(S.ARRAYS[n_original].ITEMS, KINT 1) = (ALIAS n_q)',
            '$entry_lookup(S.ARRAYS[n_original].ITEMS, KSTRING eps) = eps',
            '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_original) = 2',
        ]
    else:
        checks += [
            '$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
            '$entry_lookup(S.ARRAYS[n_original].ITEMS, KSTRING eps) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_original) = 1',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" $list_null_key_message() z',
        'S_dispatch.STORE[n_source] = DEFINED (PARRAY n_array)',
        '$list_null_write_key_source(S_dispatch, ' + args + ', 0)',
        '$task_nodes(' + marker(0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_source]',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        '~$list_null_write_key_source(S_dispatch, ' + args + ', 2)',
        f'~$list_null_write_key_source(S_dispatch, n_source, n_array, {index}, expression, phpType13*, $(z + 1), 0)',
        f'~$list_null_write_key_source(S_dispatch, n_source, n_array, {index}, expression, eps, z, 0)',
        f'~$list_null_write_key_source(S_dispatch, n_source, (|S_dispatch.ARRAYS|), {index}, expression, phpType13*, z, 1)',
        '~$list_null_write_key_source(S_dispatch[.SOURCES = eps], ' + args + ', 0)',
        '~$list_null_write_key_source(S_dispatch[.CODE = eps], ' + args + ', 0)',
        '~$list_null_write_key_source(S_dispatch[.REFCELLS = eps], ' + args + ', 0)',
        '~$list_null_write_key_source(S_dispatch[.ALLOCATIONS = eps], ' + args + ', 0)',
    ]
    if held:
        checks += [
            'n_array =/= n_original', 'S_dispatch.STORE[n_copy] = DEFINED (PARRAY n_original)',
            '$entry_lookup(S_dispatch.ARRAYS[n_array].ITEMS, KINT 1) = (ALIAS n_q)',
            '$entry_lookup(S_dispatch.ARRAYS[n_array].ITEMS, KSTRING eps) = eps',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_q) = 3',
        ]
    else:
        checks += ['n_array = n_original', 'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS']
    checks += driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
        '$list_null_write_key_source(S_resume, ' + args + ', 0)',
        'S_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_resume.STORE[n_q] = DEFINED (PINT 33)',
        'S_resume.STORE[n_dest] = DEFINED (PINT 200)', 'S_resume.STORE[n_hold] = DEFINED (PARRAY n_array)',
    ]
    if held:
        checks += [
            '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)', '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
            '$lookup(S_resume.ENV, $ptascii("key")) = (n_key_replacement)',
            'S_resume.STORE[n_key_replacement] = DEFINED (PINT 1)',
            '$lookup(S_resume.ENV, $ptascii("a")) = (n_replacement)', 'n_replacement =/= n_source',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_saved)', 'n_saved =/= n_array',
            '$entry_lookup(S_resume.ARRAYS[n_saved].ITEMS, KINT 1) = (DIRECT (PINT 22))',
            'S_resume.STORE[n_replacement] = DEFINED (PARRAY n_live)', 'n_live =/= n_saved',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 1) = (DIRECT (PINT 88))',
            'S_resume.STORE[n_tail] = DEFINED (PINT 88)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 2',
        ]
    else:
        checks += [
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_array)', 'S_resume.STORE[n_tail] = DEFINED (PINT 8)',
            'S_resume.STORE[n_key_cell] = DEFINED (PINT 7)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 3',
        ]
    checks += [
        'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
        'S_release.ALLOCATIONS = S_resume.ALLOCATIONS',
    ] + driven('S_resume', 'S_release', 'S_phase') + [
        '(HARRAY n_array) <- S_phase.ALLOCATIONS', '$list_null_write_key_source(S_phase, ' + args + ', 1)',
        '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 1' if held else '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 2',
        '$call_descriptors_valid(S_phase)', '$heap_valid($heap_graph(S_phase))',
        'PhpStep: S_phase ~> S_acquired',
        f'S_acquired.TODO = (AT porigin_x (LIST_STORE expression (REFERENCE n_slot) true z_x)) :: (LIST_NEXT (REFERENCE n_source) {index + 1} phpType13* z_next) :: ptask_tail*',
        'S_acquired.STORE[n_slot] = DEFINED PNULL', 'n_slot <- S_acquired.REFCELLS',
        'n_slot =/= n_q', 'n_slot =/= n_x', 'S_acquired.EVENTS = S_phase.EVENTS',
    ]
    if held:
        checks += [
            '$entry_lookup(S_acquired.ARRAYS[n_array].ITEMS, KSTRING eps) = (ALIAS n_slot)',
            '$entry_lookup(S_acquired.ARRAYS[n_original].ITEMS, KSTRING eps) = eps',
            'S_acquired.STORE[n_source] = DEFINED (PARRAY n_saved)',
            '$entry_lookup(S_acquired.ARRAYS[n_saved].ITEMS, KSTRING eps) = eps',
            '$heap_owners($heap_prune($heap_graph(S_acquired)), HCELL n_slot) = 2',
        ]
    else:
        checks += [
            'S_acquired.ARRAYS = S_phase.ARRAYS',
            '$entry_lookup(S_acquired.ARRAYS[n_array].ITEMS, KSTRING eps) = (ALIAS n_q)',
            'S_acquired.STORE[n_q] = DEFINED (PINT 33)',
            '$heap_owners($heap_prune($heap_graph(S_acquired)), HCELL n_slot) = 1',
        ]
    checks += driven('S_phase', 'S_acquired', 'S_acquired_driven') + [
        'S_target_found = $drive_steps(S_acquired_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
        'S_target = S_target_found[.COMPLETION = NORMAL]',
        'S_target.TODO = (LIST_STORE expression (REFERENCE n_slot) true z_x) :: ptask_bound*',
        'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("x")) = (n_slot)',
        '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_x) = 1',
    ] + driven('S_target', 'S_bound_raw', 'S_bound') + [
        'S_bound.STORE[n_x] = DEFINED (PINT 99)',
    ] + seek('S_bound', 14 if held else 4, 'S_next') + [
        f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) {index + 1} expression_tail {str(held).lower()} eps z_tail) :: ptask_next*',
        f'z_tail = {line + 1}',
        f'S_next.RESULT = VARIABLE ($ptascii("{"key" if held else "next"}")) {line + 1}',
        'S_next.STORE[n_slot] = DEFINED PNULL',
        'S_next.STORE[n_source] = DEFINED (PARRAY n_saved)' if held else 'S_next.STORE[n_source] = DEFINED (PARRAY n_array)',
        '$list_null_write_key_plan(S_next) = eps',
        'PhpStep: S_next ~> S_read',
    ]
    if held:
        checks += [
            'S_read.TODO = (AT porigin_tail (LIST_STORE expression_tail (REFERENCE n_tail_slot) true z_target_tail)) :: ptask_after*',
            'S_read.STORE[n_tail_slot] = DEFINED (PINT 22)', 'n_tail_slot =/= n_slot',
            'S_read.STORE[n_source] = DEFINED (PARRAY n_after)', 'n_after =/= n_saved',
            '$entry_lookup(S_read.ARRAYS[n_after].ITEMS, KINT 1) = (ALIAS n_tail_slot)',
            '$entry_lookup(S_read.ARRAYS[n_saved].ITEMS, KINT 1) = (DIRECT (PINT 22))',
        ]
    else:
        checks += ['S_read.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 6)) false z_target_tail)) :: ptask_after*']
    checks += driven('S_next', 'S_read', 'S_read_driven') + [
        'S_done = $drive_steps(S_read_driven, 2000)',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HCELL n_slot) <- S_done.ALLOCATIONS)',
        '~((HCELL n_x) <- S_done.ALLOCATIONS)',
    ]
    if held:
        checks += ['~((HARRAY n_original) <- S_done.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
                   '~((HARRAY n_after) <- S_done.ALLOCATIONS)', '~((HCELL n_tail_slot) <- S_done.ALLOCATIONS)']
    else:
        checks += ['S_done.STORE[n_tail] = DEFINED (PINT 6)']
    checks += [
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
    cases.CASES = {**cases.CASES, **cases.SOURCE_ONLY}
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
