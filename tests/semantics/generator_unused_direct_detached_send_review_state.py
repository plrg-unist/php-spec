#!/usr/bin/env python3
"""Reach direct SEND owner releases and cache cleanup inside forced finally."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_unused_direct_detached_send_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
ROW = 'review-unused-direct-send-array-alias-finally-cow'
THROWING = 'review-unused-direct-send-object-alias-finally-throw'
PREFIX = ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'G|', 'S|',
          'TAKE|', 'F|', 'K|', 'CLEARED|']
EVENTS = {
    ROW: PREFIX + ['J|', 'A|', 'J-END|', 'CALLER|', 'C-LIVE|', 'ROW-DROPPED|', 'E', 'R|'],
    THROWING: PREFIX + ['J|', 'D|', 'CALLER|', '1', '|', '1', '|', '1', '|', 'E', 'R|'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


CASES = {
    'direct-unused-send-releases-both-array-copies-before-finally-write': {
        'source': ROWS[ROW]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (PARRAY n_row_array)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 14'),
        'checks': [*checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.HELD = eps
S.GENERATORINPUTS = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
S.RESULT = KNOWN PNULL
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
~pgeneratorop.ADVANCE
n_middle = pgeneratorop.OBJECT
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_row_cell)
S.STORE[n_row_cell] = DEFINED (PARRAY n_row_array)
n_row_cell <- S.REFCELLS
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PARRAY n_return_array)) :: ptask_used_tail*
ptask_complete = GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PARRAY n_return_array)
$generator_return_waiting(S, n_middle)
~$generator_return_parked_waiting(S, n_middle)
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_CLOSED
~((HOBJECT n_child) <- S.ALLOCATIONS)
S.ARRAYS[n_row_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
S.ARRAYS[n_return_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]
n_row_array =/= n_return_array
$object_name(S, n_old) = $ptascii("UnusedDirectSendRowOld42")
$object_name(S, n_return) = $ptascii("UnusedDirectSendRowReturn42")
$node_children(S, HCELL n_row_cell) = [HARRAY n_row_array]
$node_children(S, HARRAY n_row_array) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$heap_owners($heap_graph(S), HCELL n_row_cell) = 2
$heap_owners($heap_graph(S), HARRAY n_row_array) = 2
$heap_count(HARRAY n_row_array, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S), HOBJECT n_return) = 1
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("row")) = (n_row_cell)
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
ptask_source = GENERATOR_ARGS pgeneratorop eps ([KNOWN (PARRAY n_row_array)])
pgeneratorop_full = pgeneratorop[.ARGUMENTS = [PARRAY n_row_array]]
$generator_pending_detached_send(S, pgeneratorop_full)
~$generator_pending_parked_send(S, pgeneratorop_full)
$generator_pending_return_leaf(S, n_middle, 1) = (n_middle)
$generator_from_refresh(S, n_middle, $(|S.OBJECTS| + 1)) = S
$generator_unused_send_refresh(S, S, pgeneratorop_full, eps)
~$generator_unused_send_refresh(S, S, pgeneratorop_full, [HOBJECT n_child])
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
S_raw = $generator_operate(S[.TODO = ptask_tail*], pgeneratorop_full)
S_raw.COMPLETION = NORMAL
S_raw.RESULT = KNOWN (PARRAY n_row_array)
pnode_inputs* = $eager_slots(S, S_raw)
pnode_inputs* = [HOBJECT n_middle]
$eager_task_inputs(S, ptask_source) = [HARRAY n_row_array, HOBJECT n_middle]
$generator_unused_send_cleanup(S, S_raw, ptask_source, pnode_inputs*)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HARRAY n_row_array, HOBJECT n_middle])
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_child, HOBJECT n_middle])
~$generator_unused_send_cleanup(S, S_raw[.RESULT = KNOWN PNULL], ptask_source, pnode_inputs*)
S_no_discard = S[.TODO = [ptask_source]]
S_no_discard_raw = $generator_operate(S_no_discard[.TODO = eps], pgeneratorop_full)
~$generator_unused_send_cleanup(S_no_discard, S_no_discard_raw, ptask_source, pnode_inputs*)
pnode_order* = $eager_owner_order(S)
(S_prepared, OBSERVED_OWNER_ORDER pnode_order*) = $destruction_transition_owners(S, S_raw)
$call_descriptors_valid(S_prepared)
$heap_valid($heap_graph(S_prepared))
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.EVENTS = S.EVENTS
S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionoperation.SOURCE = ptask_source
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.PENDING = eps
pdestructionoperation.NOGC = eps
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_row_array), DESTRUCTION_VALUE (HARRAY n_row_array), DESTRUCTION_VALUE (HOBJECT n_middle)]
$heap_owners($heap_graph(S_one), HARRAY n_row_array) = 3
$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1
$destructor_release_valid(S_one, pdestructionrelease)
$destructor_operation_valid(S_one, pdestructionoperation)
S_two_budget = $drive_steps(S_one, 1)
S_two = S_two_budget[.COMPLETION = NORMAL]
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
$heap_owners($heap_graph(S_two), HARRAY n_row_array) = 2
S_three_budget = $drive_steps(S_two, 1)
S_three = S_three_budget[.COMPLETION = NORMAL]
S_three.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)]]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
$heap_owners($heap_graph(S_three), HARRAY n_row_array) = 1
$heap_count(HARRAY n_row_array, $machine_roots(S_three)) = 0
$heap_owners($heap_graph(S_three), HOBJECT n_old) = 1
$call_descriptors_valid(S_three)
$heap_valid($heap_graph(S_three))
S_done = $drive(S_three, 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.GENERATORRETURNRETAINED = [ptask_complete]
$generator_return_retained_valid(S_done, S_done.GENERATORRETURNRETAINED)
$heap_owners($heap_graph(S_done), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1
$heap_owners($heap_graph(S_done), HARRAY n_row_array) = 0
$heap_owners($heap_graph(S_done), HCELL n_row_cell) = 0
~((HARRAY n_row_array) <- S_done.ALLOCATIONS)
~((HCELL n_row_cell) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
n_return <- S_done.DESTRUCTION.CALLED
"""), events('S', PREFIX), events('S_done', EVENTS[ROW])],
    },
    'direct-unused-send-cache-throws-from-live-finally-null-store': {
        'source': ROWS[THROWING]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("UnusedDirectSendObjectCache42")'),
        'checks': [*checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
S.GENERATORLOOPRETAINED = eps
S.FRAMES = [pframe_finally, pframe_root]
pframe_finally.CONTEXT = (pcallcontext_middle)
pframe_finally.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_finally_tail*
pdestructorcall.OBJECT = n_cache
pdestructorcall.PENDING = eps
pdestructorcall.OPERATION = (pdestructionoperation_store)
S.DESTRUCTION.OPERATIONS = [pdestructionoperation_store, pdestructionoperation_send]
pdestructionoperation_store.CALLER = (pcallcontext_middle)
pdestructionoperation_store.VALUE = KNOWN PNULL
pdestructionoperation_store.PENDING = eps
pdestructionoperation_store.COMPLETION = NORMAL
pdestructionoperation_store.SOURCE = ptask_store
~$eager_explicit_task(ptask_store)
pdestructionoperation_send.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_cache)])
pgeneratorop.NAME = "send"
pgeneratorop.LINE = 13
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
~pgeneratorop.ADVANCE
n_middle = pgeneratorop.OBJECT
pdestructionoperation_send.VALUE = KNOWN PNULL
pdestructionoperation_send.PENDING = eps
pdestructionoperation_send.CALLER = eps
pdestructionoperation_send.COMPLETION = NORMAL
~$reference_call_used(S, pgeneratorop.SITE)
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_RUNNING
~pgenerator_middle.PENDING_INIT
pgenerator_middle.FRAME = eps
pgenerator_middle.PARKED = eps
pgenerator_middle.FUNCTION = pcallcontext_middle.FUNCTION
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_slot)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("slot")) = (n_slot)
S.STORE[n_slot] = DEFINED PNULL
n_slot <- S.REFCELLS
$node_children(S, HCELL n_slot) = eps
$heap_owners($heap_graph(S), HCELL n_slot) = 2
$heap_owners($heap_graph(S), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$generator_storage_for(S, n_middle) = eps
pframe_root.CONTEXT = eps
pframe_root.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_root_tail*
pgenclose.OBJECT = n_middle
pgenclose.CONTEXT = pcallcontext_middle
pgenclose.STAGE = CLOSE_BODY porigin_finally
pgenclose.PENDING = eps
$generator_return_closing(S, n_middle)
S_finally = $constant_frame_scope(S, pframe_finally, [pframe_root])
$generator_close_saved(S_finally, S_finally.CURRENT, S_finally.FRAMES) = (pgenclose)
$generator_close_active(S_finally)
S.GENERATORRETURNRETAINED = [ptask_complete]
ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_complete n_child (PARRAY n_return_array)
pgenclose.SITE = porigin_complete
$generator_return_retained_record(S, ptask_complete)
$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)
S.ARRAYS[n_return_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]
$object_name(S, n_return) = $ptascii("UnusedDirectSendObjectReturn42")
$heap_owners($heap_graph(S), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S), HOBJECT n_return) = 1
~(n_return <- S.DESTRUCTION.CALLED)
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$destructor_operation_live(S, pdestructionoperation_store)
~$destructor_operation_valid(S, pdestructionoperation_store)
$destructor_operation_valid(S_finally, pdestructionoperation_store)
$destructor_operation_live(S, pdestructionoperation_send)
$destructor_call_live(S, pdestructorcall)
$destructor_context_valid(S, pcallcontext)
pdestructionoperation_bad = pdestructionoperation_store[.SOURCE = DESTRUCTOR_GLOBALS]
S_bad = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad, pdestructionoperation_send]]
$heap_graph(S_bad) = $heap_graph(S)
~$destructor_operation_live(S_bad, pdestructionoperation_bad)
~$call_descriptors_valid(S_bad)
S_badphase = $generator_set(S, n_middle, pgenerator_middle[.PHASE = GENERATOR_DELEGATING])
$heap_graph(S_badphase) = $heap_graph(S)
~$generator_return_retained_record(S_badphase, ptask_complete)
~$call_descriptors_valid(S_badphase)
~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_done = $drive(S_one, 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.GENERATORRETURNRETAINED = [ptask_complete]
$generator_return_retained_valid(S_done, S_done.GENERATORRETURNRETAINED)
$heap_owners($heap_graph(S_done), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
n_cache <- S_done.DESTRUCTION.CALLED
n_return <- S_done.DESTRUCTION.CALLED
"""), events('S', PREFIX + ['J|']), events('S_done', EVENTS[THROWING])],
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
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest() for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
