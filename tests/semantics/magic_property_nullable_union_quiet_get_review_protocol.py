#!/usr/bin/env python3
"""Check quiet scalar-union selection and nullable return cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_nullable_union_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''


dec $union_review_get_dtor(pstate,nat) : bool
def $union_review_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $union_review_get_dtor(S,n) = false -- otherwise
dec $union_review_get_seek_dtor(pstate,nat,nat) : pstate
def $union_review_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $union_review_get_seek_dtor(S,n_object,n) = S
  -- if $union_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $union_review_get_seek_dtor(S,n_object,0) = S
  -- if ~$union_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $union_review_get_seek_dtor(S,n_object,n) = $union_review_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$union_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $union_review_get_catch(pstate) : bool
def $union_review_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $union_review_get_catch(S) = false -- otherwise
dec $union_review_get_seek_catch(pstate,nat) : pstate
def $union_review_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $union_review_get_seek_catch(S,n) = S
  -- if $union_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $union_review_get_seek_catch(S,0) = S
  -- if ~$union_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $union_review_get_seek_catch(S,n) = $union_review_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$union_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $union_review_after(pstate,pstate) : pstate
def $union_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))


dec $union_review_result(pstate,nat) : bool
def $union_review_result(S,0) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
  -- if ppropertyempty.NAME = $ptascii("zero")
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))
def $union_review_result(S,1) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
  -- if ppropertycoalesce.NAME = $ptascii("zero")
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))
def $union_review_result(S,2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
  -- if ppropertyempty.NAME = $ptascii("false")
  -- if S.RESULT = KNOWN (PBOOL false)
def $union_review_result(S,3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
  -- if ppropertycoalesce.NAME = $ptascii("false")
  -- if S.RESULT = KNOWN (PBOOL false)
def $union_review_result(S,n) = false -- otherwise
dec $union_review_seek_result(pstate,nat,nat) : pstate
def $union_review_seek_result(S,n_stage,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $union_review_seek_result(S,n_stage,n) = S
  -- if $union_review_result(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $union_review_seek_result(S,n_stage,0) = S
  -- if ~$union_review_result(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $union_review_seek_result(S,n_stage,n) = $union_review_seek_result($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$union_review_result(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

UNION = ['S.ORIGIN = (porigin_return)',
 'z_return = 5 /\\ S.RESULT = KNOWN (PINT 0)',
 'n_receiver = ppropertyempty.OBJECT',
 'ppropertyempty.PROPERTY = eps /\\ ppropertyempty.NAME = $ptascii("zero")',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ORIGIN = ppropertyempty.GET',
 '$(|pfunction.SIGNATURE.RETURNS| = 2) /\\ "string" <- $ptmasks(pfunction.SIGNATURE.RETURNS) /\\ '
 '"false" <- $ptmasks(pfunction.SIGNATURE.RETURNS)',
 '$ppmethod_get_scalar_return(pfunction.SIGNATURE.RETURNS) /\\ ~pfunction.SIGNATURE.BYREF /\\ '
 '~pfunction.CODE.STRICT',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\\ pclassdesc.PARENT = eps',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NUnionType (SEQUENCE '
 '([NIdentifier (BYTES text_first) metadata_first, NIdentifier (BYTES text_second) metadata_second])) '
 'metadata_return)',
 '$ptlc($base64(text_first)) = $ptascii("string") /\\ $ptlc($base64(text_second)) = $ptascii("false")',
 '$ppmethod_get_scalar_union_source([NIdentifier (BYTES text_first) metadata_first, NIdentifier (BYTES '
 'text_second) metadata_second])',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
 '$ptype_normalize(NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first, NIdentifier '
 '(BYTES text_second) metadata_second])) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS '
 'eps',
 '$property_get_return_type_source(NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) '
 'metadata_first, NIdentifier (BYTES text_second) metadata_second])) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) '
 'metadata_first, NIdentifier (BYTES text_second) metadata_second])) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
 '$property_quiet_get_source(S,pmethoddesc) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$property_empty_method_source(S,pmethoddesc,true) /\\ '
 '$property_coalesce_method_source(S,pmethoddesc,true)',
 '~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
 '~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,false,false) = TYPESTRING (PINT 0)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,true,false) = TYPEREJECT',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL false,false,false) = TYPEVALUE (PBOOL '
 'false)',
 '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
 'S.FRAMES = [pframe]',
 'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertyempty.SITE)',
 'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
 '$property_empty_context(S,pcallcontext) /\\ '
 '$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("zero"))',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
 'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
 '$typed_return_task_valid(S,z_return) /\\ ~$typed_return_task_valid(S,$(z_return + 1))',
 'PhpStep: S ~> S_unwind',
 'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))) (porigin_return)) :: '
 'ptask_return*',
 'S_unwind.STORE = S.STORE /\\ S_unwind.EVENTS = S.EVENTS',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one[.COMPLETION = NORMAL] = $union_review_after(S,S_unwind)',
 'S_result_found = $union_review_seek_result(S_one[.COMPLETION = NORMAL],0,2000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_result*',
 'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))',
 '$property_magic_cv_source(S_result,ppropertyempty.SITE,ppropertyempty.LINE)',
 '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,S_result.RESULT)',
 '~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,false,S_result.RESULT)',
 '$property_empty_truth(S_result,PSTRING_CARRIER INTERNED_STRING ([48])) = (true)',
 '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2 /\\ '
 '$property_empty_guard(S_result,n_receiver,ppropertyempty.NAME)',
 'PhpStep: S_result ~> S_truth',
 'S_truth.TODO = ptask_result* /\\ S_truth.RESULT = KNOWN (PBOOL true)',
 '$heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1 /\\ '
 '~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME)',
 'S_truth_public = $union_review_after(S_result,S_truth)',
 'S_string_found = $union_review_seek_result(S_truth_public,1,2000)',
 'S_string_found.COMPLETION = NORMAL \\/ S_string_found.COMPLETION = BUDGET',
 'S_string = S_string_found[.COMPLETION = NORMAL]',
 'S_string.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce_string true) :: (ORIGIN_RETURN '
 '(porigin_string)) :: (COALESCE_QUIET expression_string_right z_string_left z_string_right) :: '
 'ptask_string*',
 'S_string.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))',
 'ppropertycoalesce_string.OBJECT = n_receiver /\\ ppropertycoalesce_string.NAME = $ptascii("zero")',
 '$property_coalesce_valid(S_string,ppropertycoalesce_string) /\\ '
 '$property_magic_cv_source(S_string,ppropertycoalesce_string.SITE,ppropertycoalesce_string.LINE)',
 '$heap_owners($heap_graph(S_string),HOBJECT n_receiver) = 2',
 'PhpStep: S_string ~> S_string_value',
 'S_string_value.TODO = (ORIGIN_RETURN (porigin_string)) :: (COALESCE_RESULT expression_string_right '
 'z_string_left z_string_right) :: ptask_string*',
 'S_string_value.RESULT = S_string.RESULT /\\ S_string_value.EVENTS = S_string.EVENTS',
 '$heap_owners($heap_graph(S_string_value),HOBJECT n_receiver) = 1',
 'S_string_public = $union_review_after(S_string,S_string_value)',
 'S_false_found = $union_review_seek_result(S_string_public,2,2000)',
 'S_false_found.COMPLETION = NORMAL \\/ S_false_found.COMPLETION = BUDGET',
 'S_false = S_false_found[.COMPLETION = NORMAL]',
 'S_false.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_false true) :: ptask_false*',
 'S_false.RESULT = KNOWN (PBOOL false) /\\ ppropertyempty_false.OBJECT = n_receiver /\\ '
 'ppropertyempty_false.NAME = $ptascii("false")',
 '$property_empty_valid(S_false,ppropertyempty_false) /\\ $property_empty_truth(S_false,PBOOL false) = '
 '(true)',
 '$lookup(S_false.ENV,$ptascii("answer")) = (n_answer)',
 'S_false.STORE[n_answer] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([48]))',
 '$heap_owners($heap_graph(S_false),HOBJECT n_receiver) = 2',
 'S_false.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY_ZERO;"),OUTPUT '
 '$ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("STRING_ZERO;"),OUTPUT $ptascii("I;"),OUTPUT '
 '$ptascii("G;")]',
 'PhpStep: S_false ~> S_false_truth',
 'S_false_truth.TODO = ptask_false* /\\ S_false_truth.RESULT = KNOWN (PBOOL true)',
 '$heap_owners($heap_graph(S_false_truth),HOBJECT n_receiver) = 1',
 'S_false_public = $union_review_after(S_false,S_false_truth)',
 'S_keep_found = $union_review_seek_result(S_false_public,3,2000)',
 'S_keep_found.COMPLETION = NORMAL \\/ S_keep_found.COMPLETION = BUDGET',
 'S_keep = S_keep_found[.COMPLETION = NORMAL]',
 'S_keep.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce_false true) :: (ORIGIN_RETURN '
 '(porigin_false)) :: (COALESCE_QUIET expression_false_right z_false_left z_false_right) :: ptask_keep*',
 'S_keep.RESULT = KNOWN (PBOOL false) /\\ ppropertycoalesce_false.OBJECT = n_receiver /\\ '
 'ppropertycoalesce_false.NAME = $ptascii("false")',
 '$property_coalesce_valid(S_keep,ppropertycoalesce_false) /\\ '
 '$property_magic_cv_source(S_keep,ppropertycoalesce_false.SITE,ppropertycoalesce_false.LINE)',
 'S_keep.STORE[n_answer] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([48])) /\\ '
 '$heap_owners($heap_graph(S_keep),HOBJECT n_receiver) = 2',
 'PhpStep: S_keep ~> S_keep_value',
 'S_keep_value.TODO = (ORIGIN_RETURN (porigin_false)) :: (COALESCE_RESULT expression_false_right '
 'z_false_left z_false_right) :: ptask_keep*',
 'S_keep_value.RESULT = KNOWN (PBOOL false) /\\ S_keep_value.EVENTS = S_keep.EVENTS',
 '$heap_owners($heap_graph(S_keep_value),HOBJECT n_receiver) = 1',
 'S_keep_public = $union_review_after(S_keep,S_keep_value)',
 'S_done = $drive_steps(S_keep_public,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY_ZERO;"),OUTPUT '
 '$ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("STRING_ZERO;"),OUTPUT $ptascii("I;"),OUTPUT '
 '$ptascii("G;"),OUTPUT $ptascii("EMPTY_FALSE;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT '
 '$ptascii("FALSE;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALL;"),OUTPUT '
 '$ptascii("RECEIVER;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_answer] = DEFINED (PBOOL false)',
 'S_done.STORE[n_selector] = DEFINED pvalue_missing_selector',
 '$string_bytes(pvalue_missing_selector) = ($ptascii("missing"))',
 '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done']

STRICT_ERROR = ['$call_task_valid(S,RETURN_VALUE z_return) /\\ z_return = 10',
 'S.RESULT = KNOWN (PINT 1)',
 'ppropertycoalesce.PROPERTY = eps /\\ ppropertycoalesce.NAME = $ptascii("gone")',
 'n_receiver = ppropertycoalesce.OBJECT',
 'S.OBJECTS[n_receiver] = INSTANCE ppropertycoalesce.CLASS',
 '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ENDLINE = 11',
 '$(|pfunction.SIGNATURE.RETURNS| = 2) /\\ "string" <- $ptmasks(pfunction.SIGNATURE.RETURNS) /\\ "null" '
 '<- $ptmasks(pfunction.SIGNATURE.RETURNS) /\\ ~pfunction.SIGNATURE.BYREF',
 'pfunction.DEFAULTS = eps /\\ pfunction.CODE.STRICT',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertycoalesce.CLASS',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous")',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NNullableType (NIdentifier '
 '(BYTES text_return) metadata_return) metadata_nullable)',
 '$ptlc($base64(text_return)) = $ptascii("string")',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
 '$ptype_normalize(NNullableType (NIdentifier (BYTES text_return) metadata_return) '
 'metadata_nullable,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
 '$property_get_return_type_source(NNullableType (NIdentifier (BYTES text_return) metadata_return) '
 'metadata_nullable,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NNullableType (NIdentifier (BYTES text_return) metadata_return) '
 'metadata_nullable,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
 '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 1,true,false) = TYPEREJECT',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 1,false,false) = TYPESTRING (PINT 1)',
 '$property_coalesce_method_source(S,pmethoddesc,true) /\\ '
 '~$property_coalesce_method_source(S,pmethoddesc,false)',
 '~$property_coalesce_method_source(S[.SOURCES = eps],pmethoddesc,true)',
 '~$property_coalesce_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
 '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
 '$c_string(pfunction.NAME) = $ptascii("class@anonymous")',
 '$return_function_name(S,pfunction[.ENDLINE = 99]) = pfunction.NAME',
 'pcallcontext_bad = pcallcontext[.FUNCTION = ppropertycoalesce.ISSET]',
 '$return_function_name(S[.CURRENT = (pcallcontext_bad)],pfunction) = pfunction.NAME',
 'pcallcontext_isset = pcallcontext[.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce false]',
 '$return_function_name(S[.CURRENT = (pcallcontext_isset)],pfunction) = $call_function_name(S[.CURRENT '
 '= (pcallcontext_isset)],pfunction)',
 'S.FRAMES = [pframe]',
 'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertycoalesce.SITE)',
 'pframe.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_caller*',
 '~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME)',
 '$property_coalesce_context(S,pcallcontext)',
 '$property_coalesce_entered(S,S.CURRENT,S.FRAMES,ppropertycoalesce,true)',
 '$property_empty_get_active(S,n_receiver,ppropertycoalesce.NAME)',
 '$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
 '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ '
 '$call_receiver_roots(pcallcontext) = eps',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$property_coalesce_valid(S_caller,ppropertycoalesce) /\\ '
 '~$property_coalesce_capture(S_caller,ppropertycoalesce)',
 '~$property_coalesce_valid(S_caller,ppropertycoalesce[.LINE = $(ppropertycoalesce.LINE + 1)])',
 '~$property_coalesce_valid(S_caller[.SOURCES = eps],ppropertycoalesce)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("gone"))',
 '$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN '
 'PNULL)',
 '$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN '
 '(PINT 0))',
 '~$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,KNOWN '
 '(PINT 0))',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_graph(S))',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET',
 'S_receiver_found = $union_review_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 '$union_review_get_dtor(S_receiver,n_receiver)',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = '
 '(pdestructorcall_receiver)',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.PENDING = (n_type_error)',
 'pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_type_error',
 'pdestructionoperation_receiver.VALUE = KNOWN PNULL',
 'S_receiver.OBJECTS[n_type_error] = THROWABLE pthrowable_type_error',
 'pthrowable_type_error.KIND = "TypeError"',
 '$string_bytes($throwable_field(S_receiver,n_type_error,"message")) = '
 '($ptascii("class@anonymous::__get(): Return value must be of type ?string, int returned"))',
 '$throwable_field(S_receiver,n_type_error,"line") = PINT 10',
 '$throwable_field(S_receiver,n_type_error,"previous") = PNULL',
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertycoalesce.NAME)',
 'S_receiver.EVENTS = S.EVENTS',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_catch_found = $union_review_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_type_error',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("receiver-nullable"))',
 'S_catch.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
 '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ (HOBJECT n_type_error) <- S_bound.ALLOCATIONS',
 '~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("receiver-nullable"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("class@anonymous::__get(): Return value must be of type ?string, int '
 'returned"),OUTPUT $ptascii(";"),OUTPUT $ptascii("10"),OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42)',
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps',
 '~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_type_error) <- '
 'S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_catch,4096) = S_done',
 '$drive_steps(S_receiver,4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done',
 '~$property_isset_guard(S_receiver,S_receiver.CURRENT,S_receiver.FRAMES,n_receiver,ppropertycoalesce.NAME)']

CASES = {
    'weak-string-false-get-conversion-and-quiet-results': {
        'source': ROWS[0]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true -- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* -- if S.RESULT = KNOWN (PINT 0)',
        'checks': UNION,
    },
    'strict-nullable-string-get-int-error-pending-cleanup': {
        'source': ROWS[1]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true -- if S.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        'checks': STRICT_ERROR,
    },
}

def render(case, fixture, filename):
    stage = case['stage']
    text = (HELPERS + '\ndec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + stage + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate,nat) : pstate\n'
            'def $seek(S,n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'def $seek(S,n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) '
            '-- if $(n > 0) /\\ ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found = $seek(S_initial,2000)\n'
            '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            '  -- if S = S_found[.COMPLETION = NORMAL]\n'
            '  -- if ' + stage + '\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__),CATALOGUE),runner_flags=('--sl',),fixture_renderer=render)
