#!/usr/bin/env python3
"""Reached literal root certificates, NULL descent and detached row results."""
import base64
import hashlib
import json
from pathlib import Path

import list_literal_cv_missing_warning_review_cases as cases
import list_recursive_literal_missing_warning_protocol as literal
import list_missing_warning_protocol as shared

HELPERS = literal.HELPERS + r'''
def $list_warning_frontier(S, 9) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression false phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 10) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 1 expression false phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (LIST_FETCH (KNOWN (PARRAY n)) 1 expression false eps z) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))
  -- if $origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)
def $list_warning_frontier(S, 12) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $lookup(S.ENV, $ptascii("dest")) = (n_dest)
  -- if S.STORE[n_dest] = DEFINED (PARRAY n_result)
'''


def conditions(name, program, path, stdout):
    pooled = name.endswith('pooled-null-key-retire')
    line, key_name = (16, 'outer') if pooled else (21, 'key')
    args = 'KNOWN (PARRAY n_source), 0, expression, phpType13*, z, KINT 0'
    marker = 'LIST_MISSING_RESULT (KNOWN (PARRAY n_source)) 0 expression phpType13* z (KINT 0)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        'S_entry.TODO = (LIST_FETCH (KNOWN (PARRAY n_source)) 0 expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S_entry.ORIGIN = (porigin)',
        f'S_entry.RESULT = VARIABLE ($ptascii("{key_name}")) z',
        '$list_missing_recursive_cv_context(S_entry, porigin) = (z_initial)',
        '$list_missing_recursive_cv_item(S_entry, porigin, 0, expression, phpType13*, z) = (S_entry.RESULT)',
        '$list_missing_plan(S_entry) = ((KNOWN (PARRAY n_source), 0, expression, phpType13*, z, KINT 0))',
        '$list_missing_source(S_entry, ' + args + ')',
        '~$list_missing_source(S_entry, KNOWN PNULL, 0, expression, phpType13*, z, KINT 0)',
        '~$list_missing_source(S_entry, KNOWN (PARRAY n_source), 0, expression, phpType13*, $(z + 1), KINT 0)',
        '~$list_missing_source(S_entry, KNOWN (PARRAY n_source), 0, expression, eps, z, KINT 0)',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        f'$lookup(S_entry.ENV, $ptascii("{key_name}")) = (n_key_cell)',
        'S_entry.STORE[n_key_cell] = DEFINED (PBOOL false)',
        '$list_missing_plan(S_entry[.RESULT = KNOWN (PBOOL false)]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'S_entry.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)', 'S_entry.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S_entry.ENV, $ptascii("tail")) = (n_tail)', 'S_entry.STORE[n_tail] = DEFINED (PINT 9)',
    ]
    if pooled:
        checks += [
            'n_root = n_source', 'porigin_root = porigin',
            '$lookup(S_entry.ENV, $ptascii("outer_alias")) = (n_key_cell)',
            '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S_entry.ENV, $ptascii("middle")) = (n_middle_cell)',
        ]
    else:
        checks += [
            '$literal_outer_array(S_entry.TODO, 1) = (n_root)',
            '$reference_origin_parent(porigin, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)', 'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
            '$lookup(S_entry.ENV, $ptascii("outer")) = (n_outer_cell)',
            '$lookup(S_entry.ENV, $ptascii("outer_alias")) = (n_outer_cell)',
            '$lookup(S_entry.ENV, $ptascii("outer_replacement")) = (n_outer_replacement)',
            '$lookup(S_entry.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$lookup(S_entry.ENV, $ptascii("key_replacement")) = (n_replacement)',
            '$lookup(S_entry.ENV, $ptascii("next")) = (n_next_cell)',
            '$lookup(S_entry.ENV, $ptascii("row")) = (n_row_cell)',
            '$lookup(S_entry.ENV, $ptascii("row_replacement")) = (n_row_replacement)',
            '$entry_lookup(S_entry.ARRAYS[n_root].ITEMS, KINT 0) = (ALIAS n_row_cell)',
            'S_entry.STORE[n_row_cell] = DEFINED (PARRAY n_source)',
            '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)', 'S_entry.STORE[n_q] = DEFINED (PINT 2)',
            '$entry_lookup(S_entry.ARRAYS[n_source].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_source) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_row_cell) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_outer_cell) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
        ]
    checks += [
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_key_cell) = 2',
        '$origin_node(S_entry.SOURCES, porigin_root) = (expression_root)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S_entry.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        'expression_rhs = NExprArray (SEQUENCE phpType13_rhs*) metadata_rhs',
        '$origin_child((porigin_assign), [PCFIELD 1]) = (porigin_rhs)',
        '$origin_node(S_entry.SOURCES, porigin_rhs) = (expression_rhs)',
        '$list_missing_cv_rhs_source(S_entry, porigin_rhs, expression_rhs, false)',
        '~$list_missing_cv_rhs_source(S_entry, porigin_rhs, expression_rhs, true)',
        '$list_missing_recursive_cv_operand_source(S_entry, porigin_root, KNOWN (PARRAY n_root))',
        '$list_missing_recursive_cv_operand_source(S_entry, porigin, KNOWN (PARRAY n_source))',
        'porigin_rhs = PORIGIN n_unit pcpath_rhs', '$code_at(S_entry.CODE, n_unit) = (pcode)',
        'S_entry.SOURCES[n_unit] = pcunit',
        'S_bad_rhs = S_entry[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_rhs (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]',
        '$list_missing_recursive_cv_context(S_bad_rhs, porigin) = eps',
        '~$list_missing_source(S_bad_rhs, ' + args + ')',
        '$task_nodes(' + marker + ') = [HARRAY n_source]',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if pooled:
        checks += [
            '$compiled_read(S_entry, porigin_rhs) = (PARRAY n_root)',
            '$code_expression(pcode.EXPRESSIONS, pcpath_rhs) = ((z_rhs, true))',
            '~$list_missing_rhs(S_entry, porigin_rhs, expression_rhs, $(n_root + 1))',
            '~$list_missing_source(S_entry[.POOLS = eps], ' + args + ')',
            'n_pool = $heap_count(HARRAY n_root, $pools_nodes(S_entry.POOLS))', '$(n_pool > 0)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_root) = $(1 + n_pool)',
            '$literal_result_tasks(S_entry.TODO)', '$compiled_effects(S_entry, porigin_assign) =/= eps',
        ]
    else:
        checks += [
            '$compiled_read(S_entry, porigin_rhs) = eps', '$compiled_read(S_entry, porigin_assign) = eps',
            '$code_expression(pcode.EXPRESSIONS, pcpath_rhs) = ((z_rhs, false))',
            '~$array_immutable(S_entry, n_root)', '~$literal_result_tasks(S_entry.TODO)',
            '$heap_count(HARRAY n_root, $pools_nodes(S_entry.POOLS)) = 0',
            '$heap_count(HARRAY n_source, $pools_nodes(S_entry.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_root) = 1',
        ]
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
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
        'S_resume.ERRORHANDLER = S_entry.ERRORHANDLER',
        '$list_missing_source(S_resume, ' + args + ')',
        '$list_missing_recursive_cv_context(S_resume, porigin) = (z_initial)',
        '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
        '$lookup(S_resume.ENV, $ptascii("outer_alias")) = eps',
        '$lookup(S_resume.ENV, $ptascii("outer")) = (n_replacement)' if pooled else '$lookup(S_resume.ENV, $ptascii("key")) = (n_replacement)',
        'S_resume.STORE[n_x] = DEFINED (PINT 99)',
    ]
    if pooled:
        checks += [
            'S_resume.STORE[n_y] = DEFINED (PINT 88)',
            'S_resume.STORE[n_middle_cell] = DEFINED (PFLOAT 4612811918334230528)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_root) = $(1 + n_pool)',
        ]
    else:
        checks += [
            '~((HCELL n_outer_cell) <- S_resume.ALLOCATIONS)',
            '$lookup(S_resume.ENV, $ptascii("outer")) = (n_outer_replacement)',
            '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
            'S_resume.STORE[n_replacement] = DEFINED pvalue_new_key', '$string_bytes(pvalue_new_key) = ($ptascii("new"))',
            'S_resume.STORE[n_next_cell] = DEFINED (PINT 1)',
            '$lookup(S_resume.ENV, $ptascii("row")) = (n_row_replacement)',
            'n_row_cell =/= n_row_replacement',
            'S_resume.STORE[n_row_cell] = DEFINED (PARRAY n_saved_row)',
            'S_resume.STORE[n_row_replacement] = DEFINED (PARRAY n_live_row)', 'n_saved_row =/= n_live_row',
            '$entry_lookup(S_resume.ARRAYS[n_saved_row].ITEMS, KINT 1) = (DIRECT (PINT 66))',
            '$entry_lookup(S_resume.ARRAYS[n_live_row].ITEMS, KINT 1) = (DIRECT (PINT 99))',
            '$entry_lookup(S_resume.ARRAYS[n_root].ITEMS, KINT 0) = (ALIAS n_row_cell)',
            '$lookup(S_resume.ENV, $ptascii("q")) = eps', 'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_root) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_row_cell) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
        ]
    checks += [
        'PhpStep: S_resume ~> S_schedule', 'S_schedule.RESULT = KNOWN PNULL',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
    ]
    if pooled:
        prior = 'S_schedule'
        for level in range(1, 4):
            state, read = f'S_null{level}', f'S_read{level}'
            checks += [
                f'{state}_found = $list_warning_seek({prior}, 9, 2000)',
                rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
                f'{state} = {state}_found[.COMPLETION = NORMAL]',
                f'{state}.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression_{level} false phpType13_{level}* z_{level}) :: ptask_{level}*',
                f'$list_missing_plan({state}) = eps',
                f'PhpStep: {state} ~> {read}', f'{read}.STORE = {state}.STORE', f'{read}.EVENTS = {state}.EVENTS',
                f'{read}_driven_found = $drive_steps({state}, 1)', f'{read}_driven_found.COMPLETION = BUDGET',
                f'{read}_driven = {read}_driven_found[.COMPLETION = NORMAL]',
                f'{read}_driven.TODO = {read}.TODO',
            ]
            prior = read + '_driven'
        checks += [
            'S_ynext_found = $list_warning_seek(S_read3_driven, 10, 2000)',
            r'S_ynext_found.COMPLETION = NORMAL \/ S_ynext_found.COMPLETION = BUDGET',
            'S_ynext = S_ynext_found[.COMPLETION = NORMAL]',
            'S_ynext.STORE[n_x] = DEFINED PNULL', 'S_ynext.STORE[n_y] = DEFINED (PINT 88)',
            'PhpStep: S_ynext ~> S_yread', 'S_yread.RESULT = KNOWN PNULL', 'S_yread.EVENTS = S_ynext.EVENTS',
            'S_done = $drive_steps(S_ynext, 2000)', 'S_done.STORE[n_y] = DEFINED PNULL',
            'S_done.STORE[n_tail] = DEFINED (PINT 3)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_root) = n_pool',
            '(HARRAY n_root) <- S_done.ALLOCATIONS', '~((HCELL n_replacement) <- S_done.ALLOCATIONS)',
        ]
    else:
        checks += [
            'S_next_found = $list_warning_seek(S_schedule, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_source)) 1 expression_next false eps z_next) :: ptask_next*',
            'z_next = 22', 'S_next.RESULT = VARIABLE ($ptascii("next")) 22',
            'S_next.STORE[n_x] = DEFINED PNULL', 'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT 33)) false z_y)) :: ptask_y*',
            'S_read_driven_found = $drive_steps(S_next, 1)', 'S_read_driven_found.COMPLETION = BUDGET',
            'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]', 'S_read_driven.TODO = S_read.TODO',
            'S_read_driven.STORE = S_read.STORE', 'S_read_driven.ARRAYS = S_read.ARRAYS',
            'S_outer_found = $list_warning_seek(S_read_driven, 11, 2000)',
            r'S_outer_found.COMPLETION = NORMAL \/ S_outer_found.COMPLETION = BUDGET',
            'S_outer = S_outer_found[.COMPLETION = NORMAL]',
            'S_outer.TODO = (LIST_FETCH (KNOWN (PARRAY n_root)) 1 expression_tail false eps z_tail) :: ptask_outer*',
            'S_outer.STORE[n_y] = DEFINED (PINT 33)',
            '~((HARRAY n_source) <- S_outer.ALLOCATIONS)', '~((HCELL n_q) <- S_outer.ALLOCATIONS)',
            'S_outer.STORE[n_row_cell] = DEFINED (PARRAY n_saved_row)',
            'PhpStep: S_outer ~> S_tail_read',
            'S_tail_read.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 4)) false z_tail_store)) :: ptask_after*',
            'S_delivered_found = $list_warning_seek(S_outer, 12, 2000)',
            r'S_delivered_found.COMPLETION = NORMAL \/ S_delivered_found.COMPLETION = BUDGET',
            'S_delivered = S_delivered_found[.COMPLETION = NORMAL]',
            'S_delivered.STORE[n_dest] = DEFINED (PARRAY n_root)',
            'S_delivered.STORE[n_row_cell] = DEFINED (PARRAY n_saved_row)',
            '$lookup(S_delivered.ENV, $ptascii("row")) = (n_row_replacement)',
            'S_delivered.STORE[n_row_replacement] = DEFINED (PARRAY n_live_row)',
            'S_done = $drive_steps(S_delivered, 2000)', 'S_done.STORE[n_y] = DEFINED (PINT 55)',
            '~((HARRAY n_root) <- S_done.ALLOCATIONS)', '~((HCELL n_row_cell) <- S_done.ALLOCATIONS)',
            '~((HCELL n_row_replacement) <- S_done.ALLOCATIONS)',
        ]
    return checks + [
        'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
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
