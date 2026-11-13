#!/usr/bin/env python3
"""Check scalar return coercions, string identity and the outer untyped Notice cell."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scalar_return_producer_cv_reference_notice_cases.json')
PREFIX = r'''
dec $ipr_output(pevent*) : ptbytes
def $ipr_output(eps) = eps
def $ipr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ipr_output(pevent*)
dec $ipr_ready(pstate, nat) : bool
def $ipr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ScalarStringReturnProducer39\\make") \/ pcallcontext.NAME = $ptascii("ScalarBoolReturnProducer39\\make") \/ pcallcontext.NAME = $ptascii("ScalarRequestStringReturn39\\make")
def $ipr_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ScalarStringReturnProducer39\\take") \/ pfunction.NAME = $ptascii("ScalarBoolReturnProducer39\\take") \/ pfunction.NAME = $ptascii("ScalarRequestStringReturn39\\take")
def $ipr_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $ipr_output(S.EVENTS) = $ptascii("S;M:5;H:1;")
def $ipr_ready(S, 3) = true
  -- if S.CURRENT = eps
  -- if $lookup(S.ENV, $ptascii("r")) = (n_private)
  -- if S.STORE[n_private] = DEFINED (PARRAY n_array)
  -- if $ipr_output(S.EVENTS) = $ptascii("S;M:5;H:1;F:1;")
def $ipr_ready(S, n_stage) = false -- otherwise
dec $ipr_seek(pstate, nat, nat) : pstate
def $ipr_seek(S, n_stage, n) = S
  -- if $ipr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $ipr_seek(S, n_stage, n) = $ipr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ipr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ipr_seek(S, n_stage, n) = S -- otherwise
'''

RETURN = r'''
S_initial.COMPLETION = BUDGET
S_return = $ipr_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ScalarStringReturnProducer39\\make")
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]
$typed_return_task_valid(S_return, z_return)
S_return.ORIGIN = (porigin_return_source)
$origin_node(S_return.SOURCES, porigin_return_source) = (NStmtReturn expression_return metadata_return_statement)
$reference_cv(expression_return) = ($ptascii("input"))
$lookup(S_return.ENV, $ptascii("input")) = (n_source_return)
S_return.STORE[n_source_return] = DEFINED (PINT 5)
n_source_return <- S_return.REFCELLS
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN (PINT 5)
S_return.FRAMES = [pframe_caller]
pframe_caller.LOCALS = eps
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.STRINGDATA = S_return.STRINGDATA
S_checked.ALLOCATIONS = S_return.ALLOCATIONS /\ S_checked.PARAMETERBACKINGS = eps
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_return_step = $drive(S_return, 1)
S_return_step.COMPLETION = BUDGET
S_after_return = S_return_step[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))) porigin_return?) :: ptask_return_tail*
S_after_return.CURRENT = S_return.CURRENT /\ S_after_return.ENV = S_return.ENV
S_after_return.STORE = S_return.STORE
$task_nodes(RETURN_UNWIND (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))) porigin_return?) = eps
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source_return) = 3
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
'''.strip().splitlines()

COMMON = r'''
S_pre = $ipr_seek(S_after_return, 1, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ScalarStringReturnProducer39\\make")
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
$call_target(S_pre, $ptascii("make"), eps) = (pfunction_global)
pfunction_global.ORIGIN =/= pfunction_producer.ORIGIN
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("string")
pssignature = pfunction_producer.SIGNATURE
pssignature.PARAMETERS = [psparam]
psparam.BYREF /\ psparam.TYPE = eps /\ ~psparam.VARIADIC /\ psparam.REQUIRED /\ psparam.DEFAULT = PSNONE
pssignature.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pssignature)
$reference_notice_producer_arguments(phpType6_producer, phpType16, pssignature[.RETURNS = eps])
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
n_source_cv = n_source_return
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
$lookup(S_pre.ENV, $ptascii("input")) = eps
S_pre.STORE[n_source_cv] = DEFINED (PINT 5)
n_source_cv <- S_pre.REFCELLS
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
$node_children(S_pre, HCELL n_source_cv) = eps
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
$ipr_output(S_pre.EVENTS) = $ptascii("S;M:5;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source_cv) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
'''.strip().splitlines()

PRIVATE = r'''
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature)
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source_cv
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))
n_private <- S_notice.REFCELLS /\ (HCELL n_private) <- S_notice.ALLOCATIONS
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = eps
S_notice.PARAMETERBACKINGS = eps /\ S_notice.PROPREFS = eps /\ S_notice.REFCOERCIONS = eps
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HCELL n_source_cv) = 2
$heap_valid(H_notice) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $ipr_seek(S_notice, 2, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_source_cv] = DEFINED (PINT 23)
S_resume.STORE[n_private] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))
S_resume.PARAMETERBACKINGS = eps /\ S_resume.PROPREFS = eps /\ S_resume.REFCOERCIONS = eps
$error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1 /\ $heap_valid(H_resume)
S_array = $ipr_seek(S_resume, 3, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_array, 3)
$lookup(S_array.ENV, $ptascii("r")) = (n_private)
S_array.STORE[n_private] = DEFINED (PARRAY n_array)
S_array.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$node_children(S_array, HCELL n_private) = [HARRAY n_array]
(HARRAY n_array) <- $pools_nodes(S_array.POOLS)
S_array.PARAMETERBACKINGS = eps /\ S_array.PROPREFS = eps /\ S_array.REFCOERCIONS = eps
H_array = $heap_graph(S_array)
$heap_owners(H_array, HARRAY n_array) = 2 /\ $heap_valid(H_array)
$call_descriptors_valid(S_array)
S_full = $drive(S_array, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$ipr_output(S_full.EVENTS) = $ptascii("S;M:5;H:1;F:1;R:9:23:23;P:29:23;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT 29)
S_full.STORE[n_source_cv] = DEFINED (PINT 23)
$lookup(S_full.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_full.ENV, $ptascii("sourceAlias")) = (n_source_cv)
$node_children(S_full, HCELL n_private) = eps
(HARRAY n_array) <- S_full.ALLOCATIONS
(HARRAY n_array) <- $pools_nodes(S_full.POOLS)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
H_full = $heap_graph(S_full)
$heap_owners(H_full, HARRAY n_array) = 1
$heap_valid(H_full) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()

CONTROLS = r'''
~$reference_notice_producer_header(phpType6_producer, phpType16, ABSENT, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES "YXJyYXk=") metadata_return, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.RETURNS = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return, pssignature[.RETURNS = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.BYREF = false]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.REQUIRED = false]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.VARIADIC = true]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]])
~$reference_notice_producer_header(SEQUENCE ([NArg (NIdentifier (BYTES "aW5wdXQ=") metadata_return) expression_input (BOOLEAN false) (BOOLEAN false) metadata_input]), phpType16, phpType18, pssignature)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_notice, perrorcall[.RESUME = CALL_ARGS pcalltarget eps 1 ([KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))]) (porigin_call) z])
S_zero_return = $drive(S_return, 0)
S_zero_return.COMPLETION = BUDGET /\ S_zero_return[.COMPLETION = NORMAL] = S_return
$drive($drive(S_zero_return[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_return, 2)
S_zero_notice = $drive(S_notice, 0)
S_zero_notice.COMPLETION = BUDGET /\ S_zero_notice[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero_notice[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
'''.strip().splitlines()

BOOLEAN = r'''
S_bool_return = $ipr_seek(S_bool_initial, 0, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_bool_return, 0)
S_bool_return.TODO = (RETURN_VALUE z_bool_return) :: ptask_bool_return*
S_bool_return.CURRENT = (pcallcontext_bool)
$function_at($all_functions(S_bool_return), pcallcontext_bool.FUNCTION) = (pfunction_bool)
pfunction_bool.NAME = $ptascii("ScalarBoolReturnProducer39\\make")
~pfunction_bool.SIGNATURE.BYREF /\ ~pfunction_bool.CODE.STRICT
pfunction_bool.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"]))]
$typed_return_task_valid(S_bool_return, z_bool_return)
$lookup(S_bool_return.ENV, $ptascii("input")) = (n_bool_source)
S_bool_return.STORE[n_bool_source] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))
$resolve_at(S_bool_return, S_bool_return.RESULT, z_bool_return).RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))
S_bool_checked = $typed_return_value(S_bool_return, z_bool_return)
S_bool_checked.RESULT = KNOWN (PBOOL false) /\ S_bool_checked.COMPLETION = NORMAL
S_bool_checked.STORE = S_bool_return.STORE /\ S_bool_checked.STRINGDATA = S_bool_return.STRINGDATA
S_bool_after_return = $drive(S_bool_return, 1)[.COMPLETION = NORMAL]
S_bool_after_return.TODO = (RETURN_UNWIND (KNOWN (PBOOL false)) porigin_bool_return?) :: ptask_bool_unwind*
$task_nodes(RETURN_UNWIND (KNOWN (PBOOL false)) porigin_bool_return?) = eps
S_bool_pre = $ipr_seek(S_bool_after_return, 1, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_bool_pre, 1)
S_bool_pre.CURRENT = eps /\ S_bool_pre.FRAMES = eps
S_bool_pre.RESULT = KNOWN (PBOOL false)
S_bool_pre.TODO = (CALL_SEND pcalltarget_bool eps 0 eps (porigin_bool_call) z_bool) :: ptask_bool_tail*
$lookup(S_bool_pre.ENV, $ptascii("source")) = (n_bool_source)
$lookup(S_bool_pre.ENV, $ptascii("sourceAlias")) = (n_bool_source)
S_bool_pre.STORE[n_bool_source] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))
$positional_reference_notice_source(S_bool_pre, pcalltarget_bool, 0, (porigin_bool_call))
$positional_reference_notice_pending(S_bool_pre)
n_bool_private = |S_bool_pre.STORE|
n_bool_private =/= n_bool_source
S_bool_notice = $drive(S_bool_pre, 1)[.COMPLETION = NORMAL]
S_bool_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_bool) :: ptask_bool_notice*
perrorcall_bool.RESUME = CALL_ARGS pcalltarget_bool eps 1 ([REFERENCE n_bool_private]) (porigin_bool_call) z_bool
S_bool_notice.STORE[n_bool_private] = DEFINED (PBOOL false)
$node_children(S_bool_notice, HCELL n_bool_private) = eps
$propref_at(S_bool_notice.PROPREFS, n_bool_private) = eps /\ $reference_coercion_at(S_bool_notice.REFCOERCIONS, n_bool_private) = eps
$parameter_backing_at(S_bool_notice.PARAMETERBACKINGS, n_bool_private) = eps
H_bool = $heap_graph(S_bool_notice)
$heap_owners(H_bool, HCELL n_bool_private) = 1 /\ $heap_owners(H_bool, HCELL n_bool_source) = 2
$heap_valid(H_bool) /\ $error_call_valid(S_bool_notice, perrorcall_bool)
S_bool_full = $drive(S_bool_notice, 10000)
S_bool_full.COMPLETION = NORMAL /\ S_bool_full.TODO = eps /\ S_bool_full.CURRENT = eps /\ S_bool_full.FRAMES = eps
$ipr_output(S_bool_full.EVENTS) = $ptascii("B;M:0;H:1;F:1;R:bool:23:23;P:31:23;")
$lookup(S_bool_full.ENV, $ptascii("r")) = (n_bool_private)
S_bool_full.STORE[n_bool_private] = DEFINED (PINT 31)
S_bool_full.STORE[n_bool_source] = DEFINED (PINT 23)
$propref_at(S_bool_full.PROPREFS, n_bool_private) = eps /\ $reference_coercion_at(S_bool_full.REFCOERCIONS, n_bool_private) = eps
$parameter_backing_at(S_bool_full.PARAMETERBACKINGS, n_bool_private) = eps
$heap_valid($heap_graph(S_bool_full)) /\ $call_descriptors_valid(S_bool_full)
'''.strip().splitlines()

REQUEST = r'''
S_request_return = $ipr_seek(S_request_initial, 0, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_request_return, 0)
S_request_return.TODO = (RETURN_VALUE z_request_return) :: ptask_request_return*
S_request_return.CURRENT = (pcallcontext_request)
$function_at($all_functions(S_request_return), pcallcontext_request.FUNCTION) = (pfunction_request)
pfunction_request.NAME = $ptascii("ScalarRequestStringReturn39\\make")
pfunction_request.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]
~pfunction_request.SIGNATURE.BYREF /\ ~pfunction_request.CODE.STRICT
$lookup(S_request_return.ENV, $ptascii("input")) = (n_request_source)
S_request_return.STORE[n_request_source] = DEFINED (PINT 17)
S_request_checked = $typed_return_value(S_request_return, z_request_return)
n_request_string = |S_request_return.STRINGDATA|
pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request_string) ($ptascii("17"))
S_request_checked.RESULT = KNOWN pvalue_request /\ S_request_checked.COMPLETION = NORMAL
S_request_checked.STORE = S_request_return.STORE
S_request_checked.STRINGDATA = S_request_return.STRINGDATA ++ [$ptascii("17")]
S_request_after_return = $drive(S_request_return, 1)[.COMPLETION = NORMAL]
S_request_after_return.TODO = (RETURN_UNWIND (KNOWN pvalue_request) porigin_request_return?) :: ptask_request_unwind*
$task_nodes(RETURN_UNWIND (KNOWN pvalue_request) porigin_request_return?) = eps
S_request_pre = $ipr_seek(S_request_after_return, 1, 1536)[.COMPLETION = NORMAL]
$ipr_ready(S_request_pre, 1)
S_request_pre.CURRENT = eps /\ S_request_pre.FRAMES = eps
S_request_pre.RESULT = KNOWN pvalue_request
S_request_pre.TODO = (CALL_SEND pcalltarget_request eps 0 eps (porigin_request_call) z_request) :: ptask_request_tail*
$lookup(S_request_pre.ENV, $ptascii("source")) = (n_request_source)
$lookup(S_request_pre.ENV, $ptascii("sourceAlias")) = (n_request_source)
S_request_pre.STORE[n_request_source] = DEFINED (PINT 17)
$string_carrier_valid(S_request_pre, pvalue_request)
S_request_pre.STRINGDATA[n_request_string] = $ptascii("17")
$positional_reference_notice_source(S_request_pre, pcalltarget_request, 0, (porigin_request_call))
$named_reference_notice_root_value(S_request_pre, pvalue_request)
$named_reference_notice_operand(S_request_pre, KNOWN pvalue_request)
$positional_reference_notice_pending(S_request_pre)
$ipr_output(S_request_pre.EVENTS) = $ptascii("R;M:17;")
n_request_private = |S_request_pre.STORE|
n_request_private =/= n_request_source
S_request_notice = $drive(S_request_pre, 1)[.COMPLETION = NORMAL]
S_request_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_request) :: ptask_request_notice*
perrorcall_request.RESUME = CALL_ARGS pcalltarget_request eps 1 ([REFERENCE n_request_private]) (porigin_request_call) z_request
S_request_notice.STORE = S_request_pre.STORE ++ [DEFINED pvalue_request]
S_request_notice.STORE[n_request_source] = DEFINED (PINT 17)
S_request_notice.STRINGDATA = S_request_pre.STRINGDATA
$error_call_valid(S_request_notice, perrorcall_request)
H_request = $heap_graph(S_request_notice)
$heap_owners(H_request, HCELL n_request_private) = 1 /\ $heap_owners(H_request, HCELL n_request_source) = 2
$heap_valid(H_request)
S_request_full = $drive(S_request_notice, 10000)
S_request_full.COMPLETION = NORMAL /\ S_request_full.TODO = eps /\ S_request_full.CURRENT = eps /\ S_request_full.FRAMES = eps
$ipr_output(S_request_full.EVENTS) = $ptascii("R;M:17;H:1;F:1;R:request:23:23;P:31:23;")
$lookup(S_request_full.ENV, $ptascii("r")) = (n_request_private)
S_request_full.STORE[n_request_private] = DEFINED (PINT 31)
S_request_full.STORE[n_request_source] = DEFINED (PINT 23)
$propref_at(S_request_full.PROPREFS, n_request_private) = eps /\ $reference_coercion_at(S_request_full.REFCOERCIONS, n_request_private) = eps
$parameter_backing_at(S_request_full.PARAMETERBACKINGS, n_request_private) = eps
$node_children(S_request_full, HCELL n_request_private) = eps
$heap_valid($heap_graph(S_request_full)) /\ $call_descriptors_valid(S_request_full)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    parser.add_argument('--request-only', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    selected = [3] if args.request_only else ([0] if args.front else [0, 1, 3])
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    source = sources[selected[0]]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    for i in selected:
        case, record = cases[i], records[cases[i]['id']]
        assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == record['source_sha256']
        assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in selected:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources[i].read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    def initial(name, i):
        return name + ' = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
    if args.request_only:
        reached = [initial('S_request_initial', 3)] + REQUEST
        derived = []
    elif args.front:
        reached = [initial('S_initial', 0)] + RETURN + COMMON
        derived = [
            '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature)',
            '~$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))',
            '~$positional_reference_notice_pending(S_pre)',
            'S_fenced = $drive(S_pre, 1)',
            'S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
            'S_fenced.EVENTS = S_pre.EVENTS',
            '|S_fenced.STORE| = $(|S_pre.STORE| + 1)',
            'S_fenced.STORE[n_source_cv] = S_pre.STORE[n_source_cv]',
            'S_fenced.STORE[|S_pre.STORE|] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))',
        ]
    else:
        reached = [initial('S_initial', 0)] + RETURN + COMMON + PRIVATE + [initial('S_bool_initial', 1)] + BOOLEAN + [initial('S_request_initial', 3)] + REQUEST
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = modules + [runner, Path(__file__), CATALOGUE, fixture, native_path, source, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
    watched += [ROOT / path for path in ('tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for i in selected:
        watched += [sources[i], Path(records[cases[i]['id']]['stdout']), Path(records[cases[i]['id']]['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in watched}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'scalar-return-request' if args.request_only else ('scalar-return-front' if args.front else 'scalar-return-notice'), 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
