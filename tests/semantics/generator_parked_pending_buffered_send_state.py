#!/usr/bin/env python3
"""Reach parked SEND overwrite and the used cache after all receivers retire."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_parked_pending_buffered_send_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
TOP = 'generator-parked-pending-buffered-send-top-overwrites-input-keeps-cache'
DROP = 'generator-parked-pending-buffered-send-temporary-top-used-cache'
EVENTS = {
    TOP: ['P|', 'O|', 'TOP|', 'U|', 'L|', 'C|', 'FIRST|', '1', '|', 'DROP|',
          'T|', 'CATCH|', '1', '|', '1', '|', 'S|', 'RET|', '1', '|', '1', '|',
          '1', '|', 'EX|', 'OF|', 'OUT|', 'TF|', 'TOP-DROP|', 'UF|', 'UP|',
          'LF|', 'LOW|', 'CHILD|', 'HELD|', '1', '|', 'A|', 'DROPPED|', 'E',
          'OLD|', 'NEW|'],
    DROP: ['P|', 'O|', 'TOP|', 'U|', 'L|', 'C|', 'FIRST|', 'T|', 'CATCH|',
           '1', '|', '1', '|', 'S|', 'TAKE|', 'OF|', 'CLEARED|', 'LF|', 'UF|',
           'TF|', 'CALLER|', '1', '|', 'D|', 'DROPPED|', 'E', 'NEW|', 'OLD|'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def outputs(parts):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = checks(r"""
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
""")
CASES = {
    'parked-buffered-send-replaces-live-input-without-releasing-old-count': {
        'source': ROWS[TOP]['source'],
        'stage': 'S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_new)])) :: ptask_tail* -- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 13',
        'checks': checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.COMPLETION = NORMAL
S.GC.ACTIVE = eps
S.HELD = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
S.ORIGIN = (pgeneratorop.SITE)
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
pgeneratorop_send = pgeneratorop[.ARGUMENTS = [POBJECT n_new]]
n_top = pgeneratorop.OBJECT
S.OBJECTS[n_top] = GENERATOR pgenerator_top
pgenerator_top.PHASE = GENERATOR_DELEGATING
pgenerator_top.PENDING_INIT
pgenerator_top.PARKED = eps
pgenerator_top.DELEGATE = (pgeneratorfrom_top)
pgeneratorfrom_top.INPUT = (POBJECT n_upper)
pgeneratorfrom_top.ACQUISITION = eps
pgeneratorfrom_top.CURRENT = eps
pgeneratorfrom_top.POSITION = 1
$generator_from_record_valid(S, n_top, pgenerator_top)
pgenerator_top.FRAME = (pframe_top)
pframe_top.HELD = eps
$tasks_nodes(pframe_top.TODO) = eps
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_DELEGATING
~pgenerator_upper.PENDING_INIT
pgenerator_upper.PARKED = eps
pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)
pgeneratorfrom_upper.INPUT = (POBJECT n_lower)
$generator_from_record_valid(S, n_upper, pgenerator_upper)
S.OBJECTS[n_lower] = GENERATOR pgenerator_lower
pgenerator_lower.PHASE = GENERATOR_DELEGATING
~pgenerator_lower.PENDING_INIT
pgenerator_lower.PARKED = eps
pgenerator_lower.DELEGATE = (pgeneratorfrom_lower)
pgeneratorfrom_lower.INPUT = (POBJECT n_child)
$generator_from_record_valid(S, n_lower, pgenerator_lower)
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
~pgenerator_child.PENDING_INIT
pgenerator_child.PARKED = (porigin_yield)
pgenerator_child.DELEGATE = eps
pgenerator_child.VALUE = (POBJECT n_cache)
pgenerator_child.REFCELL = eps
pgenerator_child.KEY = (PINT 0)
pgenerator_child.RETURN = eps
pgenerator_child.FRAME = (pframe_child)
pframe_child.ORIGIN = (porigin_yield)
pframe_child.HELD = eps
$tasks_nodes(pframe_child.TODO) = eps
pframe_child.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_target* z_target) :: ptask_child*
$generator_input_site(S, n_child, porigin_yield)
$generator_input_tail(S, porigin_yield, pframe_child.TODO)
$generator_parked_valid(S, pgenerator_child)
S.GENERATORINPUTS = [pgeneratorinput_old]
pgeneratorinput_old.LIVE
pgeneratorinput_old.OBJECT = n_child
pgeneratorinput_old.SITE = porigin_yield
pgeneratorinput_old.SOURCE.OBJECT = n_lower
pgeneratorinput_old.SOURCE.NAME = "send"
pgeneratorinput_old.SOURCE.LINE = 11
pgeneratorinput_old.SOURCE.ARGUMENTS = [POBJECT n_old]
$generator_inputs_valid(S, S.GENERATORINPUTS)
$generator_input_count(S.GENERATORINPUTS, n_child) = 1
$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_old]
$object_name(S, n_old) = $ptascii("ParkedBufferedSendOld37")
$object_name(S, n_new) = $ptascii("ParkedBufferedSendNew37")
$object_name(S, n_cache) = $ptascii("ParkedBufferedSendCache37")
n_old =/= n_new
n_old =/= n_cache
n_new =/= n_cache
$node_children(S, HOBJECT n_child) = [HOBJECT n_cache]
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_new) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S), HOBJECT n_top) = 3
$heap_owners($heap_graph(S), HOBJECT n_upper) = 2
$heap_owners($heap_graph(S), HOBJECT n_lower) = 2
$heap_owners($heap_graph(S), HOBJECT n_child) = 2
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("outer")) = (n_outer_cell)
S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)
$heap_owners($heap_graph(S), HOBJECT n_outer) = 1
$lookup(S_global.ENV, $ptascii("injected")) = (n_injected_cell)
$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)
S.STORE[n_injected_cell] = DEFINED (POBJECT n_exception)
S.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)
$heap_owners($heap_graph(S), HOBJECT n_exception) = 2
$string_bytes($throwable_field(S, n_exception, "message")) = ($ptascii("park37"))
$throwable_field(S, n_exception, "previous") = PNULL
$generator_operation_valid(S, pgeneratorop_send)
$generator_pending_resume(S, pgeneratorop_send)
$generator_pending_shared_send(S, pgeneratorop_send)
$generator_pending_parked_buffered_send(S, pgeneratorop_send)
~$generator_pending_parked_send(S, pgeneratorop_send)
~$generator_pending_parked_next(S, pgeneratorop_send)
$generator_parked(S, n_top, |S.OBJECTS|)
S_view = $generator_set(S, n_child, pgenerator_child[.PARKED = eps])
$heap_graph(S_view) = $heap_graph(S)
$generator_buffered_next_leaf(S, n_top, $(|S.OBJECTS| + 1)) = eps
$generator_buffered_next_leaf(S_view, n_top, 0) = eps
$generator_buffered_next_leaf(S_view, n_top, 3) = eps
$generator_buffered_next_leaf(S_view, n_top, 4) = (n_child)
~$generator_pending_parked_buffered_send(S, pgeneratorop)
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.LINE = 0])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.SITE = porigin_yield])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.NAME = "next"])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.ARGUMENTS = [PNULL]])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.ARGUMENTS = [POBJECT n_new, PNULL]])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.ADVANCE = true])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.BORROWED = true])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.STARTPACK = true])
S_clear = $generator_set(S, n_top, pgenerator_top[.PENDING_INIT = false])
$heap_graph(S_clear) = $heap_graph(S)
~$generator_pending_parked_buffered_send(S_clear, pgeneratorop_send)
S_blocked = $generator_resume(S_clear, pgeneratorop_send)
S_blocked.COMPLETION = UNSUPPORTED "Generator resume after pending throw"
S_blocked[.COMPLETION = NORMAL] = S_clear
S_badpark = $generator_set(S, n_child, pgenerator_child[.PARKED = (pgenerator_child.FUNCTION)])
$heap_graph(S_badpark) = $heap_graph(S)
~$generator_pending_parked_buffered_send(S_badpark, pgeneratorop_send)
S_badinput = S[.GENERATORINPUTS = [pgeneratorinput_old[.SOURCE = pgeneratorinput_old.SOURCE[.LINE = 0]]]]
$heap_graph(S_badinput) = $heap_graph(S)
~$generator_inputs_valid(S_badinput, S_badinput.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_badinput, pgeneratorop_send)
S_prior = S[.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = false], pgeneratorinput_old]]
$generator_inputs_valid(S_prior, S_prior.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_prior, pgeneratorop_send)
S_scalar = S[.GENERATORINPUTS = [pgeneratorinput_old[.SOURCE = pgeneratorinput_old.SOURCE[.ARGUMENTS = [PINT 9]]]]]
$generator_inputs_valid(S_scalar, S_scalar.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_scalar, pgeneratorop_send)
pframe_wrong = pframe_child[.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME $ptascii("wrong37") z_target) :: ptask_child*]
S_wrong = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_wrong)])
$heap_graph(S_wrong) = $heap_graph(S)
~$generator_pending_parked_buffered_send(S_wrong, pgeneratorop_send)
S_held = $generator_set(S, n_top, pgenerator_top[.FRAME = (pframe_top[.HELD = [HOBJECT n_old]])])
~$generator_pending_parked_buffered_send(S_held, pgeneratorop_send)
""") + ['S.EVENTS = ' + outputs(EVENTS[TOP][:17])] + VALID + BUDGET + checks(r"""
S_expected = $generator_set(S, n_top, pgenerator_top[.PENDING_INIT = false])
S_one.OBJECTS = S_expected.OBJECTS
S_one.OBJECTS[n_child] = GENERATOR pgenerator_child
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.FRAMES = S.FRAMES
S_one.CURRENT = S.CURRENT
S_one.GC = S.GC
S_one.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = false], pgeneratorinput_new]
pgeneratorinput_new.OBJECT = n_child
pgeneratorinput_new.SITE = porigin_yield
pgeneratorinput_new.SOURCE = pgeneratorop_send
pgeneratorinput_new.LIVE
$generator_inputs_valid(S_one, S_one.GENERATORINPUTS)
$generator_input_count(S_one.GENERATORINPUTS, n_child) = 1
$generator_inputs_nodes(S_one.GENERATORINPUTS) = [HOBJECT n_old, HOBJECT n_new]
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_top)]
pdestructionrelease.USER
pdestructionrelease.CALLER = eps
$destructor_release_valid(S_one, pdestructionrelease)
pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_new)])
pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)
pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$destructor_operation_valid(S_one, pdestructionoperation)
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_cache]
$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S_one), HOBJECT n_top) = 3
$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2
~$generator_pending_parked_buffered_send(S_one, pgeneratorop_send)
S_repending = $generator_set(S_one, n_top, pgenerator_top)
$generator_pending_resume(S_repending, pgeneratorop_send)
$generator_inputs_valid(S_repending, S_repending.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_repending, pgeneratorop_send)
S_revived = S_one[.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new]]
$heap_graph(S_revived) = $heap_graph(S_one)
~$generator_inputs_valid(S_revived, S_revived.GENERATORINPUTS)
~$call_descriptors_valid(S_revived)
""") + DONE + ['S_done.EVENTS = ' + outputs(EVENTS[TOP])] + checks(r"""
S_done.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = false], pgeneratorinput_new[.LIVE = false]]
$generator_inputs_valid(S_done, S_done.GENERATORINPUTS)
$generator_input_count(S_done.GENERATORINPUTS, n_child) = 0
S_done.GENERATORRETURNRETAINED = eps
S_done.GENERATORLOOPRETAINED = eps
$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0
~((HOBJECT n_top) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HOBJECT n_lower) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_outer) <- S_done.ALLOCATIONS)
n_cache <- S_done.DESTRUCTION.CALLED
n_old <- S_done.DESTRUCTION.CALLED
n_new <- S_done.DESTRUCTION.CALLED
"""),
    },
    'parked-buffered-send-used-cache-outlives-all-generator-storage': {
        'source': ROWS[DROP]['source'],
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* -- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_new)]) -- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 14 -- if pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)',
        'checks': checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.COMPLETION = NORMAL
