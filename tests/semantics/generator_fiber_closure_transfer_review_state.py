#!/usr/bin/env python3
"""Check captured Token and Closure callee ownership across real Fiber transfers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_closure_transfer_review_cases.json')
AUTHOR_CATALOG = Path(__file__).with_name('generator_fiber_closure_transfer_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, AUTHOR_CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
AUTHOR_ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[AUTHOR_CATALOG])}
HANDLED = 'review-generator-fiber-closure-callee-handled'
UNHANDLED = 'review-generator-fiber-closure-callee-unhandled'
REENTRY = 'generator-fiber-closure-reentry-next'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT (' + json.dumps(list(part.encode())) + ')' for part in parts) + ']'


# First native observations, split at the original echo operands.
PREFIX = ['START|', 'CALL|', 'GEN|', 'PARK', '1', '1', '1', '1', '|', 'INJECT|']
EVENTS = {
    HANDLED: [*PREFIX, 'GEN-CAUGHT', '1', '1', '1', '|', 'GEN-FINALLY|',
              'CURRENT', '1', '|', 'CALL-FINALLY|', 'REPLY', '1', '|',
              'FIBER', '1', '0', '|', 'FRETURN', '1', '|', 'OWNERS', '1', '1', '|',
              'GEN-END|', 'GRETURN', '1', '|', 'CLOSED', '1', '1', '1', '|',
              'TOKEN|', 'DROPPED', '1', '1', '|', 'GIVEN', '1', '|E'],
    UNHANDLED: [*PREFIX, 'GEN-FINALLY|', 'CALL-FINALLY|', 'CALLER-CAUGHT',
                '1', '1', '1', '|', 'FIBER', '1', '0', '|', 'OWNERS', '1', '1', '|',
                'CLOSED', '1', '1', '1', '|', 'TOKEN|', 'DROPPED', '1', '1', '|',
                'GIVEN', '1', '|E'],
    REENTRY: ['START|', 'GEN|', '1', 'PARK|', '1', '1', 'ERROR|', '1', '1',
              'RESUME|', '1', 'VALUE|', '1', 'RETURN|', '1', 'E'],
}


COMMON = checks(r"""
S.COMPLETION = NORMAL
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("weakFactory")) = (n_weak_callee_cell)
S.STORE[n_weak_callee_cell] = DEFINED (POBJECT n_weak_callee)
S.OBJECTS[n_weak_callee] = WEAKREFERENCE (n_callee)
$lookup(S_global.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
S.OBJECTS[n_weak_token] = WEAKREFERENCE (n_token)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
S_live.CURRENT = (pcallcontext_generator)
S_live.FRAMES = [pframe_generator, pframe_fiber]
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pframe_generator.ORIGIN = (pgeneratorop.SITE)
pcallcontext_callback.TARGET = CLOSURE_TARGET n_callback
pcallcontext_callback.INSTANCE = (n_callback)
n_callback =/= n_callee
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
n_generator = pgeneratorop.OBJECT
$lookup(S_global.ENV, $ptascii("generator")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.PARKED = eps
pgenerator.DELEGATE = eps
pgenerator.VALUE = eps
pgenerator.RETURN = eps
pgenerator.REFCELL = eps
pgenerator.BORROWED = eps
pgenerator.ACCESS = eps
~pgenerator.PENDING_INIT
pgenerator.CLOSURE = (n_callee)
S.OBJECTS[n_callee] = REALCLOSURE porigin_template ([DIRECT (POBJECT n_token)]) eps
pgenerator.FUNCTION = porigin_template
pcallcontext_generator.FUNCTION = porigin_template
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callee
pcallcontext_generator.INSTANCE = (n_callee)
$node_children(S, HOBJECT n_generator) = eps
$node_children(S, HOBJECT n_callee) = [HOBJECT n_token]
$object_name(S, n_token) = $ptascii("ClosureCaptureToken57")
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_generator) = 2
$heap_owners(H, HOBJECT n_callee) = 1
$heap_owners(H, HOBJECT n_token) = 1
$generator_closure_valid(S_live, pgenerator)
$call_current_valid(S_live)
$generator_resume_pairs(S_live, S_live.CURRENT, S_live.FRAMES)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
""")

# Callee mutations below are local identity/template/type refusal controls,
# not claims that their forged metadata is produced by a PHP source.
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
$string_bytes(pvalue_pause) = ($ptascii("pause57"))
$value_nodes(pvalue_pause) = eps
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
""") + COMMON + checks(r"""
$heap_owners(H, HOBJECT n_given) = 1
$generator_saved_fiber_ids(S) = [n_generator]
$generator_saved_fiber_ids(S_live) = eps
$foreach_aggregate_close_vm_ids(S, pfibervm) = [n_generator]
$generator_owners_valid(S_live)
S_main = S_live[.ACTIVEFIBER = eps]
~$fiber_generator_transfer(S_main)
S_target = S_live[.CURRENT = (pcallcontext_generator[.TARGET = CLOSURE_TARGET n_callback])]
$heap_graph(S_target) = $heap_graph(S_live)
~$fiber_generator_callee_valid(S_target, pgenerator, pcallcontext_generator[.TARGET = CLOSURE_TARGET n_callback])
$fiber_generator_body_id(S_target) = eps
S_callee = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator[.CLOSURE = (n_callback)])]
$heap_graph(S_callee) = $heap_graph(S_live)
$fiber_generator_body_id(S_callee) = eps
S_function = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator[.FUNCTION = pcallcontext_callback.FUNCTION])]
$heap_graph(S_function) = $heap_graph(S_live)
$fiber_generator_body_id(S_function) = eps
S_kind = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_callee, STDINSTANCE)]
$fiber_generator_body_id(S_kind) = eps
""")

