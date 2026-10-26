#!/usr/bin/env python3
"""Reach helper-frame owners and real injection above a retained Generator resumer."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_helper_transfer_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
HANDLED = 'review-generator-fiber-helper-transfer-handled'
UNHANDLED = 'review-generator-fiber-helper-transfer-unhandled'
CURRENT_LINES = {name: next(i for i, line in enumerate(row['source'].splitlines(), 1)
                            if '$current = $g->current();' in line)
                 for name, row in ROWS.items()}


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT (' + json.dumps(list(part.encode())) + ')' for part in parts) + ']'


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
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
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
pfibervm.CURRENT = (pcallcontext_helper)
pcallcontext_helper.NAME = $ptascii("HelperTransferBody54")
pcallcontext_helper.TARGET = pcallcontext_helper.FUNCTION
pcallcontext_helper.INSTANCE = eps
pcallcontext_helper.CALLSITE = (porigin_helper)
pcallcontext_helper.EXTRA = eps
pfibervm.FRAMES = [pframe_helper, pframe_resumer, pframe_root]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.START = eps
pfiberapi.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause54"))
$value_nodes(pvalue_pause) = eps
pfiberapi.SEQUENCE = pfiber.SEQUENCE
pfiber.FINISH = eps
~pfiber.FAILED
~pfiber.RETURNED
pframe_helper.LOCALS = (psymboltable_generator)
pframe_helper.CONTEXT = (pcallcontext_generator)
pframe_helper.ORIGIN = (porigin_helper)
$generator_resume_ids(pframe_helper.TODO) = eps
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_resumer.CONTEXT = (pcallcontext_callback)
pframe_root.TODO = [FIBER_FINISH n_fiber]
pframe_root.CONTEXT = eps
n_generator = pgeneratorop.OBJECT
pgeneratorop.NAME = "current"
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
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("supplied54"))
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_helper_token_cell)
$lookup(psymboltable_generator.ENV, $ptascii("token")) = (n_generator_token_cell)
n_helper_token_cell =/= n_generator_token_cell
S.STORE[n_helper_token_cell] = DEFINED (POBJECT n_token)
S.STORE[n_generator_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("HelperTransferToken54")
$heap_owners($heap_graph(S), HOBJECT n_token) = 2
$heap_count(HCELL n_helper_token_cell, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HCELL n_generator_token_cell, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HCELL n_helper_token_cell) = 1
$heap_owners($heap_graph(S), HCELL n_generator_token_cell) = 1
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$weakref_get(S, n_weak) = POBJECT n_token
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
~$generator_active(S_view)
$generator_context_operation(S_view, pcallcontext_helper) = eps
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_generator_transfer(S_view)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S_view) = eps
$generator_owners_valid(S_view)
S_generator = $constant_frame_scope(S_view, pframe_helper, [pframe_resumer, pframe_root])
S_generator.CURRENT = (pcallcontext_generator)
S_generator.FRAMES = [pframe_resumer, pframe_root]
S_generator.ENV = psymboltable_generator.ENV
S_generator.STORE = S_view.STORE
S_generator.OBJECTS = S_view.OBJECTS
S_generator.ALLOCATIONS = S_view.ALLOCATIONS
$generator_active(S_generator)
$generator_context_operation(S_generator, pcallcontext_generator) = (pgeneratorop)
$fiber_generator_body_id(S_generator) = (n_generator)
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
H = $heap_graph(S)
pfibervm_origin = pfibervm[.FRAMES = [pframe_helper[.ORIGIN = eps], pframe_resumer, pframe_root]]
S_origin = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_origin)])
$heap_graph(S_origin) = H
~$fiber_vm_valid(S_origin, pfibervm_origin, (n_fiber), eps)
~$call_descriptors_valid(S_origin)
pfibervm_site = pfibervm[.CURRENT = (pcallcontext_helper[.CALLSITE = (pgeneratorop.SITE)])]
S_site = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_site)])
$heap_graph(S_site) = H
~$fiber_vm_valid(S_site, pfibervm_site, (n_fiber), eps)
~$call_descriptors_valid(S_site)
pfibervm_duplicate = pfibervm[.FRAMES = [pframe_helper[.TODO = (GENERATOR_RESUME pgeneratorop) :: pframe_helper.TODO], pframe_resumer, pframe_root]]
$generator_saved_ids(pfibervm_duplicate.FRAMES) = [n_generator, n_generator]
S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])
~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)
~$call_descriptors_valid(S_duplicate)
pfibervm_nested = pfibervm[.FRAMES = [pframe_helper[.TODO = (AT pfiberapi.SITE (GENERATOR_RESUME pgeneratorop)) :: pframe_helper.TODO], pframe_resumer, pframe_root]]
$generator_saved_ids(pfibervm_nested.FRAMES) = [n_generator]
~$generator_flat_frames(pfibervm_nested.FRAMES)
S_nested = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_nested)])
~$fiber_vm_valid(S_nested, pfibervm_nested, (n_fiber), eps)
~$call_descriptors_valid(S_nested)
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid(H)
""")

