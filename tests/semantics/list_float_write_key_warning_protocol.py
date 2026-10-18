#!/usr/bin/env python3
"""Reached writable pre-COW, unique-table binding, detached NULL and throw."""
import base64
import hashlib
import json
from pathlib import Path

import list_float_write_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($list_float_write_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_FLOAT_WRITE_RESULT n_source n_array n expression phpType13* z n_bits i 0) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = LIST_KEY_FLOAT_WRITE_RESULT n_source n_array n expression phpType13* z n_bits i 0
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def expected_stderr(name, path):
    if name.endswith('pre-cow-singleton'):
        return (b'Deprecated: Implicit conversion from float 0.5 to int loses precision in '
                + bytes(path) + b' on line 14\n')
    return b''


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    copied = name.endswith('pre-cow-singleton')
    index, line, integer = (1, 14, 2) if thrown else (0, 14 if copied else 13, 0)
    plan = f'n_source, {index}, expression, phpType13*, z, n_bits, i'
    args = f'n_source, n_array, {index}, expression, phpType13*, z, n_bits, i'
    original = args.replace('n_array', 'n_before')
    marker = lambda phase: f'LIST_KEY_FLOAT_WRITE_RESULT n_source n_array {index} expression phpType13* z n_bits i {phase}'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        '$list_float_write_key_plan(S) = ((' + plan + '))',
        f'S.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression true phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {integer}', 'S.ORIGIN = (porigin)',
        'S.RESULT = VARIABLE ($ptascii("key")) z', '$list_float_write_key_pending(S)',
        '$list_float_key_plan(S) = eps', '$list_float_ref_key_plan(S) = eps', '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_before)',
        'n_source <- S.REFCELLS', '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)', '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$lookup(S.ENV, $ptascii("y")) = (n_target)', f'S.STORE[n_target] = DEFINED (PINT {8 if thrown else 7})',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_float_write_key_source(S, ' + original + ', 0)',
        f'$list_missing_integer_cv_item(S, {index}, expression, phpType13*, z) = eps',
        f'~$list_float_write_key_source(S, n_source, n_before, {index}, expression, phpType13*, z, n_bits, $(i + 1), 0)',
        f'~$list_float_write_key_source(S, n_source, n_before, {index}, expression, phpType13*, $(z + 1), n_bits, i, 0)',
        f'~$list_float_write_key_source(S, n_source, n_before, {index}, expression, eps, z, n_bits, i, 0)',
        f'~$list_float_write_key_source(S, n_source, n_before, {index}, expression, phpType13*, z, 18446744073709551616, i, 0)',
        '~$list_float_write_key_source(S, ' + original + ', 2)',
        '~$list_float_write_key_source(S[.ORIGIN = eps], ' + original + ', 0)',
        '~$list_float_write_key_source(S[.CODE = eps], ' + original + ', 0)',
        '~$list_float_write_key_source(S[.SOURCES = eps], ' + original + ', 0)',
        '~$list_float_write_key_source(S[.REFCELLS = eps], ' + original + ', 0)',
        '~$list_float_write_key_source(S[.ALLOCATIONS = eps], ' + original + ', 0)',
        '$list_float_write_key_plan(S[.RESULT = KNOWN (PFLOAT n_bits)]) = eps',
        '$list_float_write_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_float_write_key_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$list_float_write_key_plan(S[.STORE[n_source] = DEFINED PNULL]) = eps',
        f'$list_float_write_key_plan(S[.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*]) = eps',
        '$origin_node(S.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        '$list_missing_flat(phpType13_all*)', '$list_references(phpType13_all*)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_pattern (NExprArray (SEQUENCE eps) eps) metadata)) :: pcunit.OCCURRENCES]]',
        '~$list_float_write_key_source(S_literal, ' + original + ', 0)',
        '$heap_count(HARRAY n_before, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_source) = 2',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if copied or thrown:
        checks += ['$lookup(S.ENV, $ptascii("copy")) = (n_copy_cell)',
                   'S.STORE[n_copy_cell] = DEFINED (PARRAY n_before)',
                   '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_before) = 2']
    else:
        checks += ['$heap_owners($heap_prune($heap_graph(S)), HARRAY n_before) = 1',
                   '$lookup(S.ENV, $ptascii("outside")) = (n_target)',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 2']
    checks += [f'$entry_lookup(S.ARRAYS[n_before].ITEMS, KINT {2 if thrown else 1}) = (ALIAS n_q)',
               'S.STORE[n_q] = DEFINED (PINT 2)']
    if copied:
        checks += ['$lookup(S.ENV, $ptascii("q")) = eps',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 1']
    else:
        checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'S_dispatch.STORE[n_source] = DEFINED (PARRAY n_array)',
        'S_dispatch.ARRAYS[n_before] = S.ARRAYS[n_before]',
        f'S_dispatch.STORE[n_target] = DEFINED (PINT {8 if thrown else 7})',
        '$task_nodes(' + marker(0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_source]',
        '$list_float_write_key_source(S_dispatch, ' + args + ', 0)',
        '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
    ]
    if copied or thrown:
        checks += ['n_array =/= n_before', '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_before) = 1']
    else:
        checks += ['n_array = n_before']
    if copied:
        checks += ['$entry_lookup(S_dispatch.ARRAYS[n_array].ITEMS, KINT 1) = (DIRECT (PINT 2))',
                   '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_q) = 1']
    elif thrown:
        checks += ['$entry_lookup(S_dispatch.ARRAYS[n_array].ITEMS, KINT 2) = (ALIAS n_q)',
                   '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_q) = 3',
                   'S_dispatch_driven_found = $drive_steps(S, 1)',
                   'S_dispatch_driven_found.COMPLETION = BUDGET',
                   'S_dispatch_driven = S_dispatch_driven_found[.COMPLETION = NORMAL]',
                   'S_dispatch_driven.STORE = S_dispatch.STORE',
                   'S_dispatch_driven.ARRAYS = S_dispatch.ARRAYS',
                   'S_dispatch_driven.TODO = S_dispatch.TODO',
                   'S_dispatch_driven.RESULT = S_dispatch.RESULT']
    checks += seek('S_dispatch_driven' if thrown else 'S_dispatch', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_early)', 'S.STORE[n_early] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
                   '$lookup(S.ENV, $ptascii("alias")) = (n_target)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
        checks += seek('S_entered', 6, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_pending, n_second) = eps', 'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            'S_pending.STORE[n_target] = DEFINED (PINT 99)', 'S_pending.STORE[n_later] = DEFINED (PINT 7)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)', '~((HCELL n_source) <- S_pending.ALLOCATIONS)',
            '~((HARRAY n_array) <- S_pending.ALLOCATIONS)', '~((HARRAY n_before) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '$lookup(S_pending.ENV, $ptascii("y")) = (n_target)', '$lookup(S_pending.ENV, $ptascii("alias")) = (n_target)',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_early] = DEFINED (PINT 9)',
            'S_done.STORE[n_target] = DEFINED (PINT 99)', 'S_done.STORE[n_later] = DEFINED (PINT 7)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*', 'S_resume.ERRORHANDLER = S.ERRORHANDLER',
            '$list_float_write_key_source(S_resume, ' + args + ', 0)',
            f'S_resume.STORE[n_target] = DEFINED (PINT {99 if copied else 88})',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)',
        ]
        if copied:
            checks += ['S_resume.STORE[n_source] = DEFINED (PARRAY n_array)',
                       '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 2',
                       '$entry_lookup(S_resume.ARRAYS[n_array].ITEMS, KINT 1) = (DIRECT (PINT 2))',
                       '$entry_lookup(S_resume.ARRAYS[n_before].ITEMS, KINT 1) = (ALIAS n_q)']
        else:
            checks += ['S_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
                       '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 2) = (DIRECT (PINT 77))',
                       '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
                       '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3']
        checks += [
            'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
            'S_release.ALLOCATIONS = S_resume.ALLOCATIONS',
            'S_phase_found = $drive_steps(S_resume, 1)', 'S_phase_found.COMPLETION = BUDGET',
            'S_phase = S_phase_found[.COMPLETION = NORMAL]',
            'S_phase.TODO = S_release.TODO', 'S_phase.STORE = S_release.STORE', 'S_phase.ARRAYS = S_release.ARRAYS',
            '$list_float_write_key_source(S_phase, ' + args + ', 1)',
            'PhpStep: S_phase ~> S_fetch',
            'S_fetch.TODO = (AT porigin_y (LIST_STORE expression (REFERENCE n_slot) true z_target)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
            'n_slot =/= n_target', 'n_slot <- S_fetch.REFCELLS', '(HCELL n_slot) <- S_fetch.ALLOCATIONS',
        ]
        if copied:
            checks += ['$list_float_write_key_unique(S_phase, n_array)',
                       '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 1',
                       'S_fetch.STORE[n_slot] = DEFINED (PINT 9)',
                       '$entry_lookup(S_fetch.ARRAYS[n_array].ITEMS, KINT 0) = (ALIAS n_slot)',
                       'S_fetch.ARRAYS[n_before] = S_phase.ARRAYS[n_before]']
        else:
            checks += ['~((HARRAY n_array) <- S_phase.ALLOCATIONS)',
                       '~$list_float_write_key_source(S_phase, ' + args + ', 0)',
                       '~$list_float_write_key_unique(S_phase, n_array)',
                       'S_fetch.STORE[n_slot] = DEFINED PNULL', 'S_fetch.ARRAYS = S_phase.ARRAYS',
                       '$heap_owners($heap_prune($heap_graph(S_fetch)), HCELL n_slot) = 1',
                       '$heap_owners($heap_prune($heap_graph(S_phase)), HCELL n_q) = 2']
        checks += [
            'S_fetch_driven_found = $drive_steps(S_phase, 1)', 'S_fetch_driven_found.COMPLETION = BUDGET',
            'S_fetch_driven = S_fetch_driven_found[.COMPLETION = NORMAL]',
            'S_fetch_driven.STORE = S_fetch.STORE', 'S_fetch_driven.ARRAYS = S_fetch.ARRAYS', 'S_fetch_driven.TODO = S_fetch.TODO',
            'S_target_found = $drive_steps(S_fetch_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
            'S_target = S_target_found[.COMPLETION = NORMAL]',
            'S_target.TODO = (LIST_STORE expression (REFERENCE n_slot) true z_target) :: ptask_bound*',
            'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("y")) = (n_slot)',
            f'$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_target) = {0 if copied else 1}',
            'S_bound_found = $drive_steps(S_target, 1)', 'S_bound_found.COMPLETION = BUDGET',
            'S_bound = S_bound_found[.COMPLETION = NORMAL]',
            '~((HCELL n_target) <- S_bound.ALLOCATIONS)' if copied else '(HCELL n_target) <- S_bound.ALLOCATIONS',
        ]
        checks += seek('S_bound', 4, 'S_next') + [
            f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_x false eps {line + 1}) :: ptask_x*',
            f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}',
            '$lookup(S_next.ENV, $ptascii("next")) = (n_next_cell)', 'S_next.STORE[n_next_cell] = DEFINED (PINT 1)',
            'PhpStep: S_next ~> S_xread',
            f'S_xread.TODO = (AT porigin_x (LIST_STORE expression_x (KNOWN (PINT {2 if copied else 33})) false z_x)) :: ptask_xafter*',
            'S_done = $drive_steps(S_next, 2000)',
            '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_before) <- S_done.ALLOCATIONS)',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            '~((HCELL n_slot) <- S_done.ALLOCATIONS)', '~((HCELL n_target) <- S_done.ALLOCATIONS)',
            '$drive_steps(S_resume, 2000) = S_done',
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
