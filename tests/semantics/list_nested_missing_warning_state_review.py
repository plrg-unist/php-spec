#!/usr/bin/env python3
"""Outer NULL-to-child descent and completed nested-target line/owner order."""
import base64
import hashlib
import json
from pathlib import Path

import list_nested_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression false phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 7) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 1 expression false phpType13* z) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    outer_null = name.endswith('outer-null-child')
    index, line = (0, 12) if outer_null else (1, 13)
    marker = f'LIST_MISSING_RESULT (KNOWN (PARRAY n_outer)) {index} expression phpType13* z (KINT {index})'
    args = f'KNOWN (PARRAY n_outer), {index}, expression, phpType13*, z, KINT {index}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        f'S_entry.TODO = (LIST_FETCH (KNOWN (PARRAY n_outer)) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'S_entry.RESULT = KNOWN (PINT {index})',
        'S_entry.ORIGIN = (porigin)',
        '$origin_node(S_entry.SOURCES, porigin) = (expression_pattern)',
        '$list_pattern(expression_pattern) = (phpType13_all*)',
        '~$list_missing_flat(phpType13_all*)',
        '$list_missing_nested_items(phpType13_all*)', '~$list_references(phpType13_all*)',
        '$list_missing_nested_context(S_entry, porigin) = (z_initial)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S_entry.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata_assign)',
        '$list_value_cv(expression_rhs) = (n_name*)',
        '$list_missing_nested_items([NArrayItem ABSENT expression_pattern (BOOLEAN false) (BOOLEAN false) metadata_assign])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression_rhs (BOOLEAN true) (BOOLEAN false) metadata_assign])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression_rhs (BOOLEAN false) (BOOLEAN true) metadata_assign])',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        'S_entry.STORE[n_a] = DEFINED (PARRAY n_outer)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)',
        'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        '$heap_count(HARRAY n_outer, $pools_nodes(S_entry.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_outer) = 2',
        '$list_missing_source(S_entry, ' + args + ')',
        f'~$list_missing_source(S_entry, KNOWN (PARRAY n_outer), {index}, expression, phpType13*, $(z + 1), KINT {index})',
        f'~$list_missing_source(S_entry, KNOWN (PARRAY n_outer), {index}, expression, eps, z, KINT {index})',
        f'~$list_missing_source(S_entry, KNOWN (PARRAY n_outer), {index}, expression, phpType13*, z, KINT 9)',
        f'~$list_missing_source(S_entry, REFERENCE n_a, {index}, expression, phpType13*, z, KINT {index})',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        '$list_missing_plan(S_entry[.RESULT = KNOWN (PINT 9)]) = eps',
        '$task_nodes(' + marker + ') = [HARRAY n_outer]',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if outer_null:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'S_entry.STORE[n_x] = DEFINED (PINT 7)',
            '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)', 'S_entry.STORE[n_y] = DEFINED (PINT 8)',
            '$lookup(S_entry.ENV, $ptascii("z")) = (n_z)', 'S_entry.STORE[n_z] = DEFINED (PINT 9)',
            '$list_pattern(expression) = (phpType13_child*)',
        ]
    else:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("first")) = (n_first)', 'S_entry.STORE[n_first] = DEFINED (PINT 2)',
            '$lookup(S_entry.ENV, $ptascii("missing")) = (n_missing)', 'S_entry.STORE[n_missing] = DEFINED (PINT 8)',
            '$lookup(S_entry.ENV, $ptascii("last")) = (n_last)', 'S_entry.STORE[n_last] = DEFINED (PINT 9)',
            '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)', 'S_entry.STORE[n_q] = DEFINED (PINT 2)',
            '$entry_lookup(S_entry.ARRAYS[n_outer].ITEMS, KINT 0) = (DIRECT (PARRAY n_child))',
            '$entry_lookup(S_entry.ARRAYS[n_child].ITEMS, KINT 0) = (ALIAS n_q)',
            '$heap_count(HARRAY n_child, $pools_nodes(S_entry.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_child) = 1',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
        ]
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HARRAY n_outer]',
        'S_dispatch.STORE = S_entry.STORE', 'S_dispatch.ARRAYS = S_entry.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]',
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_resume_found = $list_warning_seek(S_entered, 2, 2000)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.ERRORHANDLER = S_entry.ERRORHANDLER',
        '$list_missing_source(S_resume, ' + args + ')',
        'S_resume.STORE[n_a] = DEFINED (PARRAY n_replacement)', 'n_replacement =/= n_outer',
        '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_outer) = 1',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'PhpStep: S_resume ~> S_schedule',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
        'S_schedule.EVENTS = S_resume.EVENTS', 'S_schedule.RESULT = KNOWN PNULL',
    ]
    if outer_null:
        checks += [
            'S_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_resume.STORE[n_y] = DEFINED (PINT 88)',
            'S_schedule.TODO = (AT porigin_child (LIST_PATTERN expression (KNOWN PNULL) z)) :: (LIST_NEXT (KNOWN (PARRAY n_outer)) 1 phpType13* z_after) :: ptask_tail*',
            'S_child_found = $list_warning_seek(S_schedule, 6, 2000)',
            r'S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET',
            'S_child = S_child_found[.COMPLETION = NORMAL]',
            'S_child.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression_x false phpType13_rest* z_child) :: ptask_child_tail*',
            'S_child.ORIGIN = (porigin_child)',
            '$reference_origin_parent(porigin_child, 3) = ((porigin, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$list_missing_nested_context(S_child, porigin_child) = (z_child)',
            '$list_missing_plan(S_child) = eps',
            'S_child.STORE[n_x] = DEFINED (PINT 99)', 'S_child.STORE[n_y] = DEFINED (PINT 88)',
            '$heap_owners($heap_prune($heap_graph(S_child)), HARRAY n_outer) = 1',
            'PhpStep: S_child ~> S_xread',
            'S_xread.TODO = (AT porigin_x (LIST_STORE expression_x (KNOWN PNULL) false z_x)) :: (LIST_NEXT (KNOWN PNULL) 1 phpType13_rest* z_xnext) :: ptask_child_tail*',
            'S_xread.STORE = S_child.STORE', 'S_xread.EVENTS = S_child.EVENTS',
            'S_ynext_found = $list_warning_seek(S_xread, 7, 2000)',
            r'S_ynext_found.COMPLETION = NORMAL \/ S_ynext_found.COMPLETION = BUDGET',
            'S_ynext = S_ynext_found[.COMPLETION = NORMAL]',
            'S_ynext.TODO = (LIST_FETCH (KNOWN PNULL) 1 expression_y false eps z_yfetch) :: ptask_child_tail*',
            'S_ynext.STORE[n_x] = DEFINED PNULL', 'S_ynext.STORE[n_y] = DEFINED (PINT 88)',
            '$list_missing_plan(S_ynext) = eps',
            'PhpStep: S_ynext ~> S_yread',
            'S_yread.STORE = S_ynext.STORE', 'S_yread.EVENTS = S_ynext.EVENTS',
            '$call_descriptors_valid(S_yread)', '$heap_valid($heap_graph(S_yread))',
            'S_done = $drive_steps(S_yread, 2000)',
            'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.STORE[n_y] = DEFINED PNULL',
            'S_done.STORE[n_z] = DEFINED (PINT 3)',
        ]
    else:
        checks += [
            'S_resume.STORE[n_first] = DEFINED (PINT 21)', 'S_resume.STORE[n_missing] = DEFINED (PINT 99)',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            'S_resume.ARRAYS[n_outer] = S_entry.ARRAYS[n_outer]',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_child) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 2',
            'S_schedule.TODO = (AT porigin_missing (LIST_STORE expression (KNOWN PNULL) false z_missing)) :: (LIST_NEXT (KNOWN (PARRAY n_outer)) 2 phpType13* z_after) :: ptask_tail*',
            'S_next_found = $list_warning_seek(S_schedule, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_outer)) 2 expression_last false eps z_lastfetch) :: ptask_tail*',
            'S_next.STORE[n_first] = DEFINED (PINT 21)', 'S_next.STORE[n_missing] = DEFINED PNULL',
            'S_next.STORE[n_last] = DEFINED (PINT 9)',
            'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_last (LIST_STORE expression_last (KNOWN (PINT 4)) false z_last)) :: (LIST_NEXT (KNOWN (PARRAY n_outer)) 3 eps z_final) :: ptask_tail*',
            'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS',
            '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
            'S_done = $drive_steps(S_read, 2000)',
            'S_done.STORE[n_first] = DEFINED (PINT 21)', 'S_done.STORE[n_missing] = DEFINED PNULL',
            'S_done.STORE[n_last] = DEFINED (PINT 4)',
            '$lookup(S_done.ENV, $ptascii("q")) = eps',
            '~((HARRAY n_child) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_child) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_q) = 0',
        ]
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("dest")) = eps',
        'S_done.STORE[n_a] = DEFINED (PARRAY n_replacement)',
        '~((HARRAY n_outer) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_outer) = 0',
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
