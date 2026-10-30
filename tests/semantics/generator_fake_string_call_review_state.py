#!/usr/bin/env python3
"""Check API string-bound copy chains against real warm-THROW owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fake_string_call_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i95-fake-fromcallable-string-bound-call-reference-throw-independent')
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
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake_copy
(HOBJECT n_copy) <- S.ALLOCATIONS
n_source = pboundfake_copy.SOURCE
$(n_source < n_copy)
S.OBJECTS[n_source] = BOUNDFAKECLOSURE pboundfake_source
n_original = pboundfake_source.SOURCE
$(n_original < n_source)
S.OBJECTS[n_original] = FROMCALLABLECLOSURE pfrommethod
~pfrommethod.ARRAY
$string_bytes(pfrommethod.INPUT) = ($ptascii("Base95R::stream"))
pfrommethod.FUNCTION = pgenerator.FUNCTION
~pfrommethod.STATIC
$from_receiver(pfrommethod) = (n_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base95R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child95R"))) = (porigin_child)
$class_at(S.CLASSES, porigin_base) = (pclassdesc_base)
$class_at(S.CLASSES, porigin_child) = (pclassdesc_child)
$method_named(pclassdesc_base.METHODS, $ptascii("stream")) = (pmethoddesc_stream)
$method_named(pclassdesc_child.METHODS, $ptascii("stream")) = (pmethoddesc_other)
pmethoddesc_stream.FUNCTION.ORIGIN = pgenerator.FUNCTION
pmethoddesc_other.FUNCTION.ORIGIN =/= pgenerator.FUNCTION
pmethoddesc_stream.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc_stream.FUNCTION)
pboundfake_copy.SCOPE = BIND_CLASS porigin_base
pboundfake_copy.CALLED = BIND_CLASS porigin_base
pboundfake_copy.RECEIVER = (n_maker)
pboundfake_copy.ORIGINAL = eps
pboundfake_source.SCOPE = BIND_CLASS porigin_base
pboundfake_source.CALLED = BIND_CLASS porigin_base
pboundfake_source.RECEIVER = (n_middle)
pboundfake_source.ORIGINAL = (pclosurescope_original)
$closure_binding_api_site(S, pboundfake_source.SITE)
pclosurescope_original.OBJECT = n_original
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_child
pclosurescope_original.RECEIVER = (n_old)
pclosurescope_original.CREATION = eps
S.OBJECTS[n_old] = INSTANCE porigin_child
S.OBJECTS[n_maker] = INSTANCE porigin_base
S.OBJECTS[n_middle] = INSTANCE porigin_base
(HOBJECT n_maker) <- S.ALLOCATIONS
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
~((HOBJECT n_original) <- S.ALLOCATIONS)
~((HOBJECT n_middle) <- S.ALLOCATIONS)
~$closure_callable(S, n_original)
~$bound_fake_valid(S, n_source)
~$closure_callable(S, n_source)
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_original) = eps
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = eps
$closure_call_copy_site(S, pboundfake_copy.SITE)
$fake_bind_source_valid(S, pboundfake_copy)
$bound_fake_valid(S, n_copy)
$closure_call_fake_copy_binding(S, pboundfake_copy)
$closure_call_copy_row(S, n_copy) = (pclosurebinding_copy)
pclosurebinding_copy.OBJECT = n_copy
pclosurebinding_copy.SITE = pboundfake_copy.SITE
pclosurebinding_copy.SOURCE = n_source
pclosurebinding_copy.LEXICAL = (porigin_base)
pclosurebinding_copy.CALLED = (porigin_base)
pclosurebinding_copy.RECEIVER = (n_maker)
$closure_callable(S, n_copy)
$target_function(S, CLOSURE_TARGET n_copy) = (pmethoddesc_stream.FUNCTION)
$target_lexical_class(S, CLOSURE_TARGET n_copy) = (porigin_base)
$target_called_class(S, CLOSURE_TARGET n_copy) = (porigin_base)
$target_receiver(S, CLOSURE_TARGET n_copy) = (n_maker)
$generator_closure_valid(S, pgenerator)
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token95R")
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$lookup(S.ENV, $ptascii("original")) = eps
$lookup(S.ENV, $ptascii("bound")) = eps
$lookup(S.ENV, $ptascii("middle")) = eps
$lookup(S.ENV, $ptascii("old")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakBound")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = PNULL
$lookup(S.ENV, $ptascii("weakOriginal")) = (n_weak_original_cell)
S.STORE[n_weak_original_cell] = DEFINED (POBJECT n_weak_original)
$weakref_get(S, n_weak_original) = PNULL
$lookup(S.ENV, $ptascii("weakMiddle")) = (n_weak_middle_cell)
S.STORE[n_weak_middle_cell] = DEFINED (POBJECT n_weak_middle)
$weakref_get(S, n_weak_middle) = PNULL
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = PNULL
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_old) = 0
$heap_owners(H, HOBJECT n_original) = 0
$heap_owners(H, HOBJECT n_middle) = 0
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HCELL n_cache) = 1
$heap_owners(H, HOBJECT n_token) = 1
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
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_base)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.CALLSITE = (pboundfake_copy.SITE)
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_copy]
$call_receiver_roots(pcallcontext_generator) = eps
pfibervm.FRAMES = pframe_throw :: pframe_tail*
pframe_throw.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_throw*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
$weakref_get(S, n_weak_input) = POBJECT n_input
$class_instanceof(S, POBJECT n_input, $ptascii("Throwable"))
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("first")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("error")) = eps
$heap_owners(H, HOBJECT n_input) = 1
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$heap_count(HOBJECT n_copy, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_factory_evidence_current(S_live) = (CLOSURE_SCOPE pclosurescope_copy)
pclosurescope_copy.OBJECT = n_copy
pclosurescope_copy.LEXICAL = porigin_base
pclosurescope_copy.CALLED = porigin_base
pclosurescope_copy.RECEIVER = (n_maker)
pclosurescope_copy.CREATION = eps
$generator_captured_factory_valid(S_live, pclosurescope_copy, pgenerator.FUNCTION)
$fiber_generator_method_closure_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$eval_trace_preparser(S_live, (pcallcontext_generator), pframe_throw) = eps
pboundfake_bad_scope = pboundfake_copy[.SCOPE = BIND_CLASS porigin_child]
S_bad_scope = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_bad_scope)]
~$bound_fake_valid(S_bad_scope, n_copy)
~$closure_call_fake_copy_binding(S_bad_scope, pboundfake_bad_scope)
~$fiber_generator_method_closure_valid(S_bad_scope, pgenerator, pcallcontext_generator)
pclosurescope_bad_original = pclosurescope_original[.LEXICAL = porigin_child]
pboundfake_bad_original = pboundfake_source[.ORIGINAL = (pclosurescope_bad_original)]
S_bad_original = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_source, BOUNDFAKECLOSURE pboundfake_bad_original)]
~$bound_fake_valid(S_bad_original, n_copy)
~$closure_call_fake_copy_binding(S_bad_original, pboundfake_copy)
pboundfake_bad_source = pboundfake_copy[.SOURCE = n_copy]
S_bad_source = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_bad_source)]
~$bound_fake_valid(S_bad_source, n_copy)
~$closure_call_fake_copy_binding(S_bad_source, pboundfake_bad_source)
pboundfake_bad_site = pboundfake_copy[.SITE = pfrommethod.SITE]
S_bad_site = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_bad_site)]
~$bound_fake_valid(S_bad_site, n_copy)
~$closure_call_fake_copy_binding(S_bad_site, pboundfake_bad_site)
pboundfake_child = pboundfake_copy[.CALLED = BIND_CLASS porigin_child][.RECEIVER = (n_old)]
S_child = S_live[.ALLOCATIONS = S_live.ALLOCATIONS ++ [HOBJECT n_old]][.OBJECTS = $object_set(S_live.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_child)]
$bound_fake_receiver_valid(S_child, pboundfake_child)
~$closure_call_fake_copy_binding(S_child, pboundfake_child)
pboundfake_cycle = pboundfake_source[.SOURCE = n_copy]
S_cycle = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_source, BOUNDFAKECLOSURE pboundfake_cycle)]
~$closure_call_fake_copy_binding(S_cycle, pboundfake_copy)
pfrommethod_bad_input = pfrommethod[.INPUT = PSTRING ($ptascii("Other95R::bad"))]
S_bad_input = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_original, FROMCALLABLECLOSURE pfrommethod_bad_input)]
~$closure_call_fake_copy_binding(S_bad_input, pboundfake_copy)
pgenerator_source = pgenerator[.CLOSURE = (n_source)]
S_source = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_source)]
~$fiber_generator_method_closure_valid(S_source, pgenerator_source, pcallcontext_generator)
~$fiber_generator_transfer(S_source)
S_no_copy = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_copy)]
~$fiber_generator_method_closure_valid(S_no_copy, pgenerator, pcallcontext_generator)
S_no_owner = S_live[.FRAMES = eps]
$fiber_generator_body_id(S_no_owner) = eps
~$fiber_generator_method_closure_valid(S_no_owner, pgenerator, pcallcontext_generator)
S_bad_cell = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_throw_valid(S_bad_cell, pgeneratorop, pgenerator, pcallcontext_generator)
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
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("weakFirst")) = (n_cell) '
    '-- if S.STORE[n_cell] = DEFINED (POBJECT n_weak) '
    '-- if pconfigcall.OWNER = (n_weak) '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_g_cell) '
    '-- if S.STORE[n_g_cell] = DEFINED (POBJECT n_g) '
    '-- if S.OBJECTS[n_g] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')

CLOSED = COMMON + checks(r'''
pgenerator.PHASE = GENERATOR_CLOSED
$weakref_get(S, n_weak_input) = PNULL
$node_children(S, HOBJECT n_generator) = [HCELL n_cache, HOBJECT n_copy]
$generator_close_children(S, HOBJECT n_generator) = [HOBJECT n_copy, HCELL n_cache]
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
pboundfake_bad_scope = pboundfake_copy[.SCOPE = BIND_CLASS porigin_child]
S_bad_scope = S[.OBJECTS = $object_set(S.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_bad_scope)]
~$bound_fake_valid(S_bad_scope, n_copy)
~$generator_closure_valid(S_bad_scope, pgenerator)
S_done = $drive_steps(S, 1800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i95-fake-fromcallable-string-bound-parked-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i95-fake-fromcallable-string-bound-closed-independent': {'source': ROW['source'], 'stage': CLOSED_STAGE, 'checks': CLOSED},
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
        passed = review.run(selected, process_seconds=900)
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
