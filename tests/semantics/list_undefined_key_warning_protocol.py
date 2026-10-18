#!/usr/bin/env python3
"""Reached undefined-key protection, null handoff, expiry and abrupt cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import list_undefined_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(LIST_KEY_UNDEFINED_RESULT poperand n_array n expression phpType13* z n_phase) = true
def $list_warning_task(LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z n_phase) = true
def $list_warning_frontier(S, 10) = ($list_undefined_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_UNDEFINED_RESULT poperand n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (LIST_KEY_UNDEFINED_RESULT poperand n_array n expression phpType13* z 1) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression true phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 16) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 1) :: ptask_tail*
dec $undefined_key_notice(pevent) : pevent*
def $undefined_key_notice(WARNING n_name* z) = [WARNING n_name* z]
def $undefined_key_notice(WARNING_SOURCE n_unit n_name* z) = [WARNING n_name* z]
def $undefined_key_notice(DIAGNOSTIC text n_message* z) = [DIAGNOSTIC text n_message* z]
def $undefined_key_notice(DIAGNOSTIC_SOURCE n_unit text n_message* z) = [DIAGNOSTIC text n_message* z]
def $undefined_key_notice(pevent) = eps -- otherwise
dec $undefined_key_notices(pevent*) : pevent*
def $undefined_key_notices(eps) = eps
def $undefined_key_notices(pevent :: pevent_tail*) = $undefined_key_notice(pevent) ++ $undefined_key_notices(pevent_tail*)
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, result, raw):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET', f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ['STORE', 'ARRAYS', 'TODO', 'RESULT']]]


def expected_stderr(name, path):
    if name.endswith('default-then-null'):
        return b'Warning: Undefined variable $key in ' + bytes(path) + b' on line 20\n'
    return b''


def conditions(name, program, path, stdout):
    default = name.endswith('default-then-null')
    thrown = name.endswith('supplied-throw')
    index, line = (1, 14) if thrown else (0, 20 if default else 15)
    operand = 'KNOWN (PARRAY n_array)' if default else 'REFERENCE n_source'
    args = f'{operand}, n_array, {index}, expression, phpType13*, z'
    marker = lambda phase: f'LIST_KEY_UNDEFINED_RESULT ({operand}) n_array {index} expression phpType13* z {phase}'
    null_marker = lambda phase: f'LIST_KEY_NULL_RESULT ({operand}) n_array {index} expression phpType13* z {phase}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        f'$list_undefined_key_plan(S) = (({args}))',
        f'S.TODO = (LIST_FETCH ({operand}) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)', 'S.RESULT = VARIABLE ($ptascii("key")) z',
        '$lookup(S.ENV, $ptascii("key")) = eps', '$list_undefined_key_empty(S, $ptascii("key"))',
        '$list_undefined_key_pending(S)', '$list_null_key_plan(S) = eps', '$list_missing_plan(S) = eps',
        '$list_float_key_pending(S) = false', '$list_float_write_key_pending(S) = false',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        f'$lookup(S.ENV, $ptascii("{"tail" if default else "y"}")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        f'$entry_lookup(S.ARRAYS[n_array].ITEMS, {"KSTRING eps" if default or thrown else "KINT 1"}) = (ALIAS n_q)',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
        f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = {2 if default else 1}',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        '$list_null_key_source(S, ' + args + ', 0)',
        '$call_task_valid(S, ' + marker(0) + ')', '~$call_task_valid(S, ' + marker(2) + ')',
        '$task_nodes(' + marker(0) + ') = ' + ('[HARRAY n_array]' if default else '[HCELL n_source, HARRAY n_array]'),
        '$task_nodes(' + marker(1) + ') = ' + ('[HARRAY n_array]' if default else '[HCELL n_source]'),
        '$list_undefined_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$list_undefined_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_undefined_key_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        'S_defined = S[.ENV = (BIND ($ptascii("key")) n_q) :: S.ENV]',
        '~$list_undefined_key_empty(S_defined, $ptascii("key"))', '$list_undefined_key_plan(S_defined) = eps',
        '$list_undefined_key_plan(S_defined[.STORE[n_q] = DEFINED PNULL]) = eps',
        '$list_undefined_key_plan(S_defined[.STORE[n_q] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        '~$list_undefined_key_empty(S[.ENV = (BIND ($ptascii("key")) (|S.STORE|)) :: S.ENV], $ptascii("key"))',
        f'$list_undefined_key_plan(S[.TODO = (LIST_FETCH ({operand}) {index} expression true phpType13* z) :: ptask_tail*]) = eps',
        '~$list_null_key_source(S[.ORIGIN = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.CODE = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.SOURCES = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.ALLOCATIONS = eps], ' + args + ', 0)',
        f'~$list_null_key_source(S, {operand}, (|S.ARRAYS|), {index}, expression, phpType13*, z, 1)',
        f'~$list_null_key_source(S, {operand}, n_array, {index}, expression, phpType13*, $(z + 1), 0)',
        f'~$list_null_key_source(S, {operand}, n_array, {index + 1}, expression, phpType13*, z, 0)',
        f'~$list_null_key_source(S, {operand}, n_array, {index}, expression, eps, z, 0)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_undefined_key_message($ptascii("key"))',
        'perrorcall.EVENT = WARNING ($ptascii("key")) z', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE z])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$lookup(S_dispatch.ENV, $ptascii("key")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
    ] + driven('S', 'S_dispatch_driven', 'S_dispatch') + seek('S_dispatch_driven', 3, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        'S_entered.ERRORHANDLER.CALLBACK = eps',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
        checks += seek('S_entered', 13, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)', '$lookup(S_pending.ENV, $ptascii("key")) = eps',
            '~((HCELL n_source) <- S_pending.ALLOCATIONS)', '~((HARRAY n_array) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_q) <- S_pending.ALLOCATIONS)', '$undefined_key_notices(S_pending.EVENTS) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_before] = DEFINED (PINT 9)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("key")) = (n_key_new)', '$(|S.STORE| <= n_key_new)',
            f'S_resume.STORE[n_key_new] = DEFINED (PINT {1 if default else 2})',
            '~$list_undefined_key_empty(S_resume, $ptascii("key"))',
            '$list_null_key_source(S_resume, ' + args + ', 0)',
            'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
        ] + driven('S_resume', 'S_phase', 'S_release') + [
            '$list_null_key_source(S_phase, ' + args + ', 1)',
            '$call_descriptors_valid(S_phase)', '$heap_valid($heap_graph(S_phase))',
        ]
        if default:
            checks += [
                '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 2',
                '$undefined_key_notices(S_phase.EVENTS) = [WARNING ($ptascii("key")) z]',
                'S_phase.STORE[n_x] = DEFINED (PINT 77)', 'S_phase.STORE[n_q] = DEFINED (PINT 22)',
                'PhpStep: S_phase ~> S_null_dispatch',
                'S_null_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_null) :: ptask_tail*',
                'perrorcall_null.RESUME = ' + null_marker(0), 'perrorcall_null.LEVEL = 8192',
                '$error_call_valid(S_null_dispatch, perrorcall_null)',
            ] + driven('S_phase', 'S_null_dispatch_driven', 'S_null_dispatch') + seek('S_null_dispatch_driven', 3, 'S_null_entered') + [
                'S_null_entered.FRAMES = pframe_null :: pframe_null_tail*',
                'pframe_null.TODO = (ERROR_HANDLER_RESULT perrorcall_null_entered) :: ptask_null*',
                'perrorcall_null_entered.RESUME = ' + null_marker(0), 'perrorcall_null_entered.TARGET =/= eps',
            ] + seek('S_null_entered', 15, 'S_null_resume') + [
                'S_null_resume.STORE[n_key_new] = DEFINED (PINT 2)', 'S_null_resume.STORE[n_x] = DEFINED (PINT 99)',
                'S_null_resume.STORE[n_q] = DEFINED (PINT 33)',
                'S_null_resume.STORE[n_source] = DEFINED (PARRAY n_replacement)', 'n_replacement =/= n_array',
                '$heap_owners($heap_prune($heap_graph(S_null_resume)), HARRAY n_array) = 1',
                'PhpStep: S_null_resume ~> S_null_release', 'S_null_release.TODO = (' + null_marker(1) + ') :: ptask_tail*',
            ] + driven('S_null_resume', 'S_null_phase', 'S_null_release') + [
                'PhpStep: S_null_phase ~> S_read',
                'S_read.TODO = (AT porigin_x (LIST_STORE expression (KNOWN (PINT 33)) false z_x)) :: ptask_read*',
                'S_read.STORE = S_null_phase.STORE', 'S_read.ARRAYS = S_null_phase.ARRAYS',
            ] + seek('S_null_phase', 4, 'S_next') + [
                'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_tail false eps z_tail) :: ptask_next*',
                'z_tail = 21', 'S_next.RESULT = VARIABLE ($ptascii("key")) z_tail',
                'S_next.STORE[n_x] = DEFINED (PINT 33)', 'S_next.STORE[n_key_new] = DEFINED (PINT 2)',
                '$list_undefined_key_plan(S_next) = eps', '$list_null_key_plan(S_next) = eps',
                'PhpStep: S_next ~> S_tail_read',
                'S_tail_read.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 7)) false z_target)) :: ptask_after*',
                'S_done = $drive_steps(S_next, 2000)', 'S_done.STORE[n_x] = DEFINED (PINT 33)',
                'S_done.STORE[n_y] = DEFINED (PINT 7)',
                '$undefined_key_notices(S_done.EVENTS) = [WARNING ($ptascii("key")) z]',
            ]
        else:
            checks += [
                'S_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
                '$entry_lookup(S_resume.ARRAYS[n_array].ITEMS, KSTRING eps) = (DIRECT (PINT 9))',
                '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KSTRING eps) = (DIRECT (PINT 77))',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
                '~((HARRAY n_array) <- S_phase.ALLOCATIONS)',
                '~$list_null_key_source(S_phase, ' + args + ', 0)',
                'PhpStep: S_phase ~> S_value',
                'S_value.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
                'S_value.EVENTS = S_phase.EVENTS', '$undefined_key_notices(S_value.EVENTS) = eps',
            ] + seek('S_phase', 14, 'S_next') + [
                'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_y true phpType13_y* z_y) :: ptask_y*',
                'S_next.RESULT = KNOWN (PINT 1)', 'S_next.STORE[n_x] = DEFINED PNULL',
                'PhpStep: S_next ~> S_yread',
                'S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_q) true z_target)) :: ptask_after*',
                'S_yread.STORE[n_q] = DEFINED (PINT 33)',
            ] + driven('S_next', 'S_yread_driven', 'S_yread') + [
                'S_target_found = $drive_steps(S_yread_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
                'S_target = S_target_found[.COMPLETION = NORMAL]',
                'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("y")) = (n_q)',
                '$lookup(S_bound_raw.ENV, $ptascii("outside")) = (n_y)', 'S_bound_raw.STORE[n_y] = DEFINED (PINT 88)',
            ] + driven('S_target', 'S_bound', 'S_bound_raw') + [
                'S_done = $drive_steps(S_bound, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
                'S_done.STORE[n_y] = DEFINED (PINT 88)', '$undefined_key_notices(S_done.EVENTS) = eps',
                '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
            ]
        checks += ['~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HCELL n_key_new) <- S_done.ALLOCATIONS)',
                   '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
                   '$drive_steps(S_resume, 2000) = S_done']
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
