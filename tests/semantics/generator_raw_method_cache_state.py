#!/usr/bin/env python3
"""Check raw Gen cache/input lifetimes and actual throw phases."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_raw_method_cache_cases.json')
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


COMMON = checks(r'''
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
pgenerator.CLOSURE = eps
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
pgenerator.BORROWED = eps
~pgenerator.PENDING_INIT
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_current :: pframe_tail*
pframe_current.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
$function_generator(S, pmethoddesc.FUNCTION)
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$fiber_generator_raw_method_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$call_current_valid(S_live)
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
''')

SEND = COMMON + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base88A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf88A"))) = (porigin_leaf)
pcallcontext_generator.TARGET = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) pcallableaccess) parrayselection
pcallcontext_generator.CALLSITE = (parrayselection.SITE)
pcallcontext_generator.RECEIVER = (n_maker)
pcallableaccess.SITE = (parrayselection.SITE)
pcallableaccess.SCOPE = (porigin_base)
pcallableaccess.OBJECT
pcallableaccess.CREATION = eps
parrayselection.NAME = $ptascii("stream")
parrayselection.REQUESTED = porigin_leaf
pmethoddesc.VISIBILITY = PROPERTY_PRIVATE
~pmethoddesc.STATIC
pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token88A")
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
~pgeneratorop.ADVANCE
$object_name(S, n_input) = $ptascii("Input88A")
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_owners(H, HCELL n_cache) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
S_bad_cell = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cell, pgenerator, pcallcontext_generator)
$effective_method(S, porigin_leaf, $ptascii("stream"), |S.CLASSES|) = (pmethoddesc_public)
pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC
pmethoddesc_public.FUNCTION.ORIGIN =/= pgenerator.FUNCTION
pcalltarget_public = ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_public.FUNCTION.ORIGIN) parrayselection
pcallcontext_public = pcallcontext_generator[.TARGET = pcalltarget_public]
S_public = S_live[.CURRENT = (pcallcontext_public)]
~$fiber_generator_raw_method_valid(S_public, pgenerator, pcallcontext_public)
~$fiber_generator_cached_reference_valid(S_public, pgenerator, pcallcontext_public)
S_dead = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_raw_method_valid(S_dead, pgenerator, pcallcontext_generator)
~$fiber_generator_cached_reference_valid(S_live[.FRAMES = eps], pgenerator, pcallcontext_generator)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4000)
$drive_steps(S_one[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

WARM = COMMON + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base88B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf88B"))) = (porigin_leaf)
pcallcontext_generator.TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_leaf pgenerator.FUNCTION) pstringselection
pcallcontext_generator.CALLSITE = (pstringselection.SITE)
pcallcontext_generator.RECEIVER = eps
pstringselection.REQUESTED = porigin_leaf
pstringselection.ORIGINAL = $ptascii("Leaf88B::stream")
pmethoddesc.STATIC
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.VALUE = (POBJECT n_token)
pgenerator.REFCELL = eps
$object_name(S, n_token) = $ptascii("Token88B")
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
~pgeneratorop.ADVANCE
~pgenerator.FIRST
$throwable_member(S, n_input)
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
$lookup(S.ENV, $ptascii("token")) = eps
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
$call_context_roots((pcallcontext_generator)) = eps
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 88]], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.NAME = "send"], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator[.VALUE = eps], pcallcontext_generator)
~$fiber_generator_throw_valid(S_live[.FRAMES = eps], pgeneratorop, pgenerator, pcallcontext_generator)
S_done = $drive_steps(S, 2600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

FRESH = COMMON + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base88C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf88C"))) = (porigin_leaf)
pcallcontext_generator.TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_leaf pgenerator.FUNCTION) pstringselection
pcallcontext_generator.CALLSITE = (pstringselection.SITE)
pcallcontext_generator.RECEIVER = eps
pstringselection.REQUESTED = porigin_leaf
pstringselection.ORIGINAL = $ptascii("Leaf88C::stream")
pmethoddesc.STATIC
pmethoddesc.FUNCTION.SIGNATURE.BYREF
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.ADVANCE
$throwable_member(S, n_input)
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_parameter)
n_parameter <- S.REFCELLS
S.STORE[n_parameter] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token88C")
$lookup(S.ENV, $ptascii("token")) = eps
$node_children(S, HOBJECT n_generator) = eps
$heap_owners(H, HCELL n_parameter) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 2
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 2
$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 88]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live[.FRAMES = eps], pgeneratorop, pgenerator, pcallcontext_generator)
S_done = $drive_steps(S, 3000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i88-raw-private-cache-send-parked': {'source': ROWS['i88-raw-array-private-reference-send']['source'], 'stage': park('INTRINSIC_FIBER_THROW'), 'checks': SEND},
    'i88-raw-static-warm-throw-parked': {'source': ROWS['i88-raw-string-static-cached-throw']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': WARM},
    'i88-raw-static-fresh-reference-throw-parked': {'source': ROWS['i88-raw-string-static-fresh-reference-throw']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': FRESH},
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
