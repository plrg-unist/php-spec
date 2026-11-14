#!/usr/bin/env python3
"""Check original static-method FCC authority and Empty wrapper-before-receiver release."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning
import magic_property_realclosure_quiet_get_review_protocol as literal

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.ORIGIN = (ppropertyempty.SITE) /\ S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_closure)
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
S.CLOSURECACHES = [pclosurecache]
pclosurecache = {OBJECT n_closure,FUNCTION porigin_method,SOURCE eps,SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}
$function_cache_at(S.FUNCTIONCACHES,porigin_method) = (pfunctioncache)
$function_cache_policy(S,porigin_method,n_closure) = (CACHE_SHARED)
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
$owning_review_output(S.EVENTS) = $ptascii("WARM;I;G;")
$closure_state_valid(S) /\ $closure_cache_records_valid(S) /\ $weakref_state_valid(S)
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

BASIC = r'''
$property_magic_cv_static_methodclosure(S,n_closure)
~$property_magic_cv_namedclosure(S,n_closure)
~$property_magic_cv_realclosure(S,n_closure) /\ ~$property_magic_cv_arrow(S,n_closure)
$property_empty_rv_kind(S,S.OBJECTS[n_closure])
~$property_empty_rv_kind(S[.RESULT = KNOWN PNULL],S.OBJECTS[n_closure])
~$property_empty_rv_kind(S[.RESULT = KNOWN (POBJECT n_receiver)],S.OBJECTS[n_closure])
'''.strip().splitlines()

AUTHORITY = BASIC + r'''
~$property_magic_cv_static_methodclosure(S,|S.OBJECTS|)
~$property_magic_cv_static_methodclosure(S[.SOURCES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSNAMES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CODE = [pcode[.NAMES = eps]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_site pclassdesc_receiver.NAME eps]]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_method],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_site S.OBJECTS[n_closure]],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site pmethoddesc.OWNER eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_owner ({FUNCTION porigin_method,CALLSITE (porigin_site),LEXICAL_CLASS (porigin_owner),CALLED_CLASS (porigin_owner)})],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = [pclassdesc_target[.KIND = "interface"],pclassdesc_receiver]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = [pclassdesc_target[.PARENT = (pclassdesc_receiver.NAME)],pclassdesc_receiver]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = [pclassdesc_target[.METHODS = [pmethoddesc_method[.STATIC = false]]],pclassdesc_receiver]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = [pclassdesc_target[.METHODS = [pmethoddesc_method[.ABSTRACT = true]]],pclassdesc_receiver]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = [pclassdesc_target[.METHODS = [pmethoddesc_method[.VISIBILITY = PROPERTY_PRIVATE]]],pclassdesc_receiver]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSES = [pclassdesc_target[.METHODS = [pmethoddesc_method[.FUNCTION = pfunction_method[.BODY = pcpath_method]]]],pclassdesc_receiver]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = pmethoddesc.OWNER]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = [pclosurescope[.CALLED = pmethoddesc.OWNER]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = [pclosurescope[.RECEIVER = (n_receiver)]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURESCOPES = [pclosurescope[.CREATION = ({FUNCTION porigin_method,CALLSITE (porigin_site),RECEIVER false,EVIDENCE eps})]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSUREBINDINGS = [{OBJECT n_closure,SITE porigin_site,SOURCE n_receiver,LEXICAL (porigin_owner),CALLED (porigin_owner),RECEIVER eps}]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache,pclosurecache]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache[.SOURCE = (n_closure)]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache[.SCOPE = (BIND_UNSCOPED)]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]]],n_closure)
S_late_cache = S[.FUNCTIONCACHES = $function_cache_set(S.FUNCTIONCACHES,pfunctioncache[.INITIALIZED = ($(n_closure + 1))])]
$closure_cache_records_valid(S_late_cache) /\ $closure_live_object_valid(S_late_cache,n_closure)
$function_cache_policy(S_late_cache,porigin_method,n_closure) = (CACHE_PRIVATE n_closure)
~$property_magic_cv_static_methodclosure(S_late_cache,n_closure) /\ ~$property_empty_rv_kind(S_late_cache,S.OBJECTS[n_closure])
S_clone = $clone_object(S,n_closure)
n_clone = |S.OBJECTS|
S_clone.RESULT = KNOWN (POBJECT n_clone)
S_clone.OBJECTS[n_clone] = S.OBJECTS[n_closure]
$closure_cache_at(S_clone.CLOSURECACHES,n_clone) = (pclosurecache_clone)
pclosurecache_clone.SOURCE = (n_closure) /\ pclosurecache_clone.CACHE = (CACHE_SHARED)
$closure_live_object_valid(S_clone,n_clone) /\ $closure_cache_records_valid(S_clone)
$property_magic_cv_static_methodclosure(S_clone,n_clone) /\ $property_empty_rv_kind(S_clone,S_clone.OBJECTS[n_clone])
S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]
~$property_magic_cv_static_methodclosure(S_unallocated,n_closure)
~$property_magic_cv_result_supported(S_unallocated,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
S_freeing = S[.TODO = S.TODO ++ [INSTANCE_STORAGE_STEP {OBJECT n_closure,HANDLE n_closure,SLOTS eps,NEXT 0,NOTIFY eps,CALLER eps,ORIGIN eps,CONSTCONTEXT eps,USER false}]]
$instance_storage_freeing(S_freeing,n_closure)
~$property_magic_cv_result_supported(S_freeing,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_empty_rv_ready(S_freeing,ppropertyempty)
'''.strip().splitlines()


def source_counterfact(label, *, owner=None, method=None, site=None):
    occurrences = 'pcunit.OCCURRENCES'
    for path, node in (('pcpath_class', owner), ('pcpath_method', method), ('pcpath_site', site)):
        if node is not None:
            occurrences = f'$rc_review_occurrence({occurrences},{path},{node})'
    return [f'S_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
            f'~$property_magic_cv_static_methodclosure(S_{label},n_closure)']


OWNER = ('NStmtClass phpType14_class phpType24_class '
         '(NIdentifier (BYTES text_class) metadata_class_name) ABSENT phpType42 '
         '(SEQUENCE ({members})) metadata_class')
METHOD = ('NStmtClassMethod phpType14_method (INTEGER {flags}) phpType4_ref '
          '(NIdentifier (BYTES text_method) metadata_method_name) phpType16 phpType18 '
          '(SEQUENCE ({body})) metadata_method')
SITE = ('NExprStaticCall ({class_name}) (NIdentifier (BYTES text_selected) metadata_selected) '
        '(SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site')
AUTHORITY += source_counterfact('owner_missing_method', owner=OWNER.format(members='eps'))
AUTHORITY += source_counterfact('owner_wrong_child', owner=OWNER.format(members='[NStmtNop metadata_method]'))
AUTHORITY += source_counterfact('owner_traits', owner=OWNER.format(members='[statement_method,NStmtTraitUse (SEQUENCE ([NName (BYTES text_class) metadata_class_name])) (SEQUENCE eps) metadata_class]'))
for label, flags in (('raw_nonstatic', 1), ('raw_private', 12), ('raw_abstract', 25)):
    method = METHOD.format(flags=flags, body='statement*')
    AUTHORITY += source_counterfact(label, owner=OWNER.format(members=f'[{method}]'), method=method)
generator = METHOD.format(flags=9, body='[NStmtExpression (NExprYield ABSENT ABSENT metadata_method) metadata_method]')
AUTHORITY += source_counterfact('raw_generator', owner=OWNER.format(members=f'[{generator}]'), method=generator)
AUTHORITY += ['$function_generator(S_raw_generator,pfunction_method)']
AUTHORITY += source_counterfact('capture_wrong_name', site=SITE.format(class_name='NName (BYTES "T3RoZXI=") metadata_requested'))
AUTHORITY += source_counterfact('capture_keyword', site=SITE.format(class_name='NName (BYTES "c2VsZg==") metadata_requested'))
AUTHORITY += source_counterfact('capture_dynamic_class', site=SITE.format(class_name='NExprVariable (BYTES "aGVsZA==") metadata_requested'))
AUTHORITY += source_counterfact('capture_fully_qualified', site=SITE.format(class_name='NNameFullyQualified (BYTES text_requested) metadata_requested'))

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
        'checks': FRONT + BASIC + [
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
