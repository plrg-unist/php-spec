#!/usr/bin/env python3
"""Literal pool replay cancellation and captured reference-cell rebinding."""
import base64
import hashlib
import json
from pathlib import Path

import list_literal_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

SELECTED = ('list-literal-review-pooled-throw', 'list-literal-review-reference-rebind')
HELPERS = shared.HELPERS + r'''
dec $literal_review_replay_task(ptask) : bool
def $literal_review_replay_task(COMPILED_RESULT b) = true
def $literal_review_replay_task(AT porigin ptask) = $literal_review_replay_task(ptask)
def $literal_review_replay_task(ptask) = false -- otherwise
dec $literal_review_replays(ptask*) : bool
def $literal_review_replays(eps) = false
def $literal_review_replays(ptask :: ptask_tail*) = ($literal_review_replay_task(ptask) \/ $literal_review_replays(ptask_tail*))
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if ~$literal_review_replays(S.TODO)
  -- if ~$list_warning_tasks(S.TODO)
'''


def conditions(name, program, path, stdout):
    pooled = name.endswith('pooled-throw')
    line = 9 if pooled else 10
    marker = 'LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 0 expression phpType13* z (KINT 0)'
    source_args = 'KNOWN (PARRAY n_array), 0, expression, phpType13*, z, KINT 0'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        'S_entry.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 0 expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S_entry.RESULT = KNOWN (PINT 0)',
        'S_entry.ORIGIN = (porigin)',
        '$reference_origin_parent(porigin, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S_entry.SOURCES, porigin_assign) = (NExprAssign expression_pattern expression_rhs metadata)',
        '$origin_child((porigin_assign), [PCFIELD 1]) = (porigin_rhs)',
        'porigin_rhs = PORIGIN n_unit pcpath_rhs',
        '$code_at(S_entry.CODE, n_unit) = (pcode)',
        '$list_missing_rhs(S_entry, porigin_rhs, expression_rhs, n_array)',
        '$list_missing_source(S_entry, ' + source_args + ')',
        '~$list_missing_rhs(S_entry[.CODE = eps], porigin_rhs, expression_rhs, n_array)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)',
        '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)',
        'S_entry.STORE[n_x] = DEFINED (PINT 7)',
        'S_entry.STORE[n_y] = DEFINED (PINT 8)',
        'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        'n_pool = $heap_count(HARRAY n_array, $pools_nodes(S_entry.POOLS))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = $(n_pool + 1)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if pooled:
        checks += [
            '$compiled_read(S_entry, porigin_rhs) = (PARRAY n_array)',
            '$code_expression(pcode.EXPRESSIONS, pcpath_rhs) = ((z_rhs, true))',
            '$(n_pool > 0)',
            '$literal_review_replays(S_entry.TODO)',
            '~$list_missing_rhs(S_entry[.POOLS = eps], porigin_rhs, expression_rhs, n_array)',
            '~$list_missing_rhs(S_entry, porigin_rhs, expression_rhs, $(n_array + 1))',
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ]
    else:
        checks += [
            '$compiled_read(S_entry, porigin_rhs) = eps',
            '$code_expression(pcode.EXPRESSIONS, pcpath_rhs) = ((z_rhs, false))',
            'n_pool = 0', '~$array_immutable(S_entry, n_array)',
            '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)',
            '$lookup(S_entry.ENV, $ptascii("other")) = (n_other)',
            'n_q =/= n_other', 'n_q <- S_entry.REFCELLS',
            'S_entry.STORE[n_q] = DEFINED (PINT 2)',
            'S_entry.STORE[n_other] = DEFINED (PINT 33)',
            'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 1) (ALIAS n_q)]',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_other) = 1',
        ]
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_array]',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]',
        'S_entered.CURRENT =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if pooled:
        checks += [
            'S_pending_found = $list_warning_seek(S_entered, 6, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (THROW_SEARCH n_second) :: ptask_pending*',
            '~$literal_review_replays(S_pending.TODO)',
            '(HARRAY n_array) <- S_pending.ALLOCATIONS',
            'S_pending.POOLS = S_entry.POOLS', 'S_pending.CODE = S_entry.CODE',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_array) = n_pool',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)',
            'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '$throwable_live(S_pending, n_second)',
            '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)',
            'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
            '(HARRAY n_array) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = n_pool',
        ]
    else:
        checks += [
            'S_resume_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
            'S_resume = S_resume_found[.COMPLETION = NORMAL]',
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_other)',
            '$lookup(S_resume.ENV, $ptascii("other")) = (n_other)',
            'S_resume.STORE[n_q] = DEFINED (PINT 2)',
            'S_resume.STORE[n_other] = DEFINED (PINT 44)',
            'S_resume.ARRAYS[n_array] = S_entry.ARRAYS[n_array]',
            '$list_missing_rhs(S_resume, porigin_rhs, expression_rhs, n_array)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_other) = 2',
            '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
            'PhpStep: S_resume ~> S_schedule',
            'S_schedule.STORE = S_resume.STORE', 'S_schedule.ARRAYS = S_resume.ARRAYS',
            'S_schedule.TODO = (AT porigin_target (LIST_STORE expression (KNOWN PNULL) false z_target)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 1 phpType13* z_next) :: ptask_tail*',
            'S_next_found = $list_warning_seek(S_schedule, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_next false eps z_next) :: ptask_tail*',
            'S_next.STORE[n_x] = DEFINED PNULL',
            'S_next.STORE[n_y] = DEFINED (PINT 8)',
            'PhpStep: S_next ~> S_read',
            'S_read.STORE = S_next.STORE',
            'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT 2)) false z_y)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 2 eps z_after) :: ptask_tail*',
            '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
            'S_done = $drive_steps(S_read, 2000)',
            'S_done.STORE[n_x] = DEFINED PNULL',
            'S_done.STORE[n_y] = DEFINED (PINT 2)',
            'S_done.STORE[n_other] = DEFINED (PINT 44)',
            '$lookup(S_done.ENV, $ptascii("q")) = (n_other)',
            '$lookup(S_done.ENV, $ptascii("other")) = (n_other)',
            '$lookup(S_done.ENV, $ptascii("dest")) = eps',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
            '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_q) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_other) = 2',
            '$drive_steps(S_resume, 2000) = S_done',
        ]
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.POOLS = S_entry.POOLS',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_entry, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    cases.CASES = {name: cases.CASES[name] for name in SELECTED}
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
