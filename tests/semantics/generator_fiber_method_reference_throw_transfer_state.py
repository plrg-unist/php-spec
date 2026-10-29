#!/usr/bin/env python3
"""Check a reached cached by-reference method THROW resumer and its receiver."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_method_reference_throw_transfer_cases.json')
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
S.FIBERCLOSERS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cached)
pgenerator.CLOSURE = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
n_cached <- S.REFCELLS
S.STORE[n_cached] = DEFINED (PINT 7)
$lookup(S.ENV, $ptascii("old")) = (n_cached)
$lookup(S.ENV, $ptascii("slot")) = (n_new)
n_cached =/= n_new
S.STORE[n_new] = DEFINED (PINT 9)
$node_children(S, HOBJECT n_generator) = [HCELL n_cached]
$lookup(S.ENV, $ptascii("owner")) = eps
$lookup(S.ENV, $ptascii("weakOwner")) = (n_weak_owner_cell)
S.STORE[n_weak_owner_cell] = DEFINED (POBJECT n_weak_owner)
S.OBJECTS[n_weak_owner] = WEAKREFERENCE (n_receiver)
$node_children(S, HOBJECT n_weak_owner) = eps
$weakref_get(S, n_weak_owner) = POBJECT n_receiver
S.OBJECTS[n_receiver] = INSTANCE porigin_class
$object_name(S, n_receiver) = $ptascii("Receiver68Catch")
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_given)
$node_children(S, HOBJECT n_weak) = eps
$weakref_get(S, n_weak) = POBJECT n_given
$throwable_member(S, n_given)
$lookup(S.ENV, $ptascii("error")) = (n_error_cell)
S.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$object_name(S, n_error) = $ptascii("Error")
$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("Cannot resume an already running generator"))
$throwable_previous_id(S, n_error) = eps
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_given]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
HOBJECT n_given <- $fiber_vm_nodes(pfibervm)
HOBJECT n_given <- $node_children(S, HOBJECT n_fiber)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = METHOD_TARGET n_receiver pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = (n_receiver)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_reference_producer(S_view, pgenerator)
$generator_reference_valid(S_view, GENERATOR pgenerator)
$call_reference_operand_valid(S_view, REFERENCE n_cached)
$call_current_valid(S_view)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
~$fiber_generator_throw_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]], pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator[.VALUE = (PINT 7)], pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator[.REFCELL = eps], pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator[.CLOSURE = (n_fiber)], pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.RECEIVER = eps])
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.RECEIVER = (n_fiber)])
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.INSTANCE = (n_receiver)])
~$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator[.RECEIVER = (n_fiber)])
~$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator[.INSTANCE = (n_receiver)])
pgenerator_nonbyref = pgenerator[.FUNCTION = pcallcontext_callback.FUNCTION]
S_nonbyref = $generator_set(S_view, n_generator, pgenerator_nonbyref)
~$generator_reference_producer(S_nonbyref, pgenerator_nonbyref)
~$fiber_generator_throw_valid(S_nonbyref, pgeneratorop, pgenerator_nonbyref, pcallcontext_generator)
S_badcell = $generator_set(S_view, n_generator, pgenerator[.REFCELL = (|S.STORE|)])
~$fiber_generator_cached_reference_valid(S_badcell, pgenerator[.REFCELL = (|S.STORE|)], pcallcontext_generator)
$fiber_generator_body_id(S_badcell) = eps
S_advance = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ADVANCE = true]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_advance) = eps
S_wrong_receiver = S_view[.CURRENT = (pcallcontext_generator[.RECEIVER = (n_fiber)])]
$fiber_generator_body_id(S_wrong_receiver) = eps
S_wrong_target = S_view[.CURRENT = (pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])]
$fiber_generator_body_id(S_wrong_target) = eps
S_wrong_instance = S_view[.CURRENT = (pcallcontext_generator[.INSTANCE = (n_receiver)])]
$fiber_generator_body_id(S_wrong_instance) = eps
S_current = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "current"][.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_current) = eps
S_next = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "next"][.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_next) = eps
S_send = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "send"][.ARGUMENTS = [PINT 3]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_send) = eps
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
n_receiver <- S_done.DESTRUCTION.CALLED
$weakref_get(S_done, n_weak_owner) = PNULL
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")

CASES = {'i68-method-byref-parked-rebound-cache':
         {'source': ROWS['i68-method-byref-catch-rebind']['source'],
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
