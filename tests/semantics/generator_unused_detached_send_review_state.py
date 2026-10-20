#!/usr/bin/env python3
"""Reach normal pending SEND snapshots across argument COW and cache cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_unused_detached_send_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
COW = 'review-unused-detached-send-argument-cow'
THROWING = 'review-unused-detached-send-alias-cache-throw'
EVENTS = {
    COW: ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'G|', 'S|',
          'ARG|', 'REBIND|', 'F|', 'ARG-END|', 'A|', 'K|', 'CALLER|',
          'C-LIVE|', 'ROW-DROPPED|', 'E', 'R|'],
    THROWING: ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'G|', 'S|',
               'TAKE|', 'F|', 'CLEARED|', 'D|', 'K|', 'CALLER|',
               '1', '|', '1', '|', '1', '|', 'E', 'R|'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


CASES = {
    'normal-unused-send-row-snapshot-survives-argument-cow': {
        'source': ROWS[COW]['source'],
        'stage': 'S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_argument) -- if $object_name(S, n_argument) = $ptascii("UnusedDetachedSendRowArgument41") -- if S.RESULT = KNOWN pvalue_text -- if $string_bytes(pvalue_text) = ($ptascii("ARG-END|"))',
        'checks': [*checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
S.FRAMES = [pframe_caller]
pframe_caller.CONTEXT = eps
pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_caller_tail*
pdestructorcall.OBJECT = n_argument
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructorcall.PENDING = eps
pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])
pgeneratorop.NAME = "send"
pgeneratorop.LINE = 14
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
n_upper = pgeneratorop.OBJECT
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.PENDING = eps
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.CALLER = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_old_row), DESTRUCTION_VALUE (HOBJECT n_upper)]
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_caller_tail*)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_live_row)
n_row <- S.REFCELLS
n_live_row =/= n_old_row
S.ARRAYS[n_live_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_live))]
S.ARRAYS[n_old_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_live) = $ptascii("UnusedDetachedSendRowLive41")
$object_name(S, n_old) = $ptascii("UnusedDetachedSendRowOld41")
$node_children(S, HCELL n_row) = [HARRAY n_live_row]
$node_children(S, HARRAY n_live_row) = [HOBJECT n_live]
$node_children(S, HARRAY n_old_row) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HARRAY n_old_row) = 1
$heap_count(HARRAY n_old_row, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HARRAY n_live_row) = 1
$heap_count(HARRAY n_live_row, $machine_roots(S)) = 0
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_live) = 1
~(n_old <- S.DESTRUCTION.CALLED)
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_DELEGATING
~pgenerator_upper.PENDING_INIT
pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)
pgeneratorfrom_upper.INPUT = (POBJECT n_middle)
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.FRAME = (pframe_middle)
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.CURRENT = (REFERENCE n_row)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle porigin_complete n_child (PARRAY n_return_array)) :: ptask_middle_tail*
ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_complete n_child (PARRAY n_return_array)
n_return_array =/= n_old_row
n_return_array =/= n_live_row
S.ARRAYS[n_return_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]
$object_name(S, n_return) = $ptascii("UnusedDetachedSendRowReturn41")
$heap_owners($heap_graph(S), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S), HOBJECT n_return) = 1
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$generator_return_waiting(S, n_middle)
~$generator_return_parked_waiting(S, n_middle)
$generator_parked_valid(S, pgenerator_middle)
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$destructor_operation_live(S, pdestructionoperation)
~$destructor_operation_valid(S, pdestructionoperation)
$destructor_call_live(S, pdestructorcall)
$destructor_context_valid(S, pcallcontext)
S_caller = $constant_frame_scope(S, pframe_caller, eps)
$destructor_release_valid(S_caller, pdestructionrelease)
$destructor_operation_valid(S_caller, pdestructionoperation)
pdestructionoperation_bad = pdestructionoperation[.SOURCE = DESTRUCTOR_GLOBALS]
S_bad = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]]
$heap_graph(S_bad) = $heap_graph(S)
~$destructor_operation_live(S_bad, pdestructionoperation_bad)
~$call_descriptors_valid(S_bad)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$heap_graph(S_one) = $heap_graph(S)
S_one.FRAMES = S.FRAMES
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_done = $drive(S_one, 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.GENERATORRETURNRETAINED = [ptask_complete]
$generator_return_retained_valid(S_done, S_done.GENERATORRETURNRETAINED)
$heap_owners($heap_graph(S_done), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1
$heap_owners($heap_graph(S_done), HARRAY n_old_row) = 0
$heap_owners($heap_graph(S_done), HARRAY n_live_row) = 0
~((HARRAY n_old_row) <- S_done.ALLOCATIONS)
~((HARRAY n_live_row) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
n_live <- S_done.DESTRUCTION.CALLED
n_return <- S_done.DESTRUCTION.CALLED
"""), events('S', EVENTS[COW][:12]),
            events('S_one', EVENTS[COW][:13]), events('S_done', EVENTS[COW])],
    },
    'normal-unused-send-alias-cache-throws-before-ancestor-finally': {
        'source': ROWS[THROWING]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) -- if $object_name(S, n_cache) = $ptascii("UnusedDetachedSendAliasCache41") -- if S.FRAMES = pframe_caller :: pframe_tail* -- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* -- if pdestructorcall.OPERATION = (pdestructionoperation) -- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_cache)]) -- if pgeneratorop.NAME = "send"',
        'checks': [*checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
S.GENERATORLOOPRETAINED = eps
S.GENERATORRETURNRETAINED = [ptask_complete]
ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_complete n_child (PARRAY n_return_array)
S.ARRAYS[n_return_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]
$object_name(S, n_return) = $ptascii("UnusedDetachedSendAliasReturn41")
$generator_return_retained_record(S, ptask_complete)
$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)
$heap_count(HARRAY n_return_array, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S), HOBJECT n_return) = 1
~(n_return <- S.DESTRUCTION.CALLED)
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_CLOSED
pgenerator_middle.FRAME = eps
pgenerator_middle.PARKED = eps
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_CLOSED
~((HOBJECT n_child) <- S.ALLOCATIONS)
[pgenstorage] = $generator_storage_tasks(S.TODO) ++ $generator_storage_frames(S.FRAMES)
pgenstorage.OBJECT = n_middle
pgenstorage.NEXT = 2
pgenstorage.USER
$generator_storage_for(S, n_middle) = (pgenstorage)
$generator_storage_basic(S, pgenstorage)
(HOBJECT n_middle) <- S.ALLOCATIONS
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$node_children(S, HOBJECT n_middle) = eps
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.CURRENT = (KNOWN (POBJECT n_cache))
pgeneratorop.LINE = 13
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
n_upper = pgeneratorop.OBJECT
n_upper =/= n_middle
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_CLOSING
pgenerator_upper.FRAME = eps
$generator_return_closing(S, n_upper)
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.PENDING = eps
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.CALLER = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
pdestructorcall.OBJECT = n_cache
pdestructorcall.PENDING = eps
pdestructorcall.CALLER = eps
pframe_caller.CONTEXT = eps
(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- pframe_caller.TODO
$heap_owners($heap_graph(S), HOBJECT n_cache) = 2
$destructor_operation_live(S, pdestructionoperation)
~$destructor_operation_valid(S, pdestructionoperation)
$destructor_call_live(S, pdestructorcall)
$destructor_context_valid(S, pcallcontext)
S_caller = $constant_frame_scope(S, pframe_caller, pframe_tail*)
$generator_storage_tail(pframe_caller.TODO, pgenstorage) = (ptask_storage_tail*)
$generator_storage_parent(S_caller, pgenstorage, ptask_storage_tail*)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])
porigin_complete = PORIGIN n_unit pcpath_complete
porigin_bad = PORIGIN n_unit (pcpath_complete ++ [PCFIELD 999])
S_badreceipt = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_middle porigin_bad n_child (PARRAY n_return_array)]]
$heap_graph(S_badreceipt) = $heap_graph(S)
~$generator_return_retained_valid(S_badreceipt, S_badreceipt.GENERATORRETURNRETAINED)
~$call_descriptors_valid(S_badreceipt)
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
S_done.HELD = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.GENERATORRETURNRETAINED = [ptask_complete]
$generator_return_retained_valid(S_done, S_done.GENERATORRETURNRETAINED)
$heap_owners($heap_graph(S_done), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
n_cache <- S_done.DESTRUCTION.CALLED
n_return <- S_done.DESTRUCTION.CALLED
"""), events('S', EVENTS[THROWING][:12]), events('S_done', EVENTS[THROWING])],
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
