#!/usr/bin/env python3
"""Reach one-ancestor node-free SEND argument COW and live physical finally cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_nodefree_ancestor_send_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
ROW = 'review-nodefree-ancestor-send-refreshed-argument-row-cow'
THROWING = 'review-nodefree-ancestor-send-physical-init-next-cache-throw'
PREFIX_ROW = ['P|', 'O|', 'U|', 'M|', 'C0|', 'L|', 'H|', 'G|', 'S|',
              'ARG|', 'MUTATED|', 'F|']
PREFIX_OBJECT = ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'INIT|', 'S|',
                 'ARG|', 'F|']
EVENTS = {
    ROW: PREFIX_ROW + ['ARG-END|', 'A|', 'K|', 'C|', 'K-END|', 'CALLER|', 'N|', 'ROW-DROPPED|', 'E'],
    THROWING: PREFIX_OBJECT + ['ARG-END|', 'J|', 'D|', 'K|', 'CALLER|', '1', '|', '1', '|', '1', '|', 'E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


CASES = {
    'nodefree-ancestor-send-snapshot-survives-argument-cow-before-upper-finally': {
        'source': ROWS[ROW]['source'],
        'stage': ('S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.RECEIVER = (n_argument) '
                  '-- if $object_name(S, n_argument) = $ptascii("NodefreeAncestorSendRowArgument47") '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("ARG-END|"))'),
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
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_snapshot_array), DESTRUCTION_VALUE (HOBJECT n_upper)]
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_caller_tail*)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_current_array)
n_row <- S.REFCELLS
n_current_array =/= n_snapshot_array
S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_cache))]
S.ARRAYS[n_snapshot_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_cache) = $ptascii("NodefreeAncestorSendRowNew47")
$object_name(S, n_old) = $ptascii("NodefreeAncestorSendRowOld47")
$node_children(S, HCELL n_row) = [HARRAY n_current_array]
$node_children(S, HARRAY n_current_array) = [HOBJECT n_cache]
$node_children(S, HARRAY n_snapshot_array) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HARRAY n_current_array) = 1
$heap_count(HARRAY n_current_array, $machine_roots(S)) = 0
$heap_owners($heap_graph(S), HARRAY n_snapshot_array) = 1
$heap_count(HARRAY n_snapshot_array, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 2
~(n_cache <- S.DESTRUCTION.CALLED)
~(n_old <- S.DESTRUCTION.CALLED)
n_argument <- S.DESTRUCTION.CALLED
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
pframe_upper.HELD = eps
$tasks_nodes(pframe_upper.TODO) = eps
$generator_from_record_valid(S, n_upper, pgenerator_upper)
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
n_upper =/= n_middle
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.FRAME = (pframe_middle)
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_row)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle porigin_complete n_child PNULL) :: ptask_middle_tail*
$generator_from_complete_valid(S, n_middle, porigin_complete, n_child, PNULL)
~((HOBJECT n_child) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$generator_nodefree_return_waiting(S, n_middle)
~$generator_nodefree_return_waiting(S, n_upper)
~$generator_return_waiting(S, n_middle)
~$generator_return_parked_waiting(S, n_middle)
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
S_done.GENERATORRETURNRETAINED = eps
$heap_owners($heap_graph(S_done), HARRAY n_current_array) = 0
$heap_owners($heap_graph(S_done), HARRAY n_snapshot_array) = 0
$heap_owners($heap_graph(S_done), HCELL n_row) = 0
~((HARRAY n_current_array) <- S_done.ALLOCATIONS)
~((HARRAY n_snapshot_array) <- S_done.ALLOCATIONS)
~((HCELL n_row) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
n_cache <- S_done.DESTRUCTION.CALLED
"""), events('S', PREFIX_ROW), events('S_one', PREFIX_ROW + ['ARG-END|']), events('S_done', EVENTS[ROW])],
    },
    'nodefree-ancestor-send-first-physical-next-cache-throws-before-upper-finally': {
        'source': ROWS[THROWING]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("NodefreeAncestorSendObjectCache47")'),
        'checks': [*checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
S.GENERATORRETURNRETAINED = eps
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
pdestructionoperation_send.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])
n_argument =/= n_cache
n_argument <- S.DESTRUCTION.CALLED
~((HOBJECT n_argument) <- S.ALLOCATIONS)
pgeneratorop.NAME = "send"
pgeneratorop.LINE = 12
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
~pgeneratorop.ADVANCE
n_upper = pgeneratorop.OBJECT
pdestructionoperation_send.VALUE = KNOWN PNULL
pdestructionoperation_send.PENDING = eps
pdestructionoperation_send.CALLER = eps
pdestructionoperation_send.COMPLETION = NORMAL
~$reference_call_used(S, pgeneratorop.SITE)
pframe_root.CONTEXT = eps
pframe_root.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_root_tail*
n_middle = pgenclose.OBJECT
n_middle =/= n_upper
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
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_CLOSING
~pgenerator_upper.PENDING_INIT
pgenerator_upper.FRAME = eps
$generator_return_closing(S, n_upper)
$generator_close_claims(ptask_root_tail*) = [n_upper]
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
pgenclose.CONTEXT = pcallcontext_middle
pgenclose.SITE = pgeneratorfrom_middle.SITE
pgenclose.STAGE = CLOSE_BODY porigin_finally
pgenclose.PENDING = eps
$generator_return_closing(S, n_middle)
S_finally = $constant_frame_scope(S, pframe_finally, [pframe_root])
$generator_close_saved(S_finally, S_finally.CURRENT, S_finally.FRAMES) = (pgenclose)
$generator_close_active(S_finally)
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
S_badphase = $generator_set(S_finally, n_middle, pgenerator_middle[.PHASE = GENERATOR_DELEGATING])
$heap_graph(S_badphase) = $heap_graph(S_finally)
~$generator_close_active(S_badphase)
~$call_descriptors_valid(S_badphase)
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
S_done.GENERATORRETURNRETAINED = eps
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
$heap_owners($heap_graph(S_done), HCELL n_slot) = 0
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
n_cache <- S_done.DESTRUCTION.CALLED
"""), events('S', PREFIX_OBJECT + ['ARG-END|', 'J|']), events('S_done', EVENTS[THROWING])],
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
