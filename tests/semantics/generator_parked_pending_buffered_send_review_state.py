#!/usr/bin/env python3
"""Reach the first parked input overwrite and distinguish orphan cells from replacement copies."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_parked_pending_buffered_send_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
COW = 'generator-parked-pending-buffered-send-review-reverse-row-overwrite-cow'
CELL = 'generator-parked-pending-buffered-send-review-null-cache-input-cell-copy'
EVENTS = {
    COW: ['P|', 'O|', 'T|', 'U|', 'L|', 'C0|', 'H|', '1', '|', 'S1|THROW|',
          'CALLER|', '1', '|', '1', '|', 'S2|', 'RET|', '1', '|', '1', '|',
          'COW|', '1', '|', '1', '|', 'SNAP-DROP|', 'EX|', 'Z|', 'OUT|', 'V|',
          'TOP|', 'K|', 'UP|', 'J|', 'LOW|', 'CHILD|', 'C|', 'ROW|', 'E', 'A|', 'B|'],
    CELL: ['P|', 'O|', 'T|', 'U|', 'L|', 'C|', 'H|', '1', '|', 'S1|THROW|',
           'CALLER|', '1', '|', '1', '|', 'S2|', 'RET|', '1', '|', '1', '|', '1', '|',
           'EX|', 'Z|', 'OUT|', 'V|', 'TOP|', 'K|', 'UP|', 'J|', 'LOW|', 'CHILD|',
           'WRITE|', 'UNSET|', 'E', 'CNEW|', 'R|'],
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
    'parked-buffered-send-orphans-old-row-input-and-copies-current-before-cow': {
        'source': ROWS[COW]['source'],
        'stage': 'S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (PARRAY n_newarray)])) :: ptask_tail* -- if pgeneratorop.NAME = "send" -- if pgeneratorop.LINE = 13',
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
pgeneratorop_send = pgeneratorop[.ARGUMENTS = [PARRAY n_newarray]]
n_upper = pgeneratorop.OBJECT
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_DELEGATING
pgenerator_upper.PENDING_INIT
pgenerator_upper.PARKED = eps
pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)
pgeneratorfrom_upper.INPUT = (POBJECT n_lower)
pgeneratorfrom_upper.ACQUISITION = eps
pgeneratorfrom_upper.CURRENT = eps
pgeneratorfrom_upper.POSITION = 1
$generator_from_record_valid(S, n_upper, pgenerator_upper)
pgenerator_upper.FRAME = (pframe_upper)
pframe_upper.HELD = eps
$tasks_nodes(pframe_upper.TODO) = eps
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
pgenerator_child.VALUE = eps
pgenerator_child.REFCELL = (n_row)
pgenerator_child.KEY = (PINT 7)
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
pgeneratorinput_old.SOURCE.ARGUMENTS = [PARRAY n_array]
$generator_inputs_valid(S, S.GENERATORINPUTS)
$generator_input_count(S.GENERATORINPUTS, n_child) = 1
$generator_inputs_nodes(S.GENERATORINPUTS) = [HARRAY n_array]
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("row")) = (n_row)
S.STORE[n_row] = DEFINED (PARRAY n_array)
n_row <- S.REFCELLS
(HCELL n_row) <- S.ALLOCATIONS
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
S.ARRAYS[n_newarray].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]
$object_name(S, n_old) = $ptascii("ReviewBufferedSendOld37")
$object_name(S, n_new) = $ptascii("ReviewBufferedSendNewInput37")
n_array =/= n_newarray
$node_children(S, HARRAY n_array) = [HOBJECT n_old]
$node_children(S, HARRAY n_newarray) = [HOBJECT n_new]
$node_children(S, HOBJECT n_child) = [HCELL n_row, HCELL n_row]
$heap_owners($heap_graph(S), HARRAY n_array) = 2
$heap_owners($heap_graph(S), HARRAY n_newarray) = 1
$heap_count(HARRAY n_array, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HCELL n_row) = 3
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_new) = 1
$heap_owners($heap_graph(S), HOBJECT n_upper) = 3
$heap_owners($heap_graph(S), HOBJECT n_lower) = 2
$heap_owners($heap_graph(S), HOBJECT n_child) = 2
$lookup(S_global.ENV, $ptascii("top")) = (n_top_cell)
S.STORE[n_top_cell] = DEFINED (POBJECT n_top)
S.OBJECTS[n_top] = GENERATOR pgenerator_top
~pgenerator_top.PENDING_INIT
pgenerator_top.PARKED = eps
$lookup(S_global.ENV, $ptascii("outer")) = (n_outer_cell)
S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)
$lookup(S_global.ENV, $ptascii("injected")) = (n_injected_cell)
$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)
S.STORE[n_injected_cell] = DEFINED (POBJECT n_exception)
S.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)
$heap_owners($heap_graph(S), HOBJECT n_exception) = 2
$throwable_field(S, n_exception, "previous") = PNULL
$generator_operation_valid(S, pgeneratorop_send)
$generator_pending_resume(S, pgeneratorop_send)
$generator_pending_shared_send(S, pgeneratorop_send)
$generator_pending_parked_buffered_send(S, pgeneratorop_send)
~$generator_pending_parked_send(S, pgeneratorop_send)
~$generator_pending_parked_next(S, pgeneratorop_send)
$generator_parked(S, n_upper, |S.OBJECTS|)
S_view = $generator_set(S, n_child, pgenerator_child[.PARKED = eps])
$heap_graph(S_view) = $heap_graph(S)
$generator_buffered_next_leaf(S, n_upper, $(|S.OBJECTS| + 1)) = eps
$generator_buffered_next_leaf(S_view, n_upper, 0) = eps
$generator_buffered_next_leaf(S_view, n_upper, 2) = eps
$generator_buffered_next_leaf(S_view, n_upper, 3) = (n_child)
~$generator_pending_parked_buffered_send(S, pgeneratorop)
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.LINE = 0])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.SITE = porigin_yield])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.NAME = "next"])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.NAME = "throw"])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.ARGUMENTS = [PNULL]])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.ARGUMENTS = [PARRAY n_newarray, PNULL]])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.ADVANCE = true])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.BORROWED = true])
~$generator_pending_parked_buffered_send(S, pgeneratorop_send[.STARTPACK = true])
S_clear = $generator_set(S, n_upper, pgenerator_upper[.PENDING_INIT = false])
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
S_orphan = S[.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = false]]]
$heap_graph(S_orphan) = $heap_graph(S)
~$generator_pending_parked_buffered_send(S_orphan, pgeneratorop_send)
S_prior = S[.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = false], pgeneratorinput_old]]
$generator_inputs_valid(S_prior, S_prior.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_prior, pgeneratorop_send)
S_scalar = S[.GENERATORINPUTS = [pgeneratorinput_old[.SOURCE = pgeneratorinput_old.SOURCE[.ARGUMENTS = [PINT 9]]]]]
$generator_inputs_valid(S_scalar, S_scalar.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_scalar, pgeneratorop_send)
S_duplicate = S[.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_old]]
~$generator_inputs_valid(S_duplicate, S_duplicate.GENERATORINPUTS)
~$generator_pending_parked_buffered_send(S_duplicate, pgeneratorop_send)
pframe_wrong = pframe_child[.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME $ptascii("wrong37") z_target) :: ptask_child*]
S_wrong = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_wrong)])
$heap_graph(S_wrong) = $heap_graph(S)
~$generator_pending_parked_buffered_send(S_wrong, pgeneratorop_send)
S_held = $generator_set(S, n_upper, pgenerator_upper[.FRAME = (pframe_upper[.HELD = [HARRAY n_array]])])
~$generator_pending_parked_buffered_send(S_held, pgeneratorop_send)
S_childheld = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_child[.HELD = [HARRAY n_array]])])
~$generator_pending_parked_buffered_send(S_childheld, pgeneratorop_send)
""") + ['S.EVENTS = ' + outputs(EVENTS[COW][:16])] + VALID + BUDGET + checks(r"""
S_expected = $generator_set(S, n_upper, pgenerator_upper[.PENDING_INIT = false])
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
$generator_inputs_nodes(S_one.GENERATORINPUTS) = [HARRAY n_array, HARRAY n_newarray]
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]
pdestructionrelease.USER
pdestructionrelease.CALLER = eps
$destructor_release_valid(S_one, pdestructionrelease)
pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (PARRAY n_newarray)])
pdestructionoperation.VALUE = KNOWN (PARRAY n_array)
pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$destructor_operation_valid(S_one, pdestructionoperation)
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HARRAY n_array]
$heap_owners($heap_graph(S_one), HARRAY n_array) = 3
$heap_owners($heap_graph(S_one), HARRAY n_newarray) = 1
$heap_count(HARRAY n_array, $machine_roots(S_one)) = 2
$node_children(S_one, HARRAY n_array) = [HOBJECT n_old]
$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_one), HCELL n_row) = 3
$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2
~$generator_pending_parked_buffered_send(S_one, pgeneratorop_send)
S_revived = S_one[.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new]]
$heap_graph(S_revived) = $heap_graph(S_one)
~$generator_inputs_valid(S_revived, S_revived.GENERATORINPUTS)
~$call_descriptors_valid(S_revived)
""") + DONE + ['S_done.EVENTS = ' + outputs(EVENTS[COW])] + checks(r"""
S_done.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = false], pgeneratorinput_new[.LIVE = false]]
$generator_inputs_valid(S_done, S_done.GENERATORINPUTS)
$generator_input_count(S_done.GENERATORINPUTS, n_child) = 0
S_done.GENERATORRETURNRETAINED = eps
S_done.GENERATORLOOPRETAINED = eps
S_done.ARRAYS[n_array].ITEMS = S.ARRAYS[n_array].ITEMS
S_done.ARRAYS[n_newarray].ITEMS = S.ARRAYS[n_newarray].ITEMS
$heap_owners($heap_graph(S_done), HARRAY n_array) = 1
$heap_owners($heap_graph(S_done), HARRAY n_newarray) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_done), HCELL n_row) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_lower) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HOBJECT n_top) <- S_done.ALLOCATIONS)
~((HOBJECT n_outer) <- S_done.ALLOCATIONS)
n_old <- S_done.DESTRUCTION.CALLED
n_new <- S_done.DESTRUCTION.CALLED
"""),
    },
    'overwritten-input-cell-and-replacement-object-copy-survive-late-write': {
        'source': ROWS[CELL]['source'],
        'stage': 'S.TODO = (WRITE_NAME n_name* z_write) :: ptask_tail* -- if n_name* = $ptascii("slot") -- if S.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new] -- if ~pgeneratorinput_old.LIVE -- if ~pgeneratorinput_new.LIVE -- if S.RESULT = KNOWN (POBJECT n_new) -- if $object_name(S, n_new) = $ptascii("ReviewBufferedSendCellNew37")',
        'checks': checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.COMPLETION = NORMAL
S.GC.ACTIVE = eps
S.LITERALREFDEBTS = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
z_write = 14
n_child = pgeneratorinput_old.OBJECT
pgeneratorinput_new.OBJECT = n_child
n_lower = pgeneratorinput_old.SOURCE.OBJECT
n_top = pgeneratorinput_new.SOURCE.OBJECT
pgeneratorinput_new.SITE = pgeneratorinput_old.SITE
pgeneratorinput_old.SOURCE.NAME = "send"
pgeneratorinput_new.SOURCE.NAME = "send"
pgeneratorinput_old.SOURCE.LINE = 10
pgeneratorinput_new.SOURCE.LINE = 12
pgeneratorinput_old.SOURCE.ARGUMENTS = [PARRAY n_array]
pgeneratorinput_new.SOURCE.ARGUMENTS = [PARRAY n_newarray]
n_array =/= n_newarray
$generator_input_source_valid(S, pgeneratorinput_old)
$generator_input_source_valid(S, pgeneratorinput_new)
$generator_inputs_valid(S, S.GENERATORINPUTS)
$generator_input_count(S.GENERATORINPUTS, n_child) = 0
$generator_inputs_nodes(S.GENERATORINPUTS) = [HARRAY n_array, HARRAY n_newarray]
$heap_count(HARRAY n_array, $machine_roots(S)) = 1
$heap_count(HARRAY n_newarray, $machine_roots(S)) = 1
$heap_owners($heap_graph(S), HARRAY n_array) = 1
$heap_owners($heap_graph(S), HARRAY n_newarray) = 1
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_slot)]
S.ARRAYS[n_newarray].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]
S_global = $global_table_view(S)
$lookup(S_global.ENV, n_name*) = (n_slot)
n_slot <- S.REFCELLS
(HCELL n_slot) <- S.ALLOCATIONS
S.STORE[n_slot] = DEFINED (POBJECT n_old)
$object_name(S, n_old) = $ptascii("ReviewBufferedSendReturn37")
$node_children(S, HARRAY n_array) = [HCELL n_slot]
$node_children(S, HARRAY n_newarray) = [HOBJECT n_old]
$node_children(S, HCELL n_slot) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HCELL n_slot) = 2
$heap_owners($heap_graph(S), HOBJECT n_old) = 2
$heap_owners($heap_graph(S), HOBJECT n_new) = 1
~(n_old <- S.DESTRUCTION.CALLED)
~(n_new <- S.DESTRUCTION.CALLED)
S.OBJECTS[n_lower] = GENERATOR pgenerator_lower
S.OBJECTS[n_top] = GENERATOR pgenerator_top
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_lower.PHASE = GENERATOR_CLOSED
pgenerator_top.PHASE = GENERATOR_CLOSED
pgenerator_child.PHASE = GENERATOR_CLOSED
pgenerator_lower.FRAME = eps
pgenerator_top.FRAME = eps
pgenerator_child.FRAME = eps
~((HOBJECT n_lower) <- S.ALLOCATIONS)
~((HOBJECT n_top) <- S.ALLOCATIONS)
~((HOBJECT n_child) <- S.ALLOCATIONS)
$heap_children(HOBJECT n_lower, $allocation_edges(S, S.ALLOCATIONS)) = eps
$heap_children(HOBJECT n_top, $allocation_edges(S, S.ALLOCATIONS)) = eps
$heap_children(HOBJECT n_child, $allocation_edges(S, S.ALLOCATIONS)) = eps
$lookup(S_global.ENV, $ptascii("outer")) = eps
$lookup(S_global.ENV, $ptascii("top")) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("lower")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
S_badsource = S[.GENERATORINPUTS = [pgeneratorinput_old[.SOURCE = pgeneratorinput_old.SOURCE[.LINE = 0]], pgeneratorinput_new]]
$heap_graph(S_badsource) = $heap_graph(S)
$heap_valid($heap_graph(S_badsource))
~$generator_inputs_valid(S_badsource, S_badsource.GENERATORINPUTS)
~$call_descriptors_valid(S_badsource)
S_badnew = S[.GENERATORINPUTS = [pgeneratorinput_old, pgeneratorinput_new[.SOURCE = pgeneratorinput_new.SOURCE[.LINE = 0]]]]
$heap_graph(S_badnew) = $heap_graph(S)
~$generator_inputs_valid(S_badnew, S_badnew.GENERATORINPUTS)
~$call_descriptors_valid(S_badnew)
S_revived = S[.GENERATORINPUTS = [pgeneratorinput_old[.LIVE = true], pgeneratorinput_new]]
$heap_graph(S_revived) = $heap_graph(S)
~$generator_inputs_valid(S_revived, S_revived.GENERATORINPUTS)
~$call_descriptors_valid(S_revived)
""") + ['S.EVENTS = ' + outputs(EVENTS[CELL][:33])] + VALID + BUDGET + checks(r"""
S_one.GENERATORINPUTS = S.GENERATORINPUTS
$generator_inputs_valid(S_one, S_one.GENERATORINPUTS)
S_one.ARRAYS = S.ARRAYS
S_one.OBJECTS = S.OBJECTS
S_expected = S[.STORE[n_slot] = DEFINED (POBJECT n_new)]
S_one.STORE = S_expected.STORE
S_one.ENV = S.ENV
S_one.ALLOCATIONS = S.ALLOCATIONS
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]
pdestructionrelease.USER
pdestructionrelease.CALLER = eps
pdestructionoperation.SOURCE = WRITE_NAME n_name* z_write
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
$node_children(S_one, HARRAY n_array) = [HCELL n_slot]
$node_children(S_one, HARRAY n_newarray) = [HOBJECT n_old]
$node_children(S_one, HCELL n_slot) = [HOBJECT n_new]
$heap_owners($heap_graph(S_one), HARRAY n_array) = 1
$heap_owners($heap_graph(S_one), HARRAY n_newarray) = 1
$heap_owners($heap_graph(S_one), HCELL n_slot) = 2
$heap_owners($heap_graph(S_one), HOBJECT n_old) = 2
$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1
~(n_old <- S_one.DESTRUCTION.CALLED)
S_quiet_budget = $drive_steps(S_one, 1)
S_quiet_budget.COMPLETION = BUDGET
S_quiet = S_quiet_budget[.COMPLETION = NORMAL]
S_quiet.EVENTS = S.EVENTS
$heap_owners($heap_graph(S_quiet), HOBJECT n_old) = 1
~(n_old <- S_quiet.DESTRUCTION.CALLED)
$call_descriptors_valid(S_quiet)
$heap_valid($heap_graph(S_quiet))
""") + DONE + ['S_done.EVENTS = ' + outputs(EVENTS[CELL])] + checks(r"""
S_done.GENERATORINPUTS = S.GENERATORINPUTS
$generator_inputs_valid(S_done, S_done.GENERATORINPUTS)
S_done.ARRAYS[n_array].ITEMS = S.ARRAYS[n_array].ITEMS
S_done.ARRAYS[n_newarray].ITEMS = S.ARRAYS[n_newarray].ITEMS
S_done.STORE[n_slot] = DEFINED (POBJECT n_new)
$heap_owners($heap_graph(S_done), HARRAY n_array) = 1
$heap_owners($heap_graph(S_done), HARRAY n_newarray) = 1
$heap_owners($heap_graph(S_done), HCELL n_slot) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1
(HOBJECT n_old) <- S_done.ALLOCATIONS
(HOBJECT n_new) <- S_done.ALLOCATIONS
n_old <- S_done.DESTRUCTION.CALLED
n_new <- S_done.DESTRUCTION.CALLED
"""),
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    # The full COW check reached the former 120-second bound on an exclusive CPU.
    caps = {name: 240 if name == 'parked-buffered-send-orphans-old-row-input-and-copies-current-before-cow'
            else 120 for name in CASES}
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment,
                        caps[directory.name] if stem == 'model' else cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    report_path = raw / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['budgets'].update(process_seconds=max(caps[name] for name in report['selection']),
                             case_process_seconds={name: caps[name] for name in report['selection']})
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest()
                                     for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
