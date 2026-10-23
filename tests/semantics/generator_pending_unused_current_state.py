#!/usr/bin/env python3
"""Reach pending-receiver CURRENT copies before real receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_unused_current_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
UNUSED = 'generator-pending-unused-current-row-finally-write'
USED = 'generator-pending-unused-current-assignment-control'
PREFIX = ['P|', 'O|', 'U|', 'M|', 'C0|', 'L|', 'H|', 'REFRESH|', 'INIT-M|', 'S|', 'TAKE|', 'F|', 'CLEARED|']
EVENTS = {
    UNUSED: PREFIX + ['J|', 'A|', 'J-END|', 'K|', 'CALLER|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
    USED: PREFIX + ['J|', 'J-END|', 'K|', 'CALLER|', 'A|', 'DROPPED|', 'C-LIVE|', 'ROW-DROPPED|', 'E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
         '-- if pgeneratorop.NAME = "current" -- if pgeneratorop.LINE = 14')
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
n_upper =/= n_middle
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
~pgenerator_middle.PENDING_INIT
pgenerator_middle.PARKED = eps
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_row)
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child PNULL) :: ptask_middle_tail*
~((HOBJECT n_child) <- S.ALLOCATIONS)
$generator_nodefree_return_waiting(S, n_middle)
$generator_nodefree_ancestor_leaf(S, n_upper) = (n_middle)
$generator_nodefree_ancestor_leaf(S, n_middle) = eps
~$generator_pending_resume(S, pgeneratorop)
$generator_operation_valid(S, pgeneratorop)
$getter_arguments(S, pgeneratorop.SITE) = PCALLARGUMENTS eps 2
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_array)
n_row <- S.REFCELLS
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_old) = $ptascii("PendingUnusedCurrentRowOld51")
$node_children(S, HCELL n_row) = [HARRAY n_array]
$node_children(S, HARRAY n_array) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
~(n_old <- S.DESTRUCTION.CALLED)
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$heap_owners($heap_graph(S), HARRAY n_array) = 1
$heap_count(HARRAY n_array, $machine_roots(S)) = 0
ptask_source = GENERATOR_ARGS pgeneratorop eps eps
S_call = S[.TODO = ptask_tail*]
$generator_from_refresh(S_call, n_upper, $(|S.OBJECTS| + 1)) = S_call
$generator_from_update(S_call, pgeneratorop) = S_call
S_plain = $generator_operate_plain(S_call, pgeneratorop)
S_plain = S_call[.RESULT = KNOWN (PARRAY n_array)]
$heap_owners($heap_graph(S_plain), HARRAY n_array) = 2
S_raw = $generator_operate(S_call, pgeneratorop)
S_raw.COMPLETION = NORMAL
S_raw.OBJECTS = S.OBJECTS
S_raw.STORE = S.STORE
S_raw.ARRAYS = S.ARRAYS
S_raw.ALLOCATIONS = S.ALLOCATIONS
S_raw.TODO = ptask_tail*
pnode_inputs* = $eager_slots(S, S_raw)
pnode_inputs* = [HOBJECT n_upper]
pnode_order* = $eager_owner_order(S)
(S_prepared, OBSERVED_OWNER_ORDER pnode_order*) = $destruction_transition_owners(S, S_raw)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$call_descriptors_valid(S_prepared)
$heap_valid($heap_graph(S_prepared))
""")
BUDGET = checks(r"""
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.EVENTS = S.EVENTS
S_one.OBJECTS = S.OBJECTS
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]
pdestructionoperation.SOURCE = ptask_source
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$destructor_release_valid(S_one, pdestructionrelease)
$destructor_operation_valid(S_one, pdestructionoperation)
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
""")
DONE = checks(r"""
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
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HARRAY n_array) <- S_done.ALLOCATIONS)
~((HCELL n_row) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
""")
CASES = {
    'pending-unused-current-discards-before-receiver-with-bits-preserved': {
        'source': ROWS[UNUSED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
S_raw.RESULT = KNOWN PNULL
S_raw = $generator_unused_current_result(S_call, S_plain, pgeneratorop)
$heap_owners($heap_graph(S_raw), HARRAY n_array) = 1
$generator_unused_current_result(S_call, S_plain[.RESULT = KNOWN PNULL], pgeneratorop) = S_plain[.RESULT = KNOWN PNULL]
$generator_unused_current_result(S_call, S_plain[.RESULT = KNOWN (POBJECT n_upper)], pgeneratorop) = S_plain[.RESULT = KNOWN (POBJECT n_upper)]
$generator_unused_current_result(S_call, S_plain[.COMPLETION = BUDGET], pgeneratorop) = S_plain[.COMPLETION = BUDGET]
S_no_tail = S_call[.TODO = eps]
S_no_tail_plain = $generator_operate_plain(S_no_tail, pgeneratorop)
$generator_unused_current_result(S_no_tail, S_no_tail_plain, pgeneratorop) = S_no_tail_plain
S_no_tail_plain.RESULT = KNOWN (PARRAY n_array)
S_cleared = $generator_set(S_call, n_upper, pgenerator_upper[.PENDING_INIT = false])
S_cleared_plain = $generator_operate_plain(S_cleared, pgeneratorop)
$heap_graph(S_cleared) = $heap_graph(S_call)
$generator_unused_current_result(S_cleared, S_cleared_plain, pgeneratorop) = S_cleared_plain[.RESULT = KNOWN PNULL]
S_cleared_plain.RESULT = KNOWN (PARRAY n_array)
S_held = $generator_set(S_call, n_upper, pgenerator_upper[.FRAME = (pframe_upper[.HELD = [HARRAY n_array]])])
S_held_plain = $generator_operate_plain(S_held, pgeneratorop)
$generator_nodefree_ancestor_leaf(S_held, n_upper) = eps
$generator_unused_current_result(S_held, S_held_plain, pgeneratorop) = S_held_plain
$generator_unused_current_result(S_call, S_plain, pgeneratorop[.ADVANCE = true]) = S_plain
$generator_unused_current_result(S_call, S_plain, pgeneratorop[.STARTPACK = true]) = S_plain
$generator_unused_current_result(S_call, S_plain, pgeneratorop[.BORROWED = true]) = S_plain
$generator_unused_current_result(S_call, S_plain, pgeneratorop[.ARGUMENTS = [PNULL]]) = S_plain
$generator_unused_current_result(S_call, S_plain, pgeneratorop[.SITE = pgeneratorfrom_upper.SITE]) = S_plain
"""), *BUDGET, *checks(r"""
pdestructionoperation.VALUE = KNOWN PNULL
$heap_owners($heap_graph(S_one), HARRAY n_array) = 1
"""), *DONE, events('S', PREFIX), events('S_done', EVENTS[UNUSED])],
    },
    'pending-assigned-current-retains-row-through-finally': {
        'source': ROWS[USED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
$reference_call_used(S, pgeneratorop.SITE)
~$destructor_return_discarded(ptask_tail*)
S_raw = S_plain
S_raw.RESULT = KNOWN (PARRAY n_array)
$heap_owners($heap_graph(S_raw), HARRAY n_array) = 2
$generator_unused_current_result(S_call, S_plain, pgeneratorop) = S_plain
S_forged = S_call[.TODO = [DISCARD]]
$reference_call_used(S_forged, pgeneratorop.SITE)
$destructor_return_discarded(S_forged.TODO)
S_forged_plain = $generator_operate_plain(S_forged, pgeneratorop)
S_forged_plain.RESULT = KNOWN (PARRAY n_array)
$generator_unused_current_result(S_forged, S_forged_plain, pgeneratorop) = S_forged_plain
$generator_operate(S_forged, pgeneratorop) = S_forged_plain
"""), *BUDGET, *checks(r"""
pdestructionoperation.VALUE = KNOWN (PARRAY n_array)
$heap_owners($heap_graph(S_one), HARRAY n_array) = 2
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
