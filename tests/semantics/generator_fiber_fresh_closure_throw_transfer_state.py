#!/usr/bin/env python3
"""Check the source-reached fresh Closure THROW resumer, capture and parked temporary."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_fresh_closure_throw_transfer_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

CHECKS = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FIRST
~pgenerator.PENDING_INIT
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.CLOSURE = (n_callee)
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_given)
$node_children(S, HOBJECT n_weak) = eps
$weakref_get(S, n_weak) = POBJECT n_given
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_given]
pgeneratorop.LOOP = eps
pgeneratorop.ADVANCE
$throwable_member(S, n_given)
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
HOBJECT n_given <- $fiber_vm_nodes(pfibervm)
HOBJECT n_given <- $node_children(S, HOBJECT n_fiber)
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
pgeneratorop.STARTPACK = false
pgeneratorop.BORROWED = false
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callee
pcallcontext_generator.INSTANCE = (n_callee)
pcallcontext_generator.RECEIVER = eps
$lookup(S.ENV, $ptascii("factory")) = eps
$lookup(S.ENV, $ptascii("weakClosure")) = (n_weak_callee_cell)
S.STORE[n_weak_callee_cell] = DEFINED (POBJECT n_weak_callee)
S.OBJECTS[n_weak_callee] = WEAKREFERENCE (n_callee)
$weakref_get(S, n_weak_callee) = POBJECT n_callee
S.OBJECTS[n_callee] = REALCLOSURE pgenerator.FUNCTION pitem* eps
$lookup(S.ENV, $ptascii("source")) = (n_global_source)
S.STORE[n_global_source] = DEFINED (POBJECT n_new)
$object_name(S, n_new) = $ptascii("CopyB65")
$lookup(S.ENV, $ptascii("weakA")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
S.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$object_name(S, n_old) = $ptascii("CopyA65")
pitem* = [DIRECT (POBJECT n_old)]
$node_children(S, HOBJECT n_callee) = [HOBJECT n_old]
$lookup(pfibervm.TABLE.ENV, $ptascii("source")) = (n_local_source)
S.STORE[n_local_source] = DEFINED (POBJECT n_old)
n_local_source =/= n_global_source
$node_children(S, HCELL n_local_source) = [HOBJECT n_old]
$heap_owners($heap_graph(S), HOBJECT n_old) = 2
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
~$generator_reference_producer(S_view, pgenerator)
$call_current_valid(S_view)
$generator_closure_valid(S_view, pgenerator)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.FIRST = false], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.VALUE = (PINT 7)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.REFCELL = (|S.STORE|)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.CLOSURE = eps], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.INSTANCE = eps])
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.RECEIVER = (n_fiber)])
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])
S_noarg = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_noarg) = eps
S_noadvance = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ADVANCE = false]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_noadvance) = eps
S_method = S_view[.CURRENT = (pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])]
$fiber_generator_body_id(S_method) = eps
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
n_old <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")

CASES = {'i65-fresh-closure-pre-yield-copy-owner':
         {'source': ROWS['i65-fresh-closure-copy-catch']['source'],
          'stage': STAGE, 'checks': CHECKS}}

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
