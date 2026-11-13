#!/usr/bin/env python3
"""Ground request-array leaves and existing quiet COW before selected Notice admission."""
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
CATALOGUE = Path(__file__).with_name('request_string_array_leaf_reference_notice_cases.json')

PREFIX = r"""
dec $qal_output(pevent*) : ptbytes
def $qal_output(eps) = eps
def $qal_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $qal_output(pevent*)
dec $qal_ready(pstate, nat) : bool
def $qal_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("RequestArrayLeavesNotice41\\make") \/ pcallcontext.NAME = $ptascii("RequestArrayLeavesThrow41\\make")
def $qal_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("RequestArrayLeavesNotice41\\take") \/ pfunction.NAME = $ptascii("RequestArrayLeavesThrow41\\take") \/ pfunction.NAME = $ptascii("RequestArrayObjectNotice41\\take")
def $qal_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $qal_output(S.EVENTS) = $ptascii("A;M:1:1;H:1;")
def $qal_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $lookup(S.ENV, $ptascii("r")) = (n_private)
  -- if S.STORE[n_private] = DEFINED (PARRAY n_root)
  -- if $qal_output(S.EVENTS) = $ptascii("K;M:1:1;F:1:0;")
def $qal_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $lookup(S.ENV, $ptascii("r")) = (n_private)
  -- if S.STORE[n_private] = DEFINED (PARRAY n_root)
  -- if $qal_output(S.EVENTS) = $ptascii("A;M:1:1;H:1;F:1:1;")
def $qal_ready(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $qal_ready(S, n_stage) = false -- otherwise
dec $qal_seek(pstate, nat, nat) : pstate
def $qal_seek(S, n_stage, n) = S
  -- if $qal_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $qal_seek(S, n_stage, n) = $qal_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$qal_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $qal_seek(S, n_stage, n) = $qal_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$qal_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $qal_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $qal_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]
$qal_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("RequestArrayLeavesNotice41\\make")
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("input")) = (n_source_return)
S_return.STORE[n_source_return] = DEFINED (PARRAY n_root)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (PARRAY n_child))]
S_return.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_original), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_return.STORE[n_leaf] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
n_source_return <- S_return.REFCELLS /\ n_leaf <- S_return.REFCELLS
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
n_copy =/= n_source_return /\ n_keeper =/= n_leaf
S_return.STORE[n_copy] = DEFINED (PARRAY n_root) /\ S_return.STORE[n_keeper] = DEFINED pvalue_original
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.STRINGDATA = S_return.STRINGDATA
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
$node_children(S_after_return, HARRAY n_root) = [HARRAY n_child]
$node_children(S_after_return, HARRAY n_child) = [HCELL n_leaf]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source_return) = 3 /\ $heap_owners(H_return, HCELL n_leaf) = 2
$heap_owners(H_return, HARRAY n_root) = 3 /\ $heap_owners(H_return, HARRAY n_child) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $qal_seek(S_after_return, 1, 1536)[.COMPLETION = NORMAL]
$qal_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parameter) metadata_parameter_type) (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$ptlc($base64(text_parameter)) = $ptascii("array")
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("array")
pssignature = pfunction_producer.SIGNATURE
pssignature.PARAMETERS = [psparam]
psparam.BYREF /\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~psparam.VARIADIC /\ psparam.REQUIRED /\ psparam.DEFAULT = PSNONE
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature)
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_return)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
S_pre.STORE[n_source_return] = DEFINED (PARRAY n_root) /\ S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = S_return.ARRAYS[n_root].ITEMS /\ S_pre.ARRAYS[n_child].ITEMS = S_return.ARRAYS[n_child].ITEMS
S_pre.STORE[n_leaf] = DEFINED pvalue_original /\ S_pre.STORE[n_keeper] = DEFINED pvalue_original
$string_carrier_valid(S_pre, pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_original)
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps /\ S_pre.CONTAINERINITS = eps
~$array_immutable(S_pre, n_root) /\ ~$array_immutable(S_pre, n_child)
~(n_root <- S_pre.LITERALARRAYRETAINED) /\ ~(n_child <- S_pre.LITERALARRAYRETAINED)
$qal_output(S_pre.EVENTS) = $ptascii("A;M:1:1;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source_return) = 2 /\ $heap_owners(H_pre, HCELL n_leaf) = 2
$heap_owners(H_pre, HARRAY n_root) = 3 /\ $heap_owners(H_pre, HARRAY n_child) = 1
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

QUIET = r"""
S_quiet_cow = $qal_seek(S_quiet_initial, 3, 4000)[.COMPLETION = NORMAL]
$qal_ready(S_quiet_cow, 3)
~$error_handler_eligible(S_quiet_cow, 8)
$lookup(S_quiet_cow.ENV, $ptascii("r")) = (n_quiet_private)
$lookup(S_quiet_cow.ENV, $ptascii("source")) = (n_quiet_source)
$lookup(S_quiet_cow.ENV, $ptascii("sourceAlias")) = (n_quiet_source)
$lookup(S_quiet_cow.ENV, $ptascii("copy")) = (n_quiet_copy)
$lookup(S_quiet_cow.ENV, $ptascii("leaf")) = (n_quiet_leaf)
$lookup(S_quiet_cow.ENV, $ptascii("keeper")) = (n_quiet_keeper)
S_quiet_cow.STORE[n_quiet_private] = DEFINED (PARRAY n_quiet_root)
S_quiet_cow.STORE[n_quiet_source] = DEFINED (PARRAY n_quiet_old_root)
S_quiet_cow.STORE[n_quiet_copy] = DEFINED (PARRAY n_quiet_old_root)
n_quiet_root =/= n_quiet_old_root /\ n_quiet_private =/= n_quiet_source /\ n_quiet_private =/= n_quiet_copy
S_quiet_cow.ARRAYS[n_quiet_old_root].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (PARRAY n_quiet_old_child))]
S_quiet_cow.ARRAYS[n_quiet_root].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (PARRAY n_quiet_child))]
n_quiet_child =/= n_quiet_old_child
S_quiet_cow.ARRAYS[n_quiet_old_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_quiet_original), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_quiet_leaf)]
pvalue_quiet_original = PSTRING_CARRIER (REQUEST_STRING n_quiet_string) ($ptascii("17"))
$string_carrier_valid(S_quiet_cow, pvalue_quiet_original)
S_quiet_cow.ARRAYS[n_quiet_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("Y7")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_quiet_leaf)]
S_quiet_cow.STORE[n_quiet_leaf] = DEFINED (PSTRING ($ptascii("19")))
S_quiet_cow.STORE[n_quiet_keeper] = DEFINED pvalue_quiet_original
S_quiet_cow.PARAMETERBACKINGS = eps /\ S_quiet_cow.PROPREFS = eps /\ S_quiet_cow.REFCOERCIONS = eps
H_quiet = $heap_graph(S_quiet_cow)
$heap_owners(H_quiet, HARRAY n_quiet_old_root) = 2 /\ $heap_owners(H_quiet, HARRAY n_quiet_root) = 1
$heap_owners(H_quiet, HARRAY n_quiet_old_child) = 1 /\ $heap_owners(H_quiet, HARRAY n_quiet_child) = 1
$heap_owners(H_quiet, HCELL n_quiet_leaf) = 3
$heap_valid(H_quiet) /\ $call_descriptors_valid(S_quiet_cow)
S_quiet_full = $drive(S_quiet_cow, 10000)
S_quiet_full.COMPLETION = NORMAL /\ S_quiet_full.TODO = eps /\ S_quiet_full.CURRENT = eps /\ S_quiet_full.FRAMES = eps
$qal_output(S_quiet_full.EVENTS) = $ptascii("K;M:1:1;F:1:0;R:Y7:19:17:1:19:1;Q:1:19:19:1;")
S_quiet_full.STORE[n_quiet_private] = DEFINED (PINT 31)
S_quiet_full.STORE[n_quiet_source] = DEFINED (PARRAY n_quiet_old_root) /\ S_quiet_full.STORE[n_quiet_copy] = DEFINED (PARRAY n_quiet_old_root)
S_quiet_full.STORE[n_quiet_leaf] = DEFINED (PSTRING ($ptascii("19"))) /\ S_quiet_full.STORE[n_quiet_keeper] = DEFINED pvalue_quiet_original
~((HARRAY n_quiet_root) <- S_quiet_full.ALLOCATIONS) /\ ~((HARRAY n_quiet_child) <- S_quiet_full.ALLOCATIONS)
H_quiet_full = $heap_graph(S_quiet_full)
$heap_owners(H_quiet_full, HARRAY n_quiet_old_root) = 2 /\ $heap_owners(H_quiet_full, HARRAY n_quiet_old_child) = 1
$heap_owners(H_quiet_full, HCELL n_quiet_leaf) = 2
$heap_valid(H_quiet_full) /\ $call_descriptors_valid(S_quiet_full)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_value(pvalue_original)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_operand(S_pre, KNOWN (PARRAY n_root))
~$positional_reference_notice_pending(S_pre)
pvalue_interned = PSTRING_CARRIER INTERNED_STRING ($ptascii("17"))
S_interned = S_pre[.STORE[n_leaf] = DEFINED pvalue_interned][.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_interned), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]]
$named_reference_notice_array(S_interned, PARRAY n_root)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS
S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]
S_fenced.ARRAYS = S_pre.ARRAYS /\ S_fenced.STRINGDATA = S_pre.STRINGDATA
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_operand(S_pre, KNOWN (PARRAY n_root))
$positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source_return /\ n_private =/= n_copy /\ n_private =/= n_leaf
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$named_reference_notice_operand(S_notice, REFERENCE n_private) /\ $error_call_valid(S_notice, perrorcall)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HARRAY n_root) = 3
$heap_owners(H_notice, HARRAY n_child) = 1 /\ $heap_owners(H_notice, HCELL n_leaf) = 2
$heap_valid(H_notice)
S_resume = $qal_seek(S_notice, 2, 4000)[.COMPLETION = NORMAL]
$qal_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (PARRAY n_root) /\ S_resume.STORE[n_copy] = DEFINED (PARRAY n_root)
S_resume.STORE[n_source_return] = DEFINED (PARRAY n_source_root)
n_source_root =/= n_root
S_resume.ARRAYS[n_source_root].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (PARRAY n_source_child))]
n_source_child =/= n_child
S_resume.ARRAYS[n_source_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("18")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_resume.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS /\ S_resume.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
S_resume.STORE[n_leaf] = DEFINED pvalue_current
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
n_current_string =/= n_string
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_original)
S_resume.STORE[n_keeper] = DEFINED pvalue_original
$named_reference_notice_array(S_resume, PARRAY n_root) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HARRAY n_root) = 2 /\ $heap_owners(H_resume, HARRAY n_source_root) = 1
$heap_owners(H_resume, HARRAY n_child) = 1 /\ $heap_owners(H_resume, HARRAY n_source_child) = 1
$heap_owners(H_resume, HCELL n_leaf) = 3 /\ $heap_valid(H_resume)
S_written = $qal_seek(S_resume, 4, 6000)[.COMPLETION = NORMAL]
$qal_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_private_root)
n_private_root =/= n_root /\ n_private_root =/= n_source_root
S_written.ARRAYS[n_private_root].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (PARRAY n_private_child))]
n_private_child =/= n_child /\ n_private_child =/= n_source_child
S_written.ARRAYS[n_private_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("Y7")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_written.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("29")))
S_written.STORE[n_keeper] = DEFINED pvalue_original /\ S_written.STORE[n_copy] = DEFINED (PARRAY n_root)
S_written.STORE[n_source_return] = DEFINED (PARRAY n_source_root)
S_written.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS /\ S_written.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HARRAY n_private_root) = 1 /\ $heap_owners(H_written, HARRAY n_root) = 1 /\ $heap_owners(H_written, HARRAY n_source_root) = 1
$heap_owners(H_written, HCELL n_leaf) = 4 /\ $heap_owners(H_written, HCELL n_private) = 1
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_full = $drive(S_written, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$qal_output(S_full.EVENTS) = $ptascii("A;M:1:1;H:1;F:1:1;R:Y7:29:18:1:29:1;Q:1:29:29:1;")
S_full.STORE[n_private] = DEFINED (PINT 31)
S_full.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("29"))) /\ S_full.STORE[n_keeper] = DEFINED pvalue_original
S_full.STORE[n_source_return] = DEFINED (PARRAY n_source_root) /\ S_full.STORE[n_copy] = DEFINED (PARRAY n_root)
~((HARRAY n_private_root) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_private_child) <- S_full.ALLOCATIONS)
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_leaf) = 3 /\ $heap_owners(H_full, HCELL n_private) = 1
$heap_owners(H_full, HARRAY n_root) = 1 /\ $heap_owners(H_full, HARRAY n_source_root) = 1
$heap_valid(H_full) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

