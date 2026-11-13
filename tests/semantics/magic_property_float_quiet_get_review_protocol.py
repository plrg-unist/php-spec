#!/usr/bin/env python3
"""Check quiet float return errors and NaN warning continuation lifetime."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_float_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''

dec $float_review_get_dtor(pstate,nat) : bool
def $float_review_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $float_review_get_dtor(S,n) = false -- otherwise
dec $float_review_get_seek_dtor(pstate,nat,nat) : pstate
def $float_review_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $float_review_get_seek_dtor(S,n_object,n) = S
  -- if $float_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_review_get_seek_dtor(S,n_object,0) = S
  -- if ~$float_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_review_get_seek_dtor(S,n_object,n) = $float_review_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$float_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $float_review_get_catch(pstate) : bool
def $float_review_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $float_review_get_catch(S) = false -- otherwise
dec $float_review_get_seek_catch(pstate,nat) : pstate
def $float_review_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $float_review_get_seek_catch(S,n) = S
  -- if $float_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_review_get_seek_catch(S,0) = S
  -- if ~$float_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_review_get_seek_catch(S,n) = $float_review_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$float_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

STRICT_ERROR = ['$call_task_valid(S,RETURN_VALUE z_return) /\\ z_return = 10',
 'S.RESULT = KNOWN pvalue_raw',
 '$string_bytes(pvalue_raw) = ($ptascii("0.5"))',
 'ppropertycoalesce.PROPERTY = eps /\\ ppropertycoalesce.NAME = $ptascii("gone")',
 'n_receiver = ppropertycoalesce.OBJECT',
 'S.OBJECTS[n_receiver] = INSTANCE ppropertycoalesce.CLASS',
 '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ENDLINE = 11',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"]))] /\\ ~pfunction.SIGNATURE.BYREF',
 'pfunction.DEFAULTS = eps /\\ pfunction.CODE.STRICT',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertycoalesce.CLASS',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous")',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) '
 'metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("float")',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME '
 'eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK '
 'pfunction.SIGNATURE.RETURNS eps',
 '$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
 '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_raw,true,false) = TYPEREJECT',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_raw,false,false) = TYPEVALUE (PFLOAT '
 '4602678819172646912)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 1,true,false) = TYPEVALUE (PFLOAT '
 '4607182418800017408)',
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
 '$return_function_name(S[.CURRENT = (pcallcontext_isset)],pfunction) = $call_function_name(S[.CURRENT = '
 '(pcallcontext_isset)],pfunction)',
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
 '~$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN '
 'PNULL)',
 '$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (PINT '
 '0))',
 '~$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,KNOWN '
 '(PINT 0))',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_graph(S))',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET',
 'S_receiver_found = $float_review_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 '$float_review_get_dtor(S_receiver,n_receiver)',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = '
 '(pdestructorcall_receiver)',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.PENDING = (n_type_error)',
 'pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_type_error',
 'pdestructionoperation_receiver.VALUE = KNOWN PNULL',
 'S_receiver.OBJECTS[n_type_error] = THROWABLE pthrowable_type_error',
 'pthrowable_type_error.KIND = "TypeError"',
 '$string_bytes($throwable_field(S_receiver,n_type_error,"message")) = ($ptascii("class@anonymous::__get(): '
 'Return value must be of type float, string returned"))',
 '$throwable_field(S_receiver,n_type_error,"line") = PINT 10',
 '$throwable_field(S_receiver,n_type_error,"previous") = PNULL',
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertycoalesce.NAME)',
 'S_receiver.EVENTS = S.EVENTS',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_catch_found = $float_review_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_type_error',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("receiver-float"))',
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
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("receiver-float"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("class@anonymous::__get(): Return value must be of type float, string '
 'returned"),OUTPUT $ptascii(";"),OUTPUT $ptascii("10"),OUTPUT $ptascii(";"),OUTPUT $ptascii("KEEP;"),OUTPUT '
 '$ptascii("CLEARED;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42)',
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps',
 '~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_type_error) <- S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_catch,4096) = S_done',
 '$drive_steps(S_receiver,4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done',
 '~$property_isset_guard(S_receiver,S_receiver.CURRENT,S_receiver.FRAMES,n_receiver,ppropertycoalesce.NAME)']

HELPERS += r'''

syntax pfloatreviewstage = FQ_REENTRANT | FQ_RESUME
dec $float_review_nan_stage(pstate,pfloatreviewstage) : bool
def $float_review_nan_stage(S,FQ_REENTRANT) = true
  -- if S.TODO = (ISSET_RESULT false z) :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
def $float_review_nan_stage(S,FQ_RESUME) = true
  -- if S.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask_tail*
def $float_review_nan_stage(S,pfloatreviewstage) = false -- otherwise
dec $float_review_nan_seek(pstate,pfloatreviewstage,nat) : pstate
def $float_review_nan_seek(S,pfloatreviewstage,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $float_review_nan_seek(S,pfloatreviewstage,n) = S
  -- if $float_review_nan_stage(S,pfloatreviewstage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_review_nan_seek(S,pfloatreviewstage,0) = S
  -- if ~$float_review_nan_stage(S,pfloatreviewstage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_review_nan_seek(S,pfloatreviewstage,n) = $float_review_nan_seek($drive_steps(S[.COMPLETION = NORMAL],1),pfloatreviewstage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$float_review_nan_stage(S,pfloatreviewstage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $float_review_after(pstate,pstate) : pstate
def $float_review_after(S,S_next) = $literal_reference_debt_step(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next))))
'''

NAN_WARNING = ['S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
 'S.ORIGIN = (ppropertyempty.SITE) /\\ S.BASE = BASE_VALUE (KNOWN PNULL)',
 'ppropertyempty.PROPERTY = eps /\\ ppropertyempty.NAME = $ptascii("value") /\\ ppropertyempty.LINE = 16',
 'n_receiver = ppropertyempty.OBJECT',
 'S.OBJECTS[n_receiver] = INSTANCE ppropertyempty.CLASS',
 '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = ppropertyempty.GET /\\ pfunction.ENDLINE = 4 /\\ ~pfunction.CODE.STRICT',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"]))] /\\ ~pfunction.SIGNATURE.BYREF',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous") /\\ pclassdesc.PARENT = eps',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) '
 'metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("float")',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME '
 'eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK '
 'pfunction.SIGNATURE.RETURNS eps',
 '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$property_quiet_get_source(S,pmethoddesc) /\\ $property_empty_valid(S,ppropertyempty)',
 '~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
 '~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
 '$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PFLOAT 0))',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PFLOAT '
 '18446744073709551616))',
 '$property_empty_nan_ready(S,ppropertyempty) /\\ $property_empty_truth(S,PFLOAT 9221120237041090560) = eps',
 '$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
 '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver) /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("value"))',
 'n_reader <- S.REFCELLS /\\ (HCELL n_reader) <- S.ALLOCATIONS',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
 '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
 'PhpStep: S ~> S_warning_raw',
 'S_warning = $float_review_after(S,S_warning_raw)',
 'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_caller*',
 'perrorcall.RESUME = PROPERTY_EMPTY_NAN ppropertyemptynan',
 'ppropertyemptynan.EMPTY = ppropertyempty /\\ ppropertyemptynan.FLOAT = 9221120237041090560',
 'ppropertyemptynan.OWNER = 0 /\\ ppropertyemptynan.CALLER = eps /\\ ppropertyemptynan.TAIL = ptask_caller*',
 'perrorcall.LEVEL = 2 /\\ perrorcall.LINE = 16 /\\ perrorcall.SITE = ppropertyempty.SITE',
 'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
 'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE',
 '$property_empty_nan_valid(S_warning,ppropertyemptynan) /\\ $error_call_valid(S_warning,perrorcall)',
 'PhpStep: S_warning ~> S_cursor_raw',
 'S_cursor_raw.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_caller*',
 'papiargcursor.TARGET = CLOSURE_TARGET n_handler',
 '$heap_owners($heap_graph(S_warning),HOBJECT n_handler) = 2',
 '$heap_owners($heap_graph(S_cursor_raw),HOBJECT n_handler) = 1',
 '$api_cursor_valid(S_cursor_raw,papiargcursor)',
 'S_selection = $float_review_after(S_warning,S_cursor_raw)',
 'S_selection.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_selection) :: (DESTRUCTOR_OPERATION_EXIT '
 'pdestructionoperation_selection) :: S_cursor_raw.TODO',
 'pdestructionrelease_selection.JOBS = [DESTRUCTION_VALUE (HOBJECT n_handler)]',
 'pdestructionoperation_selection.SOURCE = ERROR_HANDLER_INVOKE perrorcall',
 'pdestructionoperation_selection.VALUE = KNOWN PNULL /\\ pdestructionoperation_selection.PENDING = eps',
 '$heap_owners($heap_graph(S_selection),HOBJECT n_handler) = 2 /\\ '
 '$heap_owners($heap_graph(S_selection),HOBJECT n_receiver) = 2',
 '$api_cursor_valid(S_selection,papiargcursor) /\\ '
 '$property_empty_nan_guard(S_selection,n_receiver,ppropertyempty.NAME)',
 'S_selection.EVENTS = S.EVENTS /\\ S_selection.STORE = S_warning.STORE',
 'S_selection_public = $drive_steps(S_warning,1)',
 'S_selection_public.COMPLETION = BUDGET /\\ S_selection_public.TODO = S_selection.TODO',
 'S_selection_public[.COMPLETION = NORMAL] = S_selection',
 '$heap_owners($heap_graph(S_selection_public),HOBJECT n_handler) = 2',
 'PhpStep: S_selection ~> S_selection_unheld_raw',
 'S_selection_unheld_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_selection_empty) :: '
 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_selection) :: S_cursor_raw.TODO',
 'pdestructionrelease_selection_empty.JOBS = eps',
 '$heap_owners($heap_graph(S_selection_unheld_raw),HOBJECT n_handler) = 1 /\\ '
 '$heap_owners($heap_graph(S_selection_unheld_raw),HOBJECT n_receiver) = 2',
 'S_selection_unheld_raw.EVENTS = S.EVENTS',
 'S_selection_unheld = $float_review_after(S_selection,S_selection_unheld_raw)',
 'S_selection_unheld.TODO = S_selection_unheld_raw.TODO',
 'PhpStep: S_selection_unheld ~> S_selection_exit_raw',
 'S_selection_exit_raw.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_selection) :: S_cursor_raw.TODO',
 'S_selection_exit = $float_review_after(S_selection_unheld,S_selection_exit_raw)',
 'S_selection_exit.TODO = S_selection_exit_raw.TODO',
 'PhpStep: S_selection_exit ~> S_cursor_finished_raw',
 'S_cursor_finished_raw.TODO = S_cursor_raw.TODO /\\ S_cursor_finished_raw.RESULT = KNOWN PNULL /\\ '
 'S_cursor_finished_raw.BASE = BASE_VALUE (KNOWN PNULL)',
 'S_cursor_finished_raw.EVENTS = S.EVENTS /\\ S_cursor_finished_raw.STORE = S_warning.STORE',
 'S_cursor_finished_raw.DESTRUCTION.OPERATIONS = eps /\\ S_cursor_finished_raw.DESTRUCTION.RELEASES = eps /\\ '
 'S_cursor_finished_raw.DESTRUCTION.CALLS = eps',
 '$heap_owners($heap_graph(S_cursor_finished_raw),HOBJECT n_handler) = 1 /\\ $heap_owners($heap_graph(S_cursor_finished_raw),HOBJECT '
 'n_receiver) = 2',
 '(HOBJECT n_handler) <- S_cursor_finished_raw.ALLOCATIONS',
 'S_cursor = $float_review_after(S_selection_exit,S_cursor_finished_raw)',
 'S_cursor.TODO = S_cursor_finished_raw.TODO /\\ S_cursor.EVENTS = S_cursor_finished_raw.EVENTS',
 'papiargcursor.CALL = API_ERROR perrorcall',
 'papiargcursor.SENT = eps /\\ papiargcursor.INDEX = 0 /\\ papiargcursor.LINE = 16 /\\ papiargcursor.SITE = '
 'ppropertyempty.SITE',
 '$source_operand_marker(API_CALLBACK_SEND papiargcursor) = PROPERTY_EMPTY_NAN ppropertyemptynan',
 '$source_operand_suffix(S_cursor.TODO,PROPERTY_EMPTY_NAN ppropertyemptynan,ptask_caller*)',
 '$api_cursor_valid(S_cursor,papiargcursor) /\\ $call_task_valid(S_cursor,API_CALLBACK_SEND papiargcursor)',
 '$property_empty_nan_valid(S_cursor,ppropertyemptynan) /\\ '
 '$property_empty_nan_guard(S_cursor,n_receiver,ppropertyempty.NAME)',
 '$api_cursor_site_valid(S_cursor,papiargcursor) /\\ $api_cursor_producer_live(S_cursor,papiargcursor)',
 '$api_callback_selected(S_cursor,papiargcursor.CALL,papiargcursor.TARGET)',
 '$target_function(S_cursor,papiargcursor.TARGET) = (pfunction_handler)',
 'pfunction_handler.SIGNATURE.PARAMETERS = [psparam_level,psparam_message,psparam_file,psparam_line]',
 '~psparam_level.BYREF /\\ ~psparam_message.BYREF /\\ ~psparam_file.BYREF /\\ ~psparam_line.BYREF',
 'papiargcursor.VALUES = $api_callback_values(S_cursor,papiargcursor.CALL) /\\ |papiargcursor.VALUES| = 4',
 'papiargcursor.VALUES[0] = PINT 2 /\\ papiargcursor.VALUES[1] = PSTRING perrorcall.MESSAGE /\\ '
 'papiargcursor.VALUES[3] = PINT 16',
 '$task_nodes(API_CALLBACK_SEND papiargcursor) = $api_callback_roots(papiargcursor.CALL)',
 '$selected_task_nonce(API_CALLBACK_SEND papiargcursor) = $selected_task_nonce(perrorcall.RESUME)',
 '$heap_owners($heap_graph(S_cursor),HOBJECT n_receiver) = 2 /\\ S_cursor.EVENTS = S.EVENTS',
 '~$api_cursor_valid(S_cursor[.SOURCES = eps],papiargcursor)',
 '~$api_cursor_valid(S_cursor,papiargcursor[.LINE = 17])',
 '~$api_cursor_valid(S_cursor,papiargcursor[.VALUES = eps])',
 '~$api_cursor_valid(S_cursor,papiargcursor[.INDEX = 1])',
 '~$api_cursor_valid(S_cursor,papiargcursor[.PRODUCER = papiargcursor.PRODUCER[.INTERNAL = false]])',
 '~$api_cursor_valid(S_cursor[.ORIGIN = eps],papiargcursor)',
 'papiargcursor_badowner = papiargcursor[.CALL = API_ERROR perrorcall[.RESUME = PROPERTY_EMPTY_NAN '
 'ppropertyemptynan[.OWNER = 1]]]',
 'S_badowner = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor_badowner) :: ptask_caller*]',
 '~$api_cursor_valid(S_badowner,papiargcursor_badowner)',
 'papiargcursor_badtail = papiargcursor[.CALL = API_ERROR perrorcall[.RESUME = PROPERTY_EMPTY_NAN '
 'ppropertyemptynan[.TAIL = eps]]]',
 'S_badtail = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor_badtail) :: ptask_caller*]',
 '~$api_cursor_valid(S_badtail,papiargcursor_badtail)',
 'papiargcursor_badmessage = papiargcursor[.CALL = API_ERROR perrorcall[.MESSAGE = $ptascii("forged")]]',
 'S_badmessage = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor_badmessage) :: ptask_caller*]',
 '~$api_cursor_valid(S_badmessage,papiargcursor_badmessage)',
 'PhpStep: S_cursor ~> S_sent',
 'S_sent.TODO = (API_CALLBACK_SEND papiargcursor[.SENT = [KNOWN (PINT 2)]][.INDEX = 1]) :: ptask_caller*',
 'S_sent.STORE = S_cursor.STORE /\\ S_sent.EVENTS = S_cursor.EVENTS',
 '$heap_owners($heap_graph(S_sent),HOBJECT n_receiver) = 2',
 'S_nested_found = $float_review_nan_seek(S_sent,FQ_REENTRANT,2000)',
 'S_nested_found.COMPLETION = NORMAL \\/ S_nested_found.COMPLETION = BUDGET',
 'S_nested = S_nested_found[.COMPLETION = NORMAL]',
 'S_nested.TODO = (ISSET_RESULT false 10) :: ptask_nested*',
 'S_nested.BASE = BASE_PROPERTY (POBJECT n_receiver) ppropertyempty.NAME /\\ S_nested.RESULT = KNOWN PNULL',
 'S_nested.CURRENT = (pcallcontext_handler)',
 'S_nested.FRAMES = [pframe_handler]',
 'pcallcontext_handler.TARGET = API_BORROWED_TARGET papiargcursor.PRODUCER',
 'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
 'perrorcall_entered.RESUME = PROPERTY_EMPTY_NAN ppropertyemptynan',
 'S_handler_caller = $constant_frame_view(S_nested,pframe_handler,eps)',
 '$property_empty_nan_valid(S_handler_caller,ppropertyemptynan)',
 '$property_empty_nan_guard(S_nested,n_receiver,ppropertyempty.NAME)',
 '~$property_empty_nan_guard(S_nested,n_receiver,$ptascii("other"))',
 '~$property_empty_nan_guard(S_nested[.SOURCES = eps],n_receiver,ppropertyempty.NAME)',
 '~$property_empty_get_active(S_nested,n_receiver,ppropertyempty.NAME)',
 '$property_isset_plan(S_nested) = (ppropertyisset_nested)',
 '$property_isset_plan(S_nested[.SOURCES = eps]) = eps',
 'ppropertyisset_nested.OBJECT = n_receiver /\\ ppropertyisset_nested.NAME = ppropertyempty.NAME',
 '$property_isset_plan(S_nested[.TODO = (ISSET_RESULT false 11) :: ptask_nested*]) = eps',
 '$property_isset_plan(S_nested[.BASE = BASE_PROPERTY (POBJECT n_receiver) $ptascii("other")]) = eps',
 '$property_isset_capture(S_nested,ppropertyisset_nested) /\\ '
 '$property_isset_source(S_nested,ppropertyisset_nested)',
 'S_nested.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("WARN;"),OUTPUT perrorcall.MESSAGE,OUTPUT $ptascii(";")]',
 'PhpStep: S_nested ~> S_guarded',
 'S_guarded.TODO = ptask_nested* /\\ S_guarded.RESULT = KNOWN (PBOOL false) /\\ S_guarded.BASE = BASE_VALUE '
 '(KNOWN PNULL)',
 'S_guarded.STORE = S_nested.STORE /\\ S_guarded.EVENTS = S_nested.EVENTS',
 'S_resume_found = $float_review_nan_seek($float_review_after(S_nested,S_guarded),FQ_RESUME,2000)',
 'S_resume_found.COMPLETION = NORMAL \\/ S_resume_found.COMPLETION = BUDGET',
 'S_resume = S_resume_found[.COMPLETION = NORMAL]',
 'S_resume.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask_caller*',
 'S_resume.CURRENT = eps /\\ S_resume.FRAMES = eps /\\ S_resume.RESULT = KNOWN PNULL',
 'S_resume.STORE[n_reader] = DEFINED PNULL /\\ S_resume.STORE[n_destination] = DEFINED (PINT 42)',
 'S_resume.STORE[n_selector] = DEFINED pvalue_selector',
 'S_resume.ERRORHANDLER = S_warning.ERRORHANDLER',
 '$property_empty_nan_valid(S_resume,ppropertyemptynan) /\\ ~$property_empty_capture(S_resume,ppropertyempty)',
 '$property_empty_nan_guard(S_resume,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_get_active(S_resume,n_receiver,ppropertyempty.NAME)',
 '$heap_owners($heap_graph(S_resume),HOBJECT n_receiver) = 1',
 'S_resume.EVENTS = S_nested.EVENTS ++ [OUTPUT $ptascii("GUARD;")]',
 'PhpStep: S_resume ~> S_release',
 'S_release.TODO = ptask_caller* /\\ S_release.RESULT = KNOWN (PBOOL false) /\\ S_release.BASE = BASE_VALUE '
 '(KNOWN PNULL)',
 'S_release.STORE = S_resume.STORE /\\ S_release.EVENTS = S_resume.EVENTS',
 '$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 0',
 '~$property_empty_nan_guard(S_release,n_receiver,ppropertyempty.NAME)',
 'S_receiver_found = $float_review_get_seek_dtor(S_resume,n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = '
 '(pdestructorcall_receiver)',
 'pdestructorcall_receiver.OBJECT = n_receiver',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.SOURCE = PROPERTY_EMPTY_NAN ppropertyemptynan',
 'pdestructionoperation_receiver.VALUE = KNOWN (PBOOL false) /\\ pdestructionoperation_receiver.PENDING = eps',
 'S_receiver.EVENTS = S_resume.EVENTS',
 '~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertyempty.NAME)',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_catch_found = $float_review_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("receiver-nan"))',
 '$throwable_field(S_catch,n_receiver_error,"previous") = PNULL',
 'S_catch.EVENTS = S_resume.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
 '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ ~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 'S_done.HELD = eps',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ '
 'S_done.DESTRUCTION.CALLS = eps',
 'S_done.EVENTS = S_resume.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("receiver-nan"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("NO_PREVIOUS;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT '
 '$ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42) /\\ '
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps',
 '~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_warning.TODO /\\ S_one.EVENTS = S.EVENTS',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S_cursor,4096) = S_done',
 '$drive_steps(S_selection_public[.COMPLETION = NORMAL],4096) = S_done']

CASES = {
    'float-nan-quiet-get-warning-reentrant-isset-and-cleanup': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller* -- if S.RESULT = KNOWN (PFLOAT 9221120237041090560)',
        'checks': NAN_WARNING,
    },
    'strict-float-quiet-get-string-error-pending-cleanup': {
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
