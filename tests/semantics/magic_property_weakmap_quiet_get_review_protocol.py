#!/usr/bin/env python3
"""Check CV Empty WeakMap value disposal before the saved receiver release."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_empty_weakmap_rv_protocol as weakmap
import magic_property_owning_quiet_empty_get_review_protocol as owning

CATALOGUE = Path(__file__).with_name('magic_property_weakmap_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

COMMON = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertyempty.OBJECT
$property_get_method(S,n_receiver) = (pmethoddesc)
pfunction = pmethoddesc.FUNCTION
ppropertyempty.GET = pfunction.ORIGIN /\ ~pfunction.SIGNATURE.BYREF
pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)
$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_coalesce_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_coalesce_assign_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
S.OBJECTS[n_map] = WEAKMAP (pweakmapentry)
n_key = pweakmapentry.KEY
pweakmapentry.VALUE = POBJECT n_value
S.OBJECTS[n_key] = STDINSTANCE
S.OBJECTS[n_value] = INSTANCE porigin_value
$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_key)
pweakmapentry.BEFORE = (n_weak)
$heap_unique([HOBJECT n_receiver,HOBJECT n_map,HOBJECT n_key,HOBJECT n_value,HOBJECT n_weak])
$weakref_get(S,n_weak) = POBJECT n_key
$node_children(S,HOBJECT n_map) = [HOBJECT n_value] /\ $node_children(S,HOBJECT n_value) = eps
$weakmap_key_maps(S,S.ALLOCATIONS,n_key) = [n_map]
$heap_owners($heap_graph(S),HOBJECT n_map) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_value) = 1
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2 /\ $heap_owners($heap_graph(S),HOBJECT n_key) = 1
~$eager_property_class_valid(S,S.OBJECTS[n_map])
$property_empty_rv_ready(S,ppropertyempty) /\ $property_empty_truth(S,POBJECT n_map) = eps
~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_map)],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))
~$property_magic_cv_result_supported(S[.OBJECTS[n_map] = WEAKMAPENTRIES eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_map] = REALCLOSURE pfunction.ORIGIN eps eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
$property_magic_cv_result_supported(S[.OBJECTS[n_map] = WEAKMAP eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_empty_rv_ready(S[.SOURCES = eps],ppropertyempty)
~$property_empty_rv_ready(S,ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)])
~$property_empty_rv_ready(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_map)],ppropertyempty)
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
S.STORE[n_reader] = DEFINED (POBJECT n_receiver)
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_selector] = DEFINED pvalue_selector
$string_bytes(pvalue_selector) = ($ptascii("value")) /\ ppropertyempty.NAME = $ptascii("value")
$lookup(S.ENV,$ptascii("destination")) = (n_destination)
S.STORE[n_destination] = DEFINED (PINT 42)
$property_empty_capture(S,ppropertyempty) /\ $property_empty_guard(S,n_receiver,ppropertyempty.NAME)
~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)
S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$wm_guard(S)
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_map) = 0 /\ $heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 2
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
~$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv[.OWNER = 1])
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_value_found = $wm_seek(S_one[.COMPLETION = NORMAL],WM_DTOR n_value,2000)
S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET
S_value = S_value_found[.COMPLETION = NORMAL]
S_value.OBJECTS[n_map] = WEAKMAP eps
(HOBJECT n_map) <- S_value.ALLOCATIONS /\ $instance_storage_freeing(S_value,n_map)
$instance_storage_for(S_value,n_map) = (pinstancestorage)
pinstancestorage.OBJECT = n_map /\ pinstancestorage.SLOTS = eps /\ pinstancestorage.NEXT = 0
$instance_storage_basic(S_value,pinstancestorage)
$weakmap_key_maps(S_value,S_value.ALLOCATIONS,n_key) = eps
$heap_owners($heap_graph(S_value),HOBJECT n_map) = 1 /\ $heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 2
$property_empty_guard(S_value,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S_value,n_receiver,ppropertyempty.NAME)
$wm_output(S_value.EVENTS) = $ptascii("I;G;") /\ $wm_guard(S_value)
S_key_found = $wm_seek(S_value,WM_OUTPUT $ptascii("I;G;VALUE;KEY_GONE;"),2000)
S_key_found.COMPLETION = NORMAL \/ S_key_found.COMPLETION = BUDGET
S_key = S_key_found[.COMPLETION = NORMAL]
(HOBJECT n_map) <- S_key.ALLOCATIONS /\ ~((HOBJECT n_key) <- S_key.ALLOCATIONS)
S_key.OBJECTS[n_weak] = WEAKREFERENCE (n_key) /\ $weakref_get(S_key,n_weak) = PNULL
S_key.STORE[n_reader] = DEFINED PNULL
S_key.STORE[n_selector] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("changed"))
$heap_owners($heap_graph(S_key),HOBJECT n_receiver) = 1
$property_empty_guard(S_key,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S_key,n_receiver,ppropertyempty.NAME)
~$property_empty_capture(S_key,ppropertyempty) /\ $wm_guard(S_key)
S_receiver_found = $wm_seek(S_key,WM_DTOR n_receiver,2000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
~((HOBJECT n_map) <- S_receiver.ALLOCATIONS) /\ ~((HOBJECT n_value) <- S_receiver.ALLOCATIONS) /\ ~((HOBJECT n_key) <- S_receiver.ALLOCATIONS)
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
S_receiver.STORE[n_reader] = DEFINED PNULL /\ S_receiver.STORE[n_destination] = DEFINED (PINT 42)
$wm_output(S_receiver.EVENTS) = $ptascii("I;G;VALUE;KEY_GONE;")
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_map) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_value) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_key) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_changed
$wm_guard(S_done)
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S_value,4096) = S_done
$drive_steps(S_key,4096) = S_done
$drive_steps(S_receiver,4096) = S_done
'''.strip().splitlines()

NORMAL = COMMON + r'''
pdestructionoperation_receiver.SOURCE = PROPERTY_EMPTY_RV ppropertyemptyrv
pdestructionoperation_receiver.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation_receiver.PENDING = eps
S_done.STORE[n_destination] = DEFINED (PBOOL false)
$wm_output(S_done.EVENTS) = $ptascii("I;G;VALUE;KEY_GONE;RECEIVER;FALSE;CAPTURE;DONE;")
'''.strip().splitlines()

THROW = COMMON + r'''
S_throw_found = $wm_seek(S_key,WM_THROW,2000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
$throwable_live(S_throw,n_error)
$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("map-value"))
$throwable_field(S_throw,n_error,"line") = PINT 3 /\ $throwable_field(S_throw,n_error,"previous") = PNULL
~((HOBJECT n_map) <- S_throw.ALLOCATIONS) /\ ~((HOBJECT n_value) <- S_throw.ALLOCATIONS)
$heap_owners($heap_graph(S_throw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_throw,ppropertyemptyrv) /\ $property_empty_guard(S_throw,n_receiver,ppropertyempty.NAME)
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.EVENTS = S_throw.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 0
~$property_empty_guard(S_release_raw,n_receiver,ppropertyempty.NAME)
pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_error
pdestructionoperation_receiver.PENDING = (n_error) /\ pdestructionoperation_receiver.VALUE = KNOWN PNULL
S_catch_found = $wm_seek(S_receiver,WM_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
$call_task_valid(S_catch,CATCH_BIND porigin_try n_index n_error)
$throwable_live(S_catch,n_error) /\ $throwable_field(S_catch,n_error,"previous") = PNULL
S_catch.STORE[n_destination] = DEFINED (PINT 42)
$wm_output(S_catch.EVENTS) = $ptascii("I;G;VALUE;KEY_GONE;RECEIVER;")
PhpStep: S_catch ~> S_bound_raw
S_bound = $owning_review_after(S_catch,S_bound_raw)
$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)
S_bound.STORE[n_failure] = DEFINED (POBJECT n_error)
S_done.STORE[n_destination] = DEFINED (PINT 42) /\ $lookup(S_done.ENV,$ptascii("failure")) = eps
$wm_output(S_done.EVENTS) = $ptascii("I;G;VALUE;KEY_GONE;RECEIVER;CAUGHT;KEEP;CAPTURE;DONE;")
$drive_steps(S_throw,4096) = S_done
$drive_steps(S_bound,4096) = S_done
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_map)')
CASES = {
    'weakmap-cv-empty-pin-value-key-and-saved-name': {
        'source': ROWS[0]['source'], 'stage': STAGE, 'checks': NORMAL,
    },
    'weakmap-cv-empty-value-throw-receiver-and-catch': {
        'source': ROWS[1]['source'], 'stage': STAGE, 'checks': THROW,
    },
}


def render(case, fixture, filename):
    text, assertions = owning.render(case, fixture, filename)
    return weakmap.PREFIX + text, assertions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(weakmap.__file__), Path(owning.__file__), owning.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=render)
