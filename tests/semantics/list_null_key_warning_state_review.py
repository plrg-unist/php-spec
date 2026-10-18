#!/usr/bin/env python3
"""Reached frozen empty keys, retired CVs and replacement missing handlers."""
import base64
import hashlib
import json
from pathlib import Path

import list_null_key_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z n_phase) = true
def $list_warning_frontier(S, 10) = ($list_null_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 1) :: ptask_tail*
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) 2 expression true phpType13* z) :: ptask_tail*
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, result, raw):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ['STORE', 'ARRAYS', 'TODO', 'RESULT']]]


def conditions(name, program, path, stdout):
    mixed = name.endswith('missing-replacement-handler')
    index, line = (1, 22) if mixed else (0, 17)
    args = f'poperand_source, n_array, {index}, expression, phpType13*, z'
    marker = lambda phase: f'LIST_KEY_NULL_RESULT poperand_source n_array {index} expression phpType13* z {phase}'
    missing = f'LIST_MISSING_RESULT poperand_source {index} expression phpType13* z (KSTRING eps)'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        '$list_null_key_plan(S) = ((' + args + '))',
        f'S.TODO = (LIST_FETCH poperand_source {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.RESULT = VARIABLE ($ptascii("key")) z', 'S.ORIGIN = (porigin)',
        '$list_null_key_pending(S)', '$list_float_key_plan(S) = eps', '$list_float_ref_key_plan(S) = eps',
        '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_replacement_array)',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
        '$list_null_key_source(S, ' + args + ', 0)',
        '$list_null_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$list_null_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 0)]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PBOOL false)]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4602678819172646912)]) = eps',
        f'~$list_null_key_source(S, poperand_source, n_array, {index}, expression, phpType13*, $(z + 1), 0)',
        f'~$list_null_key_source(S, poperand_source, n_array, {index}, expression, eps, z, 0)',
        '~$list_null_key_source(S, ' + args + ', 2)',
        '~$list_null_key_source(S[.ORIGIN = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.SOURCES = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.CODE = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.ALLOCATIONS = eps], ' + args + ', 0)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if mixed:
        checks += ['poperand_source = REFERENCE n_a', 'n_a <- S.REFCELLS',
                   '$lookup(S.ENV, $ptascii("hold")) = (n_hold)', 'S.STORE[n_hold] = DEFINED PNULL',
                   '$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
                   '$lookup(S.ENV, $ptascii("next")) = (n_next_cell)',
                   '$entry_lookup(S.ARRAYS[n_array].ITEMS, KSTRING eps) = eps']
    else:
        checks += ['poperand_source = KNOWN (PARRAY n_array)', 'n_replacement_array =/= n_array',
                   '~$list_null_key_source(S, poperand_source, n_replacement_array, 0, expression, phpType13*, z, 0)',
                   '$lookup(S.ENV, $ptascii("key_alias")) = (n_key_cell)',
                   '$lookup(S.ENV, $ptascii("key_replacement")) = (n_key_replacement)',
                   '$lookup(S.ENV, $ptascii("q_replacement")) = (n_q_replacement)',
                   '$entry_lookup(S.ARRAYS[n_array].ITEMS, KSTRING eps) = (ALIAS n_q)']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$task_nodes(' + marker(0) + ') = [HCELL n_a, HARRAY n_array]' if mixed else '$task_nodes(' + marker(0) + ') = [HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_a]' if mixed else '$task_nodes(' + marker(1) + ') = [HARRAY n_array]',
    ] + driven('S', 'S_dispatch_driven', 'S_dispatch') + seek('S_dispatch_driven', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
        '$list_null_key_source(S_resume, ' + args + ', 0)',
        'S_resume.STORE[n_q] = DEFINED (PINT 33)', 'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
        '$lookup(S_resume.ENV, $ptascii("a")) = (n_replacement)', 'n_a =/= n_replacement',
    ]
    if mixed:
        checks += ['$lookup(S_resume.ENV, $ptascii("hold")) = (n_a)',
                   'S_resume.STORE[n_a] = DEFINED (PARRAY n_array)', 'S_resume.STORE[n_x] = DEFINED (PINT 77)',
                   'S_resume.STORE[n_key_cell] = DEFINED (PFLOAT n_key_live)',
                   '$float_long(n_key_live, true) = (2, [PRECISIONLOSS])',
                   'S_resume.STORE[n_next_cell] = DEFINED (PFLOAT n_key_live)',
                   '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 2']
    else:
        checks += ['~((HCELL n_a) <- S_resume.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
                   '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
                   '$lookup(S_resume.ENV, $ptascii("key")) = (n_key_replacement)',
                   'S_resume.STORE[n_key_replacement] = DEFINED (PINT 1)',
                   '$lookup(S_resume.ENV, $ptascii("q")) = (n_q_replacement)',
                   'S_resume.STORE[n_q_replacement] = DEFINED (PINT 66)',
                   'S_resume.STORE[n_x] = DEFINED (PINT 99)',
                   '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
                   '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1']
    checks += ['PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
               'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
               ] + driven('S_resume', 'S_phase', 'S_release') + [
               '(HARRAY n_array) <- S_phase.ALLOCATIONS', '$list_null_key_source(S_phase, ' + args + ', 1)',
               '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 1',
               'PhpStep: S_phase ~> S_lookup']
    if mixed:
        checks += [
            'S_lookup.TODO = (ERROR_HANDLER_INVOKE perrorcall_missing) :: ptask_tail*',
            'perrorcall_missing.RESUME = ' + missing, 'perrorcall_missing.LEVEL = 2', 'perrorcall_missing.LINE = z',
            'perrorcall_missing.MESSAGE = $list_missing_message(KSTRING eps)', '$error_call_valid(S_lookup, perrorcall_missing)',
            'S_lookup.STORE[n_x] = DEFINED (PINT 77)',
        ] + seek('S_lookup', 3, 'S_warning_entered') + [
            'S_warning_entered.FRAMES = pframe_warning :: pframe_warning_tail*',
            'pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall_warning) :: ptask_warning_tail*',
            'perrorcall_warning.RESUME = ' + missing, 'perrorcall_warning.TARGET =/= eps',
            '$task_nodes(perrorcall_warning.RESUME) = [HCELL n_a]',
        ] + seek('S_warning_entered', 2, 'S_missing_resume') + [
            'S_missing_resume.TODO = (' + missing + ') :: ptask_tail*',
            'S_missing_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_missing_resume.STORE[n_before] = DEFINED (PINT 9)',
            'S_missing_resume.STORE[n_q] = DEFINED (PINT 55)', 'S_missing_resume.STORE[n_next_cell] = DEFINED (PINT 1)',
            'S_missing_resume.STORE[n_a] = DEFINED (PARRAY n_array)',
            '$entry_lookup(S_missing_resume.ARRAYS[n_array].ITEMS, KSTRING eps) = (DIRECT (PINT 66))',
            'PhpStep: S_missing_resume ~> S_value',
            'S_value.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_target)) :: ptask_after*',
            'S_value.STORE[n_x] = DEFINED (PINT 99)',
        ]
        start = 'S_missing_resume'
    else:
        checks += ['S_lookup.TODO = (AT porigin_x (LIST_STORE expression (KNOWN (PINT 33)) false z_target)) :: ptask_after*',
                   'S_lookup.STORE = S_phase.STORE', 'S_lookup.ARRAYS = S_phase.ARRAYS']
        start = 'S_phase'
    checks += driven(start, 'S_value_driven', 'S_value' if mixed else 'S_lookup') + [
               'S_target_found = $drive_steps(S_value_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
               'S_target = S_target_found[.COMPLETION = NORMAL]',
               'PhpStep: S_target ~> S_bound_raw',
               'S_bound_raw.STORE[n_x] = DEFINED PNULL' if mixed else 'S_bound_raw.STORE[n_x] = DEFINED (PINT 33)',
               ] + driven('S_target', 'S_bound', 'S_bound_raw')
    if mixed:
        checks += seek('S_bound', 14, 'S_next') + [
            f'S_next.TODO = (LIST_FETCH (REFERENCE n_a) 2 expression_y true eps {line + 1}) :: ptask_next*',
            f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}',
            'S_next.STORE[n_x] = DEFINED PNULL', 'PhpStep: S_next ~> S_yref',
            'S_yref.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_q) true z_y)) :: ptask_yafter*',
            'S_yref.STORE[n_q] = DEFINED (PINT 55)', 'S_yref.STORE[n_a] = DEFINED (PARRAY n_array)',
            '$heap_owners($heap_prune($heap_graph(S_yref)), HCELL n_q) = 3',
        ] + driven('S_next', 'S_yref_driven', 'S_yref') + [
            'S_y_target_found = $drive_steps(S_yref_driven, 1)', 'S_y_target_found.COMPLETION = BUDGET',
            'S_y_target = S_y_target_found[.COMPLETION = NORMAL]',
            'PhpStep: S_y_target ~> S_ybound_raw', '$lookup(S_ybound_raw.ENV, $ptascii("y")) = (n_q)',
            '(HCELL n_y) <- S_ybound_raw.ALLOCATIONS',
        ] + driven('S_y_target', 'S_ybound', 'S_ybound_raw') + [
            '~((HCELL n_y) <- S_ybound.ALLOCATIONS)', 'S_ybound.STORE[n_q] = DEFINED (PINT 55)',
            'S_done = $drive_steps(S_ybound, 2000)',
        ]
    else:
        checks += seek('S_bound', 4, 'S_next') + [
            f'S_next.TODO = (LIST_FETCH poperand_source 1 expression_tail false eps {line + 1}) :: ptask_next*',
            f'S_next.RESULT = VARIABLE ($ptascii("key")) {line + 1}', '$list_null_key_plan(S_next) = eps',
            'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 6)) false z_tail)) :: ptask_next_tail*',
            'S_done = $drive_steps(S_next, 2000)',
        ]
    checks += ['~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_a) <- S_done.ALLOCATIONS)',
               '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
               'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
               '$drive_steps(S, 2000) = S_done', '$drive_steps(S_resume, 2000) = S_done']
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
