#!/usr/bin/env python3
"""Ground scalar parameter receives, caller cells and private Notice-cell replacement."""
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
CATALOGUE = Path(__file__).with_name('multi_cv_scalar_formal_producer_reference_notice_cases.json')

PREFIX = r"""
dec $mcsf_output(pevent*) : ptbytes
def $mcsf_output(eps) = eps
def $mcsf_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mcsf_output(pevent*)
dec $mcsf_ready(pstate, nat) : bool
def $mcsf_ready(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps 2 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("MultiCvScalarFormal57\\make"), $ptascii("MultiCvScalarFormalString57\\make")]
def $mcsf_ready(S, 1) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("MultiCvScalarFormal57\\make"), $ptascii("MultiCvScalarFormalString57\\make")]
def $mcsf_ready(S, 2) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 1) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("MultiCvScalarFormal57\\make"), $ptascii("MultiCvScalarFormalString57\\make")]
def $mcsf_ready(S, 3) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("MultiCvScalarFormal57\\make"), $ptascii("MultiCvScalarFormalString57\\make")]
def $mcsf_ready(S, 4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("MultiCvScalarFormal57\\take"), $ptascii("MultiCvScalarFormalString57\\take")]
def $mcsf_ready(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps 2 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("MultiCvScalarFormal57\\take"), $ptascii("MultiCvScalarFormalString57\\take")]
def $mcsf_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcsf_output(S.EVENTS) <- [$ptascii("I;M:1:1:1:1;H:8:0:body;F:29:17:1;R:41:31:37:1:1;"), $ptascii("S;M:1:1:1:1;H:8:0:body;F:29:37:1;R:41:31:37:1:1;")]
def $mcsf_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcsf_output(S.EVENTS) <- [$ptascii("I;M:1:1:1:1;H:8:0:body;F:29:17:1;R:41:31:37:1:1;P:43:1:1;"), $ptascii("S;M:1:1:1:1;H:8:0:body;F:29:37:1;R:41:31:37:1:1;P:43:1:1;")]
def $mcsf_ready(S, n_stage) = false -- otherwise
dec $mcsf_seek(pstate, nat, nat) : pstate
def $mcsf_seek(S, n_stage, n) = S -- if $mcsf_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcsf_seek(S, n_stage, n) = $mcsf_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcsf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcsf_seek(S, n_stage, n) = S -- otherwise
"""


