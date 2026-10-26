#!/usr/bin/env python3
"""Reach authentic helper prefixes, projected Generator scopes and parameter roots."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_helper_transfer_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
ONE = 'generator-fiber-helper-one-current'
TWO = 'generator-fiber-helper-two-next'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.ACTIVEFIBER = eps -- if S.CURRENT = eps '
         '-- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
         '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
         '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
         '-- if pfiber.STATUS = FIBER_SUSPENDED')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_helper)
pcallcontext_helper.NAME = $ptascii("Pause54")
pcallcontext_helper.TARGET = pcallcontext_helper.FUNCTION
pcallcontext_helper.INSTANCE = eps
pcallcontext_helper.CALLSITE = (porigin_helper)
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.SENT = (PSTRING_CARRIER INTERNED_STRING $ptascii("pause54"))
pfiberapi.SEQUENCE = pfiber.SEQUENCE
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
pframe_resumer.CONTEXT = (pcallcontext_callback)
pframe_root.TODO = [FIBER_FINISH n_fiber]
pframe_root.CONTEXT = eps
n_generator = pgeneratorop.OBJECT
pgeneratorop.LOOP = eps
pgeneratorop.ARGUMENTS = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.DELEGATE = eps
pgenerator.PARKED = eps
pgenerator.RETURN = eps
pgenerator.REFCELL = eps
~pgenerator.PENDING_INIT
$node_children(S, HOBJECT n_generator) = eps
$heap_owners($heap_graph(S), HOBJECT n_generator) = 2
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
$task_nodes(FIBER_CONTINUE pfiberapi) = eps
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_token_helper)
S.STORE[n_token_helper] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("HelperToken54")
$node_children(S, HCELL n_token_helper) = [HOBJECT n_token]
$heap_count(HCELL n_token_helper, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HCELL n_token_helper) = 1
~(n_token <- S.DESTRUCTION.CALLED)
$lookup(S.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$node_children(S, HOBJECT n_weak) = eps
$weakref_get(S, n_weak) = POBJECT n_token
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]
~$generator_active(S_view)
$call_current_valid(S_view)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$generator_saved_ids(S_view.FRAMES) = [n_generator]
$generator_flat_tasks(S_view.TODO)
$generator_flat_frames(S_view.FRAMES)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$fiber_generator_body_id(S_view[.ACTIVEFIBER = eps]) = (n_generator)
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = (n_generator)])
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = (|S.OBJECTS|)])
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
""")
GENERATOR_SCOPE = checks(r"""
S_gen.CURRENT = (pcallcontext_generator)
pcallcontext_generator.NAME = $ptascii("Work54")
pcallcontext_generator.TARGET = pgenerator.FUNCTION
S_gen.FRAMES = [pframe_resumer, pframe_root]
$generator_active(S_gen)
$call_current_valid(S_gen)
$fiber_generator_body_id(S_gen) = (n_generator)
S_gen.OBJECTS = S.OBJECTS
S_gen.STORE = S.STORE
S_gen.ALLOCATIONS = S.ALLOCATIONS
$lookup(S_gen.ENV, $ptascii("token")) = (n_token_generator)
S.STORE[n_token_generator] = DEFINED (POBJECT n_token)
n_token_generator =/= n_token_helper
$node_children(S, HCELL n_token_generator) = [HOBJECT n_token]
$heap_owners($heap_graph(S), HCELL n_token_generator) = 1
""")
# Constructed source/metadata controls; they do not add new PHP producers.
REFUSALS = checks(r"""
S_view.FRAMES = pframe_first :: pframe_tail*
H_view = $heap_graph(S_view)
pframe_origin = pframe_first[.ORIGIN = eps]
S_origin = S_view[.FRAMES = pframe_origin :: pframe_tail*]
$heap_graph(S_origin) = H_view
$fiber_generator_body_id(S_origin) = eps
S_line = S_view[.CURRENT = (pcallcontext_helper[.LINE = $(pcallcontext_helper.LINE + 1)])]
$heap_graph(S_line) = H_view
$fiber_generator_body_id(S_line) = eps
S_target = S_view[.CURRENT = (pcallcontext_helper[.TARGET = pgenerator.FUNCTION])]
$heap_graph(S_target) = H_view
$fiber_generator_body_id(S_target) = eps
S_no_locals = S_view[.FRAMES = pframe_first[.LOCALS = eps] :: pframe_tail*]
$fiber_generator_body_id(S_no_locals) = eps
S_no_context = S_view[.FRAMES = pframe_first[.CONTEXT = eps] :: pframe_tail*]
$fiber_generator_body_id(S_no_context) = eps
S_initializer = S_view[.CONSTCONTEXT = ({ORIGIN pcallcontext_helper.FUNCTION, LINE 1, FACTS eps})]
$fiber_generator_body_id(S_initializer) = eps
~$fiber_transfer_domain(S_initializer)
pframe_extra = pframe_first[.TODO = (GENERATOR_RESUME pgeneratorop) :: pframe_first.TODO]
S_extra = S_view[.FRAMES = pframe_extra :: pframe_tail*]
$generator_saved_ids(S_extra.FRAMES) = [n_generator, n_generator]
$fiber_generator_body_id(S_extra) = eps
pframe_hidden = pframe_first[.TODO = (AT pgeneratorop.SITE (GENERATOR_RESUME pgeneratorop)) :: pframe_first.TODO]
S_hidden = S_view[.FRAMES = pframe_hidden :: pframe_tail*]
$generator_saved_ids(S_hidden.FRAMES) = [n_generator]
~$generator_flat_frames(S_hidden.FRAMES)
$fiber_generator_body_id(S_hidden) = eps
S_task = S_view[.TODO = (AT pgeneratorop.SITE (GENERATOR_RESUME pgeneratorop)) :: S_view.TODO]
$generator_resume_ids(S_task.TODO) = eps
~$generator_flat_tasks(S_task.TODO)
$fiber_generator_body_id(S_task) = eps
n_copy = |S.OBJECTS|
S_copy = S[.OBJECTS = S.OBJECTS ++ [FIBER pfiber]][.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_copy]]
$generator_saved_fiber_ids(S_copy) = [n_generator, n_generator]
~$generator_owners_valid(S_copy)
""")
ENDING = checks(r"""
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_done = $drive(S_one, 4000)
$drive(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
S_done.HELD = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
n_token <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
$generator_saved_fiber_ids(S_done) = eps
""")
FINISH = ['FIBER|','1','|','1','|','CACHE|','1','|','1','|',
          'AFTER|','D|','RETURN|','1','|','1','|','E']
