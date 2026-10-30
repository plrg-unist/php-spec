#!/usr/bin/env python3
"""Check a private raw Generator body with a warm reference cache and throw input."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_raw_method_cache_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i88-raw-private-reference-warm-throw-abort-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

PARK = checks(r'''
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
pgenerator.REFCELL = (n_cache)
pgenerator.CLOSURE = eps
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
pgenerator.BORROWED = eps
~pgenerator.FIRST
~pgenerator.PENDING_INIT
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base88R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf88R"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.VISIBILITY = PROPERTY_PRIVATE
~pmethoddesc.STATIC
pmethoddesc.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc.FUNCTION)
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) pcallableaccess) parrayselection
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (parrayselection.SITE)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_maker)
pcallableaccess.SITE = (parrayselection.SITE)
pcallableaccess.SCOPE = (porigin_base)
pcallableaccess.OBJECT
pcallableaccess.CREATION = eps
parrayselection.REQUESTED = porigin_leaf
parrayselection.NAME = $ptascii("stream")
$generator_raw_method_scope_source(S, pcallableaccess, parrayselection.SITE)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
pfibervm.FRAMES = pframe_throw :: pframe_tail*
pframe_throw.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_throw*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$throwable_member(S, n_input)
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$weakref_get(S, n_weak_input) = POBJECT n_input
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token88R")
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HCELL n_cache) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$heap_valid(H)
$call_descriptors_valid(S)
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_raw_method_selected(S_live, pcallcontext_generator.TARGET, parrayselection.SITE) = (pmethoddesc)
$fiber_generator_raw_method_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$effective_method(S, porigin_leaf, $ptascii("stream"), |S.CLASSES|) = (pmethoddesc_public)
pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC
pmethoddesc_public.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc_public.FUNCTION)
pmethoddesc_public.FUNCTION.ORIGIN =/= pgenerator.FUNCTION
pcalltarget_public = ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_public.FUNCTION.ORIGIN) parrayselection
$generator_raw_method_selected(S_live, pcalltarget_public, parrayselection.SITE) = eps
pcallcontext_public = pcallcontext_generator[.TARGET = pcalltarget_public]
S_public = S_live[.CURRENT = (pcallcontext_public)]
~$fiber_generator_raw_method_valid(S_public, pgenerator, pcallcontext_public)
~$fiber_generator_throw_valid(S_public, pgeneratorop, pgenerator, pcallcontext_public)
parrayselection_bad_name = parrayselection[.NAME = $ptascii("open")]
pcalltarget_bad_name = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) pcallableaccess) parrayselection_bad_name
$generator_raw_method_selected(S_live, pcalltarget_bad_name, parrayselection.SITE) = eps
pcallableaccess_bad_scope = pcallableaccess[.SCOPE = (porigin_leaf)]
pcalltarget_bad_scope = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) pcallableaccess_bad_scope) parrayselection
$generator_raw_method_selected(S_live, pcalltarget_bad_scope, parrayselection.SITE) = eps
~$fiber_generator_raw_method_valid(S_live[.CURRENT = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_raw_method_valid(S_live[.FRAMES = eps], pgenerator, pcallcontext_generator)
S_dead = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_raw_method_valid(S_dead, pgenerator, pcallcontext_generator)
S_bad_cell = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cell, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 88]], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.NAME = "send"], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator[.REFCELL = eps], pcallcontext_generator)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4000)
$drive_steps(S_one[.COMPLETION = NORMAL], 4000) = S_done
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
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i88-raw-private-reference-warm-throw-parked-independent': {
        'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
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
