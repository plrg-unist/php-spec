#!/usr/bin/env python3
"""Check captured method Closure THROW owners and actual warm/fresh phases."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_captured_method_throw_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def park(kind):
    return ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
            '-- if pconfigcall.KIND = ' + kind + ' '
            '-- if pconfigcall.OWNER = (n_fiber) '
            '-- if S.ACTIVEFIBER = eps '
            '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
            '-- if pfiber.STATUS = FIBER_SUSPENDED')


COMMON = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = (n_callback)
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
pgenerator.BORROWED = eps
~pgenerator.PENDING_INIT
(HOBJECT n_callback) <- S.ALLOCATIONS
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_current :: pframe_tail*
pframe_current.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callback
pcallcontext_generator.INSTANCE = (n_callback)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.VISIBILITY = PROPERTY_PRIVATE
~pmethoddesc.STATIC
$function_generator(S, pmethoddesc.FUNCTION)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callback]
$call_receiver_roots(pcallcontext_generator) = eps
$node_children(S, HOBJECT n_callback) = [HOBJECT n_maker]
$lookup(S.ENV, $ptascii("callback")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$throwable_member(S, n_input)
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_factory_evidence_current(S_live) = (CLOSURE_SCOPE pclosurescope)
pclosurescope.OBJECT = n_callback
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = (n_maker)
$generator_captured_factory_valid(S_live, pclosurescope, pgenerator.FUNCTION)
$fiber_generator_method_closure_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$call_current_valid(S_live)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_callback) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_count(HOBJECT n_callback, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 0
$heap_valid(H)
$call_descriptors_valid(S)
""")

WARM = checks(r"""
~pgenerator.FIRST
~pgeneratorop.ADVANCE
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
$generator_pending_exception_nodes(pgeneratorop) = eps
$heap_owners(H, HOBJECT n_input) = 1
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 89]], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.NAME = "send"], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live[.FRAMES = eps], pgeneratorop, pgenerator, pcallcontext_generator)
""")

METHOD = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base89A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf89A"))) = (porigin_leaf)
$object_body(S.OBJECTS[n_callback]) = METHODCLOSURE pgenerator.FUNCTION porigin_capture_site porigin_requested pmethodcapture?
$closure_scope_at(S.CLOSURESCOPES, n_callback) = (pclosurescope)
pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token89A")
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$heap_owners(H, HCELL n_cache) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
S_bad_cell = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cell, pgenerator, pcallcontext_generator)
S_dead_closure = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_callback)]
~$fiber_generator_throw_valid(S_dead_closure, pgeneratorop, pgenerator, pcallcontext_generator)
S_dead_receiver = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_throw_valid(S_dead_receiver, pgeneratorop, pgenerator, pcallcontext_generator)
""") + WARM

BOUND = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base89B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child89B"))) = (porigin_child)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf89B"))) = (porigin_leaf)
S.OBJECTS[n_callback] = BOUNDFAKECLOSURE pboundfake
pboundfake.SCOPE = BIND_CLASS porigin_base
pboundfake.CALLED = BIND_CLASS porigin_leaf
pboundfake.RECEIVER = (n_maker)
pboundfake.SOURCE = n_original
$(n_original < n_callback)
S.OBJECTS[n_original] = FROMCALLABLECLOSURE pfrommethod
pfrommethod.FUNCTION = pgenerator.FUNCTION
pboundfake.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_original
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_child
pclosurescope_original.RECEIVER = (n_old)
S.OBJECTS[n_old] = INSTANCE porigin_child
~((HOBJECT n_original) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
$heap_owners(H, HOBJECT n_original) = 0
$heap_owners(H, HOBJECT n_old) = 0
$generator_captured_factory_scope(S, n_original) = (pclosurescope_original)
$bound_fake_valid(S, n_callback)
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.VALUE = (POBJECT n_token)
pgenerator.REFCELL = eps
$object_name(S, n_token) = $ptascii("Token89B")
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
$heap_owners(H, HOBJECT n_token) = 1
~$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator[.VALUE = eps], pcallcontext_generator)
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_child)]
S_bad_called = S_live[.CURRENT = (pcallcontext_bad_called)]
~$fiber_generator_throw_valid(S_bad_called, pgeneratorop, pgenerator, pcallcontext_bad_called)
""") + WARM

ARRAY = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base89C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf89C"))) = (porigin_leaf)
S.OBJECTS[n_callback] = ARRAYMETHODCLOSURE pcalltarget_original parrayselection_original eps
pcalltarget_original = SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) pcallableaccess_original
parrayselection_original.NAME = $ptascii("stream")
parrayselection_original.REQUESTED = porigin_leaf
pcallableaccess_original.SITE = (parrayselection_original.SITE)
pcallableaccess_original.SCOPE = (porigin_base)
pcallableaccess_original.OBJECT
pcallableaccess_original.CREATION = eps
$closure_scope_at(S.CLOSURESCOPES, n_callback) = (pclosurescope)
pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgeneratorop.ADVANCE
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_parameter)
n_parameter <- S.REFCELLS
S.STORE[n_parameter] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token89C")
$node_children(S, HOBJECT n_generator) = eps
$heap_owners(H, HCELL n_parameter) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 2
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 2
$generator_pending_exception_nodes(pgeneratorop) = [HOBJECT n_input]
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input, HOBJECT n_input]
$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 89]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live[.FRAMES = eps], pgeneratorop, pgenerator, pcallcontext_generator)
pcallcontext_bad_instance = pcallcontext_generator[.INSTANCE = eps]
S_bad_instance = S_live[.CURRENT = (pcallcontext_bad_instance)]
~$fiber_generator_fresh_throw_valid(S_bad_instance, pgeneratorop, pgenerator, pcallcontext_bad_instance)
""")

CASES = {
    'i89-method-warm-reference-throw-parked': {'source': ROWS['i89-method-captured-warm-reference-abort']['source'], 'stage': park('INTRINSIC_FIBER_THROW'), 'checks': METHOD},
    'i89-bound-warm-value-throw-parked': {'source': ROWS['i89-bound-fromcallable-warm-value-throw']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': BOUND},
    'i89-array-fresh-reference-throw-parked': {'source': ROWS['i89-array-captured-fresh-reference-throw']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': ARRAY},
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
