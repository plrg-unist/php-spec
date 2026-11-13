#!/usr/bin/env python3
"""Check quiet void delivery and implicit-never last-owner cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_void_never_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''


dec $bottom_review_get_dtor(pstate,nat) : bool
def $bottom_review_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $bottom_review_get_dtor(S,n) = false -- otherwise
dec $bottom_review_get_seek_dtor(pstate,nat,nat) : pstate
def $bottom_review_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bottom_review_get_seek_dtor(S,n_object,n) = S
  -- if $bottom_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bottom_review_get_seek_dtor(S,n_object,0) = S
  -- if ~$bottom_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bottom_review_get_seek_dtor(S,n_object,n) = $bottom_review_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$bottom_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $bottom_review_get_catch(pstate) : bool
def $bottom_review_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $bottom_review_get_catch(S) = false -- otherwise
dec $bottom_review_get_seek_catch(pstate,nat) : pstate
def $bottom_review_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bottom_review_get_seek_catch(S,n) = S
  -- if $bottom_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bottom_review_get_seek_catch(S,0) = S
  -- if ~$bottom_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bottom_review_get_seek_catch(S,n) = $bottom_review_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$bottom_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $bottom_review_after(pstate,pstate) : pstate
def $bottom_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))

dec $bottom_review_coalesce(pstate) : bool
def $bottom_review_coalesce(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
def $bottom_review_coalesce(S) = false -- otherwise
dec $bottom_review_seek_coalesce(pstate,nat) : pstate
def $bottom_review_seek_coalesce(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bottom_review_seek_coalesce(S,n) = S
  -- if $bottom_review_coalesce(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bottom_review_seek_coalesce(S,0) = S
  -- if ~$bottom_review_coalesce(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bottom_review_seek_coalesce(S,n) = $bottom_review_seek_coalesce($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$bottom_review_coalesce(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

VOID = ['S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps /\\ S.ORIGIN = (ppropertyempty.SITE)',
 'S.RESULT = KNOWN PNULL /\\ ppropertyempty.PROPERTY = eps /\\ ppropertyempty.NAME = $ptascii("value") '
 '/\\ ppropertyempty.LINE = 9',
 'n_receiver = ppropertyempty.OBJECT',
 '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
 'pfunction_get = pmethoddesc_get.FUNCTION',
 'ppropertyempty.GET = pfunction_get.ORIGIN',
 'pfunction_get.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))] /\\ '
 '~pfunction_get.SIGNATURE.BYREF /\\ pfunction_get.ENDLINE = 5',
 'pfunction_get.ORIGIN = PORIGIN n_unit pcpath_method',
 '$class_at(S.CLASSES,pmethoddesc_get.OWNER) = (pclassdesc_get)',
 '$c_string(pclassdesc_get.NAME) = $ptascii("class@anonymous")',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES '
 'text_return) metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("void")',
 'ptcontext = {NAMESPACE pfunction_get.ENV.NAMESPACE, IMPORTS pfunction_get.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc_get.NAME eps, POSITION PTRETURN, OWNER pclassdesc_get.NAME, MEMBER pmethoddesc_get.NAME, '
 'FILE $call_sourcefile(S.FILES,pfunction_get.ORIGIN), LINE pfunction_get.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK '
 'pfunction_get.SIGNATURE.RETURNS eps',
 '$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction_get.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction_get.SIGNATURE.RETURNS,ptcontext,false)',
 '$ppmethod_get_decl_return(pfunction_get.SIGNATURE.RETURNS) /\\ '
 '~$ppmethod_get_scalar_return(pfunction_get.SIGNATURE.RETURNS)',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 6,PCINDEX 3])) = (NStmtReturn ABSENT '
 'metadata_bare)',
 '$source_line(metadata_bare) = 5',
 '$property_get_method_source(S,pmethoddesc_get,true) /\\ '
 '~$property_empty_get_source(S,pmethoddesc_get)',
 '$property_quiet_get_source(S,pmethoddesc_get) /\\ '
 '$property_empty_method_source(S,pmethoddesc_get,true) /\\ '
 '$property_coalesce_method_source(S,pmethoddesc_get,true)',
 '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc_get,true)',
 '~$property_get_method_source(S,pmethoddesc_get[.FUNCTION = pfunction_get[.ENDLINE = 99]],true)',
 '$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN PNULL)',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN PNULL)',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT '
 'n_receiver))',
 '~$property_magic_cv_source(S,ppropertyempty.SITE,$(ppropertyempty.LINE + 1))',
 '~$property_empty_valid(S[.SOURCES = eps],ppropertyempty)',
 '$property_empty_truth(S,PNULL) = (true)',
 '$property_empty_guard(S,n_receiver,ppropertyempty.NAME)',
 '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("value"))',
 '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
 'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
 '$call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true) /\\ $call_descriptors_valid(S) /\\ '
 '$property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
 'PhpStep: S ~> S_truth',
 'S_truth.TODO = ptask_empty* /\\ S_truth.RESULT = KNOWN (PBOOL true) /\\ S_truth.BASE = BASE_VALUE '
 '(KNOWN PNULL)',
 'S_truth.STORE = S.STORE /\\ S_truth.EVENTS = S.EVENTS',
 '$heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1 /\\ '
 '~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME)',
 'S_after_truth = $bottom_review_after(S,S_truth)',
 'S_coalesce_found = $bottom_review_seek_coalesce(S_after_truth,2000)',
 'S_coalesce_found.COMPLETION = NORMAL \\/ S_coalesce_found.COMPLETION = BUDGET',
 'S_coalesce = S_coalesce_found[.COMPLETION = NORMAL]',
 'S_coalesce.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN '
 '(porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_caller*',
 'S_coalesce.RESULT = KNOWN PNULL /\\ S_coalesce.BASE = BASE_VALUE (KNOWN PNULL)',
 'S_coalesce.CURRENT = eps /\\ S_coalesce.FRAMES = eps /\\ S_coalesce.ORIGIN = (ppropertycoalesce.SITE)',
 'ppropertycoalesce.OBJECT = n_receiver /\\ ppropertycoalesce.NAME = eps /\\ ppropertycoalesce.LINE = '
 '12',
 'ppropertycoalesce.GET = (pfunction_get.ORIGIN)',
 '$property_coalesce_valid(S_coalesce,ppropertycoalesce) /\\ '
 '$property_magic_cv_source(S_coalesce,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
 '$property_magic_cv_result_supported(S_coalesce,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S_coalesce.RESULT)',
 '~$property_magic_cv_result_supported(S_coalesce,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S_coalesce.RESULT)',
 '~$property_coalesce_valid(S_coalesce[.SOURCES = eps],ppropertycoalesce)',
 '$lookup(S_coalesce.ENV,$ptascii("answer")) = (n_answer)',
 'S_coalesce.STORE[n_reader] = DEFINED PNULL /\\ S_coalesce.STORE[n_answer] = DEFINED (PINT 42)',
 'S_coalesce.STORE[n_selector] = DEFINED pvalue_empty_selector',
 '$string_bytes(pvalue_empty_selector) = (eps)',
 '$heap_owners($heap_graph(S_coalesce),HOBJECT n_receiver) = 1',
 '~$property_empty_get_active(S_coalesce,n_receiver,ppropertycoalesce.NAME)',
 'S_coalesce.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("I;"),OUTPUT '
 '$ptascii("G;")]',
 'PhpStep: S_coalesce ~> S_value_raw',
 'S_value_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left '
 'z_right) :: ptask_caller*',
 'S_value_raw.RESULT = KNOWN PNULL /\\ S_value_raw.BASE = BASE_VALUE (KNOWN PNULL)',
 'S_value_raw.STORE = S_coalesce.STORE /\\ S_value_raw.EVENTS = S_coalesce.EVENTS',
 '$heap_owners($heap_graph(S_value_raw),HOBJECT n_receiver) = 0',
 'S_zero = $drive_steps(S_coalesce,0)',
 'S_zero = S_coalesce[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one[.COMPLETION = NORMAL] = '
 '$bottom_review_after(S_coalesce,S_value_raw)',
 'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT '
 'pdestructionoperation) :: S_value_raw.TODO',
 'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]',
 'pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true',
 'pdestructionoperation.PENDING = eps /\\ pdestructionoperation.VALUE = KNOWN PNULL',
 '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
 'S_receiver_found = $bottom_review_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = '
 '(pdestructorcall_receiver)',
 'pdestructorcall_receiver.OBJECT = n_receiver',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true',
 'pdestructionoperation_receiver.PENDING = eps /\\ pdestructionoperation_receiver.VALUE = KNOWN PNULL',
 'S_receiver.EVENTS = S_coalesce.EVENTS /\\ S_receiver.STORE[n_answer] = DEFINED (PINT 42)',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_done = $drive_steps(S_receiver,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.EVENTS = S_coalesce.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("RHS;"),OUTPUT '
 '$ptascii("FALL;"),OUTPUT $ptascii("CLEARED;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_answer] = DEFINED (PINT 9) /\\ '
 'S_done.STORE[n_selector] = DEFINED pvalue_empty_selector',
 '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_coalesce,4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done']

NEVER = ['n_receiver = ppropertyempty.OBJECT',
 'ppropertyempty.PROPERTY = eps /\\ ppropertyempty.NAME = $ptascii("gone")',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = porigin_method /\\ pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ORIGIN = '
 'ppropertyempty.GET',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))] /\\ ~pfunction.SIGNATURE.BYREF /\\ '
 '~pfunction.CODE.STRICT',
 'pfunction.DEFAULTS = eps /\\ pfunction.ENDLINE = 8',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\\ pclassdesc.PARENT = eps /\\ '
 'pclassdesc.ORIGIN = ppropertyempty.CLASS',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES '
 'text_return) metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("never")',
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
 'ppropertyempty.SITE)',
 '$call_function_kind(S) = $ptascii("method")',
 '$call_function_kind(S[.CURRENT = (pcallcontext[.FUNCTION = ppropertyempty.ISSET])]) = '
 '$ptascii("function")',
 '$call_function_kind(S[.CURRENT = (pcallcontext[.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty '
 'false])]) = $ptascii("function")',
 '$call_function_kind(S[.SOURCES = eps]) = $ptascii("function")',
 '$call_function_name(S,pfunction) = pfunction.NAME /\\ 0 <- pfunction.NAME',
 '$c_string($call_function_name(S,pfunction)) = $ptascii("class@anonymous")',
 '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
 'S.FRAMES = [pframe]',
 'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertyempty.SITE)',
 'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
 '$property_empty_context(S,pcallcontext) /\\ '
 '$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("gone"))',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
 '$call_receiver_roots(pcallcontext) = eps /\\ $target_nodes(pcallcontext.TARGET) = eps',
 '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_graph(S))',
 'preqbytes_message = $ptascii("class@anonymous(): never-returning method must not implicitly return")',
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
 'S_receiver_found = $bottom_review_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
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
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertyempty.NAME)',
 'S_receiver.EVENTS = S.EVENTS /\\ S_receiver.STORE[n_destination] = DEFINED (PINT 42)',
 'S_catch_found = $bottom_review_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_type_error',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = '
 '($ptascii("receiver-quiet-never"))',
 'S_catch.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound_raw',
 'S_bound = $bottom_review_after(S_catch,S_bound_raw)',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
 '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ (HOBJECT n_type_error) <- S_bound.ALLOCATIONS',
 '~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT '
 '$ptascii("receiver-quiet-never"),OUTPUT $ptascii(";"),OUTPUT preqbytes_message,OUTPUT '
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

CASES = {
    'void-get-bare-empty-and-receiver-before-fallback': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_empty*',
        'checks': VOID,
    },
    'never-get-empty-implicit-error-receiver-replacement': {
        'source': ROWS[1]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true -- if S.TODO = (TYPE_FALLTHROUGH porigin_method) :: ptask_return*',
        'checks': NEVER,
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
