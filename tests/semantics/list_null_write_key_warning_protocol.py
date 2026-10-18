#!/usr/bin/env python3
"""Reached NULL writable-key preparation, alias binding, expiry and throw."""
import base64
import hashlib
import json
from pathlib import Path

import list_null_write_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(LIST_KEY_NULL_WRITE_RESULT n_source n_array n expression phpType13* z n_phase) = true
def $list_warning_frontier(S, 10) = ($list_null_write_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_NULL_WRITE_RESULT n_source n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (LIST_KEY_NULL_WRITE_RESULT n_source n_array n expression phpType13* z 1) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression true phpType13* z) :: ptask_tail*
dec $null_write_notice(pevent) : pevent*
def $null_write_notice(WARNING n_name* z) = [WARNING n_name* z]
def $null_write_notice(WARNING_SOURCE n_unit n_name* z) = [WARNING n_name* z]
def $null_write_notice(DIAGNOSTIC text n_message* z) = [DIAGNOSTIC text n_message* z]
def $null_write_notice(DIAGNOSTIC_SOURCE n_unit text n_message* z) = [DIAGNOSTIC text n_message* z]
def $null_write_notice(pevent) = eps -- otherwise
dec $null_write_notices(pevent*) : pevent*
def $null_write_notices(eps) = eps
def $null_write_notices(pevent :: pevent_tail*) = $null_write_notice(pevent) ++ $null_write_notices(pevent_tail*)
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, result, raw):
    return [f'{result}_found = $drive_steps({start}, 1)', f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ['STORE', 'ARRAYS', 'TODO', 'RESULT']]]


def expected_stderr(name, path):
    if name.endswith('null-unique'):
        return (b'Deprecated: Using null as an array offset is deprecated, use an empty string instead in '
                + bytes(path) + b' on line 12\n')
    return b''


