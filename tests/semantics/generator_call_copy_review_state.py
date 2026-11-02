#!/usr/bin/env python3
"""Check actual copied Closure identity, sibling selection and reference owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_copy_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i92-real-call-copied-closure-sibling-reference-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


COMMON = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.FRAME = eps
pgenerator.CLOSURE = (n_copy)
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
S.OBJECTS[n_copy] = REALCLOSURE pgenerator.FUNCTION eps eps
(HOBJECT n_copy) <- S.ALLOCATIONS
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
S.OBJECTS[n_source] = REALCLOSURE pgenerator.FUNCTION eps eps
$(n_source < n_copy)
~((HOBJECT n_source) <- S.ALLOCATIONS)
~$closure_callable(S, n_source)
$function_at(S.CLOSURETEMPLATES, pgenerator.FUNCTION) = (pfunction)
$target_function(S, CLOSURE_TARGET n_source) = (pfunction)
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
pfunction.SIGNATURE.BYREF
$function_generator(S, pfunction)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Active92R"))) = (porigin_active)
pclosurebinding.OBJECT = n_copy
pclosurebinding.LEXICAL = (porigin_active)
pclosurebinding.CALLED = (porigin_active)
pclosurebinding.RECEIVER = (n_a)
S.OBJECTS[n_a] = INSTANCE porigin_active
(HOBJECT n_a) <- S.ALLOCATIONS
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_binding_source_valid(S, pclosurebinding)
$binding_scope_valid(S, pclosurebinding)
$closure_callable(S, n_copy)
$generator_closure_valid(S, pgenerator)
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_a]
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token92R")
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$lookup(S.ENV, $ptascii("source")) = eps
$lookup(S.ENV, $ptascii("a")) = eps
$lookup(S.ENV, $ptascii("b")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = PNULL
$lookup(S.ENV, $ptascii("weakCopy")) = (n_weak_copy_cell)
S.STORE[n_weak_copy_cell] = DEFINED (POBJECT n_weak_copy)
$weakref_get(S, n_weak_copy) = POBJECT n_copy
$lookup(S.ENV, $ptascii("weakA")) = (n_weak_a_cell)
S.STORE[n_weak_a_cell] = DEFINED (POBJECT n_weak_a)
$weakref_get(S, n_weak_a) = POBJECT n_a
$lookup(S.ENV, $ptascii("weakB")) = (n_weak_b_cell)
S.STORE[n_weak_b_cell] = DEFINED (POBJECT n_weak_b)
$lookup(S.ENV, $ptascii("weakInput")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$lookup(S.ENV, $ptascii("other")) = (n_other_cell)
S.STORE[n_other_cell] = DEFINED (POBJECT n_other)
S.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator_other.PHASE = GENERATOR_FRESH
pgenerator_other.FUNCTION = pgenerator.FUNCTION
pgenerator_other.CLOSURE = (n_other_copy)
pgenerator_other.CREATION = eps
pgenerator_other.VALUE = eps
pgenerator_other.REFCELL = eps
pgenerator_other.FRAME = (pframe_other)
S.OBJECTS[n_other_copy] = REALCLOSURE pgenerator.FUNCTION eps eps
$(n_copy < n_other_copy)
(HOBJECT n_other_copy) <- S.ALLOCATIONS
$target_function(S, CLOSURE_TARGET n_other_copy) = (pfunction)
$closure_binding_at(S.CLOSUREBINDINGS, n_other_copy) = (pclosurebinding_other)
pclosurebinding_other.SOURCE = n_source
pclosurebinding_other.LEXICAL = (porigin_active)
pclosurebinding_other.CALLED = (porigin_active)
pclosurebinding_other.RECEIVER = (n_b)
pclosurebinding_other.SITE =/= pclosurebinding.SITE
S.OBJECTS[n_b] = INSTANCE porigin_active
(HOBJECT n_b) <- S.ALLOCATIONS
n_b =/= n_a
$weakref_get(S, n_weak_b) = POBJECT n_b
$closure_binding_source_valid(S, pclosurebinding_other)
$generator_closure_valid(S, pgenerator_other)
$generator_frame_valid(S, pgenerator_other, pframe_other)
pframe_other.CONTEXT = (pcallcontext_other)
pcallcontext_other.TARGET = CLOSURE_TARGET n_other_copy
pcallcontext_other.INSTANCE = (n_other_copy)
pcallcontext_other.RECEIVER = (n_b)
pcallcontext_other.LEXICAL_CLASS = (porigin_active)
pcallcontext_other.CALLED_CLASS = (porigin_active)
pcallcontext_other.FUNCTION = pgenerator.FUNCTION
pcallcontext_other.CALLSITE = (pclosurebinding_other.SITE)
pcallcontext_other.WRAPPER = eps
$node_children(S, HOBJECT n_other_copy) = [HOBJECT n_b]
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_other_copy) = 1
$heap_owners(H, HOBJECT n_a) = 1
$heap_owners(H, HOBJECT n_b) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HCELL n_cache) = 1
$call_descriptors_valid(S)
$heap_valid(H)
''')

PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

PARK = COMMON + checks(r'''
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GENERATORINPUTS = eps
pgenerator.PHASE = GENERATOR_RUNNING
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = CLOSURE_TARGET n_copy
pcallcontext_generator.INSTANCE = (n_copy)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = (n_a)
pcallcontext_generator.LEXICAL_CLASS = (porigin_active)
pcallcontext_generator.CALLED_CLASS = (porigin_active)
pcallcontext_generator.CALLSITE = (pclosurebinding.SITE)
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_copy]
$call_receiver_roots(pcallcontext_generator) = eps
pfibervm.FRAMES = pframe_send :: pframe_tail*
pframe_send.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_send*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
$weakref_get(S, n_weak_input) = POBJECT n_input
$object_name(S, n_input) = $ptascii("Input92R")
$heap_owners(H, HOBJECT n_input) = 1
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$heap_count(HOBJECT n_copy, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_a, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$eval_trace_preparser(S_live, (pcallcontext_generator), pframe_send) = eps
~$call_selected_valid(S_live, CLOSURE_TARGET n_other_copy, (pclosurebinding.SITE))
pgenerator_bad_copy = pgenerator[.CLOSURE = (n_other_copy)]
S_bad_copy = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_bad_copy)]
~$fiber_generator_callee_valid(S_bad_copy, pgenerator_bad_copy, pcallcontext_generator)
~$fiber_generator_transfer(S_bad_copy)
pgenerator_dead_source = pgenerator[.CLOSURE = (n_source)]
S_dead_source = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_dead_source)]
~$fiber_generator_callee_valid(S_dead_source, pgenerator_dead_source, pcallcontext_generator)
~$fiber_generator_transfer(S_dead_source)
pcallcontext_bad_receiver = pcallcontext_generator[.RECEIVER = (n_b)]
S_bad_receiver = S_live[.CURRENT = (pcallcontext_bad_receiver)]
~$fiber_generator_callee_valid(S_bad_receiver, pgenerator, pcallcontext_bad_receiver)
S_no_owner = S_live[.FRAMES = eps]
$fiber_generator_body_id(S_no_owner) = eps
~$fiber_generator_real_closure_valid(S_no_owner, pgenerator, pcallcontext_generator)
S_bad_cell = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cell, pgenerator, pcallcontext_generator)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4800)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 4800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.GENERATORINPUTS = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_other) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_other_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_a) <- S_done.ALLOCATIONS)
~((HOBJECT n_b) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_a <- S_done.DESTRUCTION.CALLED
n_b <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("weakInput")) = (n_cell) '
    '-- if S.STORE[n_cell] = DEFINED (POBJECT n_weak) '
    '-- if pconfigcall.OWNER = (n_weak) '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_g_cell) '
    '-- if S.STORE[n_g_cell] = DEFINED (POBJECT n_g) '
    '-- if S.OBJECTS[n_g] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')

CLOSED = COMMON + checks(r'''
S.ACTIVEFIBER = eps
pgenerator.PHASE = GENERATOR_CLOSED
$weakref_get(S, n_weak_input) = PNULL
$node_children(S, HOBJECT n_generator) = [HCELL n_cache, HOBJECT n_copy]
$generator_close_children(S, HOBJECT n_generator) = [HOBJECT n_copy, HCELL n_cache]
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
S_done = $drive_steps(S, 1800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_other) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_other_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_a) <- S_done.ALLOCATIONS)
~((HOBJECT n_b) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_a <- S_done.DESTRUCTION.CALLED
n_b <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i92-copied-closure-sibling-parked-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i92-copied-closure-sibling-closed-independent': {'source': ROW['source'], 'stage': CLOSED_STAGE, 'checks': CLOSED},
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
        passed = review.run(selected, process_seconds=600)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(peer_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  peer_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
