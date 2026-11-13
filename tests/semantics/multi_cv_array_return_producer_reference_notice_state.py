#!/usr/bin/env python3
"""Ground multiple-CV array return verification, formal retirement and TypeError priority."""
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
CATALOGUE = Path(__file__).with_name('multi_cv_array_return_producer_reference_notice_cases.json')

PREFIX = r"""
dec $mcar_output(pevent*) : ptbytes
def $mcar_output(eps) = eps
def $mcar_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mcar_output(pevent*)
dec $mcar_ready(pstate, nat) : bool
def $mcar_ready(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget phpType7* 2 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("MultiCvArrayReturn50\\make"), $ptascii("MultiCvArrayThrow50\\make"), $ptascii("MultiCvArrayPriority50\\make")]
def $mcar_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("MultiCvArrayReturn50\\make"), $ptascii("MultiCvArrayThrow50\\make"), $ptascii("MultiCvArrayPriority50\\make")]
def $mcar_ready(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("MultiCvArrayReturn50\\take"), $ptascii("MultiCvArrayThrow50\\take")]

def $mcar_ready(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps 2 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("MultiCvArrayReturn50\\take")
def $mcar_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcar_output(S.EVENTS) = $ptascii("A;M:17:23:0;H:8:0:23;F:29:17;R:X7:17:31:37:1;")
def $mcar_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcar_output(S.EVENTS) = $ptascii("A;M:17:23:0;H:8:0:23;F:29:17;R:X7:17:31:37:1;P:41:17;")
def $mcar_ready(S, 6) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $mcar_ready(S, n_stage) = false -- otherwise
dec $mcar_seek(pstate, nat, nat) : pstate
def $mcar_seek(S, n_stage, n) = S -- if $mcar_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcar_seek(S, n_stage, n) = $mcar_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcar_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcar_seek(S, n_stage, n) = S -- otherwise
"""

BASE = r"""
S_initial.COMPLETION = BUDGET
S_args = $mcar_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$mcar_ready(S_args, 0)
$lookup(S_args.ENV, $ptascii("x")) = (n_original_x)
$lookup(S_args.ENV, $ptascii("y")) = (n_y)
$lookup(S_args.ENV, $ptascii("yAlias")) = (n_y)
$lookup(S_args.ENV, $ptascii("snapshot")) = (n_snapshot)
S_args.STORE[n_original_x] = DEFINED (PARRAY n_root)
S_args.STORE[n_y] = DEFINED (PINT 5)
S_args.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_args, pvalue_original)
S_args.TODO = (CALL_ARGS pcalltarget_producer eps 2 ([KNOWN (PARRAY n_root), REFERENCE n_y]) (porigin_producer_call) z_producer) :: ptask_args*
$target_function(S_args, pcalltarget_producer) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.NAME = $ptascii("saved") /\ psparam_last.NAME = $ptascii("changed")
psparam_first.TYPE = eps /\ psparam_last.TYPE = eps
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~pfunction_producer.SIGNATURE.BYREF
$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) phpType18_return phpType23 metadata_function)
S_args.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original)]
phpType18_return = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("array")
H_args = $heap_graph(S_args)
$heap_owners(H_args, HARRAY n_root) = ARG_OWNERS /\ $heap_owners(H_args, HCELL n_y) = 4
$heap_valid(H_args) /\ $call_descriptors_valid(S_args)
S_return = $mcar_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]
$mcar_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
$lookup(S_return.ENV, $ptascii("saved")) = (n_saved)
$lookup(S_return.ENV, $ptascii("changed")) = (n_y)
n_saved =/= n_original_x /\ n_saved =/= n_y /\ ~(n_saved <- S_return.REFCELLS)
S_return.STORE[n_saved] = DEFINED (PARRAY n_root)
S_return.STORE[n_y] = DEFINED (PINT 23)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("y")) = (n_y)
$lookup(psymboltable_caller.ENV, $ptascii("yAlias")) = (n_y)
$typed_return_task_valid(S_return, z_return)
H_formals = $heap_graph(S_return)
$heap_owners(H_formals, HARRAY n_root) = FORMAL_OWNERS /\ $heap_owners(H_formals, HCELL n_y) = 4
$heap_valid(H_formals) /\ $call_descriptors_valid(S_return)
""".strip().splitlines()

