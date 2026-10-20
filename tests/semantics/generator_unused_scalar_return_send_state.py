#!/usr/bin/env python3
"""Reach unused and assigned SEND snapshots at a node-free copied return."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_unused_scalar_return_send_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
UNUSED = 'generator-unused-scalar-return-send-finally-row-write'
USED = 'generator-unused-scalar-return-send-assignment-control'
PREFIX = ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'G|', 'S|']
EVENTS = {
    UNUSED: PREFIX + ['ARG|', 'F|', 'K|', 'ARG-END|', 'J|', 'A|', 'J-END|', 'CALLER|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
    USED: PREFIX + ['ARG|', 'F|', 'K|', 'ARG-END|', 'J|', 'J-END|', 'CALLER|', 'A|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* '
         '-- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 13')
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
n_middle = pgeneratorop.OBJECT
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_row)
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 0)) :: ptask_used_tail*
ptask_complete = GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 0)
~((HOBJECT n_child) <- S.ALLOCATIONS)
S.STORE[n_row] = DEFINED (PARRAY n_old_row)
n_row <- S.REFCELLS
S.ARRAYS[n_old_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_argument) = $ptascii("UnusedScalarReturnSendRowArgument44")
$object_name(S, n_old) = $ptascii("UnusedScalarReturnSendRowOld44")
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S), HOBJECT n_middle) = 3
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HARRAY n_old_row) = 1
$heap_count(HARRAY n_old_row, $machine_roots(S)) = 0
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$node_children(S, HARRAY n_old_row) = [HOBJECT n_old]
~$generator_return_waiting(S, n_middle)
~$generator_return_parked_waiting(S, n_middle)
$generator_return_site(S, n_middle, pgeneratorfrom_middle.SITE)
$generator_input_tail(S, pgeneratorfrom_middle.SITE, ptask_used_tail*)
$task_nodes(ptask_complete) = eps
~$generator_return_receipt(S, n_middle, pgeneratorfrom_middle.SITE, n_child, PINT 0)
$generator_pending_return_leaf(S, n_middle, 0) = eps
$generator_pending_return_leaf(S, n_middle, 1) = eps
ptask_source = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])
pgeneratorop_full = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]
$generator_pending_detached_send(S, pgeneratorop_full)
~$generator_pending_parked_send(S, pgeneratorop_full)
S_refreshed = $generator_from_refresh(S, n_middle, $(|S.OBJECTS| + 1))
S_refreshed = S
$eager_slots(S, S_refreshed) = eps
$generator_unused_send_refresh(S, S, pgeneratorop_full, eps)
~$generator_unused_send_refresh(S, S, pgeneratorop_full, [HOBJECT n_child])
~$generator_unused_send_refresh(S, S, pgeneratorop_full, [HOBJECT n_argument])
S_raw = $generator_operate(S[.TODO = ptask_tail*], pgeneratorop_full)
S_raw.COMPLETION = NORMAL
S_raw.RESULT = KNOWN (PARRAY n_old_row)
S_raw.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]
S_raw.STORE = S.STORE
S_raw.ARRAYS = S.ARRAYS
S_raw.ALLOCATIONS = S.ALLOCATIONS
pnode_inputs* = $eager_slots(S, S_raw)
pnode_inputs* = [HOBJECT n_argument, HOBJECT n_middle]
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
S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]
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
n_old <- S_done.DESTRUCTION.CALLED
""")
CASES = {
    'scalar-return-unused-send-drops-current-copy-before-finally': {
        'source': ROWS[UNUSED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
$generator_unused_send_cleanup(S, S_raw, ptask_source, pnode_inputs*)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_middle])
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_middle, HOBJECT n_argument])
~$generator_unused_send_cleanup(S, S_raw[.RESULT = KNOWN PNULL], ptask_source, pnode_inputs*)
S_held = S[.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.FRAME = (pframe_middle[.HELD = [HOBJECT n_argument]])]]
~$generator_unused_send_refresh(S_held, S_held, pgeneratorop_full, eps)
S_owned_tail = S[.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.FRAME = (pframe_middle[.TODO = pframe_middle.TODO ++ [ptask_source]])]]
~$generator_unused_send_refresh(S_owned_tail, S_owned_tail, pgeneratorop_full, eps)
S_parked = S[.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PARKED = (pgeneratorop.SITE)]]
~$generator_unused_send_refresh(S_parked, S_parked, pgeneratorop_full, eps)
~$generator_unused_send_refresh(S, S, pgeneratorop_full[.BORROWED = true], eps)
~$generator_unused_send_refresh(S, S, pgeneratorop_full[.STARTPACK = true], eps)
~$generator_unused_send_refresh(S, S, pgeneratorop_full[.NAME = "next"], eps)
S_no_discard = S[.TODO = [ptask_source]]
S_no_discard_raw = $generator_operate(S_no_discard[.TODO = eps], pgeneratorop_full)
~$generator_unused_send_cleanup(S_no_discard, S_no_discard_raw, ptask_source, pnode_inputs*)
pnode_order* = $eager_owner_order(S)
(S_prepared, OBSERVED_OWNER_ORDER pnode_order*) = $destruction_transition_owners(S, S_raw)
$call_descriptors_valid(S_prepared)
$heap_valid($heap_graph(S_prepared))
"""), *BUDGET, *checks(r"""
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HARRAY n_old_row), DESTRUCTION_VALUE (HOBJECT n_middle)]
pdestructionoperation.VALUE = KNOWN PNULL
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps
"""), *DONE, events('S', PREFIX), events('S_done', EVENTS[UNUSED])],
    },
    'scalar-return-assigned-send-keeps-current-copy-through-finally': {
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
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_middle)]
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
