#!/usr/bin/env python3
"""Check raw selected factory history against real receiver/cache/SEND owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_raw_method_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i87-raw-array-retarget-reference-abort-independent')
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
pgenerator.CLOSURE = eps
pgenerator.ACCESS = eps
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base87R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf87R"))) = (porigin_leaf)
$class_at(S.CLASSES, porigin_base) = (pclassdesc_base)
$method_named(pclassdesc_base.METHODS, $ptascii("factory")) = (pmethoddesc_factory)
pgeneratorcreation.CREATOR.FUNCTION = pmethoddesc_factory.FUNCTION.ORIGIN
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CREATOR_TARGET = ARRAY_METHOD_TARGET pcalltarget_factory parrayselection
pcalltarget_factory = METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN
$(n_maker < |S.OBJECTS|)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
parrayselection.REQUESTED = porigin_leaf
parrayselection.NAME = $ptascii("factory")
pgeneratorcreation.CREATOR.CALLSITE = (parrayselection.SITE)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf (n_maker) poperand_selector
$generator_creator_target_valid(S, pgeneratorcreation, pmethoddesc_factory, parrayselection.SITE)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$function_at($all_functions(S), pgenerator.FUNCTION) = (pfunction)
pfunction.SIGNATURE.BYREF
$function_generator(S, pfunction)
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token87R")
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("selection")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$lookup(S.ENV, $ptascii("weakOther")) = (n_weak_other_cell)
S.STORE[n_weak_other_cell] = DEFINED (POBJECT n_weak_other)
$weakref_get(S, n_weak_other) = PNULL
H = $heap_graph(S)
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
(HOBJECT n_maker) <- S.ALLOCATIONS
$weakref_get(S, n_weak_old) = POBJECT n_maker
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$call_receiver_roots(pcallcontext_generator) = [HOBJECT n_maker]
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
$object_name(S, n_input) = $ptascii("Input87R")
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HCELL n_cache) = 2
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_creation_context_valid(S_live, pgenerator, pcallcontext_generator)
$generator_creation_selected(S_live, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$fiber_generator_receiver_target(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_missing)]
~$generator_creation_context_valid(S_missing, pgenerator_missing, pcallcontext_generator)
~$generator_creation_selected(S_missing, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pgeneratorcreation_bad_site = pgeneratorcreation[.SITE = parrayselection.SITE]
pgenerator_bad_site = pgenerator[.CREATION = (pgeneratorcreation_bad_site)]
S_bad_site = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_bad_site)]
~$generator_creation_selected(S_bad_site, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pmethodcapture_bad_called = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pmethodcapture_bad_called]
~$generator_creator_valid(S_live, pgeneratorcreation_bad_called)
parrayselection_bad_name = parrayselection[.NAME = $ptascii("bad")]
pgeneratorcreation_bad_name = pgeneratorcreation[.CREATOR_TARGET = ARRAY_METHOD_TARGET pcalltarget_factory parrayselection_bad_name]
~$generator_creator_valid(S_live, pgeneratorcreation_bad_name)
pcallcontext_bad_receiver = pcallcontext_generator[.RECEIVER = eps]
S_bad_receiver = S_live[.CURRENT = (pcallcontext_bad_receiver)]
~$fiber_generator_callee_valid(S_bad_receiver, pgenerator, pcallcontext_bad_receiver)
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
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("weakOld")) = (n_cell) '
    '-- if S.STORE[n_cell] = DEFINED (POBJECT n_weak) '
    '-- if pconfigcall.OWNER = (n_weak) '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_g_cell) '
    '-- if S.STORE[n_g_cell] = DEFINED (POBJECT n_g) '
    '-- if S.OBJECTS[n_g] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')

CLOSED = COMMON + checks(r'''
pgenerator.PHASE = GENERATOR_CLOSED
~((HOBJECT n_maker) <- S.ALLOCATIONS)
n_maker <- S.DESTRUCTION.CALLED
$weakref_get(S, n_weak_old) = PNULL
$heap_owners(H, HOBJECT n_maker) = 0
$heap_owners(H, HCELL n_cache) = 1
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$generator_close_children(S, HOBJECT n_generator) = [HCELL n_cache]
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
$lookup(S.ENV, $ptascii("weakInput")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$weakref_get(S, n_weak_input) = PNULL
pcalltarget_bad_receiver = METHOD_TARGET n_generator pmethoddesc_factory.FUNCTION.ORIGIN
pgeneratorcreation_bad_receiver = pgeneratorcreation[.CREATOR_TARGET = ARRAY_METHOD_TARGET pcalltarget_bad_receiver parrayselection]
~$generator_creator_valid(S, pgeneratorcreation_bad_receiver)
S_done = $drive_steps(S, 1400)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
~((HCELL n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i87-raw-factory-parked-send-independent': {
        'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i87-raw-factory-closed-history-independent': {
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
    report.update(peer_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  peer_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
