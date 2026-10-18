#!/usr/bin/env python3
"""Reached protected-table expiry, saved source cells and throw cancellation."""
import base64
import hashlib
import json
from pathlib import Path

import list_float_ref_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($list_float_ref_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_FLOAT_REF_RESULT n_source n_array n expression phpType13* z n_bits i 0) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = LIST_KEY_FLOAT_REF_RESULT n_source n_array n expression phpType13* z n_bits i 0
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def expected_stderr(name, path):
    if name.endswith('insert-expiry'):
        return (b'Deprecated: Implicit conversion from float 0.5 to int loses precision in '
                + bytes(path) + b' on line 19\n')
    return b''


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    inserted = name.endswith('insert-expiry')
    index, line, integer = (1, 14, -2) if thrown else (0, 19 if inserted else 15, 0)
    args = f'n_source, n_array, {index}, expression, phpType13*, z, n_bits, i'
    marker = lambda phase: f'LIST_KEY_FLOAT_REF_RESULT n_source n_array {index} expression phpType13* z n_bits i {phase}'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        f'$list_float_ref_key_plan(S) = (({args}))',
        f'S.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {integer}', 'S.ORIGIN = (porigin)',
        'S.RESULT = VARIABLE ($ptascii("key")) z', '$list_float_key_pending(S)',
        '$list_float_key_plan(S) = eps', '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_array)',
        'n_source <- S.REFCELLS', '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)', '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        f'$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT {"$(-2)" if thrown else "1"}) = (ALIAS n_q)',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_source) = 2',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        '$list_float_ref_key_source(S, ' + args + ', 0)',
        '$task_nodes(' + marker(0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_source]',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, phpType13*, z, n_bits, $(i + 1), 0)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, phpType13*, $(z + 1), n_bits, i, 0)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, eps, z, n_bits, i, 0)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, phpType13*, z, 18446744073709551616, i, 0)',
        '~$list_float_ref_key_source(S, ' + args + ', 2)',
        '~$list_float_ref_key_source(S[.ORIGIN = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.CODE = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.SOURCES = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.REFCELLS = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.ALLOCATIONS = eps], ' + args + ', 0)',
        f'~$list_float_ref_key_source(S, n_source, (|S.ARRAYS|), {index}, expression, phpType13*, z, n_bits, i, 1)',
        '$list_float_ref_key_plan(S[.RESULT = KNOWN (PFLOAT n_bits)]) = eps',
        '$list_float_ref_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_float_ref_key_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_source] = DEFINED PNULL]) = eps',
        f'$list_float_ref_key_plan(S[.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression true phpType13* z) :: ptask_tail*]) = eps',
        '$origin_node(S.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        '$list_missing_flat(phpType13_all*)', '$list_references(phpType13_all*)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_pattern (NExprArray (SEQUENCE eps) eps) metadata)) :: pcunit.OCCURRENCES]]',
        '~$list_float_ref_key_source(S_literal, ' + args + ', 0)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
    ] + seek('S_dispatch', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
        checks += seek('S_entered', 6, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_pending, n_second) = eps', 'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)', '~((HCELL n_source) <- S_pending.ALLOCATIONS)',
            '~((HARRAY n_array) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_before] = DEFINED (PINT 9)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
            '$list_float_ref_key_source(S_resume, ' + args + ', 0)',
            'S_resume.STORE[n_x] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
            'S_release.ALLOCATIONS = S_resume.ALLOCATIONS',
            'S_release_driven_found = $drive_steps(S_resume, 1)', 'S_release_driven_found.COMPLETION = BUDGET',
            'S_phase = S_release_driven_found[.COMPLETION = NORMAL]',
            'S_phase.TODO = S_release.TODO', 'S_phase.STORE = S_release.STORE', 'S_phase.ARRAYS = S_release.ARRAYS',
            '~((HARRAY n_array) <- S_phase.ALLOCATIONS)', '(HCELL n_source) <- S_phase.ALLOCATIONS',
            '$list_float_ref_key_source(S_phase, ' + args + ', 1)',
            '~$list_float_ref_key_source(S_phase, ' + args + ', 0)',
            '$call_descriptors_valid(S_phase)', '$heap_valid($heap_graph(S_phase))',
            'PhpStep: S_phase ~> S_store',
            'S_store.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
            'S_store.STORE = S_phase.STORE', 'S_store.ARRAYS = S_phase.ARRAYS', 'S_store.EVENTS = S_phase.EVENTS',
        ]
        if inserted:
            checks += [
                'S_resume.ERRORHANDLER =/= S.ERRORHANDLER', 'S_resume.STORE[n_y] = DEFINED (PINT 88)',
                'S_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
                '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 0) = (DIRECT (PINT 77))',
                '$entry_lookup(S_resume.ARRAYS[n_array].ITEMS, KINT 0) = eps',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
                '$heap_owners($heap_prune($heap_graph(S_phase)), HCELL n_q) = 2',
                'S_phase.STORE[n_q] = DEFINED (PINT 33)',
            ]
        else:
            checks += [
                'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.STORE[n_source] = DEFINED PNULL',
                '$lookup(S_resume.ENV, $ptascii("a")) = (n_rebound)', 'n_rebound =/= n_source',
                '$lookup(S_resume.ENV, $ptascii("other")) = (n_rebound)',
                '$lookup(S_resume.ENV, $ptascii("key")) = (n_replacement)', 'n_replacement =/= n_key_cell',
                '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 1',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
                '~((HCELL n_q) <- S_phase.ALLOCATIONS)', 'S_phase.STORE[n_source] = DEFINED PNULL',
            ]
        checks += seek('S_phase', 14, 'S_next') + [
            'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_y true eps z_y) :: ptask_y*',
            'S_next.STORE[n_x] = DEFINED PNULL', 'PhpStep: S_next ~> S_yread',
            'S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_slot) true z_target)) :: (LIST_NEXT (REFERENCE n_source) 2 eps z_after) :: ptask_y*',
            'S_yread.STORE[n_source] = DEFINED (PARRAY n_after)',
            '$entry_lookup(S_yread.ARRAYS[n_after].ITEMS, KINT 1) = (ALIAS n_slot)',
        ]
        if inserted:
            checks += ['S_next.RESULT = VARIABLE ($ptascii("next")) 20',
                       '$lookup(S_next.ENV, $ptascii("next")) = (n_next_cell)',
                       'S_next.STORE[n_next_cell] = DEFINED (PINT 1)',
                       'n_slot = n_q', 'n_after = n_live', 'S_yread.STORE[n_slot] = DEFINED (PINT 33)']
        else:
            checks += ['S_next.RESULT = KNOWN (PINT 1)', 'S_next.STORE[n_source] = DEFINED PNULL',
                       'n_after =/= n_array', 'S_yread.STORE[n_slot] = DEFINED PNULL',
                       '$heap_count(HARRAY n_after, $pools_nodes(S_yread.POOLS)) = 0']
        checks += [
            'S_yread_driven_found = $drive_steps(S_next, 1)', 'S_yread_driven_found.COMPLETION = BUDGET',
            'S_yread_driven = S_yread_driven_found[.COMPLETION = NORMAL]',
            'S_yread_driven.STORE = S_yread.STORE', 'S_yread_driven.ARRAYS = S_yread.ARRAYS',
            'S_yread_driven.TODO = S_yread.TODO',
            'S_done = $drive_steps(S_yread_driven, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
            '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
            '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HARRAY n_after) <- S_done.ALLOCATIONS)',
            '~((HCELL n_slot) <- S_done.ALLOCATIONS)', '$drive_steps(S_resume, 2000) = S_done',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
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
