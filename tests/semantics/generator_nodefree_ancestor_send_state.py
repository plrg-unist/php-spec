#!/usr/bin/env python3
"""Reach one-ancestor node-free SEND refresh and distinct unused/assigned snapshots."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_nodefree_ancestor_send_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
UNUSED = 'generator-nodefree-ancestor-send-finally-row-write'
USED = 'generator-nodefree-ancestor-send-assignment-control'
PREFIX = ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'S|']
EVENTS = {
    UNUSED: PREFIX + ['ARG|', 'F|', 'ARG-END|', 'K|', 'A|', 'K-END|', 'CALLER|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
    USED: PREFIX + ['ARG|', 'F|', 'ARG-END|', 'K|', 'K-END|', 'CALLER|', 'A|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* '
         '-- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 12')
COMMON = checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.COMPLETION = NORMAL
S.GC.ACTIVE = eps
S.HELD = eps
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
pgenerator_upper.PENDING_INIT
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
$generator_from_record_valid(S, n_upper, pgenerator_upper)
n_upper =/= n_middle
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = (POBJECT n_child)
pgeneratorfrom_middle.CURRENT = eps
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_NEXT n_middle pgeneratorfrom_middle.SITE) :: ptask_used_tail*
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_CLOSED
pgenerator_child.FRAME = eps
pgenerator_child.REFCELL = (n_row)
pgenerator_child.RETURN = (PINT 0)
(HOBJECT n_child) <- S.ALLOCATIONS
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("child")) = eps
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_old_row)
n_row <- S.REFCELLS
S.ARRAYS[n_old_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_argument) = $ptascii("NodefreeAncestorSendRowArgument47")
$object_name(S, n_old) = $ptascii("NodefreeAncestorSendRowOld47")
$heap_owners($heap_graph(S), HOBJECT n_child) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S), HOBJECT n_upper) = 3
$heap_owners($heap_graph(S), HOBJECT n_middle) = 2
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HARRAY n_old_row) = 1
$heap_count(HARRAY n_old_row, $machine_roots(S)) = 0
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$node_children(S, HARRAY n_old_row) = [HOBJECT n_old]
$generator_pending_return_leaf(S, n_upper, $(|S.OBJECTS| + 1)) = eps
$generator_nodefree_ancestor_leaf(S, n_upper) = eps
~$generator_nodefree_return_waiting(S, n_middle)
ptask_source = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])
pgeneratorop_full = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]
$generator_operation_valid(S, pgeneratorop_full)
$generator_pending_detached_send(S, pgeneratorop_full)
~$generator_pending_parked_send(S, pgeneratorop_full)
S_refreshed = $generator_from_refresh(S, n_upper, $(|S.OBJECTS| + 1))
S_refreshed.STORE = S.STORE
S_refreshed.ARRAYS = S.ARRAYS
S_refreshed.ALLOCATIONS = S.ALLOCATIONS
S_refreshed.TODO = S.TODO
S_refreshed.OBJECTS[n_upper] = GENERATOR pgenerator_upper
S_refreshed.OBJECTS[n_child] = GENERATOR pgenerator_child
S_refreshed.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed
pgenerator_refreshed.PENDING_INIT
pgenerator_refreshed.PARKED = eps
pgenerator_refreshed.DELEGATE = (pgeneratorfrom_refreshed)
pgeneratorfrom_refreshed.INPUT = eps
pgeneratorfrom_refreshed.CURRENT = (REFERENCE n_row)
pgenerator_refreshed.FRAME = (pframe_refreshed)
pframe_refreshed.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 0)) :: ptask_used_tail*
ptask_complete = GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 0)
~$generator_return_waiting(S_refreshed, n_middle)
$generator_pending_return_leaf(S_refreshed, n_upper, $(|S.OBJECTS| + 1)) = eps
$generator_nodefree_return_waiting(S_refreshed, n_middle)
~$generator_nodefree_return_waiting(S_refreshed, n_upper)
$generator_nodefree_ancestor_leaf(S_refreshed, n_upper) = (n_middle)
$generator_nodefree_ancestor_leaf(S_refreshed, n_middle) = eps
$task_nodes(ptask_complete) = eps
S_refreshed.GENERATORRETURNRETAINED = eps
$generator_pending_detached_send(S_refreshed, pgeneratorop_full)
$generator_unused_send_refresh(S_refreshed, S_refreshed, pgeneratorop_full, eps)
~$generator_unused_send_refresh(S_refreshed, S_refreshed, pgeneratorop_full, [HOBJECT n_child])
$heap_owners($heap_graph(S_refreshed), HCELL n_row) = 3
pnode_prefix* = $eager_slots(S, S_refreshed)
pnode_prefix* = [HOBJECT n_child]
$generator_unused_send_refresh(S, S_refreshed, pgeneratorop_full, pnode_prefix*)
~$generator_unused_send_refresh(S, S_refreshed, pgeneratorop_full, eps)
~$generator_unused_send_refresh(S, S_refreshed, pgeneratorop_full, [HOBJECT n_argument])
~$generator_unused_send_refresh(S, S_refreshed, pgeneratorop_full, [HOBJECT n_child, HOBJECT n_child])
~$generator_unused_send_refresh(S, S, pgeneratorop_full, pnode_prefix*)
S_raw = $generator_operate(S[.TODO = ptask_tail*], pgeneratorop_full)
S_raw.COMPLETION = NORMAL
S_raw.RESULT = KNOWN (PARRAY n_old_row)
S_raw.OBJECTS[n_upper] = GENERATOR pgenerator_upper[.PENDING_INIT = false]
S_raw.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed
S_raw.STORE = S.STORE
S_raw.ARRAYS = S.ARRAYS
S_raw.ALLOCATIONS = S.ALLOCATIONS
pnode_inputs* = $eager_slots(S, S_raw)
pnode_inputs* = [HOBJECT n_child, HOBJECT n_argument, HOBJECT n_upper]
$heap_owners($heap_graph(S_raw), HCELL n_row) = 3
$heap_owners($heap_graph(S_raw), HARRAY n_old_row) = 2
$heap_owners($heap_graph(S_raw), HOBJECT n_old) = 1
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
""")
BUDGET = checks(r"""
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.EVENTS = S.EVENTS
S_one.OBJECTS[n_upper] = GENERATOR pgenerator_upper[.PENDING_INIT = false]
S_one.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed
S_one.OBJECTS[n_child] = GENERATOR pgenerator_child
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionoperation.SOURCE = ptask_source
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$destructor_release_valid(S_one, pdestructionrelease)
$destructor_operation_valid(S_one, pdestructionoperation)
$heap_owners($heap_graph(S_one), HARRAY n_old_row) = 2
$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_one), HCELL n_row) = 3
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
""")
DONE = checks(r"""
S_done = $drive(S_one, 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.GENERATORRETURNRETAINED = eps
~$generator_return_retained_record(S_done, ptask_complete)
~((HARRAY n_old_row) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
""")
CASES = {
    'nodefree-ancestor-unused-send-releases-child-before-argument-snapshot-upper': {
        'source': ROWS[UNUSED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
$generator_unused_send_cleanup(S, S_raw, ptask_source, pnode_inputs*)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_upper])
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_upper, HOBJECT n_argument])
~$generator_unused_send_cleanup(S, S_raw[.RESULT = KNOWN PNULL], ptask_source, pnode_inputs*)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_child, HOBJECT n_child, HOBJECT n_argument, HOBJECT n_upper])
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_argument, HOBJECT n_child, HOBJECT n_upper])
$generator_pending_detached_send(S_refreshed[.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed[.PENDING_INIT = false]], pgeneratorop_full)
~$generator_pending_detached_send(S[.OBJECTS[n_child] = GENERATOR pgenerator_child[.PHASE = GENERATOR_PAUSED]], pgeneratorop_full)
~$generator_unused_send_refresh(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_child)], S_refreshed, pgeneratorop_full, [HOBJECT n_child])
~$generator_pending_detached_send(S[.OBJECTS[n_child] = GENERATOR pgenerator_child[.RETURN = eps]], pgeneratorop_full)
S_wrong_complete = $generator_set(S_refreshed, n_middle, pgenerator_refreshed[.FRAME = (pframe_refreshed[.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 9)) :: ptask_used_tail*])])
$generator_nodefree_ancestor_leaf(S_wrong_complete, n_upper) = eps
~$generator_pending_detached_send(S_wrong_complete, pgeneratorop_full)
S_badlink = $generator_set(S_refreshed, n_upper, pgenerator_upper[.DELEGATE = (pgeneratorfrom_upper[.CURRENT = (KNOWN PNULL)])])
$generator_nodefree_ancestor_leaf(S_badlink, n_upper) = eps
~$generator_pending_detached_send(S_badlink, pgeneratorop_full)
S_held = $generator_set(S_refreshed, n_upper, pgenerator_upper[.FRAME = (pframe_upper[.HELD = [HOBJECT n_argument]])])
$generator_nodefree_ancestor_leaf(S_held, n_upper) = eps
~$generator_pending_detached_send(S_held, pgeneratorop_full)
S_cleared = $generator_set(S_refreshed, n_upper, pgenerator_upper[.PENDING_INIT = false])
$heap_graph(S_cleared) = $heap_graph(S_refreshed)
~$generator_pending_detached_send(S_cleared, pgeneratorop_full)
~$generator_pending_detached_send(S, pgeneratorop_full[.SITE = pgeneratorfrom_upper.SITE])
S_no_discard = S[.TODO = [ptask_source]]
S_no_discard_raw = $generator_operate(S_no_discard[.TODO = eps], pgeneratorop_full)
~$generator_unused_send_cleanup(S_no_discard, S_no_discard_raw, ptask_source, pnode_inputs*)
pnode_order* = $eager_owner_order(S)
(S_prepared, OBSERVED_OWNER_ORDER pnode_order*) = $destruction_transition_owners(S, S_raw)
$call_descriptors_valid(S_prepared)
$heap_valid($heap_graph(S_prepared))
"""), *BUDGET, *checks(r"""
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HARRAY n_old_row), DESTRUCTION_VALUE (HOBJECT n_upper)]
pdestructionoperation.VALUE = KNOWN PNULL
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps
"""), *DONE, events('S', PREFIX), events('S_done', EVENTS[UNUSED])],
    },
    'nodefree-ancestor-assigned-send-keeps-copy-after-child-release': {
        'source': ROWS[USED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
$reference_call_used(S, pgeneratorop.SITE)
~$destructor_return_discarded(ptask_tail*)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, pnode_inputs*)
S_forged = S[.TODO = ptask_source :: [DISCARD]]
$reference_call_used(S_forged, pgeneratorop.SITE)
$destructor_return_discarded([DISCARD])
S_forged_raw = $generator_operate(S_forged[.TODO = [DISCARD]], pgeneratorop_full)
~$generator_unused_send_cleanup(S_forged, S_forged_raw, ptask_source, pnode_inputs*)
"""), *BUDGET, *checks(r"""
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_upper)]
pdestructionoperation.VALUE = KNOWN (PARRAY n_old_row)
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HARRAY n_old_row]
"""), *DONE, events('S', PREFIX), events('S_done', EVENTS[USED])],
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
