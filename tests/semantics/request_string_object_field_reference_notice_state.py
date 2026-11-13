#!/usr/bin/env python3
"""Ground authentic stdClass REQUEST fields and existing object-owner contours before Notices."""
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
CATALOGUE = Path(__file__).with_name('request_string_object_field_reference_notice_cases.json')

PREFIX = r"""
dec $qof_output(pevent*) : ptbytes
def $qof_output(eps) = eps
def $qof_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $qof_output(pevent*)
dec $qof_ready(pstate, nat) : bool
def $qof_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("RequestObjectFieldsNotice42\\make") \/ pcallcontext.NAME = $ptascii("RequestObjectFieldsThrow42\\make")
def $qof_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("RequestObjectFieldsNotice42\\take") \/ pfunction.NAME = $ptascii("RequestObjectFieldsThrow42\\take") \/ pfunction.NAME = $ptascii("RequestObjectAliasFieldControl42\\take")
def $qof_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $qof_output(S.EVENTS) = $ptascii("O;M:1;H:1;")
def $qof_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $lookup(S.ENV, $ptascii("r")) = (n_private)
  -- if S.STORE[n_private] = DEFINED (POBJECT n_object)
  -- if $qof_output(S.EVENTS) = $ptascii("O;M:1;H:1;F:1:1;")
def $qof_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $qof_output(S.EVENTS) = $ptascii("O;M:1;H:1;F:1:1;R:29:29:1:1:1;P:1:29;")
def $qof_ready(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $qof_ready(S, n_stage) = false -- otherwise
dec $qof_seek(pstate, nat, nat) : pstate
def $qof_seek(S, n_stage, n) = S
  -- if $qof_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $qof_seek(S, n_stage, n) = $qof_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$qof_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $qof_seek(S, n_stage, n) = $qof_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$qof_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $qof_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $qof_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]
$qof_ready(S_return, 0)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("RequestObjectFieldsNotice42\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
$lookup(S_return.ENV, $ptascii("input")) = (n_source)
S_return.STORE[n_source] = DEFINED (POBJECT n_object)
n_source <- S_return.REFCELLS
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
S_return.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops)
pobjectprops.SLOTS = [ppropertyslot]
ppropertyslot.DECL = eps /\ ppropertyslot.NAME = $ptascii("value")
ppropertyslot.STATE = PROP_VALUE (DIRECT pvalue_original)
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) = [HOBJECT n_object]
$node_children(S_after_return, HOBJECT n_object) = eps
$node_children(S_after_return, HCELL n_snapshot) = eps
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source) = 3 /\ $heap_owners(H_return, HCELL n_keeper) = 1 /\ $heap_owners(H_return, HCELL n_snapshot) = 1
$heap_owners(H_return, HOBJECT n_object) = 3
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $qof_seek(S_after_return, 1, 2000)[.COMPLETION = NORMAL]
$qof_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 ABSENT phpType23 metadata_function)
$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
pssignature = pfunction_producer.SIGNATURE
pssignature.PARAMETERS = [psparam]
psparam.BYREF /\ psparam.TYPE = eps /\ ~psparam.VARIADIC /\ psparam.REQUIRED /\ psparam.DEFAULT = PSNONE
$reference_notice_producer_header(phpType6_producer, phpType16, ABSENT, pssignature)
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(S_pre.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S_pre.ENV, $ptascii("snapshot")) = (n_snapshot)
S_pre.STORE[n_source] = DEFINED (POBJECT n_object) /\ S_pre.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops)
S_pre.OBJECTS[n_object] = STDINSTANCE
$objectprops_valid(S_pre, [pobjectprops]) /\ $property_unique_names(pobjectprops.SLOTS)
$string_carrier_valid(S_pre, pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_original)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps
$node_children(S_pre, HOBJECT n_object) = eps
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
~$weakmap_key_waiting(S_pre, n_object)
$qof_output(S_pre.EVENTS) = $ptascii("O;M:1;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source) = 2 /\ $heap_owners(H_pre, HOBJECT n_object) = 3
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

THROW = r"""
S_throw_return = $qof_seek(S_throw_initial, 0, 3000)[.COMPLETION = NORMAL]
$qof_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("RequestObjectFieldsThrow42\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (POBJECT n_throw_object)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
S_throw_after_return = $drive(S_throw_return, 1)[.COMPLETION = NORMAL]
S_throw_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_throw_object)) porigin_throw_return?) :: ptask_throw_return_tail*
H_throw_return = $heap_graph(S_throw_after_return)
$heap_owners(H_throw_return, HOBJECT n_throw_object) = 2 /\ $heap_valid(H_throw_return)
S_throw_pre = $qof_seek(S_throw_after_return, 1, 3000)[.COMPLETION = NORMAL]
$qof_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (POBJECT n_throw_object)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps
$lookup(S_throw_pre.ENV, $ptascii("snapshot")) = (n_throw_snapshot)
S_throw_pre.STORE[n_throw_source] = DEFINED (PINT 7)
S_throw_pre.STORE[n_throw_snapshot] = DEFINED pvalue_throw
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_pre, pvalue_throw)
$objectprops_record_at(S_throw_pre.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
pobjectprops_throw.SLOTS = [ppropertyslot_throw]
ppropertyslot_throw.DECL = eps /\ ppropertyslot_throw.NAME = $ptascii("value")
ppropertyslot_throw.STATE = PROP_VALUE (DIRECT pvalue_throw)
$objectprops_valid(S_throw_pre, [pobjectprops_throw])
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$qof_output(S_throw_pre.EVENTS) = $ptascii("T;M;")
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HOBJECT n_throw_object) = 1
$node_children(S_throw_pre, HOBJECT n_throw_object) = eps /\ $node_children(S_throw_pre, HCELL n_throw_snapshot) = eps
$heap_valid(H_throw_pre) /\ $call_descriptors_valid(S_throw_pre)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object)
~$named_reference_notice_operand(S_pre, KNOWN (POBJECT n_object))
~$positional_reference_notice_pending(S_pre)
pvalue_interned = PSTRING_CARRIER INTERNED_STRING ($ptascii("17"))
S_interned = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_object, [ppropertyslot[.STATE = PROP_VALUE (DIRECT pvalue_interned)]])]
$named_reference_notice_object(S_interned, POBJECT n_object) /\ $positional_reference_notice_pending(S_interned)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (POBJECT n_object)]
~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ ~$positional_reference_notice_pending(S_throw_pre)
S_throw_interned = S_throw_pre[.OBJECTPROPS = $objectprops_set(S_throw_pre.OBJECTPROPS, n_throw_object, [ppropertyslot_throw[.STATE = PROP_VALUE (DIRECT pvalue_interned)]])]
$named_reference_notice_object(S_throw_interned, POBJECT n_throw_object) /\ $positional_reference_notice_pending(S_throw_interned)
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
$named_reference_notice_object(S_pre, POBJECT n_object)
$named_reference_notice_operand(S_pre, KNOWN (POBJECT n_object)) /\ $positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source /\ n_private =/= n_keeper /\ n_private =/= n_snapshot
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]
$named_reference_notice_operand(S_notice, REFERENCE n_private) /\ $error_call_valid(S_notice, perrorcall)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HOBJECT n_object) = 3
$heap_valid(H_notice)
S_resume = $qof_seek(S_notice, 2, 4000)[.COMPLETION = NORMAL]
$qof_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (POBJECT n_object) /\ S_resume.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_resume.STORE[n_source] = DEFINED (PINT 7) /\ S_resume.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_resume.OBJECTPROPS, n_object) = (pobjectprops_resume)
pobjectprops_resume.SLOTS = [ppropertyslot[.STATE = PROP_VALUE (DIRECT pvalue_current)]]
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
n_current_string =/= n_string
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_original)
$named_reference_notice_object(S_resume, POBJECT n_object) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HOBJECT n_object) = 2 /\ $heap_owners(H_resume, HCELL n_private) = 1
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $qof_seek(S_resume, 3, 5000)[.COMPLETION = NORMAL]
$qof_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (POBJECT n_object) /\ S_written.STORE[n_keeper] = DEFINED (POBJECT n_object)
n_keeper <- S_written.REFCELLS
$objectprops_record_at(S_written.OBJECTPROPS, n_object) = (pobjectprops_written)
pobjectprops_written.SLOTS = [ppropertyslot[.STATE = PROP_VALUE (DIRECT (PSTRING ($ptascii("29"))))]]
S_written.STORE[n_source] = DEFINED (PINT 7) /\ S_written.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HOBJECT n_object) = 2 /\ $heap_owners(H_written, HCELL n_private) = 1
$node_children(S_written, HOBJECT n_object) = eps /\ $heap_valid(H_written)
S_one = $qof_seek(S_written, 4, 4000)[.COMPLETION = NORMAL]
$qof_ready(S_one, 4)
S_one.STORE[n_private] = DEFINED (PINT 31) /\ S_one.STORE[n_keeper] = DEFINED (POBJECT n_object)
H_one = $heap_graph(S_one)
$heap_owners(H_one, HOBJECT n_object) = 1 /\ $heap_owners(H_one, HCELL n_keeper) = 1
$node_children(S_one, HCELL n_private) = eps /\ $heap_valid(H_one)
S_full = $drive(S_one, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$qof_output(S_full.EVENTS) = $ptascii("O;M:1;H:1;F:1:1;R:29:29:1:1:1;P:1:29;Q:1:1;")
$lookup(S_full.ENV, $ptascii("keeper")) = eps
~((HCELL n_keeper) <- S_full.ALLOCATIONS) /\ ~((HOBJECT n_object) <- S_full.ALLOCATIONS)
S_full.STORE[n_private] = DEFINED (PINT 31) /\ S_full.STORE[n_source] = DEFINED (PINT 7) /\ S_full.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_full, pvalue_original)
$heap_owners($heap_graph(S_full), HOBJECT n_object) = 0
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CANCEL = r"""
$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ $positional_reference_notice_pending(S_throw_pre)
n_throw_private = |S_throw_pre.STORE|
$lookup(S_throw_pre.ENV, $ptascii("r")) = (n_throw_r)
S_throw_pre.STORE[n_throw_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))
S_throw_notice = $drive(S_throw_pre, 1)[.COMPLETION = NORMAL]
S_throw_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_throw) :: ptask_throw_notice*
perrorcall_throw.RESUME = CALL_ARGS pcalltarget_throw eps 1 ([REFERENCE n_throw_private]) (porigin_throw_call) z_throw
S_throw_notice.STORE[n_throw_private] = DEFINED (POBJECT n_throw_object)
$error_call_valid(S_throw_notice, perrorcall_throw)
S_throw_pending = $qof_seek(S_throw_notice, 5, 4000)[.COMPLETION = NORMAL]
$qof_ready(S_throw_pending, 5)
S_throw_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw_pending*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw_pending, perrorcall_entered) /\ $throwable_live(S_throw_pending, n_exception)
H_throw_pending = $heap_graph(S_throw_pending)
$heap_owners(H_throw_pending, HCELL n_throw_private) = 1 /\ $heap_owners(H_throw_pending, HOBJECT n_throw_object) = 1
$heap_valid(H_throw_pending)
S_cancel = $drive(S_throw_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS) /\ ~((HOBJECT n_throw_object) <- S_cancel.ALLOCATIONS)
$heap_owners($heap_graph(S_cancel), HOBJECT n_throw_object) = 0
S_cancel.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
S_throw_full = $drive(S_cancel, 10000)
S_throw_full.COMPLETION = NORMAL /\ S_throw_full.TODO = eps /\ S_throw_full.CURRENT = eps /\ S_throw_full.FRAMES = eps
$qof_output(S_throw_full.EVENTS) = $ptascii("T;M;H;C:stop:1:1:1;")
S_throw_full.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full.STORE[n_throw_source] = DEFINED (PINT 7) /\ S_throw_full.STORE[n_throw_snapshot] = DEFINED pvalue_throw
$string_carrier_valid(S_throw_full, pvalue_throw)
$heap_valid($heap_graph(S_throw_full)) /\ $call_descriptors_valid(S_throw_full)
""".strip().splitlines()

