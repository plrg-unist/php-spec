#!/usr/bin/env python3
"""Check captured method Generator physical Closure and receiver owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_captured_method_body_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

FIRSTCLASS = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.RETURN = eps
pgenerator.CLOSURE = (n_callback)
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
(HOBJECT n_callback) <- S.ALLOCATIONS
$object_body(S.OBJECTS[n_callback]) = METHODCLOSURE pgenerator.FUNCTION porigin_capture_site porigin_requested pmethodcapture?
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base86A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child86A"))) = (porigin_child)
$closure_scope_at(S.CLOSURESCOPES, n_callback) = (pclosurescope)
pclosurescope.OBJECT = n_callback
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_child
pclosurescope.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_child
(HOBJECT n_maker) <- S.ALLOCATIONS
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_current :: pframe_tail*
pframe_current.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callback
pcallcontext_generator.INSTANCE = (n_callback)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_child)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callback]
$call_receiver_roots(pcallcontext_generator) = eps
$node_children(S, HOBJECT n_generator) = eps
$node_children(S, HOBJECT n_callback) = [HOBJECT n_maker]
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_callback) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_count(HOBJECT n_callback, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 0
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("callback")) = eps
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_factory_evidence_current(S_live) = (CLOSURE_SCOPE pclosurescope)
$generator_captured_factory_valid(S_live, pclosurescope, pgenerator.FUNCTION)
$fiber_generator_method_closure_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$call_descriptors_valid(S)
$heap_valid(H)
pcallcontext_bad_instance = pcallcontext_generator[.INSTANCE = eps]
S_bad_instance = S_live[.CURRENT = (pcallcontext_bad_instance)]
~$fiber_generator_method_closure_valid(S_bad_instance, pgenerator, pcallcontext_bad_instance)
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_base)]
S_bad_called = S_live[.CURRENT = (pcallcontext_bad_called)]
~$fiber_generator_method_closure_valid(S_bad_called, pgenerator, pcallcontext_bad_called)
S_dead_receiver = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_method_closure_valid(S_dead_receiver, pgenerator, pcallcontext_generator)
pgenerator_missing = pgenerator[.CLOSURE = eps]
~$fiber_generator_method_closure_valid(S_live, pgenerator_missing, pcallcontext_generator)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_method_closure_valid(S_no_owner, pgenerator, pcallcontext_generator)
S_done = $drive_steps(S, 1600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_callback) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
""")

STORAGE_STAGE = (
    'S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_tail* '
    '-- if pgenstorage.NEXT = 1 '
    '-- if S.OBJECTS[pgenstorage.OBJECT] = GENERATOR pgenerator')

