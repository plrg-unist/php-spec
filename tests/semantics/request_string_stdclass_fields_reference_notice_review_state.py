#!/usr/bin/env python3
"""Ground REQUEST object-field boundaries and existing quiet-object physical owners."""
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
CATALOGUE = Path(__file__).with_name('request_string_stdclass_fields_reference_notice_review_cases.json')

PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice42\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice42\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;")
def $nrpr_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;R:X3:2Z:X3:2Z:1:31:31;")
def $nrpr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;R:X3:2Z:X3:2Z:1:31:31;D:1;")
def $nrpr_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;R:X3:2Z:X3:2Z:1:31:31;D:1;O:1;")
def $nrpr_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;R:X3:2Z:X3:2Z:1:31:31;D:1;O:1;P:1;")
def $nrpr_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;R:X3:2Z:X3:2Z:1:31:31;D:1;O:1;P:1;L:1;")
def $nrpr_ready(S, 8) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;R:X3:2Z:X3:2Z:1:31:31;D:1;O:1;P:1;L:1;N:1;")
def $nrpr_ready(S, n_stage) = false -- otherwise
dec $nrpr_seek(pstate, nat, nat) : pstate
def $nrpr_seek(S, n_stage, n) = S
  -- if $nrpr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $nrpr_seek(S, n_stage, n) = $nrpr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$nrpr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nrpr_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $nrpr_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ReviewNotice42\\Primary\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("input")) = (n_formal)
