#!/usr/bin/env python3
"""Ground current owning-array field cells, child sharing and a genuine object-array cycle."""
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
CATALOGUE = Path(__file__).with_name('stdclass_alias_array_field_reference_notice_review_cases.json')

PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice44\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice44\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 9) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice44\\Cycle\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("U;M;")
def $nrpr_ready(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;")
def $nrpr_ready(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice44\\Primary\\take")
  -- if S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;C:23:Y9:2Z;")
def $nrpr_ready(S, 4) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;C:23:Y9:2Z;R:2Z:Y9:X7:17:17:Y9:2Z:1:31;")
def $nrpr_ready(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;C:23:Y9:2Z;R:2Z:Y9:X7:17:17:Y9:2Z:1:31;O:1:2Z;")
def $nrpr_ready(S, 6) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;C:23:Y9:2Z;R:2Z:Y9:X7:17:17:Y9:2Z:1:31;O:1:2Z;D:2Z:YQ:1;")
def $nrpr_ready(S, 7) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1:1;F:4:23:29;C:23:Y9:2Z;R:2Z:Y9:X7:17:17:Y9:2Z:1:31;O:1:2Z;D:2Z:YQ:1;L:YQ:1;")
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
S_return = $nrpr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ReviewNotice44\\Primary\\make")
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
$lookup(psymboltable_caller.ENV, $ptascii("data")) = (n_data)
$lookup(psymboltable_caller.ENV, $ptascii("dataAlias")) = (n_data)
$lookup(psymboltable_caller.ENV, $ptascii("oldCopy")) = (n_old_copy)
$lookup(psymboltable_caller.ENV, $ptascii("child")) = (n_child_cv)
$lookup(psymboltable_caller.ENV, $ptascii("next")) = (n_next_cv)
$lookup(psymboltable_caller.ENV, $ptascii("nextText")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("watch")) = (n_watch)
S_return.STORE[n_obj_cv] = DEFINED PNULL
S_return.STORE[n_data] = DEFINED (PARRAY n_old_array)
S_return.STORE[n_old_copy] = DEFINED (PARRAY n_old_array)
S_return.STORE[n_child_cv] = DEFINED (PARRAY n_child)
S_return.STORE[n_next_cv] = DEFINED (PARRAY n_next_array)
S_return.STORE[n_leaf] = DEFINED pvalue_original
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
n_data <- S_return.REFCELLS /\ n_leaf <- S_return.REFCELLS
n_snapshot =/= n_leaf /\ n_data =/= n_leaf
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("obj"))) (DIRECT (POBJECT n_object))]
S_return.ARRAYS[n_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_child)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (PARRAY n_child))]
S_return.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_original), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_return.ARRAYS[n_next_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_next_child))]
S_return.ARRAYS[n_next_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT pvalue_next), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
pvalue_next = PSTRING_CARRIER (REQUEST_STRING n_next_string) ($ptascii("23"))
$string_carrier_valid(S_return, pvalue_next)
n_next_array =/= n_old_array /\ n_next_child =/= n_child
S_return.OBJECTS[n_object] = STDINSTANCE
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops)
ppropertyslot_field = {DECL eps, NAME ($ptascii("bag")), STATE (PROP_VALUE (ALIAS n_data))}
pobjectprops.SLOTS = [ppropertyslot_field]
$objectprops_valid(S_return, [pobjectprops])
S_return.STORE[n_watch] = DEFINED (POBJECT n_weak)
S_return.OBJECTS[n_weak] = WEAKREFERENCE (n_object)
$weakref_get(S_return, n_weak) = POBJECT n_object
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HOBJECT n_object) = 1 /\ $heap_owners(H_return, HCELL n_data) = 3
$heap_owners(H_return, HARRAY n_old_array) = 2 /\ $heap_owners(H_return, HARRAY n_child) = 3
$heap_owners(H_return, HARRAY n_next_array) = 1 /\ $heap_owners(H_return, HARRAY n_next_child) = 1
$heap_owners(H_return, HCELL n_leaf) = 3 /\ $heap_owners(H_return, HCELL n_formal) = 1
$heap_owners(H_return, HCELL n_source_return) = 3
$node_children(S_after_return, HOBJECT n_object) = [HCELL n_data]
$node_children(S_after_return, HCELL n_data) = [HARRAY n_old_array]
$node_children(S_after_return, HARRAY n_old_array) = [HARRAY n_child, HARRAY n_child]
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
preqbytes = $ptascii("ReviewNotice44\\Primary\\make")
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
S_pre.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_pre.STORE[n_obj_cv] = DEFINED PNULL
$lookup(S_pre.ENV, $ptascii("data")) = (n_data) /\ $lookup(S_pre.ENV, $ptascii("dataAlias")) = (n_data)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
S_pre.STORE[n_data] = DEFINED (PARRAY n_old_array)
S_pre.STORE[n_old_copy] = DEFINED (PARRAY n_old_array)
S_pre.STORE[n_child_cv] = DEFINED (PARRAY n_child)
S_pre.STORE[n_next_cv] = DEFINED (PARRAY n_next_array)
S_pre.STORE[n_leaf] = DEFINED pvalue_original /\ S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops)
$named_reference_notice_root_value(S_pre, pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_next)
$call_reference_operand_valid(S_pre, REFERENCE n_data) /\ $call_reference_operand_valid(S_pre, REFERENCE n_leaf)
~$foreach_released_cell(S_pre, n_data) /\ ~$foreach_released_cell(S_pre, n_leaf)
~(n_data <- S_pre.LITERALREFRETAINED) /\ ~(n_data <- S_pre.LITERALREFDEBTS)
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
$heap_count(HCELL n_data, S_pre.NATIVEEXCESS) = 0 /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
$named_reference_notice_object_ancestors(S_pre, [n_root, n_old_array, n_child, n_next_array, n_next_child])
$named_reference_notice_array(S_pre, PARRAY n_old_array) /\ $named_reference_notice_array(S_pre, PARRAY n_next_array)
$node_children(S_pre, HOBJECT n_object) = $property_release_nodes(pobjectprops.SLOTS)
$node_children(S_pre, HCELL n_data) = [HARRAY n_old_array]
$node_children(S_pre, HARRAY n_old_array) = [HARRAY n_child, HARRAY n_child]
$node_children(S_pre, HARRAY n_child) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = eps /\ $node_children(S_pre, HCELL n_snapshot) = eps
$weakref_get(S_pre, n_weak) = POBJECT n_object
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps /\ ~$weakmap_key_waiting(S_pre, n_object)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1 /\ $heap_owners(H_pre, HOBJECT n_object) = 1
$heap_owners(H_pre, HCELL n_data) = 3 /\ $heap_owners(H_pre, HARRAY n_old_array) = 2
$heap_owners(H_pre, HARRAY n_child) = 3 /\ $heap_owners(H_pre, HCELL n_leaf) = 3
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

