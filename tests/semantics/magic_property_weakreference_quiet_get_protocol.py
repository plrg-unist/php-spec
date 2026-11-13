#!/usr/bin/env python3
"""Check initialized WeakReference quiet Get transfer and nonowning target history."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_weakreference_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

COMMON = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.RESULT = KNOWN (POBJECT n_wrapper)
S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertycoalesce.OBJECT
S.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)
S.OBJECTS[n_target] = STDINSTANCE
$(n_target < n_wrapper) /\ (HOBJECT n_wrapper) <- S.ALLOCATIONS
~$instance_storage_freeing(S,n_wrapper)
$weakref_at(S,n_wrapper) = (WEAKREFERENCE (n_target))
$property_magic_cv_weakreference(S.OBJECTS[n_wrapper])
~$property_magic_cv_weakreference(WEAKREFERENCE eps) /\ ~$property_magic_cv_weakreference(WEAKMAP eps)
~$eager_property_class_valid(S,S.OBJECTS[n_wrapper]) /\ $enum_case_object(S,n_wrapper) = eps
$property_get_method(S,n_receiver) = (pmethoddesc)
pfunction = pmethoddesc.FUNCTION
ppropertycoalesce.GET = (pfunction.ORIGIN) /\ ~pfunction.SIGNATURE.BYREF
pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
$property_coalesce_valid(S,ppropertycoalesce) /\ $call_task_valid(S,PROPERTY_COALESCE_RESULT ppropertycoalesce true)
$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_wrapper] = WEAKREFERENCE eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
$weakref_at(S[.OBJECTS[n_wrapper] = WEAKREFERENCE eps],n_wrapper) = (WEAKREFERENCE eps)
~$weakref_state_valid(S[.OBJECTS[n_wrapper] = WEAKREFERENCE eps])
~$weakref_state_valid(S[.OBJECTS[n_wrapper] = WEAKREFERENCE (n_wrapper)])
~$property_magic_cv_result_supported(S[.OBJECTS[n_wrapper] = REALCLOSURE pfunction.ORIGIN eps eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_wrapper)],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))
~$property_coalesce_valid(S[.SOURCES = eps],ppropertycoalesce)
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
$lookup(S.ENV,$ptascii("held")) = (n_held)
S.STORE[n_reader] = DEFINED PNULL /\ S.STORE[n_held] = DEFINED PNULL
S.STORE[n_selector] = DEFINED pvalue_selector
$string_bytes(pvalue_selector) = ($ptascii("changed"))
~$property_magic_name_capture(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,ppropertycoalesce.NAME)
$lookup(S.ENV,$ptascii("wrapperWeak")) = (n_observer_cell)
S.STORE[n_observer_cell] = DEFINED (POBJECT n_observer)
S.OBJECTS[n_observer] = WEAKREFERENCE (n_wrapper)
$weakref_get(S,n_observer) = POBJECT n_wrapper
~$call_descriptors_valid(S[.OBJECTS[n_observer] = WEAKREFERENCE (n_target)])
$heap_unique([HOBJECT n_receiver,HOBJECT n_wrapper,HOBJECT n_target,HOBJECT n_observer])
$node_children(S,HOBJECT n_wrapper) = eps /\ $node_children(S,HOBJECT n_observer) = eps
$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_wrapper) = 1
S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$weakref_state_valid(S) /\ $call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
PhpStep: S ~> S_value
S_value.RESULT = S.RESULT /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE
S_value.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)
$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0 /\ $heap_owners($heap_graph(S_value),HOBJECT n_wrapper) = 1
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_value.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]
pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true
pdestructionoperation.VALUE = KNOWN (POBJECT n_wrapper) /\ pdestructionoperation.PENDING = eps
$heap_owners($heap_graph(S_one),HOBJECT n_wrapper) = 1
S_one.OBJECTS[n_wrapper] = S.OBJECTS[n_wrapper] /\ S_one.EVENTS = S.EVENTS
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_wrapper) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_target) <- S_done.ALLOCATIONS)
S_done.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)
$weakref_get(S_done,n_observer) = PNULL /\ $lookup(S_done.ENV,$ptascii("answer")) = eps
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_selector
$weakref_state_valid(S_done) /\ $call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
'''.strip().splitlines()

BINARY = COMMON + r'''
ppropertycoalesce.PROPERTY = eps
$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_source(S[.SOURCES = eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,$(ppropertycoalesce.LINE + 1))
S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*
~((HOBJECT n_target) <- S.ALLOCATIONS) /\ $heap_owners($heap_graph(S),HOBJECT n_target) = 0
$weakref_get(S,n_wrapper) = PNULL
S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("DEAD_TARGET;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("RETIRED;"),OUTPUT $ptascii("DONE;")]
'''.strip().splitlines()

ASSIGN = COMMON + r'''
ppropertycoalesce.PROPERTY = (porigin_property)
$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S[.SOURCES = eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,$(ppropertycoalesce.LINE + 1))
$property_coalesce_assign_source(S,porigin_parent) /\ $property_coalesce_assign_base(S,porigin_parent,pbase)
$task_nodes(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) = eps
S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*
(HOBJECT n_target) <- S.ALLOCATIONS /\ $heap_owners($heap_graph(S),HOBJECT n_target) = 1
$weakref_get(S,n_wrapper) = POBJECT n_target
S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("LIVE_TARGET;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("RETIRED;"),OUTPUT $ptascii("FRESH;"),OUTPUT $ptascii("DONE;")]
'''.strip().splitlines()

CASES = {
    'weakreference-cv-coalesce-expired-target-wrapper': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*',
        'checks': BINARY,
    },
    'weakreference-cv-coalesce-assignment-live-target-wrapper': {
        'source': ROWS[1]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
        'checks': ASSIGN,
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), runner_flags=('--sl',))
