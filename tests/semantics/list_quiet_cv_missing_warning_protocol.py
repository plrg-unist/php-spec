#!/usr/bin/env python3
"""Reached quiet CV conversions, immutable carrier history and saved keys."""
import base64
import hashlib
import json
from pathlib import Path

import list_quiet_cv_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    boolean = name.endswith('bool-two-handlers')
    floating = name.endswith('float-snapshot')
    thrown = not boolean and not floating
    index, line = (0, 22) if boolean else (0, 13) if floating else (1, 16)
    key = 'KINT 0' if boolean else 'KINT (-2)' if floating else 'KSTRING ($ptascii("gone-key"))'
    args = f'KNOWN (PARRAY n_array), {index}, expression, phpType13*, z, {key}'
    marker = f'LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) {index} expression phpType13* z ({key})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]',
        '$list_missing_plan(S) = ((' + args + '))',
        f'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.RESULT = VARIABLE ($ptascii("key")) z', 'S.ORIGIN = (porigin)',
        f'$list_missing_integer_cv_item(S, {index}, expression, phpType13*, z) = (S.RESULT)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED pvalue_key',
        '$list_missing_quiet_key(pvalue_key) = (' + key + ')',
        r'$string_plain(pvalue_key) = pvalue_key \/ $string_carrier_valid(S, pvalue_key)',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_source(S, ' + args + ')',
        '$list_missing_cv_key_valid(' + key + ')', '$list_missing_cv_key_valid(KINT 9)',
        '$list_missing_cv_key_valid(KSTRING eps)', '~$list_missing_cv_key_valid(KSTRING ([0]))',
        '~$list_missing_cv_key_valid(KSTRING ([256]))',
        f'~$list_missing_source(S, KNOWN PNULL, {index}, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_array), {index}, expression, phpType13*, $(z + 1), {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_array), {index + 1}, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_array), {index}, expression, eps, z, {key})',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$list_missing_plan(S[.RESULT = KNOWN pvalue_key]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED (PARRAY n_array)]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 9218868437227405312)]) = eps',
        '$list_missing_plan(S[.ENV = $unbind(S.ENV, $ptascii("key"))]) = eps',
        '$entry_lookup(S.ARRAYS[n_array].ITEMS, ' + key + ') = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '$task_nodes(' + marker + ') = [HARRAY n_array]',
        '$heap_count(HCELL n_key_cell, $task_nodes(' + marker + ')) = 0',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.FRAMES = pframe :: eps',
        'S_entered.CURRENT =/= eps', '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if boolean:
        checks += ['pvalue_key = PBOOL false']
    elif floating:
        checks += ['pvalue_key = PFLOAT n_bits', '$float_long(n_bits, true) = ((-2), eps)']
    else:
        checks += [
            'pvalue_key = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("gone-key"))',
            'S.STRINGDATA[n_string] = $ptascii("gone-key")', '$string_carrier_valid(S, pvalue_key)',
            '$list_missing_plan(S[.STRINGDATA = eps]) = eps',
            '$list_missing_plan(S[.STRINGDATA[n_string] = $ptascii("different")]) = eps',
        ]
    if not boolean:
        checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
                   f'$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT {0 if floating else 1}) = (ALIAS n_q)',
                   '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2']
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_pending_found = $list_warning_seek(S_entered, 6, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$lookup(S_pending.ENV, $ptascii("key")) = eps', '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)',
            '$lookup(S_pending.ENV, $ptascii("a")) = eps', '$lookup(S_pending.ENV, $ptascii("q")) = eps',
            '~((HARRAY n_array) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            'S_pending.STRINGDATA[n_string] = $ptascii("gone-key")', '$string_carrier_valid(S_pending, pvalue_key)',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_before] = DEFINED (PINT 9)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + marker + ') :: ptask_tail*',
            '$list_missing_source(S_return, ' + args + ')', 'S_return.STORE[n_a] = DEFINED (PARRAY n_live)',
            'n_live =/= n_array', 'S_return.STORE[n_x] = DEFINED (PINT 99)',
            'PhpStep: S_return ~> S_schedule', 'S_schedule.STORE = S_return.STORE', 'S_schedule.ARRAYS = S_return.ARRAYS',
            f'S_schedule.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_array), {index}, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_next_found = $list_warning_seek(S_schedule, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET', 'S_next = S_next_found[.COMPLETION = NORMAL]',
            'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)',
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_y false phpType13_y* z_y) :: ptask_y*',
            'S_next.RESULT = VARIABLE ($ptascii("next")) z_y',
        ]
        if floating:
            checks += [
                'S_return.ERRORHANDLER = S.ERRORHANDLER', 'S_return.STORE[n_key_cell] = DEFINED (PFLOAT n_changed)',
                '$float_long(n_changed, true) = (2, [PRECISIONLOSS])', 'S_return.STORE[n_q] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 3',
                '$entry_lookup(S_return.ARRAYS[n_array].ITEMS, KINT (-2)) = eps',
                '$entry_lookup(S_return.ARRAYS[n_live].ITEMS, KINT (-2)) = (DIRECT (PINT 55))',
                'z_y = 14', '$lookup(S_next.ENV, $ptascii("next")) = (n_next)',
                'S_next.STORE[n_next] = DEFINED (PBOOL false)', '$list_missing_plan(S_next) = eps',
                'PhpStep: S_next ~> S_read',
                'S_read.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 33)) false z_store_y)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 2 phpType13_y* z_follow_y) :: ptask_y*',
                'S_done = $drive_steps(S_read, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.STORE[n_y] = DEFINED (PINT 33)',
                '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_live) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            ]
        else:
            checks += [
                'S_return.ERRORHANDLER =/= S.ERRORHANDLER', 'S_return.STORE[n_key_cell] = DEFINED (PFLOAT n_changed)',
                '$float_long(n_changed, true) = (1, [PRECISIONLOSS])', 'z_y = 23',
                '$lookup(S_next.ENV, $ptascii("next")) = (n_next)', 'S_next.STORE[n_next] = DEFINED (PBOOL true)',
                '$list_missing_plan(S_next) = ((KNOWN (PARRAY n_array), 1, expression_y, phpType13_y*, z_y, KINT 1))',
                'PhpStep: S_next ~> S_second_dispatch', 'S_second_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_y*',
                'perrorcall_second.RESUME = LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 1 expression_y phpType13_y* z_y (KINT 1)',
                '$error_call_valid(S_second_dispatch, perrorcall_second)',
                'S_second_entered_found = $list_warning_seek(S_second_dispatch, 3, 2000)',
                r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
                'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', 'S_second_entered.FRAMES = pframe_second :: eps',
                '$call_descriptors_valid(S_second_entered)', '$heap_valid($heap_graph(S_second_entered))',
                'S_second_return_found = $list_warning_seek(S_second_entered, 2, 2000)',
                r'S_second_return_found.COMPLETION = NORMAL \/ S_second_return_found.COMPLETION = BUDGET',
                'S_second_return = S_second_return_found[.COMPLETION = NORMAL]',
                'S_second_return.TODO = (LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 1 expression_y phpType13_y* z_y (KINT 1)) :: ptask_y*',
                'S_second_return.STORE[n_key_cell] = DEFINED (PBOOL false)',
                'S_second_return.STORE[n_x] = DEFINED (PINT 77)', 'S_second_return.STORE[n_y] = DEFINED (PINT 88)',
                '$list_missing_source(S_second_return, KNOWN (PARRAY n_array), 1, expression_y, phpType13_y*, z_y, KINT 1)',
                'PhpStep: S_second_return ~> S_second_schedule', 'S_second_schedule.STORE = S_second_return.STORE',
                'S_done = $drive_steps(S_second_schedule, 2000)', 'S_done.STORE[n_x] = DEFINED (PINT 77)', 'S_done.STORE[n_y] = DEFINED PNULL',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = $heap_count(HARRAY n_array, $pools_nodes(S_done.POOLS))',
                '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
            ]
        checks += ['$lookup(S_done.ENV, $ptascii("present")) = (n_present)', 'S_done.STORE[n_present] = DEFINED PNULL',
                   '$lookup(S_done.ENV, $ptascii("calls")) = (n_calls)', f'S_done.STORE[n_calls] = DEFINED (PINT {2 if boolean else 1})',
                   '$lookup(S_done.ENV, $ptascii("a")) = eps', '$lookup(S_done.ENV, $ptascii("dest")) = eps']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
