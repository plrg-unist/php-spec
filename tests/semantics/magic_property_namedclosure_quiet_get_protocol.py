#!/usr/bin/env python3
"""Check original named FCC Get transfer with separately owned function statics."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_namedclosure_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.RESULT = KNOWN (POBJECT n_closure)
S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertycoalesce.OBJECT
S.OBJECTS[n_closure] = NAMEDCLOSURE porigin_named
(HOBJECT n_closure) <- S.ALLOCATIONS /\ ~$instance_storage_freeing(S,n_closure)
$function_at(S.FUNCTIONS,porigin_named) = (pfunction_named)
$origin_node(S.SOURCES,porigin_named) = (NStmtFunction phpType14 phpType4_ref phpType11 phpType16 phpType18 (SEQUENCE statement*) metadata_named)
~$function_generator(S,pfunction_named)
$closure_live_object_valid(S,n_closure)
$closure_scope_at(S.CLOSURESCOPES,n_closure) = eps /\ $closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps
$closure_cache_at(S.CLOSURECACHES,n_closure) = (pclosurecache)
pclosurecache = {OBJECT n_closure,FUNCTION porigin_named,SOURCE eps,SCOPE (BIND_UNSCOPED),CACHE (CACHE_SHARED)}
$node_children(S,HOBJECT n_closure) = eps /\ $destruction_child_jobs(S,HOBJECT n_closure) = eps
$heap_owners($heap_graph(S),HOBJECT n_closure) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
S.STATICS = [pstaticcell]
n_counter = pstaticcell.CELL
S.STORE[n_counter] = DEFINED (PINT 1)
(HCELL n_counter) <- S.ALLOCATIONS /\ $static_roots(S.STATICS) = [HCELL n_counter]
$heap_owners($heap_graph(S),HCELL n_counter) = 1
$property_get_method(S,n_receiver) = (pmethoddesc)
ppropertycoalesce.GET = (pmethoddesc.FUNCTION.ORIGIN)
pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
$property_coalesce_valid(S,ppropertycoalesce) /\ $call_task_valid(S,PROPERTY_COALESCE_RESULT ppropertycoalesce true)
$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("held")) = (n_held)
S.STORE[n_reader] = DEFINED PNULL /\ S.STORE[n_held] = DEFINED PNULL
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_selector] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("changed"))
~$property_magic_name_capture(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,ppropertycoalesce.NAME)
$lookup(S.ENV,$ptascii("watch")) = (n_watch_cell)
S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)
S.OBJECTS[n_watch] = WEAKREFERENCE (n_closure)
$weakref_get(S,n_watch) = POBJECT n_closure
$heap_unique([HOBJECT n_receiver,HOBJECT n_closure,HOBJECT n_watch,HCELL n_counter])
S.EVENTS = [OUTPUT $ptascii("WARM;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$closure_state_valid(S) /\ $closure_cache_records_valid(S) /\ $weakref_state_valid(S)
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

LIFETIME = r'''
$property_magic_cv_namedclosure(S,n_closure)
~$property_magic_cv_realclosure(S,n_closure) /\ ~$property_magic_cv_arrow(S,n_closure)
$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S.RESULT)
S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]
~$property_magic_cv_result_supported(S_unallocated,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))
~$property_coalesce_valid(S[.SOURCES = eps],ppropertycoalesce)
PhpStep: S ~> S_value
S_value.RESULT = S.RESULT /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE
S_value.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_value.CLOSURECACHES = S.CLOSURECACHES
S_value.STATICS = S.STATICS /\ S_value.STORE[n_counter] = DEFINED (PINT 1)
$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0 /\ $heap_owners($heap_graph(S_value),HOBJECT n_closure) = 1
$heap_owners($heap_graph(S_value),HCELL n_counter) = 1 /\ $node_children(S_value,HOBJECT n_closure) = eps
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_value.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]
pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true
pdestructionoperation.VALUE = KNOWN (POBJECT n_closure) /\ pdestructionoperation.PENDING = eps
$heap_owners($heap_graph(S_one),HOBJECT n_closure) = 1 /\ $heap_owners($heap_graph(S_one),HCELL n_counter) = 1
S_one.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_one.EVENTS = S.EVENTS /\ S_one.STATICS = S.STATICS
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_closure) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_watch) <- S_done.ALLOCATIONS)
S_done.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_done.CLOSURECACHES = S.CLOSURECACHES
S_done.STORE[n_counter] = DEFINED (PINT 3)
$weakref_get(S_done,n_watch) = PNULL /\ $lookup(S_done.ENV,$ptascii("answer")) = eps
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_changed
$closure_state_valid(S_done) /\ $closure_cache_records_valid(S_done) /\ $call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("RESULT;"),OUTPUT $ptascii("STATIC;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("RETIRED;"),OUTPUT $ptascii("DONE;")]
'''.strip().splitlines()

CASES = {
    ROWS[0]['id']: {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*',
        'checks': FRONT + LIFETIME + [
            'ppropertycoalesce.PROPERTY = eps',
            '$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
            '~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
            'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*',
        ],
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
        'checks': FRONT + LIFETIME + [
            'ppropertycoalesce.PROPERTY = (porigin_property)',
            '$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
            '~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
            r'$property_coalesce_assign_source(S,porigin_parent) /\ $property_coalesce_assign_base(S,porigin_parent,pbase)',
            'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), runner_flags=('--sl',))
