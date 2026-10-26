#!/usr/bin/env python3
"""Check a real method receiver in a parked VM and after unhandled retirement."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_method_transfer_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
HANDLED = 'review-generator-fiber-method-receiver-handled'
UNHANDLED = 'review-generator-fiber-method-receiver-unhandled'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join(
        'OUTPUT (' + json.dumps(list(part.encode())) + ')' for part in parts) + ']'


# Actual first native output, divided at the original echo operands.
PREFIX = ['START|', 'CALL|', 'GEN', '1', '|', 'PARK', '1', '1', '1', '|', 'INJECT|']
RETIRED_PREFIX = [*PREFIX, 'GEN-FINALLY', '1', '|', 'RECEIVER|']
EVENTS = {
    HANDLED: [*PREFIX, 'GEN-CAUGHT', '1', '1', '1', '|', 'GEN-FINALLY', '1', '|',
              'CURRENT', '1', '1', '|', 'CALL-FINALLY', '1', '|', 'REPLY', '1', '|',
              'FIBER', '1', '0', '|', 'FRETURN', '1', '|', 'LIVE', '1', '|',
              'GEN-END|', 'RECEIVER|', 'GRETURN', '1', '|', 'CLOSED', '1', '1', '|',
              'DROPPED', '1', '|', 'GIVEN', '1', '|E'],
    UNHANDLED: [*RETIRED_PREFIX, 'CALL-FINALLY', '0', '|', 'CALLER-CAUGHT', '1', '1', '1', '|',
                'FIBER', '1', '0', '|', 'LIVE', '0', '|', 'CLOSED', '1', '1', '|',
                'DROPPED', '1', '|', 'GIVEN', '1', '|E'],
}

GLOBAL = checks(r"""
S.COMPLETION = NORMAL
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("generator")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$lookup(S_global.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("given58"))
$lookup(S_global.ENV, $ptascii("receiver")) = eps
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.CLOSURE = eps
pgenerator.ACCESS = eps
H = $heap_graph(S)
""")

PARKED = checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = [pframe_generator, pframe_fiber]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause58"))
$value_nodes(pvalue_pause) = eps
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pframe_generator.ORIGIN = (pgeneratorop.SITE)
pcallcontext_callback.NAME = $ptascii("RunMethodReceiver58")
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.PARKED = eps
pgenerator.DELEGATE = eps
pgenerator.VALUE = eps
pgenerator.RETURN = eps
pgenerator.REFCELL = eps
pgenerator.BORROWED = eps
~pgenerator.PENDING_INIT
pcallcontext_generator.TARGET = METHOD_TARGET n_receiver pgenerator.FUNCTION
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = (n_receiver)
S.OBJECTS[n_receiver] = INSTANCE porigin_class
$object_name(S, n_receiver) = $ptascii("FiberMethodReceiver58")
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_class
pmethoddesc.VISIBILITY = PROPERTY_PUBLIC
~pmethoddesc.STATIC
~pmethoddesc.ABSTRACT
pcallcontext_generator.LEXICAL_CLASS = (porigin_class)
pcallcontext_generator.CALLED_CLASS = (porigin_class)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_receiver)
$node_children(S, HOBJECT n_weak) = eps
$node_children(S, HOBJECT n_receiver) = eps
$node_children(S, HOBJECT n_generator) = eps
$heap_owners(H, HOBJECT n_receiver) = 1
$heap_owners(H, HOBJECT n_generator) = 2
$heap_owners(H, HOBJECT n_given) = 1
$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibervm)) = 1
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver]
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
~(n_receiver <- S.DESTRUCTION.CALLED)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$call_current_valid(S_view)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_from_saved_fiber_claims(S) = eps
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
""")

