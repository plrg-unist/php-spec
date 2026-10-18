#!/usr/bin/env python3
"""Literal root certificates, frozen CV keys and known-result cancellation."""
import base64
import hashlib
import json
from pathlib import Path

import list_literal_cv_missing_warning_cases as cases
import list_missing_warning_protocol as shared
import list_recursive_literal_missing_warning_protocol as literal

HELPERS = literal.HELPERS


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def conditions(name, program, path, stdout):
    runtime = name.endswith('runtime-reference')
    thrown = name.endswith('pooled-throw')
    line = 13 if runtime else 17 if thrown else 21
    key = 'KSTRING ($ptascii("lost-key"))' if runtime else 'KINT 0'
    array = 'n_inner' if thrown else 'n_root'
    args = f'KNOWN (PARRAY {array}), 0, expression, phpType13*, z, {key}'
    marker = f'LIST_MISSING_RESULT (KNOWN (PARRAY {array})) 0 expression phpType13* z ({key})'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S')
    checks += [
        '$list_missing_plan(S) = ((' + args + '))',
        f'S.TODO = (LIST_FETCH (KNOWN (PARRAY {array})) 0 expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)', 'S.RESULT = VARIABLE ($ptascii("key")) z',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED pvalue_key',
        '$list_missing_quiet_key(pvalue_key) = (' + key + ')',
        '$list_missing_integer_cv_item(S, 0, expression, phpType13*, z) = (S.RESULT)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_source(S, ' + args + ')',
        f'~$list_missing_source(S, KNOWN PNULL, 0, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY {array}), 1, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY {array}), 0, expression, eps, z, {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY {array}), 0, expression, phpType13*, $(z + 1), {key})',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '$list_missing_plan(S[.RESULT = KNOWN pvalue_key]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
    ]
    if thrown:
        checks += [
            '$literal_outer_array(S.TODO, 2) = (n_root)',
            '$reference_origin_parent(porigin, 3) = ((porigin_mid, [PCFIELD 0, PCINDEX 1, PCFIELD 1]))',
            '$reference_origin_parent(porigin_mid, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 1, PCFIELD 1]))',
            '$list_missing_nested_context(S, porigin) = eps', '$list_missing_recursive_cv_context(S, porigin) = (z_initial)',
            '$entry_lookup(S.ARRAYS[n_root].ITEMS, KINT 1) = (DIRECT (PARRAY n_mid))',
            '$entry_lookup(S.ARRAYS[n_mid].ITEMS, KINT 1) = (DIRECT (PARRAY n_inner))',
            'n_root =/= n_inner',
            '$list_missing_recursive_cv_operand_source(S, porigin, KNOWN (PARRAY n_inner))',
            '$lookup(S.ENV, $ptascii("outer")) = (n_outer_key_cell)',
            '$lookup(S.ENV, $ptascii("middle")) = (n_middle_key_cell)',
        ]
    else:
        checks += ['porigin_root = porigin', '$list_missing_recursive_cv_context(S, porigin) = eps']
    checks += [
        '$origin_node(S.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
        '~$list_references(phpType13_root*)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        '$origin_child((porigin_assign), [PCFIELD 1]) = (porigin_rhs)',
        '$origin_node(S.SOURCES, porigin_rhs) = (expression_rhs)',
        'expression_rhs = NExprArray (SEQUENCE phpType13_rhs*) metadata_rhs',
        '$list_missing_cv_rhs_source(S, porigin_rhs, expression_rhs, false)',
        '~$list_missing_cv_rhs_source(S, porigin_rhs, expression_rhs, true)',
        '~$list_missing_cv_rhs_source(S, PORIGIN 9 eps, expression_rhs, false)',
        '$list_missing_recursive_cv_operand_source(S, porigin_root, KNOWN (PARRAY n_root))',
        '~$list_missing_recursive_cv_operand_source(S[.CODE = eps], porigin_root, KNOWN (PARRAY n_root))',
        '~$list_missing_recursive_cv_operand_source(S[.ALLOCATIONS = eps], porigin_root, KNOWN (PARRAY n_root))',
        'porigin_rhs = PORIGIN n_unit_rhs pcpath_rhs', 'S.SOURCES[n_unit_rhs] = pcunit_rhs',
        'S_mismatch = S[.SOURCES[n_unit_rhs] = pcunit_rhs[.OCCURRENCES = (PCOCCURRENCE pcpath_rhs (NScalarInt (INTEGER 1) eps)) :: pcunit_rhs.OCCURRENCES]]',
        '~$list_missing_cv_rhs_source(S_mismatch, porigin_rhs, expression_rhs, false)',
        '~$list_missing_source(S_mismatch, ' + args + ')',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    nodes = ['root', 'mid', 'inner'] if thrown else ['root']
    for node in nodes:
        checks += [f'n_pool_{node} = $heap_count(HARRAY n_{node}, $pools_nodes(S.POOLS))',
                   f'$heap_count(HARRAY n_{node}, $tasks_nodes(S.TODO)) = 1',
                   f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_{node}) = $({1 if node == "root" else 2} + n_pool_{node})']
    if runtime:
        checks += [
            'n_pool_root = 0', '$compiled_read(S, porigin_rhs) = eps',
            '$code_at(S.CODE, n_unit_rhs) = (pcode_rhs)', '$code_expression(pcode_rhs.EXPRESSIONS, pcpath_rhs) = ((z_rhs, false))',
            '~$array_immutable(S, n_root)', '~$literal_result_tasks(S.TODO)',
            'pvalue_key = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("lost-key"))',
            'S.STRINGDATA[n_string] = $ptascii("lost-key")', '$string_carrier_valid(S, pvalue_key)',
            '$list_missing_plan(S[.STRINGDATA = eps]) = eps',
            '$list_missing_plan(S[.STRINGDATA[n_string] = $ptascii("wrong")]) = eps',
            '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
            '$lookup(S.ENV, $ptascii("other")) = (n_other)',
            '$entry_lookup(S.ARRAYS[n_root].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        ]
    else:
        checks += [
            'pvalue_key = PBOOL false', '$(n_pool_root > 0)',
            '$compiled_read(S, porigin_rhs) = (PARRAY n_root)',
            '$compiled_read(S, porigin_assign) = (PARRAY n_result)', '$compiled_effects(S, porigin_assign) =/= eps',
            '$literal_result_tasks(S.TODO)',
            '~$list_missing_recursive_cv_operand_source(S[.POOLS = eps], porigin_root, KNOWN (PARRAY n_root))',
            '~$list_missing_recursive_cv_operand_source(S, porigin_root, KNOWN (PARRAY (|S.ARRAYS|)))',
        ]
        if thrown:
            checks += ['~$list_missing_recursive_cv_operand_source(S, porigin_root, KNOWN (PARRAY n_inner))']
        else:
            checks += ['~$list_missing_source(S[.POOLS = eps], ' + args + ')']
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
    ] + seek('S_dispatch', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.FRAMES = pframe :: eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    for node in nodes:
        checks += [f'$heap_count(HARRAY n_{node}, $tasks_nodes(pframe.TODO)) = 1']
    if thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 5)',
                   '$lookup(S.ENV, $ptascii("outerbefore")) = (n_outerbefore)', 'S.STORE[n_outerbefore] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
        checks += seek('S_entered', 6, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '~$literal_result_tasks(S_pending.TODO)', 'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            '$throwable_previous_id(S_pending, n_second) = eps',
            '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_outer_key_cell) <- S_pending.ALLOCATIONS)', '~((HCELL n_middle_key_cell) <- S_pending.ALLOCATIONS)',
        ]
        for node in nodes:
            checks += [f'$heap_count(HARRAY n_{node}, $tasks_nodes(S_pending.TODO)) = 0',
                       f'$heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_{node}) = $({0 if node == "root" else 1} + n_pool_{node})']
        checks += ['S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_x] = DEFINED (PINT 99)',
                   'S_done.STORE[n_y] = DEFINED (PINT 8)', 'S_done.STORE[n_before] = DEFINED (PINT 5)',
                   'S_done.STORE[n_outerbefore] = DEFINED (PINT 9)', 'S_done.STORE[n_dest] = DEFINED (PINT 100)']
    else:
        checks += seek('S_entered', 2, 'S_return') + [
            'S_return.TODO = (' + marker + ') :: ptask_tail*', '$list_missing_source(S_return, ' + args + ')',
            '$list_missing_recursive_cv_operand_source(S_return, porigin_root, KNOWN (PARRAY n_root))',
            'S_return.STORE[n_x] = DEFINED (PINT 99)', 'S_return.STORE[n_y] = DEFINED (PINT 8)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_root) = $(1 + n_pool_root)',
            'PhpStep: S_return ~> S_schedule',
            'S_schedule.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_root), 0, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_schedule.STORE = S_return.STORE', 'S_schedule.ARRAYS = S_return.ARRAYS',
        ] + seek('S_schedule', 4, 'S_next') + [
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_root)) 1 expression_y false phpType13_y* z_y) :: ptask_y*',
            'S_next.RESULT = VARIABLE ($ptascii("next")) z_y',
            '$lookup(S_next.ENV, $ptascii("next")) = (n_next_cell)', 'S_next.STORE[n_next_cell] = DEFINED (PBOOL true)',
            'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)',
        ]
        if runtime:
            checks += [
                'S_return.ERRORHANDLER = S.ERRORHANDLER', '$lookup(S_return.ENV, $ptascii("key")) = eps',
                '~((HCELL n_key_cell) <- S_return.ALLOCATIONS)',
                '$lookup(S_return.ENV, $ptascii("q")) = (n_other)', 'n_other =/= n_q',
                'S_return.STORE[n_other] = DEFINED (PINT 44)', 'S_return.STORE[n_q] = DEFINED (PINT 2)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1',
                'S_return.STRINGDATA[n_string] = $ptascii("lost-key")',
                '$list_missing_plan(S_next) = eps', 'PhpStep: S_next ~> S_read',
                'S_read.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 2)) false z_store_y)) :: ptask_read*',
                'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS',
                'S_read_driven_found = $drive_steps(S_next, 1)', 'S_read_driven_found.COMPLETION = BUDGET',
                'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]',
                'S_read_driven.TODO = S_read.TODO', 'S_read_driven.STORE = S_read.STORE', 'S_read_driven.ARRAYS = S_read.ARRAYS',
                'S_done = $drive_steps(S_read_driven, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.STORE[n_y] = DEFINED (PINT 2)',
                '~((HARRAY n_root) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
                '~((HCELL n_other) <- S_done.ALLOCATIONS)',
            ]
        else:
            checks += [
                'S_return.ERRORHANDLER =/= S.ERRORHANDLER', 'S_return.STORE[n_dest] = DEFINED (PINT 150)',
                'S_return.STORE[n_key_cell] = DEFINED (PFLOAT n_changed)', '$float_long(n_changed, true) = (1, [PRECISIONLOSS])',
                '$list_missing_plan(S_next) = ((KNOWN (PARRAY n_root), 1, expression_y, phpType13_y*, z_y, KINT 1))',
                'PhpStep: S_next ~> S_second_dispatch', 'S_second_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_y*',
                'perrorcall_second.RESUME = LIST_MISSING_RESULT (KNOWN (PARRAY n_root)) 1 expression_y phpType13_y* z_y (KINT 1)',
                '$error_call_valid(S_second_dispatch, perrorcall_second)',
            ] + seek('S_second_dispatch', 3, 'S_second_entered') + seek('S_second_entered', 2, 'S_second_return') + [
                'S_second_return.STORE[n_x] = DEFINED (PINT 77)', 'S_second_return.STORE[n_y] = DEFINED (PINT 88)',
                'S_second_return.STORE[n_dest] = DEFINED (PINT 200)',
                'S_second_return.STORE[n_next_cell] = DEFINED (PFLOAT n_next_bits)', '$float_long(n_next_bits, true) = (2, [PRECISIONLOSS])',
                'S_second_return.TODO = (LIST_MISSING_RESULT (KNOWN (PARRAY n_root)) 1 expression_y phpType13_y* z_y (KINT 1)) :: ptask_y*',
                '$list_missing_source(S_second_return, KNOWN (PARRAY n_root), 1, expression_y, phpType13_y*, z_y, KINT 1)',
                'PhpStep: S_second_return ~> S_second_schedule', 'S_second_schedule.STORE = S_second_return.STORE',
                'S_second_schedule.ARRAYS = S_second_return.ARRAYS', 'S_done = $drive_steps(S_second_schedule, 2000)',
                'S_done.STORE[n_x] = DEFINED (PINT 77)', 'S_done.STORE[n_y] = DEFINED PNULL',
                '$lookup(S_done.ENV, $ptascii("calls")) = (n_calls)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
            ]
        checks += ['$lookup(S_done.ENV, $ptascii("present")) = (n_present)', 'S_done.STORE[n_present] = DEFINED PNULL',
                   '$lookup(S_done.ENV, $ptascii("dest")) = eps']
    if not runtime:
        for node in nodes:
            checks += [f'(HARRAY n_{node}) <- S_done.ALLOCATIONS',
                       f'S_done.ARRAYS[n_{node}].ITEMS = S.ARRAYS[n_{node}].ITEMS',
                       f'$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_{node}) = $({0 if node == "root" else 1} + n_pool_{node})']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~$literal_result_tasks(S_done.TODO)', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