THROW = r"""
S_throw_return = $qal_seek(S_throw_initial, 0, 4000)[.COMPLETION = NORMAL]
$qal_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("RequestArrayLeavesThrow41\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (PARRAY n_throw_root)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
S_throw_return.ARRAYS[n_throw_root].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (PARRAY n_throw_child))]
S_throw_return.ARRAYS[n_throw_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_throw_original), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_throw_leaf)]
pvalue_throw_original = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_return, pvalue_throw_original)
S_throw_pre = $qal_seek(S_throw_return, 1, 4000)[.COMPLETION = NORMAL]
$qal_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (PARRAY n_throw_root)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps
$lookup(S_throw_pre.ENV, $ptascii("r")) = (n_throw_r)
$lookup(S_throw_pre.ENV, $ptascii("leaf")) = (n_throw_leaf)
$lookup(S_throw_pre.ENV, $ptascii("keeper")) = (n_throw_keeper)
S_throw_pre.STORE[n_throw_source] = DEFINED (PINT 7)
S_throw_pre.STORE[n_throw_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))
S_throw_pre.STORE[n_throw_leaf] = DEFINED pvalue_throw_original /\ S_throw_pre.STORE[n_throw_keeper] = DEFINED pvalue_throw_original
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call)) /\ $positional_reference_notice_pending(S_throw_pre)
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HARRAY n_throw_root) = 1 /\ $heap_owners(H_throw_pre, HARRAY n_throw_child) = 1 /\ $heap_owners(H_throw_pre, HCELL n_throw_leaf) = 2
$heap_valid(H_throw_pre)
n_throw_private = |S_throw_pre.STORE|
S_throw_notice = $drive(S_throw_pre, 1)[.COMPLETION = NORMAL]
S_throw_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_throw) :: ptask_throw_notice*
perrorcall_throw.RESUME = CALL_ARGS pcalltarget_throw eps 1 ([REFERENCE n_throw_private]) (porigin_throw_call) z_throw
S_throw_notice.STORE[n_throw_private] = DEFINED (PARRAY n_throw_root)
$error_call_valid(S_throw_notice, perrorcall_throw)
S_throw_pending = $qal_seek(S_throw_notice, 5, 4000)[.COMPLETION = NORMAL]
$qal_ready(S_throw_pending, 5)
S_throw_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw_pending*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw_pending, perrorcall_entered) /\ $throwable_live(S_throw_pending, n_exception)
S_throw_pending.STORE[n_throw_leaf] = DEFINED pvalue_throw_current
pvalue_throw_current = PSTRING_CARRIER (REQUEST_STRING n_throw_current) ($ptascii("23"))
$string_carrier_valid(S_throw_pending, pvalue_throw_current) /\ $string_carrier_valid(S_throw_pending, pvalue_throw_original)
S_throw_pending.STORE[n_throw_keeper] = DEFINED pvalue_throw_original
H_throw_pending = $heap_graph(S_throw_pending)
$heap_owners(H_throw_pending, HCELL n_throw_private) = 1 /\ $heap_owners(H_throw_pending, HARRAY n_throw_root) = 1 /\ $heap_owners(H_throw_pending, HARRAY n_throw_child) = 1
$heap_owners(H_throw_pending, HCELL n_throw_leaf) = 2 /\ $heap_valid(H_throw_pending)
S_cancel = $drive(S_throw_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS) /\ ~((HARRAY n_throw_root) <- S_cancel.ALLOCATIONS) /\ ~((HARRAY n_throw_child) <- S_cancel.ALLOCATIONS)
H_cancel = $heap_graph(S_cancel)
$heap_owners(H_cancel, HCELL n_throw_private) = 0 /\ $heap_owners(H_cancel, HARRAY n_throw_root) = 0 /\ $heap_owners(H_cancel, HARRAY n_throw_child) = 0
$heap_owners(H_cancel, HCELL n_throw_leaf) = 1 /\ $heap_valid(H_cancel)
S_cancel.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full = $drive(S_cancel, 10000)
S_throw_full.COMPLETION = NORMAL /\ S_throw_full.TODO = eps /\ S_throw_full.CURRENT = eps /\ S_throw_full.FRAMES = eps
$qal_output(S_throw_full.EVENTS) = $ptascii("T;M;H:1;C:stop:1:1:1:1;")
S_throw_full.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full.STORE[n_throw_source] = DEFINED (PINT 7) /\ S_throw_full.STORE[n_throw_leaf] = DEFINED pvalue_throw_current /\ S_throw_full.STORE[n_throw_keeper] = DEFINED pvalue_throw_original
$heap_valid($heap_graph(S_throw_full)) /\ $call_descriptors_valid(S_throw_full)
""".strip().splitlines()

