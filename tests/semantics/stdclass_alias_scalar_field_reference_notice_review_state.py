#!/usr/bin/env python3
"""Ground two physical ALIAS fields sharing a scalar cell and the pre-Notice domain gap."""
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
CATALOGUE = Path(__file__).with_name('stdclass_alias_scalar_field_reference_notice_review_cases.json')

PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice43\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice43\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;")
def $nrpr_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:23:23;R:2Z:X3:X3:2Z:1:31;")
def $nrpr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:23:23;R:2Z:X3:X3:2Z:1:31;B:1:X3:X3;")
def $nrpr_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:23:23;R:2Z:X3:X3:2Z:1:31;B:1:X3:X3;T:XY:1;")
def $nrpr_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;H:1;F:4:23:23;R:2Z:X3:X3:2Z:1:31;B:1:X3:X3;T:XY:1;A:1:2Z;")
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
pfunction_producer.NAME = $ptascii("ReviewNotice43\\Primary\\make")
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
$lookup(psymboltable_caller.ENV, $ptascii("a")) = (n_a_cv)
$lookup(psymboltable_caller.ENV, $ptascii("b")) = (n_b_cv)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("text")) = (n_text)
$lookup(psymboltable_caller.ENV, $ptascii("other")) = (n_other)
$lookup(psymboltable_caller.ENV, $ptascii("weakA")) = (n_weak_a_cv)
$lookup(psymboltable_caller.ENV, $ptascii("weakB")) = (n_weak_b_cv)
S_return.STORE[n_a_cv] = DEFINED PNULL /\ S_return.STORE[n_b_cv] = DEFINED PNULL
S_return.STORE[n_text] = DEFINED pvalue_original
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
S_return.STORE[n_other] = DEFINED pvalue_other
pvalue_other = PSTRING_CARRIER (REQUEST_STRING n_other_string) ($ptascii("29"))
$string_carrier_valid(S_return, pvalue_other)
n_snapshot =/= n_text /\ n_other =/= n_text
n_text <- S_return.REFCELLS /\ ~(n_snapshot <- S_return.REFCELLS)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("first"))) (DIRECT (POBJECT n_a)), ENTRY (KSTRING ($ptascii("second"))) (DIRECT (POBJECT n_b))]
n_a =/= n_b
S_return.OBJECTS[n_a] = STDINSTANCE /\ S_return.OBJECTS[n_b] = STDINSTANCE
$objectprops_record_at(S_return.OBJECTPROPS, n_a) = (pobjectprops_a)
$objectprops_record_at(S_return.OBJECTPROPS, n_b) = (pobjectprops_b)
ppropertyslot_field = {DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (ALIAS n_text))}
pobjectprops_a.SLOTS = [ppropertyslot_field] /\ pobjectprops_b.SLOTS = [ppropertyslot_field]
$objectprops_valid(S_return, [pobjectprops_a, pobjectprops_b])
S_return.STORE[n_weak_a_cv] = DEFINED (POBJECT n_weak_a)
S_return.STORE[n_weak_b_cv] = DEFINED (POBJECT n_weak_b)
S_return.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a) /\ S_return.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)
$weakref_get(S_return, n_weak_a) = POBJECT n_a /\ $weakref_get(S_return, n_weak_b) = POBJECT n_b
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HOBJECT n_a) = 1 /\ $heap_owners(H_return, HOBJECT n_b) = 1
$heap_owners(H_return, HCELL n_text) = 3 /\ $heap_owners(H_return, HCELL n_formal) = 1
$heap_owners(H_return, HCELL n_source_return) = 3
$node_children(S_after_return, HOBJECT n_a) = [HCELL n_text] /\ $node_children(S_after_return, HOBJECT n_b) = [HCELL n_text]
$node_children(S_after_return, HCELL n_text) = eps
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
preqbytes = $ptascii("ReviewNotice43\\Primary\\make")
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
$lookup(S_pre.ENV, $ptascii("a")) = (n_a_cv) /\ $lookup(S_pre.ENV, $ptascii("b")) = (n_b_cv)
S_pre.STORE[n_a_cv] = DEFINED PNULL /\ S_pre.STORE[n_b_cv] = DEFINED PNULL
$lookup(S_pre.ENV, $ptascii("text")) = (n_text) /\ $lookup(S_pre.ENV, $ptascii("other")) = (n_other)
$lookup(S_pre.ENV, $ptascii("snapshot")) = (n_snapshot)
S_pre.STORE[n_text] = DEFINED pvalue_original /\ S_pre.STORE[n_snapshot] = DEFINED pvalue_original
S_pre.STORE[n_other] = DEFINED pvalue_other
S_pre.ARRAYS[n_root].ITEMS = S_return.ARRAYS[n_root].ITEMS
$objectprops_record_at(S_pre.OBJECTPROPS, n_a) = (pobjectprops_a)
$objectprops_record_at(S_pre.OBJECTPROPS, n_b) = (pobjectprops_b)
$string_carrier_valid(S_pre, pvalue_original) /\ $string_carrier_valid(S_pre, pvalue_other)
$named_reference_notice_root_value(S_pre, pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_other)
$call_reference_operand_valid(S_pre, REFERENCE n_text)
$propref_at(S_pre.PROPREFS, n_text) = eps /\ $reference_coercion_at(S_pre.REFCOERCIONS, n_text) = eps
~(n_text <- S_pre.LITERALREFRETAINED) /\ ~(n_text <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_text) /\ $heap_count(HCELL n_text, S_pre.NATIVEEXCESS) = 0
$property_release_nodes(pobjectprops_a.SLOTS) = [HCELL n_text] /\ $property_release_nodes(pobjectprops_b.SLOTS) = [HCELL n_text]
$node_children(S_pre, HARRAY n_root) = [HOBJECT n_a, HOBJECT n_b]
$node_children(S_pre, HOBJECT n_a) = [HCELL n_text] /\ $node_children(S_pre, HOBJECT n_b) = [HCELL n_text]
$node_children(S_pre, HCELL n_text) = eps /\ $node_children(S_pre, HCELL n_snapshot) = eps
$weakref_get(S_pre, n_weak_a) = POBJECT n_a /\ $weakref_get(S_pre, n_weak_b) = POBJECT n_b
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
$object_table_at(S_pre.OBJECTTABLES, n_a) = eps /\ $object_table_at(S_pre.OBJECTTABLES, n_b) = eps
~$weakmap_key_waiting(S_pre, n_a) /\ ~$weakmap_key_waiting(S_pre, n_b)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1
$heap_owners(H_pre, HOBJECT n_a) = 1 /\ $heap_owners(H_pre, HOBJECT n_b) = 1
$heap_owners(H_pre, HCELL n_text) = 3 /\ $heap_owners(H_pre, HCELL n_source_cv) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops_a.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_a) /\ ~$named_reference_notice_object(S_pre, POBJECT n_b)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_operand(S_pre, KNOWN (PARRAY n_root)) /\ ~$named_reference_notice_pending(S_pre)
ppropertyslot_direct = ppropertyslot_field[.STATE = PROP_VALUE (DIRECT pvalue_original)]
S_direct = S_pre[.OBJECTPROPS = $objectprops_set($objectprops_set(S_pre.OBJECTPROPS, n_a, [ppropertyslot_direct]), n_b, [ppropertyslot_direct])]
$named_reference_notice_object(S_direct, POBJECT n_a) /\ $named_reference_notice_object(S_direct, POBJECT n_b)
$named_reference_notice_array(S_direct, PARRAY n_root) /\ $named_reference_notice_pending(S_direct)
$node_children(S_direct, HOBJECT n_a) = eps /\ $node_children(S_direct, HOBJECT n_b) = eps
H_direct = $heap_graph(S_direct)
$heap_owners(H_direct, HCELL n_text) = 1
$heap_owners(H_direct, HOBJECT n_a) = 1 /\ $heap_owners(H_direct, HOBJECT n_b) = 1
$heap_valid(H_direct) /\ $call_descriptors_valid(S_direct)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]
S_fenced.ARRAYS = S_pre.ARRAYS /\ S_fenced.OBJECTPROPS = S_pre.OBJECTPROPS
""".strip().splitlines()



PRIVATE = r"""
$named_reference_notice_object_slots(S_pre, pobjectprops_a.SLOTS)
$named_reference_notice_object_slots(S_pre, pobjectprops_b.SLOTS)
$named_reference_notice_object(S_pre, POBJECT n_a) /\ $named_reference_notice_object(S_pre, POBJECT n_b)
$named_reference_notice_array(S_pre, PARRAY n_root) /\ $named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_text /\ n_private =/= n_other /\ n_private =/= n_source_cv
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
$heap_owners(H_notice, HOBJECT n_a) = 1 /\ $heap_owners(H_notice, HOBJECT n_b) = 1
$heap_owners(H_notice, HCELL n_text) = 3
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
S_resume = $nrpr_seek(S_notice, 2, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_notice*
S_resume.STORE[n_private] = DEFINED (PARRAY n_root)
S_resume.STORE[n_text] = DEFINED pvalue_current
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
n_current_string =/= n_string
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_original)
S_resume.STORE[n_snapshot] = DEFINED pvalue_original /\ S_resume.STORE[n_other] = DEFINED pvalue_other
$objectprops_record_at(S_resume.OBJECTPROPS, n_a) = (pobjectprops_a)
$objectprops_record_at(S_resume.OBJECTPROPS, n_b) = (pobjectprops_b)
$named_reference_notice_pending(S_pre) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1 /\ $heap_owners(H_resume, HARRAY n_root) = 1
$heap_owners(H_resume, HCELL n_text) = 3
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $nrpr_seek(S_resume, 3, 6000)[.COMPLETION = NORMAL]
$nrpr_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
$lookup(S_written.ENV, $ptascii("text")) = (n_text)
$lookup(S_written.ENV, $ptascii("other")) = (n_other)
n_other <- S_written.REFCELLS
S_written.STORE[n_private] = DEFINED (PARRAY n_root)
S_written.STORE[n_text] = DEFINED (PSTRING ($ptascii("X3")))
S_written.STORE[n_other] = DEFINED (PSTRING ($ptascii("2Z")))
S_written.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_written.OBJECTPROPS, n_a) = (pobjectprops_a_written)
$objectprops_record_at(S_written.OBJECTPROPS, n_b) = (pobjectprops_b)
pobjectprops_a_written.SLOTS = [ppropertyslot_field[.STATE = PROP_VALUE (ALIAS n_other)]]
$node_children(S_written, HOBJECT n_a) = [HCELL n_other] /\ $node_children(S_written, HOBJECT n_b) = [HCELL n_text]
$node_children(S_written, HCELL n_other) = eps /\ $node_children(S_written, HCELL n_text) = eps
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current) /\ $string_carrier_valid(S_written, pvalue_other)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HCELL n_private) = 1 /\ $heap_owners(H_written, HARRAY n_root) = 1
$heap_owners(H_written, HOBJECT n_a) = 1 /\ $heap_owners(H_written, HOBJECT n_b) = 1
$heap_owners(H_written, HCELL n_text) = 2 /\ $heap_owners(H_written, HCELL n_other) = 2
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_b_retired = $nrpr_seek(S_written, 4, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_b_retired, 4)
$lookup(S_b_retired.ENV, $ptascii("out")) = (n_text)
S_b_retired.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("first"))) (DIRECT (POBJECT n_a))]
~((HOBJECT n_b) <- S_b_retired.ALLOCATIONS)
$weakref_get(S_b_retired, n_weak_b) = PNULL /\ $weakref_get(S_b_retired, n_weak_a) = POBJECT n_a
S_b_retired.STORE[n_text] = DEFINED (PSTRING ($ptascii("X3")))
H_b_retired = $heap_graph(S_b_retired)
$heap_owners(H_b_retired, HOBJECT n_b) = 0 /\ $heap_owners(H_b_retired, HOBJECT n_a) = 1
$heap_owners(H_b_retired, HCELL n_text) = 2 /\ $heap_owners(H_b_retired, HCELL n_other) = 2
$heap_valid(H_b_retired) /\ $call_descriptors_valid(S_b_retired)
S_one_alias = $nrpr_seek(S_b_retired, 5, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_one_alias, 5)
$lookup(S_one_alias.ENV, $ptascii("text")) = eps /\ $lookup(S_one_alias.ENV, $ptascii("out")) = (n_text)
S_one_alias.STORE[n_text] = DEFINED (PSTRING ($ptascii("XY")))
S_one_alias.STORE[n_snapshot] = DEFINED pvalue_original
H_one_alias = $heap_graph(S_one_alias)
$heap_owners(H_one_alias, HCELL n_text) = 1 /\ $heap_owners(H_one_alias, HCELL n_other) = 2
$heap_valid(H_one_alias) /\ $call_descriptors_valid(S_one_alias)
S_a_retired = $nrpr_seek(S_one_alias, 6, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_a_retired, 6)
S_a_retired.ARRAYS[n_root].ITEMS = eps
~((HOBJECT n_a) <- S_a_retired.ALLOCATIONS) /\ ~((HOBJECT n_b) <- S_a_retired.ALLOCATIONS)
$weakref_get(S_a_retired, n_weak_a) = PNULL /\ $weakref_get(S_a_retired, n_weak_b) = PNULL
S_a_retired.STORE[n_other] = DEFINED (PSTRING ($ptascii("2Z")))
H_a_retired = $heap_graph(S_a_retired)
$heap_owners(H_a_retired, HOBJECT n_a) = 0 /\ $heap_owners(H_a_retired, HOBJECT n_b) = 0
$heap_owners(H_a_retired, HCELL n_text) = 1 /\ $heap_owners(H_a_retired, HCELL n_other) = 1
$heap_owners(H_a_retired, HARRAY n_root) = 1 /\ $heap_valid(H_a_retired)
S_full = $drive(S_a_retired, 12000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
~((HCELL n_text) <- S_full.ALLOCATIONS) /\ ~((HCELL n_other) <- S_full.ALLOCATIONS)
~((HARRAY n_root) <- S_full.ALLOCATIONS)
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_full.STORE[n_snapshot] = DEFINED pvalue_original
$weakref_get(S_full, n_weak_a) = PNULL /\ $weakref_get(S_full, n_weak_b) = PNULL
$string_carrier_valid(S_full, pvalue_original)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_text) = 0 /\ $heap_owners(H_full, HCELL n_other) = 0 /\ $heap_owners(H_full, HARRAY n_root) = 0
$heap_owners(H_full, HOBJECT n_a) = 0 /\ $heap_owners(H_full, HOBJECT n_b) = 0
$heap_valid(H_full) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CONTROLS = r"""
$named_reference_notice_object_slots(S_notice, [ppropertyslot_field])
$named_reference_notice_object_slots(S_notice, [ppropertyslot_field, ppropertyslot_field[.NAME = $ptascii("other")]])
~$named_reference_notice_object_slots(S_notice[.REFCELLS = eps], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_text)], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.STORE[n_text] = UNDEFINED], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.PROPREFS = [{CELL n_text, SOURCES eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.REFCOERCIONS = [{CELL n_text, SITE porigin_call, LINE 0, VALUE eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_text, LINE 0, VALUE eps}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.CONTAINERINITS = [{CELL n_text, ARRAY n_root, SITE porigin_call, LINE 0}]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.LITERALREFRETAINED = [n_text]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.LITERALREFDEBTS = [n_text]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.NATIVEEXCESS = [HCELL n_text]], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_field[.STATE = PROP_VALUE (ALIAS n_snapshot)]])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
~$named_reference_notice_object_slots(S_notice[.STORE[n_text] = DEFINED pvalue_bad_id], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.STORE[n_text] = DEFINED pvalue_bad_bytes], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.STORE[n_text] = DEFINED (PSTRING ($ptascii("17")))], [ppropertyslot_field])
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_object_slots(S_nul[.STORE[n_text] = DEFINED pvalue_nul], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_field[.NAME = [0]]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_field[.NAME = [256]]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_field[.DECL = (INTERNAL_PROPERTY "stdClass" ($ptascii("value")))]])
~$named_reference_notice_object_slots(S_notice[.STORE[n_text] = DEFINED (PARRAY n_root)], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice[.STORE[n_text] = DEFINED (POBJECT n_a)], [ppropertyslot_field])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_field[.STATE = PROP_UNSET]])
~$named_reference_notice_object(S_notice[.OBJECTTABLES = [{OBJECT n_a, TABLE 0}]], POBJECT n_a)
~$named_reference_notice_object(S_notice[.DESTRUCTION.CALLED = [n_a]], POBJECT n_a)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HOBJECT n_a]], POBJECT n_a)
~$named_reference_notice_object(S_notice[.GC.WORKER = (0)], POBJECT n_a)
~$named_reference_notice_object(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HOBJECT n_a)], POBJECT n_a)
~$named_reference_notice_array(S_notice[.LITERALARRAYRETAINED = [n_root]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.LITERALARRAYDEBTS = [n_root]], PARRAY n_root)
~$named_reference_notice_array(S_notice[.NATIVEEXCESS = [HARRAY n_root]], PARRAY n_root)
~$named_reference_notice_object(S_written, POBJECT n_a) /\ ~$named_reference_notice_object(S_written, POBJECT n_b)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_b_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_b_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_b_retired, 2)
""".strip().splitlines()

for value in ('PNULL', 'PBOOL true', 'PINT 9', 'PFLOAT 4607182418800017408', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("quiet"))'):
    CONTROLS.append('$named_reference_notice_object_slots(S_notice[.STORE[n_text] = DEFINED (' + value + ')], [ppropertyslot_field])')

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
        'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'stdclass-alias-scalar-field-front' if args.front else 'stdclass-alias-scalar-field-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': len({line.split(' = ', 1)[0] for line in reached if line.startswith('H_') and ' = $heap_graph(' in line}),
        'executed_heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('stdclass-alias-scalar-field', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
