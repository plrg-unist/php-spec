#!/usr/bin/env python3
"""Reached converted-key lookup, default reporting and throw retirement."""
import base64
import hashlib
import json
from pathlib import Path

import list_float_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($list_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_KEY_FLOAT_RESULT n_array n expression phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = LIST_KEY_FLOAT_RESULT n_array n expression phpType13* z n_bits i
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
dec $float_key_diagnostic(pevent) : pevent*
def $float_key_diagnostic(DIAGNOSTIC text n_message* z) = [DIAGNOSTIC text n_message* z]
def $float_key_diagnostic(DIAGNOSTIC_SOURCE n_unit text n_message* z) = [DIAGNOSTIC text n_message* z]
def $float_key_diagnostic(pevent) = eps -- otherwise
dec $float_key_diagnostics(pevent*) : pevent*
def $float_key_diagnostics(eps) = eps
def $float_key_diagnostics(pevent :: pevent_tail*) = $float_key_diagnostic(pevent) ++ $float_key_diagnostics(pevent_tail*)
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def expected_stderr(name, path):
    if name.endswith('two-conversions-default'):
        return (b'Deprecated: Implicit conversion from float 2.5 to int loses precision in '
                + bytes(path) + b' on line 20\n')
    return b''


def conditions(name, program, path, stdout):
    default = name.endswith('two-conversions-default')
    thrown = name.endswith('supplied-throw')
    index, line, integer = (1, 14, -2) if thrown else (0, 20, 2) if default else (0, 13, 0)
    args = f'n_array, {index}, expression, phpType13*, z, n_bits, i'
    marker = f'LIST_KEY_FLOAT_RESULT n_array {index} expression phpType13* z n_bits i'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        f'$list_float_key_plan(S) = ((n_array, {index}, expression, phpType13*, z, n_bits, i))',
        f'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {integer}', 'S.ORIGIN = (porigin)',
        'S.RESULT = VARIABLE ($ptascii("key")) z', '$list_float_key_pending(S)', '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)',
        '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$list_float_key_source(S, ' + args + ')', '$task_nodes(' + marker + ') = [HARRAY n_array]',
        f'~$list_float_key_source(S, n_array, {index}, expression, phpType13*, z, n_bits, $(i + 1))',
        f'~$list_float_key_source(S, n_array, {index}, expression, phpType13*, $(z + 1), n_bits, i)',
        f'~$list_float_key_source(S, n_array, {index}, expression, eps, z, n_bits, i)',
        f'~$list_float_key_source(S, n_array, {index}, expression, phpType13*, z, 18446744073709551616, i)',
        '~$list_float_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$list_float_key_source(S[.CODE = eps], ' + args + ')',
        '~$list_float_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_float_key_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$list_float_key_plan(S[.RESULT = KNOWN (PFLOAT n_bits)]) = eps',
        '$list_float_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_float_key_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_float_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_float_key_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_float_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$list_float_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        f'$list_float_key_plan(S[.TODO = (LIST_FETCH (REFERENCE n_a) {index} expression false phpType13* z) :: ptask_tail*]) = eps',
        '$origin_node(S.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        '$list_missing_flat(phpType13_all*)', '~$list_references(phpType13_all*)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_pattern (NExprArray (SEQUENCE eps) eps) metadata)) :: pcunit.OCCURRENCES]]',
        '~$list_float_key_source(S_literal, ' + args + ')',
        'n_pool = $heap_count(HARRAY n_array, $pools_nodes(S.POOLS))',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = $(2 + n_pool)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if default:
        checks += ['$(n_pool > 0)', '$lookup(S.ENV, $ptascii("next")) = (n_next_cell)',
                   '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 2) = (DIRECT (PINT 22))']
    else:
        checks += ['n_pool = 0', '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
                   f'$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT {-2 if thrown else 1}) = (ALIAS n_q)',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
    ] + seek('S_dispatch', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
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
            '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)', '~((HARRAY n_array) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_before] = DEFINED (PINT 9)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)', '$float_key_diagnostics(S_done.EVENTS) = eps',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*', '$list_float_key_source(S_resume, ' + args + ')',
            'S_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_resume.STORE[n_y] = DEFINED (PINT 8)',
            'PhpStep: S_resume ~> S_lookup',
            f'S_lookup.TODO = (AT porigin_x (LIST_STORE expression (KNOWN {"(PINT 22)" if default else "PNULL"}) false z_x)) :: ptask_after*',
            'S_lookup.STORE = S_resume.STORE', 'S_lookup.ARRAYS = S_resume.ARRAYS', 'S_lookup.EVENTS = S_resume.EVENTS',
            'S_lookup_driven_found = $drive_steps(S_resume, 1)', 'S_lookup_driven_found.COMPLETION = BUDGET',
            'S_lookup_driven = S_lookup_driven_found[.COMPLETION = NORMAL]',
            'S_lookup_driven.TODO = S_lookup.TODO', 'S_lookup_driven.STORE = S_lookup.STORE',
            'S_lookup_driven.ARRAYS = S_lookup.ARRAYS',
        ]
        if default:
            checks += [
                'S_resume.ERRORHANDLER =/= S.ERRORHANDLER', 'S_resume.STORE[n_key_cell] = DEFINED (PINT 0)',
                'S_resume.STORE[n_dest] = DEFINED (PINT 150)',
                'S_resume.STORE[n_a] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = $(1 + n_pool)',
                '$float_key_diagnostics(S_resume.EVENTS) = [DIAGNOSTIC "Deprecated" $list_float_key_message(n_bits) z]',
            ] + seek('S_lookup_driven', 10, 'S_second') + [
                'S_second.STORE[n_x] = DEFINED (PINT 22)', 'S_second.STORE[n_y] = DEFINED (PINT 8)',
                'S_second.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_y false eps 21) :: ptask_y*',
                'S_second.RESULT = VARIABLE ($ptascii("next")) 21', 'S_second.STORE[n_next_cell] = DEFINED (PFLOAT n_second_bits)',
                '$float_long(n_second_bits, true) = ($(-1), [PRECISIONLOSS])',
                '$list_float_key_plan(S_second) = ((n_array, 1, expression_y, eps, 21, n_second_bits, $(-1)))',
                'PhpStep: S_second ~> S_second_dispatch',
                'S_second_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_y*',
                '$error_call_valid(S_second_dispatch, perrorcall_second)',
            ] + seek('S_second_dispatch', 13, 'S_second_entered') + seek('S_second_entered', 11, 'S_second_resume') + [
                'S_second_resume.TODO = (LIST_KEY_FLOAT_RESULT n_array 1 expression_y eps 21 n_second_bits $(-1)) :: ptask_y*',
                'S_second_resume.STORE[n_x] = DEFINED (PINT 22)', 'S_second_resume.STORE[n_y] = DEFINED (PINT 88)',
                'S_second_resume.STORE[n_next_cell] = DEFINED (PBOOL false)',
                'S_second_resume.STORE[n_dest] = DEFINED (PINT 200)',
                'PhpStep: S_second_resume ~> S_second_lookup',
                'S_second_lookup.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 11)) false z_y)) :: ptask_rest*',
                'S_second_lookup.STORE = S_second_resume.STORE', 'S_second_lookup.ARRAYS = S_second_resume.ARRAYS',
                'S_done = $drive_steps(S_second_resume, 2000)',
                'S_done.STORE[n_x] = DEFINED (PINT 22)', 'S_done.STORE[n_y] = DEFINED (PINT 11)',
                '$float_key_diagnostics(S_done.EVENTS) = [DIAGNOSTIC "Deprecated" $list_float_key_message(n_bits) z]',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = n_pool',
                '$lookup(S_done.ENV, $ptascii("calls")) = (n_calls)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
            ]
        else:
            checks += [
                'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$lookup(S_resume.ENV, $ptascii("a")) = eps',
                '$lookup(S_resume.ENV, $ptascii("key")) = eps', '$lookup(S_resume.ENV, $ptascii("q")) = eps',
                '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)', 'S_resume.STORE[n_q] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
                '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
            ] + seek('S_lookup_driven', 4, 'S_next') + [
                'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_y false eps 14) :: ptask_y*',
                'S_next.RESULT = VARIABLE ($ptascii("next")) 14',
                '$lookup(S_next.ENV, $ptascii("next")) = (n_next_cell)', 'S_next.STORE[n_next_cell] = DEFINED (PBOOL true)',
                'PhpStep: S_next ~> S_yread',
                'S_yread.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 33)) false z_y)) :: ptask_after_y*',
                'S_done = $drive_steps(S_next, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.STORE[n_y] = DEFINED (PINT 33)',
                '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
                '$float_key_diagnostics(S_done.EVENTS) = eps',
            ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
    ]
    if not thrown:
        checks += ['$drive_steps(S_resume, 2000) = S_done']
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
