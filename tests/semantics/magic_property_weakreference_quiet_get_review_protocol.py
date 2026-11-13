#!/usr/bin/env python3
"""Check initialized WeakReference Empty results and saved-receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning

CATALOGUE = Path(__file__).with_name('magic_property_weakreference_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PREFIX = r'''
dec $wr_quiet_resume(pstate) : bool
def $wr_quiet_resume(S) = true
  -- if S.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $wr_quiet_resume(S) = false -- otherwise
dec $wr_quiet_seek(pstate,nat) : pstate
def $wr_quiet_seek(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $wr_quiet_seek(S,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $wr_quiet_resume(S) \/ n = 0
def $wr_quiet_seek(S,n) = $wr_quiet_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$wr_quiet_resume(S) /\ $(n > 0)
'''

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.ORIGIN = (ppropertyempty.SITE) /\ S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_wrapper)
S.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)
S.OBJECTS[n_target] = STDINSTANCE
$(n_target < n_wrapper) /\ (HOBJECT n_wrapper) <- S.ALLOCATIONS
~$instance_storage_freeing(S,n_wrapper)
$weakref_at(S,n_wrapper) = (WEAKREFERENCE (n_target))
$lookup(S.ENV,$ptascii("watch")) = (n_watch_cell)
S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)
S.OBJECTS[n_watch] = WEAKREFERENCE (n_wrapper)
$weakref_get(S,n_watch) = POBJECT n_wrapper
$heap_unique([HOBJECT n_receiver,HOBJECT n_wrapper,HOBJECT n_target,HOBJECT n_watch])
$node_children(S,HOBJECT n_wrapper) = eps /\ $node_children(S,HOBJECT n_watch) = eps
$heap_owners($heap_graph(S),HOBJECT n_wrapper) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("held")) = (n_held)
S.STORE[n_reader] = DEFINED PNULL /\ S.STORE[n_held] = DEFINED PNULL
$lookup(S.ENV,$ptascii("destination")) = (n_destination)
S.STORE[n_destination] = DEFINED (PINT 42)
$property_get_method(S,n_receiver) = (pmethoddesc)
pmethoddesc.FUNCTION.ORIGIN = ppropertyempty.GET
pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)
$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)
$weakref_state_valid(S) /\ $call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

CV_FRONT = r'''
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
(HOBJECT n_target) <- S.ALLOCATIONS
$weakref_get(S,n_wrapper) = POBJECT n_target
$heap_owners($heap_graph(S),HOBJECT n_target) = 1
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_selector] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("changed")) /\ ppropertyempty.NAME = $ptascii("value")
~$property_empty_capture(S,ppropertyempty)
$owning_review_output(S.EVENTS) = $ptascii("I;G;")
'''.strip().splitlines()

LITERAL_FRONT = r'''
~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~((HOBJECT n_target) <- S.ALLOCATIONS)
$weakref_get(S,n_wrapper) = PNULL
$heap_owners($heap_graph(S),HOBJECT n_target) = 0
$owning_review_output(S.EVENTS) = $ptascii("EXPIRED;I;G;")
'''.strip().splitlines()

LIFETIME = r'''
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
$property_empty_rv_ready(S,ppropertyempty) /\ $property_empty_truth(S,POBJECT n_wrapper) = eps
$property_empty_rv_kind(S,WEAKREFERENCE (n_target)) /\ ~$property_empty_rv_kind(S,WEAKREFERENCE eps)
~$property_empty_rv_ready(S[.OBJECTS[n_wrapper] = WEAKREFERENCE eps],ppropertyempty)
$weakref_at(S[.OBJECTS[n_wrapper] = WEAKREFERENCE eps],n_wrapper) = (WEAKREFERENCE eps)
~$weakref_state_valid(S[.OBJECTS[n_wrapper] = WEAKREFERENCE (n_wrapper)])
~$call_descriptors_valid(S[.OBJECTS[n_watch] = WEAKREFERENCE (n_target)])
~$property_empty_rv_ready(S[.SOURCES = eps],ppropertyempty)
~$property_empty_rv_ready(S,ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)])
~$property_empty_rv_ready(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_wrapper)],ppropertyempty)
~$property_empty_rv_ready(S[.RESULT = KNOWN (POBJECT (|S.OBJECTS|))],ppropertyempty)
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_wrapper) = 0 /\ $heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
~$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv[.OWNER = 1])
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_releasing = S_one[.COMPLETION = NORMAL]
S_releasing.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_cached_raw.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_wrapper)]
pdestructionoperation.SOURCE = PROPERTY_EMPTY_RESULT ppropertyempty true
pdestructionoperation.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation.PENDING = eps
$heap_owners($heap_graph(S_releasing),HOBJECT n_wrapper) = 1
$weakref_get(S_releasing,n_watch) = POBJECT n_wrapper
$weakmap_key_maps(S_releasing,S_releasing.ALLOCATIONS,n_wrapper) = eps
PhpStep: S_releasing ~> S_retired_raw
~((HOBJECT n_wrapper) <- S_retired_raw.ALLOCATIONS)
S_retired_raw.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)
$weakref_get(S_retired_raw,n_watch) = PNULL
$weakref_find(S_retired_raw,S_retired_raw.ALLOCATIONS,n_target) = eps
S_retired = $owning_review_after(S_releasing,S_retired_raw)
$property_empty_guard(S_retired,n_receiver,ppropertyempty.NAME)
S_retired.STORE[n_destination] = DEFINED (PINT 42)
S_ready_found = $wr_quiet_seek(S_retired,1000)
S_ready_found.COMPLETION = NORMAL \/ S_ready_found.COMPLETION = BUDGET
S_ready = S_ready_found[.COMPLETION = NORMAL]
S_ready.TODO = S_cached_raw.TODO /\ S_ready.RESULT = KNOWN (PBOOL false)
~((HOBJECT n_wrapper) <- S_ready.ALLOCATIONS) /\ $weakref_get(S_ready,n_watch) = PNULL
$heap_owners($heap_graph(S_ready),HOBJECT n_receiver) = 1
$property_empty_guard(S_ready,n_receiver,ppropertyempty.NAME)
PhpStep: S_ready ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL false)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 0
~$property_empty_guard(S_release_raw,n_receiver,ppropertyempty.NAME)
S_receiver_found = $owning_review_seek($owning_review_after(S_ready,S_release_raw),OW_DTOR n_receiver,1000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
pdestructionoperation_receiver.SOURCE = PROPERTY_EMPTY_RV ppropertyemptyrv
pdestructionoperation_receiver.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation_receiver.PENDING = eps
~((HOBJECT n_wrapper) <- S_receiver.ALLOCATIONS) /\ $weakref_get(S_receiver,n_watch) = PNULL
S_receiver.STORE[n_destination] = DEFINED (PINT 42)
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_wrapper) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_target) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_watch) <- S_done.ALLOCATIONS)
S_done.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL
$weakref_state_valid(S_done) /\ $call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S_releasing,4096) = S_done /\ $drive_steps(S_retired,4096) = S_done
$drive_steps(S_ready,4096) = S_done
$drive_steps(S_receiver,4096) = S_done
'''.strip().splitlines()

NORMAL = r'''
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_wrapper] = WEAKREFERENCE eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
$property_magic_cv_empty_source(S_retired,ppropertyempty.SITE,ppropertyempty.LINE) /\ $property_magic_cv_weakreference(S_retired.OBJECTS[n_wrapper]) /\ ~$property_magic_cv_result_supported(S_retired,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_wrapper))
(HOBJECT n_target) <- S_receiver.ALLOCATIONS
S_done.STORE[n_destination] = DEFINED (PBOOL false) /\ S_done.STORE[n_selector] = DEFINED pvalue_changed
$owning_review_output(S_done.EVENTS) = $ptascii("I;G;RECEIVER;WR_GONE;TARGET_LIVE;FALSE;CAPTURE;DONE;")
'''.strip().splitlines()

THROW = r'''
S_catch_found = $owning_review_seek(S_receiver,OW_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
$call_task_valid(S_catch,CATCH_BIND porigin_try n_index n_error)
$throwable_live(S_catch,n_error) /\ $throwable_field(S_catch,n_error,"previous") = PNULL
$string_bytes($throwable_field(S_catch,n_error,"message")) = ($ptascii("receiver"))
$throwable_field(S_catch,n_error,"line") = PINT 6
S_catch.STORE[n_destination] = DEFINED (PINT 42)
~((HOBJECT n_wrapper) <- S_catch.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_catch.ALLOCATIONS)
$owning_review_output(S_catch.EVENTS) = $ptascii("EXPIRED;I;G;RECEIVER;WR_GONE;")
PhpStep: S_catch ~> S_bound_raw
S_bound = $owning_review_after(S_catch,S_bound_raw)
$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)
S_bound.STORE[n_failure] = DEFINED (POBJECT n_error)
S_done.STORE[n_destination] = DEFINED (PINT 42) /\ $lookup(S_done.ENV,$ptascii("failure")) = eps
$owning_review_output(S_done.EVENTS) = $ptascii("EXPIRED;I;G;RECEIVER;WR_GONE;CAUGHT;KEEP;CAPTURE;DONE;")
$drive_steps(S_catch,4096) = S_done /\ $drive_steps(S_bound,4096) = S_done
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_wrapper)')
CASES = {
    'weakreference-cv-empty-live-wrapper-before-receiver': {
        'source': ROWS[0]['source'], 'stage': STAGE,
        'checks': FRONT + CV_FRONT + LIFETIME + NORMAL,
    },
    'weakreference-literal-empty-expired-wrapper-receiver-throw': {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': FRONT + LITERAL_FRONT + LIFETIME + THROW,
    },
}


def render(case, fixture, filename):
    text, assertions = owning.render(case, fixture, filename)
    return PREFIX + text, assertions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(owning.__file__), owning.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=render)