VERIFY = r"""
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.ALLOCATIONS = S_return.ALLOCATIONS /\ S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
$heap_valid($heap_graph(S_checked))
""".strip().splitlines()

CONTINUE = r"""
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HARRAY n_root) = RETURN_OWNERS
$heap_valid(H_return)
S_pre = $mcar_seek(S_after_return, 2, 5000)[.COMPLETION = NORMAL]
$mcar_ready(S_pre, 2)
S_pre.TODO = (CALL_SEND pcalltarget eps 1 ([REFERENCE n_y]) (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$lookup(S_pre.ENV, $ptascii("x")) = eps
$lookup(S_pre.ENV, $ptascii("y")) = (n_y)
S_pre.STORE[n_y] = DEFINED (PINT 23)
~((HCELL n_saved) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("saved")) = eps /\ $lookup(S_pre.ENV, $ptascii("changed")) = eps
$named_reference_notice_array(S_pre, PARRAY n_root)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = PRE_OWNERS /\ $heap_owners(H_pre, HCELL n_y) = 3
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$call_argument_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$call_argument_expression(S_pre, (porigin_call), 1) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE ([phpType7_first, phpType7_last])) metadata_call
phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg
phpType7_last = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last_arg
expression_first = NExprVariable (BYTES text_first) metadata_first
expression_last = NExprVariable (BYTES text_last) metadata_last
$reference_cv(expression_first) = ($ptascii("x"))
$reference_cv(expression_last) = ($ptascii("y"))
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression_last)
$source_line(metadata_first) = 8 /\ $source_line(metadata_last) = 9
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = 8
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE)
~$positional_reference_notice_pending(S_pre)
""".strip().splitlines()

COPY = r"""
$lookup(S_args.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
S_args.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS
""".strip().splitlines()

SOLE = r"""
$lookup(S_args.ENV, $ptascii("copy")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = eps
S_pre.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS
""".strip().splitlines()

PRIORITY = r"""
$lookup(S_args.ENV, $ptascii("r")) = (n_r)
S_args.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))
$lookup(S_args.ENV, $ptascii("copy")) = (n_copy)
S_args.STORE[n_copy] = DEFINED (PARRAY n_root)
S_rejected = $typed_return_value(S_return, z_return)
S_rejected.COMPLETION = THROWN "TypeError" ($ptascii("MultiCvArrayPriority50\\make(): Return value must be of type array, int returned")) z_return
S_rejected.STORE = S_return.STORE /\ S_rejected.ARRAYS = S_return.ARRAYS
$mcar_output(S_rejected.EVENTS) = $ptascii("P;M:17:23:0;")
S_priority_full = $drive(S_return, 10000)
S_priority_full.COMPLETION = NORMAL /\ S_priority_full.TODO = eps /\ S_priority_full.CURRENT = eps /\ S_priority_full.FRAMES = eps
$lookup(S_priority_full.ENV, $ptascii("r")) = (n_r)
S_priority_full.STORE[n_r] = S_args.STORE[n_r]
$lookup(S_priority_full.ENV, $ptascii("x")) = eps
$lookup(S_priority_full.ENV, $ptascii("copy")) = eps
$lookup(S_priority_full.ENV, $ptascii("y")) = (n_y)
$lookup(S_priority_full.ENV, $ptascii("yAlias")) = (n_y)
S_priority_full.STORE[n_y] = DEFINED (PINT 31)
~((HCELL n_original_x) <- S_priority_full.ALLOCATIONS) /\ ~((HCELL n_saved) <- S_priority_full.ALLOCATIONS) /\ ~((HCELL n_copy) <- S_priority_full.ALLOCATIONS)
$lookup(S_priority_full.ENV, $ptascii("e")) = (n_exception_cv)
S_priority_full.STORE[n_exception_cv] = DEFINED (POBJECT n_exception)
$throwable_live(S_priority_full, n_exception)
(HARRAY n_root) <- $heap_reach([HOBJECT n_exception], eps, $allocation_edges(S_priority_full, S_priority_full.ALLOCATIONS))
$heap_owners($heap_graph(S_priority_full), HARRAY n_root) = 1
$heap_owners($heap_graph(S_priority_full), HCELL n_y) = 2
S_priority_full.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_priority_full, pvalue_original)
$heap_valid($heap_graph(S_priority_full)) /\ $call_descriptors_valid(S_priority_full)
""".strip().splitlines()