ARRAY_STORAGE = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.FRAME = eps
pgenerator.CREATION = eps
pgenerator.CLOSURE = (n_callback)
(HOBJECT pgenstorage.OBJECT) <- S.ALLOCATIONS
S.OBJECTS[n_callback] = ARRAYMETHODCLOSURE pcalltarget parrayselection pmethodcapture?
~((HOBJECT n_callback) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_callback) = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base86B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child86B"))) = (porigin_child)
parrayselection.NAME = $ptascii("stream")
parrayselection.REQUESTED = porigin_child
$generator_captured_factory_scope(S, n_callback) = (pclosurescope)
pclosurescope.OBJECT = n_callback
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_child
pclosurescope.RECEIVER = (n_maker)
pclosurescope.CREATION = eps
S.OBJECTS[n_maker] = INSTANCE porigin_child
~((HOBJECT n_maker) <- S.ALLOCATIONS)
n_maker <- S.DESTRUCTION.CALLED
$target_function(S, CLOSURE_TARGET n_callback) = eps
$generator_captured_factory_valid(S, pclosurescope, pgenerator.FUNCTION)
$generator_storage_closure_borrowed(S, pgenerator)
$generator_storage_method_history(S, pgenerator)
$generator_storage_history(S, pgenerator)
$generator_closure_valid(S, pgenerator)
$generator_storage_basic(S, pgenstorage)
$generator_storage_valid(S, pgenstorage)
$generator_storage_state_valid(S)
$call_task_valid(S, GENERATOR_STORAGE_STEP pgenstorage)
$node_children(S, HOBJECT pgenstorage.OBJECT) = $generator_storage_remaining(pgenerator, 1)
H = $heap_graph(S)
$heap_owners(H, HOBJECT pgenstorage.OBJECT) = 1
$heap_owners(H, HOBJECT n_callback) = 0
$heap_owners(H, HOBJECT n_maker) = 0
pgenstorage_zero = pgenstorage[.NEXT = 0]
S_zero_slot = S[.TODO = (GENERATOR_STORAGE_STEP pgenstorage_zero) :: ptask_tail*]
~$generator_storage_closure_borrowed(S_zero_slot, pgenerator)
~$generator_storage_method_history(S_zero_slot, pgenerator)
~$generator_closure_valid(S_zero_slot, pgenerator)
S_no_storage = S[.TODO = ptask_tail*]
~$generator_storage_method_history(S_no_storage, pgenerator)
~$generator_closure_valid(S_no_storage, pgenerator)
pgenstorage.ORIGIN = (porigin_storage)
parrayselection_bad_site = parrayselection[.SITE = porigin_storage]
S_bad_site = S[.OBJECTS = $object_set(S.OBJECTS, n_callback, ARRAYMETHODCLOSURE pcalltarget parrayselection_bad_site pmethodcapture?)]
~$generator_storage_method_history(S_bad_site, pgenerator)
parrayselection_bad_name = parrayselection[.NAME = $ptascii("bad")]
S_bad_name = S[.OBJECTS = $object_set(S.OBJECTS, n_callback, ARRAYMETHODCLOSURE pcalltarget parrayselection_bad_name pmethodcapture?)]
~$generator_storage_method_history(S_bad_name, pgenerator)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Other86B"))) = (porigin_other)
$effective_method(S, porigin_other, $ptascii("bad"), |S.CLASSES|) = (pmethoddesc_other)
pgenerator_wrong = pgenerator[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN]
S_wrong = S[.OBJECTS = $object_set(S.OBJECTS, pgenstorage.OBJECT, GENERATOR pgenerator_wrong)]
~$generator_storage_method_history(S_wrong, pgenerator_wrong)
$call_descriptors_valid(S)
$heap_valid(H)
S_done = $drive_steps(S, 800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
$heap_valid($heap_graph(S_done))
""")

STATIC_PARK = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GENERATORINPUTS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.CLOSURE = (n_callback)
pgenerator.CREATION = eps
S.OBJECTS[n_callback] = STRINGMETHODCLOSURE pcalltarget pstringselection
(HOBJECT n_callback) <- S.ALLOCATIONS
pstringselection.ORIGINAL = $ptascii("Child86C::stream")
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base86C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child86C"))) = (porigin_child)
pstringselection.REQUESTED = porigin_child
$closure_scope_at(S.CLOSURESCOPES, n_callback) = (pclosurescope)
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_child
pclosurescope.RECEIVER = eps
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callback
pcallcontext_generator.INSTANCE = (n_callback)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_child)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.WRAPPER = eps
pfibervm.FRAMES = pframe_current :: pframe_tail*
pframe_current.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callback]
$node_children(S, HOBJECT n_callback) = eps
$node_children(S, HOBJECT n_generator) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_callback) = 1
$lookup(S.ENV, $ptascii("callback")) = eps
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_factory_evidence_current(S_live) = (CLOSURE_SCOPE pclosurescope)
$generator_captured_factory_valid(S_live, pclosurescope, pgenerator.FUNCTION)
$fiber_generator_method_closure_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
pstringselection_bad = pstringselection[.ORIGINAL = $ptascii("Other86C::bad")]
S_bad_string = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_callback, STRINGMETHODCLOSURE pcalltarget pstringselection_bad)]
~$fiber_generator_method_closure_valid(S_bad_string, pgenerator, pcallcontext_generator)
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_base)]
S_bad_called = S_live[.CURRENT = (pcallcontext_bad_called)]
~$fiber_generator_method_closure_valid(S_bad_called, pgenerator, pcallcontext_bad_called)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_method_closure_valid(S_no_owner, pgenerator, pcallcontext_generator)
$call_descriptors_valid(S)
$heap_valid(H)
S_done = $drive_steps(S, 1600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
$heap_valid($heap_graph(S_done))
~((HOBJECT n_callback) <- S_done.ALLOCATIONS)
""")

CASES = {
    'i86-firstclass-captured-parked-current': {
        'source': ROWS['i86-captured-method-firstclass-closed']['source'],
        'stage': PARK_STAGE, 'checks': FIRSTCLASS},
    'i86-array-captured-storage-consumed': {
        'source': ROWS['i86-captured-method-array-retarget']['source'],
        'stage': STORAGE_STAGE, 'checks': ARRAY_STORAGE},
    'i86-string-captured-parked-current': {
        'source': ROWS['i86-captured-method-string-static']['source'],
        'stage': PARK_STAGE, 'checks': STATIC_PARK},
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
        passed = review.run(selected, process_seconds=300)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
