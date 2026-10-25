#!/usr/bin/env python3
"""Reach parked direct Generator resumers, frame roots and native reentry Errors."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_transfer_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
FRESH = 'generator-fiber-transfer-fresh-current-echo'
PAUSED = 'generator-fiber-transfer-after-yield-echo'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
         '-- if pgeneratorop.NAME = "next" -- if S.ACTIVEFIBER = eps '
         '-- if S.CURRENT = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
         '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
         '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
         '-- if pfiber.STATUS = FIBER_SUSPENDED')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S.HELD = eps
S.RESULT = KNOWN PNULL
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
n_generator = pgeneratorop.OBJECT
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = [pframe_resumer, pframe_root]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.SENT = (PSTRING_CARRIER INTERNED_STRING $ptascii("pause53"))
pfiberapi.SEQUENCE = pfiber.SEQUENCE
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_original) :: ptask_resumer*
pframe_resumer.CONTEXT = (pcallcontext_callback)
pframe_root.TODO = [FIBER_FINISH n_fiber]
pframe_root.CONTEXT = eps
pgeneratorop_original.OBJECT = n_generator
pgeneratorop_original.LOOP = eps
pgeneratorop_original.ARGUMENTS = eps
~pgeneratorop_original.ADVANCE
~pgeneratorop_original.STARTPACK
~pgeneratorop_original.BORROWED
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.DELEGATE = eps
pgenerator.PARKED = eps
pgenerator.RETURN = eps
pgenerator.REFCELL = eps
~pgenerator.PENDING_INIT
$node_children(S, HOBJECT n_generator) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop_original) = [HOBJECT n_generator]
$task_nodes(FIBER_CONTINUE pfiberapi) = eps
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_token_cell)
S.STORE[n_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token53")
$node_children(S, HCELL n_token_cell) = [HOBJECT n_token]
$heap_count(HCELL n_token_cell, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HCELL n_token_cell) = 1
$heap_owners($heap_graph(S), HOBJECT n_token) = 1
~(n_token <- S.DESTRUCTION.CALLED)
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$node_children(S, HOBJECT n_weak) = eps
$weakref_get(S, n_weak) = POBJECT n_token
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
H_view = $heap_graph(S_view)
$fiber_generator_body_id(S_view[.ACTIVEFIBER = eps]) = (n_generator)
~$fiber_transfer_domain(S_view[.ACTIVEFIBER = eps])
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = (n_generator)])
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = (|S.OBJECTS|)])
~$fiber_generator_transfer($fiber_put(S_view, n_fiber, pfiber[.STATUS = FIBER_INIT]))
~$fiber_generator_transfer($fiber_put(S_view, n_fiber, pfiber[.STATUS = FIBER_TERMINATED]))
~$fiber_transfer_domain(S_view[.CONSTCONTEXT = ({ORIGIN pgenerator.FUNCTION, LINE 1, FACTS eps})])
$fiber_generator_body_id(S_view[.SOURCES = eps]) = eps
pframe_wrong = pframe_resumer[.ORIGIN = eps]
S_wrong = S_view[.FRAMES = [pframe_wrong, pframe_root]]
$heap_graph(S_wrong) = H_view
$fiber_generator_body_id(S_wrong) = eps
pgeneratorop_wrong = pgeneratorop_original[.SITE = pgenerator.FUNCTION]
pframe_source = pframe_resumer[.TODO = (GENERATOR_RESUME pgeneratorop_wrong) :: ptask_resumer*]
S_source = S_view[.FRAMES = [pframe_source, pframe_root]]
$heap_graph(S_source) = H_view
$fiber_generator_body_id(S_source) = eps
S_duplicate_frame = S_view[.FRAMES = [pframe_resumer, pframe_resumer, pframe_root]]
$fiber_generator_body_id(S_duplicate_frame) = eps
S_pending = $generator_set(S_view, n_generator, pgenerator[.PENDING_INIT = true])
$heap_graph(S_pending) = H_view
$fiber_generator_body_id(S_pending) = eps
S_parked = $generator_set(S_view, n_generator, pgenerator[.PARKED = (pgeneratorop_original.SITE)])
$heap_graph(S_parked) = H_view
$fiber_generator_body_id(S_parked) = eps
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
""")
# These are constructed carrier/metadata controls, not new valid Fiber sources.
OCCURRENCES = checks(r"""
n_copy = |S.OBJECTS|
S_copy = S[.OBJECTS = S.OBJECTS ++ [FIBER pfiber]][.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_copy]]
$generator_saved_fiber_ids(S_copy) = [n_generator, n_generator]
~$generator_owners_valid(S_copy)
pfibercaller_copy = {OBJECT n_fiber, PREVIOUS eps, VM pfibervm, API pfiberapi}
S_caller = S[.FIBERCALLERS = [pfibercaller_copy]]
$generator_saved_fiber_ids(S_caller) = [n_generator, n_generator]
~$generator_owners_valid(S_caller)
pdestructionrelease_copy = {JOBS eps, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, USER false}
pfiberclose_copy = {OBJECT n_fiber, PREVIOUS eps, CALLERS 0, VM pfibervm, RELEASE pdestructionrelease_copy, SUSPEND pfiberapi, EXIT n_fiber, SEQUENCE pfiber.SEQUENCE}
S_closer = S[.FIBERCLOSERS = [pfiberclose_copy]]
$generator_saved_fiber_ids(S_closer) = [n_generator, n_generator]
~$generator_owners_valid(S_closer)
""")
ENDING = checks(r"""
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_call = S[.TODO = ptask_tail*]
S_error = $generator_operate(S_call, pgeneratorop)
S_error.COMPLETION = THROWING n_error
$object_name(S_error, n_error) = $ptascii("Error")
$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Cannot resume an already running generator"))
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.TODO = (THROW_SEARCH n_error) :: ptask_error*
S_one.OBJECTS = S_error.OBJECTS
S_one.OBJECTS[n_fiber] = FIBER pfiber
S_one.OBJECTS[n_generator] = GENERATOR pgenerator
$heap_owners($heap_graph(S_one), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_token) = 1
$generator_saved_fiber_ids(S_one) = [n_generator]
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_done = $drive(S_one, 4000)
$drive(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
S_done.HELD = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
n_token <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
$generator_saved_fiber_ids(S_done) = eps
""")

