#!/usr/bin/env python3
"""Reached NULL conversion, frozen empty lookup and protected source cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import list_null_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z n_phase) = true
def $list_warning_frontier(S, 10) = ($list_null_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 0) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (LIST_KEY_NULL_RESULT poperand n_array n expression phpType13* z 1) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression true phpType13* z) :: ptask_tail*
dec $null_key_diagnostic(pevent) : pevent*
def $null_key_diagnostic(DIAGNOSTIC text n_message* z) = [DIAGNOSTIC text n_message* z]
def $null_key_diagnostic(DIAGNOSTIC_SOURCE n_unit text n_message* z) = [DIAGNOSTIC text n_message* z]
def $null_key_diagnostic(pevent) = eps -- otherwise
dec $null_key_diagnostics(pevent*) : pevent*
def $null_key_diagnostics(eps) = eps
def $null_key_diagnostics(pevent :: pevent_tail*) = $null_key_diagnostic(pevent) ++ $null_key_diagnostics(pevent_tail*)
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


def expected_stderr(name, path):
    if name.endswith('default-missing-order'):
        prefix = (b'Deprecated: Using null as an array offset is deprecated, '
                  b'use an empty string instead in ' + bytes(path))
        return prefix + b' on line 25\n' + prefix + b' on line 26\n'
    return b''


def conditions(name, program, path, stdout):
    default = name.endswith('default-missing-order')
    thrown = name.endswith('supplied-throw')
    index, line = (1, 14) if thrown else (0, 25 if default else 15)
    operand = 'KNOWN (PARRAY n_array)' if default else 'REFERENCE n_source'
    args = f'{operand}, n_array, {index}, expression, phpType13*, z'
    marker = lambda phase: f'LIST_KEY_NULL_RESULT ({operand}) n_array {index} expression phpType13* z {phase}'
    roots = '[HARRAY n_array]' if default else '[HCELL n_source, HARRAY n_array]'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        f'$list_null_key_plan(S) = (({args}))',
        f'S.TODO = (LIST_FETCH ({operand}) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)', 'S.RESULT = VARIABLE ($ptascii("key")) z',
        '$list_null_key_pending(S)', '$list_missing_plan(S) = eps',
        '$list_float_key_pending(S) = false', '$list_float_write_key_pending(S) = false',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        f'$entry_lookup(S.ARRAYS[n_array].ITEMS, {"KSTRING eps" if thrown else "KINT 1"}) = (ALIAS n_q)',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
        f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = {2 if default else 1}',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        '$list_null_key_source(S, ' + args + ', 0)',
        '$task_nodes(' + marker(0) + ') = ' + roots,
        '$task_nodes(' + marker(1) + ') = ' + ('[HARRAY n_array]' if default else '[HCELL n_source]'),
        '~$list_null_key_source(S, ' + args + ', 2)',
        f'~$list_null_key_source(S, {operand}, n_array, {index}, expression, phpType13*, $(z + 1), 0)',
        f'~$list_null_key_source(S, {operand}, n_array, {index + 1}, expression, phpType13*, z, 0)',
        f'~$list_null_key_source(S, {operand}, n_array, {index}, expression, eps, z, 0)',
        '~$list_null_key_source(S[.ORIGIN = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.CODE = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.SOURCES = eps], ' + args + ', 0)',
        '~$list_null_key_source(S[.ALLOCATIONS = eps], ' + args + ', 0)',
        f'~$list_null_key_source(S, {operand}, (|S.ARRAYS|), {index}, expression, phpType13*, z, 1)',
        '$list_null_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$list_null_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_null_key_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 0)]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PBOOL false)]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        '$list_null_key_plan(S[.STORE[n_key_cell] = DEFINED (PSTRING eps)]) = eps',
        f'$list_null_key_plan(S[.TODO = (LIST_FETCH ({operand}) {index} expression true phpType13* z) :: ptask_tail*]) = eps',
        '$origin_node(S.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        '$list_missing_flat(phpType13_all*)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_pattern (NExprArray (SEQUENCE eps) eps) metadata)) :: pcunit.OCCURRENCES]]',
        '~$list_null_key_source(S_literal, ' + args + ', 0)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
    ] + driven('S', 'S_dispatch_driven', 'S_dispatch') + seek('S_dispatch_driven', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if not default:
        checks += ['n_source <- S.REFCELLS', '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1']
    if thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
        checks += seek('S_entered', 13, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '~((HCELL n_source) <- S_pending.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)',
            '~((HARRAY n_array) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '$null_key_diagnostics(S_pending.EVENTS) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_before] = DEFINED (PINT 9)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
            '$list_null_key_source(S_resume, ' + args + ', 0)',
            'S_resume.ERRORHANDLER =/= S.ERRORHANDLER', 'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            f'S_resume.STORE[n_x] = DEFINED (PINT {77 if default else 99})',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KSTRING eps) = (DIRECT (PINT 77))',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
            'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
            'S_release.ALLOCATIONS = S_resume.ALLOCATIONS',
        ] + driven('S_resume', 'S_phase', 'S_release') + [
            '$list_null_key_source(S_phase, ' + args + ', 1)',
            '$call_descriptors_valid(S_phase)', '$heap_valid($heap_graph(S_phase))',
        ]
        if default:
            checks += [
                'S_resume.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)',
                '$entry_lookup(S_phase.ARRAYS[n_array].ITEMS, KSTRING eps) = eps',
                '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 1',
                '$heap_owners($heap_prune($heap_graph(S_phase)), HCELL n_q) = 3',
                'PhpStep: S_phase ~> S_missing',
                'S_missing.TODO = (ERROR_HANDLER_INVOKE perrorcall_missing) :: ptask_tail*',
                'perrorcall_missing.RESUME = LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 0 expression phpType13* z (KSTRING eps)',
                'perrorcall_missing.LEVEL = 2', '$error_call_valid(S_missing, perrorcall_missing)',
                'S_missing.STORE[n_x] = DEFINED (PINT 77)',
                '$null_key_diagnostics(S_missing.EVENTS) = [DIAGNOSTIC "Deprecated" $list_null_key_message() z]',
            ] + seek('S_missing', 3, 'S_warning_entered') + [
                'S_warning_entered.FRAMES = pframe_warning :: pframe_warning_tail*',
                'pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall_warning) :: ptask_warning*',
                'perrorcall_warning.LEVEL = 2', 'perrorcall_warning.TARGET =/= eps',
            ] + seek('S_warning_entered', 2, 'S_warning_resume') + [
                'S_warning_resume.STORE[n_x] = DEFINED (PINT 88)', 'S_warning_resume.STORE[n_y] = DEFINED (PINT 66)',
                'PhpStep: S_warning_resume ~> S_null_store',
                'S_null_store.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 1 phpType13* z_next) :: ptask_tail*',
                'S_null_store.STORE = S_warning_resume.STORE', 'S_null_store.ARRAYS = S_warning_resume.ARRAYS',
            ] + seek('S_warning_resume', 10, 'S_next') + [
                '$list_null_key_plan(S_next) = ((KNOWN (PARRAY n_array), n_array, 1, expression_y, phpType13_y*, z_y))',
                'z_y = 26', 'S_next.RESULT = VARIABLE ($ptascii("next")) z_y',
                '$lookup(S_next.ENV, $ptascii("next")) = (n_next_cell)', 'S_next.STORE[n_next_cell] = DEFINED PNULL',
                'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 66)',
                '~$error_handler_eligible(S_next, 8192)', '$error_handler_eligible(S_next, 2)', '$list_null_key_pending(S_next)',
                'PhpStep: S_next ~> S_second',
                'S_second.TODO = (LIST_KEY_NULL_RESULT (KNOWN (PARRAY n_array)) n_array 1 expression_y phpType13_y* z_y 0) :: ptask_y*',
                '$null_key_diagnostics(S_second.EVENTS) = [DIAGNOSTIC "Deprecated" $list_null_key_message() z, DIAGNOSTIC "Deprecated" $list_null_key_message() z_y]',
            ] + seek('S_second', 12, 'S_second_phase') + [
                'PhpStep: S_second_phase ~> S_second_missing',
                'S_second_missing.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_y*',
                'perrorcall_second.RESUME = LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 1 expression_y phpType13_y* z_y (KSTRING eps)',
                'S_second_missing.STORE[n_x] = DEFINED PNULL', 'S_second_missing.STORE[n_y] = DEFINED (PINT 66)',
                '$error_call_valid(S_second_missing, perrorcall_second)',
            ] + seek('S_second_missing', 3, 'S_second_entered') + seek('S_second_entered', 2, 'S_second_resume') + [
                'S_second_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_second_resume.STORE[n_y] = DEFINED (PINT 55)',
                'S_done = $drive_steps(S_second_resume, 2000)',
                'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED PNULL',
                '$null_key_diagnostics(S_done.EVENTS) = [DIAGNOSTIC "Deprecated" $list_null_key_message() z, DIAGNOSTIC "Deprecated" $list_null_key_message() z_y]',
                '$drive_steps(S_resume, 2000) = S_done',
            ]
        else:
            checks += [
                'S_resume.STORE[n_key_cell] = DEFINED (PBOOL false)', 'S_resume.STORE[n_y] = DEFINED (PINT 88)',
                '~((HARRAY n_array) <- S_phase.ALLOCATIONS)',
                '~$list_null_key_source(S_phase, ' + args + ', 0)',
                '$heap_owners($heap_prune($heap_graph(S_phase)), HCELL n_q) = 2',
                'PhpStep: S_phase ~> S_store',
                'S_store.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
                'S_store.STORE = S_phase.STORE', 'S_store.ARRAYS = S_phase.ARRAYS', 'S_store.EVENTS = S_phase.EVENTS',
            ] + seek('S_phase', 14, 'S_next') + [
                'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_y true phpType13_y* z_y) :: ptask_y*',
                'S_next.RESULT = KNOWN (PINT 1)', 'S_next.STORE[n_x] = DEFINED PNULL',
                'PhpStep: S_next ~> S_yread',
                'S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_q) true z_target)) :: (LIST_NEXT (REFERENCE n_source) 2 phpType13_y* z_after) :: ptask_y*',
                'S_yread.STORE[n_source] = DEFINED (PARRAY n_live)',
                '$entry_lookup(S_yread.ARRAYS[n_live].ITEMS, KINT 1) = (ALIAS n_q)',
                'S_yread.STORE[n_q] = DEFINED (PINT 33)',
            ] + driven('S_next', 'S_yread_driven', 'S_yread') + [
                'S_target_found = $drive_steps(S_yread_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
                'S_target = S_target_found[.COMPLETION = NORMAL]',
                'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("y")) = (n_q)',
                '$lookup(S_bound_raw.ENV, $ptascii("outside")) = (n_y)', 'S_bound_raw.STORE[n_y] = DEFINED (PINT 88)',
            ] + driven('S_target', 'S_bound', 'S_bound_raw') + [
                'S_done = $drive_steps(S_bound, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
                'S_done.STORE[n_y] = DEFINED (PINT 88)', '$null_key_diagnostics(S_done.EVENTS) = eps',
                '$drive_steps(S_resume, 2000) = S_done',
            ]
        checks += ['~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
                   '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HCELL n_source) <- S_done.ALLOCATIONS)']
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
