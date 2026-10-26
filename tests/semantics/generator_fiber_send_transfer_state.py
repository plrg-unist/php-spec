#!/usr/bin/env python3
"""Reach real SEND buffers, delivered CVs and returned Generator/Fiber values."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_send_transfer_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
CV = 'generator-fiber-send-delivered-cv'
OBJECT = 'generator-fiber-send-object-return'
PARTS = {
    CV: ['SEED|','1','START|','CALL|','VALUE|','1','1','PARKED|','1','1',
         'RESUME|','REPLY|','1','BUFFER|','1','D|','SEND|','1','1','1',
         'FIBER|','1','BODY-END|','RETURN|','1','E'],
    OBJECT: ['SEED|','1','START|','CALL|','VALUE|','1','1','PARKED|','1','1',
             'RESUME|','REPLY|','1','1','RETURNED|','1','BODY-END|',
             'CLOSED|','1','CACHE|','1','D|','FINAL|','1','E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in PARTS.items())


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(name):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT (' + json.dumps(list(part.encode())) + ')' for part in PARTS[name]) + ']'


PARK_STAGE = ('S.ACTIVEFIBER = eps -- if S.CURRENT = eps '
              '-- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
              '-- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPENDED '
              '-- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
              '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
              '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
              '-- if pfiber.STATUS = FIBER_SUSPENDED')
RETURN_STAGE = ('S.ACTIVEFIBER = eps -- if S.CURRENT = eps '
                '-- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
                '-- if $lookup(S.ENV, $ptascii("result")) = (n_result_cell) '
                '-- if S.STORE[n_result_cell] = DEFINED (POBJECT n_token) '
                '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
                '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
                '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
                '-- if pgenerator.PHASE = GENERATOR_PAUSED')
COMMON = checks(r'''
S.COMPLETION = NORMAL
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$lookup(S.ENV, $ptascii("payload")) = eps
$object_name(S, n_token) = $ptascii("SendToken56")
$node_children(S, HOBJECT n_weak) = eps
$weakref_get(S, n_weak) = POBJECT n_token
~(n_token <- S.DESTRUCTION.CALLED)
H = $heap_graph(S)
$call_descriptors_valid(S)
$heap_valid(H)
''')
PARKED = checks(r'''
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.NAME = $ptascii("Body56")
pfibervm.FRAMES = [pframe_send, pframe_base]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.SENT = (PSTRING_CARRIER INTERNED_STRING $ptascii("pause"))
pframe_send.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_send*
pframe_send.CONTEXT = (pcallcontext_callback)
pcallcontext_callback.NAME = $ptascii("Run56")
pframe_base.TODO = [FIBER_FINISH n_fiber]
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_token]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = (n_received)
S.STORE[n_received] = DEFINED (POBJECT n_token)
$node_children(S, HCELL n_received) = [HOBJECT n_token]
$heap_owners(H, HCELL n_received) = 1
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HOBJECT n_generator) = 2
$node_children(S, HOBJECT n_generator) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_token]
$heap_count(HOBJECT n_token, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HCELL n_received, $fiber_vm_nodes(pfibervm)) = 1
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]
$generator_active(S_view)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S_view) = eps
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
''')
# Constructed metadata/occurrence counterexamples; no extra source coverage.
REFUSALS = checks(r'''
S_zero_arg = S_view[.FRAMES = [pframe_send[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = eps]) :: ptask_send*], pframe_base]]
$fiber_generator_body_id(S_zero_arg) = eps
S_two_args = S_view[.FRAMES = [pframe_send[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = [POBJECT n_token, POBJECT n_token]]) :: ptask_send*], pframe_base]]
$fiber_generator_body_id(S_two_args) = eps
S_current = S_view[.FRAMES = [pframe_send[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "current"]) :: ptask_send*], pframe_base]]
$fiber_generator_body_id(S_current) = eps
S_line = S_view[.FRAMES = [pframe_send[.TODO = (GENERATOR_RESUME pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]) :: ptask_send*], pframe_base]]
$heap_graph(S_line) = $heap_graph(S_view)
$fiber_generator_body_id(S_line) = eps
S_duplicate = S[.OBJECTS = $object_set(S.OBJECTS, n_weak, FIBER pfiber)]
$generator_saved_fiber_ids(S_duplicate) = [n_generator, n_generator]
~$generator_owners_valid(S_duplicate)
''')
RETURNED = checks(r'''
$lookup(S.ENV, $ptascii("f")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.RETURNED
~pfiber.FAILED
pfiber.VM = eps
pfiber.VALUE = POBJECT n_token
pgenerator.FRAME = (pframe_generator)
pgenerator.VALUE = (POBJECT n_token)
pgenerator.RETURN = eps
pframe_generator.LOCALS = (psymboltable_generator)
$lookup(psymboltable_generator.ENV, $ptascii("received")) = (n_received)
S.STORE[n_received] = DEFINED (POBJECT n_token)
$heap_owners(H, HCELL n_received) = 1
$heap_owners(H, HCELL n_result_cell) = 1
$heap_owners(H, HOBJECT n_token) = 4
$heap_count(HOBJECT n_token, $node_children(S, HOBJECT n_generator)) = 1
$heap_count(HCELL n_received, $node_children(S, HOBJECT n_generator)) = 1
$heap_count(HOBJECT n_token, $node_children(S, HOBJECT n_fiber)) = 1
$generator_saved_fiber_ids(S) = eps
$generator_saved_ids(S.FRAMES) = eps
''')
ENDING = checks(r'''
$call_entry_check(S) = S
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S))) = S
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$call_entry_check(S_one) = S_one
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S_one))) = S_one
$drive_steps(S, 2) = $drive_steps(S_one, 1)
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
S_done.HELD = eps
n_token <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
$generator_saved_fiber_ids(S_done) = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')
CASES = {
    'generator-fiber-send-delivered-cv-buffer': {
        'source': ROWS[CV]['source'], 'stage': PARK_STAGE,
        'checks': [*COMMON, *PARKED, *REFUSALS, *ENDING, events(CV)],
    },
    'generator-fiber-send-returned-object-owners': {
        'source': ROWS[OBJECT]['source'], 'stage': RETURN_STAGE,
        'checks': [*COMMON, *RETURNED, *ENDING, events(OBJECT)],
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
