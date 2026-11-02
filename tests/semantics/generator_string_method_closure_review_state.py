#!/usr/bin/env python3
"""Check retired string-bound factory history against real reference-cache owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_string_method_closure_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i91-bound-string-factory-retired-reference-independent')
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
pgenerator.CLOSURE = eps
pgenerator.ACCESS = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CLOSURE = (CLOSURE_SCOPE pclosurescope)
n_factory = pclosurescope.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
S.OBJECTS[n_factory] = BOUNDFAKECLOSURE pboundfake
n_source = pboundfake.SOURCE
n_source <- S.GC.FAKE_NOCOLLECT
pboundfake.ORIGINAL = (pclosurescope_original)
S.OBJECTS[n_source] = STRINGMETHODCLOSURE pcalltarget_source pstringselection
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base91R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf91R"))) = (porigin_leaf)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Other91R"))) = (porigin_other)
$class_at(S.CLASSES, porigin_base) = (pclassdesc_base)
$method_named(pclassdesc_base.METHODS, $ptascii("make")) = (pmethoddesc_make)
$method_named(pclassdesc_base.METHODS, $ptascii("body")) = (pmethoddesc_body)
porigin_make = pmethoddesc_make.FUNCTION.ORIGIN
pgenerator.FUNCTION = pmethoddesc_body.FUNCTION.ORIGIN
pgeneratorcreation.CREATOR.FUNCTION = porigin_make
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_base)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_base eps poperand_body
~pmethoddesc_make.FUNCTION.SIGNATURE.BYREF
~$function_generator(S, pmethoddesc_make.FUNCTION)
pmethoddesc_body.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc_body.FUNCTION)
pboundfake.SCOPE = BIND_CLASS porigin_base
pboundfake.CALLED = BIND_CLASS porigin_base
pboundfake.RECEIVER = eps
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_base
pclosurescope.RECEIVER = eps
pclosurescope.CREATION = eps
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_leaf
pclosurescope_original.RECEIVER = eps
pclosurescope_original.CREATION = eps
pstringselection.REQUESTED = porigin_leaf
pstringselection.ORIGINAL = $ptascii("Leaf91R::make")
$(n_source < n_factory)
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_factory) = eps
$node_children(S, HOBJECT n_factory) = eps
~$closure_callable(S, n_factory)
~$bound_fake_valid(S, n_factory)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_factory]]
$bound_fake_valid(S_lookup, n_factory)
$target_function(S_lookup, CLOSURE_TARGET n_factory) = (pmethoddesc_make.FUNCTION)
$target_lexical_class(S_lookup, CLOSURE_TARGET n_factory) = (porigin_base)
$target_called_class(S_lookup, CLOSURE_TARGET n_factory) = (porigin_base)
$target_receiver(S_lookup, CLOSURE_TARGET n_factory) = eps
$generator_captured_factory_valid(S, pclosurescope, porigin_make)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token91R")
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$lookup(S.ENV, $ptascii("original")) = eps
$lookup(S.ENV, $ptascii("callback")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakOriginal")) = (n_weak_original_cell)
S.STORE[n_weak_original_cell] = DEFINED (POBJECT n_weak_original)
$weakref_get(S, n_weak_original) = PNULL
$lookup(S.ENV, $ptascii("weakCallback")) = (n_weak_callback_cell)
S.STORE[n_weak_callback_cell] = DEFINED (POBJECT n_weak_callback)
$weakref_get(S, n_weak_callback) = PNULL
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_first_cell)
S.STORE[n_weak_first_cell] = DEFINED (POBJECT n_weak_first)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_factory) = 0
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
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_base)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = eps
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
$weakref_get(S, n_weak_first) = POBJECT n_input
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
$heap_owners(H, HCELL n_cache) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_creation_context_valid(S_live, pgenerator, pcallcontext_generator)
$generator_creation_selected(S_live, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
pclosurescope_bad_called = pclosurescope[.CALLED = porigin_leaf]
~$generator_captured_factory_valid(S_live, pclosurescope_bad_called, porigin_make)
pclosurescope_bad_class = pclosurescope[.LEXICAL = porigin_other]
~$generator_captured_factory_valid(S_live, pclosurescope_bad_class, porigin_make)
pgeneratorcreation_original = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_original)]
~$generator_creator_valid(S_live, pgeneratorcreation_original)
pstringselection_other = pstringselection[.ORIGINAL = $ptascii("Other91R::make")]
S_other_selection = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_source, STRINGMETHODCLOSURE pcalltarget_source pstringselection_other)]
~$generator_captured_factory_valid(S_other_selection, pclosurescope, porigin_make)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_missing)]
~$generator_creation_context_valid(S_missing, pgenerator_missing, pcallcontext_generator)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
S_no_owner = S_live[.FRAMES = eps]
$fiber_generator_body_id(S_no_owner) = eps
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4000)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.GENERATORINPUTS = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
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
$heap_owners(H, HCELL n_cache) = 1
$generator_close_children(S, HOBJECT n_generator) = [HCELL n_cache]
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
$weakref_get(S, n_weak_first) = PNULL
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
pclosurescope_bad_called = pclosurescope[.CALLED = porigin_leaf]
~$generator_captured_factory_valid(S, pclosurescope_bad_called, porigin_make)
pgeneratorcreation_original = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_original)]
~$generator_creator_valid(S, pgeneratorcreation_original)
S_done = $drive_steps(S, 1600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i91-retired-string-factory-parked-throw-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i91-retired-string-factory-closed-cache-independent': {'source': ROW['source'], 'stage': CLOSED_STAGE, 'checks': CLOSED},
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
