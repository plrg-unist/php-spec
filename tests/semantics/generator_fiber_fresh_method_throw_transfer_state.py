#!/usr/bin/env python3
"""Check a reached fresh by-value method THROW scope and value-cache ownership."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_fresh_method_throw_transfer_cases.json')
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
    '-- if pfiber.STATUS = FIBER_SUSPENDED '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.CLOSURE = eps
pgenerator.REFCELL = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
$lookup(S.ENV, $ptascii("owner")) = eps
$lookup(S.ENV, $ptascii("weakOwner")) = (n_weak_owner_cell)
S.STORE[n_weak_owner_cell] = DEFINED (POBJECT n_weak_owner)
S.OBJECTS[n_weak_owner] = WEAKREFERENCE (n_receiver)
$node_children(S, HOBJECT n_weak_owner) = eps
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_given_cell)
S.STORE[n_weak_given_cell] = DEFINED (POBJECT n_weak_given)
S.OBJECTS[n_weak_given] = WEAKREFERENCE (n_given)
$node_children(S, HOBJECT n_weak_given) = eps
~$generator_reference_producer(S, pgenerator)
""")
RESUMER = checks(r"""
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
$weakref_get(S, n_weak_owner) = POBJECT n_receiver
$weakref_get(S, n_weak_given) = POBJECT n_given
$throwable_member(S, n_given)
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
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = METHOD_TARGET n_receiver pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = (n_receiver)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$call_current_valid(S_view)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
""")
FRESH = checks(r"""
pgenerator.FIRST
pgenerator.VALUE = eps
pgeneratorop.ADVANCE
$node_children(S, HOBJECT n_generator) = eps
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$lookup(S.ENV, $ptascii("input")) = (n_input)
S.STORE[n_input] = DEFINED (PINT 9)
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (PINT 5)
n_item =/= n_input
~(n_item <- S.REFCELLS)
$heap_owners($heap_graph(S), HCELL n_item) = 1
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
$object_name(S, n_receiver) = $ptascii("Leaf70Catch")
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.LEXICAL_CLASS = (porigin_parent)
porigin_parent =/= porigin_leaf
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_parent
$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "current"][.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "next"][.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "send"][.ARGUMENTS = [PINT 3]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.FIRST = false], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.VALUE = (PINT 7)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.REFCELL = (n_item)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.CLOSURE = (n_fiber)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.RECEIVER = eps])
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.RECEIVER = (n_fiber)])
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.INSTANCE = (n_receiver)])
pgenerator_bogus = pgenerator[.FUNCTION = pcallcontext_callback.FUNCTION]
pcallcontext_bogus = pcallcontext_generator[.FUNCTION = pcallcontext_callback.FUNCTION][.TARGET = METHOD_TARGET n_receiver pcallcontext_callback.FUNCTION]
S_bogus = $generator_set(S_view, n_generator, pgenerator_bogus)[.CURRENT = (pcallcontext_bogus)]
~$generator_reference_producer(S_bogus, pgenerator_bogus)
$fiber_generator_fresh_throw_valid(S_bogus, pgeneratorop, pgenerator_bogus, pcallcontext_bogus)
~$fiber_generator_callee_valid(S_bogus, pgenerator_bogus, pcallcontext_bogus)
$fiber_generator_body_id(S_bogus) = eps
pcallcontext_forged = pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION][.RECEIVER = (n_fiber)]
S_forged = S_view[.CURRENT = (pcallcontext_forged)]
$fiber_generator_fresh_throw_valid(S_forged, pgeneratorop, pgenerator, pcallcontext_forged)
~$fiber_generator_callee_valid(S_forged, pgenerator, pcallcontext_forged)
$fiber_generator_body_id(S_forged) = eps
S_lexical = S_view[.CURRENT = (pcallcontext_generator[.LEXICAL_CLASS = (porigin_leaf)])]
$fiber_generator_body_id(S_lexical) = eps
S_called = S_view[.CURRENT = (pcallcontext_generator[.CALLED_CLASS = (porigin_parent)])]
$fiber_generator_body_id(S_called) = eps
S_noadvance = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ADVANCE = false]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_noadvance) = eps
S_current = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "current"][.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_current) = eps
S_next = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "next"][.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_next) = eps
S_send = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "send"][.ARGUMENTS = [PINT 3]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_send) = eps
""")
TOKEN = checks(r"""
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
S.OBJECTS[n_weak_token] = WEAKREFERENCE (n_token)
$node_children(S, HOBJECT n_weak_token) = eps
$weakref_get(S, n_weak_token) = POBJECT n_token
$object_name(S, n_token) = $ptascii("Token70Normal")
pgenerator.VALUE = (POBJECT n_token)
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
""")
CACHED = checks(r"""
~pgeneratorop.ADVANCE
$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$heap_owners($heap_graph(S), HOBJECT n_token) = 2
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (POBJECT n_token)
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HOBJECT n_given) = 2
$heap_count(HOBJECT n_given, $fiber_vm_nodes(pfibervm)) = 2
$object_name(S, n_receiver) = $ptascii("Receiver70Normal")
""")
CLOSED = checks(r"""
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.FRAME = eps
~((HOBJECT n_receiver) <- S.ALLOCATIONS)
~((HOBJECT n_given) <- S.ALLOCATIONS)
n_receiver <- S.DESTRUCTION.CALLED
$weakref_get(S, n_weak_owner) = PNULL
$weakref_get(S, n_weak_given) = PNULL
$heap_owners($heap_graph(S), HOBJECT n_token) = 1
~(n_token <- S.DESTRUCTION.CALLED)
$generator_saved_fiber_ids(S) = eps
$generator_owners_valid(S)
""")
ENDING = checks(r"""
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
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")
TOKEN_END = checks(r"""
n_token <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
""")
NORMAL_SOURCE = ROWS['i70-fresh-method-finally-normal-token-cache']['source']
CACHE_LINE = next(i for i,line in enumerate(NORMAL_SOURCE.splitlines(),1) if line.startswith("echo 'CACHE|'"))
CASES = {
    'i70-inherited-pre-yield-copied-scalar':
        {'source': ROWS['i70-fresh-inherited-method-scalar-catch']['source'],
         'stage': PARK_STAGE + ' -- if pgenerator.VALUE = eps',
         'checks': [*COMMON, *RESUMER, *FRESH, *ENDING]},
    'i70-pending-finally-token-value-cache':
        {'source': NORMAL_SOURCE,
         'stage': PARK_STAGE + ' -- if pgenerator.VALUE = (POBJECT n_token)',
         'checks': [*COMMON, *RESUMER, *TOKEN, *CACHED, *ENDING, *TOKEN_END]},
    'i70-closed-token-only-cache':
        {'source': NORMAL_SOURCE,
         'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
                  f'-- if pconfigcall.LINE = {CACHE_LINE}',
         'checks': [*COMMON, *TOKEN, *CLOSED, *ENDING, *TOKEN_END]},
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
