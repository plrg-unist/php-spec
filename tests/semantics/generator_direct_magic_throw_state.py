#!/usr/bin/env python3
"""Check direct magic Generator THROW receipts, caches and API owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_direct_magic_throw_cases.json')
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
pgenerator.CLOSURE = eps
pgenerator.CREATION = (pgeneratorcreation)
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.REFCELL = eps
pgenerator.RETURN = eps
pgenerator.BORROWED = eps
~pgenerator.PENDING_INIT
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR_TARGET = pgeneratorcreation.CALLEE
pgeneratorcreation.CREATOR.FUNCTION = pgenerator.FUNCTION
pgeneratorcreation.CREATOR.CALLSITE = (pgeneratorcreation.SITE)
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
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.ARGC = 2
pcallcontext_generator.EXTRA = eps
pcallcontext_generator.NAMED = eps
pcallcontext_generator.HOLES = eps
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc.FUNCTION)
~$generator_reference_producer(S, pgenerator)
$throwable_member(S, n_input)
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_creation_selected(S_live, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_creation_record_valid(S_live, pgenerator)
$generator_creation_context_valid(S_live, pgenerator, pcallcontext_generator)
$generator_magic_context_valid(S_live, pcallcontext_generator)
$fiber_generator_magic_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$call_current_valid(S_live)
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_live, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$fiber_generator_magic_valid(S_missing, pgenerator_missing, pcallcontext_generator)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_magic_valid(S_no_owner, pgenerator, pcallcontext_generator)
pcallcontext_bad_argc = pcallcontext_generator[.ARGC = 1]
S_bad_argc = S_live[.CURRENT = (pcallcontext_bad_argc)]
~$fiber_generator_magic_valid(S_bad_argc, pgenerator, pcallcontext_bad_argc)
pgenerator_paused = pgenerator[.PHASE = GENERATOR_PAUSED]
S_paused_record = $generator_set(S_live, n_generator, pgenerator_paused)
~$fiber_generator_magic_valid(S_paused_record, pgenerator_paused, pcallcontext_generator)
""")

WARM = checks(r"""
~pgenerator.FIRST
~pgeneratorop.ADVANCE
pgenerator.VALUE = (POBJECT n_token)
$lookup(pfibervm.TABLE.ENV, $ptascii("arguments")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
~((HARRAY n_arguments) <- S.ALLOCATIONS)
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
$heap_owners(H, HARRAY n_arguments) = 0
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$generator_pending_exception_nodes(pgeneratorop) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 90]], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop[.NAME = "send"], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_missing, pgeneratorop, pgenerator_missing, pcallcontext_generator)
~$fiber_generator_throw_valid(S_no_owner, pgeneratorop, pgenerator, pcallcontext_generator)
pgenerator_empty_cache = pgenerator[.VALUE = eps]
S_empty_cache = $generator_set(S_live, n_generator, pgenerator_empty_cache)
$fiber_generator_magic_valid(S_empty_cache, pgenerator_empty_cache, pcallcontext_generator)
~$fiber_generator_throw_valid(S_empty_cache, pgeneratorop, pgenerator_empty_cache, pcallcontext_generator)
""")

INSTANCE = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base90A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf90A"))) = (porigin_leaf)
pgeneratorcreation.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([POBJECT n_token])
pmagicmethodcall.SITE = pgeneratorcreation.SITE
pmagicmethodcall.METHOD = pgenerator.FUNCTION
pmagicmethodcall.CLASS = porigin_leaf
pmagicmethodcall.OBJECT = n_maker
pmagicmethodcall.NAME = $ptascii("missing")
pmagicmethodcall.CALLER = eps
pmagicmethodcall.OWNER = 0
$magic_method_descriptor(S, pmagicmethodcall)
~pmethoddesc.STATIC
pcallcontext_generator.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
$object_name(S, n_token) = $ptascii("Token90A")
$target_receiver(S, pgeneratorcreation.CALLEE) = (n_maker)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_owners(H, HOBJECT n_maker) = 1
$lookup(S.ENV, $ptascii("maker")) = eps
S_dead = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_magic_valid(S_dead, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_dead, pgeneratorop, pgenerator, pcallcontext_generator)
""") + WARM

STATIC = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base90B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf90B"))) = (porigin_leaf)
pgeneratorcreation.CALLEE = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_arguments ([POBJECT n_token])
pmagicstaticmethodcall.SITE = pgeneratorcreation.SITE
pmagicstaticmethodcall.METHOD = pgenerator.FUNCTION
pmagicstaticmethodcall.CLASS = porigin_leaf
pmagicstaticmethodcall.NAME = $ptascii("missing")
pmagicstaticmethodcall.CALLER = eps
pmagicstaticmethodcall.OWNER = 0
$magic_static_method_descriptor(S, pmagicstaticmethodcall)
pmethoddesc.STATIC
pcallcontext_generator.RECEIVER = eps
$object_name(S, n_token) = $ptascii("Token90B")
$target_receiver(S, pgeneratorcreation.CALLEE) = eps
$call_context_roots((pcallcontext_generator)) = eps
""") + WARM

FRESH = COMMON + checks(r"""
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base90C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf90C"))) = (porigin_leaf)
pgeneratorcreation.CALLEE = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_arguments ([POBJECT n_token])
pmagicstaticmethodcall.SITE = pgeneratorcreation.SITE
pmagicstaticmethodcall.METHOD = pgenerator.FUNCTION
pmagicstaticmethodcall.CLASS = porigin_leaf
pmagicstaticmethodcall.NAME = $ptascii("missing")
pmagicstaticmethodcall.CALLER = eps
pmagicstaticmethodcall.OWNER = 0
$magic_static_method_descriptor(S, pmagicstaticmethodcall)
pmethoddesc.STATIC
pcallcontext_generator.RECEIVER = eps
pgenerator.FIRST
pgenerator.VALUE = eps
pgeneratorop.ADVANCE
$lookup(pfibervm.TABLE.ENV, $ptascii("arguments")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_local_token)
S.STORE[n_local_token] = DEFINED (POBJECT n_token)
~(n_local_token <- S.REFCELLS)
$object_name(S, n_token) = $ptascii("Token90C")
~((HARRAY n_arguments) <- S.ALLOCATIONS)
$node_children(S, HOBJECT n_generator) = eps
$call_context_roots((pcallcontext_generator)) = eps
$heap_owners(H, HARRAY n_arguments) = 0
$heap_owners(H, HCELL n_local_token) = 1
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
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 90]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_missing, pgeneratorop, pgenerator_missing, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_no_owner, pgeneratorop, pgenerator, pcallcontext_generator)
pgenerator_not_first = pgenerator[.FIRST = false]
S_not_first = $generator_set(S_live, n_generator, pgenerator_not_first)
$fiber_generator_magic_valid(S_not_first, pgenerator_not_first, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_not_first, pgeneratorop, pgenerator_not_first, pcallcontext_generator)
""")

CASES = {
    'i90-magic-instance-warm-throw-parked': {'source': ROWS['i90-magic-instance-warm-throw-abort']['source'], 'stage': park('INTRINSIC_FIBER_THROW'), 'checks': INSTANCE},
    'i90-magic-static-warm-throw-parked': {'source': ROWS['i90-magic-static-warm-throw']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': STATIC},
    'i90-magic-static-fresh-throw-parked': {'source': ROWS['i90-magic-static-fresh-throw']['source'], 'stage': park('INTRINSIC_FIBER_RESUME'), 'checks': FRESH},
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
