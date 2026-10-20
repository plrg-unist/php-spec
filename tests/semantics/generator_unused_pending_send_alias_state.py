#!/usr/bin/env python3
"""Reach aliased pending SEND argument/result owners and assignment fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_unused_pending_send_alias_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
UNUSED = 'generator-unused-pending-send-alias-object-unused'
USED = 'generator-unused-pending-send-alias-object-assigned'
PREFIX = ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'T|', 'CATCH|', '1', '|', '1', '|', 'S|', 'ARG|', 'F|', 'ARG-END|']
EVENTS = {
    UNUSED: PREFIX + ['D|', 'K|', 'CALLER|', 'DROPPED|', 'E', 'R|'],
    USED: PREFIX + ['K|', 'CALLER|', 'D|', 'DROPPED|', 'E', 'R|'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* '
         '-- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 13')
COMMON = checks(r'''
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
n_upper = pgeneratorop.OBJECT
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PENDING_INIT
pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)
pgeneratorfrom_upper.INPUT = (POBJECT n_middle)
n_upper =/= n_middle
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
~pgenerator_middle.PENDING_INIT
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (KNOWN (POBJECT n_cache))
n_argument = n_cache
pgenerator_middle.PARKED = (pgeneratorfrom_middle.SITE)
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PARRAY n_return_array)) :: ptask_used_tail*
ptask_complete = GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PARRAY n_return_array)
$generator_return_parked_waiting(S, n_middle)
S.ARRAYS[n_return_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]
$object_name(S, n_cache) = $ptascii("UnusedPendingSendAliasCache40")
$object_name(S, n_return) = $ptascii("UnusedPendingSendAliasReturn40")
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S), HOBJECT n_return) = 1
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
ptask_source = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])
pgeneratorop_full = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]
$generator_pending_parked_send(S, pgeneratorop_full)
S_raw = $generator_operate(S[.TODO = ptask_tail*], pgeneratorop_full)
S_raw.COMPLETION = NORMAL
S_raw.RESULT = KNOWN (POBJECT n_cache)
pnode_inputs* = $eager_slots(S, S_raw)
pnode_inputs* = [HOBJECT n_upper]
$eager_operation_destination(S, S_raw) = S_raw
''')
BUDGET = checks(r'''
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.EVENTS = S.EVENTS
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_one.OBJECTS[n_upper] = GENERATOR pgenerator_upper[.PENDING_INIT = false]
S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.GENERATORRETURNRETAINED = eps
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionoperation.SOURCE = ptask_source
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$destructor_release_valid(S_one, pdestructionrelease)
$destructor_operation_valid(S_one, pdestructionoperation)
$heap_owners($heap_graph(S_one), HOBJECT n_upper) = 1
''')
DONE = checks(r'''
S_done = $drive(S_one, 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
S_done.GENERATORRETURNRETAINED = [ptask_complete]
$generator_return_retained_record(S_done, ptask_complete)
$heap_owners($heap_graph(S_done), HARRAY n_return_array) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
~((HOBJECT n_cache) <- S_done.ALLOCATIONS)
n_cache <- S_done.DESTRUCTION.CALLED
n_return <- S_done.DESTRUCTION.CALLED
''')
CASES = {
    'unused-send-alias-restores-two-real-cache-release-owners': {
        'source': ROWS[UNUSED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r'''
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
$generator_unused_send_cleanup(S, S_raw, ptask_source, pnode_inputs*)
pnode_order* = $eager_owner_order(S)
(S_prepared, OBSERVED_OWNER_ORDER pnode_order*) = $destruction_transition_owners(S, S_raw)
$call_descriptors_valid(S_prepared)
$heap_valid($heap_graph(S_prepared))
~$generator_unused_send_cleanup(S, S_raw, ptask_source, eps)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_cache, HOBJECT n_upper])
~$generator_unused_send_cleanup(S, S_raw, ptask_source, [HOBJECT n_upper, HOBJECT n_upper])
~$generator_unused_send_cleanup(S, S_raw[.RESULT = KNOWN PNULL], ptask_source, pnode_inputs*)
~$generator_unused_send_cleanup(S, S_raw[.RESULT = KNOWN (POBJECT n_return)], ptask_source, pnode_inputs*)
S_no_discard = S[.TODO = [ptask_source]]
S_no_discard_raw = $generator_operate(S_no_discard[.TODO = eps], pgeneratorop_full)
~$generator_unused_send_cleanup(S_no_discard, S_no_discard_raw, ptask_source, pnode_inputs*)
'''), *BUDGET, *checks(r'''
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_cache), DESTRUCTION_VALUE (HOBJECT n_cache), DESTRUCTION_VALUE (HOBJECT n_upper)]
pdestructionoperation.VALUE = KNOWN PNULL
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps
$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 3
S_two = S_two_budget[.COMPLETION = NORMAL]
S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_cache), DESTRUCTION_VALUE (HOBJECT n_upper)]]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
$heap_owners($heap_graph(S_two), HOBJECT n_cache) = 2
~(n_cache <- S_two.DESTRUCTION.CALLED)
S_two.OBJECTS[n_middle] = GENERATOR pgenerator_middle
S_two.ALLOCATIONS = S_one.ALLOCATIONS
$call_descriptors_valid(S_two)
S_three_budget = $drive_steps(S_two, 1)
S_three_budget.COMPLETION = BUDGET
S_three = S_three_budget[.COMPLETION = NORMAL]
S_three.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
$heap_owners($heap_graph(S_three), HOBJECT n_cache) = 1
~(n_cache <- S_three.DESTRUCTION.CALLED)
S_three.OBJECTS[n_middle] = GENERATOR pgenerator_middle
S_three.ALLOCATIONS = S_one.ALLOCATIONS
$call_descriptors_valid(S_three)
'''), *DONE, events('S', PREFIX), events('S_done', EVENTS[UNUSED])],
    },
    'assigned-send-alias-keeps-net-result-transfer': {
        'source': ROWS[USED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r'''
$reference_call_used(S, pgeneratorop.SITE)
~$destructor_return_discarded(ptask_tail*)
~$generator_unused_send_cleanup(S, S_raw, ptask_source, pnode_inputs*)
S_forged = S[.TODO = ptask_source :: [DISCARD]]
$heap_graph(S_forged) = $heap_graph(S)
$generator_operation_valid(S_forged, pgeneratorop_full)
$reference_call_used(S_forged, pgeneratorop.SITE)
$destructor_return_discarded([DISCARD])
S_forged_raw = $generator_operate(S_forged[.TODO = [DISCARD]], pgeneratorop_full)
~$generator_unused_send_cleanup(S_forged, S_forged_raw, ptask_source, pnode_inputs*)
'''), *BUDGET, *checks(r'''
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]
$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2
pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_cache]
'''), *DONE, events('S', PREFIX), events('S_done', EVENTS[USED])],
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
