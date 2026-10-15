#!/usr/bin/env python3
"""Captured source-cell rebinding, reference COW and inherited fetch lines."""
import base64
import hashlib
import json
from pathlib import Path

import list_reference_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    rebound = name.endswith('unset-rebind-cow')
    index, line, next_index = (0, 11, 1) if rebound else (2, 18, 3)
    target = 'x' if rebound else 'missing'
    reference_target = 'y' if rebound else 'last'
    initial_target, initial_reference, fetched = (7, 8, 2) if rebound else (8, 9, 34)
    marker = f'LIST_MISSING_RESULT (REFERENCE n_source) {index} expression phpType13* z (KINT {index})'
    args = f'REFERENCE n_source, {index}, expression, phpType13*, z, KINT {index}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        f'S_entry.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'S_entry.RESULT = KNOWN (PINT {index})',
        'S_entry.ORIGIN = (porigin)',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_source)',
        'S_entry.STORE[n_source] = DEFINED (PARRAY n_before)',
        'n_source <- S_entry.REFCELLS',
        '$heap_count(HARRAY n_before, $pools_nodes(S_entry.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_source) = 2',
        f'$lookup(S_entry.ENV, $ptascii("{target}")) = (n_target)',
        f'$lookup(S_entry.ENV, $ptascii("{reference_target}")) = (n_old_reference)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)',
        f'S_entry.STORE[n_target] = DEFINED (PINT {initial_target})',
        f'S_entry.STORE[n_old_reference] = DEFINED (PINT {initial_reference})',
        'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        f'$entry_lookup(S_entry.ARRAYS[n_before].ITEMS, KINT {index}) = eps',
        '$list_missing_source(S_entry, ' + args + ')',
        f'~$list_missing_source(S_entry, REFERENCE n_source, {index}, expression, phpType13*, $(z + 1), KINT {index})',
        f'~$list_missing_source(S_entry, REFERENCE n_source, {index}, expression, eps, z, KINT {index})',
        f'~$list_missing_source(S_entry, REFERENCE n_source, {index}, expression, phpType13*, z, KINT 9)',
        f'~$list_missing_source(S_entry, KNOWN (PARRAY n_before), {index}, expression, phpType13*, z, KINT {index})',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.ALLOCATIONS = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.REFCELLS = eps], ' + args + ')',
        f'~$list_missing_source(S_entry, REFERENCE (|S_entry.STORE|), {index}, expression, phpType13*, z, KINT {index})',
        '$list_missing_plan(S_entry[.RESULT = KNOWN (PINT 9)]) = eps',
        '$task_nodes(' + marker + ') = [HCELL n_source]',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if rebound:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("copy")) = (n_copy)',
            'S_entry.STORE[n_copy] = DEFINED (PARRAY n_before)',
            '$lookup(S_entry.ENV, $ptascii("other")) = (n_other)',
            'n_source =/= n_other',
            '$entry_lookup(S_entry.ARRAYS[n_before].ITEMS, KINT 1) = (DIRECT (PINT 2))',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_before) = 2',
        ]
    else:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("first")) = (n_first)',
            'S_entry.STORE[n_first] = DEFINED (PINT 2)',
            '$entry_lookup(S_entry.ARRAYS[n_before].ITEMS, KINT 0) = (ALIAS n_first)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_first) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_before) = 1',
        ]
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 512])',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_source]',
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
        'S_resume.STORE[n_source] = DEFINED (PARRAY n_before)',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
    ]
    if rebound:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("a")) = (n_other)',
            '$lookup(S_resume.ENV, $ptascii("other")) = (n_other)',
            'S_resume.STORE[n_other] = DEFINED (PARRAY n_other_array)',
            '$entry_lookup(S_resume.ARRAYS[n_other_array].ITEMS, KINT 1) = (DIRECT (PINT 44))',
            'S_resume.ARRAYS[n_before] = S_entry.ARRAYS[n_before]',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_other) = 2',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_before) = 2',
            'S_resume.STORE[n_target] = DEFINED (PINT 7)',
        ]
    else:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("a")) = (n_source)',
            'S_resume.STORE[n_first] = DEFINED (PINT 21)',
            'S_resume.STORE[n_target] = DEFINED (PINT 99)',
            '$entry_lookup(S_resume.ARRAYS[n_before].ITEMS, KINT 3) = (DIRECT (PINT 34))',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 2',
        ]
    checks += [
        'PhpStep: S_resume ~> S_schedule',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
        f'S_schedule.TODO = (AT porigin_target (LIST_STORE expression (KNOWN PNULL) false z_target)) :: (LIST_NEXT (REFERENCE n_source) {index + 1} phpType13* z_next) :: ptask_tail*',
        'S_next_found = $list_warning_seek(S_schedule, 6, 2000)',
        r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
        'S_next = S_next_found[.COMPLETION = NORMAL]',
        f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) {next_index} expression_next true eps z_fetch) :: ptask_tail*',
        f'S_next.RESULT = KNOWN (PINT {next_index})',
        'S_next.STORE[n_target] = DEFINED PNULL',
        f'S_next.STORE[n_old_reference] = DEFINED (PINT {initial_reference})',
        'PhpStep: S_next ~> S_read',
        f'S_read.TODO = (AT porigin_reference (LIST_STORE expression_next (REFERENCE n_element) true z_reference)) :: (LIST_NEXT (REFERENCE n_source) {next_index + 1} eps z_after) :: ptask_tail*',
        'S_read.STORE[n_source] = DEFINED (PARRAY n_write)',
        f'$entry_lookup(S_read.ARRAYS[n_write].ITEMS, KINT {next_index}) = (ALIAS n_element)',
        f'S_read.STORE[n_element] = DEFINED (PINT {fetched})',
        'n_element <- S_read.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_read)), HCELL n_element) = 2',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
    ]
    if rebound:
        checks += [
            'n_write =/= n_before',
            'S_read.STORE[n_copy] = DEFINED (PARRAY n_before)',
            '$entry_lookup(S_read.ARRAYS[n_before].ITEMS, KINT 1) = (DIRECT (PINT 2))',
            '$heap_owners($heap_prune($heap_graph(S_read)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_read)), HARRAY n_before) = 1',
        ]
    else:
        checks += [
            'n_write = n_before',
            'S_read.STORE[n_first] = DEFINED (PINT 21)',
            '$entry_lookup(S_read.ARRAYS[n_write].ITEMS, KINT 0) = (ALIAS n_first)',
        ]
    checks += [
        'S_target_found = $drive_steps(S_read, 1)',
        'S_target_found.COMPLETION = BUDGET',
        'S_target = S_target_found[.COMPLETION = NORMAL]',
        'S_target.TODO = (LIST_STORE expression_next (REFERENCE n_element) true z_reference) :: ptask_after*',
        'PhpStep: S_target ~> S_bound_raw',
        f'$lookup(S_bound_raw.ENV, $ptascii("{reference_target}")) = (n_element)',
        '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_old_reference) = 0',
        'S_bound_budget = $drive_steps(S_target, 1)',
        'S_bound_budget.COMPLETION = BUDGET',
        'S_bound = S_bound_budget[.COMPLETION = NORMAL]',
        'S_bound.STORE = S_bound_raw.STORE', 'S_bound.ARRAYS = S_bound_raw.ARRAYS',
        f'$lookup(S_bound.ENV, $ptascii("{reference_target}")) = (n_element)',
        '~((HCELL n_old_reference) <- S_bound.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_bound)), HCELL n_element) = 2',
        '$call_descriptors_valid(S_bound)', '$heap_valid($heap_graph(S_bound))',
        'S_done = $drive_steps(S_bound, 2000)',
        'S_done.STORE[n_target] = DEFINED PNULL',
    ]
    if rebound:
        checks += [
            '$lookup(S_done.ENV, $ptascii("a")) = (n_other)',
            '$lookup(S_done.ENV, $ptascii("other")) = (n_other)',
            '$lookup(S_done.ENV, $ptascii("dest")) = eps',
            '$lookup(S_done.ENV, $ptascii("y")) = eps',
            '~((HCELL n_source) <- S_done.ALLOCATIONS)',
            '~((HCELL n_element) <- S_done.ALLOCATIONS)',
            '~((HARRAY n_write) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_source) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_element) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_write) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_before) = 1',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_other) = 2',
            'S_done.STORE[n_copy] = DEFINED (PARRAY n_before)',
            'S_done.STORE[n_other] = DEFINED (PARRAY n_other_array)',
            '$entry_lookup(S_done.ARRAYS[n_other_array].ITEMS, KINT 1) = (DIRECT (PINT 44))',
        ]
    else:
        checks += [
            'S_done.STORE[n_first] = DEFINED (PINT 22)',
            'S_done.STORE[n_element] = DEFINED (PINT 35)',
            'S_done.STORE[n_dest] = DEFINED (PARRAY n_write)',
            'S_done.STORE[n_source] = DEFINED (PARRAY n_write)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_write) = 2',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_first) = 2',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_element) = 2',
        ]
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
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