def conditions(name, program, path, stdout):
    unique = name.endswith('null-unique')
    thrown = name.endswith('supplied-throw')
    index, line = (1, 14) if thrown else (0, 12 if unique else 15)
    plan = f'n_source, {index}, expression, phpType13*, z'
    args = f'n_source, n_array, {index}, expression, phpType13*, z'
    marker = lambda phase: f'LIST_KEY_NULL_WRITE_RESULT n_source n_array {index} expression phpType13* z {phase}'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        '$list_null_write_key_plan(S) = ((' + plan + '))',
        f'S.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression true phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)', 'S.RESULT = VARIABLE ($ptascii("key")) z',
        '$list_null_write_key_pending(S)', '$list_float_write_key_plan(S) = eps',
        '$list_null_key_plan(S) = eps', '$list_undefined_key_plan(S) = eps', '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'n_source <- S.REFCELLS',
        '$list_float_write_key_container(S, n_source)',
        f'$list_null_write_key_origin(S, n_source, {index}, expression, phpType13*, z)',
        f'~$list_null_write_key_source(S, n_source, (|S.ARRAYS|), {index}, expression, phpType13*, z, 0)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("x")) = (n_old_target)', '$lookup(S.ENV, $ptascii("outside")) = (n_old_target)',
        'S.STORE[n_old_target] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', f'S.STORE[n_y] = DEFINED (PINT {9 if unique else 7})',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_null_write_key_plan(S[.STORE[n_source] = UNDEFINED]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_source] = DEFINED (PBOOL true)]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_source] = DEFINED (PINT 7)]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 0)]) = eps',
        '$list_null_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4602678819172646912)]) = eps',
        '$list_null_write_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$list_null_write_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_null_write_key_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        f'~$list_null_write_key_origin(S, n_source, {index}, expression, phpType13*, $(z + 1))',
        f'~$list_null_write_key_origin(S, n_source, {index}, expression, eps, z)',
        f'~$list_null_write_key_origin(S[.REFCELLS = eps], n_source, {index}, expression, phpType13*, z)',
        f'~$list_null_write_key_origin(S[.CODE = eps], n_source, {index}, expression, phpType13*, z)',
        f'~$list_null_write_key_origin(S[.SOURCES = eps], n_source, {index}, expression, phpType13*, z)',
        f'$list_null_write_key_plan(S[.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*]) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if thrown:
        checks += ['S.STORE[n_source] = DEFINED (PARRAY n_original)',
                   '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
                   '$entry_lookup(S.ARRAYS[n_original].ITEMS, KSTRING eps) = (ALIAS n_q)',
                   '$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
    else:
        checks += ['S.STORE[n_source] = DEFINED PNULL' if unique else 'S.STORE[n_source] = DEFINED (PBOOL false)',
                   '$list_missing_array(S, REFERENCE n_source) = eps']
        if unique:
            checks += ['$lookup(S.ENV, $ptascii("alias")) = (n_source)',
                       '$heap_owners($heap_prune($heap_graph(S)), HCELL n_source) = 3']
        else:
            checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" $list_null_key_message() z',
        'S_dispatch.STORE[n_source] = DEFINED (PARRAY n_array)',
        '(HARRAY n_array) <- S_dispatch.ALLOCATIONS', '~$array_immutable(S_dispatch, n_array)',
        '$heap_count(HARRAY n_array, $pools_nodes(S_dispatch.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
        'S_dispatch.STORE[n_old_target] = DEFINED (PINT 8)',
        '$task_nodes(' + marker(0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_source]',
        '$list_null_write_key_source(S_dispatch, ' + args + ', 0)', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        '~$call_task_valid(S_dispatch, ' + marker(2) + ')',
    ]
    if thrown:
        checks += ['n_array = n_original', 'S_dispatch.ARRAYS = S.ARRAYS']
    else:
        checks += ['n_array = |S.ARRAYS|', '|S_dispatch.ARRAYS| = $(|S.ARRAYS| + 1)',
                   'S_dispatch.ARRAYS[n_array].ITEMS = eps']
    checks += driven('S', 'S_dispatch_driven', 'S_dispatch') + seek('S_dispatch_driven', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += seek('S_entered', 13, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_pending, n_second) = eps', 'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            'S_pending.STORE[n_before] = DEFINED (PINT 9)', 'S_pending.STORE[n_old_target] = DEFINED (PINT 99)',
            'S_pending.STORE[n_y] = DEFINED (PINT 7)', 'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '$lookup(S_pending.ENV, $ptascii("x")) = (n_old_target)',
            '$lookup(S_pending.ENV, $ptascii("outside")) = (n_old_target)',
            '~((HCELL n_source) <- S_pending.ALLOCATIONS)', '~((HARRAY n_array) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '$null_write_notices(S_pending.EVENTS) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_old_target] = DEFINED (PINT 99)',
            'S_done.STORE[n_before] = DEFINED (PINT 9)', 'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
            '$list_null_write_key_source(S_resume, ' + args + ', 0)',
            'S_resume.STORE[n_old_target] = DEFINED (PINT 88)',
            'S_resume.STORE[n_key_cell] = DEFINED (PFLOAT n_key_live)',
            f'$float_long(n_key_live, true) = ({1 if unique else 0}, [PRECISIONLOSS])',
            'S_resume.ARRAYS[n_array].ITEMS = eps',
        ]
        if unique:
            checks += ['S_resume.STORE[n_source] = DEFINED (PARRAY n_array)',
                       '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 2']
        else:
            checks += ['S_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
                       '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KSTRING eps) = (DIRECT (PINT 77))',
                       '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 1) = (ALIAS n_q)',
                       'S_resume.STORE[n_q] = DEFINED (PINT 33)',
                       '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1']
        checks += ['PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
                   'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
                   'S_release.ALLOCATIONS = S_resume.ALLOCATIONS']
        checks += driven('S_resume', 'S_phase', 'S_release') + [
            '$list_null_write_key_source(S_phase, ' + args + ', 1)',
            'PhpStep: S_phase ~> S_fetch',
            'S_fetch.TODO = (AT porigin_x (LIST_STORE expression (REFERENCE n_slot) true z_target)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
            'S_fetch.STORE[n_slot] = DEFINED PNULL', 'n_slot =/= n_old_target', 'n_slot <- S_fetch.REFCELLS',
        ]
        if unique:
            checks += ['$list_float_write_key_unique(S_phase, n_array)',
                       '$entry_lookup(S_fetch.ARRAYS[n_array].ITEMS, KSTRING eps) = (ALIAS n_slot)',
                       '$heap_owners($heap_prune($heap_graph(S_fetch)), HCELL n_slot) = 2']
        else:
            checks += ['~((HARRAY n_array) <- S_phase.ALLOCATIONS)', '~$list_float_write_key_unique(S_phase, n_array)',
                       'S_fetch.ARRAYS = S_phase.ARRAYS', '$heap_owners($heap_prune($heap_graph(S_fetch)), HCELL n_slot) = 1']
        checks += driven('S_phase', 'S_fetch_driven', 'S_fetch') + [
            'S_target_found = $drive_steps(S_fetch_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
            'S_target = S_target_found[.COMPLETION = NORMAL]',
            'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("x")) = (n_slot)',
            '$lookup(S_bound_raw.ENV, $ptascii("outside")) = (n_old_target)',
        ] + driven('S_target', 'S_bound', 'S_bound_raw') + [
            'S_bound.STORE[n_old_target] = DEFINED (PINT 88)',
            '$heap_owners($heap_prune($heap_graph(S_bound)), HCELL n_old_target) = 1',
        ] + seek('S_bound', 14 if unique else 4, 'S_next') + [
            f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_y {"true" if unique else "false"} eps {line + 1}) :: ptask_y*',
            f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}',
            '$lookup(S_next.ENV, $ptascii("next")) = (n_next_cell)', 'S_next.STORE[n_next_cell] = DEFINED (PINT 1)',
            'PhpStep: S_next ~> S_yread',
        ]
        if unique:
            checks += ['S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_y_slot) true z_y)) :: ptask_yafter*',
                       'S_yread.STORE[n_y_slot] = DEFINED PNULL',
                       '$entry_lookup(S_yread.ARRAYS[n_array].ITEMS, KINT 1) = (ALIAS n_y_slot)']
            checks += driven('S_next', 'S_yread_driven', 'S_yread') + [
                'S_y_target_found = $drive_steps(S_yread_driven, 1)', 'S_y_target_found.COMPLETION = BUDGET',
                'S_y_target = S_y_target_found[.COMPLETION = NORMAL]', 'PhpStep: S_y_target ~> S_ybound_raw',
                '$lookup(S_ybound_raw.ENV, $ptascii("y")) = (n_y_slot)', '(HCELL n_y) <- S_ybound_raw.ALLOCATIONS',
            ] + driven('S_y_target', 'S_ybound', 'S_ybound_raw') + [
                '~((HCELL n_y) <- S_ybound.ALLOCATIONS)', 'S_done = $drive_steps(S_ybound, 2000)',
                '~((HCELL n_y_slot) <- S_done.ALLOCATIONS)',
                '$null_write_notices(S_done.EVENTS) = [DIAGNOSTIC "Deprecated" $list_null_key_message() z]']
        else:
            checks += ['S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 33)) false z_y)) :: ptask_yafter*',
                       'S_done = $drive_steps(S_next, 2000)', 'S_done.STORE[n_y] = DEFINED (PINT 33)',
                       '~((HARRAY n_live) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
                       '$null_write_notices(S_done.EVENTS) = eps']
        checks += ['~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
                   '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_slot) <- S_done.ALLOCATIONS)',
                   'S_done.STORE[n_old_target] = DEFINED (PINT 88)', '$drive_steps(S_resume, 2000) = S_done']
    checks += ['S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
               'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done']
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
