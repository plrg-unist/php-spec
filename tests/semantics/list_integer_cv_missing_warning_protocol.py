#!/usr/bin/env python3
"""Reached integer-CV key capture, next-key ordering and callback cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import list_integer_cv_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    snapshot = name.endswith('snapshot-next')
    second = name.endswith('second-handler')
    thrown = not snapshot and not second
    index, key, line = (0, 0, 13) if snapshot else (1, 4, 23) if second else (1, 1, 15)
    args = f'KNOWN (PARRAY n_array), {index}, expression, phpType13*, z, KINT {key}'
    marker = f'LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) {index} expression phpType13* z (KINT {key})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]',
        '$list_missing_plan(S) = ((' + args + '))',
        f'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.RESULT = VARIABLE ($ptascii("key")) z', 'S.ORIGIN = (porigin)',
        f'$list_missing_integer_cv_item(S, {index}, expression, phpType13*, z) = (S.RESULT)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', f'S.STORE[n_key] = DEFINED (PINT {key})',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$origin_node(S.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        '$list_missing_flat(phpType13_all*)', '~$list_references(phpType13_all*)',
        '$list_missing_nested_context(S, porigin) = eps',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata_assign)',
        '$code_expression_at_source(S, porigin_assign, [PCFIELD 1]) = (z_initial)',
        f'$list_missing_item(S, porigin, phpType13_all*, 0, {index}, z_initial) = eps',
        '$list_missing_source(S, ' + args + ')',
        # Pure source compatibility cannot reconstruct the historical integer.
        f'$list_missing_source(S, KNOWN (PARRAY n_array), {index}, expression, phpType13*, z, KINT {key + 9})',
        f'~$list_missing_source(S, KNOWN PNULL, {index}, expression, phpType13*, z, KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_array), {index}, expression, phpType13*, $(z + 1), KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_array), {index + 1}, expression, phpType13*, z, KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_array), {index}, expression, eps, z, KINT {key})',
        '~$list_missing_source(S[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$list_missing_plan(S[.RESULT = KNOWN (PINT 0)]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_missing_plan(S[.STORE = $set_cell(S.STORE, n_key, UNDEFINED)]) = eps',
        '$list_missing_plan(S[.STORE = $set_cell(S.STORE, n_key, DEFINED PNULL)]) = eps',
        '$list_missing_plan(S[.STORE = $set_cell(S.STORE, n_key, DEFINED (PARRAY n_array))]) = eps',
        '$list_missing_plan(S[.ENV = $unbind(S.ENV, $ptascii("key"))]) = eps',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_pattern (NExprArray (SEQUENCE eps) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '~$list_missing_source(S_literal, ' + args + ')',
        'S_nested = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign (NExprArray (SEQUENCE ([NArrayItem ABSENT expression_pattern (BOOLEAN false) (BOOLEAN false) eps])) eps) expression_rhs metadata_assign)) :: pcunit.OCCURRENCES]]',
        '~$list_missing_source(S_nested, ' + args + ')',
        f'$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT {key}) = eps',
        'S_present = S[.ARRAYS[n_array] = S.ARRAYS[n_array][.ITEMS = (ENTRY (KINT ' + str(key) + ') (DIRECT (PINT 11))) :: S.ARRAYS[n_array].ITEMS]]',
        '$list_missing_plan(S_present) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = $(2 + $heap_count(HARRAY n_array, $pools_nodes(S.POOLS)))',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '$task_nodes(' + marker + ') = [HARRAY n_array]',
        '$heap_count(HCELL n_key, $task_nodes(' + marker + ')) = 0',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.FRAMES = pframe :: eps',
        'S_entered.CURRENT =/= eps', '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if not second:
        checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
                   '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 2) = (ALIAS n_q)',
                   '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
                   '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
                   '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)']
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 9)',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_pending_found = $list_warning_seek(S_entered, 6, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$lookup(S_pending.ENV, $ptascii("key")) = eps', '$lookup(S_pending.ENV, $ptascii("a")) = eps',
            '$lookup(S_pending.ENV, $ptascii("q")) = eps', '~((HCELL n_key) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_q) <- S_pending.ALLOCATIONS)', '~((HARRAY n_array) <- S_pending.ALLOCATIONS)',
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
            'n_live =/= n_array', '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = $(1 + $heap_count(HARRAY n_array, $pools_nodes(S.POOLS)))',
            'PhpStep: S_return ~> S_store',
            f'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_array), {index}, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS',
            'S_next_found = $list_warning_seek(S_store, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
        ]
        if snapshot:
            checks += [
                'S_return.ERRORHANDLER = S.ERRORHANDLER', 'S_return.STORE[n_key] = DEFINED (PINT 7)',
                'S_return.STORE[n_x] = DEFINED (PINT 99)', 'S_return.STORE[n_q] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 3',
                '$entry_lookup(S_return.ARRAYS[n_array].ITEMS, KINT 0) = eps',
                '$entry_lookup(S_return.ARRAYS[n_live].ITEMS, KINT 0) = (DIRECT (PINT 11))',
                'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)',
                'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_y false phpType13_y* z_y) :: ptask_y*',
                'S_next.RESULT = VARIABLE ($ptascii("next")) z_y', 'z_y = 14',
                '$lookup(S_next.ENV, $ptascii("next")) = (n_next)', 'S_next.STORE[n_next] = DEFINED (PINT 2)',
                '$list_missing_plan(S_next) = eps', 'PhpStep: S_next ~> S_read',
                'S_read.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 33)) false z_store_y)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 2 phpType13_y* z_follow_y) :: ptask_y*',
                'S_done = $drive_steps(S_read, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
                'S_done.STORE[n_y] = DEFINED (PINT 33)',
                '$lookup(S_done.ENV, $ptascii("present")) = (n_present)', 'S_done.STORE[n_present] = DEFINED PNULL',
                '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
                '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            ]
        else:
            checks += [
                'S_return.ERRORHANDLER =/= S.ERRORHANDLER', 'S_return.STORE[n_key] = DEFINED (PINT 2)',
                '$lookup(S.ENV, $ptascii("missing")) = (n_missing)', '$lookup(S.ENV, $ptascii("tail")) = (n_tail)',
                'S_return.STORE[n_missing] = DEFINED (PINT 99)',
                'S_next.STORE[n_missing] = DEFINED PNULL', 'S_next.STORE[n_tail] = DEFINED (PINT 8)',
                'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 2 expression_tail false eps z_tail) :: ptask_next*',
                'S_next.RESULT = VARIABLE ($ptascii("later")) z_tail', 'z_tail = 24',
                '$list_missing_plan(S_next) = ((KNOWN (PARRAY n_array), 2, expression_tail, eps, z_tail, KINT 5))',
                'PhpStep: S_next ~> S_second_dispatch',
                'S_second_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_next*',
                'perrorcall_second.RESUME = LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 2 expression_tail eps z_tail (KINT 5)',
                '$error_call_valid(S_second_dispatch, perrorcall_second)',
                'S_second_entered_found = $list_warning_seek(S_second_dispatch, 3, 2000)',
                r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
                'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', 'S_second_entered.FRAMES = pframe_second :: eps',
                '$call_descriptors_valid(S_second_entered)', '$heap_valid($heap_graph(S_second_entered))',
                'S_second_return_found = $list_warning_seek(S_second_entered, 2, 2000)',
                r'S_second_return_found.COMPLETION = NORMAL \/ S_second_return_found.COMPLETION = BUDGET',
                'S_second_return = S_second_return_found[.COMPLETION = NORMAL]',
                'S_second_return.TODO = (LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 2 expression_tail eps z_tail (KINT 5)) :: ptask_next*',
                'S_second_return.STORE[n_key] = DEFINED (PINT 6)',
                'S_second_return.STORE[n_missing] = DEFINED (PINT 77)', 'S_second_return.STORE[n_tail] = DEFINED (PINT 88)',
                '$list_missing_source(S_second_return, KNOWN (PARRAY n_array), 2, expression_tail, eps, z_tail, KINT 5)',
                'PhpStep: S_second_return ~> S_second_store', 'S_second_store.STORE = S_second_return.STORE',
                'S_done = $drive_steps(S_second_store, 2000)', 'S_done.STORE[n_tail] = DEFINED PNULL',
                'S_done.STORE[n_missing] = DEFINED (PINT 77)', 'S_done.STORE[n_key] = DEFINED (PINT 6)',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = $heap_count(HARRAY n_array, $pools_nodes(S_done.POOLS))',
                '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
            ]
        checks += ['$lookup(S_done.ENV, $ptascii("calls")) = (n_calls)',
                   f'S_done.STORE[n_calls] = DEFINED (PINT {1 if snapshot else 2})',
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
