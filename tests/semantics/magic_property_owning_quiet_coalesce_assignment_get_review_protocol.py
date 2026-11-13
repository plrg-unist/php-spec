#!/usr/bin/env python3
"""Check private CV ??= saved values, private storage and abrupt owner transfer."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_coalesce_get_review_protocol as binary_review

CATALOGUE = Path(__file__).with_name('magic_property_owning_quiet_coalesce_assignment_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

COMMON = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
n_receiver = ppropertycoalesce.OBJECT
ppropertycoalesce.PROPERTY = (porigin_property)
ppropertycoalesce.GET = (porigin_get)
ppropertycoalesce.OWNER = 0 /\ ppropertycoalesce.CALLER = eps
$property_get_method(S,n_receiver) = (pmethoddesc)
pfunction = pmethoddesc.FUNCTION
pfunction.ORIGIN = porigin_get /\ ~pfunction.SIGNATURE.BYREF
pfunction.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ ~psparam.VARIADIC
$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)
pclassdesc.KIND = "class" /\ pclassdesc.PARENT = eps
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)
~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])
$property_coalesce_valid(S,ppropertycoalesce) /\ $call_task_valid(S,PROPERTY_COALESCE_RESULT ppropertycoalesce true)
~$property_coalesce_valid(S,ppropertycoalesce[.LINE = $(ppropertycoalesce.LINE + 1)])
~$property_coalesce_valid(S[.SOURCES = eps],ppropertycoalesce)
~$property_coalesce_descriptor(S,ppropertycoalesce[.PROPERTY = eps])
$property_effective_desc(S,n_receiver,ppropertycoalesce.NAME) = (ppropertydesc)
ppropertydesc.ORIGIN = porigin_property /\ ppropertydesc.VISIBILITY = PROPERTY_PRIVATE /\ ~ppropertydesc.STATIC
ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]
$objectprops_at(S.OBJECTPROPS,n_receiver) = (ppropertyslot*)
$property_slot_at(ppropertyslot*,ppropertydesc.KEY) = (ppropertyslot_value)
ppropertyslot_value.DECL = (porigin_property) /\ ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 41))
$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S[.SOURCES = eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,$(ppropertycoalesce.LINE + 1))
$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S.RESULT)
$property_coalesce_assign_source(S,porigin_parent) /\ $property_coalesce_assign_base(S,porigin_parent,pbase)
$task_nodes(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) = eps
~$property_coalesce_active(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME,true)
~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME)
~$property_coalesce_capture(S,ppropertycoalesce)
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_reader] = DEFINED PNULL
S.STORE[n_selector] = DEFINED pvalue_selector
$string_bytes(pvalue_selector) = ($ptascii("changed"))
S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))
$property_hook_coalesce_parent(S,ppropertycoalesce.SITE) = eps
porigin_parent = PORIGIN n_unit pcpath_parent
$origin_node(S.SOURCES,porigin_parent) = (NExprAssignOpCoalesce expression_left expression_right metadata_parent)
$origin_node(S.SOURCES,ppropertycoalesce.SITE) = (expression_left)
expression_left =/= expression_right
S.SOURCES = [pcunit]
S_swapped = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent (NExprAssignOpCoalesce expression_right expression_left metadata_parent)) :: pcunit.OCCURRENCES]]]
$property_magic_cv_source(S_swapped,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S_swapped,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_result_supported(S_swapped,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
S_literal = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent (NExprAssignOpCoalesce expression_left (NScalarInt (INTEGER 9) metadata_parent) metadata_parent)) :: pcunit.OCCURRENCES]]]
$property_magic_cv_source(S_literal,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_coalesce_assign_source(S_literal,ppropertycoalesce.SITE,ppropertycoalesce.LINE)
~$property_magic_cv_result_supported(S_literal,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
PhpStep: S ~> S_release_raw
S_release_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_delivery*
S_release_raw.RESULT = S.RESULT /\ S_release_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_release_raw.EVENTS = S.EVENTS /\ S_release_raw.STORE = S.STORE
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $oc_review_after(S,S_release_raw)
S_one.EVENTS = S.EVENTS
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_release_raw.TODO
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]
pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true
pdestructionoperation.VALUE = S.RESULT /\ pdestructionoperation.PENDING = eps
'''.strip().splitlines()

ARRAY = COMMON + r'''
ppropertycoalesce.NAME = $ptascii("value") /\ ~pfunction.CODE.STRICT
pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$string_bytes(pvalue_selector) = ($ptascii("changed"))
$lookup(S.ENV,$ptascii("destination")) = (n_destination)
S.STORE[n_destination] = DEFINED (PINT 42)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]
n_payload =/= n_receiver
S.OBJECTS[n_payload] = INSTANCE porigin_payload
$heap_owners($heap_graph(S),HARRAY n_array) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_array)],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (PARRAY (|S.ARRAYS|)))
$heap_owners($heap_graph(S_release_raw),HARRAY n_array) = 1 /\ $heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 0
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HARRAY n_array]
$heap_owners($heap_graph(S_one),HARRAY n_array) = 1
S_receiver_found = $oc_review_seek(S_one[.COMPLETION = NORMAL],OC_DTOR n_receiver,2000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
$oc_review_stage(S_receiver,OC_DTOR n_receiver)
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation)
pdestructorcall_receiver.PENDING = eps
(HARRAY n_array) <- S_receiver.ALLOCATIONS /\ (HOBJECT n_payload) <- S_receiver.ALLOCATIONS
$heap_owners($heap_graph(S_receiver),HARRAY n_array) = 1 /\ $heap_owners($heap_graph(S_receiver),HOBJECT n_payload) = 1
S_receiver.EVENTS = S.EVENTS /\ S_receiver.STORE[n_destination] = DEFINED (PINT 42)
S_payload_found = $oc_review_seek(S_receiver,OC_DTOR n_payload,2000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
$oc_review_stage(S_payload,OC_DTOR n_payload)
S_payload.CURRENT = (pcallcontext_payload)
$destructor_context_call(pcallcontext_payload,S_payload.CURRENT,S_payload.FRAMES) = (pdestructorcall_payload)
pdestructorcall_payload.OPERATION = eps /\ pdestructorcall_payload.FRAME = eps
pdestructorcall_payload.PENDING = (n_receiver_error)
$destructor_call_pending_tail(S_payload,pdestructorcall_payload) = (ptask_pending*)
$destructor_tail_pending(ptask_pending*) = (n_receiver_error)
$destructor_call_pending_valid(S_payload,pdestructorcall_payload)
$throwable_live(S_payload,n_receiver_error)
$string_bytes($throwable_field(S_payload,n_receiver_error,"message")) = ($ptascii("receiver-assignment"))
$throwable_field(S_payload,n_receiver_error,"previous") = PNULL
~((HARRAY n_array) <- S_payload.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_payload.ALLOCATIONS)
(HOBJECT n_payload) <- S_payload.ALLOCATIONS
S_payload.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]
S_payload.STORE[n_destination] = DEFINED (PINT 42)
S_catch_found = $oc_review_seek(S_payload,OC_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_payload_error) :: ptask_catch*
$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_payload_error)
$throwable_field(S_catch,n_payload_error,"previous") = POBJECT n_receiver_error
$string_bytes($throwable_field(S_catch,n_payload_error,"message")) = ($ptascii("payload-assignment"))
$throwable_field(S_catch,n_payload_error,"line") = PINT 3 /\ $throwable_field(S_catch,n_receiver_error,"line") = PINT 11
$throwable_field(S_catch,n_receiver_error,"previous") = PNULL
$oc_review_output(S_catch.EVENTS) = $ptascii("I;G;RECEIVER;PAYLOAD;")
~((HOBJECT n_receiver) <- S_catch.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_catch.ALLOCATIONS)
S_catch.STORE[n_destination] = DEFINED (PINT 42)
PhpStep: S_catch ~> S_bound_raw
S_bound = $oc_review_after(S_catch,S_bound_raw)
$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)
S_bound.STORE[n_failure] = DEFINED (POBJECT n_payload_error)
(HOBJECT n_payload_error) <- S_bound.ALLOCATIONS /\ (HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS
S_done = $drive_steps(S_bound,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
$oc_review_output(S_done.EVENTS) = $ptascii("I;G;RECEIVER;PAYLOAD;payload-assignment;receiver-assignment;ROOT;KEEP;CLEARED;NAME_CHANGED;DONE;")
S_done.STORE[n_destination] = DEFINED (PINT 42) /\ S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_selector
S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\ S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps
$lookup(S_done.ENV,$ptascii("failure")) = eps
~((HARRAY n_array) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_payload_error) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S,4096) = S_done
'''.strip().splitlines()

OBJECT = COMMON + r'''
ppropertycoalesce.NAME = $ptascii("value") /\ pfunction.CODE.STRICT
pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]
S.RESULT = KNOWN (POBJECT n_receiver)
$string_bytes(pvalue_selector) = ($ptascii("changed"))
~$property_magic_name_capture(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,ppropertycoalesce.NAME)
$eager_property_class_valid(S,S.OBJECTS[n_receiver]) /\ ~$instance_storage_freeing(S,n_receiver)
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2
~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))
~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_receiver)],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_receiver] = WEAKMAPENTRIES eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_receiver) = 1
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2
S_ready_found = $drive_steps(S_one[.COMPLETION = NORMAL],3)
S_ready_found.COMPLETION = BUDGET
S_ready = S_ready_found[.COMPLETION = NORMAL]
S_ready.TODO = S_release_raw.TODO /\ S_ready.RESULT = S.RESULT /\ S_ready.EVENTS = S.EVENTS
$heap_owners($heap_graph(S_ready),HOBJECT n_receiver) = 1
S_owned_found = $oc_review_seek(S_ready,OC_OUTPUT $ptascii("I;G;OWNED;"),2000)
S_owned_found.COMPLETION = NORMAL \/ S_owned_found.COMPLETION = BUDGET
S_owned = S_owned_found[.COMPLETION = NORMAL]
$oc_review_stage(S_owned,OC_OUTPUT $ptascii("I;G;OWNED;"))
$lookup(S_owned.ENV,$ptascii("answer")) = (n_answer)
S_owned.STORE[n_answer] = DEFINED (POBJECT n_receiver)
$objectprops_at(S_owned.OBJECTPROPS,n_receiver) = (ppropertyslot_owned*)
$property_slot_at(ppropertyslot_owned*,ppropertydesc.KEY) = (ppropertyslot_value)
$heap_owners($heap_graph(S_owned),HOBJECT n_receiver) = 1
(HOBJECT n_receiver) <- S_owned.ALLOCATIONS
S_owned.STORE[n_reader] = DEFINED PNULL /\ S_owned.STORE[n_selector] = DEFINED pvalue_selector
S_receiver_found = $oc_review_seek(S_owned,OC_DTOR n_receiver,2000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
$oc_review_stage(S_receiver,OC_DTOR n_receiver)
$lookup(S_receiver.ENV,$ptascii("answer")) = eps
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
pdestructionoperation_receiver.SOURCE = UNSET (NExprVariable (BYTES text_answer) metadata_answer)
$base64(text_answer) = $ptascii("answer")
pdestructionoperation_receiver.VALUE = KNOWN PNULL /\ pdestructionoperation_receiver.PENDING = eps
$oc_review_output(S_receiver.EVENTS) = $ptascii("I;G;OWNED;")
S_done = $drive_steps(S_receiver,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
$oc_review_output(S_done.EVENTS) = $ptascii("I;G;OWNED;RECEIVER;DONE;")
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_selector
S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\ S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S,4096) = S_done
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: '
         '(ORIGIN_RETURN (porigin_parent)) :: '
         '(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*')
CASES = {
    'private-object-assignment-saved-name-and-answer-owner': {
        'source': ROWS[0]['source'],
        'stage': STAGE + ' -- if S.RESULT = KNOWN (POBJECT n_receiver)',
        'checks': OBJECT,
    },
    'private-array-assignment-receiver-first-payload-replacement': {
        'source': ROWS[1]['source'],
        'stage': STAGE + ' -- if S.RESULT = KNOWN (PARRAY n_array)',
        'checks': ARRAY,
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(binary_review.__file__), binary_review.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=binary_review.render)
