#!/usr/bin/env python3
"""Check private array-factory authority and parked reference SEND owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_array_string_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i81-array-private-reference-abort-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

stage = (
    'S.ACTIVEFIBER = eps '
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
S.OBJECTS[n_factory] = ARRAYMETHODCLOSURE (SCOPE_METHOD_TARGET (METHOD_TARGET n_host porigin_make) pcallableaccess) parrayselection eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base81"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Host81"))) = (porigin_host)
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_host
pclosurescope.RECEIVER = (n_host)
pclosurescope.CREATION = eps
S.OBJECTS[n_host] = INSTANCE porigin_host
~((HOBJECT n_host) <- S.ALLOCATIONS)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
pcallableaccess.SCOPE = (porigin_base)
pcallableaccess.OBJECT
pcallableaccess.SITE = (parrayselection.SITE)
pcallableaccess.CREATION = eps
parrayselection.REQUESTED = porigin_host
parrayselection.NAME = $ptascii("make")
porigin_make = pgeneratorcreation.CREATOR.FUNCTION
~$closure_callable(S, n_factory)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
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
pcallcontext_generator.CALLED_CLASS = (porigin_host)
pcallcontext_generator.RECEIVER = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_cache)
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token81")
$object_name(S, n_input) = $ptascii("Input81")
$lookup(S.ENV, $ptascii("token")) = (n_rebound)
n_rebound =/= n_cache
S.STORE[n_rebound] = DEFINED (PINT 81)
$node_children(S, HOBJECT n_generator) = [HCELL n_cache]
$node_children(S, HCELL n_cache) = [HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HCELL n_cache) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HOBJECT n_factory) = 0
$heap_owners(H, HOBJECT n_host) = 0
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
pclosurescope_bad_lexical = pclosurescope[.LEXICAL = porigin_host]
~$generator_captured_factory_valid(S, pclosurescope_bad_lexical, porigin_make)
pclosurescope_bad_called = pclosurescope[.CALLED = porigin_base]
~$generator_captured_factory_valid(S, pclosurescope_bad_called, porigin_make)
pcallableaccess_bad_scope = pcallableaccess[.SCOPE = (porigin_host)]
S_bad_scope = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, ARRAYMETHODCLOSURE (SCOPE_METHOD_TARGET (METHOD_TARGET n_host porigin_make) pcallableaccess_bad_scope) parrayselection eps)]
~$generator_captured_factory_valid(S_bad_scope, pclosurescope, porigin_make)
pcallableaccess_bad_site = pcallableaccess[.SITE = (pgeneratorcreation.SITE)]
S_bad_site = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, ARRAYMETHODCLOSURE (SCOPE_METHOD_TARGET (METHOD_TARGET n_host porigin_make) pcallableaccess_bad_site) parrayselection eps)]
~$generator_captured_factory_valid(S_bad_site, pclosurescope, porigin_make)
pcallableaccess_bad_certificate = pcallableaccess[.CREATION = (pgeneratorcreation.CREATOR)]
S_bad_certificate = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, ARRAYMETHODCLOSURE (SCOPE_METHOD_TARGET (METHOD_TARGET n_host porigin_make) pcallableaccess_bad_certificate) parrayselection (pgeneratorcreation.CREATOR))]
~$generator_captured_factory_valid(S_bad_certificate, pclosurescope, porigin_make)
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


CASES = {'i81-private-array-parked-send-independent': {
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
