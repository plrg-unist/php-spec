#!/usr/bin/env python3
"""Reach pending argument exceptions before one-ancestor SEND cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_ancestor_abrupt_argument_send_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
UNUSED = 'generator-ancestor-abrupt-argument-send-unused-row-finally'
USED = 'generator-ancestor-abrupt-argument-send-used-temporary-control'
PREFIX = ['P|', 'O|', 'U|', 'M|', 'C|', 'L|', 'H|', 'G|', 'S|', 'ARG|', 'F|', 'ARG-END|']
SUFFIX = ['CALLER|', '1', '|', '1', '|', 'COPY|', '0', '|', 'C-LIVE|', 'ROW-DROPPED|', 'E']
EVENTS = {UNUSED: PREFIX + ['K|', 'A|', 'K-END|'] + SUFFIX,
          USED: PREFIX + ['K|', 'K-END|', 'A|'] + SUFFIX}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.CURRENT = eps -- if S.FRAMES = eps '
         '-- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
         '-- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)]) '
         '-- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 12 '
         '-- if pdestructionoperation.PENDING = (n_given)')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.HELD = eps
S.GENERATORINPUTS = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.CALLER = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
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
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_row)
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 0)) :: ptask_middle_tail*
pframe_middle.HELD = eps
$task_nodes(GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 0)) = eps
$generator_from_complete_valid(S, n_middle, pgeneratorfrom_middle.SITE, n_child, PINT 0)
$generator_nodefree_ancestor_leaf(S, n_upper) = (n_middle)
$generator_nodefree_return_waiting(S, n_middle)
~$generator_return_waiting(S, n_middle)
~$generator_return_parked_waiting(S, n_middle)
~((HOBJECT n_child) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$generator_storage_for(S, n_upper) = eps
$generator_storage_for(S, n_middle) = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("argument50"))
$throwable_field(S, n_given, "previous") = PNULL
$destructor_selected_pending(S, eps) = (n_given)
$heap_owners($heap_graph(S), HOBJECT n_given) = 2
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_array)
n_row <- S.REFCELLS
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
$object_name(S, n_old) = $ptascii("AncestorAbruptArgumentSendRowOld50")
$node_children(S, HCELL n_row) = [HARRAY n_array]
$node_children(S, HARRAY n_array) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HCELL n_row) = 2
$heap_owners($heap_graph(S), HARRAY n_array) = 2
$heap_count(HARRAY n_array, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
~(n_old <- S.DESTRUCTION.CALLED)
n_argument <- S.DESTRUCTION.CALLED
~((HOBJECT n_argument) <- S.ALLOCATIONS)
$lookup(S_global.ENV, $ptascii("copy")) = eps
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$destructor_release_valid(S, pdestructionrelease)
$destructor_operation_valid(S, pdestructionoperation)
pdestructionoperation_bad = pdestructionoperation[.SOURCE = DESTRUCTOR_GLOBALS]
S_bad = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]]
$heap_graph(S_bad) = $heap_graph(S)
~$destructor_operation_live(S_bad, pdestructionoperation_bad)
~$call_descriptors_valid(S_bad)
pdestructionoperation_badpending = pdestructionoperation[.PENDING = (n_upper)]
S_badpending = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_badpending]]
~$destructor_operation_live(S_badpending, pdestructionoperation_badpending)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
""")
BUDGET_DONE = checks(r"""
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.EVENTS = S.EVENTS
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
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
~((HARRAY n_array) <- S_done.ALLOCATIONS)
~((HCELL n_row) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
""")
CASES = {
    'ancestor-abrupt-argument-unused-retires-snapshot-before-receiver': {
        'source': ROWS[UNUSED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
~$reference_call_used(S, pgeneratorop.SITE)
$destructor_return_discarded(ptask_tail*)
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_array), DESTRUCTION_VALUE (HOBJECT n_upper)]
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_given]
"""), *BUDGET_DONE, *checks(r"""
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_one) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease_one = pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]]
$heap_owners($heap_graph(S_one), HARRAY n_array) = 1
$heap_count(HARRAY n_array, $machine_roots(S_one)) = 0
S_one.OBJECTS = S.OBJECTS
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
$destructor_selected_pending(S_one, eps) = (n_given)
$destructor_operation_valid(S_one, pdestructionoperation)
"""), events('S', PREFIX), events('S_done', EVENTS[UNUSED])],
    },
    'ancestor-abrupt-argument-assigned-retains-temporary-without-cv-store': {
        'source': ROWS[USED]['source'],
        'stage': STAGE,
        'checks': [*COMMON, *checks(r"""
$reference_call_used(S, pgeneratorop.SITE)
pdestructionoperation.VALUE = KNOWN (PARRAY n_array)
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HARRAY n_array, HOBJECT n_given]
"""), *BUDGET_DONE, events('S', PREFIX), events('S_done', EVENTS[USED])],
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