REENTRY = ['REENTRY53\n', 'Error', '|', 'Cannot resume an already running generator', '\n', 'PREVIOUS-NULL|']
FINISH = ['FIBER|', '1', '|', '1', '|\n', 'CACHE|', '1', '|', '1', '|\n',
          'E53\n', 'D53\n', 'RETURN|', '1', '|', '1', '|\n', 'END53\n']
EVENTS = {
 FRESH: ['START|', 'F53\n', 'CURRENT|', 'B53\n', '1', '|\n', 'PARKED|', '1', '|', '1', '|\n',
         *REENTRY, '0', '|\n', 'RESUME|', 'R53\n', 'RECEIVED|', '1', '|\n', '1', '|\n', 'C53\n', '1', '|\n', *FINISH],
 PAUSED: ['B53\n', 'START|', 'F53\n', 'NEXT|', 'A53\n', '1', '|\n', 'PARKED|', '1', '|', '1', '|\n',
          *REENTRY, '1', '|\n', 'RESUME|', 'R53\n', 'RECEIVED|', '1', '|\n', '1', '|\n',
          'CURRENT|', '1', '|\n', 'C53\n', '1', '|\n', *FINISH],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())
CASES = {
 'generator-fiber-fresh-frame-and-double-reentry': {
  'source': ROWS[FRESH]['source'], 'stage': STAGE,
  'checks': [*COMMON, *OCCURRENCES, *checks(r"""
pgeneratorop_original.NAME = "current"
pgenerator.VALUE = eps
pgenerator.KEY = eps
pgenerator.FIRST
"""), *ENDING, *checks(r"""
$throwable_previous_id(S_one, n_error) = (n_initial)
$object_name(S_one, n_initial) = $ptascii("Error")
$string_bytes($throwable_field(S_one, n_initial, "message")) = ($ptascii("Cannot resume an already running generator"))
$throwable_previous_id(S_one, n_initial) = eps
$heap_owners($heap_graph(S_one), HOBJECT n_initial) = 1
n_initial = |S.OBJECTS|
n_error = $(|S.OBJECTS| + 1)
|S_one.OBJECTS| = $(|S.OBJECTS| + 2)
"""), events(EVENTS[FRESH])],
 },
 'generator-fiber-after-yield-frame-and-single-reentry': {
  'source': ROWS[PAUSED]['source'], 'stage': STAGE,
  'checks': [*COMMON, *checks(r"""
pgeneratorop_original.NAME = "next"
pgenerator.VALUE = (PSTRING_CARRIER INTERNED_STRING $ptascii("first53"))
pgenerator.KEY = (PINT 0)
~pgenerator.FIRST
"""), *ENDING, *checks(r"""
$throwable_previous_id(S_one, n_error) = eps
n_error = |S.OBJECTS|
|S_one.OBJECTS| = $(|S.OBJECTS| + 1)
"""), events(EVENTS[PAUSED])],
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