PRIVATE = r"""
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 2 ([REFERENCE n_y, REFERENCE n_private]) (porigin_call) z_call
perrorcall.LINE = 8
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
n_private =/= n_original_x /\ n_private =/= n_y /\ n_private =/= n_saved
$error_call_valid(S_notice, perrorcall)
$lookup(S_notice.ENV, $ptascii("x")) = eps
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HARRAY n_root) = PRE_OWNERS /\ $heap_owners(H_notice, HCELL n_y) = 3
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps
$reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
""".strip().splitlines()

NORMAL = r"""
S_resume = $mcar_seek(S_notice, 3, 7000)[.COMPLETION = NORMAL]
$mcar_ready(S_resume, 3)
S_resume.TODO = (CALL_ARGS pcalltarget eps 2 ([REFERENCE n_y, REFERENCE n_private]) (porigin_call) z_call) :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("x")) = (n_new_x)
n_new_x =/= n_original_x /\ n_new_x =/= n_private /\ n_new_x =/= n_y
$lookup(S_resume.ENV, $ptascii("y")) = (n_y)
$lookup(S_resume.ENV, $ptascii("yAlias")) = (n_y)
S_resume.STORE[n_new_x] = DEFINED (PINT 37) /\ S_resume.STORE[n_y] = DEFINED (PINT 29)
S_resume.STORE[n_private] = DEFINED (PARRAY n_root)
S_resume.STORE[n_copy] = DEFINED (PARRAY n_root)
S_resume.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS
S_resume.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_resume, pvalue_original)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1 /\ $heap_owners(H_resume, HARRAY n_root) = 2 /\ $heap_owners(H_resume, HCELL n_y) = 3
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $mcar_seek(S_resume, 4, 9000)[.COMPLETION = NORMAL]
$mcar_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_current)
n_current =/= n_root
S_written.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("X7"))))]
S_written.STORE[n_copy] = DEFINED (PARRAY n_root)
S_written.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS
S_written.STORE[n_new_x] = DEFINED (PINT 37) /\ S_written.STORE[n_y] = DEFINED (PINT 31)
S_written.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_written, pvalue_original)
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps
$reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
H_written = $heap_graph(S_written)
$heap_owners(H_written, HCELL n_private) = 1 /\ $heap_owners(H_written, HARRAY n_current) = 1 /\ $heap_owners(H_written, HARRAY n_root) = 1 /\ $heap_owners(H_written, HCELL n_y) = 2
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_retired = $mcar_seek(S_written, 5, 6000)[.COMPLETION = NORMAL]
$mcar_ready(S_retired, 5)
S_retired.STORE[n_private] = DEFINED (PINT 41)
~((HARRAY n_current) <- S_retired.ALLOCATIONS)
S_retired.STORE[n_copy] = DEFINED (PARRAY n_root)
S_retired.ARRAYS[n_root].ITEMS = S_args.ARRAYS[n_root].ITEMS
$node_children(S_retired, HCELL n_private) = eps
$heap_owners($heap_graph(S_retired), HARRAY n_root) = 1
$heap_valid($heap_graph(S_retired)) /\ $call_descriptors_valid(S_retired)
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT 41) /\ S_full.STORE[n_new_x] = DEFINED (PINT 37) /\ S_full.STORE[n_y] = DEFINED (PINT 43)
$lookup(S_full.ENV, $ptascii("y")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("yAlias")) = (n_y)
~((HCELL n_original_x) <- S_full.ALLOCATIONS) /\ ~((HCELL n_saved) <- S_full.ALLOCATIONS) /\ ~((HCELL n_copy) <- S_full.ALLOCATIONS)
~((HARRAY n_root) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_current) <- S_full.ALLOCATIONS)
$heap_owners($heap_graph(S_full), HCELL n_y) = 1
S_full.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_full, pvalue_original)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CANCEL = r"""
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
S_pre.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))
S_pending = $mcar_seek(S_notice, 6, 7000)[.COMPLETION = NORMAL]
$mcar_ready(S_pending, 6)
S_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_pending*
perrorcall_entered.RESUME = perrorcall.RESUME
$error_entered_call_valid(S_pending, perrorcall_entered) /\ $throwable_live(S_pending, n_exception)
H_pending = $heap_graph(S_pending)
$heap_owners(H_pending, HCELL n_private) = 1 /\ $heap_owners(H_pending, HARRAY n_root) = 1 /\ $heap_owners(H_pending, HCELL n_y) = 3
$heap_valid(H_pending)
S_cancel = $drive(S_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_private) <- S_cancel.ALLOCATIONS) /\ ~((HARRAY n_root) <- S_cancel.ALLOCATIONS)
$lookup(S_cancel.ENV, $ptascii("r")) = (n_r)
S_cancel.STORE[n_r] = S_pre.STORE[n_r]
$heap_owners($heap_graph(S_cancel), HCELL n_y) = 2
$lookup(S_cancel.ENV, $ptascii("x")) = eps
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
S_full = $drive(S_cancel, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_r)
S_full.STORE[n_r] = S_pre.STORE[n_r]
$lookup(S_full.ENV, $ptascii("x")) = eps
$lookup(S_full.ENV, $ptascii("yAlias")) = (n_y)
S_full.STORE[n_y] = DEFINED (PINT 31)
S_full.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_full, pvalue_original)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CONTROLS = r"""
~$typed_return_task_valid(S_return, $(z_return + 1))
~$error_call_valid(S_notice, perrorcall[.LINE = 9])
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$named_reference_notice_array(S_written, PARRAY n_current)
$reference_notice_producer_line(S_pre, (porigin_producer), expression_producer) = 8
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ABSENT, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES "aW50") metadata_return, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]])
$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_retired, 2)
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_paths = [path.resolve() for path in args.native_report]
    natives = [json.loads(path.read_bytes()) for path in native_paths]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {}
    for native in natives:
        for row in native['records']:
            assert row['id'] not in records
            records[row['id']] = row
    selected = [0, 1, 2]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for native in natives:
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
    case_specs = []
    reached = []
    derived = []
    for i in (0, 1, 2):
        conditions = [initial('S_initial', i)] + BASE
        if i < 2:
            conditions += VERIFY + CONTINUE + (COPY if i == 0 else SOLE)
            if not args.front:
                conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += ['$mcar_output(S_pre.EVENTS) = $ptascii(' + json.dumps(('A' if i == 0 else 'T') + ';M:17:23:0;') + ')']
        else:
            conditions += PRIORITY + ['$mcar_output(S_priority_full.EVENTS) = $ptascii(' + json.dumps(cases[i]['native_stdout']) + ')']
        current_derived = []
        if not args.front and i < 2:
            conditions += PRIVATE + (NORMAL if i == 0 else CANCEL)
            conditions += ['$mcar_output(S_full.EVENTS) = $ptascii(' + json.dumps(cases[i]['native_stdout']) + ')']
            if i == 0: current_derived = CONTROLS
        derived += current_derived
        replacements = {'ARG_OWNERS': '2' if i == 1 else '3', 'FORMAL_OWNERS': '1' if i == 1 else '2', 'RETURN_OWNERS': '2' if i == 1 else '3', 'PRE_OWNERS': '1' if i == 1 else '2'}
        for old, new in replacements.items():
            conditions = [line.replace(old, new) for line in conditions]
        case_specs.append('dec $mcar_case' + str(i) + '() : bool\ndef $mcar_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
        reached += conditions
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $mcar_case0()\n  -- if $mcar_case1()\n  -- if $mcar_case2()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), CATALOGUE, fixture, *native_paths, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'multi-cv-array-return-producer-front' if args.front else 'multi-cv-array-return-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
