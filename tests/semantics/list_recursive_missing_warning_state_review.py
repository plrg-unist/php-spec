#!/usr/bin/env python3
"""Deep NULL descent and captured old-row tasks versus live result aliases."""
import base64
import hashlib
import json
from pathlib import Path

import list_recursive_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression false phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 7) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 1 expression false phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 8) = true
  -- if S.TODO = (LIST_FETCH (KNOWN (PARRAY n)) 2 expression false eps z) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))
  -- if $origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)
'''


def conditions(name, program, path, stdout):
    null_chain = name.endswith('outer-null-chain')
    marker = 'LIST_MISSING_RESULT (KNOWN (PARRAY n_source)) 0 expression phpType13* z (KINT 0)'
    args = 'KNOWN (PARRAY n_source), 0, expression, phpType13*, z, KINT 0'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        'S_entry.TODO = (LIST_FETCH (KNOWN (PARRAY n_source)) 0 expression false phpType13* z) :: ptask_tail*',
        'z = 14', 'S_entry.RESULT = KNOWN (PINT 0)', 'S_entry.ORIGIN = (porigin)',
        '$list_missing_nested_context(S_entry, porigin) = (z_initial)',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)', 'S_entry.STORE[n_a] = DEFINED (PARRAY n_root)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)', 'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        '$heap_count(HARRAY n_root, $pools_nodes(S_entry.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_source) = 2',
        '$list_missing_source(S_entry, ' + args + ')',
        '~$list_missing_source(S_entry, KNOWN (PARRAY n_source), 0, expression, phpType13*, $(z + 1), KINT 0)',
        '~$list_missing_source(S_entry, KNOWN (PARRAY n_source), 0, expression, eps, z, KINT 0)',
        '~$list_missing_source(S_entry, KNOWN (PARRAY n_source), 0, expression, phpType13*, z, KINT 9)',
        '~$list_missing_source(S_entry, REFERENCE n_a, 0, expression, phpType13*, z, KINT 0)',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        '$list_missing_plan(S_entry[.RESULT = KNOWN (PINT 9)]) = eps',
        '$task_nodes(' + marker + ') = [HARRAY n_source]',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if null_chain:
        checks += [
            'n_source = n_root', 'porigin_root = porigin',
            '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'S_entry.STORE[n_x] = DEFINED (PINT 7)',
            '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)', 'S_entry.STORE[n_y] = DEFINED (PINT 8)',
            '$lookup(S_entry.ENV, $ptascii("z")) = (n_z)', 'S_entry.STORE[n_z] = DEFINED (PINT 9)',
        ]
    else:
        checks += [
            '$reference_origin_parent(porigin, 9) = ((porigin_root, [PCFIELD 0, PCINDEX 1, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$lookup(S_entry.ENV, $ptascii("row")) = (n_row_cell)',
            '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)', 'S_entry.STORE[n_q] = DEFINED (PINT 2)',
            '$entry_lookup(S_entry.ARRAYS[n_root].ITEMS, KINT 1) = (ALIAS n_row_cell)',
            'S_entry.STORE[n_row_cell] = DEFINED (PARRAY n_old_row)',
            '$entry_lookup(S_entry.ARRAYS[n_old_row].ITEMS, KINT 0) = (DIRECT (PARRAY n_mid))',
            '$entry_lookup(S_entry.ARRAYS[n_mid].ITEMS, KINT 0) = (DIRECT (PARRAY n_source))',
            '$entry_lookup(S_entry.ARRAYS[n_source].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_row_cell) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
        ]
        for array in ('n_root', 'n_old_row', 'n_mid', 'n_source'):
            checks += [f'$heap_count(HARRAY {array}, $tasks_nodes(S_entry.TODO)) = 1']
            if array != 'n_root':
                checks += [f'$heap_count(HARRAY {array}, $pools_nodes(S_entry.POOLS)) = 0']
            if array != 'n_source':
                checks += [f'$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY {array}) = 2']
        for var, value in (('first', 5), ('missing', 8), ('last', 9), ('near', 10), ('middle', 11), ('tail', 12)):
            checks += [f'$lookup(S_entry.ENV, $ptascii("{var}")) = (n_{var})', f'S_entry.STORE[n_{var}] = DEFINED (PINT {value})']
    checks += [
        '$origin_node(S_entry.SOURCES, porigin_root) = (expression_root)',
        '$list_pattern(expression_root) = (phpType13_root*)', '~$list_missing_flat(phpType13_root*)',
        '$list_missing_nested_items(phpType13_root*)', '~$list_references(phpType13_root*)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S_entry.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        '$list_missing_nested_items([NArrayItem ABSENT expression_root (BOOLEAN false) (BOOLEAN false) metadata_assign])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression_root (BOOLEAN true) (BOOLEAN false) metadata_assign])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression_rhs (BOOLEAN false) (BOOLEAN true) metadata_assign])',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S_entry.SOURCES[n_unit] = pcunit',
        'S_wide = S_entry[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NScalarInt (INTEGER 1) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_nested_context(S_wide, porigin) = eps', '~$list_missing_source(S_wide, ' + args + ')',
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*', 'perrorcall.RESUME = ' + marker,
        '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HARRAY n_source]',
        'S_dispatch.STORE = S_entry.STORE', 'S_dispatch.ARRAYS = S_entry.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT =/= eps',
        'S_entered.ERRORHANDLER.CALLBACK = eps', 'S_entered.FRAMES = pframe :: eps',
        '$heap_count(HARRAY n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_resume_found = $list_warning_seek(S_entered, 2, 2000)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', 'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        'S_resume.ERRORHANDLER = S_entry.ERRORHANDLER', '$list_missing_source(S_resume, ' + args + ')',
        'S_resume.STORE[n_dest] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'PhpStep: S_resume ~> S_schedule',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
        'S_schedule.EVENTS = S_resume.EVENTS', 'S_schedule.RESULT = KNOWN PNULL',
    ]
    if null_chain:
        checks += [
            'S_resume.STORE[n_a] = DEFINED (PARRAY n_replacement)', 'n_replacement =/= n_root',
            'S_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_resume.STORE[n_y] = DEFINED (PINT 88)',
            'S_schedule.TODO = (AT porigin_1 (LIST_PATTERN expression (KNOWN PNULL) z)) :: (LIST_NEXT (KNOWN (PARRAY n_root)) 1 phpType13* z_after) :: ptask_tail*',
        ]
        prior = 'S_schedule'
        for level in range(1, 4):
            state, read = f'S_level{level}', f'S_read{level}'
            parent = 'porigin_root' if level == 1 else f'porigin_{level - 1}'
            checks += [
                f'{state}_found = $list_warning_seek({prior}, 6, 2000)',
                rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
                f'{state} = {state}_found[.COMPLETION = NORMAL]',
                f'{state}.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression_{level} false phpType13_{level}* z_{level}) :: ptask_{level}*',
                f'{state}.ORIGIN = (porigin_{level})',
                f'$reference_origin_parent(porigin_{level}, 3) = (({parent}, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
                f'$list_missing_nested_context({state}, porigin_{level}) = (z_{level})',
                f'$list_missing_plan({state}) = eps',
                f'$heap_owners($heap_prune($heap_graph({state})), HARRAY n_root) = 1',
                f'PhpStep: {state} ~> {read}', f'{read}.STORE = {state}.STORE', f'{read}.EVENTS = {state}.EVENTS',
            ]
            if level < 3:
                checks += [f'{read}.TODO = (AT porigin_{level + 1} (LIST_PATTERN expression_{level} (KNOWN PNULL) z_{level})) :: (LIST_NEXT (KNOWN PNULL) 1 phpType13_{level}* z_after_{level}) :: ptask_{level}*']
            prior = read
        checks += [
            'S_ynext_found = $list_warning_seek(S_read3, 7, 2000)',
            r'S_ynext_found.COMPLETION = NORMAL \/ S_ynext_found.COMPLETION = BUDGET',
            'S_ynext = S_ynext_found[.COMPLETION = NORMAL]',
            'S_ynext.TODO = (LIST_FETCH (KNOWN PNULL) 1 expression_y false eps z_y) :: ptask_y*',
            'S_ynext.STORE[n_x] = DEFINED PNULL', 'S_ynext.STORE[n_y] = DEFINED (PINT 88)',
            '$list_missing_plan(S_ynext) = eps', 'PhpStep: S_ynext ~> S_yread',
            'S_yread.STORE = S_ynext.STORE', 'S_yread.EVENTS = S_ynext.EVENTS',
            'S_done = $drive_steps(S_yread, 2000)',
            'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.STORE[n_y] = DEFINED PNULL',
            'S_done.STORE[n_z] = DEFINED (PINT 3)',
            'S_done.STORE[n_a] = DEFINED (PARRAY n_replacement)',
        ]
    else:
        checks += [
            'S_resume.STORE[n_a] = DEFINED (PARRAY n_root)',
            'S_resume.STORE[n_row_cell] = DEFINED (PARRAY n_new_row)', 'n_new_row =/= n_old_row',
            'S_resume.ARRAYS[n_root] = S_entry.ARRAYS[n_root]',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)', 'S_resume.STORE[n_first] = DEFINED (PINT 21)',
            'S_resume.STORE[n_missing] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_old_row) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_mid) = 2',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_source) = 2',
            'S_schedule.TODO = (AT porigin_missing (LIST_STORE expression (KNOWN PNULL) false z_missing)) :: (LIST_NEXT (KNOWN (PARRAY n_source)) 1 phpType13* z_after) :: ptask_tail*',
            'S_next_found = $list_warning_seek(S_schedule, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_source)) 1 expression_last false eps z_last) :: ptask_next*',
            'S_next.STORE[n_missing] = DEFINED PNULL', 'S_next.STORE[n_last] = DEFINED (PINT 9)',
            'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_last (LIST_STORE expression_last (KNOWN (PINT 33)) false z_store)) :: (LIST_NEXT (KNOWN (PARRAY n_source)) 2 eps z_follow) :: ptask_next*',
            'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS',
            'S_outer_found = $list_warning_seek(S_read, 8, 2000)',
            r'S_outer_found.COMPLETION = NORMAL \/ S_outer_found.COMPLETION = BUDGET',
            'S_outer = S_outer_found[.COMPLETION = NORMAL]',
            'S_outer.TODO = (LIST_FETCH (KNOWN (PARRAY n_root)) 2 expression_tail false eps z_tail) :: ptask_outer*',
            'S_outer.STORE[n_dest] = DEFINED (PINT 100)',
            'S_outer.STORE[n_row_cell] = DEFINED (PARRAY n_new_row)',
            '$heap_owners($heap_prune($heap_graph(S_outer)), HCELL n_q) = 1',
            '$call_descriptors_valid(S_outer)', '$heap_valid($heap_graph(S_outer))',
        ]
        for array in ('n_old_row', 'n_mid', 'n_source'):
            checks += [f'~((HARRAY {array}) <- S_outer.ALLOCATIONS)', f'$heap_owners($heap_prune($heap_graph(S_outer)), HARRAY {array}) = 0']
        for var, value in (('first', 21), ('last', 33), ('near', 6), ('middle', 7), ('tail', 12)):
            checks += [f'S_outer.STORE[n_{var}] = DEFINED (PINT {value})']
        checks += [
            'PhpStep: S_outer ~> S_tailread',
            'S_tailread.TODO = (AT porigin_tail (LIST_STORE expression_tail (KNOWN (PINT 4)) false z_tailstore)) :: (LIST_NEXT (KNOWN (PARRAY n_root)) 3 eps z_final) :: ptask_outer*',
            'S_done = $drive_steps(S_tailread, 2000)', 'S_done.STORE[n_missing] = DEFINED PNULL',
            '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HCELL n_row_cell) <- S_done.ALLOCATIONS)',
        ]
        for var, value in (('first', 21), ('last', 33), ('near', 6), ('middle', 7), ('tail', 4)):
            checks += [f'S_done.STORE[n_{var}] = DEFINED (PINT {value})']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("dest")) = eps', '~((HARRAY n_root) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_root) = 0',
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
