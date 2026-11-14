#!/usr/bin/env python3
"""Check original named FCC retirement without owning function static storage."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning
import magic_property_realclosure_quiet_get_review_protocol as literal

CATALOGUE = Path(__file__).with_name('magic_property_namedclosure_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.ORIGIN = (ppropertyempty.SITE) /\ S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_closure)
S.OBJECTS[n_closure] = NAMEDCLOSURE porigin_named
(HOBJECT n_closure) <- S.ALLOCATIONS
~$instance_storage_freeing(S,n_closure)
$function_at(S.FUNCTIONS,porigin_named) = (pfunction_named)
$origin_node(S.SOURCES,porigin_named) = (NStmtFunction phpType14 phpType4_ref phpType11 phpType16 phpType18 (SEQUENCE statement*) metadata_named)
porigin_named = PORIGIN n_unit_named pcpath_named
S.SOURCES = [pcunit]
pcunit.ID = n_unit_named
S.CLOSURETEMPLATES = eps
~$function_generator(S,pfunction_named)
$closure_cache_named_source(S,porigin_named) = (pfunction_named)
$callable_at(S.CALLABLES,$ptlc(pfunction_named.NAME)) = (porigin_named)
$closure_scope_at(S.CLOSURESCOPES,n_closure) = eps /\ $closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps
~$internal_closure_object(S,n_closure)
$closure_live_object_valid(S,n_closure)
$closure_cache_at(S.CLOSURECACHES,n_closure) = (pclosurecache)
S.CLOSURECACHES = [pclosurecache]
pclosurecache.OBJECT = n_closure /\ pclosurecache.FUNCTION = porigin_named /\ pclosurecache.SOURCE = eps
pclosurecache.SCOPE = (BIND_UNSCOPED) /\ pclosurecache.CACHE = (CACHE_SHARED)
$node_children(S,HOBJECT n_closure) = eps /\ $destruction_child_jobs(S,HOBJECT n_closure) = eps
S.STATICS = [pstaticcell]
n_counter = pstaticcell.CELL
(HCELL n_counter) <- S.ALLOCATIONS /\ n_counter <- S.REFCELLS
S.STORE[n_counter] = DEFINED (PINT 1)
$static_roots(S.STATICS) = [HCELL n_counter]
$heap_owners($heap_graph(S),HCELL n_counter) = 1
$heap_owners($heap_graph(S),HOBJECT n_closure) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
$lookup(S.ENV,$ptascii("watch")) = (n_watch_cell)
S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)
S.OBJECTS[n_watch] = WEAKREFERENCE (n_closure)
$weakref_get(S,n_watch) = POBJECT n_closure
$lookup(S.ENV,$ptascii("readerWeak")) = (n_reader_weak_cell)
S.STORE[n_reader_weak_cell] = DEFINED (POBJECT n_reader_weak)
S.OBJECTS[n_reader_weak] = WEAKREFERENCE (n_receiver)
$weakref_get(S,n_reader_weak) = POBJECT n_receiver
$heap_unique([HOBJECT n_receiver,HOBJECT n_closure,HOBJECT n_watch,HOBJECT n_reader_weak,HCELL n_counter])
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("held")) = (n_held)
S.STORE[n_reader] = DEFINED PNULL /\ S.STORE[n_held] = DEFINED PNULL
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_selector] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("changed")) /\ ppropertyempty.NAME = $ptascii("value")
$lookup(S.ENV,$ptascii("destination")) = (n_destination)
S.STORE[n_destination] = DEFINED (PINT 42)
$property_get_method(S,n_receiver) = (pmethoddesc)
pmethoddesc.FUNCTION.ORIGIN = ppropertyempty.GET
pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)
$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)
$owning_review_output(S.EVENTS) = $ptascii("WARM;I;G;")
$closure_state_valid(S) /\ $closure_cache_records_valid(S) /\ $weakref_state_valid(S)
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

AUTHORITY = r'''
$property_magic_cv_namedclosure(S,n_closure)
~$property_magic_cv_realclosure(S,n_closure) /\ ~$property_magic_cv_arrow(S,n_closure)
~$property_magic_cv_namedclosure(S,|S.OBJECTS|)
~$property_magic_cv_namedclosure(S[.SOURCES = eps],n_closure)
~$property_magic_cv_namedclosure(S[.FUNCTIONS = eps],n_closure)
~$property_magic_cv_namedclosure(S[.CALLABLES = eps],n_closure)
~$property_magic_cv_namedclosure(S[.OBJECTS[n_closure] = REALCLOSURE porigin_named eps eps],n_closure)
~$property_magic_cv_namedclosure(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_named (NAMEDCLOSURE porigin_named)],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSURESCOPES = [{OBJECT n_closure,LEXICAL pmethoddesc.OWNER,CALLED pmethoddesc.OWNER,RECEIVER eps,CREATION eps}]],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSUREBINDINGS = [{OBJECT n_closure,SITE ppropertyempty.SITE,SOURCE n_receiver,LEXICAL eps,CALLED eps,RECEIVER eps}]],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSURECACHES = eps],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSURECACHES = [pclosurecache,pclosurecache]],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSURECACHES = [pclosurecache[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]]],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSURECACHES = [pclosurecache[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]],n_closure)
~$property_magic_cv_namedclosure(S[.CLOSURECACHES = [pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]]],n_closure)
S_generator = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_named,NStmtFunction phpType14 phpType4_ref phpType11 phpType16 phpType18 (SEQUENCE ([NStmtExpression (NExprYield ABSENT ABSENT metadata_named) metadata_named])) metadata_named)]]]
$function_generator(S_generator,pfunction_named) /\ ~$property_magic_cv_namedclosure(S_generator,n_closure)
n_clone = |S.OBJECTS|
S_clone = $clone_object(S,n_closure)
S_clone.RESULT = KNOWN (POBJECT n_clone) /\ S_clone.OBJECTS[n_clone] = NAMEDCLOSURE porigin_named
$closure_cache_at(S_clone.CLOSURECACHES,n_clone) = (pclosurecache_clone)
pclosurecache_clone.SOURCE = (n_closure) /\ pclosurecache_clone.CACHE = (CACHE_SHARED)
$closure_live_object_valid(S_clone,n_clone) /\ $closure_cache_records_valid(S_clone)
$property_magic_cv_namedclosure(S_clone,n_clone)
$property_empty_rv_kind(S_clone,S_clone.OBJECTS[n_clone]) /\ $property_empty_rv_ready(S_clone,ppropertyempty)
$property_empty_rv_kind(S,S.OBJECTS[n_closure])
~$property_empty_rv_kind(S[.RESULT = KNOWN PNULL],S.OBJECTS[n_closure])
'''.strip().splitlines()

LIFETIME = r'''
$property_empty_rv_ready(S,ppropertyempty)
~$property_empty_rv_ready(S[.SOURCES = eps],ppropertyempty)
~$property_empty_rv_ready(S,ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)])
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_closure) = 0 /\ $heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_releasing = S_one[.COMPLETION = NORMAL]
S_releasing.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_cached_raw.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_closure)]
PhpStep: S_releasing ~> S_retired_raw
~((HOBJECT n_closure) <- S_retired_raw.ALLOCATIONS)
S_retired_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_cached_raw.TODO
pdestructionrelease_child.JOBS = [DESTRUCTION_HANDLE n_closure]
S_retired_raw.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_retired_raw.CLOSURECACHES = S.CLOSURECACHES
$weakref_get(S_retired_raw,n_watch) = PNULL /\ $weakref_get(S_retired_raw,n_reader_weak) = POBJECT n_receiver
S_retired_raw.STATICS = S.STATICS /\ S_retired_raw.STORE[n_counter] = DEFINED (PINT 1)
(HCELL n_counter) <- S_retired_raw.ALLOCATIONS /\ $heap_owners($heap_graph(S_retired_raw),HCELL n_counter) = 1
S_retired = $owning_review_after(S_releasing,S_retired_raw)
S_ready_found = $rc_review_seek(S_retired,1000)
S_ready_found.COMPLETION = NORMAL \/ S_ready_found.COMPLETION = BUDGET
S_ready = S_ready_found[.COMPLETION = NORMAL]
S_ready.TODO = S_cached_raw.TODO /\ S_ready.RESULT = KNOWN (PBOOL false)
~((HOBJECT n_closure) <- S_ready.ALLOCATIONS)
S_ready.STATICS = S.STATICS /\ S_ready.STORE[n_counter] = DEFINED (PINT 1)
S_ready.STORE[n_destination] = DEFINED (PINT 42)
$weakref_get(S_ready,n_watch) = PNULL /\ $weakref_get(S_ready,n_reader_weak) = POBJECT n_receiver
$property_empty_rv_valid(S_ready,ppropertyemptyrv) /\ $property_empty_guard(S_ready,n_receiver,ppropertyempty.NAME)
$owning_review_output(S_ready.EVENTS) = $ptascii("WARM;I;G;")
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
S_receiver.STORE[n_destination] = DEFINED (PINT 42) /\ S_receiver.STORE[n_counter] = DEFINED (PINT 1)
$weakref_get(S_receiver,n_watch) = PNULL /\ $weakref_get(S_receiver,n_reader_weak) = POBJECT n_receiver
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
'''.strip().splitlines()

THROW = r'''
S_catch_found = $owning_review_seek(S_receiver,OW_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
$call_task_valid(S_catch,CATCH_BIND porigin_try n_index n_error)
$throwable_field(S_catch,n_error,"previous") = PNULL
$string_bytes($throwable_field(S_catch,n_error,"message")) = ($ptascii("receiver"))
$throwable_field(S_catch,n_error,"line") = PINT 7
S_catch.STORE[n_destination] = DEFINED (PINT 42) /\ S_catch.STORE[n_counter] = DEFINED (PINT 1)
~((HOBJECT n_receiver) <- S_catch.ALLOCATIONS) /\ $weakref_get(S_catch,n_reader_weak) = PNULL
$weakref_get(S_catch,n_watch) = PNULL
$owning_review_output(S_catch.EVENTS) = $ptascii("WARM;I;G;RECEIVER;WRAPPER_GONE;")
'''.strip().splitlines()

DONE = r'''
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_closure) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_watch) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_reader_weak) <- S_done.ALLOCATIONS)
S_done.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_done.CLOSURECACHES = S.CLOSURECACHES
S_done.STORE[n_counter] = DEFINED (PINT 2)
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL
S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\ S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps
$closure_state_valid(S_done) /\ $closure_cache_records_valid(S_done) /\ $weakref_state_valid(S_done)
$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S_retired,4096) = S_done
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_closure)')
CASES = {
    ROWS[0]['id']: {
        'source': ROWS[0]['source'], 'stage': STAGE,
        'checks': FRONT + AUTHORITY + [
            '$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
            '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
        ] + LIFETIME + DONE + [
            'S_done.STORE[n_destination] = DEFINED (PBOOL false)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("WARM;I;G;RECEIVER;WRAPPER_GONE;FALSE;CAPTURE;RECEIVER_GONE;STATIC;DONE;")',
        ],
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': FRONT + AUTHORITY + [
            '~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
        ] + LIFETIME + THROW + DONE + [
            'S_done.STORE[n_destination] = DEFINED (PINT 42)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("WARM;I;G;RECEIVER;WRAPPER_GONE;CAUGHT;KEEP;CAPTURE;RECEIVER_GONE;STATIC;DONE;")',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(owning.__file__), owning.CATALOGUE,
                  Path(literal.__file__), literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=literal.render)