S.GC.ACTIVE = eps
S.HELD = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
S.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new]
~pgeneratorinput_old.LIVE
~pgeneratorinput_new.LIVE
pgeneratorinput_old.OBJECT = n_child
pgeneratorinput_new.OBJECT = n_child
pgeneratorinput_old.SITE = porigin_yield
pgeneratorinput_new.SITE = porigin_yield
pgeneratorinput_old.SOURCE.NAME = "send"
pgeneratorinput_old.SOURCE.LINE = 12
pgeneratorinput_old.SOURCE.ARGUMENTS = [POBJECT n_old]
pgeneratorinput_old.SOURCE.OBJECT = n_lower
pgeneratorinput_new.SOURCE.NAME = "send"
pgeneratorinput_new.SOURCE.LINE = 14
pgeneratorinput_new.SOURCE.ARGUMENTS = [POBJECT n_new]
pgeneratorinput_new.SOURCE.OBJECT = n_top
n_top = pgeneratorop.OBJECT
$generator_inputs_valid(S, S.GENERATORINPUTS)
$generator_input_count(S.GENERATORINPUTS, n_child) = 0
$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_old, HOBJECT n_new]
S.OBJECTS[n_top] = GENERATOR pgenerator_top
S.OBJECTS[n_lower] = GENERATOR pgenerator_lower
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_top.PHASE = GENERATOR_CLOSED
pgenerator_lower.PHASE = GENERATOR_CLOSED
pgenerator_child.PHASE = GENERATOR_CLOSED
pgenerator_top.FRAME = eps
pgenerator_lower.FRAME = eps
pgenerator_child.FRAME = eps
pgenerator_top.PARKED = eps
pgenerator_child.PARKED = eps
~((HOBJECT n_top) <- S.ALLOCATIONS)
~((HOBJECT n_lower) <- S.ALLOCATIONS)
~((HOBJECT n_child) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_top) = 0
$heap_owners($heap_graph(S), HOBJECT n_lower) = 0
$heap_owners($heap_graph(S), HOBJECT n_child) = 0
$heap_children(HOBJECT n_child, $allocation_edges(S, S.ALLOCATIONS)) = eps
$generator_storage_for(S, n_top) = eps
$generator_storage_for(S, n_child) = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("top")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("lower")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$lookup(S_global.ENV, $ptascii("injected")) = (n_injected_cell)
$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)
S.STORE[n_injected_cell] = DEFINED (POBJECT n_exception)
S.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)
$heap_owners($heap_graph(S), HOBJECT n_exception) = 2
$string_bytes($throwable_field(S, n_exception, "message")) = ($ptascii("old37"))
$throwable_field(S, n_exception, "previous") = PNULL
$object_name(S, n_old) = $ptascii("ParkedBufferedSendOldLate37")
$object_name(S, n_new) = $ptascii("ParkedBufferedSendNewLate37")
$object_name(S, n_cache) = $ptascii("ParkedBufferedSendLateCache37")
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_new) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
~(n_old <- S.DESTRUCTION.CALLED)
~(n_new <- S.DESTRUCTION.CALLED)
~(n_cache <- S.DESTRUCTION.CALLED)
$heap_count(HOBJECT n_cache, $machine_roots(S)) = 1
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_cache]
S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
S.DESTRUCTION.CALLS = eps
pdestructionoperation.CALLER = eps
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
$destructor_operation_live(S, pdestructionoperation)
$destructor_operation_valid(S, pdestructionoperation)
~$generator_operation_valid(S, pgeneratorop)
~$generator_pending_parked_buffered_send(S, pgeneratorop)
~$destructor_operation_valid(S, pdestructionoperation[.ORIGIN = eps])
S_badold = S[.GENERATORINPUTS = [pgeneratorinput_old[.SOURCE = pgeneratorinput_old.SOURCE[.LINE = 0]], pgeneratorinput_new]]
$heap_graph(S_badold) = $heap_graph(S)
~$generator_inputs_valid(S_badold, S_badold.GENERATORINPUTS)
~$call_descriptors_valid(S_badold)
S_badnew = S[.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new[.SOURCE = pgeneratorinput_new.SOURCE[.LINE = 0]]]]
$heap_graph(S_badnew) = $heap_graph(S)
~$generator_inputs_valid(S_badnew, S_badnew.GENERATORINPUTS)
~$call_descriptors_valid(S_badnew)
S_revived = S[.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new[.LIVE = true]]]
$heap_graph(S_revived) = $heap_graph(S)
~$generator_inputs_valid(S_revived, S_revived.GENERATORINPUTS)
~$call_descriptors_valid(S_revived)
""") + ['S.EVENTS = ' + outputs(EVENTS[DROP][:20])] + VALID + BUDGET + checks(r"""
S_one.TODO = ptask_tail*
S_one.RESULT = KNOWN (POBJECT n_cache)
S_one.OBJECTS = S.OBJECTS
S_one.STORE = S.STORE
S_one.ARRAYS = S.ARRAYS
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.GENERATORINPUTS = S.GENERATORINPUTS
S_one.DESTRUCTION.OPERATIONS = eps
$heap_graph(S_one) = $heap_graph(S)
$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1
~(n_cache <- S_one.DESTRUCTION.CALLED)
""") + DONE + ['S_done.EVENTS = ' + outputs(EVENTS[DROP])] + checks(r"""
S_done.GENERATORINPUTS = S.GENERATORINPUTS
$generator_inputs_valid(S_done, S_done.GENERATORINPUTS)
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_new) = 1
n_cache <- S_done.DESTRUCTION.CALLED
n_old <- S_done.DESTRUCTION.CALLED
n_new <- S_done.DESTRUCTION.CALLED
"""),
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
    report_path = raw / 'report.json'
    report = json.loads(report_path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(b).hexdigest() for p, b in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
