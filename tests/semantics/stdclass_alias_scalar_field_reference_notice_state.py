#!/usr/bin/env python3
"""Ground scalar ALIAS fields, property rebinding, physical edges and last-owner cancellation."""
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
CATALOGUE = Path(__file__).with_name('stdclass_alias_scalar_field_reference_notice_cases.json')

PREFIX = r"""
dec $asf_output(pevent*) : ptbytes
def $asf_output(eps) = eps
def $asf_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $asf_output(pevent*)
dec $asf_ready(pstate, nat) : bool
def $asf_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("StdClassAliasScalarNotice43\\make") \/ pcallcontext.NAME = $ptascii("StdClassAliasScalarThrow43\\make")
def $asf_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("StdClassAliasScalarNotice43\\take") \/ pfunction.NAME = $ptascii("StdClassAliasScalarThrow43\\take") \/ pfunction.NAME = $ptascii("StdClassAliasOwningControl43\\take")
def $asf_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;")
def $asf_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;F:1:1;R:29:29:29:29:31:31:1:1;")
def $asf_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;F:1:1;R:29:29:29:29:31:31:1:1;D;")
def $asf_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;F:1:1;R:29:29:29:29:31:31:1:1;D;P;")
def $asf_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;F:1:1;R:29:29:29:29:31:31:1:1;D;P;K;")
def $asf_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;F:1:1;R:29:29:29:29:31:31:1:1;D;P;K;L;")
def $asf_ready(S, 8) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $asf_output(S.EVENTS) = $ptascii("A;M:1:1;H:1:1;F:1:1;R:29:29:29:29:31:31:1:1;D;P;K;L;Z;")
def $asf_ready(S, 9) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $asf_ready(S, n_stage) = false -- otherwise
dec $asf_seek(pstate, nat, nat) : pstate
def $asf_seek(S, n_stage, n) = S
  -- if $asf_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $asf_seek(S, n_stage, n) = $asf_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$asf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $asf_seek(S, n_stage, n) = $asf_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$asf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $asf_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $asf_seek(S_initial, 0, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_return, 0)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("StdClassAliasScalarNotice43\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
$lookup(S_return.ENV, $ptascii("input")) = (n_source)
S_return.STORE[n_source] = DEFINED (POBJECT n_object)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("leafAlias")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("holder")) = (n_holder)
$lookup(psymboltable_caller.ENV, $ptascii("replacement")) = (n_replacement)
S_return.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_return.STORE[n_leaf] = DEFINED pvalue_original
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
S_return.STORE[n_replacement] = DEFINED pvalue_replacement
pvalue_replacement = PSTRING_CARRIER (REQUEST_STRING n_replacement_string) ($ptascii("31"))
$string_carrier_valid(S_return, pvalue_replacement)
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops)
pobjectprops.SLOTS = [ppropertyslot_a, ppropertyslot_b]
ppropertyslot_a = {DECL eps, NAME ($ptascii("a")), STATE (PROP_VALUE (ALIAS n_leaf))}
ppropertyslot_b = {DECL eps, NAME ($ptascii("b")), STATE (PROP_VALUE (ALIAS n_leaf))}
S_return.STORE[n_holder] = DEFINED (POBJECT n_holder_object)
$objectprops_record_at(S_return.OBJECTPROPS, n_holder_object) = (pobjectprops_holder)
pobjectprops_holder.SLOTS = [{DECL eps, NAME ($ptascii("p")), STATE (PROP_VALUE (ALIAS n_leaf))}]
$node_children(S_return, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_return, HOBJECT n_holder_object) = [HCELL n_leaf]
$node_children(S_return, HCELL n_leaf) = eps /\ $node_children(S_return, HCELL n_snapshot) = eps
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source) = 3 /\ $heap_owners(H_return, HOBJECT n_object) = 3
$heap_owners(H_return, HCELL n_leaf) = 5 /\ $heap_owners(H_return, HOBJECT n_holder_object) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $asf_seek(S_after_return, 1, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(S_pre.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("leafAlias")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("holder")) = (n_holder)
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops)
$objectprops_record_at(S_pre.OBJECTPROPS, n_holder_object) = (pobjectprops_holder)
S_pre.STORE[n_leaf] = DEFINED pvalue_original
$call_reference_operand_valid(S_pre, REFERENCE n_leaf) /\ $named_reference_notice_root_value(S_pre, pvalue_original)
$objectprops_valid(S_pre, [pobjectprops])
$property_release_nodes(pobjectprops.SLOTS) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf) /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
~$weakmap_key_waiting(S_pre, n_object)
$asf_output(S_pre.EVENTS) = $ptascii("A;M:1:1;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source) = 2 /\ $heap_owners(H_pre, HOBJECT n_object) = 3
$heap_owners(H_pre, HCELL n_leaf) = 5
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

THROW = r"""
S_throw_return = $asf_seek(S_throw_initial, 0, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("StdClassAliasScalarThrow43\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (POBJECT n_throw_object)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
pobjectprops_throw.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (ALIAS n_throw_leaf))}]
S_throw_return.STORE[n_throw_leaf] = DEFINED pvalue_throw
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_return, pvalue_throw)
S_throw_return.GLOBALTABLE = (psymboltable_throw)
$lookup(psymboltable_throw.ENV, $ptascii("leaf")) = eps
$lookup(psymboltable_throw.ENV, $ptascii("snapshot")) = (n_throw_snapshot)
$lookup(psymboltable_throw.ENV, $ptascii("watch")) = (n_throw_watch)
S_throw_return.STORE[n_throw_snapshot] = DEFINED pvalue_throw
S_throw_return.STORE[n_throw_watch] = DEFINED (POBJECT n_throw_weak)
S_throw_return.OBJECTS[n_throw_weak] = WEAKREFERENCE (n_throw_object)
$node_children(S_throw_return, HOBJECT n_throw_weak) = eps
S_throw_after_return = $drive(S_throw_return, 1)[.COMPLETION = NORMAL]
H_throw_return = $heap_graph(S_throw_after_return)
$heap_owners(H_throw_return, HOBJECT n_throw_object) = 2 /\ $heap_owners(H_throw_return, HCELL n_throw_leaf) = 1
$heap_valid(H_throw_return)
S_throw_pre = $asf_seek(S_throw_after_return, 1, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (POBJECT n_throw_object)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps
$lookup(S_throw_pre.ENV, $ptascii("leaf")) = eps
$call_reference_operand_valid(S_throw_pre, REFERENCE n_throw_leaf)
$named_reference_notice_root_value(S_throw_pre, pvalue_throw)
$objectprops_record_at(S_throw_pre.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
$objectprops_valid(S_throw_pre, [pobjectprops_throw])
$node_children(S_throw_pre, HOBJECT n_throw_object) = [HCELL n_throw_leaf] /\ $node_children(S_throw_pre, HCELL n_throw_leaf) = eps
S_throw_pre.PARAMETERBACKINGS = eps /\ S_throw_pre.PROPREFS = eps /\ S_throw_pre.REFCOERCIONS = eps /\ S_throw_pre.CONTAINERINITS = eps
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$asf_output(S_throw_pre.EVENTS) = $ptascii("T;M;")
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pre, HCELL n_throw_leaf) = 1
$heap_valid(H_throw_pre) /\ $call_descriptors_valid(S_throw_pre)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object)
~$positional_reference_notice_pending(S_pre)
S_direct = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_object, [ppropertyslot_a[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_b[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_direct, POBJECT n_object) /\ $positional_reference_notice_pending(S_direct)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (POBJECT n_object)]
~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ ~$positional_reference_notice_pending(S_throw_pre)
S_throw_direct = S_throw_pre[.OBJECTPROPS = $objectprops_set(S_throw_pre.OBJECTPROPS, n_throw_object, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_throw))}])]
$named_reference_notice_object(S_throw_direct, POBJECT n_throw_object) /\ $positional_reference_notice_pending(S_throw_direct)
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
$named_reference_notice_object(S_pre, POBJECT n_object) /\ $positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source /\ n_private =/= n_keeper /\ n_private =/= n_leaf /\ n_private =/= n_replacement
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]
$named_reference_notice_operand(S_notice, REFERENCE n_private) /\ $error_call_valid(S_notice, perrorcall)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HOBJECT n_object) = 3 /\ $heap_owners(H_notice, HCELL n_leaf) = 5
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
S_resume = $asf_seek(S_notice, 2, 5000)[.COMPLETION = NORMAL]
$asf_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (POBJECT n_object) /\ S_resume.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_resume.STORE[n_source] = DEFINED (PINT 7) /\ S_resume.STORE[n_snapshot] = DEFINED pvalue_original
S_resume.STORE[n_leaf] = DEFINED pvalue_current
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
n_current_string =/= n_string
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_original)
S_resume.STORE[n_replacement] = DEFINED pvalue_replacement
$objectprops_record_at(S_resume.OBJECTPROPS, n_object) = (pobjectprops)
$objectprops_record_at(S_resume.OBJECTPROPS, n_holder_object) = (pobjectprops_holder_resume)
pobjectprops_holder_resume.SLOTS = [{DECL eps, NAME ($ptascii("p")), STATE (PROP_VALUE (ALIAS n_replacement))}]
$node_children(S_resume, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_resume, HOBJECT n_holder_object) = [HCELL n_replacement]
$named_reference_notice_object(S_resume, POBJECT n_object) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HOBJECT n_object) = 2 /\ $heap_owners(H_resume, HCELL n_private) = 1
$heap_owners(H_resume, HCELL n_leaf) = 4 /\ $heap_owners(H_resume, HCELL n_replacement) = 2
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $asf_seek(S_resume, 3, 6000)[.COMPLETION = NORMAL]
$asf_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
$lookup(S_written.ENV, $ptascii("leaf")) = (n_leaf) /\ $lookup(S_written.ENV, $ptascii("leafAlias")) = (n_leaf)
S_written.STORE[n_private] = DEFINED (POBJECT n_object) /\ S_written.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_written.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("29")))
S_written.STORE[n_source] = DEFINED (PINT 7) /\ S_written.STORE[n_snapshot] = DEFINED pvalue_original
S_written.STORE[n_replacement] = DEFINED pvalue_replacement
$objectprops_record_at(S_written.OBJECTPROPS, n_object) = (pobjectprops)
$objectprops_record_at(S_written.OBJECTPROPS, n_holder_object) = (pobjectprops_holder_resume)
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current) /\ $string_carrier_valid(S_written, pvalue_replacement)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HOBJECT n_object) = 2 /\ $heap_owners(H_written, HCELL n_leaf) = 4 /\ $heap_owners(H_written, HCELL n_replacement) = 2
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_deleted = $asf_seek(S_written, 4, 4000)[.COMPLETION = NORMAL]
$asf_ready(S_deleted, 4)
$objectprops_record_at(S_deleted.OBJECTPROPS, n_object) = (pobjectprops_deleted)
pobjectprops_deleted.SLOTS = [ppropertyslot_a[.STATE = PROP_UNSET], ppropertyslot_b]
$node_children(S_deleted, HOBJECT n_object) = [HCELL n_leaf]
H_deleted = $heap_graph(S_deleted)
$heap_owners(H_deleted, HOBJECT n_object) = 2 /\ $heap_owners(H_deleted, HCELL n_leaf) = 3
$heap_valid(H_deleted) /\ $call_descriptors_valid(S_deleted)
S_one_object = $asf_seek(S_deleted, 5, 4000)[.COMPLETION = NORMAL]
$asf_ready(S_one_object, 5)
S_one_object.STORE[n_private] = DEFINED (PINT 37) /\ S_one_object.STORE[n_keeper] = DEFINED (POBJECT n_object)
$node_children(S_one_object, HCELL n_private) = eps
H_one_object = $heap_graph(S_one_object)
$heap_owners(H_one_object, HOBJECT n_object) = 1 /\ $heap_owners(H_one_object, HCELL n_leaf) = 3
$heap_valid(H_one_object) /\ $call_descriptors_valid(S_one_object)
S_object_retired = $asf_seek(S_one_object, 6, 4000)[.COMPLETION = NORMAL]
$asf_ready(S_object_retired, 6)
$lookup(S_object_retired.ENV, $ptascii("keeper")) = eps
~((HCELL n_keeper) <- S_object_retired.ALLOCATIONS) /\ ~((HOBJECT n_object) <- S_object_retired.ALLOCATIONS)
H_object_retired = $heap_graph(S_object_retired)
$heap_owners(H_object_retired, HOBJECT n_object) = 0 /\ $heap_owners(H_object_retired, HCELL n_leaf) = 2
$heap_valid(H_object_retired) /\ $call_descriptors_valid(S_object_retired)
S_one_cell = $asf_seek(S_object_retired, 7, 4000)[.COMPLETION = NORMAL]
$asf_ready(S_one_cell, 7)
$lookup(S_one_cell.ENV, $ptascii("leafAlias")) = eps /\ $lookup(S_one_cell.ENV, $ptascii("leaf")) = (n_leaf)
H_one_cell = $heap_graph(S_one_cell)
$heap_owners(H_one_cell, HCELL n_leaf) = 1 /\ $heap_valid(H_one_cell) /\ $call_descriptors_valid(S_one_cell)
S_cell_retired = $asf_seek(S_one_cell, 8, 4000)[.COMPLETION = NORMAL]
$asf_ready(S_cell_retired, 8)
$lookup(S_cell_retired.ENV, $ptascii("leaf")) = eps
~((HCELL n_leaf) <- S_cell_retired.ALLOCATIONS)
H_cell_retired = $heap_graph(S_cell_retired)
$heap_owners(H_cell_retired, HCELL n_leaf) = 0 /\ $heap_owners(H_cell_retired, HCELL n_replacement) = 2
$heap_valid(H_cell_retired) /\ $call_descriptors_valid(S_cell_retired)
S_full = $drive(S_cell_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source] = DEFINED (PINT 7)
S_full.STORE[n_snapshot] = DEFINED pvalue_original /\ S_full.STORE[n_replacement] = DEFINED pvalue_replacement
$string_carrier_valid(S_full, pvalue_original) /\ $string_carrier_valid(S_full, pvalue_replacement)
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
S_throw_pending = $asf_seek(S_throw_notice, 9, 4000)[.COMPLETION = NORMAL]
$asf_ready(S_throw_pending, 9)
S_throw_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw_pending*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw_pending, perrorcall_entered) /\ $throwable_live(S_throw_pending, n_exception)
H_throw_pending = $heap_graph(S_throw_pending)
$heap_owners(H_throw_pending, HCELL n_throw_private) = 1 /\ $heap_owners(H_throw_pending, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pending, HCELL n_throw_leaf) = 1
$heap_valid(H_throw_pending)
S_cancel = $drive(S_throw_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS) /\ ~((HOBJECT n_throw_object) <- S_cancel.ALLOCATIONS) /\ ~((HCELL n_throw_leaf) <- S_cancel.ALLOCATIONS)
$weakref_get(S_cancel, n_throw_weak) = PNULL
$heap_owners($heap_graph(S_cancel), HOBJECT n_throw_object) = 0 /\ $heap_owners($heap_graph(S_cancel), HCELL n_throw_leaf) = 0
S_cancel.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
S_throw_full = $drive(S_cancel, 10000)
S_throw_full.COMPLETION = NORMAL /\ S_throw_full.TODO = eps /\ S_throw_full.CURRENT = eps /\ S_throw_full.FRAMES = eps
S_throw_full.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full.STORE[n_throw_source] = DEFINED (PINT 7) /\ S_throw_full.STORE[n_throw_snapshot] = DEFINED pvalue_throw
$string_carrier_valid(S_throw_full, pvalue_throw) /\ $weakref_get(S_throw_full, n_throw_weak) = PNULL
$heap_valid($heap_graph(S_throw_full)) /\ $call_descriptors_valid(S_throw_full)
""".strip().splitlines()

OWNING = r"""
S_owning_pre = $asf_seek(S_owning_initial, 1, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_owning_pre, 1)
S_owning_pre.TODO = (CALL_SEND pcalltarget_owning eps 0 eps (porigin_owning_call) z_owning) :: ptask_owning_tail*
S_owning_pre.RESULT = KNOWN (POBJECT n_owning_object)
$objectprops_record_at(S_owning_pre.OBJECTPROPS, n_owning_object) = (pobjectprops_owning)
pobjectprops_owning.SLOTS = [ppropertyslot_owning]
ppropertyslot_owning.STATE = PROP_VALUE (ALIAS n_owning_leaf)
$call_reference_operand_valid(S_owning_pre, REFERENCE n_owning_leaf)
S_owning_pre.STORE[n_owning_leaf] = DEFINED (PARRAY n_owning_array)
$node_children(S_owning_pre, HOBJECT n_owning_object) = [HCELL n_owning_leaf]
$node_children(S_owning_pre, HCELL n_owning_leaf) = [HARRAY n_owning_array]
$positional_reference_notice_source(S_owning_pre, pcalltarget_owning, 0, (porigin_owning_call))
~$named_reference_notice_object_slots(S_owning_pre, pobjectprops_owning.SLOTS)
~$named_reference_notice_object(S_owning_pre, POBJECT n_owning_object) /\ ~$positional_reference_notice_pending(S_owning_pre)
S_owning_fenced = $drive(S_owning_pre, 1)
S_owning_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
$asf_output(S_owning_fenced.EVENTS) = $ptascii("U;M;")
S_owning_fenced.EVENTS = S_owning_pre.EVENTS /\ S_owning_fenced.STORE = S_owning_pre.STORE ++ [DEFINED (POBJECT n_owning_object)]
$heap_valid($heap_graph(S_owning_pre)) /\ $call_descriptors_valid(S_owning_pre)
""".strip().splitlines()

CONTROLS = r"""
$named_reference_notice_object_slots(S_notice, [ppropertyslot_a, ppropertyslot_b])
~$named_reference_notice_object_slots(S_notice[.REFCELLS = eps], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_leaf)], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = UNDEFINED], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.PROPREFS = [{CELL n_leaf, SOURCES eps}]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.REFCOERCIONS = [{CELL n_leaf, SITE porigin_call, LINE 0, VALUE eps}]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.CONTAINERINITS = [{CELL n_leaf, ARRAY n_owning_array, SITE porigin_call, LINE 0}]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.LITERALREFRETAINED = [n_leaf]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.LITERALREFDEBTS = [n_leaf]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.NATIVEEXCESS = [HCELL n_leaf]], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_a[.STATE = PROP_VALUE (ALIAS n_snapshot)]])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = DEFINED pvalue_bad_id], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = DEFINED pvalue_bad_bytes], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("17")))], [ppropertyslot_a])
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_object_slots(S_nul[.STORE[n_leaf] = DEFINED pvalue_nul], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_a[.NAME = [0]]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_a[.DECL = (INTERNAL_PROPERTY "stdClass" ($ptascii("a")))]])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = DEFINED (PARRAY n_owning_array)], [ppropertyslot_a])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = DEFINED (POBJECT n_object)], [ppropertyslot_a])
~$named_reference_notice_object(S_notice[.OBJECTTABLES = [{OBJECT n_object, TABLE 0}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.DESTRUCTION.CALLED = [n_object]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.GC.WORKER = (0)], POBJECT n_object)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HOBJECT n_object]], POBJECT n_object)
~$named_reference_notice_object(S_written, POBJECT n_object)
~$positional_reference_notice_source(S_pre, pcalltarget, 0, eps)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_object_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_object_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_object_retired, 2)
S_zero_throw = $drive(S_throw_pending, 0)
S_zero_throw.COMPLETION = BUDGET /\ S_zero_throw[.COMPLETION = NORMAL] = S_throw_pending
$drive($drive(S_zero_throw[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_throw_pending, 2)
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
        reached += PRIVATE + [initial('S_throw_initial', 1)] + THROW + CANCEL + [initial('S_owning_initial', 2)] + OWNING
        reached += ['$asf_output(S_full.EVENTS) = $ptascii(' + json.dumps(cases[0]['native_stdout']) + ')', '$asf_output(S_throw_full.EVENTS) = $ptascii(' + json.dumps(cases[1]['native_stdout']) + ')']
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'stdclass-alias-scalar-field-front' if args.front else 'stdclass-alias-scalar-field-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
