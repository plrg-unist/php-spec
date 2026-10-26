#!/usr/bin/env python3
"""Reach real delegated Generator Fiber roots and source-authenticated carriers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_delegation_transfer_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
FRESH = 'generator-fiber-delegation-fresh-current'
PENDING_COMPLETIONS = {'generator-fiber-fresh-native-link-completion'}


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


PARTS = ['START|','CALL|','CHILD|','PAUSE|','1','|','1','|','OWNERS|',
         '1','|','1','|','RESUME|','RESUMED|','1','|','VALUE|','1','|','1','|',
         'FINISH|','1','|','1','|','CACHE|','1','|','1','|','NEXT|','LEAF-END|',
         'ROOT-RETURN|','1','|','ROOT-FINALLY|','RETURN|','1','|','1','|',
         'D|','WEAK|','1','|','1','|','E']
assert ''.join(PARTS) == ROWS[FRESH]['native_stdout']
EVENTS = 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(p) + ')' for p in PARTS) + ']'
PREFIX = 'S.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(p) + ')' for p in PARTS[:9]) + ']'
STAGE = ('S.ACTIVEFIBER = eps -- if S.CURRENT = eps '
         '-- if $lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell) '
         '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
         '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
         '-- if pfiber.STATUS = FIBER_SUSPENDED -- if ' + PREFIX)
BINDINGS = checks(r'''
S.COMPLETION = NORMAL
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_child)
pcallcontext_child.NAME = $ptascii("child55")
pfibervm.FRAMES = [pframe_parent, pframe_api, pframe_base]
pframe_parent.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin n_child) :: ptask_parent*
pframe_api.TODO = (GENERATOR_RESUME pgeneratorop_parent) :: ptask_api*
n_child = pgeneratorop_child.OBJECT
n_parent = pgeneratorop_parent.OBJECT
pgeneratorop_child.NAME = "current"
pgeneratorop_parent.NAME = "current"
pframe_base.TODO = [FIBER_FINISH n_fiber]
pframe_parent.LOCALS = (psymboltable_parent)
S.OBJECTS[n_parent] = GENERATOR pgenerator_parent
S.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_parent.PHASE = GENERATOR_RUNNING
pgenerator_child.PHASE = GENERATOR_RUNNING
pgenerator_parent.PENDING_INIT
~pgenerator_child.PENDING_INIT
pgenerator_parent.FRAME = eps
pgenerator_child.FRAME = eps
pgenerator_parent.DELEGATE = (pgeneratorfrom)
pgeneratorfrom.INPUT = (POBJECT n_child)
pgeneratorfrom.SITE = porigin
pgeneratorfrom.POSITION = 0
pgeneratorfrom.CURRENT = eps
$node_children(S, HOBJECT n_parent) = [HOBJECT n_child]
$node_children(S, HOBJECT n_child) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop_child) = [HOBJECT n_child]
$task_nodes(GENERATOR_FROM_RESULT n_parent porigin n_child) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop_parent) = [HOBJECT n_parent]
$lookup(S.ENV, $ptascii("child")) = eps
$lookup(psymboltable_parent.ENV, $ptascii("child")) = (n_child_cell)
S.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$heap_owners($heap_graph(S), HCELL n_child_cell) = 1
$heap_owners($heap_graph(S), HOBJECT n_child) = 3
$heap_owners($heap_graph(S), HOBJECT n_parent) = 2
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_token_cell)
S.STORE[n_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token55")
$heap_owners($heap_graph(S), HCELL n_token_cell) = 1
$heap_owners($heap_graph(S), HOBJECT n_token) = 1
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$lookup(S.ENV, $ptascii("childWeak")) = (n_child_weak_cell)
S.STORE[n_child_weak_cell] = DEFINED (POBJECT n_child_weak)
S.OBJECTS[n_child_weak] = WEAKREFERENCE (n_child)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]
$fiber_generator_body_id(S_view) = eps
$fiber_generator_delegation_ids(S_view) = [n_child, n_parent]
$generator_saved_fiber_ids(S) = [n_child, n_parent]
$generator_from_saved_fiber_claims(S) = [n_parent]
$fiber_transfer_domain(S_view)
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
S_parent = $constant_frame_scope(S_view, pframe_parent, [pframe_api, pframe_base])[.TODO = ptask_parent*]
$fiber_generator_chain_ids(S_parent) = [n_parent]
S_parent.OBJECTS = S.OBJECTS
S_parent.STORE = S.STORE
S_parent.ALLOCATIONS = S.ALLOCATIONS
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')
# Constructed metadata/carrier controls are not fresh PHP source histories.
REFUSALS = checks(r'''
H_view = $heap_graph(S_view)
pframe_line = pframe_parent[.TODO = (GENERATOR_RESUME pgeneratorop_child[.LINE = $(pgeneratorop_child.LINE + 1)]) :: (GENERATOR_FROM_RESULT n_parent porigin n_child) :: ptask_parent*]
S_line = S_view[.FRAMES = [pframe_line, pframe_api, pframe_base]]
$heap_graph(S_line) = H_view
$fiber_generator_delegation_ids(S_line) = eps
pframe_missing = pframe_parent[.TODO = (GENERATOR_RESUME pgeneratorop_child) :: ptask_parent*]
pfibervm_missing = pfibervm[.FRAMES = [pframe_missing, pframe_api, pframe_base]]
S_missing = S[.OBJECTS = $object_set(S.OBJECTS, n_fiber, FIBER pfiber[.VM = (pfibervm_missing)])]
$heap_graph(S_missing) = $heap_graph(S)
~$call_descriptors_valid(S_missing)
pframe_extra = pframe_parent[.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin n_child) :: (GENERATOR_FROM_RESULT n_parent porigin n_child) :: ptask_parent*]
S_extra = S_view[.FRAMES = [pframe_extra, pframe_api, pframe_base]]
$heap_graph(S_extra) = H_view
$fiber_generator_delegation_ids(S_extra) = eps
pframe_hidden = pframe_parent[.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (AT porigin (GENERATOR_FROM_RESULT n_parent porigin n_child)) :: ptask_parent*]
S_hidden = S_view[.FRAMES = [pframe_hidden, pframe_api, pframe_base]]
$heap_graph(S_hidden) = H_view
$fiber_generator_delegation_ids(S_hidden) = eps
S_duplicate = S[.OBJECTS = $object_set(S.OBJECTS, n_child_weak, FIBER pfiber)]
$generator_saved_fiber_ids(S_duplicate) = [n_child, n_parent, n_child, n_parent]
$generator_from_saved_fiber_claims(S_duplicate) = [n_parent, n_parent]
~$generator_owners_valid(S_duplicate)
~$generator_from_state_valid(S_duplicate)
''')
# These fixed points establish the public drive preprocessing once per input.
# The raw whole/split equalities then retain its 0/1/2/4000-step behavior.
ENDING = checks(r'''
$call_entry_check(S) = S
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S))) = S
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$call_entry_check(S_one) = S_one
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S_one))) = S_one
S_two_budget = $drive_steps(S_one, 1)
$drive_steps(S, 2) = S_two_budget
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
S_done.HELD = eps
n_token <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_parent) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
$generator_saved_fiber_ids(S_done) = eps
$generator_from_saved_fiber_claims(S_done) = eps
''')
# Retain the full whole/split ending as a named core-required recipe. The
# default tests structure and its real public 0/1/2 prefix without long completion.
SHORT = ENDING[:ENDING.index('S_done = $drive_steps(S_one, 4000)')]
COMPLETION_BINDINGS = checks(r"""
pfiber.VM = (pfibervm)
pfibervm.FRAMES = [pframe_parent, pframe_api, pframe_base]
pframe_parent.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin n_child) :: ptask_parent*
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
""")
CASES = {
 'generator-fiber-fresh-native-link-parked-structure': {
    'source': ROWS[FRESH]['source'], 'stage': STAGE,
    'checks': [*BINDINGS, *REFUSALS, *SHORT],
 },
 'generator-fiber-fresh-native-link-completion': {
    'source': ROWS[FRESH]['source'], 'stage': STAGE,
    'checks': [*COMPLETION_BINDINGS, *ENDING, EVENTS],
 },
}


def run(selected, *, pending_completion=False):
    assert not pending_completion or selected and set(selected) <= PENDING_COMPLETIONS
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=review.ROOT,text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None
    def recorded(command,directory,stem,environment,cap):
        nonlocal raw
        raw = directory.parent
        return original(command,directory,stem,environment,cap)
    review.recorded = recorded
    try:
        passed = review.run(selected, process_seconds=240 if pending_completion else 120)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p:p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git','rev-parse','HEAD'],cwd=review.ROOT,text=True).strip()
    path=raw/'report.json';report=json.loads(path.read_bytes())
    report.update(author_inputs={str(p):hashlib.sha256(b).hexdigest() for p,b in INPUT_BYTES.items()},
                  author_inputs_stable=stable,head_stable=head_stable,passed=passed and stable and head_stable)
    path.write_text(json.dumps(report,indent=2)+'\n')
    return passed and stable and head_stable


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',action='append')
    parser.add_argument('--pending-completion', action='store_true',
                        help='Use the fixed 240s budget for explicit pending whole completions.')
    args = parser.parse_args()
    selected = args.case
    if args.pending_completion and (not selected or not set(selected) <= PENDING_COMPLETIONS):
        parser.error('--pending-completion requires only explicit pending completion --case IDs')
    if selected is None:
        selected = ['generator-fiber-fresh-native-link-parked-structure']
    raise SystemExit(0 if run(selected, pending_completion=args.pending_completion) else 1)
