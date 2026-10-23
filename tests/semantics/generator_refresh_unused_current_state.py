#!/usr/bin/env python3
"""Reach first CURRENT refresh, transferred child edges and real prefix cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_refresh_unused_current_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
UNUSED = 'generator-refresh-unused-current-row-finally-write'
USED = 'generator-refresh-unused-current-assignment-control'
PREFIX = ['P|', 'U|', 'M|', 'C0|', 'READY|', 'L|', 'H|', 'S|', 'TAKE|', 'CLEARED|']
EVENTS = {
    UNUSED: PREFIX + ['K|', 'A|', 'K-END|', 'CALLER|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
    USED: PREFIX + ['K|', 'K-END|', 'CALLER|', 'A|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
         '-- if pgeneratorop.NAME = "current" -- if pgeneratorop.LINE = 12')
COMMON = checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.COMPLETION = NORMAL
S.GC.ACTIVE = eps
S.HELD = eps
~S.CONSTCONTEXT
S.GENERATORINPUTS = eps
S.GENERATORRETURNRETAINED = eps
S.RESULT = KNOWN PNULL
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
~pgeneratorop.ADVANCE
n_upper = pgeneratorop.OBJECT
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_DELEGATING
~pgenerator_upper.PENDING_INIT
pgenerator_upper.PARKED = eps
pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)
pgeneratorfrom_upper.INPUT = (POBJECT n_middle)
pgeneratorfrom_upper.CURRENT = eps
pgeneratorfrom_upper.ACQUISITION = eps
pgeneratorfrom_upper.POSITION = 1
pgenerator_upper.FRAME = (pframe_upper)
pframe_upper.TODO = (GENERATOR_FROM_NEXT n_upper pgeneratorfrom_upper.SITE) :: ptask_upper_tail*
pframe_upper.HELD = eps
$tasks_nodes(pframe_upper.TODO) = eps
n_upper =/= n_middle
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = (POBJECT n_child)
pgeneratorfrom_middle.CURRENT = eps
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_NEXT n_middle pgeneratorfrom_middle.SITE) :: ptask_middle_tail*
pframe_middle.HELD = eps
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_CLOSED
pgenerator_child.FRAME = eps
pgenerator_child.REFCELL = (n_row)
$generator_values_nodes(pgenerator_child.KEY) = eps
pgenerator_child.RETURN = (PNULL)
pgenerator_child.CLOSURE = eps
(HOBJECT n_child) <- S.ALLOCATIONS
$generator_storage_for(S, n_child) = eps
$generator_record_valid(S, pgenerator_child)
$node_children(S, HOBJECT n_child) = [HCELL n_row]
~$generator_nodefree_return_waiting(S, n_middle)
$generator_nodefree_ancestor_leaf(S, n_upper) = eps
$generator_operation_valid(S, pgeneratorop)
$getter_arguments(S, pgeneratorop.SITE) = PCALLARGUMENTS eps 2
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_array)
n_row <- S.REFCELLS
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_old) = $ptascii("RefreshUnusedCurrentRowOld52")
$node_children(S, HCELL n_row) = [HARRAY n_array]
$node_children(S, HARRAY n_array) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HARRAY n_array) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
~(n_old <- S.DESTRUCTION.CALLED)
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$heap_owners($heap_graph(S), HOBJECT n_child) = 1
ptask_source = GENERATOR_ARGS pgeneratorop eps eps
S_call = S[.TODO = ptask_tail*]
S_updated = $generator_from_update(S_call, pgeneratorop)
S_updated = $generator_from_refresh(S_call, n_upper, $(|S.OBJECTS| + 1))
S_updated =/= S_call
S_updated.OBJECTS[n_upper] = GENERATOR pgenerator_upper
S_updated.OBJECTS[n_child] = GENERATOR pgenerator_child
S_updated.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed
pgenerator_refreshed.PENDING_INIT
pgenerator_refreshed.DELEGATE = (pgeneratorfrom_refreshed)
pgeneratorfrom_refreshed.INPUT = eps
pgeneratorfrom_refreshed.CURRENT = (REFERENCE n_row)
pgenerator_refreshed.FRAME = (pframe_refreshed)
pframe_refreshed.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child PNULL) :: ptask_middle_tail*
$generator_from_complete_valid(S_updated, n_middle, pgeneratorfrom_middle.SITE, n_child, PNULL)
$generator_nodefree_return_waiting(S_updated, n_middle)
$generator_nodefree_ancestor_leaf(S_updated, n_upper) = (n_middle)
$task_nodes(GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child PNULL) = eps
S_updated.STORE = S.STORE
S_updated.ARRAYS = S.ARRAYS
S_updated.ALLOCATIONS = S.ALLOCATIONS
S_updated.REFCELLS = S.REFCELLS
S_updated.TODO = ptask_tail*
$heap_owners($heap_graph(S_updated), HOBJECT n_child) = 0
$heap_owners($heap_graph(S_updated), HCELL n_row) = 3
$eager_slots(S_call, S_updated) = [HOBJECT n_child]
$generator_unused_current_refresh(S_call, S_updated, n_upper)
~$generator_unused_current_refresh(S_call, S_call, n_upper)
$generator_unused_current_refresh(S_updated, S_updated, n_upper)
S_plain = $generator_operate_plain(S_updated, pgeneratorop)
S_plain = S_updated[.RESULT = KNOWN (PARRAY n_array)]
$heap_owners($heap_graph(S_plain), HARRAY n_array) = 2
S_raw = $generator_operate(S_call, pgeneratorop)
S_raw.COMPLETION = NORMAL
S_raw.OBJECTS = S_updated.OBJECTS
S_raw.STORE = S.STORE
S_raw.ARRAYS = S.ARRAYS
S_raw.ALLOCATIONS = S.ALLOCATIONS
S_raw.TODO = ptask_tail*
pnode_inputs* = $eager_slots(S, S_raw)
pnode_inputs* = [HOBJECT n_child, HOBJECT n_upper]
pnode_order* = $eager_owner_order(S)
(S_prepared, OBSERVED_OWNER_ORDER pnode_order*) = $destruction_transition_owners(S, S_raw)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$call_descriptors_valid(S_prepared)
$heap_valid($heap_graph(S_prepared))
""")
REFUSALS = checks(r"""
S_key_heap = $generator_set(S, n_child, pgenerator_child[.KEY = (POBJECT n_old)])
$heap_valid($heap_graph(S_key_heap))
S_key = S_key_heap[.TODO = ptask_tail*]
$node_children(S_key, HOBJECT n_child) = [HCELL n_row, HOBJECT n_old]
S_key_updated = $generator_from_update(S_key, pgeneratorop)
$generator_nodefree_ancestor_leaf(S_key_updated, n_upper) = (n_middle)
$eager_slots(S_key, S_key_updated) = [HOBJECT n_child]
~$generator_unused_current_refresh(S_key, S_key_updated, n_upper)
S_key_plain = $generator_operate_plain(S_key_updated, pgeneratorop)
$generator_unused_current_result(S_key, S_key_plain, pgeneratorop) = S_key_plain
S_return_heap = $generator_set(S, n_child, pgenerator_child[.RETURN = (POBJECT n_old)])
$heap_valid($heap_graph(S_return_heap))
S_return = S_return_heap[.TODO = ptask_tail*]
S_return_updated = $generator_from_update(S_return, pgeneratorop)
$generator_nodefree_ancestor_leaf(S_return_updated, n_upper) = eps
~$generator_unused_current_refresh(S_return, S_return_updated, n_upper)
S_closure_heap = $generator_set(S, n_child, pgenerator_child[.CLOSURE = (n_old)])
$heap_valid($heap_graph(S_closure_heap))
S_closure = S_closure_heap[.TODO = ptask_tail*]
$node_children(S_closure, HOBJECT n_child) = [HCELL n_row, HOBJECT n_old]
S_closure_updated = $generator_from_update(S_closure, pgeneratorop)
$generator_nodefree_ancestor_leaf(S_closure_updated, n_upper) = (n_middle)
~$generator_unused_current_refresh(S_closure, S_closure_updated, n_upper)
S_absent = S_call[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_child)]
S_absent_updated = $generator_from_update(S_absent, pgeneratorop)
~$generator_unused_current_refresh(S_absent, S_absent_updated, n_upper)
S_badupdate = S_updated[.CONSTCONTEXT = true]
$heap_graph(S_badupdate) = $heap_graph(S_updated)
$generator_nodefree_ancestor_leaf(S_badupdate, n_upper) = (n_middle)
~$generator_unused_current_refresh(S_call, S_badupdate, n_upper)
S_badupdate_plain = $generator_operate_plain(S_badupdate, pgeneratorop)
$generator_unused_current_result(S_call, S_badupdate_plain, pgeneratorop) = S_badupdate_plain
$generator_unused_current_result(S_call, S_plain[.RESULT = KNOWN (POBJECT n_upper)], pgeneratorop) = S_plain[.RESULT = KNOWN (POBJECT n_upper)]
$generator_unused_current_result(S_call, S_plain[.COMPLETION = BUDGET], pgeneratorop) = S_plain[.COMPLETION = BUDGET]
""")
BUDGET_DONE = checks(r"""
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.EVENTS = S.EVENTS
S_one.OBJECTS = S_updated.OBJECTS
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_VALUE (HOBJECT n_upper)]
pdestructionoperation.SOURCE = ptask_source
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1
$heap_owners($heap_graph(S_one), HCELL n_row) = 3
$destructor_release_valid(S_one, pdestructionrelease)
$destructor_operation_valid(S_one, pdestructionoperation)
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_two = S_two_budget[.COMPLETION = NORMAL]
S_two.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: (DESTRUCTOR_RELEASE pdestructionrelease_rest) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease_rest = pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]]
pgenstorage.OBJECT = n_child
pgenstorage.NEXT = 0
$generator_storage_for(S_two, n_child) = (pgenstorage)
$generator_storage_valid(S_two, pgenstorage)
$heap_owners($heap_graph(S_two), HOBJECT n_child) = 1
$heap_owners($heap_graph(S_two), HOBJECT n_upper) = 1
$heap_owners($heap_graph(S_two), HCELL n_row) = 3
$call_descriptors_valid(S_two)
$heap_valid($heap_graph(S_two))
S_done = $drive(S_one, 4000)
$drive(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
S_done.GENERATORRETURNRETAINED = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HARRAY n_array) <- S_done.ALLOCATIONS)
~((HCELL n_row) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
""")
CASES = {
    'refresh-unused-current-authenticates-child-before-receiver': {
        'source': ROWS[UNUSED]['source'], 'stage': STAGE,
        'checks': [*COMMON, *REFUSALS, *checks(r"""
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
S_raw.RESULT = KNOWN PNULL
S_raw = $generator_unused_current_result(S_call, S_plain, pgeneratorop)
$heap_owners($heap_graph(S_raw), HARRAY n_array) = 1
"""), *BUDGET_DONE, *checks(r"""
pdestructionoperation.VALUE = KNOWN PNULL
$heap_owners($heap_graph(S_one), HARRAY n_array) = 1
"""), events('S', PREFIX), events('S_done', EVENTS[UNUSED])],
    },
    'refresh-assigned-current-keeps-copy-through-child-prefix': {
        'source': ROWS[USED]['source'], 'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
$reference_call_used(S, pgeneratorop.SITE)
~$destructor_return_discarded(ptask_tail*)
S_raw = S_plain
S_raw.RESULT = KNOWN (PARRAY n_array)
$heap_owners($heap_graph(S_raw), HARRAY n_array) = 2
$generator_unused_current_result(S_call, S_plain, pgeneratorop) = S_plain
S_forged = S_call[.TODO = [DISCARD]]
S_forged_updated = $generator_from_update(S_forged, pgeneratorop)
$reference_call_used(S_forged, pgeneratorop.SITE)
$destructor_return_discarded(S_forged.TODO)
S_forged_plain = $generator_operate_plain(S_forged_updated, pgeneratorop)
$generator_unused_current_result(S_forged, S_forged_plain, pgeneratorop) = S_forged_plain
"""), *BUDGET_DONE, *checks(r"""
pdestructionoperation.VALUE = KNOWN (PARRAY n_array)
$heap_owners($heap_graph(S_one), HARRAY n_array) = 2
"""), events('S', PREFIX), events('S_done', EVENTS[USED])],
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(b).hexdigest() for p, b in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
