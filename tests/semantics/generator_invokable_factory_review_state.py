#!/usr/bin/env python3
"""Check inherited implicit factory selection and parked reference SEND owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_invokable_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i83-implicit-inherited-reference-abort-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

stage = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if $lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell) '
    '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED '
    '-- if $lookup(S.ENV, $ptascii("alias")) = eps')

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
pgeneratorcreation.CREATOR_TARGET = METHOD_TARGET n_maker porigin_invoke
pgeneratorcreation.CREATOR.FUNCTION = porigin_invoke
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base83R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid83R"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf83R"))) = (porigin_leaf)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
~((HOBJECT n_maker) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("maker")) = eps
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CREATOR.CALLSITE = (PORIGIN n_unit pcpath_invoke)
$origin_node(S.SOURCES, PORIGIN n_unit pcpath_invoke) = (NExprFuncCall expression_invoke (SEQUENCE phpType7*) metadata_invoke)
$ppcall_dynamic(expression_invoke)
~$ppfirstclass(phpType7*)
$dynamic_fixed_name(S, PORIGIN n_unit pcpath_invoke) = eps
$goto_source_owner($all_functions(S), n_unit, pcpath_invoke) = (pfunction_open)
$class_method_origin(S.CLASSES, pfunction_open.ORIGIN) = (pmethoddesc_open)
pmethoddesc_open.OWNER = porigin_base
pmethoddesc_open.NAME = $ptascii("open")
$object_invoke_method(S, n_maker) = eps
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_maker]]
$object_invoke_method(S_lookup, n_maker) = (pmethoddesc_invoke)
pmethoddesc_invoke.OWNER = porigin_mid
pmethoddesc_invoke.NAME = $ptascii("__invoke")
pmethoddesc_invoke.FUNCTION.ORIGIN = porigin_invoke
~pmethoddesc_invoke.STATIC
~pmethoddesc_invoke.ABSTRACT
$method_call_selected(S_lookup, METHOD_TARGET n_maker porigin_invoke, (PORIGIN n_unit pcpath_invoke))
$generator_implicit_invoke_target(S, METHOD_TARGET n_maker porigin_invoke, PORIGIN n_unit pcpath_invoke)
$effective_method(S, porigin_base, $ptascii("__invoke"), |S.CLASSES|) = (pmethoddesc_base_invoke)
pmethoddesc_base_invoke.FUNCTION.ORIGIN =/= porigin_invoke
~$method_call_selected(S_lookup, METHOD_TARGET n_maker pmethoddesc_base_invoke.FUNCTION.ORIGIN, (PORIGIN n_unit pcpath_invoke))
~$generator_implicit_invoke_target(S, METHOD_TARGET n_maker pmethoddesc_base_invoke.FUNCTION.ORIGIN, PORIGIN n_unit pcpath_invoke)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
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
pcallcontext_generator.LEXICAL_CLASS = (porigin_mid)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_mid pgenerator.FUNCTION porigin_leaf eps poperand_body
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_cache)
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token83R")
$object_name(S, n_input) = $ptascii("Input83R")
$lookup(S.ENV, $ptascii("token")) = (n_rebound)
n_rebound =/= n_cache
S.STORE[n_rebound] = DEFINED (PINT 83)
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HCELL n_cache) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HOBJECT n_maker) = 0
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_owner(S_live) = (n_generator)
$generator_creation_selected(S_live, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_mid)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgeneratorcreation_bad_lexical = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.LEXICAL_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_lexical)
pgeneratorcreation_bad_site = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLSITE = (pgeneratorcreation.SITE)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_site)
pgeneratorcreation_bad_receiver = pgeneratorcreation[.CREATOR_TARGET = METHOD_TARGET n_token porigin_invoke]
~$generator_creator_valid(S, pgeneratorcreation_bad_receiver)
n_unbounded = |S.OBJECTS|
pgeneratorcreation_unbounded_receiver = pgeneratorcreation[.CREATOR_TARGET = METHOD_TARGET n_unbounded porigin_invoke]
~$generator_creator_valid(S, pgeneratorcreation_unbounded_receiver)
~$generator_implicit_invoke_target(S, METHOD_TARGET n_unbounded porigin_invoke, PORIGIN n_unit pcpath_invoke)
~$generator_implicit_invoke_target(S, METHOD_TARGET n_token porigin_invoke, PORIGIN n_unit pcpath_invoke)
~$generator_implicit_invoke_target(S, STATIC_METHOD_TARGET porigin_leaf porigin_invoke, PORIGIN n_unit pcpath_invoke)
~$generator_implicit_invoke_target(S, METHOD_TARGET n_maker porigin_invoke, pgeneratorcreation.SITE)
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


CASES = {'i83-implicit-inherited-parked-send-independent': {
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