INJECTED = checks(r"""
S_live = S
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
pfiber.VM = eps
pfibercaller.OBJECT = n_fiber
pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW)
pfibercaller.API.SENT = (POBJECT n_given)
""") + COMMON + checks(r"""
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

# NORMAL public drive equals this factored preprocessing and raw step budget.
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
~((HOBJECT n_callee) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$generator_saved_fiber_ids(S_done) = eps
""")

REENTRY_STAGE = ('S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
                 '-- if pgeneratorop.NAME = "next" -- if S.ACTIVEFIBER = eps '
                 '-- if S.CURRENT = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
                 '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                 '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                 '-- if pfiber.STATUS = FIBER_SUSPENDED')
NEXT_LINE = next(i for i, line in enumerate(AUTHOR_ROWS[REENTRY]['source'].splitlines(), 1)
                 if line.strip() == '$g->next();')
REENTRY_CHECKS = [f'pgeneratorop.LINE = {NEXT_LINE}'] + checks(r"""
S.COMPLETION = NORMAL
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.HELD = eps
S.GC.ACTIVE = eps
S.RESULT = KNOWN PNULL
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
n_generator = pgeneratorop.OBJECT
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.CLOSURE = (n_callee)
pgenerator.FRAME = eps
pgenerator.DELEGATE = eps
pgenerator.VALUE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callee
pcallcontext_generator.INSTANCE = (n_callee)
S.OBJECTS[n_callee] = REALCLOSURE pgenerator.FUNCTION ([DIRECT pvalue_capture]) eps
$string_bytes(pvalue_capture) = ($ptascii("cap57"))
$value_nodes(pvalue_capture) = eps
pfibervm.FRAMES = [pframe_generator, pframe_fiber]
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop_original) :: ptask_generator*
pframe_generator.ORIGIN = (pgeneratorop_original.SITE)
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pgeneratorop_original.OBJECT = n_generator
pgeneratorop_original.NAME = "current"
pgeneratorop_original.ARGUMENTS = eps
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.OBJECT = n_fiber
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_operation_valid(S, pgeneratorop)
~$generator_operation_valid(S, pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)])
$generator_operation_trace(S, pgeneratorop) = [ptraceframe_next]
ptraceframe_next.FILE = $call_sourcefile(S.FILES, pgeneratorop.SITE)
ptraceframe_next.LINE = pgeneratorop.LINE
ptraceframe_next.FUNCTION = $ptascii("next")
ptraceframe_next.CLASS = ($ptascii("Generator"))
ptraceframe_next.TYPE = ($ptascii("->"))
ptraceframe_next.ARGS = eps
ptraceframe_next.HASARGS
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$call_entry_check(S) = S
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S))) = S
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_error*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_generator)]
pdestructionoperation.PENDING = (n_error)
pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps eps
pdestructionoperation.VALUE = KNOWN PNULL
$destructor_release_valid(S_one, pdestructionrelease)
$destructor_operation_valid(S_one, pdestructionoperation)
S_one.OBJECTS[n_fiber] = FIBER pfiber
S_one.OBJECTS[n_generator] = GENERATOR pgenerator
S_one.OBJECTS[n_callee] = S.OBJECTS[n_callee]
$throwable_previous_id(S_one, n_error) = (n_initial)
$throwable_previous_id(S_one, n_initial) = eps
n_initial = |S.OBJECTS|
n_error = $(|S.OBJECTS| + 1)
|S_one.OBJECTS| = $(|S.OBJECTS| + 2)
$heap_owners($heap_graph(S_one), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_initial) = 1
$generator_saved_fiber_ids(S_one) = [n_generator]
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
""")
# Both Errors retain the same source-level NEXT site and an ordinary method trace.
for object_id, suffix in [('n_initial', 'initial'), ('n_error', 'outer')]:
    REENTRY_CHECKS += checks(f"""
$object_name(S_one, {object_id}) = $ptascii("Error")
$string_bytes($throwable_field(S_one, {object_id}, "message")) = ($ptascii("Cannot resume an already running generator"))
$throwable_field(S_one, {object_id}, "line") = PINT pgeneratorop.LINE
$string_bytes($throwable_field(S_one, {object_id}, "file")) = ($call_sourcefile(S.FILES, pgeneratorop.SITE))
$throwable_field(S_one, {object_id}, "trace") = PARRAY n_trace_{suffix}
S_one.ARRAYS[n_trace_{suffix}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_{suffix}))]
$entry_lookup(S_one.ARRAYS[n_frame_{suffix}].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("next")))
$entry_lookup(S_one.ARRAYS[n_frame_{suffix}].ITEMS, KSTRING $ptascii("class")) = (DIRECT (PSTRING $ptascii("Generator")))
$entry_lookup(S_one.ARRAYS[n_frame_{suffix}].ITEMS, KSTRING $ptascii("line")) = (DIRECT (PINT pgeneratorop.LINE))
""")
REENTRY_CHECKS += checks(r"""
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
~((HOBJECT n_callee) <- S_done.ALLOCATIONS)
~((HOBJECT n_error) <- S_done.ALLOCATIONS)
~((HOBJECT n_initial) <- S_done.ALLOCATIONS)
$generator_saved_fiber_ids(S_done) = eps
""")

CASES = {
    'generator-fiber-closure-callee-parked-handled': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*PARKED, *ENDING, events(EVENTS[HANDLED])],
    },
    'generator-fiber-closure-callee-injected-unhandled': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if $generator_active(S)'),
        'checks': [*INJECTED, *ENDING, events(EVENTS[UNHANDLED])],
    },
    'generator-fiber-closure-fresh-reentry-errors': {
        'source': AUTHOR_ROWS[REENTRY]['source'],
        'stage': REENTRY_STAGE,
        'checks': [*REENTRY_CHECKS, events(EVENTS[REENTRY])],
    },
}


def run(selected):
    assert all(''.join(parts) == (AUTHOR_ROWS if name == REENTRY else ROWS)[name]['native_stdout']
               for name, parts in EVENTS.items())
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
