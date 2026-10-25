#!/usr/bin/env python3
"""Reach a parked Generator VM and real supplied-Throwable injection in its body."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_transfer_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
HANDLED = 'review-generator-fiber-transfer-handled-injection'
UNHANDLED = 'review-generator-fiber-transfer-unhandled-injection'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


ENDING = checks(r"""
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
$drive(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
$generator_saved_fiber_ids(S_done) = eps
""")

PARKED = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = [pframe_generator, pframe_root]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.START = eps
pfiberapi.SENT = (PSTRING_CARRIER INTERNED_STRING $ptascii("pause53"))
pfiberapi.SEQUENCE = pfiber.SEQUENCE
pfiber.FINISH = eps
~pfiber.FAILED
~pfiber.RETURNED
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pframe_root.TODO = [FIBER_FINISH n_fiber]
pframe_root.CONTEXT = eps
n_generator = pgeneratorop.OBJECT
pgeneratorop.NAME = "current"
pgeneratorop.LINE = 23
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.DELEGATE = eps
pgenerator.CLOSURE = eps
pgenerator.REFCELL = eps
pgenerator.VALUE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
pgenerator.FUNCTION = pcallcontext_generator.FUNCTION
pcallcontext_generator.TARGET = pgenerator.FUNCTION
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$lookup(S.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("supplied53"))
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$heap_owners($heap_graph(S), HOBJECT n_generator) = 2
$heap_count(HOBJECT n_generator, $fiber_vm_nodes(pfibervm)) = 1
$node_children(S, HOBJECT n_generator) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
$task_nodes(FIBER_CONTINUE pfiberapi) = eps
$generator_resume_ids(S.TODO) = eps
$generator_saved_ids(S.FRAMES) = eps
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_generator_transfer(S_view)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S_view) = eps
$generator_owners_valid(S_view)
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
~$fiber_transfer_domain(S_view[.ACTIVEFIBER = eps])
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = (n_generator)])
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = (|S.OBJECTS|)])
H = $heap_graph(S)
pgeneratorop_wrong = pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]
pframe_wrong = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop_wrong) :: ptask_generator*]
pfibervm_wrong = pfibervm[.FRAMES = [pframe_wrong, pframe_root]]
S_wrong = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_wrong)])
$heap_graph(S_wrong) = H
~$fiber_vm_valid(S_wrong, pfibervm_wrong, (n_fiber), eps)
~$call_descriptors_valid(S_wrong)
pfibervm_target = pfibervm[.CURRENT = (pcallcontext_generator[.TARGET = pgeneratorop.SITE])]
S_target = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_target)])
$heap_graph(S_target) = H
~$fiber_vm_valid(S_target, pfibervm_target, (n_fiber), eps)
~$call_descriptors_valid(S_target)
S_phase = $generator_set(S, n_generator, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_phase) = H
~$fiber_vm_valid(S_phase, pfibervm, (n_fiber), eps)
~$call_descriptors_valid(S_phase)
~$generator_running_owners(S, S.ALLOCATIONS, [n_generator, n_generator])
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid(H)
""")

INJECTED = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext_generator)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
pfiber.VM = eps
pfiber.FINISH = eps
~pfiber.FAILED
~pfiber.RETURNED
pfibercaller.OBJECT = n_fiber
pfibercaller.PREVIOUS = eps
pfibercaller.API.START = eps
pfibercaller.API.SENT = (POBJECT n_given)
pfibercaller.API.SEQUENCE = pfiber.SEQUENCE
pfibercaller.VM.GLOBAL
pfibercaller.VM.TABLE = $empty_table()
pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_waiting*
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S.RESULT = KNOWN PNULL
S.HELD = eps
S.FRAMES = [pframe_generator, pframe_root]
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pframe_root.CONTEXT = eps
pframe_root.TODO = [FIBER_FINISH n_fiber]
n_generator = pgeneratorop.OBJECT
pgeneratorop.NAME = "current"
pgeneratorop.LINE = 19
pgeneratorop.LOOP = eps
pgeneratorop.ARGUMENTS = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.DELEGATE = eps
pgenerator.CLOSURE = eps
pgenerator.VALUE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
pgenerator.FUNCTION = pcallcontext_generator.FUNCTION
pcallcontext_generator.TARGET = pgenerator.FUNCTION
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$lookup(S_global.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("supplied53"))
$heap_owners($heap_graph(S), HOBJECT n_given) = 3
$heap_count(HOBJECT n_given, $task_nodes(THROW_SEARCH n_given)) = 1
$heap_count(HOBJECT n_given, $fiber_api_nodes(pfibercaller.API)) = 1
$heap_owners($heap_graph(S), HOBJECT n_generator) = 2
$generator_saved_fiber_ids(S) = eps
$generator_saved_ids(S.FRAMES) = [n_generator]
$generator_resume_pairs(S, S.CURRENT, S.FRAMES)
$fiber_generator_body_id(S) = (n_generator)
$fiber_generator_transfer(S)
$fiber_transfer_domain(S)
$fiber_api_valid(S, pfibercaller.API)
H = $heap_graph(S)
pgeneratorop_wrong = pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]
pframe_wrong = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop_wrong) :: ptask_generator*]
S_wrong = S[.FRAMES = [pframe_wrong, pframe_root]]
$heap_graph(S_wrong) = H
$fiber_generator_body_id(S_wrong) = eps
~$call_descriptors_valid(S_wrong)
S_target = S[.CURRENT = (pcallcontext_generator[.TARGET = pgeneratorop.SITE])]
$heap_graph(S_target) = H
$fiber_generator_body_id(S_target) = eps
~$call_descriptors_valid(S_target)
S_phase = $generator_set(S, n_generator, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_phase) = H
$fiber_generator_body_id(S_phase) = eps
~$call_descriptors_valid(S_phase)
~$fiber_generator_transfer(S[.ACTIVEFIBER = eps])
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid(H)
""")

EVENTS = {
    HANDLED: ['START|', 'CALL|', 'G|', 'pause53', '|', 'PAUSED|', '1', '|',
              'THROW|', 'INNER|', '1', '|', '1', '|', 'FINALLY|', 'CURRENT|',
              'yield53', '|', 'DELIVERED|', '1', '|', 'DONE|', '1', '|',
              'done53', '|', 'VALID|', '1', '|', 'AFTER-YIELD|', 'CLOSED|',
              '0', '|', '73', '|', 'GIVEN|', '1', '|', 'E'],
    UNHANDLED: ['START|', 'CALL|', 'G|', 'pause53', '|', 'PAUSED|', '1', '|',
                'THROW|', 'FINALLY|', 'OUTER|', '1', '|', '1', '|', '1', '|',
                'DONE|', '1', '|', 'CLOSED|', '0', '|', 'GIVEN|', '1', '|', 'E'],
}
CASES = {
    'generator-fiber-parked-handled-source': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*PARKED, *ENDING, events(EVENTS[HANDLED])],
    },
    'generator-fiber-injected-unhandled-source': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW) '
                  '-- if S.CURRENT = (pcallcontext_generator) '
                  '-- if $generator_context_operation(S, pcallcontext_generator) = (pgeneratorop)'),
        'checks': [*INJECTED, *ENDING, events(EVENTS[UNHANDLED])],
    },
}


def run(selected):
    assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())
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