CYCLE = r"""
S_cycle = $nrpr_seek(S_cycle_initial, 9, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_cycle, 9)
S_cycle.TODO = (CALL_SEND pcalltarget_cycle eps 0 eps (porigin_cycle_call) z_cycle) :: ptask_cycle_tail*
S_cycle.RESULT = KNOWN (PARRAY n_cycle_root)
S_cycle.ARRAYS[n_cycle_root].ITEMS = [ENTRY (KSTRING ($ptascii("obj"))) (DIRECT (POBJECT n_cycle_object))]
$objectprops_record_at(S_cycle.OBJECTPROPS, n_cycle_object) = (pobjectprops_cycle)
pobjectprops_cycle.SLOTS = [ppropertyslot_cycle]
ppropertyslot_cycle = {DECL eps, NAME ($ptascii("bag")), STATE (PROP_VALUE (ALIAS n_cycle_data))}
S_cycle.STORE[n_cycle_data] = DEFINED (PARRAY n_cycle_array)
S_cycle.ARRAYS[n_cycle_array].ITEMS = [ENTRY (KSTRING ($ptascii("self"))) (DIRECT (POBJECT n_cycle_object))]
$node_children(S_cycle, HOBJECT n_cycle_object) = [HCELL n_cycle_data]
$node_children(S_cycle, HCELL n_cycle_data) = [HARRAY n_cycle_array]
$node_children(S_cycle, HARRAY n_cycle_array) = [HOBJECT n_cycle_object]
$call_reference_operand_valid(S_cycle, REFERENCE n_cycle_data)
$objectprops_valid(S_cycle, [pobjectprops_cycle])
$positional_reference_notice_source(S_cycle, pcalltarget_cycle, 0, (porigin_cycle_call))
H_cycle = $heap_graph(S_cycle)
$heap_owners(H_cycle, HOBJECT n_cycle_object) = 3 /\ $heap_owners(H_cycle, HCELL n_cycle_data) = 2
$heap_owners(H_cycle, HARRAY n_cycle_array) = 1
$heap_valid(H_cycle) /\ $call_descriptors_valid(S_cycle)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object)
~$named_reference_notice_array(S_pre, PARRAY n_root) /\ ~$named_reference_notice_pending(S_pre)
S_scalar = S_pre[.STORE[n_data] = DEFINED pvalue_original]
$named_reference_notice_object_slots(S_scalar, pobjectprops.SLOTS)
$named_reference_notice_object(S_scalar, POBJECT n_object) /\ $named_reference_notice_pending(S_scalar)
$node_children(S_scalar, HCELL n_data) = eps
H_scalar = $heap_graph(S_scalar)
$heap_owners(H_scalar, HCELL n_data) = 3 /\ $heap_owners(H_scalar, HARRAY n_old_array) = 1
$heap_owners(H_scalar, HARRAY n_child) = 3 /\ $heap_owners(H_scalar, HCELL n_leaf) = 3
$heap_valid(H_scalar) /\ $call_descriptors_valid(S_scalar)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]
~$named_reference_notice_object(S_cycle, POBJECT n_cycle_object) /\ ~$positional_reference_notice_pending(S_cycle)
S_cycle_fenced = $drive(S_cycle, 1)
S_cycle_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_cycle_fenced.EVENTS = S_cycle.EVENTS
""".strip().splitlines()