# Constructed same-heap metadata controls confer no additional PHP source credit.
REFUSALS = checks(r"""
H_view = $heap_graph(S_view)
S_receiver = S_view[.CURRENT = (pcallcontext_generator[.RECEIVER = eps])]
$heap_graph(S_receiver) = H_view
~$fiber_generator_callee_valid(S_receiver, pgenerator, pcallcontext_generator[.RECEIVER = eps])
$fiber_generator_body_id(S_receiver) = eps
S_target = S_view[.CURRENT = (pcallcontext_generator[.TARGET = METHOD_TARGET n_generator pgenerator.FUNCTION])]
$heap_graph(S_target) = H_view
$fiber_generator_body_id(S_target) = eps
S_lexical = S_view[.CURRENT = (pcallcontext_generator[.LEXICAL_CLASS = eps])]
$heap_graph(S_lexical) = H_view
$fiber_generator_body_id(S_lexical) = eps
S_called = S_view[.CURRENT = (pcallcontext_generator[.CALLED_CLASS = eps])]
$heap_graph(S_called) = H_view
$fiber_generator_body_id(S_called) = eps
S_line = S_view[.CURRENT = (pcallcontext_generator[.LINE = $(pcallcontext_generator.LINE + 1)])]
$heap_graph(S_line) = H_view
$fiber_generator_body_id(S_line) = eps
S_closure = $generator_set(S_view, n_generator, pgenerator[.CLOSURE = (n_receiver)])
$heap_graph(S_closure) = H_view
$fiber_generator_body_id(S_closure) = eps
""")

RETIRED = checks(r"""
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
pfiber.VM = eps
pfibercaller.OBJECT = n_fiber
pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW)
pfibercaller.API.SENT = (POBJECT n_given)
S.CURRENT = (pcallcontext_callback)
pcallcontext_callback.TARGET = pcallcontext_callback.FUNCTION
pcallcontext_callback.INSTANCE = eps
pcallcontext_callback.RECEIVER = eps
S.FRAMES = [pframe_fiber]
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.KEY = eps
pgenerator.RETURN = eps
S.DESTRUCTION.CALLED = [n_receiver]
S.OBJECTS[n_receiver] = INSTANCE porigin_class
$object_name(S, n_receiver) = $ptascii("FiberMethodReceiver58")
~((HOBJECT n_receiver) <- S.ALLOCATIONS)
S.OBJECTS[n_weak] = WEAKREFERENCE eps
$weakref_get(S, n_weak) = PNULL
$node_children(S, HOBJECT n_generator) = eps
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_given) = 3
$heap_count(HOBJECT n_given, $task_nodes(THROW_SEARCH n_given)) = 1
$heap_count(HOBJECT n_given, $fiber_api_nodes(pfibercaller.API)) = 1
$fiber_api_valid(S, pfibercaller.API)
$generator_resume_ids(S.TODO) = eps
$generator_saved_fiber_ids(S) = eps
$generator_from_saved_fiber_claims(S) = eps
$call_current_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
""")

# Fixed points make these raw budgets the exact NORMAL public-drive definition.
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
$drive_steps(S, 2) = $drive_steps(S_one, 1)
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
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
n_receiver <- S_done.DESTRUCTION.CALLED
$throwable_field(S_done, n_given, "previous") = PNULL
$generator_saved_fiber_ids(S_done) = eps
""")

CASES = {
    'generator-fiber-method-parked-sole-receiver': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*GLOBAL, *PARKED, *REFUSALS, *ENDING, events('S_done', EVENTS[HANDLED])],
    },
    'generator-fiber-method-unhandled-receiver-retired': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) -- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if S.CURRENT = (pcallcontext_callback) '
                  '-- if pcallcontext_callback.NAME = $ptascii("RunMethodReceiver58") '
                  '-- if S_global = $global_table_view(S) '
                  '-- if $lookup(S_global.ENV, $ptascii("generator")) = (n_generator_cell) '
                  '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
                  '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
                  '-- if pgenerator.PHASE = GENERATOR_CLOSED '
                  '-- if S.DESTRUCTION.CALLED = [n_receiver] '
                  '-- if ~((HOBJECT n_receiver) <- S.ALLOCATIONS) '
                  '-- if $generator_resume_ids(S.TODO) = eps'),
        'checks': [*GLOBAL, *RETIRED, events('S', RETIRED_PREFIX), *ENDING,
                   events('S_done', EVENTS[UNHANDLED])],
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
