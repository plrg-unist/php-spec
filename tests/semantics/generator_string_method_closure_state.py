#!/usr/bin/env python3
"""Check static string Closure identity, binding and real Generator cache owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_string_method_closure_cases.json')
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
S.FIBERCLOSERS = eps
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.FRAME = eps
pgenerator.CLOSURE = (n_callback)
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
(HOBJECT n_callback) <- S.ALLOCATIONS
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.STATIC
$function_generator(S, pmethoddesc.FUNCTION)
$generator_captured_factory_scope(S, n_callback) = (pclosurescope)
pclosurescope.OBJECT = n_callback
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_called
pclosurescope.RECEIVER = eps
pclosurescope.CREATION = eps
$generator_captured_factory_valid(S, pclosurescope, pgenerator.FUNCTION)
$generator_closure_valid(S, pgenerator)
$node_children(S, HOBJECT n_callback) = eps
$lookup(S.ENV, $ptascii("callback")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_callback) = 1
$call_descriptors_valid(S)
$heap_valid(H)
""")

PARK = checks(r"""
pgenerator.PHASE = GENERATOR_RUNNING
~pgenerator.FIRST
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_current :: pframe_tail*
pframe_current.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callback
pcallcontext_generator.INSTANCE = (n_callback)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_called)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.WRAPPER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callback]
$call_receiver_roots(pcallcontext_generator) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
$throwable_member(S, n_input)
$heap_owners(H, HOBJECT n_input) = 1
$heap_count(HOBJECT n_callback, $fiber_vm_nodes(pfibervm)) = 1
$generator_pending_exception_nodes(pgeneratorop) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_factory_evidence_current(S_live) = (CLOSURE_SCOPE pclosurescope)
$fiber_generator_method_closure_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
S_dead = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_callback)]
~$fiber_generator_callee_valid(S_dead, pgenerator, pcallcontext_generator)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_method_closure_valid(S_no_owner, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 91]], pgenerator, pcallcontext_generator)
""")

STRING = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base91A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf91A"))) = (porigin_called)
S.OBJECTS[n_callback] = STRINGMETHODCLOSURE pcalltarget pstringselection
pcalltarget = STATIC_METHOD_TARGET porigin_called pgenerator.FUNCTION
pstringselection.REQUESTED = porigin_called
pstringselection.ORIGINAL = $ptascii("Leaf91A::stream")
$closure_scope_at(S.CLOSURESCOPES, n_callback) = (pclosurescope)
$class_instanceof(S, POBJECT n_callback, $ptascii("cLoSuRe"))
~$class_instanceof(S, POBJECT n_callback, $ptascii("Token91A"))
$getclass_live_object(S, n_callback)
$lookup(S.ENV, $ptascii("weakCallback")) = (n_weak_callback_cell)
S.STORE[n_weak_callback_cell] = DEFINED (POBJECT n_weak_callback)
$weakref_get(S, n_weak_callback) = POBJECT n_callback
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.VALUE = (POBJECT n_token)
pgenerator.REFCELL = eps
$object_name(S, n_token) = $ptascii("Token91A")
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
$heap_owners(H, HOBJECT n_token) = 1
""") + PARK + checks(r"""
$effective_method(S, porigin_called, $ptascii("stream"), |S.CLASSES|) = (pmethoddesc)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Other91A"))) = (porigin_other)
$effective_method(S, porigin_other, $ptascii("bad"), |S.CLASSES|) = (pmethoddesc_other)
pmethoddesc_other.FUNCTION.ORIGIN =/= pgenerator.FUNCTION
pstringselection_bad = pstringselection[.ORIGINAL = $ptascii("Other91A::bad")]
S_bad_selection = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_callback, STRINGMETHODCLOSURE pcalltarget pstringselection_bad)]
~$generator_captured_factory_valid(S_bad_selection, pclosurescope, pgenerator.FUNCTION)
~$fiber_generator_callee_valid(S_bad_selection, pgenerator, pcallcontext_generator)
""")

BOUND = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base91B"))) = (porigin_base)
porigin_called = porigin_base
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child91B"))) = (porigin_child)
S.OBJECTS[n_callback] = BOUNDFAKECLOSURE pboundfake
pboundfake.SCOPE = BIND_CLASS porigin_base
pboundfake.CALLED = BIND_CLASS porigin_base
pboundfake.RECEIVER = eps
pboundfake.SOURCE = n_source
$(n_source < n_callback)
S.OBJECTS[n_source] = STRINGMETHODCLOSURE pcalltarget_source pstringselection
pstringselection.REQUESTED = porigin_child
pstringselection.ORIGINAL = $ptascii("Child91B::stream")
pboundfake.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_child
pclosurescope_original.RECEIVER = eps
pclosurescope_original.CREATION = eps
~((HOBJECT n_source) <- S.ALLOCATIONS)
$heap_owners(H, HOBJECT n_source) = 0
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_callback) = eps
$generator_captured_factory_scope(S, n_source) = (pclosurescope_original)
$bound_fake_valid(S, n_callback)
$closure_binding_site(S, pboundfake.SITE, INTRINSIC_CLOSURE_BINDTO)
pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token91B")
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$heap_owners(H, HOBJECT n_token) = 1
$lookup(S.ENV, $ptascii("weakOriginal")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = PNULL
""")

BOUND_PARK = BOUND + PARK + checks(r"""
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$heap_owners(H, HCELL n_cache) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
pclosurescope_bad_called = pclosurescope[.CALLED = porigin_child]
~$generator_captured_factory_valid(S_live, pclosurescope_bad_called, pgenerator.FUNCTION)
S_bad_cell = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cell, pgenerator, pcallcontext_generator)
""")

BOUND_CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("weakCallback")) = (n_weak_cell) '
    '-- if S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak_callback) '
    '-- if pconfigcall.OWNER = (n_weak_callback) '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_g_cell) '
    '-- if S.STORE[n_g_cell] = DEFINED (POBJECT n_g) '
    '-- if S.OBJECTS[n_g] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')

BOUND_CLOSED = BOUND + checks(r"""
S.ACTIVEFIBER = eps
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.RETURN = eps
$node_children(S, HOBJECT n_generator) = [HCELL n_cache, HOBJECT n_callback]
$generator_close_children(S, HOBJECT n_generator) = [HOBJECT n_callback, HCELL n_cache]
$heap_owners(H, HCELL n_cache) = 1
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_first_cell)
S.STORE[n_weak_first_cell] = DEFINED (POBJECT n_weak_first)
$weakref_get(S, n_weak_first) = PNULL
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
S_done = $drive_steps(S, 1600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_callback) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
""")

CASES = {
    'i91-string-value-throw-parked': {'source': ROWS['i91-static-string-captured-identity-retarget']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': STRING},
    'i91-bound-string-reference-throw-parked': {'source': ROWS['i91-bound-private-string-reference-throw-abort']['source'], 'stage': park('INTRINSIC_FIBER_THROW'), 'checks': BOUND_PARK},
    'i91-bound-string-reference-closed': {'source': ROWS['i91-bound-private-string-reference-throw-abort']['source'], 'stage': BOUND_CLOSED_STAGE, 'checks': BOUND_CLOSED},
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
