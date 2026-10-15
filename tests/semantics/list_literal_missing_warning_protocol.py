#!/usr/bin/env python3
"""Literal RHS source certificates, saved owners and effect cancellation."""
import base64
import hashlib
import json
from pathlib import Path

import list_literal_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
dec $literal_result_task(ptask) : bool
def $literal_result_task(COMPILED_RESULT b) = true
def $literal_result_task(AT porigin ptask) = $literal_result_task(ptask)
def $literal_result_task(ptask) = false -- otherwise
dec $literal_result_tasks(ptask*) : bool
def $literal_result_tasks(eps) = false
def $literal_result_tasks(ptask :: ptask_tail*) = ($literal_result_task(ptask) \/ $literal_result_tasks(ptask_tail*))
'''


def conditions(name, program, path, stdout):
    pooled = name == 'list-literal-missing-pooled-result'
    thrown = name == 'list-literal-missing-reference-throw'
    args = 'KNOWN (PARRAY n_array), 0, expression, phpType13*, z, KINT 0'
    marker = 'LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 0 expression phpType13* z (KINT 0)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        '$list_missing_plan(S) = ((KNOWN (PARRAY n_array), 0, expression, phpType13*, z, KINT 0))',
        'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 0 expression false phpType13* z) :: ptask_tail*',
        'S.ORIGIN = (porigin)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_child((porigin_assign), [PCFIELD 1]) = (porigin_rhs)',
        '$origin_node(S.SOURCES, porigin_rhs) = (expression_rhs)',
        'expression_rhs = NExprArray (SEQUENCE phpType13_rhs*) metadata',
        '$list_value_cv(expression_rhs) = eps',
        '$list_missing_rhs(S, porigin_rhs, expression_rhs, n_array)',
        '~$list_missing_rhs(S[.CODE = eps], porigin_rhs, expression_rhs, n_array)',
        '~$list_missing_rhs(S, PORIGIN 9 eps, expression_rhs, n_array)',
        '$list_missing_source(S, ' + args + ')',
        '~$list_missing_source(S, KNOWN (PARRAY n_array), 0, expression, phpType13*, $(z + 1), KINT 0)',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        'n_pool = $heap_count(HARRAY n_array, $pools_nodes(S.POOLS))',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = $(1 + n_pool)',
        '$task_nodes(LIST_FETCH (KNOWN (PARRAY n_array)) 0 expression false phpType13* z) = [HARRAY n_array]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    if pooled:
        checks += [
            '$(n_pool > 0)', '$compiled_read(S, porigin_rhs) = (PARRAY n_array)',
            '~$list_missing_rhs(S, porigin_rhs, expression_rhs, $(n_array + 1))',
            '~$list_missing_rhs(S[.POOLS = eps], porigin_rhs, expression_rhs, n_array)',
            '$literal_result_tasks(S.TODO)', '$compiled_effects(S, porigin_assign) =/= eps',
            '$compiled_read(S, porigin_assign) = (PARRAY n_result)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'n_pool = 0', '$compiled_read(S, porigin_rhs) = eps',
            'porigin_rhs = PORIGIN n_unit pcpath_rhs', '$code_at(S.CODE, n_unit) = (pcode)',
            '$code_expression(pcode.EXPRESSIONS, pcpath_rhs) = ((z_rhs, false))',
            '~$array_immutable(S, n_array)',
            '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 1) (ALIAS n_q)]',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        ]
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
            'S_pending_found = $list_warning_seek(S_dispatch, 5, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_pending, 5)',
            'S_pending.TODO = (THROW_SEARCH n_second) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            '~((HARRAY n_array) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)',
        ]
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_dispatch, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_return, 2)',
            'S_return.TODO = (' + marker + ') :: ptask_tail*',
            '$list_missing_rhs(S_return, porigin_rhs, expression_rhs, n_array)',
            'S_return.ERRORHANDLER = S.ERRORHANDLER',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = $(1 + n_pool)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'PhpStep: S_return ~> S_store',
            'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_array), 0, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.RESULT = KNOWN PNULL', 'S_store.STORE = S_return.STORE',
            'S_store.ARRAYS = S_return.ARRAYS', '$heap_valid($heap_graph(S_store))',
            'S_done = $drive_steps(S_store, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
        ]
        if pooled:
            checks += [
                'S_return.STORE[n_x] = DEFINED (PINT 90)', 'S_done.STORE[n_y] = DEFINED (PINT 2)',
                'S_done.STORE[n_dest] = DEFINED (PARRAY n_result)',
                '(HARRAY n_array) <- S_done.ALLOCATIONS',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = $(n_pool + $heap_count(HARRAY n_array, $value_nodes(PARRAY n_result)))',
            ]
        else:
            checks += [
                '$lookup(S_return.ENV, $ptascii("q")) = eps', 'S_return.STORE[n_q] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1',
                'S_done.STORE[n_y] = DEFINED (PINT 33)',
                '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            ]
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~$list_warning_tasks(S_done.TODO)',
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