OBJECT = r"""
S_object_pre = $qal_seek(S_object_initial, 1, 4000)[.COMPLETION = NORMAL]
$qal_ready(S_object_pre, 1)
S_object_pre.TODO = (CALL_SEND pcalltarget_object eps 0 eps (porigin_object_call) z_object) :: ptask_object_tail*
S_object_pre.RESULT = KNOWN (PARRAY n_object_root)
S_object_pre.ARRAYS[n_object_root].ITEMS = [ENTRY (KSTRING ($ptascii("object"))) (DIRECT (POBJECT n_object))]
$objectprops_record_at(S_object_pre.OBJECTPROPS, n_object) = (pobjectprops)
pobjectprops.SLOTS = [ppropertyslot]
ppropertyslot.DECL = eps /\ ppropertyslot.NAME = $ptascii("value")
ppropertyslot.STATE = PROP_VALUE (DIRECT pvalue_object)
pvalue_object = PSTRING_CARRIER (REQUEST_STRING n_object_string) ($ptascii("17"))
$string_carrier_valid(S_object_pre, pvalue_object) /\ $named_reference_notice_root_value(S_object_pre, pvalue_object)
~$named_reference_notice_object_slots(pobjectprops.SLOTS)
~$named_reference_notice_object(S_object_pre, POBJECT n_object)
$positional_reference_notice_source(S_object_pre, pcalltarget_object, 0, (porigin_object_call))
~$named_reference_notice_array(S_object_pre, PARRAY n_object_root) /\ ~$positional_reference_notice_pending(S_object_pre)
S_object_fenced = $drive(S_object_pre, 1)
S_object_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_object_fenced.EVENTS = S_object_pre.EVENTS
$qal_output(S_object_fenced.EVENTS) = $ptascii("O;M;")
""".strip().splitlines()

