#!/usr/bin/env python3
"""Check exact mixed returns, missing-return cleanup and the owned-RV fence."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_mixed_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''


dec $mixed_review_get_dtor(pstate,nat) : bool
def $mixed_review_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $mixed_review_get_dtor(S,n) = false -- otherwise
dec $mixed_review_get_seek_dtor(pstate,nat,nat) : pstate
def $mixed_review_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $mixed_review_get_seek_dtor(S,n_object,n) = S
  -- if $mixed_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_get_seek_dtor(S,n_object,0) = S
  -- if ~$mixed_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_get_seek_dtor(S,n_object,n) = $mixed_review_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$mixed_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $mixed_review_get_catch(pstate) : bool
def $mixed_review_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $mixed_review_get_catch(S) = false -- otherwise
dec $mixed_review_get_seek_catch(pstate,nat) : pstate
def $mixed_review_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $mixed_review_get_seek_catch(S,n) = S
  -- if $mixed_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_get_seek_catch(S,0) = S
  -- if ~$mixed_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_get_seek_catch(S,n) = $mixed_review_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$mixed_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $mixed_review_after(pstate,pstate) : pstate
def $mixed_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))

dec $mixed_review_coalesce(pstate) : bool
def $mixed_review_coalesce(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
def $mixed_review_coalesce(S) = false -- otherwise
dec $mixed_review_seek_coalesce(pstate,nat) : pstate
def $mixed_review_seek_coalesce(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $mixed_review_seek_coalesce(S,n) = S
  -- if $mixed_review_coalesce(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_seek_coalesce(S,0) = S
  -- if ~$mixed_review_coalesce(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_seek_coalesce(S,n) = $mixed_review_seek_coalesce($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$mixed_review_coalesce(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $mixed_review_request(pstate) : bool
def $mixed_review_request(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_text) ptbytes)
  -- if ptbytes = $ptascii("ab")
def $mixed_review_request(S) = false -- otherwise
dec $mixed_review_seek_request(pstate,nat) : pstate
def $mixed_review_seek_request(S,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $mixed_review_seek_request(S,n) = S -- if $mixed_review_request(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_seek_request(S,0) = S -- if ~$mixed_review_request(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mixed_review_seek_request(S,n) = $mixed_review_seek_request($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$mixed_review_request(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

EXACT = ['S.ORIGIN = (porigin_return)',
 'z_return = 6',
 'n_receiver = ppropertyempty.OBJECT',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ORIGIN = ppropertyempty.GET',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))] /\\ ~pfunction.SIGNATURE.BYREF /\\ '
 'pfunction.CODE.STRICT /\\ pfunction.ENDLINE = 6',
 'pfunction.SIGNATURE.PARAMETERS = [psparam]',
 'psparam.TYPE = eps /\\ psparam.REQUIRED /\\ ~psparam.BYREF /\\ ~psparam.VARIADIC',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\\ pclassdesc.PARENT = eps',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES '
 'text_return) metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("mixed")',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE '
 'eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) '
 'metadata_parameter) ABSENT (SEQUENCE eps) metadata_param)',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK '
 'pfunction.SIGNATURE.RETURNS eps',
 '$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
 '$property_quiet_get_source(S,pmethoddesc) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
 '~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
 'S.RESULT = VARIABLE $ptascii("sample") 6',
 'S_read = $resolve_at(S,S.RESULT,z_return)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 0)',
 'S_read.STORE = S.STORE /\\ S_read.EVENTS = S.EVENTS',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,true,false) = TYPEVALUE (PINT 0)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,false,false) = TYPEVALUE (PINT 0)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,true,false) = TYPEVALUE (PBOOL '
 'true)',
 'S.FRAMES = [pframe]',
 'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
 '$property_empty_context(S,pcallcontext) /\\ $typed_return_task_valid(S,z_return)',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("sample")) = (n_sample)',
 '$lookup(S.ENV,$ptascii("sample")) = (n_sample)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\\ S.STORE[n_sample] = DEFINED (PINT 0)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("value"))',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
 'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
 'PhpStep: S ~> S_unwind',
 'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PINT 0)) (porigin_return)) :: ptask_return*',
 'S_unwind.STORE = S.STORE /\\ S_unwind.EVENTS = S.EVENTS /\\ S_unwind.STRINGDATA = S.STRINGDATA',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one[.COMPLETION = NORMAL] = $mixed_review_after(S,S_unwind)',
 'S_request_found = $mixed_review_seek_request(S_one[.COMPLETION = NORMAL],4000)',
 'S_request_found.COMPLETION = NORMAL \\/ S_request_found.COMPLETION = BUDGET',
 'S_request = S_request_found[.COMPLETION = NORMAL]',
 'S_request.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN '
 '(porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_request*',
 'S_request.RESULT = KNOWN pvalue_request',
 'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_text) ptbytes_text',
 'ptbytes_text = $ptascii("ab") /\\ $(n_text < |S_request.STRINGDATA|) /\\ S_request.STRINGDATA[n_text] '
 '= ptbytes_text',
 '$string_carrier_valid(S_request,pvalue_request) /\\ $value_nodes(pvalue_request) = eps',
 'ppropertycoalesce.OBJECT = n_receiver /\\ ppropertycoalesce.LINE = 20',
 '$property_coalesce_valid(S_request,ppropertycoalesce) /\\ '
 '$property_magic_cv_source(S_request,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
 '$property_magic_cv_result_supported(S_request,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S_request.RESULT)',
 '~$property_magic_cv_result_supported(S_request,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S_request.RESULT)',
 '~$property_coalesce_valid(S_request[.SOURCES = eps],ppropertycoalesce)',
 '$lookup(S_request.ENV,$ptascii("answer")) = (n_answer)',
 'S_request.STORE[n_answer] = DEFINED (PBOOL true) /\\ S_request.STORE[n_sample] = DEFINED '
 'pvalue_request',
 'n_sample <- S_request.REFCELLS /\\ $heap_owners($heap_graph(S_request),HOBJECT n_receiver) = 2',
 'S_request.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY_INT;"),OUTPUT '
 '$ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("INT;"),OUTPUT $ptascii("I;"),OUTPUT '
 '$ptascii("G;"),OUTPUT $ptascii("NONEMPTY_BOOL;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT '
 '$ptascii("TRUE;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
 'PhpStep: S_request ~> S_value_raw',
 'S_value_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left '
 'z_right) :: ptask_request*',
 'S_value_raw.RESULT = KNOWN pvalue_request /\\ S_value_raw.STRINGDATA = S_request.STRINGDATA /\\ '
 'S_value_raw.EVENTS = S_request.EVENTS',
 '$heap_owners($heap_graph(S_value_raw),HOBJECT n_receiver) = 1',
 'S_request_zero = $drive_steps(S_request,0)',
 'S_request_zero = S_request[.COMPLETION = BUDGET]',
 'S_request_one = $drive_steps(S_request_zero[.COMPLETION = NORMAL],1)',
 'S_request_one.COMPLETION = BUDGET /\\ S_request_one[.COMPLETION = NORMAL] = '
 '$mixed_review_after(S_request,S_value_raw)',
 'S_request_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT '
 'pdestructionoperation) :: S_value_raw.TODO',
 'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]',
 'pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true',
 'pdestructionoperation.VALUE = KNOWN pvalue_request /\\ pdestructionoperation.PENDING = eps',
 '$heap_owners($heap_graph(S_request_one),HOBJECT n_receiver) = 2',
 'S_ready_found = $drive_steps(S_request_one[.COMPLETION = NORMAL],3)',
 'S_ready_found.COMPLETION = BUDGET',
 'S_ready = S_ready_found[.COMPLETION = NORMAL]',
 'S_ready.TODO = S_value_raw.TODO /\\ S_ready.RESULT = KNOWN pvalue_request',
 '$heap_owners($heap_graph(S_ready),HOBJECT n_receiver) = 1 /\\ S_ready.EVENTS = S_request.EVENTS',
 'S_done = $drive_steps(S_ready,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.EVENTS = S_request.EVENTS ++ [OUTPUT $ptascii("COPY;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT '
 '$ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_answer] = DEFINED pvalue_request /\\ '
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 'S_done.STORE[n_sample] = DEFINED pvalue_changed',
 '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
 'S_done.STRINGDATA[n_text] = ptbytes_text /\\ $string_carrier_valid(S_done,pvalue_request)',
 '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_request_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done']

FALLTHROUGH = ['n_receiver = ppropertycoalesce.OBJECT',
 'ppropertycoalesce.PROPERTY = eps /\\ ppropertycoalesce.NAME = $ptascii("gone")',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = porigin_method /\\ pfunction.ORIGIN = pcallcontext.FUNCTION /\\ '
 'ppropertycoalesce.GET = (pfunction.ORIGIN)',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))] /\\ ~pfunction.SIGNATURE.BYREF /\\ '
 '~pfunction.CODE.STRICT',
 'pfunction.DEFAULTS = eps /\\ pfunction.ENDLINE = 8',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\\ pclassdesc.PARENT = eps /\\ '
 'pclassdesc.ORIGIN = ppropertycoalesce.CLASS',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES '
 'text_return) metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("mixed")',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK '
 'pfunction.SIGNATURE.RETURNS eps',
 '$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
 '$property_quiet_get_source(S,pmethoddesc) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$property_empty_method_source(S,pmethoddesc,true) /\\ '
 '~$property_empty_method_source(S,pmethoddesc,false)',
 '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
 '~$property_get_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
 '$typed_fallthrough(pfunction) = TYPE_FALLTHROUGH porigin_method',
 '$call_task_valid(S,TYPE_FALLTHROUGH porigin_method) /\\ ~$call_task_valid(S,TYPE_FALLTHROUGH '
 'ppropertycoalesce.SITE)',
 '$call_function_kind(S) = $ptascii("method")',
 '$call_function_kind(S[.CURRENT = (pcallcontext[.FUNCTION = ppropertycoalesce.ISSET])]) = '
 '$ptascii("function")',
 '$call_function_kind(S[.CURRENT = (pcallcontext[.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce '
 'false])]) = $ptascii("function")',
 '$call_function_kind(S[.SOURCES = eps]) = $ptascii("function")',
 '$call_function_name(S,pfunction) = pfunction.NAME /\\ 0 <- pfunction.NAME',
 '$c_string($call_function_name(S,pfunction)) = $ptascii("class@anonymous")',
 '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
 'S.FRAMES = [pframe]',
 'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertycoalesce.SITE)',
 'pframe.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_caller*',
 '$property_coalesce_context(S,pcallcontext) /\\ '
 '$property_empty_get_active(S,n_receiver,ppropertycoalesce.NAME)',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("gone"))',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
 '$call_receiver_roots(pcallcontext) = eps /\\ $target_nodes(pcallcontext.TARGET) = eps',
 '$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_graph(S))',
 'preqbytes_message = $ptascii("class@anonymous::__get(): Return value must be of type mixed, none '
 'returned")',
 'S_error = S[.COMPLETION = THROWN "TypeError" preqbytes_message 8]',
 'PhpStep: S ~> S_error',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET',
 'S_one.TODO = (THROW_SEARCH n_type_error) :: ptask_throw*',
 'S_one.OBJECTS[n_type_error] = THROWABLE pthrowable_type',
 'pthrowable_type.KIND = "TypeError"',
 '$string_bytes($throwable_field(S_one,n_type_error,"message")) = (preqbytes_message)',
 '$throwable_field(S_one,n_type_error,"line") = PINT 8 /\\ '
 '$throwable_field(S_one,n_type_error,"previous") = PNULL',
 'S_one.CURRENT = S.CURRENT /\\ S_one.FRAMES = S.FRAMES /\\ S_one.EVENTS = S.EVENTS',
 'S_one.STORE[n_destination] = DEFINED (PINT 42) /\\ S_one.STORE[n_reader] = DEFINED PNULL',
 '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
 'S_receiver_found = $mixed_review_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = '
 '(pdestructorcall_receiver)',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.PENDING = (n_type_error)',
 'pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_type_error /\\ '
 'pdestructionoperation_receiver.VALUE = KNOWN PNULL',
 '$throwable_field(S_receiver,n_type_error,"previous") = PNULL',
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertycoalesce.NAME)',
 'S_receiver.EVENTS = S.EVENTS /\\ S_receiver.STORE[n_destination] = DEFINED (PINT 42)',
 'S_catch_found = $mixed_review_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_type_error',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = '
 '($ptascii("receiver-mixed-none"))',
 'S_catch.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound_raw',
 'S_bound = $mixed_review_after(S_catch,S_bound_raw)',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
 '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ (HOBJECT n_type_error) <- S_bound.ALLOCATIONS',
 '~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT '
 '$ptascii("receiver-mixed-none"),OUTPUT $ptascii(";"),OUTPUT preqbytes_message,OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("8"),OUTPUT $ptascii(";"),OUTPUT $ptascii("ROOT;"),OUTPUT '
 '$ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42) /\\ '
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps',
 '~((HOBJECT n_type_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_receiver_error) <- '
 'S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_catch,4096) = S_done',
 '$drive_steps(S_receiver,4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done']

OBJECT_SOURCE = '<?php\nclass MixedObjectBoundary {\n    public function __isset(string $incoming): bool { echo "I;"; return true; }\n    public function __get(string $incoming): mixed { echo "G;"; return $this; }\n}\n$reader = new MixedObjectBoundary;\n$selector = "value";\necho empty($reader->$selector) ? "BAD_EMPTY;" : "OBJECT;";\necho "DONE;";\n'
OBJECT_SOURCE_SHA256 = '22e4c6fca2432d8a764d888aad694fb17a1be77041f3b4acb9f4dd743b7ee324'
assert hashlib.sha256(OBJECT_SOURCE.encode()).hexdigest() == OBJECT_SOURCE_SHA256

OBJECT_CONTROL = ['S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
 'n_receiver = ppropertyempty.OBJECT',
 'S.RESULT = KNOWN (POBJECT n_receiver)',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))] /\\ ~pfunction.SIGNATURE.BYREF',
 '$property_quiet_get_source(S,pmethoddesc) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$property_empty_valid(S,ppropertyempty) /\\ '
 '$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
 '$property_empty_rv_kind(S,S.OBJECTS[n_receiver])',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
 '~$property_empty_rv_ready(S,ppropertyempty)',
 '$value_nodes(POBJECT n_receiver) = [HOBJECT n_receiver]',
 '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 3',
 '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
 'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
 'PhpStep: S ~> S_raw',
 'S_raw.COMPLETION = UNSUPPORTED "CV-name magic empty getter result"',
 'S_raw.TODO = S.TODO /\\ S_raw.RESULT = S.RESULT /\\ S_raw.EVENTS = S.EVENTS /\\ S_raw.STORE = S.STORE',
 'S_done = $drive_steps(S,64)',
 'S_done.COMPLETION = UNSUPPORTED "CV-name magic empty getter result" /\\ S_done.TODO = eps',
 'S_done.BASE = BASE_VALUE (KNOWN PNULL)',
 'S_done.EVENTS = S.EVENTS /\\ S_done.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
 '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
 '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))']

CASES = {
    'strict-mixed-get-exact-int-and-request-snapshot': {
        'source': ROWS[0]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true -- if S.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        'checks': EXACT,
    },
    'mixed-get-missing-return-and-receiver-replacement': {
        'source': ROWS[1]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true -- if S.TODO = (TYPE_FALLTHROUGH porigin_method) :: ptask_return*',
        'checks': FALLTHROUGH,
    },
    'mixed-get-live-object-cv-result-refusal': {
        'source': OBJECT_SOURCE,
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_receiver)',
        'checks': OBJECT_CONTROL,
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