CONTROLS = r"""
$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
~$named_reference_notice_object_slots(S_notice, [ppropertyslot[.STATE = PROP_VALUE (DIRECT pvalue_bad_id)]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot[.STATE = PROP_VALUE (DIRECT pvalue_bad_bytes)]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot[.STATE = PROP_VALUE (DIRECT (PSTRING ($ptascii("17"))))]])
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_object_slots(S_nul, [ppropertyslot[.STATE = PROP_VALUE (DIRECT pvalue_nul)]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot[.STATE = PROP_VALUE (ALIAS n_snapshot)]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot[.NAME = [0]]])
~$named_reference_notice_object(S_notice[.OBJECTPROPS = $objectprops_set(S_notice.OBJECTPROPS, n_object, [ppropertyslot[.STATE = PROP_VALUE (DIRECT pvalue_bad_id)]])], POBJECT n_object)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HOBJECT n_object]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.DESTRUCTION.CALLED = [n_object]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.ALLOCATIONS = eps], POBJECT n_object)
~$named_reference_notice_operand(S_notice[.PROPREFS = [{CELL n_private, SOURCES eps}]], REFERENCE n_private)
~$named_reference_notice_operand(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_private, LINE z, VALUE eps}]], REFERENCE n_private)
~$named_reference_notice_object(S_written, POBJECT n_object)
~$named_reference_notice_operand(S_written, REFERENCE n_private)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_notice, perrorcall[.RESUME = CALL_ARGS pcalltarget eps 1 ([KNOWN (POBJECT n_object)]) (porigin_call) z])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_throw = $drive(S_throw_pending, 0)
S_zero_throw.COMPLETION = BUDGET /\ S_zero_throw[.COMPLETION = NORMAL] = S_throw_pending
$drive($drive(S_zero_throw[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_throw_pending, 2)
""".strip().splitlines()