CONTROLS = r"""
~$named_reference_notice_value(pvalue_original)
$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT pvalue_original)])
$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (ALIAS n_leaf)])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
~$named_reference_notice_array(S_notice[.STORE[n_leaf] = DEFINED pvalue_bad_id], PARRAY n_root)
~$named_reference_notice_array(S_notice[.STORE[n_leaf] = DEFINED pvalue_bad_bytes], PARRAY n_root)
~$named_reference_notice_array(S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_bad_id)]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("17")))], PARRAY n_root)
~$named_reference_notice_array(S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("17"))))]], PARRAY n_root)
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_array(S_nul[.STORE[n_leaf] = DEFINED pvalue_nul], PARRAY n_root)
~$named_reference_notice_array(S_nul[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_nul)]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.PROPREFS = [{CELL n_leaf, SOURCES eps}]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.REFCOERCIONS = [{CELL n_leaf, SITE pfunction_producer.ORIGIN, LINE 0, VALUE eps}]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.CONTAINERINITS = [{CELL n_leaf, ARRAY n_root, SITE porigin_call, LINE 0}]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.LITERALREFRETAINED = [n_leaf]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.REFCELLS = [n_private]], PARRAY n_root)
~$named_reference_notice_array(S_written, PARRAY n_private_root)
~$named_reference_notice_operand(S_written, REFERENCE n_private)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_notice, perrorcall[.RESUME = CALL_ARGS pcalltarget eps 1 ([KNOWN (PARRAY n_root)]) (porigin_call) z])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_throw = $drive(S_throw_pending, 0)
S_zero_throw.COMPLETION = BUDGET /\ S_zero_throw[.COMPLETION = NORMAL] = S_throw_pending
$drive($drive(S_zero_throw[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_throw_pending, 2)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    selected = [0, 3] if args.front else [0, 1, 2]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
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
    reached = [initial('S_initial', 0)] + RETURN + COMMON
    if args.front:
        reached += [initial('S_quiet_initial', 3)] + QUIET
        derived = FRONT
    else:
        reached += PRIVATE + [initial('S_throw_initial', 1)] + THROW + [initial('S_object_initial', 2)] + OBJECT
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), CATALOGUE, fixture, native_path, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
    paths += [ROOT / path for path in ('tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for i in selected:
        paths += [sources[i], Path(records[cases[i]['id']]['stdout']), Path(records[cases[i]['id']]['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'request-string-array-leaf-front' if args.front else 'request-string-array-leaf-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