INJECTED = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext_helper)
pcallcontext_helper.NAME = $ptascii("HelperTransferBody54")
pcallcontext_helper.TARGET = pcallcontext_helper.FUNCTION
pcallcontext_helper.CALLSITE = (porigin_helper)
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
S.FRAMES = [pframe_helper, pframe_resumer, pframe_root]
pframe_helper.LOCALS = (psymboltable_generator)
pframe_helper.CONTEXT = (pcallcontext_generator)
pframe_helper.ORIGIN = (porigin_helper)
$generator_resume_ids(pframe_helper.TODO) = eps
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_resumer.CONTEXT = (pcallcontext_callback)
pframe_root.CONTEXT = eps
pframe_root.TODO = [FIBER_FINISH n_fiber]
n_generator = pgeneratorop.OBJECT
pgeneratorop.NAME = "current"
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
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("supplied54"))
$heap_owners($heap_graph(S), HOBJECT n_given) = 3
$heap_count(HOBJECT n_given, $task_nodes(THROW_SEARCH n_given)) = 1
$heap_count(HOBJECT n_given, $fiber_api_nodes(pfibercaller.API)) = 1
$lookup(S.ENV, $ptascii("token")) = (n_helper_token_cell)
$lookup(psymboltable_generator.ENV, $ptascii("token")) = (n_generator_token_cell)
n_helper_token_cell =/= n_generator_token_cell
S.STORE[n_helper_token_cell] = DEFINED (POBJECT n_token)
S.STORE[n_generator_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("HelperTransferToken54")
$heap_owners($heap_graph(S), HOBJECT n_token) = 2
$heap_owners($heap_graph(S), HOBJECT n_generator) = 2
$generator_saved_fiber_ids(S) = eps
$generator_saved_ids(S.FRAMES) = [n_generator]
~$generator_active(S)
$generator_context_operation(S, pcallcontext_helper) = eps
$generator_resume_pairs(S, S.CURRENT, S.FRAMES)
$fiber_generator_body_id(S) = (n_generator)
$fiber_generator_transfer(S)
$fiber_transfer_domain(S)
S_generator = $constant_frame_scope(S, pframe_helper, [pframe_resumer, pframe_root])
$generator_active(S_generator)
$generator_context_operation(S_generator, pcallcontext_generator) = (pgeneratorop)
$fiber_generator_body_id(S_generator) = (n_generator)
$fiber_api_valid(S, pfibercaller.API)
H = $heap_graph(S)
S_origin = S[.FRAMES = [pframe_helper[.ORIGIN = eps], pframe_resumer, pframe_root]]
$heap_graph(S_origin) = H
$fiber_generator_body_id(S_origin) = eps
~$call_descriptors_valid(S_origin)
S_site = S[.CURRENT = (pcallcontext_helper[.CALLSITE = (pgeneratorop.SITE)])]
$heap_graph(S_site) = H
$fiber_generator_body_id(S_site) = eps
~$call_descriptors_valid(S_site)
S_nested = S[.FRAMES = [pframe_helper[.TODO = (AT pgeneratorop.SITE (GENERATOR_RESUME pgeneratorop)) :: pframe_helper.TODO], pframe_resumer, pframe_root]]
$generator_saved_ids(S_nested.FRAMES) = [n_generator]
~$generator_flat_frames(S_nested.FRAMES)
$fiber_generator_body_id(S_nested) = eps
~$call_descriptors_valid(S_nested)
~$fiber_generator_transfer(S[.ACTIVEFIBER = eps])
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid(H)
""")

EVENTS = {
    HANDLED: ['START|', 'FIBER|', 'GEN|', 'HELPER|', 'pause54', '|', 'PARKED|',
              '1', '|', '1', '|', 'INJECT|', 'HELPER-FINALLY|', 'GEN-CAUGHT|',
              '1', '|', '1', '|', 'GEN-FINALLY|', 'CURRENT|', '1', '|', 'REPLY|',
              '1', '|', 'FIBER-DONE|', '1', '|', '1', '|', 'LIVE|', '1', '|',
              'GEN-END|', 'TOKEN|', 'GEN-DONE|', '0', '|', '1', '|', 'DROPPED|',
              '1', '|', 'GIVEN|', '1', '|', 'E'],
    UNHANDLED: ['START|', 'FIBER|', 'GEN|', 'HELPER|', 'pause54', '|', 'PARKED|',
                '1', '|', '1', '|', 'INJECT|', 'HELPER-FINALLY|', 'GEN-FINALLY|',
                'TOKEN|', 'OUTER|', '1', '|', '1', '|', '1', '|', 'FIBER-DONE|',
                '1', '|', 'GEN-DONE|', '0', '|', 'DROPPED|', '1', '|', 'GIVEN|',
                '1', '|', 'E'],
}
CASES = {
    'generator-fiber-helper-parked-handled': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*PARKED, f'pgeneratorop.LINE = {CURRENT_LINES[HANDLED]}',
                   *ENDING, events(EVENTS[HANDLED])],
    },
    'generator-fiber-helper-injected-unhandled': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW) '
                  '-- if S.CURRENT = (pcallcontext_helper) '
                  '-- if pcallcontext_helper.NAME = $ptascii("HelperTransferBody54")'),
        'checks': [*INJECTED, f'pgeneratorop.LINE = {CURRENT_LINES[UNHANDLED]}',
                   *ENDING, events(EVENTS[UNHANDLED])],
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
