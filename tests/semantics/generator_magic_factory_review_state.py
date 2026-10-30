#!/usr/bin/env python3
"""Check retired magic argument history and parked reference SEND owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_magic_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i84-magic-packed-reference-abort-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

stage = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if $lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell) '
    '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

checks = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([POBJECT n_token])
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base84R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf84R"))) = (porigin_leaf)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pmagicmethodcall.CLASS = porigin_leaf
pmagicmethodcall.OBJECT = n_maker
pmagicmethodcall.NAME = $ptascii("open")
pmagicmethodcall.CALLER = eps
pmagicmethodcall.OWNER = 0
|pmagicmethodcall.ARGUMENTS| = 1
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
~((HOBJECT n_maker) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("maker")) = eps
$(n_arguments < |S.ARRAYS|)
~((HARRAY n_arguments) <- S.ALLOCATIONS)
S.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (ALIAS n_cache)]
S.ARRAYS[n_arguments] =/= $magic_method_array([POBJECT n_token], 0)
$magic_method_call_source(S, pmagicmethodcall)
$magic_method_arguments_source(S, pmagicmethodcall.SITE, pmagicmethodcall.ARGUMENTS, 0)
$magic_method_descriptor(S, pmagicmethodcall)
~$magic_method_caller(S, pmagicmethodcall)
~$magic_method_pending(S, pmagicmethodcall, n_arguments, [POBJECT n_token])
~$magic_method_entered(S, S.CURRENT, S.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
$class_method_origin(S.CLASSES, pmagicmethodcall.METHOD) = (pmethoddesc_factory)
pmethoddesc_factory.OWNER = porigin_base
pmethoddesc_factory.NAME = $ptascii("__call")
~$function_generator(S, pmethoddesc_factory.FUNCTION)
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_maker]]
$target_function(S_lookup, METHOD_TARGET n_maker pmagicmethodcall.METHOD) = (pmethoddesc_factory.FUNCTION)
$generator_creator_receiver(S, pgeneratorcreation.CREATOR_TARGET, eps) = (n_maker)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = PNULL
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
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
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf eps poperand_body
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_cache)
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token84R")
$object_name(S, n_input) = $ptascii("Input84R")
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HCELL n_cache) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HOBJECT n_maker) = 0
$heap_owners(H, HARRAY n_arguments) = 0
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HARRAY n_arguments, $fiber_vm_nodes(pfibervm)) = 0
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_owner(S_live) = (n_generator)
$generator_creation_selected(S_live, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
pmagicmethodcall_bad_name = pmagicmethodcall[.NAME = $ptascii("other")]
pgeneratorcreation_bad_name = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_name n_arguments ([POBJECT n_token])]
~$generator_creator_valid(S, pgeneratorcreation_bad_name)
pmagicmethodcall_bad_site = pmagicmethodcall[.SITE = pgeneratorcreation.SITE]
pgeneratorcreation_bad_site = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_site n_arguments ([POBJECT n_token])]
~$generator_creator_valid(S, pgeneratorcreation_bad_site)
pmagicmethodcall_bad_method = pmagicmethodcall[.METHOD = pgenerator.FUNCTION]
pgeneratorcreation_bad_method = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_method n_arguments ([POBJECT n_token])]
~$generator_creator_valid(S, pgeneratorcreation_bad_method)
pmagicmethodcall_bad_class = pmagicmethodcall[.CLASS = porigin_base]
pgeneratorcreation_bad_class = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_class n_arguments ([POBJECT n_token])][.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_class)
pmagicmethodcall_bad_receiver = pmagicmethodcall[.OBJECT = n_input]
pgeneratorcreation_bad_receiver = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_receiver n_arguments ([POBJECT n_token])]
~$generator_creator_valid(S, pgeneratorcreation_bad_receiver)
n_unbounded_object = |S.OBJECTS|
pmagicmethodcall_unbounded_receiver = pmagicmethodcall[.OBJECT = n_unbounded_object]
pgeneratorcreation_unbounded_receiver = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_unbounded_receiver n_arguments ([POBJECT n_token])]
~$generator_creator_valid(S, pgeneratorcreation_unbounded_receiver)
n_unbounded_array = |S.ARRAYS|
pgeneratorcreation_unbounded_array = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_unbounded_array ([POBJECT n_token])]
~$generator_creator_valid(S, pgeneratorcreation_unbounded_array)
pgeneratorcreation_bad_count = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments eps]
~$generator_creator_valid(S, pgeneratorcreation_bad_count)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgeneratorcreation_bad_lexical = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.LEXICAL_CLASS = (porigin_leaf)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_lexical)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_live, n_generator, pgenerator_missing)
$generator_creation_owner(S_missing) = (n_generator)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_current_valid(S_missing)
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
~((HCELL n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
'''.splitlines() if line.strip()]


CASES = {'i84-magic-packed-parked-send-independent': {
    'source': ROW['source'], 'stage': stage, 'checks': checks}}


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
