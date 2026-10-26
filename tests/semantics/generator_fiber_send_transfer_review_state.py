#!/usr/bin/env python3
"""Check the sole native SEND buffer across parking and injected unwinding."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_send_transfer_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
HANDLED = 'review-generator-fiber-send-transfer-buffer-handled'
UNHANDLED = 'review-generator-fiber-send-transfer-buffer-unhandled'
SEND_LINES = {name: next(i for i, line in enumerate(row['source'].splitlines(), 1)
                        if '->send(' in line) for name, row in ROWS.items()}


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT (' + json.dumps(list(part.encode())) + ')' for part in parts) + ']'


# Actual native output, split at the original source echo operands.
PREFIX = ['PRIME', 'GEN|', '1', '|', 'START|', 'CALL|', 'NEW|',
          'RECEIVED', '1', '|', 'PARK', '1', '1', '1', '|', 'INJECT|']
EVENTS = {
    HANDLED: [*PREFIX, 'GEN-CAUGHT', '1', '1', '1', '|', 'GEN-FINALLY|',
              'TOKEN|', 'SEND-RESULT', '1', '|', 'CALL-FINALLY|', 'REPLY',
              '1', '|', 'FIBER', '1', '0', '|', 'FRETURN', '1', '|',
              'GVALID', '1', '1', '|', 'GEN-END|', 'GRETURN', '1', '|',
              'CLOSED', '1', '1', '|', 'GIVEN', '1', '|E'],
    UNHANDLED: [*PREFIX, 'GEN-FINALLY|', 'TOKEN|', 'CALL-FINALLY|',
                'CALLER-CAUGHT', '1', '1', '1', '|', 'FIBER', '1', '0', '|',
                'GVALID', '0', '1', '|', 'CLOSED', '1', '1', '|',
                'GIVEN', '1', '|E'],
}


def body(name):
    return checks(f"""
S.COMPLETION = NORMAL
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("given56"))
S_live.CURRENT = (pcallcontext_generator)
pcallcontext_generator.NAME = $ptascii("sendTransferBody56")
S_live.FRAMES = [pframe_generator, pframe_fiber]
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pframe_generator.ORIGIN = (pgeneratorop.SITE)
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pframe_fiber.CONTEXT = eps
n_generator = pgeneratorop.OBJECT
$lookup(S_global.ENV, $ptascii("generator")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
pgeneratorop.NAME = "send"
pgeneratorop.LINE = {SEND_LINES[name]}
pgeneratorop.ARGUMENTS = [POBJECT n_token]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_token]
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.PARKED = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
pgenerator.REFCELL = eps
pgenerator.BORROWED = eps
pgenerator.CLOSURE = eps
pgenerator.ACCESS = eps
~pgenerator.PENDING_INIT
pgenerator.FUNCTION = pcallcontext_generator.FUNCTION
pcallcontext_generator.TARGET = pcallcontext_generator.FUNCTION
pcallcontext_generator.INSTANCE = eps
$object_name(S, n_token) = $ptascii("SendTransferToken56")
$node_children(S, HOBJECT n_token) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_generator) = 2
$generator_resume_ids(S_live.TODO) = eps
$generator_saved_ids(S_live.FRAMES) = [n_generator]
$generator_resume_pairs(S_live, S_live.CURRENT, S_live.FRAMES)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
""")


# Local malformed-arity/source controls retain their explicit scope. Replacing
# Given's object slot with a second VM is constructed duplicate-carrier refusal,
# not a source claim that PHP can copy a Fiber.
PARKED = checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause56"))
$value_nodes(pvalue_pause) = eps
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
""") + body(HANDLED) + checks(r"""
$heap_owners(H, HOBJECT n_given) = 1
$heap_count(HOBJECT n_token, $fiber_vm_nodes(pfibervm)) = 1
$generator_saved_fiber_ids(S) = [n_generator]
$generator_from_saved_fiber_claims(S) = eps
$foreach_aggregate_close_vm_ids(S, pfibervm) = [n_generator]
$generator_saved_fiber_ids(S_live) = eps
$generator_owners_valid(S_live)
S_main = S_live[.ACTIVEFIBER = eps]
~$fiber_generator_transfer(S_main)
S_two = S_live[.FRAMES = [pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = [POBJECT n_token, PNULL]]) :: ptask_generator*], pframe_fiber]]
$heap_graph(S_two) = $heap_graph(S_live)
$fiber_generator_body_id(S_two) = eps
S_zero_args = S_live[.FRAMES = [pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = eps]) :: ptask_generator*], pframe_fiber]]
$fiber_generator_body_id(S_zero_args) = eps
S_method = S_live[.FRAMES = [pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "current"]) :: ptask_generator*], pframe_fiber]]
$heap_graph(S_method) = $heap_graph(S_live)
$fiber_generator_body_id(S_method) = eps
S_line = S_live[.FRAMES = [pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]) :: ptask_generator*], pframe_fiber]]
$heap_graph(S_line) = $heap_graph(S_live)
$fiber_generator_body_id(S_line) = eps
S_pending = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator[.PENDING_INIT = true])]
$fiber_generator_body_id(S_pending) = eps
S_duplicate = S[.OBJECTS = $object_set(S.OBJECTS, n_given, FIBER pfiber)]
$generator_saved_fiber_ids(S_duplicate) = [n_generator, n_generator]
~$generator_owners_valid(S_duplicate)
""")

INJECTED = checks(r"""
S_live = S
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
pfiber.VM = eps
pfibercaller.OBJECT = n_fiber
pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW)
pfibercaller.API.SENT = (POBJECT n_given)
""") + body(UNHANDLED) + checks(r"""
$heap_owners(H, HOBJECT n_given) = 3
$heap_count(HOBJECT n_given, $task_nodes(THROW_SEARCH n_given)) = 1
$heap_count(HOBJECT n_given, $fiber_api_nodes(pfibercaller.API)) = 1
$fiber_api_valid(S, pfibercaller.API)
$generator_saved_fiber_ids(S) = eps
$generator_from_saved_fiber_claims(S) = eps
S_origin = S[.FRAMES = [pframe_generator[.ORIGIN = eps], pframe_fiber]]
$heap_graph(S_origin) = H
$fiber_generator_body_id(S_origin) = eps
""")

# At NORMAL inputs, these fixed points make raw budget comparisons exactly the
# public drive definition in40-control, without repeating its preprocessing.
ENDING = checks(r"""
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
S_two_budget = $drive_steps(S_one, 1)
$drive_steps(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
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
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$generator_saved_fiber_ids(S_done) = eps
""")

CASES = {
    'generator-fiber-send-sole-buffer-parked-handled': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*PARKED, *ENDING, events(EVENTS[HANDLED])],
    },
    'generator-fiber-send-sole-buffer-injected-unhandled': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if S.CURRENT = (pcallcontext_generator) '
                  '-- if pcallcontext_generator.NAME = $ptascii("sendTransferBody56")'),
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
        passed = review.run(selected, process_seconds=240)
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
