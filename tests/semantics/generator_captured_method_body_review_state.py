#!/usr/bin/env python3
"""Check the actual bound Closure, borrowed This and reference-cache owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_captured_method_body_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i86-bound-fromcallable-reference-abort-independent')
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
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
pgenerator.CLOSURE = (n_callback)
pgenerator.ACCESS = eps
pgenerator.CREATION = eps
$(n_callback < |S.OBJECTS|)
(HOBJECT n_callback) <- S.ALLOCATIONS
S.OBJECTS[n_callback] = BOUNDFAKECLOSURE pboundfake
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base86R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child86R"))) = (porigin_child)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf86R"))) = (porigin_leaf)
pboundfake.SCOPE = BIND_CLASS porigin_base
pboundfake.CALLED = BIND_CLASS porigin_leaf
pboundfake.RECEIVER = (n_new)
S.OBJECTS[n_new] = INSTANCE porigin_leaf
(HOBJECT n_new) <- S.ALLOCATIONS
pboundfake.SOURCE = n_original
$(n_original < n_callback)
S.OBJECTS[n_original] = FROMCALLABLECLOSURE pfrommethod
pfrommethod.FUNCTION = pgenerator.FUNCTION
~((HOBJECT n_original) <- S.ALLOCATIONS)
pboundfake.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_original
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_child
pclosurescope_original.RECEIVER = (n_old)
S.OBJECTS[n_old] = INSTANCE porigin_child
~((HOBJECT n_old) <- S.ALLOCATIONS)
$generator_captured_factory_scope(S, n_original) = (pclosurescope_original)
$generator_captured_factory_valid(S, pclosurescope_original, pgenerator.FUNCTION)
$generator_captured_factory_scope(S, n_callback) = ({OBJECT n_callback, LEXICAL porigin_base, CALLED porigin_leaf, RECEIVER (n_new), CREATION eps})
$closure_scope_at(S.CLOSURESCOPES, n_callback) = eps
$bound_fake_valid(S, n_callback)
$target_function(S, CLOSURE_TARGET n_callback) = (pfunction)
pfunction.ORIGIN = pgenerator.FUNCTION
pfunction.SIGNATURE.BYREF
$function_generator(S, pfunction)
$generator_closure_valid(S, pgenerator)
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token86R")
$node_children(S, HOBJECT n_callback) = [HOBJECT n_new]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$lookup(S.ENV, $ptascii("original")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("callback")) = eps
$lookup(S.ENV, $ptascii("new")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_callback) = 1
$heap_owners(H, HOBJECT n_new) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_original) = 0
$heap_owners(H, HOBJECT n_old) = 0
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = PNULL
$lookup(S.ENV, $ptascii("weakOriginal")) = (n_weak_original_cell)
S.STORE[n_weak_original_cell] = DEFINED (POBJECT n_weak_original)
$weakref_get(S, n_weak_original) = PNULL
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
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callback
pcallcontext_generator.INSTANCE = (n_callback)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_new)
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callback]
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
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_cache)
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
$object_name(S, n_input) = $ptascii("Input86R")
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$heap_owners(H, HCELL n_cache) = 2
$heap_owners(H, HOBJECT n_input) = 1
$heap_count(HOBJECT n_callback, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_new, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_factory_evidence_current(S_live) = (CLOSURE_SCOPE pclosurescope)
pclosurescope.OBJECT = n_callback
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = (n_new)
pclosurescope.CREATION = eps
$generator_captured_factory_valid(S_live, pclosurescope, pgenerator.FUNCTION)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$generator_owners_valid(S)
pgenerator_missing = pgenerator[.CLOSURE = eps]
~$fiber_generator_callee_valid(S_live, pgenerator_missing, pcallcontext_generator)
~$fiber_generator_cached_reference_valid(S_live, pgenerator_missing, pcallcontext_generator)
pcallcontext_bad_instance = pcallcontext_generator[.INSTANCE = (n_original)]
S_bad_instance = S_live[.CURRENT = (pcallcontext_bad_instance)]
~$fiber_generator_callee_valid(S_bad_instance, pgenerator, pcallcontext_bad_instance)
pcallcontext_bad_receiver = pcallcontext_generator[.RECEIVER = (n_old)]
S_bad_receiver = S_live[.CURRENT = (pcallcontext_bad_receiver)]
~$fiber_generator_callee_valid(S_bad_receiver, pgenerator, pcallcontext_bad_receiver)
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_child)]
S_bad_called = S_live[.CURRENT = (pcallcontext_bad_called)]
~$fiber_generator_callee_valid(S_bad_called, pgenerator, pcallcontext_bad_called)
pboundfake_cycle = pboundfake[.SOURCE = n_callback]
S_cycle = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_callback, BOUNDFAKECLOSURE pboundfake_cycle)]
~$bound_fake_valid(S_cycle, n_callback)
~$generator_closure_valid(S_cycle, pgenerator)
~$fiber_generator_callee_valid(S_cycle, pgenerator, pcallcontext_generator)
~$fiber_generator_cached_reference_valid(S_cycle, pgenerator, pcallcontext_generator)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_callee_valid(S_no_owner, pgenerator, pcallcontext_generator)
~$fiber_generator_cached_reference_valid(S_no_owner, pgenerator, pcallcontext_generator)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$drive_steps(S, 2) = $drive_steps(S_one, 1)
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_callback) <- S_done.ALLOCATIONS)
~((HOBJECT n_new) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
n_new <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
''')

CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if pconfigcall.OWNER = (n_weak_callback) '
    '-- if $lookup(S.ENV, $ptascii("weakCallback")) = (n_weak_callback_cell) '
    '-- if S.STORE[n_weak_callback_cell] = DEFINED (POBJECT n_weak_callback) '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')

CLOSED = COMMON + checks(r'''
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.RETURN = eps
$weakref_get(S, n_weak_callback) = POBJECT n_callback
$lookup(S.ENV, $ptascii("weakNew")) = (n_weak_new_cell)
S.STORE[n_weak_new_cell] = DEFINED (POBJECT n_weak_new)
$weakref_get(S, n_weak_new) = POBJECT n_new
$lookup(S.ENV, $ptascii("weakInput")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$weakref_get(S, n_weak_input) = PNULL
$node_children(S, HOBJECT n_generator) = [HCELL n_cache, HOBJECT n_callback]
$generator_close_children(S, HOBJECT n_generator) = [HOBJECT n_callback, HCELL n_cache]
$heap_owners(H, HCELL n_cache) = 1
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
S_done = $drive_steps(S, 1200)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_callback) <- S_done.ALLOCATIONS)
~((HOBJECT n_new) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_new <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
''')

CASES = {
    'i86-bound-captured-parked-send-independent': {
        'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i86-bound-captured-closed-independent': {
        'source': ROW['source'], 'stage': CLOSED_STAGE, 'checks': CLOSED},
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
    report.update(independent_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
