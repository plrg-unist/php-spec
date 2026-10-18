#!/usr/bin/env python3
"""Reached undefined/NULL conversion cycles with detached and shared tables."""
import base64
import hashlib
import json
from pathlib import Path

import list_undefined_key_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(LIST_KEY_UNDEFINED_RESULT poperand n_array n expression phpType13* z n_phase) = true
def $list_warning_task(LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z n_phase) = true
def $list_warning_frontier(S, 10) = ($list_undefined_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_UNDEFINED_RESULT poperand n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (LIST_KEY_UNDEFINED_RESULT poperand n_array n expression phpType13* z 1) :: ptask_tail*
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 16) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 1) :: ptask_tail*
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, result, raw):
    return [f'{result}_found = $drive_steps({start}, 1)', f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ['STORE', 'ARRAYS', 'TODO', 'RESULT']]]


def entered(start, label, marker):
    state = f'S_{label}_entered'
    return seek(start, 3, state) + [
        f'{state}.CURRENT =/= eps', f'{state}.FRAMES = pframe_{label} :: pframe_{label}_tail*',
        f'pframe_{label}.TODO = (ERROR_HANDLER_RESULT perrorcall_{label}_entered) :: ptask_{label}_frame*',
        f'perrorcall_{label}_entered.RESUME = {marker}', f'perrorcall_{label}_entered.TARGET =/= eps',
        f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def conditions(name, program, path, stdout):
    cascade = name.endswith('three-handlers')
    index, line = (1, 26) if cascade else (0, 23)
    args = f'REFERENCE n_source, n_array, {index}, expression, phpType13*, z'
    marker = lambda kind, phase: f'LIST_KEY_{kind}_RESULT (REFERENCE n_source) n_array {index} expression phpType13* z {phase}'
    missing = f'LIST_MISSING_RESULT (REFERENCE n_source) {index} expression phpType13* z (KSTRING eps)'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        '$list_undefined_key_plan(S) = ((' + args + '))',
        f'S.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.RESULT = VARIABLE ($ptascii("key")) z', 'S.ORIGIN = (porigin)',
        '$lookup(S.ENV, $ptascii("key")) = eps', '$list_undefined_key_empty(S, $ptascii("key"))',
        '$list_undefined_key_pending(S)', '$list_null_key_plan(S) = eps', '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'n_source <- S.REFCELLS',
        'S.STORE[n_source] = DEFINED (PARRAY n_array)', '$list_null_key_source(S, ' + args + ', 0)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        '$entry_lookup(S.ARRAYS[n_array].ITEMS, KSTRING eps) = eps' if cascade else '$entry_lookup(S.ARRAYS[n_array].ITEMS, KSTRING eps) = (ALIAS n_q)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("next")) = (n_next_cell)',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
        f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = {2 if cascade else 1}',
        '$list_undefined_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$list_undefined_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_undefined_key_plan(S[.ENV = (BIND ($ptascii("key")) n_x) :: S.ENV]) = eps',
        '$list_undefined_key_plan(S[.ENV = (BIND ($ptascii("key")) (|S.STORE|)) :: S.ENV]) = eps',
        '$list_undefined_key_plan(S[.ENV = (BIND ($ptascii("key")) n_x) :: S.ENV][.STORE[n_x] = UNDEFINED][.ALLOCATIONS = eps]) = eps',
        '~$list_null_key_source(S[.ORIGIN = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.SOURCES = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.CODE = eps], ' + args + ', 0)',
        f'~$list_null_key_source(S, REFERENCE n_source, n_array, {index}, expression, phpType13*, $(z + 1), 0)',
        '$task_nodes(' + marker('UNDEFINED', 0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker('UNDEFINED', 1) + ') = [HCELL n_source]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_u_dispatch', 'S_u_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_u) :: ptask_tail*',
        'perrorcall_u.RESUME = ' + marker('UNDEFINED', 0), 'perrorcall_u.LEVEL = 2', 'perrorcall_u.LINE = z',
        'perrorcall_u.MESSAGE = $list_undefined_key_message($ptascii("key"))',
        'perrorcall_u.EVENT = WARNING ($ptascii("key")) z', '$error_call_valid(S_u_dispatch, perrorcall_u)',
        '~$error_call_valid(S_u_dispatch, perrorcall_u[.LEVEL = 8192])',
        '~$error_call_valid(S_u_dispatch, perrorcall_u[.MESSAGE = $list_undefined_key_message($ptascii("other"))])',
        '~$error_call_valid(S_u_dispatch, perrorcall_u[.RESUME = ' + marker('UNDEFINED', 1) + '])',
    ] + driven('S', 'S_u_dispatch_driven', 'S_u_dispatch') + entered('S_u_dispatch_driven', 'u', marker('UNDEFINED', 0))
    checks += seek('S_u_entered', 11, 'S_u_resume') + [
        'S_u_resume.TODO = (' + marker('UNDEFINED', 0) + ') :: ptask_tail*',
        '$list_null_key_source(S_u_resume, ' + args + ', 0)', 'S_u_resume.ERRORHANDLER =/= S.ERRORHANDLER',
        'S_u_resume.STORE[n_q] = DEFINED (PINT 33)', 'S_u_resume.STORE[n_x] = DEFINED (PINT 77)',
        'S_u_resume.STORE[n_dest] = DEFINED (PINT 150)',
        '$lookup(S_u_resume.ENV, $ptascii("key")) = (n_key_cell)',
        f'$heap_owners($heap_prune($heap_graph(S_u_resume)), HARRAY n_array) = {3 if cascade else 2}',
    ]
    if cascade:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("copy")) = (n_copy)', 'S_u_resume.STORE[n_copy] = DEFINED (PARRAY n_array)',
                   'S_u_resume.STORE[n_source] = DEFINED (PARRAY n_array)',
                   'S_u_resume.STORE[n_key_cell] = DEFINED (PFLOAT n_key_first)', '$float_long(n_key_first, true) = (9, [PRECISIONLOSS])']
    else:
        checks += ['$lookup(S_u_resume.ENV, $ptascii("hold")) = (n_hold)', 'S_u_resume.STORE[n_hold] = DEFINED (PARRAY n_array)',
                   'S_u_resume.STORE[n_source] = DEFINED (PARRAY n_saved)', 'n_saved =/= n_array',
                   '$entry_lookup(S_u_resume.ARRAYS[n_saved].ITEMS, KINT 1) = (DIRECT (PINT 44))',
                   '$lookup(S_u_resume.ENV, $ptascii("a")) = (n_replacement)', 'n_replacement =/= n_source',
                   '$lookup(S_u_resume.ENV, $ptascii("oldq")) = (n_q)',
                   '$lookup(S_u_resume.ENV, $ptascii("q")) = (n_q_replacement)', 'n_q_replacement =/= n_q',
                   'S_u_resume.STORE[n_q_replacement] = DEFINED (PINT 66)',
                   'S_u_resume.STORE[n_key_cell] = DEFINED (PINT 1)',
                   '$heap_count(HARRAY n_saved, $pools_nodes(S_u_resume.POOLS)) = n_pooled', '$(n_pooled > 0)']
    checks += ['PhpStep: S_u_resume ~> S_u_release', 'S_u_release.TODO = (' + marker('UNDEFINED', 1) + ') :: ptask_tail*']
    checks += driven('S_u_resume', 'S_u_phase', 'S_u_release') + [
        '$list_null_key_source(S_u_phase, ' + args + ', 1)', '(HARRAY n_array) <- S_u_phase.ALLOCATIONS',
        f'$heap_owners($heap_prune($heap_graph(S_u_phase)), HARRAY n_array) = {2 if cascade else 1}',
        'PhpStep: S_u_phase ~> S_d_dispatch', 'S_d_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_d) :: ptask_tail*',
        'perrorcall_d.RESUME = ' + marker('NULL', 0), 'perrorcall_d.LEVEL = 8192', 'perrorcall_d.LINE = z',
        'perrorcall_d.MESSAGE = $list_null_key_message()', '$error_call_valid(S_d_dispatch, perrorcall_d)',
        f'$heap_owners($heap_prune($heap_graph(S_d_dispatch)), HARRAY n_array) = {3 if cascade else 2}',
    ] + driven('S_u_phase', 'S_d_dispatch_driven', 'S_d_dispatch') + entered('S_d_dispatch_driven', 'd', marker('NULL', 0))
    checks += seek('S_d_entered', 15, 'S_d_resume') + [
        'S_d_resume.TODO = (' + marker('NULL', 0) + ') :: ptask_tail*',
        f'S_d_resume.STORE[n_q] = DEFINED (PINT {44 if cascade else 55})',
        f'S_d_resume.STORE[n_x] = DEFINED (PINT {88 if cascade else 99})',
        'S_d_resume.STORE[n_key_cell] = DEFINED (PFLOAT n_key_live)', '$float_long(n_key_live, true) = (2, [PRECISIONLOSS])',
        'PhpStep: S_d_resume ~> S_d_release', 'S_d_release.TODO = (' + marker('NULL', 1) + ') :: ptask_tail*',
    ] + driven('S_d_resume', 'S_d_phase', 'S_d_release') + [
        '$list_null_key_source(S_d_phase, ' + args + ', 1)',
        f'$heap_owners($heap_prune($heap_graph(S_d_phase)), HARRAY n_array) = {2 if cascade else 1}',
        'PhpStep: S_d_phase ~> S_lookup']
    if cascade:
        checks += ['S_lookup.TODO = (ERROR_HANDLER_INVOKE perrorcall_w) :: ptask_tail*',
                   'perrorcall_w.RESUME = ' + missing, 'perrorcall_w.LEVEL = 2', 'perrorcall_w.LINE = z',
                   '$error_call_valid(S_lookup, perrorcall_w)']
        checks += entered('S_lookup', 'w', missing) + seek('S_w_entered', 2, 'S_w_resume') + [
            'S_w_resume.TODO = (' + missing + ') :: ptask_tail*',
            'S_w_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
            'S_w_resume.STORE[n_copy] = DEFINED (PARRAY n_array)',
            '$entry_lookup(S_w_resume.ARRAYS[n_array].ITEMS, KSTRING eps) = eps',
            '$entry_lookup(S_w_resume.ARRAYS[n_live].ITEMS, KSTRING eps) = (DIRECT (PINT 66))',
            'S_w_resume.STORE[n_q] = DEFINED (PINT 55)', 'S_w_resume.STORE[n_x] = DEFINED (PINT 99)',
            'S_w_resume.STORE[n_next_cell] = DEFINED (PINT 1)',
            '$heap_owners($heap_prune($heap_graph(S_w_resume)), HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_w_resume)), HARRAY n_live) = 1',
            '$heap_owners($heap_prune($heap_graph(S_w_resume)), HCELL n_q) = 3',
            'PhpStep: S_w_resume ~> S_value_raw',
            'S_value_raw.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: ptask_after*',
            'S_value_raw.STORE[n_x] = DEFINED (PINT 99)',
        ]
        value_start = 'S_w_resume'
    else:
        checks += ['S_lookup.TODO = (AT porigin_x (LIST_STORE expression (KNOWN (PINT 55)) false z_x)) :: ptask_after*',
                   'S_lookup.STORE[n_source] = DEFINED (PARRAY n_saved)',
                   'S_lookup.STORE[n_x] = DEFINED (PINT 99)']
        value_start = 'S_d_phase'
    checks += driven(value_start, 'S_value', 'S_value_raw' if cascade else 'S_lookup') + [
        'S_x_target_found = $drive_steps(S_value, 1)', 'S_x_target_found.COMPLETION = BUDGET',
        'S_x_target = S_x_target_found[.COMPLETION = NORMAL]', 'PhpStep: S_x_target ~> S_xbound_raw',
        'S_xbound_raw.STORE[n_x] = DEFINED PNULL' if cascade else 'S_xbound_raw.STORE[n_x] = DEFINED (PINT 55)',
    ] + driven('S_x_target', 'S_xbound', 'S_xbound_raw') + seek('S_xbound', 14, 'S_next') + [
        f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) {index + 1} expression_y true eps {line + 1}) :: ptask_next*',
        f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}', 'S_next.STORE[n_next_cell] = DEFINED (PINT 1)',
        'PhpStep: S_next ~> S_yread',
        'S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_ref) true z_y)) :: ptask_yafter*',
        f'S_yread.STORE[n_ref] = DEFINED (PINT {55 if cascade else 44})',
        'S_yread.STORE[n_source] = DEFINED (PARRAY n_selected)',
        '$entry_lookup(S_yread.ARRAYS[n_selected].ITEMS, KINT 1) = (ALIAS n_ref)',
    ]
    if cascade:
        checks += ['n_ref = n_q', 'n_selected = n_live', '$heap_owners($heap_prune($heap_graph(S_yread)), HCELL n_q) = 4']
    else:
        checks += ['n_selected =/= n_saved', '$entry_lookup(S_yread.ARRAYS[n_saved].ITEMS, KINT 1) = (DIRECT (PINT 44))',
                   'S_yread.STORE[n_hold] = DEFINED (PARRAY n_array)', 'S_yread.STORE[n_q] = DEFINED (PINT 55)']
    checks += driven('S_next', 'S_yread_driven', 'S_yread') + [
        'S_y_target_found = $drive_steps(S_yread_driven, 1)', 'S_y_target_found.COMPLETION = BUDGET',
        'S_y_target = S_y_target_found[.COMPLETION = NORMAL]', 'PhpStep: S_y_target ~> S_ybound_raw',
        '$lookup(S_ybound_raw.ENV, $ptascii("y")) = (n_ref)', '(HCELL n_y) <- S_ybound_raw.ALLOCATIONS',
    ] + driven('S_y_target', 'S_ybound', 'S_ybound_raw') + [
        '~((HCELL n_y) <- S_ybound.ALLOCATIONS)', 'S_done = $drive_steps(S_ybound, 2000)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_selected) <- S_done.ALLOCATIONS)',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
        '~((HCELL n_ref) <- S_done.ALLOCATIONS)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
        '$drive_steps(S_u_resume, 2000) = S_done', '$drive_steps(S_d_resume, 2000) = S_done',
    ]
    if not cascade:
        checks += ['(HARRAY n_saved) <- S_done.ALLOCATIONS', '$heap_count(HARRAY n_saved, $pools_nodes(S_done.POOLS)) = n_pooled']
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
