#!/usr/bin/env python3
"""Check retired static-method clone ancestry, wrapper disposal and saved receiver throws."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning
import magic_property_realclosure_quiet_get_review_protocol as literal

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_clone_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.ORIGIN = (ppropertyempty.SITE) /\ S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_closure)
n_original = 0
n_intermediate = 1
n_closure = 2
S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_owner pmethodcapture?
pmethodcapture? = eps
(HOBJECT n_closure) <- S.ALLOCATIONS
~$instance_storage_freeing(S,n_closure)
$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)
pmethoddesc_method.FUNCTION = pfunction_method
pmethoddesc_method.OWNER = porigin_owner
pmethoddesc_method.STATIC /\ ~pmethoddesc_method.ABSTRACT /\ pmethoddesc_method.VISIBILITY = PROPERTY_PUBLIC
$class_at(S.CLASSES,porigin_owner) = (pclassdesc_target)
pclassdesc_target.KIND = "class" /\ pclassdesc_target.PARENT = eps
porigin_owner = PORIGIN n_unit pcpath_class
porigin_method = PORIGIN n_unit pcpath_method
pcpath_method = pcpath_class ++ [PCFIELD 5,PCINDEX 0]
$origin_node(S.SOURCES,porigin_owner) = (NStmtClass phpType14_class phpType24_class (NIdentifier (BYTES text_class) metadata_class_name) ABSENT phpType42 (SEQUENCE ([statement_method])) metadata_class)
statement_method = NStmtClassMethod phpType14_method (INTEGER flags_method) phpType4_ref (NIdentifier (BYTES text_method) metadata_method_name) phpType16 phpType18 (SEQUENCE statement*) metadata_method
$origin_node(S.SOURCES,porigin_method) = (statement_method)
pfunction_method.BODY = pcpath_method ++ [PCFIELD 6]
pclassdesc_target.NAME = $base64(text_class)
pmethoddesc_method.NAME = $base64(text_method)
$ppmethod_flags(flags_method,"class") /\ $ppproperty_flag(flags_method,8) /\ ~$ppproperty_flag(flags_method,16)
~$function_generator(S,pfunction_method)
porigin_site = PORIGIN n_unit pcpath_site
$origin_node(S.SOURCES,porigin_site) = (NExprStaticCall (NName (BYTES text_requested) metadata_requested) (NIdentifier (BYTES text_selected) metadata_selected) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site)
$base64(text_requested) = pclassdesc_target.NAME
$ptlc($base64(text_selected)) = $ptlc(pmethoddesc_method.NAME)
$scoped_requested_site(S,porigin_site,NName (BYTES text_requested) metadata_requested,porigin_owner,eps)
$goto_source_owner($all_functions(S),n_unit,pcpath_site) = eps /\ $closure_source_class(S,porigin_site) = eps
S.SOURCES = [pcunit]
pcunit.ID = n_unit
S.CODE = [pcode]
pcode.UNIT = n_unit
$code_name(pcode.NAMES,pcpath_site) = ((pclassdesc_target.NAME,eps))
$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)
pclosurescope = {OBJECT n_closure,LEXICAL porigin_owner,CALLED porigin_owner,RECEIVER eps,CREATION eps}
S.CLOSURESCOPES = [pclosurescope]
$closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps
~$internal_closure_object(S,n_closure)
$closure_live_object_valid(S,n_closure)
$closure_cache_at(S.CLOSURECACHES,n_closure) = (pclosurecache)
S.CLOSURECACHES = [pclosurecache_original,pclosurecache_intermediate,pclosurecache]
pclosurecache = {OBJECT n_closure,FUNCTION porigin_method,SOURCE (n_intermediate),SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}
$function_cache_at(S.FUNCTIONCACHES,porigin_method) = (pfunctioncache)
$function_cache_policy(S,porigin_method,n_closure) = (CACHE_SHARED)
pclosurecache_original = {OBJECT n_original,FUNCTION porigin_method,SOURCE eps,SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}
pclosurecache_intermediate = {OBJECT n_intermediate,FUNCTION porigin_method,SOURCE (n_original),SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}
S.OBJECTS[n_original] = S.OBJECTS[n_closure]
S.OBJECTS[n_intermediate] = S.OBJECTS[n_closure]
~((HOBJECT n_original) <- S.ALLOCATIONS) /\ ~((HOBJECT n_intermediate) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES,n_original) = eps /\ $closure_scope_at(S.CLOSURESCOPES,n_intermediate) = eps
$closure_binding_at(S.CLOSUREBINDINGS,n_original) = eps /\ $closure_binding_at(S.CLOSUREBINDINGS,n_intermediate) = eps
$function_cache_policy(S,porigin_method,n_original) = (CACHE_SHARED)
$heap_owners($heap_graph(S),HOBJECT n_original) = 0 /\ $heap_owners($heap_graph(S),HOBJECT n_intermediate) = 0
$lookup(S.ENV,$ptascii("original")) = (n_original_cell)
$lookup(S.ENV,$ptascii("intermediate")) = (n_intermediate_cell)
S.STORE[n_original_cell] = DEFINED PNULL /\ S.STORE[n_intermediate_cell] = DEFINED PNULL
$lookup(S.ENV,$ptascii("sourceWeak")) = (n_source_weak_cell)
S.STORE[n_source_weak_cell] = DEFINED (POBJECT n_source_weak)
$weakref_get(S,n_source_weak) = PNULL
$lookup(S.ENV,$ptascii("intermediateWeak")) = (n_intermediate_weak_cell)
S.STORE[n_intermediate_weak_cell] = DEFINED (POBJECT n_intermediate_weak)
$weakref_get(S,n_intermediate_weak) = PNULL
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
$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc_receiver)
S.CLASSES = [pclassdesc_target,pclassdesc_receiver]
pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)
$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)
$owning_review_output(S.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;")
$closure_state_valid(S) /\ $closure_cache_records_valid(S) /\ $weakref_state_valid(S)
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

BASIC = r'''
$property_magic_cv_static_methodclosure(S,n_closure)
$property_magic_cv_static_method_clone_history(S,n_closure,porigin_method,porigin_site,porigin_owner)
$property_magic_cv_static_method_clone_history(S,n_intermediate,porigin_method,porigin_site,porigin_owner)
~$property_magic_cv_static_methodclosure(S,n_original) /\ ~$property_magic_cv_static_methodclosure(S,n_intermediate)
$property_empty_rv_kind(S,S.OBJECTS[n_closure])
~$property_empty_rv_kind(S[.RESULT = KNOWN PNULL],S.OBJECTS[n_closure])
~$property_empty_rv_kind(S[.RESULT = KNOWN (POBJECT n_receiver)],S.OBJECTS[n_closure])
'''.strip().splitlines()

AUTHORITY = BASIC + r'''
~$property_magic_cv_static_method_clone_history(S,|S.OBJECTS|,porigin_method,porigin_site,porigin_owner)
~$property_magic_cv_static_methodclosure(S[.SOURCES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CODE = [pcode[.NAMES = eps]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_original] = CONSTANTCLOSURE porigin_site S.OBJECTS[n_original]],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_intermediate] = CONSTANTCLOSURE porigin_site S.OBJECTS[n_intermediate]],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_original] = METHODCLOSURE porigin_method ppropertyempty.SITE porigin_owner eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_intermediate] = METHODCLOSURE porigin_method porigin_site pmethoddesc.OWNER eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = [pclosurescope[.CALLED = pmethoddesc.OWNER]]],n_closure)
S_bad_root_scope = S[.CLOSURESCOPES = [pclosurescope,{OBJECT n_original,LEXICAL porigin_owner,CALLED pmethoddesc.OWNER,RECEIVER eps,CREATION eps}]]
$closure_cache_records_valid(S_bad_root_scope) /\ $closure_live_object_valid(S_bad_root_scope,n_closure)
~$property_magic_cv_static_method_clone_history(S_bad_root_scope,n_closure,porigin_method,porigin_site,porigin_owner)
~$property_magic_cv_static_methodclosure(S_bad_root_scope,n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = [pclosurescope,{OBJECT n_intermediate,LEXICAL porigin_owner,CALLED porigin_owner,RECEIVER (n_receiver),CREATION eps}]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSUREBINDINGS = [{OBJECT n_original,SITE porigin_site,SOURCE n_receiver,LEXICAL (porigin_owner),CALLED (porigin_owner),RECEIVER eps}]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSUREBINDINGS = [{OBJECT n_intermediate,SITE porigin_site,SOURCE n_receiver,LEXICAL (porigin_owner),CALLED (porigin_owner),RECEIVER eps}]],n_closure)
S_late_origin = S[.FUNCTIONCACHES = $function_cache_set(S.FUNCTIONCACHES,pfunctioncache[.INITIALIZED = ($(n_original + 1))])]
$function_cache_policy(S_late_origin,porigin_method,n_original) = (CACHE_PRIVATE n_original)
$function_cache_policy(S_late_origin,porigin_method,n_closure) = (CACHE_SHARED)
$closure_cache_records_valid(S_late_origin) /\ $closure_live_object_valid(S_late_origin,n_closure)
$heap_graph(S_late_origin) = $heap_graph(S)
~$property_magic_cv_static_method_clone_history(S_late_origin,n_closure,porigin_method,porigin_site,porigin_owner)
~$property_magic_cv_static_methodclosure(S_late_origin,n_closure)
~$property_empty_rv_kind(S_late_origin,S.OBJECTS[n_closure])
~$property_magic_cv_result_supported(S_late_origin,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
S_next = $clone_object(S,n_closure)
n_next = |S.OBJECTS|
S_next.RESULT = KNOWN (POBJECT n_next)
$closure_cache_at(S_next.CLOSURECACHES,n_next) = (pclosurecache_next)
pclosurecache_next.SOURCE = (n_closure) /\ pclosurecache_next.CACHE = (CACHE_SHARED)
$closure_live_object_valid(S_next,n_next) /\ $closure_cache_records_valid(S_next)
$property_magic_cv_static_methodclosure(S_next,n_next) /\ $property_empty_rv_kind(S_next,S_next.OBJECTS[n_next])
S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]
~$property_magic_cv_static_methodclosure(S_unallocated,n_closure)
~$property_magic_cv_result_supported(S_unallocated,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
'''.strip().splitlines()


# Retained cache stamps must describe a descending same-function Shared chain.
for label, root, middle, current in (
    ('root_missing', None, 'pclosurecache_intermediate', 'pclosurecache'),
    ('root_private', 'pclosurecache_original[.CACHE = (CACHE_PRIVATE n_original)]', 'pclosurecache_intermediate', 'pclosurecache'),
    ('root_scope', 'pclosurecache_original[.SCOPE = (BIND_UNSCOPED)]', 'pclosurecache_intermediate', 'pclosurecache'),
    ('root_function', 'pclosurecache_original[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]', 'pclosurecache_intermediate', 'pclosurecache'),
    ('root_cycle', 'pclosurecache_original[.SOURCE = (n_original)]', 'pclosurecache_intermediate', 'pclosurecache'),
    ('middle_cycle', 'pclosurecache_original', 'pclosurecache_intermediate[.SOURCE = (n_intermediate)]', 'pclosurecache'),
    ('middle_forward', 'pclosurecache_original', 'pclosurecache_intermediate[.SOURCE = (n_closure)]', 'pclosurecache'),
    ('middle_private', 'pclosurecache_original', 'pclosurecache_intermediate[.CACHE = (CACHE_PRIVATE n_intermediate)]', 'pclosurecache'),
    ('current_cycle', 'pclosurecache_original', 'pclosurecache_intermediate', 'pclosurecache[.SOURCE = (n_closure)]'),
    ('current_forward', 'pclosurecache_original', 'pclosurecache_intermediate', 'pclosurecache[.SOURCE = (|S.OBJECTS|)]'),
    ('current_private', 'pclosurecache_original', 'pclosurecache_intermediate', 'pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]'),
    ('current_scope', 'pclosurecache_original', 'pclosurecache_intermediate', 'pclosurecache[.SCOPE = (BIND_UNSCOPED)]'),
):
    records = ','.join(record for record in (root,middle,current) if record is not None)
    AUTHORITY += [f'S_{label} = S[.CLOSURECACHES = [{records}]]',
                  f'~$property_magic_cv_static_method_clone_history(S_{label},n_closure,porigin_method,porigin_site,porigin_owner)',
                  f'~$property_magic_cv_static_methodclosure(S_{label},n_closure)']

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
$owning_review_output(S_ready.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;")
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
$owning_review_output(S_catch.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;RECEIVER;WRAPPER_GONE;")
'''.strip().splitlines()

DONE = r'''
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_closure) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_watch) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_reader_weak) <- S_done.ALLOCATIONS)
~((HOBJECT n_source_weak) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_intermediate_weak) <- S_done.ALLOCATIONS)
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
            '$owning_review_output(S_done.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;RECEIVER;WRAPPER_GONE;FALSE;CAPTURE;RECEIVER_GONE;STATIC;DONE;")',
        ],
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': FRONT + BASIC + [
            '~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
        ] + LIFETIME + THROW + DONE + [
            'S_done.STORE[n_destination] = DEFINED (PINT 42)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;RECEIVER;WRAPPER_GONE;CAUGHT;KEEP;CAPTURE;RECEIVER_GONE;STATIC;DONE;")',
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
