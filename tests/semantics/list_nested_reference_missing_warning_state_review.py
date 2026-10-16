#!/usr/bin/env python3
"""Detached child CELL authority, nested COW and inherited reference lines."""
import base64
import hashlib
import json
from pathlib import Path

import list_nested_reference_missing_warning_review_cases as cases
import list_nested_reference_missing_warning_protocol as author
import list_missing_warning_protocol as shared

HELPERS = author.HELPERS + r'''
def $list_warning_frontier(S, 9) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n) 1 expression false eps z) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))
  -- if $origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)
'''


def conditions(name, program, path, stdout):
    detached = name.endswith('detached-child-rebind')
    index, line = (0, 18) if detached else (1, 22)
    target, reference = ('x', 'y') if detached else ('missing', 'late')
    initial_target, initial_reference = (7, 8) if detached else (12, 13)
    marker = f'LIST_MISSING_RESULT (REFERENCE n_source) {index} expression phpType13* z (KINT {index})'
    args = f'REFERENCE n_source, {index}, expression, phpType13*, z, KINT {index}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        f'S_entry.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'S_entry.RESULT = KNOWN (PINT {index})', 'S_entry.ORIGIN = (porigin)',
        'S_entry.STORE[n_source] = DEFINED (PARRAY n_before)', 'n_source <- S_entry.REFCELLS',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_root_cell)', 'n_source =/= n_root_cell',
        'S_entry.STORE[n_root_cell] = DEFINED (PARRAY n_root)', 'n_root_cell <- S_entry.REFCELLS',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)', 'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)', 'S_entry.STORE[n_q] = DEFINED (PINT 2)',
        f'$lookup(S_entry.ENV, $ptascii("{target}")) = (n_target)', f'S_entry.STORE[n_target] = DEFINED (PINT {initial_target})',
        f'$lookup(S_entry.ENV, $ptascii("{reference}")) = (n_old_reference)', f'S_entry.STORE[n_old_reference] = DEFINED (PINT {initial_reference})',
        f'$entry_lookup(S_entry.ARRAYS[n_before].ITEMS, KINT {index}) = eps',
        f'$entry_lookup(S_entry.ARRAYS[n_before].ITEMS, KINT {index + 1}) = (ALIAS n_q)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_source) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_root_cell) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_before) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_root) = 1',
        '$heap_count(HARRAY n_before, $pools_nodes(S_entry.POOLS)) = 0',
        '$heap_count(HCELL n_source, $tasks_nodes(S_entry.TODO)) = 1',
        '$heap_count(HCELL n_root_cell, $tasks_nodes(S_entry.TODO)) = 1',
        '$task_nodes(' + marker + ') = [HCELL n_source]',
        '$list_missing_source(S_entry, ' + args + ')',
        f'~$list_missing_source(S_entry, KNOWN (PARRAY n_before), {index}, expression, phpType13*, z, KINT {index})',
        f'~$list_missing_source(S_entry, REFERENCE n_source, {index}, expression, phpType13*, $(z + 1), KINT {index})',
        f'~$list_missing_source(S_entry, REFERENCE n_source, {index}, expression, eps, z, KINT {index})',
        f'~$list_missing_source(S_entry, REFERENCE n_source, {index}, expression, phpType13*, z, KINT 9)',
        f'~$list_missing_source(S_entry, REFERENCE (|S_entry.STORE|), {index}, expression, phpType13*, z, KINT {index})',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.REFCELLS = eps], ' + args + ')',
        '$list_missing_plan(S_entry[.RESULT = KNOWN (PINT 9)]) = eps',
    ]
    if detached:
        checks += [
            '$reference_origin_parent(porigin, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$entry_lookup(S_entry.ARRAYS[n_root].ITEMS, KINT 0) = (ALIAS n_source)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
            '$lookup(S_entry.ENV, $ptascii("tail")) = (n_tail)', 'S_entry.STORE[n_tail] = DEFINED (PINT 9)',
        ]
    else:
        checks += [
            '$reference_origin_parent(porigin, 3) = ((porigin_mid, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$reference_origin_parent(porigin_mid, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$entry_lookup(S_entry.ARRAYS[n_root].ITEMS, KINT 0) = (ALIAS n_mid_cell)',
            'S_entry.STORE[n_mid_cell] = DEFINED (PARRAY n_mid)', 'n_mid_cell <- S_entry.REFCELLS',
            '$entry_lookup(S_entry.ARRAYS[n_mid].ITEMS, KINT 0) = (ALIAS n_source)',
            '$lookup(S_entry.ENV, $ptascii("copy")) = (n_copy)', 'S_entry.STORE[n_copy] = DEFINED (PARRAY n_copy_root)',
            '$entry_lookup(S_entry.ARRAYS[n_copy_root].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_mid))',
            '$entry_lookup(S_entry.ARRAYS[n_copy_mid].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_inner))',
            '$entry_lookup(S_entry.ARRAYS[n_copy_inner].ITEMS, KINT 0) = (DIRECT (PINT 5))',
            '$entry_lookup(S_entry.ARRAYS[n_copy_inner].ITEMS, KINT 2) = (ALIAS n_q)',
            'n_root =/= n_copy_root', 'n_mid =/= n_copy_mid', 'n_before =/= n_copy_inner',
            '$lookup(S_entry.ENV, $ptascii("early")) = (n_early)', 'S_entry.STORE[n_early] = DEFINED (PINT 5)',
            '$entry_lookup(S_entry.ARRAYS[n_before].ITEMS, KINT 0) = (ALIAS n_early)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_early) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 3',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_mid_cell) = 2',
            '$heap_count(HCELL n_mid_cell, $tasks_nodes(S_entry.TODO)) = 1',
        ]
        for array in ('n_mid', 'n_copy_root', 'n_copy_mid', 'n_copy_inner'):
            checks += [f'$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY {array}) = 1']
    checks += [
        '$origin_node(S_entry.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        '$list_references(phpType13_all*)', '$list_missing_nested_mixed_items(phpType13_all*)',
        '~$list_missing_nested_items(phpType13_all*)',
        '$list_missing_nested_context(S_entry, porigin) = (z_initial)', 'z = z_initial',
        '$origin_node(S_entry.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
        '~$list_missing_flat(phpType13_root*)', '$list_references(phpType13_root*)',
        '$list_missing_nested_mixed_items(phpType13_root*)', '~$list_missing_nested_items(phpType13_root*)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S_entry.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        '$list_value_cv(expression_rhs) = ($ptascii("a"))',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S_entry.SOURCES[n_unit] = pcunit',
        'S_literal = S_entry[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NExprArray (SEQUENCE eps) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_nested_context(S_literal, porigin) = eps', '~$list_missing_source(S_literal, ' + args + ')',
        '~$list_missing_nested_mixed_items([NArrayItem ABSENT expression (BOOLEAN false) (BOOLEAN true) metadata_assign])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*', 'perrorcall.RESUME = ' + marker,
        '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_source]',
        'S_dispatch.STORE = S_entry.STORE', 'S_dispatch.ARRAYS = S_entry.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT =/= eps',
        'S_entered.ERRORHANDLER.CALLBACK = eps', 'S_entered.FRAMES = pframe :: eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_root_cell, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_resume_found = $list_warning_seek(S_entered, 2, 2000)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', 'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.ERRORHANDLER = S_entry.ERRORHANDLER', '$list_missing_source(S_resume, ' + args + ')',
        'S_resume.STORE[n_target] = DEFINED (PINT 99)', 'S_resume.STORE[n_dest] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
    ]
    if detached:
        checks += [
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_replaced)', 'n_replaced =/= n_before',
            '$entry_lookup(S_resume.ARRAYS[n_replaced].ITEMS, KINT 1) = (DIRECT (PINT 22))',
            'S_resume.STORE[n_root_cell] = DEFINED (PARRAY n_saved_root)', 'n_saved_root =/= n_root',
            '$entry_lookup(S_resume.ARRAYS[n_saved_root].ITEMS, KINT 0) = (DIRECT (PARRAY n_saved_row))',
            '$entry_lookup(S_resume.ARRAYS[n_saved_row].ITEMS, KINT 1) = (DIRECT (PINT 66))',
            '$entry_lookup(S_resume.ARRAYS[n_saved_root].ITEMS, KINT 1) = (DIRECT (PINT 44))',
            '$lookup(S_resume.ENV, $ptascii("a")) = (n_live_cell)', 'n_live_cell =/= n_root_cell',
            'S_resume.STORE[n_live_cell] = DEFINED (PARRAY n_live_root)',
            '$entry_lookup(S_resume.ARRAYS[n_live_root].ITEMS, KINT 0) = (DIRECT (PARRAY n_live_row))',
            '$entry_lookup(S_resume.ARRAYS[n_live_row].ITEMS, KINT 1) = (DIRECT (PINT 77))',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_root_cell) = 1',
            '~((HARRAY n_before) <- S_resume.ALLOCATIONS)', '~((HARRAY n_root) <- S_resume.ALLOCATIONS)',
            '~((HCELL n_q) <- S_resume.ALLOCATIONS)', '$lookup(S_resume.ENV, $ptascii("q")) = eps',
        ]
    else:
        checks += [
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_before)',
            'S_resume.STORE[n_early] = DEFINED (PINT 21)', 'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            'S_resume.ARRAYS[n_copy_inner] = S_entry.ARRAYS[n_copy_inner]',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
        ]
    checks += [
        'PhpStep: S_resume ~> S_schedule',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
        f'S_schedule.TODO = (AT porigin_target (LIST_STORE expression (KNOWN PNULL) false z_target)) :: (LIST_NEXT (REFERENCE n_source) {index + 1} phpType13* z_next) :: ptask_tail*',
        'S_next_found = $list_warning_seek(S_schedule, 6, 2000)',
        r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
        'S_next = S_next_found[.COMPLETION = NORMAL]',
        f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) {index + 1} expression_next true eps z_fetch) :: ptask_next*',
        'S_next.STORE[n_target] = DEFINED PNULL', f'S_next.STORE[n_old_reference] = DEFINED (PINT {initial_reference})',
        'PhpStep: S_next ~> S_read',
        f'S_read.TODO = (AT porigin_reference (LIST_STORE expression_next (REFERENCE n_element) true z_reference)) :: (LIST_NEXT (REFERENCE n_source) {index + 2} eps z_after) :: ptask_next*',
        'S_read.STORE[n_source] = DEFINED (PARRAY n_write)',
        f'$entry_lookup(S_read.ARRAYS[n_write].ITEMS, KINT {index + 1}) = (ALIAS n_element)',
        f'S_read.STORE[n_element] = DEFINED (PINT {22 if detached else 33})', 'n_element <- S_read.REFCELLS',
        f'$heap_owners($heap_prune($heap_graph(S_read)), HCELL n_element) = {2 if detached else 4}',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
    ]
    checks += ['n_write =/= n_replaced'] if detached else ['n_write = n_before', 'n_element = n_q']
    checks += [
        'S_target_found = $drive_steps(S_read, 1)', 'S_target_found.COMPLETION = BUDGET',
        'S_target = S_target_found[.COMPLETION = NORMAL]',
        'S_target.TODO = (LIST_STORE expression_next (REFERENCE n_element) true z_reference) :: ptask_after*',
        'PhpStep: S_target ~> S_bound_raw', f'$lookup(S_bound_raw.ENV, $ptascii("{reference}")) = (n_element)',
        '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_old_reference) = 0',
        'S_bound_budget = $drive_steps(S_target, 1)', 'S_bound_budget.COMPLETION = BUDGET',
        'S_bound = S_bound_budget[.COMPLETION = NORMAL]',
        'S_bound.STORE = S_bound_raw.STORE', 'S_bound.ARRAYS = S_bound_raw.ARRAYS',
        '~((HCELL n_old_reference) <- S_bound.ALLOCATIONS)',
        f'$heap_owners($heap_prune($heap_graph(S_bound)), HCELL n_element) = {2 if detached else 4}',
        '$call_descriptors_valid(S_bound)', '$heap_valid($heap_graph(S_bound))',
    ]
    if detached:
        checks += [
            'S_outer_found = $list_warning_seek(S_bound, 9, 2000)',
            r'S_outer_found.COMPLETION = NORMAL \/ S_outer_found.COMPLETION = BUDGET',
            'S_outer = S_outer_found[.COMPLETION = NORMAL]',
            'S_outer.TODO = (LIST_FETCH (REFERENCE n_root_cell) 1 expression_tail false eps z_tail) :: ptask_outer*',
            '~((HCELL n_source) <- S_outer.ALLOCATIONS)', '~((HARRAY n_write) <- S_outer.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_outer)), HCELL n_element) = 1',
            'S_outer.STORE[n_element] = DEFINED (PINT 22)', 'S_outer.STORE[n_tail] = DEFINED (PINT 9)',
            'S_outer.STORE[n_dest] = DEFINED (PINT 100)',
            'PhpStep: S_outer ~> S_tailread',
            'S_tailread.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 44)) false z_tailstore)) :: (LIST_NEXT (REFERENCE n_root_cell) 2 eps z_final) :: ptask_outer*',
            'S_done = $drive_steps(S_tailread, 2000)', 'S_done.STORE[n_tail] = DEFINED (PINT 44)',
            '~((HCELL n_live_cell) <- S_done.ALLOCATIONS)',
        ]
    else:
        checks += ['S_done = $drive_steps(S_bound, 2000)']
        for array in ('n_before', 'n_mid', 'n_root', 'n_copy_inner', 'n_copy_mid', 'n_copy_root'):
            checks += [f'~((HARRAY {array}) <- S_done.ALLOCATIONS)']
        for cell in ('n_mid_cell', 'n_early', 'n_q'):
            checks += [f'~((HCELL {cell}) <- S_done.ALLOCATIONS)']
        checks += ['$lookup(S_done.ENV, $ptascii("copy")) = eps']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_target] = DEFINED PNULL', '~((HCELL n_root_cell) <- S_done.ALLOCATIONS)',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HCELL n_element) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("dest")) = eps', '$lookup(S_done.ENV, $ptascii("a")) = eps',
        'S_done.POOLS = S_entry.POOLS', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_entry, 2000) = S_done', '$drive_steps(S_resume, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