def front_lines(index, case):
    first, last = case['formal_kinds']
    result = '17' if index == 0 else '37'
    lines = r"""
S_initial.COMPLETION = BUDGET
S_args = $mcsf_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$mcsf_ready(S_args, 0)
$lookup(S_args.ENV, $ptascii("x")) = (n_original_x)
$lookup(S_args.ENV, $ptascii("y")) = (n_y)
$lookup(S_args.ENV, $ptascii("yAlias")) = (n_y)
$lookup(S_args.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(S_args.ENV, $ptascii("ySnapshot")) = (n_y_snapshot)
S_args.STORE[n_original_x] = DEFINED pvalue_original
S_args.STORE[n_snapshot] = DEFINED pvalue_original
S_args.STORE[n_y] = DEFINED pvalue_y_original
S_args.STORE[n_y_snapshot] = DEFINED pvalue_y_original
S_args.TODO = (CALL_ARGS pcalltarget_producer eps 2 ([KNOWN pvalue_original, REFERENCE n_y]) (porigin_producer_call) z_producer) :: ptask_args*
$target_function(S_args, pcalltarget_producer) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.NAME = $ptascii("saved") /\ psparam_last.NAME = $ptascii("changed")
psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "FIRST_TYPE"]))]
psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "LAST_TYPE"]))]
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))] /\ ~pfunction_producer.SIGNATURE.BYREF
$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) phpType18_return phpType23 metadata_function)
phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_first_type) metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter
phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_last_type) metadata_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter
$ptlc($base64(text_first_type)) = $ptascii("FIRST_TYPE")
$ptlc($base64(text_last_type)) = $ptascii("LAST_TYPE")
phpType18_return = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("int")
H_args = $heap_graph(S_args)
$heap_owners(H_args, HCELL n_y) = 4
$heap_valid(H_args) /\ $call_descriptors_valid(S_args)
S_receive_first = $mcsf_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]
$mcsf_ready(S_receive_first, 1)
$typed_receive_valid(S_receive_first, pfunction_producer.ORIGIN, 0)
~$typed_caller_strict(S_receive_first)
$lookup(S_receive_first.ENV, $ptascii("saved")) = (n_saved)
$lookup(S_receive_first.ENV, $ptascii("changed")) = (n_y)
n_saved =/= n_original_x /\ n_saved =/= n_y /\ ~(n_saved <- S_receive_first.REFCELLS)
S_receive_first.STORE[n_saved] = DEFINED pvalue_original
S_receive_first.STORE[n_y] = DEFINED pvalue_y_original
S_receive_first.GLOBALTABLE = (psymboltable_before)
$lookup(psymboltable_before.ENV, $ptascii("x")) = (n_original_x)
S_receive_first.STORE[n_original_x] = DEFINED pvalue_original
S_received_first_budget = $drive_steps(S_receive_first, 1)
S_received_first_budget.COMPLETION = BUDGET
S_receive_last = $mcsf_seek(S_received_first_budget[.COMPLETION = NORMAL], 2, 100)[.COMPLETION = NORMAL]
$mcsf_ready(S_receive_last, 2)
$typed_receive_valid(S_receive_last, pfunction_producer.ORIGIN, 1)
~$typed_caller_strict(S_receive_last)
S_receive_last.STORE[n_saved] = DEFINED pvalue_saved
S_receive_last.STORE[n_original_x] = DEFINED pvalue_original
S_receive_last.STORE[n_y] = DEFINED pvalue_y_original
S_receive_last.STORE[n_snapshot] = DEFINED pvalue_original
S_receive_last.STORE[n_y_snapshot] = DEFINED pvalue_y_original
S_receive_last.ARRAYS = S_receive_first.ARRAYS
$parameter_backing_at(S_receive_last.PARAMETERBACKINGS, n_y) = eps
$propref_at(S_receive_last.PROPREFS, n_y) = eps
$reference_coercion_at(S_receive_last.REFCOERCIONS, n_y) = eps
S_received_last_budget = $drive_steps(S_receive_last, 1)
S_received_last_budget.COMPLETION = BUDGET
S_received = S_received_last_budget[.COMPLETION = NORMAL]
S_received.STORE[n_saved] = DEFINED pvalue_saved
S_received.STORE[n_y] = DEFINED pvalue_received_last
S_received.STORE[n_original_x] = DEFINED pvalue_original
S_received.STORE[n_y_snapshot] = DEFINED pvalue_y_original
S_received.ARRAYS = S_receive_last.ARRAYS
$node_children(S_received, HCELL n_y) = eps
$heap_owners($heap_graph(S_received), HCELL n_y) = 4
$heap_valid($heap_graph(S_received)) /\ $call_descriptors_valid(S_received)
S_return = $mcsf_seek(S_received, 3, 5000)[.COMPLETION = NORMAL]
$mcsf_ready(S_return, 3)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.STORE[n_saved] = DEFINED pvalue_saved
S_return.STORE[n_y] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("y")) = (n_y)
~((HCELL n_original_x) <- S_return.ALLOCATIONS)
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PINT RESULT_INT)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PINT RESULT_INT)) porigin_return?) :: ptask_return*
S_pre = $mcsf_seek(S_after_return, 4, 5000)[.COMPLETION = NORMAL]
$mcsf_ready(S_pre, 4)
S_pre.TODO = (CALL_SEND pcalltarget eps 1 ([REFERENCE n_y]) (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PINT RESULT_INT)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$lookup(S_pre.ENV, $ptascii("x")) = eps
$lookup(S_pre.ENV, $ptascii("y")) = (n_y)
$lookup(S_pre.ENV, $ptascii("yAlias")) = (n_y)
S_pre.STORE[n_y] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))
~((HCELL n_saved) <- S_pre.ALLOCATIONS) /\ ~((HCELL n_original_x) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("saved")) = eps /\ $lookup(S_pre.ENV, $ptascii("changed")) = eps
$heap_owners($heap_graph(S_pre), HCELL n_y) = 3
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
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
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE)
~$positional_reference_notice_pending(S_pre)
$parameter_backing_at(S_pre.PARAMETERBACKINGS, n_y) = eps
$propref_at(S_pre.PROPREFS, n_y) = eps
$reference_coercion_at(S_pre.REFCOERCIONS, n_y) = eps
""".strip().splitlines()
    if index == 0:
        lines += [
            'pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_original_string) ($ptascii("17"))', '$string_carrier_valid(S_args, pvalue_original)',
            'pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', 'pvalue_saved = PINT 17', 'pvalue_received_last = PBOOL false',
            '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEINTEGER pvalue_original', '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEBOOL pvalue_y_original',
            '$string_carrier_valid(S_pre, pvalue_original)']
    else:
        lines += ['pvalue_original = PINT 37', 'pvalue_y_original = PINT 17', 'pvalue_saved = PSTRING_CARRIER (REQUEST_STRING n_saved_string) ($ptascii("37"))', '$string_carrier_valid(S_receive_last, pvalue_saved)', 'pvalue_received_last = PFLOAT 4625478292286210048',
            '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPESTRING (PINT 37)', '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE (PFLOAT 4625478292286210048)']
    lines += ['$mcsf_output(S_pre.EVENTS) = $ptascii(' + json.dumps(('I' if index == 0 else 'S') + ';M:1:1:1:1;') + ')']
    return [line.replace('FIRST_TYPE', first).replace('LAST_TYPE', last).replace('RESULT_INT', result) for line in lines]


