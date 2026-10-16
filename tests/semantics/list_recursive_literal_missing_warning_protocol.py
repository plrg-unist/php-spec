#!/usr/bin/env python3
"""Recursive literal roots, captured child owners and known-result cancellation."""
import base64
import hashlib
import json
from pathlib import Path

import list_recursive_literal_missing_warning_cases as cases
import list_literal_missing_warning_protocol as literal
import list_missing_warning_protocol as shared

HELPERS = literal.HELPERS + r'''
dec $literal_outer_array_task(ptask, nat) : nat?
def $literal_outer_array_task(LIST_NEXT (KNOWN (PARRAY n_array)) n phpType13* z, n) = (n_array)
def $literal_outer_array_task(AT porigin ptask, n) = $literal_outer_array_task(ptask, n)
def $literal_outer_array_task(ptask, n) = eps -- otherwise
dec $literal_outer_array(ptask*, nat) : nat?
def $literal_outer_array(eps, n) = eps
def $literal_outer_array(ptask :: ptask_tail*, n) = (n_array)
  -- if $literal_outer_array(ptask_tail*, n) = (n_array)
def $literal_outer_array(ptask :: ptask_tail*, n) = $literal_outer_array_task(ptask, n)
  -- if $literal_outer_array(ptask_tail*, n) = eps
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    pooled = name != 'list-recursive-literal-runtime-ref-rebind'
    thrown = name.endswith('pooled-throw')
    chain = ['root', 'upper', 'parent', 'inner'] if thrown else ['root', 'parent', 'inner']
    origins = ['porigin_' + node if node != 'inner' else 'porigin' for node in chain]
    branch, index, key = (1, 0, 0) if thrown else (0, 1 if pooled else 0, 3 if pooled else 0)
    line = 13 if pooled and not thrown else 14
    args = f'KNOWN (PARRAY n_inner), {index}, expression, phpType13*, z, KINT {key}'
    marker = f'LIST_MISSING_RESULT (KNOWN (PARRAY n_inner)) {index} expression phpType13* z (KINT {key})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]',
        f'$list_missing_plan(S) = ((KNOWN (PARRAY n_inner), {index}, expression, phpType13*, z, KINT {key}))',
        f'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)',
        f'$literal_outer_array(S.TODO, {2 if thrown else 1}) = (n_root)',
    ]
    for parent, child in zip(reversed(origins[:-1]), reversed(origins[1:])):
        checks += [f'$reference_origin_parent({child}, 3) = (({parent}, [PCFIELD 0, PCINDEX {branch}, PCFIELD 1]))',
                   f'$list_missing_nested_context(S, {parent}) = (z_{parent})']
    checks += [
        '$origin_node(S.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
        '~$list_missing_flat(phpType13_root*)', '$list_missing_nested_items(phpType13_root*)',
        '$list_missing_nested_items([NArrayItem ABSENT expression_root (BOOLEAN false) (BOOLEAN false) eps])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression (BOOLEAN true) (BOOLEAN false) eps])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression (BOOLEAN false) (BOOLEAN true) eps])',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        '$origin_child((porigin_assign), [PCFIELD 1]) = (porigin_rhs)',
        'expression_rhs = NExprArray (SEQUENCE phpType13_rhs*) metadata_rhs', '$list_value_cv(expression_rhs) = eps',
        '$list_missing_nested_rhs(expression_rhs)', '~$list_missing_nested_rhs(NScalarInt (INTEGER 1) eps)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_scalar = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NScalarInt (INTEGER 1) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_nested_context(S_scalar, porigin) = eps', '~$list_missing_source(S_scalar, ' + args + ')',
        '$list_missing_nested_operand_source(S, porigin_root, n_root)',
        '~$list_missing_nested_operand_source(S[.CODE = eps], porigin_root, n_root)',
        '~$list_missing_nested_operand_source(S[.ALLOCATIONS = eps], porigin_root, n_root)',
        '$list_missing_nested_operand_source(S, porigin, n_inner)', '$list_missing_source(S, ' + args + ')',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, phpType13*, $(z + 1), KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, eps, z, KINT {key})',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')', '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', f'S.STORE[n_x] = DEFINED (PINT {8 if pooled and not thrown else 7})',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', f'S.STORE[n_y] = DEFINED (PINT {9 if pooled and not thrown else 8})',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
    ]
    for parent, child in zip(chain[:-1], chain[1:]):
        checks += [f'$entry_lookup(S.ARRAYS[n_{parent}].ITEMS, KINT {branch}) = (DIRECT (PARRAY n_{child}))', f'n_{parent} =/= n_{child}']
    for node in chain:
        checks += [f'n_pool_{node} = $heap_count(HARRAY n_{node}, $pools_nodes(S.POOLS))',
                   f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_{node}) = $({1 if node == "root" else 2} + n_pool_{node})',
                   f'$heap_count(HARRAY n_{node}, $tasks_nodes(S.TODO)) = 1']
    if pooled:
        checks += [
            '$(n_pool_root > 0)', '$compiled_read(S, porigin_rhs) = (PARRAY n_root)',
            '~$list_missing_nested_operand_source(S, porigin_root, n_inner)',
            '~$list_missing_nested_operand_source(S[.POOLS = eps], porigin_root, n_root)',
            '$compiled_read(S, porigin_assign) = (PARRAY n_result)',
            '$compiled_effects(S, porigin_assign) =/= eps', '$literal_result_tasks(S.TODO)',
            '$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 5)',
        ]
    else:
        checks += [
            '$compiled_read(S, porigin_rhs) = eps', 'porigin_rhs = PORIGIN n_unit_rhs pcpath_rhs',
            '$code_at(S.CODE, n_unit_rhs) = (pcode_rhs)',
            '$code_expression(pcode_rhs.EXPRESSIONS, pcpath_rhs) = ((z_rhs, false))', '~$array_immutable(S, n_root)',
            '~$literal_result_tasks(S.TODO)', '$lookup(S.ENV, $ptascii("q")) = (n_q)',
            'S.STORE[n_q] = DEFINED (PINT 2)', '$entry_lookup(S.ARRAYS[n_inner].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        ] + [f'n_pool_{node} = 0' for node in chain]
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT =/= eps', 'S_entered.FRAMES = pframe :: eps',
    ]
    checks += [f'$heap_count(HARRAY n_{node}, $tasks_nodes(pframe.TODO)) = 1' for node in chain]
    checks += ['$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))']
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_pending_found = $list_warning_seek(S_entered, 6, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '~$literal_result_tasks(S_pending.TODO)', 'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            '$throwable_previous_id(S_pending, n_second) = eps',
        ]
        for node in chain:
            checks += [f'$heap_count(HARRAY n_{node}, $tasks_nodes(S_pending.TODO)) = 0',
                       f'$heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_{node}) = $({0 if node == "root" else 1} + n_pool_{node})']
        checks += ['$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
                   'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_x] = DEFINED (PINT 99)',
                   'S_done.STORE[n_y] = DEFINED (PINT 8)', 'S_done.STORE[n_dest] = DEFINED (PINT 100)']
        for name, value in [('outerbefore', 9), ('midbefore', 7), ('before', 5), ('near', 50), ('middle', 60), ('tail', 70)]:
            checks += [f'$lookup(S_done.ENV, $ptascii("{name}")) = (n_{name})', f'S_done.STORE[n_{name}] = DEFINED (PINT {value})']
    else:
        fetched = 6 if pooled else 2
        checks += [
            'S_return_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + marker + ') :: ptask_tail*',
            '$list_missing_source(S_return, ' + args + ')', 'S_return.ERRORHANDLER = S.ERRORHANDLER',
            'S_return.STORE[n_x] = DEFINED (PINT 99)',
            '$list_missing_nested_operand_source(S_return, porigin_root, n_root)',
        ]
        if not pooled:
            checks += ['$lookup(S_return.ENV, $ptascii("other")) = (n_other)',
                       '$lookup(S_return.ENV, $ptascii("q")) = (n_other)', 'n_other =/= n_q',
                       'S_return.STORE[n_other] = DEFINED (PINT 44)', 'S_return.STORE[n_q] = DEFINED (PINT 2)',
                       '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1']
        checks += [
            'PhpStep: S_return ~> S_store',
            f'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_inner), {index}, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS',
            'S_next_found = $list_warning_seek(S_store, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET', 'S_next = S_next_found[.COMPLETION = NORMAL]',
            f'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) {index + 1} expression_next false phpType13_next* z_next) :: ptask_next*',
            'S_next.STORE[n_x] = DEFINED PNULL', 'PhpStep: S_next ~> S_read',
            f'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT {fetched})) false z_y)) :: (LIST_NEXT (KNOWN (PARRAY n_inner)) {index + 2} phpType13_next* z_follow) :: ptask_next*',
            'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS',
            'S_done = $drive_steps(S_read, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL', f'S_done.STORE[n_y] = DEFINED (PINT {fetched})',
            '$lookup(S_done.ENV, $ptascii("dest")) = eps',
        ]
        for name, value in [('near', 7 if pooled else 3), ('tail', 8 if pooled else 4)]:
            checks += [f'$lookup(S_done.ENV, $ptascii("{name}")) = (n_{name})', f'S_done.STORE[n_{name}] = DEFINED (PINT {value})']
        if pooled:
            checks += ['S_done.STORE[n_before] = DEFINED (PINT 21)', '$lookup(S_done.ENV, $ptascii("nil")) = (n_nil)',
                       'S_done.STORE[n_nil] = DEFINED PNULL', '$lookup(S_done.ENV, $ptascii("calls")) = (n_calls)',
                       'S_done.STORE[n_calls] = DEFINED (PINT 1)']
        else:
            checks += ['~((HCELL n_q) <- S_done.ALLOCATIONS)'] + [f'~((HARRAY n_{node}) <- S_done.ALLOCATIONS)' for node in chain]
    if pooled:
        for node in chain:
            checks += [f'(HARRAY n_{node}) <- S_done.ALLOCATIONS', f'S_done.ARRAYS[n_{node}].ITEMS = S.ARRAYS[n_{node}].ITEMS',
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