PRIVATE = r"""
$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
$named_reference_notice_object(S_pre, POBJECT n_object) /\ $named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (KNOWN (PINT 4)), NAMED_SENT (REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$error_call_valid(S_notice, perrorcall)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HOBJECT n_object) = 1
$heap_owners(H_notice, HCELL n_data) = 3 /\ $heap_owners(H_notice, HARRAY n_old_array) = 2
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
S_resume = $nrpr_seek(S_notice, 2, 7000)[.COMPLETION = NORMAL]
$nrpr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_notice*
S_resume.STORE[n_data] = DEFINED (PARRAY n_next_array)
S_resume.STORE[n_next_cv] = DEFINED PNULL
S_resume.STORE[n_old_copy] = DEFINED (PARRAY n_old_array)
S_resume.ARRAYS[n_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_old_copy_child)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (PARRAY n_child))]
n_old_copy_child =/= n_child
S_resume.ARRAYS[n_old_copy_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("X7")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_resume.ARRAYS[n_child].ITEMS = S_return.ARRAYS[n_child].ITEMS
S_resume.STORE[n_leaf] = DEFINED pvalue_shared_current
pvalue_shared_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("29"))
$string_carrier_valid(S_resume, pvalue_shared_current) /\ $string_carrier_valid(S_resume, pvalue_next) /\ $string_carrier_valid(S_resume, pvalue_original)
S_resume.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_resume.OBJECTPROPS, n_object) = (pobjectprops)
$named_reference_notice_object(S_resume, POBJECT n_object) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_data) = 3 /\ $heap_owners(H_resume, HARRAY n_old_array) = 1
$heap_owners(H_resume, HARRAY n_child) = 2 /\ $heap_owners(H_resume, HARRAY n_old_copy_child) = 1
$heap_owners(H_resume, HARRAY n_next_array) = 1 /\ $heap_owners(H_resume, HARRAY n_next_child) = 1
$heap_owners(H_resume, HCELL n_leaf) = 4 /\ $heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_cow = $nrpr_seek(S_resume, 3, 8000)[.COMPLETION = NORMAL]
$nrpr_ready(S_cow, 3)
$lookup(S_cow.ENV, $ptascii("current")) = (n_data)
$lookup(S_cow.ENV, $ptascii("copy")) = (n_copy_cv)
S_cow.STORE[n_copy_cv] = DEFINED (PARRAY n_next_array)
S_cow.STORE[n_data] = DEFINED (PARRAY n_current_array)
n_current_array =/= n_next_array
S_cow.ARRAYS[n_current_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_current_child))]
n_current_child =/= n_next_child
S_cow.ARRAYS[n_current_child].ITEMS = [ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (PSTRING ($ptascii("2Z")))), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_cow.ARRAYS[n_next_child].ITEMS = S_return.ARRAYS[n_next_child].ITEMS
S_cow.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("Y9")))
$node_children(S_cow, HOBJECT n_object) = [HCELL n_data]
$node_children(S_cow, HCELL n_data) = [HARRAY n_current_array]
H_cow = $heap_graph(S_cow)
$heap_owners(H_cow, HCELL n_data) = 4 /\ $heap_owners(H_cow, HCELL n_leaf) = 5
$heap_owners(H_cow, HARRAY n_next_array) = 1 /\ $heap_owners(H_cow, HARRAY n_next_child) = 1
$heap_owners(H_cow, HARRAY n_current_array) = 1 /\ $heap_owners(H_cow, HARRAY n_current_child) = 1
$heap_valid(H_cow) /\ $call_descriptors_valid(S_cow)
S_written = $nrpr_seek(S_cow, 4, 7000)[.COMPLETION = NORMAL]
$nrpr_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_root)
S_written.STORE[n_data] = DEFINED (PARRAY n_current_array)
S_written.STORE[n_snapshot] = DEFINED pvalue_original
~((HARRAY n_next_array) <- S_written.ALLOCATIONS) /\ ~((HARRAY n_next_child) <- S_written.ALLOCATIONS)
~((HCELL n_copy_cv) <- S_written.ALLOCATIONS)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HOBJECT n_object) = 1 /\ $heap_owners(H_written, HARRAY n_root) = 1
$heap_owners(H_written, HCELL n_data) = 3 /\ $heap_owners(H_written, HCELL n_leaf) = 4
$heap_owners(H_written, HARRAY n_next_array) = 0 /\ $heap_owners(H_written, HARRAY n_current_array) = 1
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_object_retired = $nrpr_seek(S_written, 5, 6000)[.COMPLETION = NORMAL]
$nrpr_ready(S_object_retired, 5)
S_object_retired.ARRAYS[n_root].ITEMS = eps
~((HOBJECT n_object) <- S_object_retired.ALLOCATIONS)
$weakref_get(S_object_retired, n_weak) = PNULL
S_object_retired.STORE[n_data] = DEFINED (PARRAY n_current_array)
H_object_retired = $heap_graph(S_object_retired)
$heap_owners(H_object_retired, HOBJECT n_object) = 0 /\ $heap_owners(H_object_retired, HCELL n_data) = 2
$heap_owners(H_object_retired, HARRAY n_current_array) = 1 /\ $heap_valid(H_object_retired)
S_one_data = $nrpr_seek(S_object_retired, 6, 6000)[.COMPLETION = NORMAL]
$nrpr_ready(S_one_data, 6)
$lookup(S_one_data.ENV, $ptascii("data")) = eps /\ $lookup(S_one_data.ENV, $ptascii("dataAlias")) = (n_data)
S_one_data.STORE[n_private] = DEFINED (PINT 37)
S_one_data.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("YQ")))
~((HARRAY n_root) <- S_one_data.ALLOCATIONS)
H_one_data = $heap_graph(S_one_data)
$heap_owners(H_one_data, HCELL n_data) = 1 /\ $heap_owners(H_one_data, HCELL n_leaf) = 4
$heap_valid(H_one_data) /\ $call_descriptors_valid(S_one_data)
S_one_leaf = $nrpr_seek(S_one_data, 7, 7000)[.COMPLETION = NORMAL]
$nrpr_ready(S_one_leaf, 7)
~((HCELL n_data) <- S_one_leaf.ALLOCATIONS) /\ ~((HCELL n_old_copy) <- S_one_leaf.ALLOCATIONS) /\ ~((HCELL n_child_cv) <- S_one_leaf.ALLOCATIONS)
~((HARRAY n_old_array) <- S_one_leaf.ALLOCATIONS) /\ ~((HARRAY n_child) <- S_one_leaf.ALLOCATIONS) /\ ~((HARRAY n_old_copy_child) <- S_one_leaf.ALLOCATIONS)
~((HARRAY n_current_array) <- S_one_leaf.ALLOCATIONS) /\ ~((HARRAY n_current_child) <- S_one_leaf.ALLOCATIONS)
S_one_leaf.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("YQ")))
S_one_leaf.STORE[n_snapshot] = DEFINED pvalue_original
H_one_leaf = $heap_graph(S_one_leaf)
$heap_owners(H_one_leaf, HCELL n_leaf) = 1 /\ $heap_owners(H_one_leaf, HCELL n_data) = 0
$heap_valid(H_one_leaf) /\ $call_descriptors_valid(S_one_leaf)
S_full = $drive(S_one_leaf, 14000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
~((HCELL n_leaf) <- S_full.ALLOCATIONS)
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_full.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_full, pvalue_original) /\ $string_carrier_valid(S_full, pvalue_next) /\ $string_carrier_valid(S_full, pvalue_shared_current)
$weakref_get(S_full, n_weak) = PNULL
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CONTROLS = r"""
$update_warning_no_objects($heap_reach([HARRAY n_old_array], eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
$update_warning_no_objects($heap_reach([HARRAY n_next_array], eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
~$update_warning_no_objects($heap_reach([HARRAY n_cycle_array], eps, $allocation_edges(S_cycle, S_cycle.ALLOCATIONS)))
~$named_reference_notice_object_slots(S_cycle, pobjectprops_cycle.SLOTS)
~$positional_reference_notice_pending(S_cycle)
S_cycle_fenced = $drive(S_cycle, 1)
S_cycle_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_cycle_fenced.EVENTS = S_cycle.EVENTS
~$named_reference_notice_object_slots(S_pre[.REFCELLS = eps], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HCELL n_data)], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.STORE[n_data] = UNDEFINED], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.PROPREFS = [{CELL n_data, SOURCES eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.REFCOERCIONS = [{CELL n_data, SITE porigin_call, LINE 0, VALUE eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_data, LINE 0, VALUE eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.CONTAINERINITS = [{CELL n_data, ARRAY n_old_array, SITE porigin_call, LINE 0}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.LITERALREFRETAINED = [n_data]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.LITERALREFDEBTS = [n_data]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.NATIVEEXCESS = [HCELL n_data]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.LITERALARRAYRETAINED = [n_old_array]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.LITERALARRAYDEBTS = [n_old_array]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.NATIVEEXCESS = [HARRAY n_old_array]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.LITERALARRAYRETAINED = [n_child]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.NATIVEEXCESS = [HCELL n_leaf]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.STORE[n_leaf] = DEFINED (PSTRING ($ptascii("17")))], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_pre[.STORE[n_data] = DEFINED (POBJECT n_object)], [ppropertyslot_field])
S_array_cycle = S_pre[.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("back"))) (DIRECT (PARRAY n_old_array))]]
$update_warning_no_objects($heap_reach([HARRAY n_old_array], eps, $allocation_edges(S_array_cycle, S_array_cycle.ALLOCATIONS)))
~$named_reference_notice_object_slots(S_array_cycle, [ppropertyslot_field])
~$named_reference_notice_object(S_pre[.OBJECTTABLES = [{OBJECT n_object, TABLE 0}]], POBJECT n_object)
~$named_reference_notice_object(S_pre[.NATIVEEXCESS = [HOBJECT n_object]], POBJECT n_object)
~$named_reference_notice_object(S_pre[.GC.WORKER = (0)], POBJECT n_object)
~$named_reference_notice_array(S_pre[.LITERALARRAYRETAINED = [n_root]], PARRAY n_root)
~$named_reference_notice_object(S_cow, POBJECT n_object)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_object_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_object_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_object_retired, 2)
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = [path.resolve() for path in args.native_provenance]
    natives = [json.loads(path.read_bytes()) for path in provenance]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in natives}
    assert len(records) == len(natives) == len(cases) == 2
    sources = {i: Path(records[row['id']]['command'][-1]) for i, row in enumerate(cases)}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for i, row in enumerate(cases):
        native, source = records[row['id']], sources[i]
        assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable'] and native['head_stable']
        assert source.read_bytes() == row['source'].encode() and sha(source) == native['source_sha256'] == row['source_sha256']
        assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
        assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
        assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
        assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
        assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i, source in sources.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
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
        reached += [initial('S_cycle_initial', 1)] + CYCLE
        derived = FRONT
    else:
        reached += PRIVATE + [initial('S_cycle_initial', 1)] + CYCLE
        reached.append('$nrpr_output(S_full.EVENTS) = $ptascii(' + json.dumps(cases[0]['native_stdout']) + ')')
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, Path(__file__), CATALOGUE, *provenance]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    for source in sources.values():
        paths += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
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
        'fixture_sha256': sha(fixture), 'part': 'stdclass-alias-array-field-front' if args.front else 'stdclass-alias-array-field-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('stdclass-alias-array-field', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