def full_lines(index, case):
    result = '17' if index == 0 else '37'
    lines = r"""
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 2 ([REFERENCE n_y, REFERENCE n_private]) (porigin_call) z_call
perrorcall.LINE = 8
S_notice.STORE[n_private] = DEFINED (PINT RESULT_INT)
n_private =/= n_original_x /\ n_private =/= n_y /\ n_private =/= n_saved
$error_call_valid(S_notice, perrorcall)
$node_children(S_notice, HCELL n_private) = eps
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps
$reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_valid($heap_graph(S_notice)) /\ $call_descriptors_valid(S_notice)
S_resume = $mcsf_seek(S_notice, 5, 7000)[.COMPLETION = NORMAL]
$mcsf_ready(S_resume, 5)
S_resume.TODO = (CALL_ARGS pcalltarget eps 2 ([REFERENCE n_y, REFERENCE n_private]) (porigin_call) z_call) :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("x")) = (n_new_x)
n_new_x =/= n_original_x /\ n_new_x =/= n_private /\ n_new_x =/= n_y
S_resume.STORE[n_new_x] = DEFINED (PINT 37)
S_resume.STORE[n_y] = DEFINED (PINT 29)
S_resume.STORE[n_private] = DEFINED (PINT RESULT_INT)
$heap_owners($heap_graph(S_resume), HCELL n_y) = 3
S_written = $mcsf_seek(S_resume, 6, 9000)[.COMPLETION = NORMAL]
$mcsf_ready(S_written, 6)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_written)
S_written.ARRAYS[n_written].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41))]
$node_children(S_written, HCELL n_private) = [HARRAY n_written]
$heap_owners($heap_graph(S_written), HARRAY n_written) = 1
$heap_owners($heap_graph(S_written), HCELL n_y) = 2
S_written.STORE[n_y] = DEFINED (PINT 31)
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps
$reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_retired = $mcsf_seek(S_written, 7, 6000)[.COMPLETION = NORMAL]
$mcsf_ready(S_retired, 7)
S_retired.STORE[n_private] = DEFINED (PINT 43)
$node_children(S_retired, HCELL n_private) = eps
~((HARRAY n_written) <- S_retired.ALLOCATIONS)
$heap_valid($heap_graph(S_retired)) /\ $call_descriptors_valid(S_retired)
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT 43)
S_full.STORE[n_new_x] = DEFINED (PINT 37)
S_full.STORE[n_y] = DEFINED (PINT 47)
$lookup(S_full.ENV, $ptascii("y")) = eps
$lookup(S_full.ENV, $ptascii("yAlias")) = (n_y)
$heap_owners($heap_graph(S_full), HCELL n_y) = 1
S_full.STORE[n_snapshot] = DEFINED pvalue_original
S_full.STORE[n_y_snapshot] = DEFINED pvalue_y_original
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()
    if index == 0:
        lines.append('$string_carrier_valid(S_full, pvalue_original)')
    lines.append('$mcsf_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')')
    return [line.replace('RESULT_INT', result) for line in lines]


def controls(index):
    return r"""
~$typed_return_task_valid(S_return, $(z_return + 1))
~$error_call_valid(S_notice, perrorcall[.LINE = 9])
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
$reference_notice_producer_line(S_pre, (porigin_producer), expression_producer) = 8
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = eps], psparam_last]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.BYREF = true], psparam_last]])
phpType17_nullable = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES text_first_type) metadata_first_type) metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_nullable, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = psparam_first.TYPE ++ [(PTBRANCH ([PTBUILTIN "null"]))]], psparam_last]])
phpType17_int_first = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "aW50") metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter
phpType17_int_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "aW50") metadata_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter
phpType17_untyped_first = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter
phpType17_untyped_last = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_int_first, phpType17_untyped_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]], psparam_last[.TYPE = eps]]])
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_untyped_first, phpType17_int_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = eps], psparam_last[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]])
phpType17_third = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "aW50") metadata_first_type) (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES "dGhpcmQ=") metadata_first) ABSENT (SEQUENCE eps) metadata_first_parameter
psparam_third = psparam_first[.NAME = $ptascii("third")][.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last, phpType7_first]), SEQUENCE ([phpType17_first, phpType17_last, phpType17_third]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first, psparam_last, psparam_third]])
phpType17_mixed = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "bWl4ZWQ=") metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_mixed, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]], psparam_last]])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_received = $drive(S_receive_last, 0)
S_zero_received.COMPLETION = BUDGET /\ S_zero_received[.COMPLETION = NORMAL] = S_receive_last
$drive($drive(S_zero_received[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_receive_last, 2)
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
    selected = [0, 1]
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
    for i in selected:
        conditions = [initial('S_initial', i)] + front_lines(i, cases[i])
        current_derived = []
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line.startswith('~$reference_notice_producer_arguments(') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, cases[i])
            current_derived = controls(i)
        case_specs.append('dec $mcsf_case' + str(i) + '() : bool\ndef $mcsf_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
        reached += conditions
        derived += current_derived
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $mcsf_case' + str(i) + '()\n' for i in selected))
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'multi-cv-scalar-formal-producer-front' if args.front else 'multi-cv-scalar-formal-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
