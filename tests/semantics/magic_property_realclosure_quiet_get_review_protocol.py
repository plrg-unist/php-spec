#!/usr/bin/env python3
"""Check source Closure admission, capture disposal and saved-receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning

CATALOGUE = Path(__file__).with_name('magic_property_realclosure_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PREFIX = r'''
dec $rc_review_resume(pstate) : bool
def $rc_review_resume(S) = true
  -- if S.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $rc_review_resume(S) = false -- otherwise
dec $rc_review_seek(pstate,nat) : pstate
def $rc_review_seek(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $rc_review_seek(S,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $rc_review_resume(S) \/ n = 0
def $rc_review_seek(S,n) = $rc_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$rc_review_resume(S) /\ $(n > 0)

;; Counterfeit only the selected occurrence; genuine source fronts stay intact.
dec $rc_review_occurrence(pcoccurrence*,pcpath,pcnode) : pcoccurrence*
def $rc_review_occurrence(eps,pcpath,pcnode) = eps
def $rc_review_occurrence((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: $rc_review_occurrence(pcoccurrence*,pcpath,pcnode)
def $rc_review_occurrence((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $rc_review_occurrence(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_other =/= pcpath
'''

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.ORIGIN = (ppropertyempty.SITE) /\ S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_closure)
S.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps
S.OBJECTS[n_payload] = INSTANCE porigin_payload
(HOBJECT n_closure) <- S.ALLOCATIONS /\ (HOBJECT n_payload) <- S.ALLOCATIONS
~$instance_storage_freeing(S,n_closure)
$function_at(S.CLOSURETEMPLATES,porigin_closure) = (pfunction_closure)
S.CLOSURETEMPLATES = [pfunction_closure]
$origin_node(S.SOURCES,porigin_closure) = (NExprClosure phpType14 phpType4_static phpType4_ref phpType16 phpType21 phpType18 phpType23 metadata_closure)
porigin_closure = PORIGIN n_unit_closure pcpath_closure
S.SOURCES = [pcunit]
pcunit.ID = n_unit_closure
$closure_template_origins_valid(S,[pfunction_closure])
~$function_generator(S,pfunction_closure)
$closure_source_class(S,porigin_closure) = eps
$closure_scope_at(S.CLOSURESCOPES,n_closure) = eps /\ $closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps
~$internal_closure_object(S,n_closure)
$closure_capture_tasks(S.TODO,n_closure) ++ $closure_capture_frames(S.FRAMES,n_closure) = eps
$closure_capture_prefix(S,[DIRECT (POBJECT n_payload)],$closure_lexicals(pfunction_closure.CODE.EXPRESSIONS),|$closure_lexicals(pfunction_closure.CODE.EXPRESSIONS)|)
$closure_live_object_valid(S,n_closure)
$closure_cache_at(S.CLOSURECACHES,n_closure) = (pclosurecache)
S.CLOSURECACHES = [pclosurecache]
pclosurecache.OBJECT = n_closure /\ pclosurecache.FUNCTION = porigin_closure /\ pclosurecache.SOURCE = eps
pclosurecache.SCOPE = (BIND_UNSCOPED) /\ pclosurecache.CACHE = (CACHE_SHARED)
$closure_cache_literal_scope(S,porigin_closure,BIND_UNSCOPED)
$node_children(S,HOBJECT n_closure) = [HOBJECT n_payload] /\ $node_children(S,HOBJECT n_payload) = eps
$heap_owners($heap_graph(S),HOBJECT n_closure) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
$lookup(S.ENV,$ptascii("watch")) = (n_watch_cell)
S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)
S.OBJECTS[n_watch] = WEAKREFERENCE (n_closure)
$weakref_get(S,n_watch) = POBJECT n_closure
$lookup(S.ENV,$ptascii("readerWeak")) = (n_reader_weak_cell)
S.STORE[n_reader_weak_cell] = DEFINED (POBJECT n_reader_weak)
S.OBJECTS[n_reader_weak] = WEAKREFERENCE (n_receiver)
$weakref_get(S,n_reader_weak) = POBJECT n_receiver
$heap_unique([HOBJECT n_receiver,HOBJECT n_closure,HOBJECT n_payload,HOBJECT n_watch,HOBJECT n_reader_weak])
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("held")) = (n_held)
$lookup(S.ENV,$ptascii("payload")) = (n_payload_cell)
S.STORE[n_reader] = DEFINED PNULL /\ S.STORE[n_held] = DEFINED PNULL /\ S.STORE[n_payload_cell] = DEFINED PNULL
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
$owning_review_output(S.EVENTS) = $ptascii("I;G;")
$closure_state_valid(S) /\ $closure_cache_records_valid(S) /\ $weakref_state_valid(S)
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

AUTHORITY = r'''
$property_magic_cv_realclosure(S,n_closure)
~$property_magic_cv_realclosure(S,|S.OBJECTS|)
~$property_magic_cv_realclosure(S[.SOURCES = eps],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURETEMPLATES = eps],n_closure)
~$property_magic_cv_realclosure(S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_closure],n_closure)
~$property_magic_cv_realclosure(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps)],n_closure)
~$property_magic_cv_realclosure(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure eps eps],n_closure)
~$property_magic_cv_realclosure(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([UNINITIALIZED]) eps],n_closure)
~$property_magic_cv_realclosure(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([ALIAS n_payload_cell]) eps],n_closure)
~$property_magic_cv_realclosure(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) ([{ORIGIN porigin_closure,CELL n_payload_cell}])],n_closure)
~$property_magic_cv_realclosure(S[.TODO = (AT porigin_closure (CLOSURE_CAPTURE n_closure 1)) :: S.TODO],n_closure)
pframe_capture = {SILENCES eps,LOCALS eps,TODO ([CLOSURE_CAPTURE n_closure 1]),ORIGIN (porigin_closure),HELD eps,CONTEXT eps,RETIREDOWNERS eps,BORROWEDREAD eps,OBJECTCAST eps,CONSTCONTEXT eps}
~$property_magic_cv_realclosure(S[.FRAMES = [pframe_capture]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURESCOPES = [{OBJECT n_closure,LEXICAL pmethoddesc.OWNER,CALLED pmethoddesc.OWNER,RECEIVER eps,CREATION eps}]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSUREBINDINGS = [{OBJECT n_closure,SITE ppropertyempty.SITE,SOURCE n_receiver,LEXICAL eps,CALLED eps,RECEIVER eps}]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = eps],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache,pclosurecache]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.OBJECT = n_receiver]]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.SOURCE = (n_receiver)]]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.SCOPE = eps]]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.CACHE = eps]]],n_closure)
~$property_magic_cv_realclosure(S[.CLOSURECACHES = [pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]]],n_closure)
S_arrow = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_closure,NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 (NScalarInt (INTEGER 7) metadata_closure) metadata_closure)]]]
$closure_template_origins_valid(S_arrow,[pfunction_closure]) /\ $closure_cache_records_valid(S_arrow)
~$property_magic_cv_realclosure(S_arrow,n_closure)
S_generator = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_closure,NExprClosure phpType14 phpType4_static phpType4_ref phpType16 phpType21 phpType18 (SEQUENCE ([NStmtExpression (NExprYield ABSENT ABSENT metadata_closure) metadata_closure])) metadata_closure)]]]
$function_generator(S_generator,pfunction_closure) /\ ~$property_magic_cv_realclosure(S_generator,n_closure)
'''.strip().splitlines()

CV_FRONT = r'''
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_empty_capture(S,ppropertyempty)
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps)],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_arrow,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_generator,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
'''.strip().splitlines()

LITERAL_FRONT = r'''
~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
'''.strip().splitlines()

LIFETIME = r'''
$property_empty_rv_kind(S,S.OBJECTS[n_closure]) /\ $property_empty_rv_ready(S,ppropertyempty)
~$property_empty_rv_ready(S[.SOURCES = eps],ppropertyempty)
~$property_empty_rv_ready(S,ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)])
~$property_empty_rv_ready(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)],ppropertyempty)
~$property_empty_rv_ready(S[.RESULT = KNOWN (POBJECT (|S.OBJECTS|))],ppropertyempty)
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_closure) = 0 /\ $heap_owners($heap_graph(S_cached_raw),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
~$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv[.OWNER = 1])
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_releasing = S_one[.COMPLETION = NORMAL]
S_releasing.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_cached_raw.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_closure)]
pdestructionoperation.SOURCE = PROPERTY_EMPTY_RESULT ppropertyempty true
pdestructionoperation.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation.PENDING = eps
$weakref_get(S_releasing,n_watch) = POBJECT n_closure
PhpStep: S_releasing ~> S_retired_raw
~((HOBJECT n_closure) <- S_retired_raw.ALLOCATIONS) /\ (HOBJECT n_payload) <- S_retired_raw.ALLOCATIONS
S_retired_raw.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_retired_raw.CLOSURECACHES = S.CLOSURECACHES
$weakref_get(S_retired_raw,n_watch) = PNULL /\ $weakref_get(S_retired_raw,n_reader_weak) = POBJECT n_receiver
S_retired_raw.EVENTS = S.EVENTS /\ S_retired_raw.STORE[n_destination] = DEFINED (PINT 42)
S_retired_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_cached_raw.TODO
pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_payload),DESTRUCTION_HANDLE n_closure]
$heap_owners($heap_graph(S_retired_raw),HOBJECT n_payload) = 1 /\ $heap_owners($heap_graph(S_retired_raw),HOBJECT n_receiver) = 1
S_retired = $owning_review_after(S_releasing,S_retired_raw)
S_payload_found = $owning_review_seek(S_retired,OW_DTOR n_payload,1000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
S_payload.CURRENT = (pcallcontext_payload)
$destructor_context_call(pcallcontext_payload,S_payload.CURRENT,S_payload.FRAMES) = (pdestructorcall_payload)
pdestructorcall_payload.OPERATION = (pdestructionoperation_payload)
pdestructionoperation_payload.SOURCE = PROPERTY_EMPTY_RESULT ppropertyempty true
pdestructionoperation_payload.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation_payload.PENDING = eps
~((HOBJECT n_closure) <- S_payload.ALLOCATIONS) /\ (HOBJECT n_payload) <- S_payload.ALLOCATIONS
$weakref_get(S_payload,n_watch) = PNULL /\ $weakref_get(S_payload,n_reader_weak) = POBJECT n_receiver
$heap_owners($heap_graph(S_payload),HOBJECT n_receiver) = 1
$property_empty_guard(S_payload,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S_payload,n_receiver,ppropertyempty.NAME)
S_payload.EVENTS = S.EVENTS /\ S_payload.STORE[n_destination] = DEFINED (PINT 42)
S_payload.STORE[n_selector] = DEFINED pvalue_changed
'''.strip().splitlines()

NORMAL = r'''
S_ready_found = $rc_review_seek(S_payload,2000)
S_ready_found.COMPLETION = NORMAL \/ S_ready_found.COMPLETION = BUDGET
S_ready = S_ready_found[.COMPLETION = NORMAL]
S_ready.TODO = S_cached_raw.TODO /\ S_ready.RESULT = KNOWN (PBOOL false)
~((HOBJECT n_closure) <- S_ready.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_ready.ALLOCATIONS)
$weakref_get(S_ready,n_watch) = PNULL /\ $weakref_get(S_ready,n_reader_weak) = POBJECT n_receiver
$heap_owners($heap_graph(S_ready),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_ready,ppropertyemptyrv) /\ $property_empty_guard(S_ready,n_receiver,ppropertyempty.NAME)
$owning_review_output(S_ready.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;")
S_ready.STORE[n_destination] = DEFINED (PINT 42)
S_ready.STORE[n_selector] = DEFINED pvalue_after
$string_bytes(pvalue_after) = ($ptascii("after-payload"))
~$property_magic_cv_result_supported(S_ready,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_closure))
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
S_receiver.STORE[n_destination] = DEFINED (PINT 42)
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
'''.strip().splitlines()

THROW = r'''
S_throw_found = $owning_review_seek(S_payload,OW_RV_THROW,2000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: S_cached_raw.TODO
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps
$throwable_live(S_throw,n_error) /\ $throwable_field(S_throw,n_error,"previous") = PNULL
$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("capture"))
$throwable_field(S_throw,n_error,"line") = PINT 3
~((HOBJECT n_closure) <- S_throw.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_throw.ALLOCATIONS)
$weakref_get(S_throw,n_watch) = PNULL /\ $weakref_get(S_throw,n_reader_weak) = POBJECT n_receiver
$heap_owners($heap_graph(S_throw),HOBJECT n_receiver) = 1
$property_empty_rv_valid(S_throw,ppropertyemptyrv) /\ $property_empty_guard(S_throw,n_receiver,ppropertyempty.NAME)
$owning_review_output(S_throw.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;")
S_throw.STORE[n_destination] = DEFINED (PINT 42)
S_throw.STORE[n_selector] = DEFINED pvalue_after
$string_bytes(pvalue_after) = ($ptascii("after-payload"))
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail* /\ S_release_raw.RESULT = KNOWN PNULL
$heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 0
~$property_empty_guard(S_release_raw,n_receiver,ppropertyempty.NAME)
S_receiver_found = $owning_review_seek($owning_review_after(S_throw,S_release_raw),OW_DTOR n_receiver,1000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_error
pdestructionoperation_receiver.VALUE = KNOWN PNULL /\ pdestructionoperation_receiver.PENDING = (n_error)
S_receiver.STORE[n_destination] = DEFINED (PINT 42)
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
S_catch_found = $owning_review_seek(S_receiver,OW_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
$call_task_valid(S_catch,CATCH_BIND porigin_try n_index n_error)
$throwable_field(S_catch,n_error,"previous") = PNULL
S_catch.STORE[n_destination] = DEFINED (PINT 42)
~((HOBJECT n_receiver) <- S_catch.ALLOCATIONS) /\ $weakref_get(S_catch,n_reader_weak) = PNULL
$owning_review_output(S_catch.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;")
PhpStep: S_catch ~> S_bound_raw
S_bound = $owning_review_after(S_catch,S_bound_raw)
$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)
S_bound.STORE[n_failure] = DEFINED (POBJECT n_error)
'''.strip().splitlines()

DONE = r'''
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_closure) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_watch) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_reader_weak) <- S_done.ALLOCATIONS)
S_done.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_done.CLOSURECACHES = S.CLOSURECACHES
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL
S_done.STORE[n_selector] = DEFINED pvalue_after
S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\ S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps
$closure_state_valid(S_done) /\ $closure_cache_records_valid(S_done) /\ $weakref_state_valid(S_done)
$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S_retired,4096) = S_done
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_closure)')
CASES = {
    'realclosure-cv-empty-captured-owner-before-receiver': {
        'source': ROWS[0]['source'], 'stage': STAGE,
        'checks': FRONT + AUTHORITY + CV_FRONT + LIFETIME + NORMAL + DONE + [
            'S_done.STORE[n_destination] = DEFINED (PBOOL false)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;FALSE;CAPTURE;RECEIVER_GONE;DONE;")',
        ],
    },
    'realclosure-literal-empty-capture-throw-existing-route': {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': FRONT + AUTHORITY + LITERAL_FRONT + LIFETIME + THROW + DONE + [
            r'S_done.STORE[n_destination] = DEFINED (PINT 42) /\ $lookup(S_done.ENV,$ptascii("failure")) = eps',
            '$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;CAUGHT;KEEP;CAPTURE;RECEIVER_GONE;DONE;")',
        ],
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