EVENTS = {
 ONE: ['START|','F|','CURRENT|','G|','H|','1','|','PARKED|','1','|','1','|',
       'RESUME|','R|','VALUE|','1','|','1','|','CALLER|','1','|',*FINISH],
 TWO: ['G|','START|','F|','NEXT|','O|','H|','1','|','PARKED|','1','|','1','|',
       'RESUME|','R|','VALUE|','1','|','1','|','CURRENT|','1','|','CALLER|','1','|',*FINISH],
}
assert all(''.join(parts)==ROWS[name]['native_stdout'] for name,parts in EVENTS.items())
CASES = {
 'generator-fiber-one-helper-real-caller-scope': {
  'source':ROWS[ONE]['source'], 'stage':STAGE,
  'checks':[*checks(r"""
pfiber.VM = (pfibervm)
pfibervm.FRAMES = [pframe_generator, pframe_resumer, pframe_root]
"""),*COMMON,*checks(r"""
pframe_generator.ORIGIN = (porigin_helper)
S_gen = $constant_frame_scope(S_view, pframe_generator, [pframe_resumer, pframe_root])
pgeneratorop.NAME = "current"
pgenerator.VALUE = eps
pgenerator.KEY = eps
$heap_owners($heap_graph(S), HOBJECT n_token) = 2
"""),*GENERATOR_SCOPE,*REFUSALS,*ENDING,events(EVENTS[ONE])],
 },
 'generator-fiber-two-helper-complete-prefix': {
  'source':ROWS[TWO]['source'], 'stage':STAGE,
  'checks':[*checks(r"""
pfiber.VM = (pfibervm)
pfibervm.FRAMES = [pframe_outer, pframe_generator, pframe_resumer, pframe_root]
"""),*COMMON,*checks(r"""
pframe_outer.ORIGIN = (porigin_helper)
S_outer = $constant_frame_scope(S_view, pframe_outer, [pframe_generator, pframe_resumer, pframe_root])
S_outer.CURRENT = (pcallcontext_outer)
pcallcontext_outer.NAME = $ptascii("OuterPause54")
~$generator_active(S_outer)
$call_current_valid(S_outer)
$fiber_generator_body_id(S_outer) = (n_generator)
S_outer.OBJECTS = S.OBJECTS
S_outer.STORE = S.STORE
S_outer.ALLOCATIONS = S.ALLOCATIONS
$lookup(S_outer.ENV, $ptascii("token")) = (n_token_outer)
S.STORE[n_token_outer] = DEFINED (POBJECT n_token)
n_token_outer =/= n_token_helper
$node_children(S, HCELL n_token_outer) = [HOBJECT n_token]
$heap_count(HCELL n_token_outer, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HCELL n_token_outer) = 1
S_gen = $constant_frame_scope(S_outer, pframe_generator, [pframe_resumer, pframe_root])
pgeneratorop.NAME = "next"
pgenerator.VALUE = (PSTRING_CARRIER INTERNED_STRING $ptascii("first54"))
pgenerator.KEY = (PINT 0)
$heap_owners($heap_graph(S), HOBJECT n_token) = 3
"""),*GENERATOR_SCOPE,"n_token_generator =/= n_token_outer",*REFUSALS,*ENDING,events(EVENTS[TWO])],
 },
}


def run(selected):
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
        passed = review.run(selected)
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
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