$lookup(S_return.ENV, $ptascii("source")) = (n_source_return)
n_formal =/= n_source_return
~(n_formal <- S_return.REFCELLS) /\ n_source_return <- S_return.REFCELLS
S_return.STORE[n_formal] = DEFINED (PARRAY n_root)
S_return.STORE[n_source_return] = DEFINED (PINT 31)
S_return.RESULT = VARIABLE ($ptascii("input")) z_input
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("obj")) = (n_obj_cv)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("leafAlias")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("next")) = (n_next_cv)
$lookup(psymboltable_caller.ENV, $ptascii("weakOld")) = (n_weak_old_cv)
$lookup(psymboltable_caller.ENV, $ptascii("weakNew")) = (n_weak_new_cv)
S_return.STORE[n_obj_cv] = DEFINED (POBJECT n_old)
S_return.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_return.STORE[n_next_cv] = DEFINED (POBJECT n_new)
n_new =/= n_old /\ n_obj_cv =/= n_leaf /\ n_next_cv =/= n_leaf
n_leaf <- S_return.REFCELLS
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_return.OBJECTS[n_old] = STDINSTANCE /\ S_return.OBJECTS[n_new] = STDINSTANCE
$objectprops_record_at(S_return.OBJECTPROPS, n_old) = (pobjectprops_old)
$objectprops_record_at(S_return.OBJECTPROPS, n_new) = (pobjectprops_new)
pobjectprops_old.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}]
pobjectprops_new.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_next))}]
pvalue_next = PSTRING_CARRIER (REQUEST_STRING n_next_string) ($ptascii("29"))
$string_carrier_valid(S_return, pvalue_next)
$objectprops_valid(S_return, [pobjectprops_old, pobjectprops_new])
S_return.STORE[n_weak_old_cv] = DEFINED (POBJECT n_weak_old)
S_return.STORE[n_weak_new_cv] = DEFINED (POBJECT n_weak_new)
S_return.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old)
S_return.OBJECTS[n_weak_new] = WEAKREFERENCE (n_new)
$weakref_get(S_return, n_weak_old) = POBJECT n_old /\ $weakref_get(S_return, n_weak_new) = POBJECT n_new
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HOBJECT n_old) = 3 /\ $heap_owners(H_return, HOBJECT n_new) = 1
$heap_owners(H_return, HCELL n_leaf) = 3 /\ $heap_owners(H_return, HCELL n_formal) = 1
$heap_owners(H_return, HCELL n_source_return) = 3
$node_children(S_after_return, HOBJECT n_old) = eps /\ $node_children(S_after_return, HOBJECT n_new) = eps
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $nrpr_seek(S_after_return, 1, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 4))] /\ pnamedargs.NAMED = eps
$named_origin(S_pre, (porigin_call), 1) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ReviewNotice42\\Primary\\make")
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
pfunction_producer.NAME = preqbytes /\ pfunction_producer.EARLY
$call_target(S_pre, $ptascii("make"), eps) = (pfunction_global)
pfunction_global.ORIGIN =/= pfunction_producer.ORIGIN
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_pre, pfunction_producer)
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$ptlc($base64(text_type)) = $ptascii("array")
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer_call
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("array")
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)
(PDEFUNCTION n_unit pfunction_producer.ORIGIN) <- S_pre.DECLARATIONS
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$named_reference_notice_source(S_pre, pcalltarget, 1, (porigin_call))
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
S_pre.FRAMES = eps /\ S_pre.CURRENT = eps
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("input")) = eps
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
n_source_cv = n_source_return
S_pre.STORE[n_source_cv] = DEFINED (PINT 31)
$lookup(S_pre.ENV, $ptascii("obj")) = (n_obj_cv)
$lookup(S_pre.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("leafAlias")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("next")) = (n_next_cv)
S_pre.STORE[n_obj_cv] = DEFINED (POBJECT n_old) /\ S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_next_cv] = DEFINED (POBJECT n_new) /\ S_pre.STORE[n_snapshot] = DEFINED pvalue_original
S_pre.ARRAYS[n_root].ITEMS = S_return.ARRAYS[n_root].ITEMS
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
$objectprops_record_at(S_pre.OBJECTPROPS, n_new) = (pobjectprops_new)
$string_carrier_valid(S_pre, pvalue_original) /\ $string_carrier_valid(S_pre, pvalue_next)
$named_reference_notice_root_value(S_pre, pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_next)
$node_children(S_pre, HARRAY n_root) = [HOBJECT n_old, HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$node_children(S_pre, HOBJECT n_old) = eps /\ $node_children(S_pre, HOBJECT n_new) = eps
$weakref_get(S_pre, n_weak_old) = POBJECT n_old /\ $weakref_get(S_pre, n_weak_new) = POBJECT n_new
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
$object_table_at(S_pre.OBJECTTABLES, n_old) = eps /\ $object_table_at(S_pre.OBJECTTABLES, n_new) = eps
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1
$heap_owners(H_pre, HOBJECT n_old) = 3 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
$heap_owners(H_pre, HCELL n_leaf) = 3 /\ $heap_owners(H_pre, HCELL n_source_cv) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops_old.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_old)
~$named_reference_notice_object(S_pre, POBJECT n_new)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_operand(S_pre, KNOWN (PARRAY n_root))
~$named_reference_notice_pending(S_pre)
pvalue_interned = PSTRING_CARRIER INTERNED_STRING ($ptascii("17"))
pvalue_next_interned = PSTRING_CARRIER INTERNED_STRING ($ptascii("29"))
S_interned = S_pre[.OBJECTPROPS = $objectprops_set($objectprops_set(S_pre.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_interned))}]), n_new, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_next_interned))}])]
$named_reference_notice_object(S_interned, POBJECT n_old) /\ $named_reference_notice_object(S_interned, POBJECT n_new)
$named_reference_notice_array(S_interned, PARRAY n_root) /\ $named_reference_notice_pending(S_interned)
$heap_graph(S_interned) = H_pre
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS
S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]
S_fenced.ARRAYS = S_pre.ARRAYS /\ S_fenced.OBJECTPROPS = S_pre.OBJECTPROPS
""".strip().splitlines()


PRIVATE = r"""
$named_reference_notice_object_slots(S_pre, pobjectprops_old.SLOTS)
$named_reference_notice_object_slots(S_pre, pobjectprops_new.SLOTS)
$named_reference_notice_object(S_pre, POBJECT n_old) /\ $named_reference_notice_object(S_pre, POBJECT n_new)
$named_reference_notice_array(S_pre, PARRAY n_root) /\ $named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_leaf /\ n_private =/= n_source_cv /\ n_private =/= n_obj_cv /\ n_private =/= n_next_cv
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (KNOWN (PINT 4)), NAMED_SENT (REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$named_reference_notice_operand(S_notice, REFERENCE n_private) /\ $error_call_valid(S_notice, perrorcall)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HARRAY n_root) = 1
$heap_owners(H_notice, HOBJECT n_old) = 3 /\ $heap_owners(H_notice, HOBJECT n_new) = 1 /\ $heap_owners(H_notice, HCELL n_leaf) = 3
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
S_resume = $nrpr_seek(S_notice, 2, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (PARRAY n_root)
S_resume.ARRAYS = S_notice.ARRAYS
S_resume.STORE[n_obj_cv] = DEFINED (POBJECT n_old) /\ S_resume.STORE[n_leaf] = DEFINED (POBJECT n_new)
S_resume.STORE[n_next_cv] = DEFINED PNULL /\ S_resume.STORE[n_snapshot] = DEFINED pvalue_original
$lookup(S_resume.ENV, $ptascii("leaf")) = (n_leaf) /\ $lookup(S_resume.ENV, $ptascii("leafAlias")) = (n_leaf)
$objectprops_record_at(S_resume.OBJECTPROPS, n_old) = (pobjectprops_current)
pobjectprops_current.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_current))}]
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_original) /\ $string_carrier_valid(S_resume, pvalue_next)
$objectprops_record_at(S_resume.OBJECTPROPS, n_new) = (pobjectprops_new)
$named_reference_notice_object(S_resume, POBJECT n_old) /\ $named_reference_notice_object(S_resume, POBJECT n_new)
$node_children(S_resume, HCELL n_leaf) = [HOBJECT n_new]
$named_reference_notice_array(S_resume, PARRAY n_root) /\ $error_call_valid(S_resume, perrorcall)
$weakref_get(S_resume, n_weak_old) = POBJECT n_old /\ $weakref_get(S_resume, n_weak_new) = POBJECT n_new
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HARRAY n_root) = 1 /\ $heap_owners(H_resume, HCELL n_leaf) = 3
$heap_owners(H_resume, HOBJECT n_old) = 2 /\ $heap_owners(H_resume, HOBJECT n_new) = 1
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $nrpr_seek(S_resume, 3, 10000)[.COMPLETION = NORMAL]
$nrpr_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_root)
S_written.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_written.STORE[n_obj_cv] = DEFINED (POBJECT n_old) /\ S_written.STORE[n_leaf] = DEFINED (POBJECT n_new)
$objectprops_record_at(S_written.OBJECTPROPS, n_old) = (pobjectprops_old_written)
$objectprops_record_at(S_written.OBJECTPROPS, n_new) = (pobjectprops_new_written)
pobjectprops_old_written.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("X3")))))}]
pobjectprops_new_written.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("2Z")))))}]
S_written.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current) /\ $string_carrier_valid(S_written, pvalue_next)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HCELL n_private) = 1 /\ $heap_owners(H_written, HARRAY n_root) = 1
$heap_owners(H_written, HOBJECT n_old) = 2 /\ $heap_owners(H_written, HOBJECT n_new) = 1 /\ $heap_owners(H_written, HCELL n_leaf) = 3
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_direct = $nrpr_seek(S_written, 4, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_direct, 4)
S_direct.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
$weakref_get(S_direct, n_weak_old) = POBJECT n_old
H_direct = $heap_graph(S_direct)
$heap_owners(H_direct, HOBJECT n_old) = 1 /\ $heap_owners(H_direct, HCELL n_leaf) = 3 /\ $heap_valid(H_direct)
S_old_retired = $nrpr_seek(S_direct, 5, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_old_retired, 5)
~((HCELL n_obj_cv) <- S_old_retired.ALLOCATIONS) /\ ~((HOBJECT n_old) <- S_old_retired.ALLOCATIONS)
$weakref_get(S_old_retired, n_weak_old) = PNULL /\ $weakref_get(S_old_retired, n_weak_new) = POBJECT n_new
H_old_retired = $heap_graph(S_old_retired)
$heap_owners(H_old_retired, HOBJECT n_old) = 0 /\ $heap_owners(H_old_retired, HOBJECT n_new) = 1 /\ $heap_valid(H_old_retired)
S_private_cleared = $nrpr_seek(S_old_retired, 6, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_private_cleared, 6)
S_private_cleared.STORE[n_private] = DEFINED (PINT 37)
~((HARRAY n_root) <- S_private_cleared.ALLOCATIONS)
$node_children(S_private_cleared, HCELL n_private) = eps
$weakref_get(S_private_cleared, n_weak_new) = POBJECT n_new
H_private_cleared = $heap_graph(S_private_cleared)
$heap_owners(H_private_cleared, HARRAY n_root) = 0 /\ $heap_owners(H_private_cleared, HCELL n_leaf) = 2
$heap_owners(H_private_cleared, HOBJECT n_new) = 1 /\ $heap_valid(H_private_cleared)
S_one_alias = $nrpr_seek(S_private_cleared, 7, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_one_alias, 7)
$lookup(S_one_alias.ENV, $ptascii("leaf")) = eps /\ $lookup(S_one_alias.ENV, $ptascii("leafAlias")) = (n_leaf)
S_one_alias.STORE[n_leaf] = DEFINED (POBJECT n_new)
$weakref_get(S_one_alias, n_weak_new) = POBJECT n_new
H_one_alias = $heap_graph(S_one_alias)
$heap_owners(H_one_alias, HCELL n_leaf) = 1 /\ $heap_owners(H_one_alias, HOBJECT n_new) = 1 /\ $heap_valid(H_one_alias)
S_new_retired = $nrpr_seek(S_one_alias, 8, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_new_retired, 8)
S_new_retired.STORE[n_leaf] = DEFINED (PINT 31)
~((HOBJECT n_new) <- S_new_retired.ALLOCATIONS)
$weakref_get(S_new_retired, n_weak_new) = PNULL
H_new_retired = $heap_graph(S_new_retired)
$heap_owners(H_new_retired, HOBJECT n_new) = 0 /\ $heap_owners(H_new_retired, HCELL n_leaf) = 1 /\ $heap_valid(H_new_retired)
S_full = $drive(S_new_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
~((HCELL n_leaf) <- S_full.ALLOCATIONS)
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_full.STORE[n_snapshot] = DEFINED pvalue_original
$weakref_get(S_full, n_weak_old) = PNULL /\ $weakref_get(S_full, n_weak_new) = PNULL
$string_carrier_valid(S_full, pvalue_original)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_leaf) = 0 /\ $heap_owners(H_full, HOBJECT n_old) = 0 /\ $heap_owners(H_full, HOBJECT n_new) = 0
$heap_valid(H_full) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CONTROLS = r"""
$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
~$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_bad_id))}])
~$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_bad_bytes))}])
~$named_reference_notice_object(S_notice[.OBJECTPROPS = $objectprops_set(S_notice.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_bad_id))}])], POBJECT n_old)
~$named_reference_notice_object(S_notice[.OBJECTPROPS = $objectprops_set(S_notice.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("17")))))}])], POBJECT n_old)
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_object(S_nul[.OBJECTPROPS = $objectprops_set(S_nul.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_nul))}])], POBJECT n_old)
~$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ([0]), STATE (PROP_VALUE (DIRECT pvalue_original))}])
~$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (ALIAS n_snapshot))}])
~$named_reference_notice_object_slots(S_notice, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (POBJECT n_new)))}])
~$named_reference_notice_object(S_notice[.OBJECTTABLES = [{OBJECT n_old, TABLE 0}]], POBJECT n_old)
~$named_reference_notice_object(S_notice[.DESTRUCTION.CALLED = [n_old]], POBJECT n_old)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HOBJECT n_old]], POBJECT n_old)
~$named_reference_notice_object(S_notice[.GC.WORKER = (0)], POBJECT n_old)
~$named_reference_notice_object(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HOBJECT n_old)], POBJECT n_old)
~$named_reference_notice_array(S_notice[.LITERALARRAYRETAINED = [n_root]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.NATIVEEXCESS = [HARRAY n_root]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.PROPREFS = [{CELL n_leaf, SOURCES eps}]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]], PARRAY n_root)
~$named_reference_notice_object(S_written, POBJECT n_old) /\ ~$named_reference_notice_object(S_written, POBJECT n_new)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_old_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_old_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_old_retired, 2)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    row, = json.loads(CATALOGUE.read_bytes())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert sha(source) == native['source_sha256'] == row['source_sha256']
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
    assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
    assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = [initial] + RETURN + COMMON
    if args.front:
        derived = FRONT
    else:
        reached += PRIVATE
        reached.append('$nrpr_output(S_full.EVENTS) = $ptascii(' + json.dumps(row['native_stdout']) + ')')
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, source, provenance, source.with_name('native.stdout'), source.with_name('native.stderr'), Path(__file__), CATALOGUE]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable,
        'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'request-string-stdclass-fields-front' if args.front else 'request-string-stdclass-fields-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': len({line.split(' = ', 1)[0] for line in reached if line.startswith('H_') and ' = $heap_graph(' in line}),
        'executed_heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('request-string-stdclass-fields', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
