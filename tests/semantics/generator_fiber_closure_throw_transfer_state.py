#!/usr/bin/env python3
"""Reach saved Closure THROW, capture and closed-cache states from PHP sources."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_closure_throw_transfer_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

PARKED = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.VALUE = (PSTRING_CARRIER INTERNED_STRING $ptascii("seed64"))
pgenerator.REFCELL = eps
pgenerator.CLOSURE = (n_callee)
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
$lookup(S.ENV, $ptascii("factory")) = eps
$lookup(S.ENV, $ptascii("weakClosure")) = (n_weak_callee_cell)
S.STORE[n_weak_callee_cell] = DEFINED (POBJECT n_weak_callee)
S.OBJECTS[n_weak_callee] = WEAKREFERENCE (n_callee)
$node_children(S, HOBJECT n_weak_callee) = eps
$weakref_get(S, n_weak_callee) = POBJECT n_callee
S.OBJECTS[n_callee] = REALCLOSURE pgenerator.FUNCTION pitem* eps
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_given_cell)
S.STORE[n_weak_given_cell] = DEFINED (POBJECT n_weak_given)
S.OBJECTS[n_weak_given] = WEAKREFERENCE (n_given)
$node_children(S, HOBJECT n_weak_given) = eps
$weakref_get(S, n_weak_given) = POBJECT n_given
$throwable_member(S, n_given)
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_given]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
HOBJECT n_given <- $fiber_vm_nodes(pfibervm)
HOBJECT n_given <- $node_children(S, HOBJECT n_fiber)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callee
pcallcontext_generator.INSTANCE = (n_callee)
pcallcontext_generator.RECEIVER = eps
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callee]
$node_children(S, HOBJECT n_generator) = eps
$heap_owners($heap_graph(S), HOBJECT n_callee) = 1
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$call_current_valid(S_view)
$generator_closure_valid(S_view, pgenerator)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
~$fiber_generator_throw_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator[.VALUE = eps], pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator[.REFCELL = (|S.STORE|)], pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator[.CLOSURE = eps], pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.INSTANCE = eps])
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.RECEIVER = (n_fiber)])
S_bad_argument = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_bad_argument) = eps
S_advance = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ADVANCE = true]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_advance) = eps
S_wrong_callee = S_view[.OBJECTS = $object_set(S_view.OBJECTS, n_callee, FIBER pfiber)]
$fiber_generator_body_id(S_wrong_callee) = eps
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
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
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_callee) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")

COPIED = checks(r"""
$lookup(S.ENV, $ptascii("source")) = (n_global_source)
S.STORE[n_global_source] = DEFINED (POBJECT n_new)
$object_name(S, n_new) = $ptascii("CopyB64")
$lookup(S.ENV, $ptascii("weakA")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
S.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$object_name(S, n_old) = $ptascii("CopyA64")
pitem* = [DIRECT (POBJECT n_old)]
$node_children(S, HOBJECT n_callee) = [HOBJECT n_old]
$lookup(pfibervm.TABLE.ENV, $ptascii("source")) = (n_local_source)
S.STORE[n_local_source] = DEFINED (POBJECT n_old)
n_local_source =/= n_global_source
$node_children(S, HCELL n_local_source) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HOBJECT n_old) = 2
$lookup(S.ENV, $ptascii("error")) = (n_error_cell)
S.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$object_name(S, n_error) = $ptascii("Error")
$throwable_previous_id(S, n_error) = eps
n_old <- S_done.DESTRUCTION.CALLED
""")

SHARED = checks(r"""
$lookup(S.ENV, $ptascii("source")) = (n_external)
S.STORE[n_external] = DEFINED (POBJECT n_external_object)
$object_name(S, n_external_object) = $ptascii("ReferenceB64")
$lookup(S.ENV, $ptascii("weakC")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
S.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$object_name(S, n_old) = $ptascii("ReferenceC64")
pitem* = [ALIAS n_old_cell]
n_old_cell =/= n_external
n_old_cell <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("source")) = (n_old_cell)
S.STORE[n_old_cell] = DEFINED (POBJECT n_old)
$node_children(S, HOBJECT n_callee) = [HCELL n_old_cell]
$node_children(S, HCELL n_old_cell) = [HOBJECT n_old]
$lookup(S.ENV, $ptascii("weakA")) = (n_weak_a_cell)
S.STORE[n_weak_a_cell] = DEFINED (POBJECT n_weak_a)
$weakref_get(S, n_weak_a) = PNULL
n_old <- S_done.DESTRUCTION.CALLED
""")

NORMAL_SOURCE = ROWS['generator-fiber-closure-throw-closure-object-finally-normal']['source']
CLOSED_LINE = next(i for i, line in enumerate(NORMAL_SOURCE.splitlines(), 1)
                   if line.startswith("echo 'CLOSED|'"))
CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    f'-- if pconfigcall.LINE = {CLOSED_LINE}')
CLOSED_CACHE = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.VALUE = (POBJECT n_token)
pgenerator.REFCELL = eps
pgenerator.CLOSURE = (n_callee)
pgenerator.RETURN = eps
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
S.OBJECTS[n_weak_token] = WEAKREFERENCE (n_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$object_name(S, n_token) = $ptascii("Cache64Normal")
$lookup(S.ENV, $ptascii("weakClosure")) = (n_weak_callee_cell)
S.STORE[n_weak_callee_cell] = DEFINED (POBJECT n_weak_callee)
S.OBJECTS[n_weak_callee] = WEAKREFERENCE (n_callee)
$weakref_get(S, n_weak_callee) = POBJECT n_callee
S.OBJECTS[n_callee] = REALCLOSURE pgenerator.FUNCTION pitem* eps
pitem* = [DIRECT (POBJECT n_token)]
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token, HOBJECT n_callee]
$node_children(S, HOBJECT n_callee) = [HOBJECT n_token]
$heap_owners($heap_graph(S), HOBJECT n_token) = 2
$heap_owners($heap_graph(S), HOBJECT n_callee) = 1
$generator_saved_fiber_ids(S) = eps
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
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
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
n_token <- S_done.DESTRUCTION.CALLED
$weakref_get(S_done, n_weak_token) = PNULL
$weakref_get(S_done, n_weak_callee) = PNULL
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")

CASES = {
    'generator-fiber-closure-throw-copied-capture':
        {'source': ROWS['generator-fiber-closure-throw-closure-copy-catch']['source'],
         'stage': PARK_STAGE, 'checks': [*PARKED, *COPIED]},
    'generator-fiber-closure-throw-original-reference-cell':
        {'source': ROWS['generator-fiber-closure-throw-closure-reference-catch']['source'],
         'stage': PARK_STAGE, 'checks': [*PARKED, *SHARED]},
    'generator-fiber-closure-throw-closed-object-cache':
        {'source': NORMAL_SOURCE, 'stage': CLOSED_STAGE, 'checks': CLOSED_CACHE},
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
        passed = review.run(selected, process_seconds=240)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    report_path = raw / 'report.json'
    report = json.loads(report_path.read_bytes())
    report.update(author_inputs={str(path): hashlib.sha256(data).hexdigest() for path, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
