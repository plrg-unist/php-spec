#!/usr/bin/env python3
"""Check authenticated Arrow Closure quiet Get transfer and capture ownership."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_arrow_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.RESULT = KNOWN (POBJECT n_closure)
S.BASE = BASE_VALUE (KNOWN PNULL)
n_receiver = ppropertycoalesce.OBJECT
S.OBJECTS[n_closure] = REALCLOSURE porigin_closure pitem* eps
(HOBJECT n_closure) <- S.ALLOCATIONS /\ ~$instance_storage_freeing(S,n_closure)
$function_at(S.CLOSURETEMPLATES,porigin_closure) = (pfunction_closure)
$origin_node(S.SOURCES,porigin_closure) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression_body metadata_closure)
~$function_generator(S,pfunction_closure)
porigin_closure = PORIGIN n_unit pcpath_closure
pfunction_closure.BODY = pcpath_closure ++ [PCFIELD 5]
$pparrow_template(pfunction_closure)
(IMPLICIT ptbytes_capture z_capture)* = $closure_lexicals(pfunction_closure.CODE.EXPRESSIONS)
ptbytes_capture* = $pparrow_remove($pparrow_discover(expression_body),$pparrow_param_names(phpType16))
$closure_source_class(S,porigin_closure) = eps
$closure_scope_at(S.CLOSURESCOPES,n_closure) = eps /\ $closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps
~$internal_closure_object(S,n_closure)
$closure_capture_tasks(S.TODO,n_closure) ++ $closure_capture_frames(S.FRAMES,n_closure) = eps
$closure_capture_prefix(S,pitem*,$closure_lexicals(pfunction_closure.CODE.EXPRESSIONS),|$closure_lexicals(pfunction_closure.CODE.EXPRESSIONS)|)
$closure_live_object_valid(S,n_closure)
$closure_cache_at(S.CLOSURECACHES,n_closure) = (pclosurecache)
pclosurecache.OBJECT = n_closure /\ pclosurecache.FUNCTION = porigin_closure /\ pclosurecache.SOURCE = eps
pclosurecache.SCOPE = (BIND_UNSCOPED) /\ pclosurecache.CACHE = (CACHE_SHARED)
$closure_cache_literal_scope(S,porigin_closure,BIND_UNSCOPED)
$node_children(S,HOBJECT n_closure) = $closure_items_nodes(pitem*)
$heap_owners($heap_graph(S),HOBJECT n_closure) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
$property_get_method(S,n_receiver) = (pmethoddesc)
ppropertycoalesce.GET = (pmethoddesc.FUNCTION.ORIGIN)
pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
$property_coalesce_valid(S,ppropertycoalesce) /\ $call_task_valid(S,PROPERTY_COALESCE_RESULT ppropertycoalesce true)
$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
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
$heap_unique([HOBJECT n_receiver,HOBJECT n_closure,HOBJECT n_watch])
S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$closure_state_valid(S) /\ $closure_cache_records_valid(S) /\ $weakref_state_valid(S)
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
'''.strip().splitlines()

BINARY = FRONT + r'''
ppropertycoalesce.PROPERTY = eps
$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
pitem* = eps /\ $node_children(S,HOBJECT n_closure) = eps
ptbytes_capture* = eps
expression_body = NScalarInt (INTEGER 7) metadata_body
'''.strip().splitlines()

ASSIGN = FRONT + r'''
ppropertycoalesce.PROPERTY = (porigin_property)
$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
$property_coalesce_assign_source(S,porigin_parent) /\ $property_coalesce_assign_base(S,porigin_parent,pbase)
pitem* = [DIRECT (POBJECT n_payload)]
ptbytes_capture* = [$ptascii("payload")]
expression_body = NExprVariable (BYTES text_body) metadata_body
$base64(text_body) = $ptascii("payload")
S.OBJECTS[n_payload] = INSTANCE porigin_payload
$node_children(S,HOBJECT n_closure) = [HOBJECT n_payload] /\ $node_children(S,HOBJECT n_payload) = eps
$heap_owners($heap_graph(S),HOBJECT n_payload) = 1
$lookup(S.ENV,$ptascii("payload")) = (n_payload_cell)
S.STORE[n_payload_cell] = DEFINED PNULL
'''.strip().splitlines()

LIFETIME = r'''
$property_magic_cv_arrow(S,n_closure)
$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S.RESULT)
~$property_magic_cv_arrow(S[.CLOSURETEMPLATES = eps],n_closure)
~$property_magic_cv_arrow(S[.SOURCES = eps],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = eps],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache,pclosurecache]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.SOURCE = (n_closure)]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]]],n_closure)
~$property_magic_cv_arrow(S[.CLOSURECACHES = [pclosurecache[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure pitem* eps)],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE pmethoddesc.FUNCTION.ORIGIN eps eps],n_closure)
~$property_magic_cv_arrow(S[.TODO = (CLOSURE_CAPTURE n_closure 0) :: S.TODO],n_closure)
~$property_magic_cv_realclosure(S,n_closure)
~$property_magic_cv_arrow(S,|S.OBJECTS|)
S_badbody = S[.CLOSURETEMPLATES = [pfunction_closure[.BODY = pcpath_closure ++ [PCFIELD 6]]]]
~$property_magic_cv_arrow(S_badbody,n_closure)
S_nomarker = S[.CLOSURETEMPLATES = [pfunction_closure[.CODE.EXPRESSIONS = eps]]]
~$property_magic_cv_arrow(S_nomarker,n_closure)
S_explicit = S[.CLOSURETEMPLATES = [pfunction_closure[.CODE.EXPRESSIONS = [CODELEXICAL pfunction_closure.BODY $ptascii("payload") false pfunction_closure.LINE,CODEARROW pfunction_closure.BODY pfunction_closure.LINE]]]]
~$property_magic_cv_arrow(S_explicit,n_closure)
S_badname = S[.CLOSURETEMPLATES = [pfunction_closure[.CODE.EXPRESSIONS = [CODEIMPLICIT pfunction_closure.BODY $ptascii("different") pfunction_closure.LINE,CODEARROW pfunction_closure.BODY pfunction_closure.LINE]]]]
~$property_magic_cv_arrow(S_badname,n_closure)
S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]
$property_magic_cv_arrow(S_unallocated,n_closure)
~$property_magic_cv_result_supported(S_unallocated,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))
~$property_coalesce_valid(S[.SOURCES = eps],ppropertycoalesce)
PhpStep: S ~> S_value
S_value.RESULT = S.RESULT /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE
S_value.OBJECTS[n_closure] = S.OBJECTS[n_closure]
$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0 /\ $heap_owners($heap_graph(S_value),HOBJECT n_closure) = 1
$node_children(S_value,HOBJECT n_closure) = $closure_items_nodes(pitem*)
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_value.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]
pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true
pdestructionoperation.VALUE = KNOWN (POBJECT n_closure) /\ pdestructionoperation.PENDING = eps
$heap_owners($heap_graph(S_one),HOBJECT n_closure) = 1
S_one.OBJECTS[n_closure] = S.OBJECTS[n_closure] /\ S_one.EVENTS = S.EVENTS
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
~((HOBJECT n_closure) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_watch) <- S_done.ALLOCATIONS)
S_done.OBJECTS[n_closure] = S.OBJECTS[n_closure]
$weakref_get(S_done,n_watch) = PNULL /\ $lookup(S_done.ENV,$ptascii("answer")) = eps
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_changed
$closure_state_valid(S_done) /\ $closure_cache_records_valid(S_done) /\ $call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
'''.strip().splitlines()

# The edited states above are fixture counterfeits, not source agreements.
BINARY += LIFETIME + r'''
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([UNINITIALIZED]) eps],n_closure)
~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,$(ppropertycoalesce.LINE + 1))
S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*
S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("RESULT;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("RETIRED;"),OUTPUT $ptascii("DONE;")]
'''.strip().splitlines()

ASSIGN += LIFETIME + r'''
$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([UNINITIALIZED]) eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure eps eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload),DIRECT (POBJECT n_payload)]) eps],n_closure)
~$property_magic_cv_arrow(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([ALIAS n_payload_cell]) eps],n_closure)
~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,$(ppropertycoalesce.LINE + 1))
S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*
$heap_owners($heap_graph(S_value),HOBJECT n_payload) = 1
~((HOBJECT n_payload) <- S_done.ALLOCATIONS)
S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("RESULT;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("PAYLOAD;"),OUTPUT $ptascii("CLOSURE_GONE;"),OUTPUT $ptascii("RETIRED;"),OUTPUT $ptascii("DONE;")]
'''.strip().splitlines()

CASES = {
    'arrow-cv-coalesce-literal-result-owner': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*',
        'checks': BINARY,
    },
    'arrow-private-coalesce-assignment-implicit-captured-owner': {
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