ALIAS = r"""
S_alias_pre = $qof_seek(S_alias_initial, 1, 3000)[.COMPLETION = NORMAL]
$qof_ready(S_alias_pre, 1)
S_alias_pre.TODO = (CALL_SEND pcalltarget_alias eps 0 eps (porigin_alias_call) z_alias) :: ptask_alias_tail*
S_alias_pre.RESULT = KNOWN (POBJECT n_alias_object)
$objectprops_record_at(S_alias_pre.OBJECTPROPS, n_alias_object) = (pobjectprops_alias)
pobjectprops_alias.SLOTS = [ppropertyslot_alias]
ppropertyslot_alias.STATE = PROP_VALUE (ALIAS n_alias_leaf)
S_alias_pre.STORE[n_alias_leaf] = DEFINED pvalue_alias
pvalue_alias = PSTRING_CARRIER (REQUEST_STRING n_alias_string) ($ptascii("17"))
$string_carrier_valid(S_alias_pre, pvalue_alias) /\ $call_reference_operand_valid(S_alias_pre, REFERENCE n_alias_leaf)
$objectprops_valid(S_alias_pre, [pobjectprops_alias])
$node_children(S_alias_pre, HOBJECT n_alias_object) = [HCELL n_alias_leaf]
~$named_reference_notice_object_slots(S_alias_pre, pobjectprops_alias.SLOTS)
~$named_reference_notice_object(S_alias_pre, POBJECT n_alias_object)
$positional_reference_notice_source(S_alias_pre, pcalltarget_alias, 0, (porigin_alias_call))
~$positional_reference_notice_pending(S_alias_pre)
S_alias_fenced = $drive(S_alias_pre, 1)
S_alias_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_alias_fenced.EVENTS = S_alias_pre.EVENTS
$qof_output(S_alias_fenced.EVENTS) = $ptascii("A;M;")
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
    selected = [0, 1] if args.front else [0, 1, 2]
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
    reached = [initial('S_initial', 0)] + RETURN + COMMON
    if args.front:
        reached += [initial('S_throw_initial', 1)] + THROW
        derived = FRONT
    else:
        reached += PRIVATE + [initial('S_throw_initial', 1)] + THROW + CANCEL + [initial('S_alias_initial', 2)] + ALIAS
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'request-string-object-field-front' if args.front else 'request-string-object-field-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
