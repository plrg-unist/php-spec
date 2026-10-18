#!/usr/bin/env python3
"""Reached dynamic ancestors, detached child tables and reference COW."""
import base64
import hashlib
import json
from pathlib import Path

import list_recursive_cv_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 8) = true
  -- if S.TODO = (LIST_FETCH (KNOWN (PARRAY n_root)) 1 expression false eps z) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))
  -- if $origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)
'''


def conditions(name, program, path, stdout):
    detached = name.endswith('detached-child-key-retire')
    index, line = (0, 19) if detached else (1, 16)
    operand = 'KNOWN (PARRAY n_child)' if detached else 'REFERENCE n_child_cell'
    key = 'KINT 0' if detached else 'KINT 1'
    target, later = ('x', 'y') if detached else ('missing', 'late')
    marker = f'LIST_MISSING_RESULT ({operand}) {index} expression phpType13* z ({key})'
    args = f'({operand}), {index}, expression, phpType13*, z, {key}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        f'S_entry.TODO = (LIST_FETCH ({operand}) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S_entry.ORIGIN = (porigin)',
        '$list_missing_nested_context(S_entry, porigin) = eps',
        '$list_missing_recursive_cv_context(S_entry, porigin) = (z_initial)',
        '$origin_node(S_entry.SOURCES, porigin) = (expression_pattern)',
        '$list_pattern(expression_pattern) = (phpType13_all*)',
        f'$list_missing_recursive_cv_item_line(S_entry, porigin, phpType13_all*, {index}, z_initial) = ((expression, phpType13*, z))',
        f'$list_missing_plan(S_entry) = ((({operand}), {index}, expression, phpType13*, z, {key}))',
        '$list_missing_pending(S_entry)', '$list_missing_source(S_entry, ' + args + ')',
        f'~$list_missing_source(S_entry, KNOWN PNULL, {index}, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S_entry, ({operand}), {index}, expression, phpType13*, $(z + 1), {key})',
        f'~$list_missing_source(S_entry, ({operand}), {index + 1}, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S_entry, ({operand}), {index}, expression, eps, z, {key})',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        'S_entry.STORE[n_a] = DEFINED (PARRAY n_root)',
        f'$lookup(S_entry.ENV, $ptascii("{target}")) = (n_target)',
        f'$lookup(S_entry.ENV, $ptascii("{later}")) = (n_later)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)',
        'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S_entry.ENV, $ptascii("outer")) = (n_outer_cell)',
        '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)',
        'S_entry.STORE[n_q] = DEFINED (PINT 2)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if detached:
        checks += [
            'z_initial = 18', 'S_entry.RESULT = VARIABLE ($ptascii("key")) 19',
            '$list_missing_recursive_cv_item(S_entry, porigin, 0, expression, phpType13*, z) = (S_entry.RESULT)',
            '$list_missing_integer_cv_item(S_entry, 0, expression, phpType13*, z) = (S_entry.RESULT)',
            '$reference_origin_parent(porigin, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$lookup(S_entry.ENV, $ptascii("key")) = (n_key_cell)',
            'S_entry.STORE[n_key_cell] = DEFINED (PBOOL false)',
            '$lookup(S_entry.ENV, $ptascii("next")) = (n_next_cell)',
            '$lookup(S_entry.ENV, $ptascii("outer_alias")) = (n_outer_cell)',
            '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S_entry.ENV, $ptascii("row")) = (n_row_cell)',
            '$entry_lookup(S_entry.ARRAYS[n_root].ITEMS, KINT 0) = (ALIAS n_row_cell)',
            'S_entry.STORE[n_row_cell] = DEFINED (PARRAY n_child)',
            '$entry_lookup(S_entry.ARRAYS[n_child].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_outer_cell) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_root) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_child) = 2',
            '$task_nodes(' + marker + ') = [HARRAY n_child]',
            '$list_missing_plan(S_entry[.RESULT = KNOWN (PBOOL false)]) = eps',
            '$list_missing_plan(S_entry[.RESULT = VARIABLE ($ptascii("next")) 19]) = eps',
            '$list_missing_plan(S_entry[.STORE[n_key_cell] = UNDEFINED]) = eps',
            '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
            '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        ]
    else:
        checks += [
            'z_initial = 16', 'S_entry.RESULT = KNOWN (PINT 1)',
            '$list_missing_recursive_cv_item(S_entry, porigin, 1, expression, phpType13*, z) = eps',
            '$list_missing_plan(S_entry[.RESULT = KNOWN (PINT 9)]) = eps',
            '~$list_missing_source(S_entry, REFERENCE n_child_cell, 1, expression, phpType13*, z, KINT 9)',
            '$reference_origin_parent(porigin, 6) = ((porigin_root, [PCFIELD 0, PCINDEX 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$lookup(S_entry.ENV, $ptascii("middle")) = (n_middle_cell)',
            '$lookup(S_entry.ENV, $ptascii("copy")) = (n_copy)',
            'S_entry.STORE[n_copy] = DEFINED (PARRAY n_copy_root)',
            '$entry_lookup(S_entry.ARRAYS[n_root].ITEMS, KSTRING ($ptascii("branch"))) = (ALIAS n_mid_cell)',
            'S_entry.STORE[n_mid_cell] = DEFINED (PARRAY n_mid)',
            '$entry_lookup(S_entry.ARRAYS[n_mid].ITEMS, KSTRING ($ptascii("deep"))) = (ALIAS n_child_cell)',
            'S_entry.STORE[n_child_cell] = DEFINED (PARRAY n_child)',
            '$entry_lookup(S_entry.ARRAYS[n_copy_root].ITEMS, KSTRING ($ptascii("branch"))) = (DIRECT (PARRAY n_copy_mid))',
            '$entry_lookup(S_entry.ARRAYS[n_copy_mid].ITEMS, KSTRING ($ptascii("deep"))) = (DIRECT (PARRAY n_copy_child))',
            'n_root =/= n_copy_root', 'n_mid =/= n_copy_mid', 'n_child =/= n_copy_child',
            '$lookup(S_entry.ENV, $ptascii("early")) = (n_early)',
            'S_entry.STORE[n_early] = DEFINED (PINT 5)',
            '$entry_lookup(S_entry.ARRAYS[n_child].ITEMS, KINT 0) = (ALIAS n_early)',
            '$entry_lookup(S_entry.ARRAYS[n_copy_child].ITEMS, KINT 0) = (DIRECT (PINT 5))',
            '$entry_lookup(S_entry.ARRAYS[n_child].ITEMS, KINT 2) = (ALIAS n_q)',
            '$entry_lookup(S_entry.ARRAYS[n_copy_child].ITEMS, KINT 2) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 3',
            '$task_nodes(' + marker + ') = [HCELL n_child_cell]',
        ]
    checks += [
        '$origin_node(S_entry.SOURCES, porigin_root) = (expression_root)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S_entry.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S_entry.SOURCES[n_unit] = pcunit',
        'S_literal = S_entry[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NExprArray (SEQUENCE eps) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_recursive_cv_context(S_literal, porigin) = eps',
        '~$list_missing_source(S_literal, ' + args + ')',
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        f'perrorcall.MESSAGE = $list_missing_message({key})',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S_entry.STORE', 'S_dispatch.ARRAYS = S_entry.ARRAYS',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]',
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_rest*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_resume_found = $list_warning_seek(S_entered, 2, 2000)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.CURRENT = eps', 'S_resume.FRAMES = eps',
        'S_resume.ERRORHANDLER = S_entry.ERRORHANDLER',
        '$list_missing_recursive_cv_context(S_resume, porigin) = (z_initial)',
        '$list_missing_source(S_resume, ' + args + ')',
        'S_resume.STORE[n_target] = DEFINED (PINT 99)',
    ]
    if detached:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("outer")) = (n_replacement)',
            '$lookup(S_resume.ENV, $ptascii("outer_alias")) = eps',
            'n_outer_cell =/= n_replacement', '~((HCELL n_outer_cell) <- S_resume.ALLOCATIONS)',
            'S_resume.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)',
            'S_resume.STORE[n_next_cell] = DEFINED (PINT 1)',
            'S_resume.STORE[n_row_cell] = DEFINED (PARRAY n_new_row)', 'n_new_row =/= n_child',
            '$entry_lookup(S_resume.ARRAYS[n_new_row].ITEMS, KINT 1) = (DIRECT (PINT 66))',
            'S_resume.STORE[n_a] = DEFINED (PARRAY n_live)', 'n_live =/= n_root',
            '$lookup(S_resume.ENV, $ptascii("q")) = eps',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_root) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_child) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
        ]
    else:
        checks += [
            'S_resume.STORE[n_outer_cell] = DEFINED pvalue_outer', '$string_bytes(pvalue_outer) = ($ptascii("gone"))',
            'S_resume.STORE[n_middle_cell] = DEFINED pvalue_middle', '$string_bytes(pvalue_middle) = ($ptascii("gone"))',
            'S_resume.STORE[n_child_cell] = DEFINED (PARRAY n_child)',
            'S_resume.STORE[n_early] = DEFINED (PINT 21)',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            '$entry_lookup(S_resume.ARRAYS[n_child].ITEMS, KINT 1) = (DIRECT (PINT 77))',
            '$entry_lookup(S_resume.ARRAYS[n_copy_child].ITEMS, KINT 1) = eps',
            '$entry_lookup(S_resume.ARRAYS[n_copy_child].ITEMS, KINT 0) = (DIRECT (PINT 5))',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
        ]
    checks += [
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'PhpStep: S_resume ~> S_schedule', 'S_schedule.RESULT = KNOWN PNULL',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
        f'S_next_found = $list_warning_seek(S_schedule, {4 if detached else 6}, 2000)',
        r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
        'S_next = S_next_found[.COMPLETION = NORMAL]', 'S_next.STORE[n_target] = DEFINED PNULL',
    ]
    if detached:
        checks += [
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_child)) 1 expression_next false eps z_next) :: ptask_next*',
            'z_next = 20', 'S_next.RESULT = VARIABLE ($ptascii("next")) 20',
            '$list_missing_plan(S_next) = eps', 'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_later (LIST_STORE expression_next (KNOWN (PINT 33)) false z_later)) :: (LIST_NEXT (KNOWN (PARRAY n_child)) 2 eps z_end) :: ptask_next*',
        ]
    else:
        checks += [
            'S_next.TODO = (LIST_FETCH (REFERENCE n_child_cell) 2 expression_next true eps z_next) :: ptask_next*',
            'z_next = 18', 'S_next.RESULT = KNOWN (PINT 2)', 'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_later (LIST_STORE expression_next (REFERENCE n_q) true z_later)) :: (LIST_NEXT (REFERENCE n_child_cell) 3 eps z_end) :: ptask_next*',
            '$heap_owners($heap_prune($heap_graph(S_read)), HCELL n_q) = 4',
        ]
    checks += [
        'S_read_driven_found = $drive_steps(S_next, 1)', 'S_read_driven_found.COMPLETION = BUDGET',
        'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]',
        'S_read_driven.STORE = S_read.STORE', 'S_read_driven.ARRAYS = S_read.ARRAYS',
        'S_read_driven.TODO = S_read.TODO', 'S_read_driven.RESULT = S_read.RESULT',
    ]
    if detached:
        checks += [
            'S_outer_found = $list_warning_seek(S_read_driven, 8, 2000)',
            r'S_outer_found.COMPLETION = NORMAL \/ S_outer_found.COMPLETION = BUDGET',
            'S_outer = S_outer_found[.COMPLETION = NORMAL]',
            'S_outer.TODO = (LIST_FETCH (KNOWN (PARRAY n_root)) 1 expression_tail false eps z_tail) :: ptask_outer*',
            'S_outer.STORE[n_later] = DEFINED (PINT 33)',
            '~((HARRAY n_child) <- S_outer.ALLOCATIONS)', '~((HCELL n_q) <- S_outer.ALLOCATIONS)',
            'S_outer.STORE[n_row_cell] = DEFINED (PARRAY n_new_row)',
            '$heap_owners($heap_prune($heap_graph(S_outer)), HARRAY n_root) = 1',
            'PhpStep: S_outer ~> S_tail_read',
            'S_tail_read.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 4)) false z_tail_store)) :: (LIST_NEXT (KNOWN (PARRAY n_root)) 2 eps z_tail_end) :: ptask_outer*',
            'S_done = $drive_steps(S_tail_read, 2000)', 'S_done.STORE[n_later] = DEFINED (PINT 55)',
            '~((HCELL n_row_cell) <- S_done.ALLOCATIONS)', '~((HCELL n_replacement) <- S_done.ALLOCATIONS)',
        ]
    else:
        checks += [
            'S_target_found = $drive_steps(S_read_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
            'S_target = S_target_found[.COMPLETION = NORMAL]',
            'S_target.TODO = (LIST_STORE expression_next (REFERENCE n_q) true z_later) :: ptask_after*',
            'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("late")) = (n_q)',
            '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_later) = 0',
            '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_q) = 4',
            'S_bound_found = $drive_steps(S_target, 1)', 'S_bound_found.COMPLETION = BUDGET',
            'S_bound = S_bound_found[.COMPLETION = NORMAL]', '~((HCELL n_later) <- S_bound.ALLOCATIONS)',
            'S_done = $drive_steps(S_bound, 2000)',
        ]
        for cell in ('n_a', 'n_mid_cell', 'n_child_cell', 'n_early', 'n_q'):
            checks += [f'~((HCELL {cell}) <- S_done.ALLOCATIONS)']
        for array in ('n_mid', 'n_child', 'n_copy_root', 'n_copy_mid', 'n_copy_child'):
            checks += [f'~((HARRAY {array}) <- S_done.ALLOCATIONS)']
    return checks + [
        'S_done.STORE[n_target] = DEFINED PNULL', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HARRAY n_root) <- S_done.ALLOCATIONS)', '$lookup(S_done.ENV, $ptascii("dest")) = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
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
