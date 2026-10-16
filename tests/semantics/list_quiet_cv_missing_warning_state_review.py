#!/usr/bin/env python3
"""Reached request-string key cells and integer/string reference selection."""
import base64
import hashlib
import json
from pathlib import Path

import list_quiet_cv_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    request = name.endswith('request-key-cell-retire')
    line = 15 if request else 13
    operand = 'KNOWN (PARRAY n_array)' if request else 'REFERENCE n_source'
    key = 'KSTRING ($ptascii("old-row"))' if request else 'KINT 2'
    target, later = ('x', 'y') if request else ('missing', 'late')
    marker = f'LIST_MISSING_RESULT ({operand}) 0 expression phpType13* z ({key})'
    args = f'({operand}), 0, expression, phpType13*, z, {key}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        f'S_entry.TODO = (LIST_FETCH ({operand}) 0 expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S_entry.ORIGIN = (porigin)',
        'S_entry.RESULT = VARIABLE ($ptascii("key")) z',
        '$list_missing_integer_cv_item(S_entry, 0, expression, phpType13*, z) = (S_entry.RESULT)',
        f'$list_missing_plan(S_entry) = ((({operand}), 0, expression, phpType13*, z, {key}))',
        '$list_missing_pending(S_entry)',
        '$lookup(S_entry.ENV, $ptascii("key")) = (n_key_cell)',
        'S_entry.STORE[n_key_cell] = DEFINED pvalue_key',
        '$string_carrier_valid(S_entry, pvalue_key)',
        f'$list_missing_quiet_key(pvalue_key) = ({key})',
        f'$list_missing_cv_key_valid({key})',
        f'$lookup(S_entry.ENV, $ptascii("{target}")) = (n_target)',
        f'$lookup(S_entry.ENV, $ptascii("{later}")) = (n_later)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)',
        'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_source(S_entry, ' + args + ')',
        f'~$list_missing_source(S_entry, KNOWN PNULL, 0, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S_entry, ({operand}), 0, expression, phpType13*, $(z + 1), {key})',
        f'~$list_missing_source(S_entry, ({operand}), 0, expression, eps, z, {key})',
        '~$list_missing_source(S_entry[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S_entry[.CODE = eps], ' + args + ')',
        '$list_missing_plan(S_entry[.RESULT = KNOWN pvalue_key]) = eps',
        '$list_missing_plan(S_entry[.RESULT = VARIABLE ($ptascii("key")) $(z + 1)]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED (PFLOAT 9218868437227405312)]) = eps',
        'pvalue_invalid = PSTRING_CARRIER (REQUEST_STRING (|S_entry.STRINGDATA|)) ($ptascii("old-row"))',
        '~$string_carrier_valid(S_entry, pvalue_invalid)',
        '$list_missing_plan(S_entry[.STORE[n_key_cell] = DEFINED pvalue_invalid]) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if request:
        checks += [
            'pvalue_key = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("old-row"))',
            'S_entry.STRINGDATA[n_identity] = $ptascii("old-row")',
            '$lookup(S_entry.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S_entry.ENV, $ptascii("next")) = (n_next)',
            '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
            'S_entry.STORE[n_a] = DEFINED (PARRAY n_array)',
            'S_entry.STORE[n_target] = DEFINED (PINT 7)',
            'S_entry.STORE[n_later] = DEFINED (PINT 8)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_key_cell) = 2',
            '$heap_count(HARRAY n_array, $pools_nodes(S_entry.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 2',
            '$list_missing_plan(S_entry[.STRINGDATA = eps]) = eps',
            '$task_nodes(' + marker + ') = [HARRAY n_array]',
        ]
    else:
        checks += [
            'pvalue_key = PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))',
            '$lookup(S_entry.ENV, $ptascii("a")) = (n_source)',
            'n_source <- S_entry.REFCELLS',
            'S_entry.STORE[n_source] = DEFINED (PARRAY n_array)',
            '$lookup(S_entry.ENV, $ptascii("copy")) = (n_copy)',
            'S_entry.STORE[n_copy] = DEFINED (PARRAY n_array)',
            '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)',
            'S_entry.STORE[n_q] = DEFINED (PINT 2)',
            'S_entry.STORE[n_target] = DEFINED (PINT 7)',
            'S_entry.STORE[n_later] = DEFINED (PINT 8)',
            '$entry_lookup(S_entry.ARRAYS[n_array].ITEMS, KINT 2) = eps',
            '$entry_lookup(S_entry.ARRAYS[n_array].ITEMS, KSTRING ($ptascii("02"))) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
            '$task_nodes(' + marker + ') = [HCELL n_source]',
        ]
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        f'perrorcall.MESSAGE = $list_missing_message({key})',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
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
        '$list_missing_source(S_resume, ' + args + ')',
        'S_resume.STORE[n_target] = DEFINED (PINT 99)',
    ]
    if request:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("key")) = (n_replacement)',
            '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
            'n_key_cell =/= n_replacement',
            '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_key_cell) = 0',
            # Identity bytes persist as metadata; no string heap owner exists.
            'S_resume.STRINGDATA[n_identity] = $ptascii("old-row")',
            'S_resume.STORE[n_a] = DEFINED (PARRAY n_live)',
            'n_live =/= n_array',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KSTRING ($ptascii("old-row"))) = (DIRECT (PINT 77))',
            '$entry_lookup(S_resume.ARRAYS[n_array].ITEMS, KSTRING ($ptascii("old-row"))) = eps',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
        ]
    else:
        checks += [
            'S_resume.STORE[n_key_cell] = DEFINED pvalue_later_key',
            '$string_carrier_valid(S_resume, pvalue_later_key)',
            '$string_bytes(pvalue_later_key) = ($ptascii("02"))',
            '$list_missing_quiet_key(pvalue_later_key) = (KSTRING ($ptascii("02")))',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_live)',
            'n_live =/= n_array', 'S_resume.STORE[n_copy] = DEFINED (PARRAY n_array)',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 2) = (DIRECT (PINT 77))',
            '$entry_lookup(S_resume.ARRAYS[n_array].ITEMS, KINT 2) = eps',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
        ]
    checks += [
        'PhpStep: S_resume ~> S_schedule',
        'S_schedule.RESULT = KNOWN PNULL',
        'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
        f'S_next_found = $list_warning_seek(S_schedule, {4 if request else 6}, 2000)',
        r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
        'S_next = S_next_found[.COMPLETION = NORMAL]',
        'S_next.STORE[n_target] = DEFINED PNULL',
    ]
    if request:
        checks += [
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_next false eps z_next) :: ptask_next*',
            'z_next = 16', 'S_next.RESULT = VARIABLE ($ptascii("next")) 16',
            'S_next.STORE[n_next] = DEFINED pvalue_next',
            '$string_bytes(pvalue_next) = ($ptascii("old"))',
            '$list_missing_quiet_key(pvalue_next) = (KSTRING ($ptascii("old")))',
            '$list_missing_plan(S_next) = eps',
            'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_later (LIST_STORE expression_next (KNOWN (PINT 11)) false z_later)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 2 eps z_end) :: ptask_next*',
        ]
    else:
        checks += [
            'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_next true eps z_next) :: ptask_next*',
            'z_next = 14', 'S_next.RESULT = VARIABLE ($ptascii("key")) 14',
            'PhpStep: S_next ~> S_read',
            'S_read.TODO = (AT porigin_later (LIST_STORE expression_next (REFERENCE n_q) true z_later)) :: (LIST_NEXT (REFERENCE n_source) 2 eps z_end) :: ptask_next*',
            'S_read.STORE[n_source] = DEFINED (PARRAY n_live)',
            '$entry_lookup(S_read.ARRAYS[n_live].ITEMS, KSTRING ($ptascii("02"))) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S_read)), HCELL n_q) = 4',
        ]
    checks += [
        'S_read_driven_found = $drive_steps(S_next, 1)',
        'S_read_driven_found.COMPLETION = BUDGET',
        'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]',
        'S_read_driven.STORE = S_read.STORE', 'S_read_driven.ARRAYS = S_read.ARRAYS',
        'S_read_driven.TODO = S_read.TODO', 'S_read_driven.RESULT = S_read.RESULT',
    ]
    if request:
        checks += [
            'S_done = $drive_steps(S_read_driven, 2000)',
            'S_done.STORE[n_later] = DEFINED (PINT 11)',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
            '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)', '~((HCELL n_replacement) <- S_done.ALLOCATIONS)',
        ]
    else:
        checks += [
            'S_target_found = $drive_steps(S_read_driven, 1)',
            'S_target_found.COMPLETION = BUDGET',
            'S_target = S_target_found[.COMPLETION = NORMAL]',
            'S_target.TODO = (LIST_STORE expression_next (REFERENCE n_q) true z_later) :: ptask_after*',
            'PhpStep: S_target ~> S_bound_raw',
            '$lookup(S_bound_raw.ENV, $ptascii("late")) = (n_q)',
            '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_later) = 0',
            '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_q) = 4',
            'S_bound_found = $drive_steps(S_target, 1)',
            'S_bound_found.COMPLETION = BUDGET',
            'S_bound = S_bound_found[.COMPLETION = NORMAL]',
            '~((HCELL n_later) <- S_bound.ALLOCATIONS)',
            'S_done = $drive_steps(S_bound, 2000)',
            '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_live) <- S_done.ALLOCATIONS)',
        ]
    return checks + [
        'S_done.STORE[n_target] = DEFINED PNULL',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_resume, 2000) = S_done', '$drive_steps(S_entry, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
