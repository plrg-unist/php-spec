#!/usr/bin/env python3
"""Check repeated method binding history and parked reference SEND owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_bound_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i82-repeated-private-reference-abort-independent')
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
pgeneratorcreation.CLOSURE = (CLOSURE_SCOPE pclosurescope)
pgeneratorcreation.ANCESTORS = eps
n_factory = pclosurescope.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
S.OBJECTS[n_factory] = BOUNDFAKECLOSURE pboundfake
n_first = pboundfake.SOURCE
S.OBJECTS[n_first] = BOUNDFAKECLOSURE pboundfake_first
n_source = pboundfake_first.SOURCE
pboundfake_first.ORIGINAL = (pclosurescope_original)
S.OBJECTS[n_source] = METHODCLOSURE porigin_make porigin_capture porigin_old eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base82R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Old82R"))) = (porigin_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Middle82R"))) = (porigin_middle)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Final82R"))) = (porigin_final)
pboundfake.SCOPE = BIND_CLASS porigin_base
pboundfake.CALLED = BIND_CLASS porigin_final
pboundfake.RECEIVER = (n_final)
pboundfake.ORIGINAL = eps
pboundfake_first.SCOPE = BIND_CLASS porigin_base
pboundfake_first.CALLED = BIND_CLASS porigin_middle
pboundfake_first.RECEIVER = (n_middle)
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_old
pclosurescope_original.RECEIVER = (n_old)
pclosurescope_original.CREATION = eps
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_final
pclosurescope.RECEIVER = (n_final)
pclosurescope.CREATION = eps
S.OBJECTS[n_old] = INSTANCE porigin_old
S.OBJECTS[n_middle] = INSTANCE porigin_middle
S.OBJECTS[n_final] = INSTANCE porigin_final
$(n_source < n_first)
$(n_first < n_factory)
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_first) <- S.ALLOCATIONS)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
~((HOBJECT n_middle) <- S.ALLOCATIONS)
~((HOBJECT n_final) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_first) = eps
$closure_scope_at(S.CLOSURESCOPES, n_factory) = eps
$node_children(S, HOBJECT n_factory) = [HOBJECT n_final]
$node_children(S, HOBJECT n_first) = [HOBJECT n_middle]
porigin_make = pgeneratorcreation.CREATOR.FUNCTION
~$closure_callable(S, n_factory)
~$bound_fake_valid(S, n_factory)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_factory, HOBJECT n_final]]
$bound_fake_valid(S_lookup, n_factory)
$target_function(S_lookup, CLOSURE_TARGET n_factory) = (pfunction_factory)
pfunction_factory.ORIGIN = porigin_make
$target_lexical_class(S_lookup, CLOSURE_TARGET n_factory) = (porigin_base)
$target_called_class(S_lookup, CLOSURE_TARGET n_factory) = (porigin_final)
$target_receiver(S_lookup, CLOSURE_TARGET n_factory) = (n_final)
$generator_captured_factory_valid(S, pclosurescope, porigin_make)
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
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_final)
pcallcontext_generator.RECEIVER = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_final eps poperand_body
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_cache)
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token82R")
$object_name(S, n_input) = $ptascii("Input82R")
$lookup(S.ENV, $ptascii("token")) = (n_rebound)
n_rebound =/= n_cache
S.STORE[n_rebound] = DEFINED (PINT 82)
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HCELL n_cache) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HOBJECT n_factory) = 0
$heap_owners(H, HOBJECT n_first) = 0
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_old) = 0
$heap_owners(H, HOBJECT n_middle) = 0
$heap_owners(H, HOBJECT n_final) = 0
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
pclosurescope_no_receiver = pclosurescope[.RECEIVER = eps]
~$generator_captured_factory_valid(S, pclosurescope_no_receiver, porigin_make)
pclosurescope_bad_receiver = pclosurescope[.RECEIVER = (n_middle)]
~$generator_captured_factory_valid(S, pclosurescope_bad_receiver, porigin_make)
pclosurescope_unbounded_receiver = pclosurescope[.RECEIVER = (|S.OBJECTS|)]
~$generator_captured_factory_valid(S, pclosurescope_unbounded_receiver, porigin_make)
pclosurescope_bad_lexical = pclosurescope[.LEXICAL = porigin_final]
~$generator_captured_factory_valid(S, pclosurescope_bad_lexical, porigin_make)
pclosurescope_bad_called = pclosurescope[.CALLED = porigin_middle]
~$generator_captured_factory_valid(S, pclosurescope_bad_called, porigin_make)
pboundfake_self = pboundfake[.SOURCE = n_factory]
S_self = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_self)]
~$generator_captured_factory_valid(S_self, pclosurescope, porigin_make)
pboundfake_unbounded = pboundfake[.SOURCE = |S.OBJECTS|]
S_unbounded = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_unbounded)]
~$generator_captured_factory_valid(S_unbounded, pclosurescope, porigin_make)
pboundfake_bad_original = pboundfake[.ORIGINAL = (pclosurescope_original)]
S_bad_original = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_bad_original)]
~$generator_captured_factory_valid(S_bad_original, pclosurescope, porigin_make)
pboundfake_missing_history = pboundfake_first[.ORIGINAL = eps]
S_missing_history = S[.OBJECTS = $object_set(S.OBJECTS, n_first, BOUNDFAKECLOSURE pboundfake_missing_history)]
~$generator_captured_factory_valid(S_missing_history, pclosurescope, porigin_make)
pclosurescope_original_bad_lexical = pclosurescope_original[.LEXICAL = porigin_final]
pboundfake_bad_history = pboundfake_first[.ORIGINAL = (pclosurescope_original_bad_lexical)]
S_bad_history = S[.OBJECTS = $object_set(S.OBJECTS, n_first, BOUNDFAKECLOSURE pboundfake_bad_history)]
~$generator_captured_factory_valid(S_bad_history, pclosurescope, porigin_make)
pboundfake_bad_site = pboundfake_first[.SITE = pgeneratorcreation.SITE]
S_bad_site = S[.OBJECTS = $object_set(S.OBJECTS, n_first, BOUNDFAKECLOSURE pboundfake_bad_site)]
~$generator_captured_factory_valid(S_bad_site, pclosurescope, porigin_make)
pboundfake_bad_scope = pboundfake[.SCOPE = BIND_CLASS porigin_final]
S_bad_scope = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_bad_scope)]
~$generator_captured_factory_valid(S_bad_scope, pclosurescope, porigin_make)
pboundfake_bad_called = pboundfake[.CALLED = BIND_CLASS porigin_middle]
S_bad_called = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_bad_called)]
~$generator_captured_factory_valid(S_bad_called, pclosurescope, porigin_make)
pclosurescope_first = pclosurescope[.OBJECT = n_first][.CALLED = porigin_middle][.RECEIVER = (n_middle)]
$generator_captured_factory_valid(S, pclosurescope_first, porigin_make)
pgeneratorcreation_wrong_factory = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_first)]
~$generator_creator_valid(S, pgeneratorcreation_wrong_factory)
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


CASES = {'i82-repeated-private-parked-send-independent': {
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
