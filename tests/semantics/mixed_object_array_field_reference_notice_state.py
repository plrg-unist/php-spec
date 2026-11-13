#!/usr/bin/env python3
"""Ground mixed object-array field edges, quiet table COW and recursive retirement."""
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
CATALOGUE = Path(__file__).with_name('mixed_object_array_field_reference_notice_cases.json')

PREFIX = r"""
dec $mof_output(pevent*) : ptbytes
def $mof_output(eps) = eps
def $mof_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mof_output(pevent*)
dec $mof_ready(pstate, nat) : bool
def $mof_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("MixedObjectArrayNotice48\\make") \/ pcallcontext.NAME = $ptascii("MixedObjectArrayThrow48\\make")
def $mof_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("MixedObjectArrayNotice48\\take") \/ pfunction.NAME = $ptascii("MixedObjectArrayThrow48\\take")
def $mof_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("K;M:17:17;F:17;C:17:18:18:1:0;R:18:18:1:1;")

def $mof_ready(S, 3) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;")
def $mof_ready(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("MixedObjectArrayNotice48\\take")
  -- if S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;")
def $mof_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;")
def $mof_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;P;")
def $mof_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;P;K:1:1:1:1;")
def $mof_ready(S, 8) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;P;K:1:1:1:1;O:1:1;")
def $mof_ready(S, 9) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;P;K:1:1:1:1;O:1:1;B:1;")
def $mof_ready(S, 10) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;P;K:1:1:1:1;O:1:1;B:1;N:1:32;")
def $mof_ready(S, 11) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mof_output(S.EVENTS) = $ptascii("A;M:17:17;H:1:1;F:31;C:31:32:32:1:0;R:32:23:1:1;P;K:1:1:1:1;O:1:1;B:1;N:1:32;E:1:43;")
def $mof_ready(S, 20) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $mof_ready(S, n_stage) = false -- otherwise
dec $mof_seek(pstate, nat, nat) : pstate
def $mof_seek(S, n_stage, n) = S
  -- if $mof_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mof_seek(S, n_stage, n) = $mof_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mof_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mof_seek(S, n_stage, n) = $mof_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$mof_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $mof_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $mof_seek(S_initial, 0, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_return, 0)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("MixedObjectArrayNotice48\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
$lookup(S_return.ENV, $ptascii("input")) = (n_source)
S_return.STORE[n_source] = DEFINED (POBJECT n_object)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(psymboltable_caller.ENV, $ptascii("outside")) = (n_outside_cv)
$lookup(psymboltable_caller.ENV, $ptascii("payload")) = (n_payload)
$lookup(psymboltable_caller.ENV, $ptascii("payloadAlias")) = (n_payload)
$lookup(psymboltable_caller.ENV, $ptascii("nextBag")) = (n_next_bag_cv)
$lookup(psymboltable_caller.ENV, $ptascii("nextPayload")) = (n_next_payload)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("node")) = eps /\ $lookup(psymboltable_caller.ENV, $ptascii("nextNode")) = eps
S_return.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_return.STORE[n_outside_cv] = DEFINED (PARRAY n_old_array)
S_return.STORE[n_payload] = DEFINED (POBJECT n_old_leaf)
S_return.STORE[n_next_bag_cv] = DEFINED (PARRAY n_next_array)
S_return.STORE[n_next_payload] = DEFINED (POBJECT n_next_leaf)
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops_root)
pobjectprops_root.SLOTS = [ppropertyslot_bag]
ppropertyslot_bag = {DECL eps, NAME ($ptascii("bag")), STATE (PROP_VALUE (DIRECT (PARRAY n_old_array)))}
S_return.ARRAYS[n_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_old_node)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (POBJECT n_old_node))]
S_return.ARRAYS[n_next_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_next_node)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (POBJECT n_next_node))]
$objectprops_record_at(S_return.OBJECTPROPS, n_old_node) = (pobjectprops_old_node)
pobjectprops_old_node.SLOTS = [{DECL eps, NAME ($ptascii("item")), STATE (PROP_VALUE (ALIAS n_payload))}]
$objectprops_record_at(S_return.OBJECTPROPS, n_next_node) = (pobjectprops_next_node)
pobjectprops_next_node.SLOTS = [{DECL eps, NAME ($ptascii("item")), STATE (PROP_VALUE (ALIAS n_next_payload))}]
$objectprops_record_at(S_return.OBJECTPROPS, n_old_leaf) = (pobjectprops_old_leaf)
pobjectprops_old_leaf.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}]
$objectprops_record_at(S_return.OBJECTPROPS, n_next_leaf) = (pobjectprops_next_leaf)
pobjectprops_next_leaf.SLOTS = [ppropertyslot_next_value]
ppropertyslot_next_value.STATE = PROP_VALUE (DIRECT pvalue_next)
pvalue_next = PSTRING_CARRIER (REQUEST_STRING n_next_string) ($ptascii("31"))
$string_carrier_valid(S_return, pvalue_next)
$objectprops_valid(S_return, [pobjectprops_root, pobjectprops_old_node, pobjectprops_next_node, pobjectprops_old_leaf, pobjectprops_next_leaf])
$call_reference_operand_valid(S_return, REFERENCE n_payload) /\ $call_reference_operand_valid(S_return, REFERENCE n_next_payload)
$node_children(S_return, HOBJECT n_object) = [HARRAY n_old_array]
$node_children(S_return, HARRAY n_old_array) = [HOBJECT n_old_node, HOBJECT n_old_node]
$node_children(S_return, HOBJECT n_old_node) = [HCELL n_payload]
$node_children(S_return, HCELL n_payload) = [HOBJECT n_old_leaf]
$node_children(S_return, HOBJECT n_next_node) = [HCELL n_next_payload]
$node_children(S_return, HCELL n_next_payload) = [HOBJECT n_next_leaf]
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source) = 3 /\ $heap_owners(H_return, HOBJECT n_object) = 3
$heap_owners(H_return, HARRAY n_old_array) = 2 /\ $heap_owners(H_return, HOBJECT n_old_node) = 2
$heap_owners(H_return, HCELL n_payload) = 3 /\ $heap_owners(H_return, HOBJECT n_old_leaf) = 1
$heap_owners(H_return, HARRAY n_next_array) = 1 /\ $heap_owners(H_return, HOBJECT n_next_node) = 2
$heap_owners(H_return, HCELL n_next_payload) = 2 /\ $heap_owners(H_return, HOBJECT n_next_leaf) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $mof_seek(S_after_return, 1, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_root)
$objectprops_record_at(S_pre.OBJECTPROPS, n_old_node) = (pobjectprops_old_node)
$objectprops_record_at(S_pre.OBJECTPROPS, n_old_leaf) = (pobjectprops_old_leaf)
$named_reference_notice_array(S_pre, PARRAY n_old_array) /\ $named_reference_notice_array(S_pre, PARRAY n_next_array)
$named_reference_notice_object(S_pre, POBJECT n_old_node) /\ $named_reference_notice_object(S_pre, POBJECT n_next_node)
$named_reference_notice_object_ancestors(S_pre, [n_old_array, n_next_array])
~$update_warning_no_objects($heap_reach([HARRAY n_old_array], eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
$propref_at(S_pre.PROPREFS, n_payload) = eps /\ $propref_at(S_pre.PROPREFS, n_next_payload) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.REFCOERCIONS = eps /\ S_pre.CONTAINERINITS = eps
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
$mof_output(S_pre.EVENTS) = $ptascii("A;M:17:17;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source) = 2 /\ $heap_owners(H_pre, HOBJECT n_object) = 3
$heap_owners(H_pre, HARRAY n_old_array) = 2 /\ $heap_owners(H_pre, HOBJECT n_old_node) = 2
$heap_owners(H_pre, HCELL n_payload) = 3 /\ $heap_owners(H_pre, HOBJECT n_old_leaf) = 1
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

THROW = r"""
S_throw_return = $mof_seek(S_throw_initial, 0, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("MixedObjectArrayThrow48\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (POBJECT n_throw_object)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_object) = (pobjectprops_throw_root)
pobjectprops_throw_root.SLOTS = [{DECL eps, NAME ($ptascii("bag")), STATE (PROP_VALUE (DIRECT (PARRAY n_throw_array)))}]
S_throw_return.ARRAYS[n_throw_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_throw_node)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (POBJECT n_throw_node))]
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_node) = (pobjectprops_throw_node)
pobjectprops_throw_node.SLOTS = [{DECL eps, NAME ($ptascii("one")), STATE (PROP_VALUE (ALIAS n_throw_payload))}, {DECL eps, NAME ($ptascii("two")), STATE (PROP_VALUE (ALIAS n_throw_payload))}]
S_throw_return.STORE[n_throw_payload] = DEFINED (POBJECT n_throw_leaf)
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_leaf) = (pobjectprops_throw_leaf)
pobjectprops_throw_leaf.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_throw))}]
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_return, pvalue_throw)
S_throw_return.GLOBALTABLE = (psymboltable_throw)
$lookup(psymboltable_throw.ENV, $ptascii("payload")) = eps /\ $lookup(psymboltable_throw.ENV, $ptascii("alias")) = eps
$lookup(psymboltable_throw.ENV, $ptascii("node")) = eps /\ $lookup(psymboltable_throw.ENV, $ptascii("bag")) = eps
$lookup(psymboltable_throw.ENV, $ptascii("snapshot")) = (n_throw_snapshot)
S_throw_return.STORE[n_throw_snapshot] = DEFINED pvalue_throw
$lookup(psymboltable_throw.ENV, $ptascii("wRoot")) = (n_throw_root_cv)
$lookup(psymboltable_throw.ENV, $ptascii("wNode")) = (n_throw_node_cv)
$lookup(psymboltable_throw.ENV, $ptascii("wLeaf")) = (n_throw_leaf_cv)
S_throw_return.STORE[n_throw_root_cv] = DEFINED (POBJECT n_throw_root_weak)
S_throw_return.STORE[n_throw_node_cv] = DEFINED (POBJECT n_throw_node_weak)
S_throw_return.STORE[n_throw_leaf_cv] = DEFINED (POBJECT n_throw_leaf_weak)
S_throw_return.OBJECTS[n_throw_root_weak] = WEAKREFERENCE (n_throw_object)
S_throw_return.OBJECTS[n_throw_node_weak] = WEAKREFERENCE (n_throw_node)
S_throw_return.OBJECTS[n_throw_leaf_weak] = WEAKREFERENCE (n_throw_leaf)
S_throw_after_return = $drive(S_throw_return, 1)[.COMPLETION = NORMAL]
H_throw_return = $heap_graph(S_throw_after_return)
$heap_owners(H_throw_return, HOBJECT n_throw_object) = 2 /\ $heap_owners(H_throw_return, HARRAY n_throw_array) = 1
$heap_owners(H_throw_return, HOBJECT n_throw_node) = 2 /\ $heap_owners(H_throw_return, HCELL n_throw_payload) = 2 /\ $heap_owners(H_throw_return, HOBJECT n_throw_leaf) = 1
$heap_valid(H_throw_return)
S_throw_pre = $mof_seek(S_throw_after_return, 1, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (POBJECT n_throw_object)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps
$node_children(S_throw_pre, HOBJECT n_throw_object) = [HARRAY n_throw_array]
$node_children(S_throw_pre, HARRAY n_throw_array) = [HOBJECT n_throw_node, HOBJECT n_throw_node]
$node_children(S_throw_pre, HOBJECT n_throw_node) = [HCELL n_throw_payload, HCELL n_throw_payload]
$node_children(S_throw_pre, HCELL n_throw_payload) = [HOBJECT n_throw_leaf]
$named_reference_notice_array(S_throw_pre, PARRAY n_throw_array)
$named_reference_notice_object(S_throw_pre, POBJECT n_throw_node)
$named_reference_notice_object_ancestors(S_throw_pre, [n_throw_array])
S_throw_pre.PARAMETERBACKINGS = eps /\ S_throw_pre.PROPREFS = eps /\ S_throw_pre.REFCOERCIONS = eps /\ S_throw_pre.CONTAINERINITS = eps
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$mof_output(S_throw_pre.EVENTS) = $ptascii("T;M;")
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pre, HARRAY n_throw_array) = 1
$heap_owners(H_throw_pre, HOBJECT n_throw_node) = 2 /\ $heap_owners(H_throw_pre, HCELL n_throw_payload) = 2 /\ $heap_owners(H_throw_pre, HOBJECT n_throw_leaf) = 1
$heap_valid(H_throw_pre) /\ $call_descriptors_valid(S_throw_pre)
""".strip().splitlines()

QUIET = r"""
S_quiet_shared = $mof_seek(S_quiet_initial, 2, 14000)[.COMPLETION = NORMAL]
$mof_ready(S_quiet_shared, 2)
~$error_handler_eligible(S_quiet_shared, 8)
$lookup(S_quiet_shared.ENV, $ptascii("r")) = (n_quiet_private)
$lookup(S_quiet_shared.ENV, $ptascii("source")) = (n_quiet_source)
$lookup(S_quiet_shared.ENV, $ptascii("sourceAlias")) = (n_quiet_source)
$lookup(S_quiet_shared.ENV, $ptascii("keeper")) = (n_quiet_keeper)
$lookup(S_quiet_shared.ENV, $ptascii("outside")) = (n_quiet_outside)
$lookup(S_quiet_shared.ENV, $ptascii("payload")) = (n_quiet_payload)
$lookup(S_quiet_shared.ENV, $ptascii("payloadAlias")) = (n_quiet_payload)
$lookup(S_quiet_shared.ENV, $ptascii("nextPayload")) = (n_quiet_next_payload)
$lookup(S_quiet_shared.ENV, $ptascii("nextBag")) = (n_quiet_next_bag_cv)
$lookup(S_quiet_shared.ENV, $ptascii("snapshot")) = (n_quiet_snapshot)
S_quiet_shared.STORE[n_quiet_private] = DEFINED (POBJECT n_quiet_object)
S_quiet_shared.STORE[n_quiet_source] = DEFINED (POBJECT n_quiet_object) /\ S_quiet_shared.STORE[n_quiet_keeper] = DEFINED (POBJECT n_quiet_object)
S_quiet_shared.STORE[n_quiet_outside] = DEFINED (PARRAY n_quiet_old_array)
S_quiet_shared.STORE[n_quiet_payload] = DEFINED (POBJECT n_quiet_old_leaf)
S_quiet_shared.STORE[n_quiet_next_payload] = DEFINED (POBJECT n_quiet_next_leaf)
S_quiet_shared.STORE[n_quiet_next_bag_cv] = DEFINED (PARRAY n_quiet_next_array)
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_object) = (pobjectprops_quiet_root)
pobjectprops_quiet_root.SLOTS = [{DECL eps, NAME ($ptascii("bag")), STATE (PROP_VALUE (DIRECT (PARRAY n_quiet_current_array)))}]
S_quiet_shared.ARRAYS[n_quiet_current_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_quiet_old_node))]
S_quiet_shared.ARRAYS[n_quiet_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_quiet_old_node)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (POBJECT n_quiet_old_node))]
S_quiet_shared.ARRAYS[n_quiet_next_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_quiet_next_node)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (POBJECT n_quiet_next_node))]
n_quiet_current_array =/= n_quiet_old_array /\ n_quiet_current_array =/= n_quiet_next_array
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_old_node) = (pobjectprops_quiet_old_node)
pobjectprops_quiet_old_node.SLOTS = [{DECL eps, NAME ($ptascii("item")), STATE (PROP_VALUE (ALIAS n_quiet_payload))}]
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_next_node) = (pobjectprops_quiet_next_node)
pobjectprops_quiet_next_node.SLOTS = [{DECL eps, NAME ($ptascii("item")), STATE (PROP_VALUE (ALIAS n_quiet_next_payload))}]
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_old_leaf) = (pobjectprops_quiet_old_leaf)
pobjectprops_quiet_old_leaf.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("18")))))}]
S_quiet_shared.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet_original
pvalue_quiet_original = PSTRING_CARRIER (REQUEST_STRING n_quiet_string) ($ptascii("17"))
$string_carrier_valid(S_quiet_shared, pvalue_quiet_original)
$lookup(S_quiet_shared.ENV, $ptascii("wRoot")) = (n_quiet_root_weak_cv)
S_quiet_shared.STORE[n_quiet_root_weak_cv] = DEFINED (POBJECT n_quiet_root_weak)
$weakref_get(S_quiet_shared, n_quiet_root_weak) = POBJECT n_quiet_object
$lookup(S_quiet_shared.ENV, $ptascii("wOldNode")) = (n_quiet_old_node_weak_cv)
S_quiet_shared.STORE[n_quiet_old_node_weak_cv] = DEFINED (POBJECT n_quiet_old_node_weak)
$weakref_get(S_quiet_shared, n_quiet_old_node_weak) = POBJECT n_quiet_old_node
$lookup(S_quiet_shared.ENV, $ptascii("wOldLeaf")) = (n_quiet_old_leaf_weak_cv)
S_quiet_shared.STORE[n_quiet_old_leaf_weak_cv] = DEFINED (POBJECT n_quiet_old_leaf_weak)
$weakref_get(S_quiet_shared, n_quiet_old_leaf_weak) = POBJECT n_quiet_old_leaf
$lookup(S_quiet_shared.ENV, $ptascii("wNewNode")) = (n_quiet_next_node_weak_cv)
S_quiet_shared.STORE[n_quiet_next_node_weak_cv] = DEFINED (POBJECT n_quiet_next_node_weak)
$weakref_get(S_quiet_shared, n_quiet_next_node_weak) = POBJECT n_quiet_next_node
$lookup(S_quiet_shared.ENV, $ptascii("wNewLeaf")) = (n_quiet_next_leaf_weak_cv)
S_quiet_shared.STORE[n_quiet_next_leaf_weak_cv] = DEFINED (POBJECT n_quiet_next_leaf_weak)
$weakref_get(S_quiet_shared, n_quiet_next_leaf_weak) = POBJECT n_quiet_next_leaf
H_quiet = $heap_graph(S_quiet_shared)
$heap_owners(H_quiet, HOBJECT n_quiet_object) = 3
$heap_owners(H_quiet, HARRAY n_quiet_old_array) = 1
$heap_owners(H_quiet, HARRAY n_quiet_current_array) = 1
$heap_owners(H_quiet, HARRAY n_quiet_next_array) = 1
$heap_owners(H_quiet, HOBJECT n_quiet_old_node) = 3
$heap_owners(H_quiet, HCELL n_quiet_payload) = 3
$heap_owners(H_quiet, HOBJECT n_quiet_old_leaf) = 1
$heap_owners(H_quiet, HOBJECT n_quiet_next_node) = 2
$heap_owners(H_quiet, HCELL n_quiet_next_payload) = 2
$heap_owners(H_quiet, HOBJECT n_quiet_next_leaf) = 1
$heap_valid(H_quiet) /\ $call_descriptors_valid(S_quiet_shared)
S_quiet_full = $drive(S_quiet_shared, 18000)
S_quiet_full.COMPLETION = NORMAL /\ S_quiet_full.TODO = eps /\ S_quiet_full.CURRENT = eps /\ S_quiet_full.FRAMES = eps
~((HOBJECT n_quiet_object) <- S_quiet_full.ALLOCATIONS)
~((HOBJECT n_quiet_old_node) <- S_quiet_full.ALLOCATIONS)
~((HOBJECT n_quiet_old_leaf) <- S_quiet_full.ALLOCATIONS)
~((HOBJECT n_quiet_next_node) <- S_quiet_full.ALLOCATIONS)
~((HOBJECT n_quiet_next_leaf) <- S_quiet_full.ALLOCATIONS)
~((HARRAY n_quiet_old_array) <- S_quiet_full.ALLOCATIONS)
~((HARRAY n_quiet_current_array) <- S_quiet_full.ALLOCATIONS)
~((HARRAY n_quiet_next_array) <- S_quiet_full.ALLOCATIONS)
~((HCELL n_quiet_payload) <- S_quiet_full.ALLOCATIONS)
~((HCELL n_quiet_next_payload) <- S_quiet_full.ALLOCATIONS)
$weakref_get(S_quiet_full, n_quiet_root_weak) = PNULL
$weakref_get(S_quiet_full, n_quiet_old_node_weak) = PNULL
$weakref_get(S_quiet_full, n_quiet_old_leaf_weak) = PNULL
$weakref_get(S_quiet_full, n_quiet_next_node_weak) = PNULL
$weakref_get(S_quiet_full, n_quiet_next_leaf_weak) = PNULL
S_quiet_full.STORE[n_quiet_private] = DEFINED (PINT 37) /\ S_quiet_full.STORE[n_quiet_source] = DEFINED (PINT 7)
S_quiet_full.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet_original
$string_carrier_valid(S_quiet_full, pvalue_quiet_original)
$heap_valid($heap_graph(S_quiet_full)) /\ $call_descriptors_valid(S_quiet_full)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops_root.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object) /\ ~$positional_reference_notice_pending(S_pre)
S_scalar = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_object, [ppropertyslot_bag[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_scalar, POBJECT n_object) /\ $positional_reference_notice_pending(S_scalar)
H_scalar = $heap_graph(S_scalar)
$heap_owners(H_scalar, HARRAY n_old_array) = 1 /\ $heap_owners(H_scalar, HOBJECT n_old_node) = 2 /\ $heap_owners(H_scalar, HCELL n_payload) = 3 /\ $heap_owners(H_scalar, HOBJECT n_old_leaf) = 1
$heap_valid(H_scalar) /\ $call_descriptors_valid(S_scalar)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (POBJECT n_object)]
~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ ~$positional_reference_notice_pending(S_throw_pre)
S_throw_fenced = $drive(S_throw_pre, 1)
S_throw_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_throw_fenced.EVENTS = S_throw_pre.EVENTS
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_object(S_pre, POBJECT n_object) /\ $positional_reference_notice_pending(S_pre)
$named_reference_notice_heap_object(S_pre, POBJECT n_object, eps, eps)
$named_reference_notice_heap_object_slots(S_pre, pobjectprops_root.SLOTS, eps, [n_object])
$named_reference_notice_heap_array(S_pre, PARRAY n_old_array, eps, [n_object])
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
$error_call_valid(S_notice, perrorcall)
$lookup(S_notice.ENV, $ptascii("wRoot")) = (n_root_weak_cv)
S_notice.STORE[n_root_weak_cv] = DEFINED (POBJECT n_root_weak)
$weakref_get(S_notice, n_root_weak) = POBJECT n_object
$lookup(S_notice.ENV, $ptascii("wOldNode")) = (n_old_node_weak_cv)
S_notice.STORE[n_old_node_weak_cv] = DEFINED (POBJECT n_old_node_weak)
$weakref_get(S_notice, n_old_node_weak) = POBJECT n_old_node
$lookup(S_notice.ENV, $ptascii("wOldLeaf")) = (n_old_leaf_weak_cv)
S_notice.STORE[n_old_leaf_weak_cv] = DEFINED (POBJECT n_old_leaf_weak)
$weakref_get(S_notice, n_old_leaf_weak) = POBJECT n_old_leaf
$lookup(S_notice.ENV, $ptascii("wNewNode")) = (n_next_node_weak_cv)
S_notice.STORE[n_next_node_weak_cv] = DEFINED (POBJECT n_next_node_weak)
$weakref_get(S_notice, n_next_node_weak) = POBJECT n_next_node
$lookup(S_notice.ENV, $ptascii("wNewLeaf")) = (n_next_leaf_weak_cv)
S_notice.STORE[n_next_leaf_weak_cv] = DEFINED (POBJECT n_next_leaf_weak)
$weakref_get(S_notice, n_next_leaf_weak) = POBJECT n_next_leaf
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HOBJECT n_object) = 3
$heap_owners(H_notice, HARRAY n_old_array) = 2 /\ $heap_owners(H_notice, HOBJECT n_old_node) = 2
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
S_resume = $mof_seek(S_notice, 3, 9000)[.COMPLETION = NORMAL]
$mof_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (POBJECT n_object) /\ S_resume.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_resume.STORE[n_source] = DEFINED (PINT 7) /\ S_resume.STORE[n_next_bag_cv] = DEFINED (PINT 7)
S_resume.STORE[n_outside_cv] = DEFINED (PARRAY n_outside_array)
n_outside_array =/= n_old_array /\ n_outside_array =/= n_next_array
S_resume.ARRAYS[n_outside_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_old_node)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (POBJECT n_old_node)), ENTRY (KSTRING ($ptascii("mark"))) (DIRECT (PINT 5))]
$objectprops_record_at(S_resume.OBJECTPROPS, n_object) = (pobjectprops_root_resume)
pobjectprops_root_resume.SLOTS = [ppropertyslot_bag_resume]
ppropertyslot_bag_resume.STATE = PROP_VALUE (DIRECT (PARRAY n_next_array))
ppropertyslot_bag_resume = ppropertyslot_bag[.STATE = PROP_VALUE (DIRECT (PARRAY n_next_array))]
$objectprops_record_at(S_resume.OBJECTPROPS, n_old_leaf) = (pobjectprops_old_leaf_resume)
pobjectprops_old_leaf_resume.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_current))}]
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
$objectprops_record_at(S_resume.OBJECTPROPS, n_old_node) = (pobjectprops_old_node)
$objectprops_record_at(S_resume.OBJECTPROPS, n_next_node) = (pobjectprops_next_node)
$objectprops_record_at(S_resume.OBJECTPROPS, n_next_leaf) = (pobjectprops_next_leaf)
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_original) /\ $string_carrier_valid(S_resume, pvalue_next)
~((HARRAY n_old_array) <- S_resume.ALLOCATIONS)
$named_reference_notice_object(S_resume, POBJECT n_object) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HOBJECT n_object) = 2 /\ $heap_owners(H_resume, HARRAY n_outside_array) = 1
$heap_owners(H_resume, HOBJECT n_old_node) = 2 /\ $heap_owners(H_resume, HCELL n_payload) = 3 /\ $heap_owners(H_resume, HOBJECT n_old_leaf) = 1
$heap_owners(H_resume, HARRAY n_next_array) = 1 /\ $heap_owners(H_resume, HOBJECT n_next_node) = 2
$heap_owners(H_resume, HCELL n_next_payload) = 2 /\ $heap_owners(H_resume, HOBJECT n_next_leaf) = 1
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_copy_live = $mof_seek(S_resume, 4, 11000)[.COMPLETION = NORMAL]
$mof_ready(S_copy_live, 4)
$lookup(S_copy_live.ENV, $ptascii("copy")) = (n_copy_cv)
$lookup(S_copy_live.ENV, $ptascii("text")) = (n_text_cv)
S_copy_live.STORE[n_copy_cv] = DEFINED (PARRAY n_next_array)
S_copy_live.STORE[n_text_cv] = DEFINED pvalue_next
$objectprops_record_at(S_copy_live.OBJECTPROPS, n_object) = (pobjectprops_root_written)
pobjectprops_root_written.SLOTS = [ppropertyslot_bag_written]
ppropertyslot_bag_written.STATE = PROP_VALUE (DIRECT (PARRAY n_current_array))
ppropertyslot_bag_written = ppropertyslot_bag[.STATE = PROP_VALUE (DIRECT (PARRAY n_current_array))]
n_current_array =/= n_next_array /\ n_current_array =/= n_outside_array
S_copy_live.ARRAYS[n_current_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (POBJECT n_next_node))]
S_copy_live.ARRAYS[n_next_array].ITEMS = S_return.ARRAYS[n_next_array].ITEMS
$objectprops_record_at(S_copy_live.OBJECTPROPS, n_next_node) = (pobjectprops_next_node)
$objectprops_record_at(S_copy_live.OBJECTPROPS, n_next_leaf) = (pobjectprops_next_leaf_written)
pobjectprops_next_leaf_written.SLOTS = [ppropertyslot_next_value[.STATE = PROP_VALUE (DIRECT (PSTRING ($ptascii("32"))))]]
H_copy_live = $heap_graph(S_copy_live)
$heap_owners(H_copy_live, HARRAY n_next_array) = 1 /\ $heap_owners(H_copy_live, HARRAY n_current_array) = 1
$heap_owners(H_copy_live, HOBJECT n_next_node) = 3 /\ $heap_owners(H_copy_live, HCELL n_next_payload) = 2 /\ $heap_owners(H_copy_live, HOBJECT n_next_leaf) = 1
$heap_valid(H_copy_live) /\ $call_descriptors_valid(S_copy_live)
S_written = $mof_seek(S_copy_live, 5, 7000)[.COMPLETION = NORMAL]
$mof_ready(S_written, 5)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
$objectprops_record_at(S_written.OBJECTPROPS, n_object) = (pobjectprops_root_written)
~((HARRAY n_next_array) <- S_written.ALLOCATIONS) /\ ~((HCELL n_copy_cv) <- S_written.ALLOCATIONS) /\ ~((HCELL n_text_cv) <- S_written.ALLOCATIONS)
S_written.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_written, pvalue_original) /\ $string_carrier_valid(S_written, pvalue_current) /\ $string_carrier_valid(S_written, pvalue_next)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HOBJECT n_object) = 2 /\ $heap_owners(H_written, HARRAY n_current_array) = 1 /\ $heap_owners(H_written, HOBJECT n_next_node) = 1
$heap_owners(H_written, HCELL n_next_payload) = 2 /\ $heap_owners(H_written, HOBJECT n_next_leaf) = 1
$heap_owners(H_written, HARRAY n_outside_array) = 1 /\ $heap_owners(H_written, HOBJECT n_old_node) = 2 /\ $heap_owners(H_written, HCELL n_payload) = 3
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_private_overwritten = $mof_seek(S_written, 6, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_private_overwritten, 6)
$lookup(S_private_overwritten.ENV, $ptascii("out")) = (n_next_payload)
S_private_overwritten.STORE[n_private] = DEFINED (PINT 37)
$heap_owners($heap_graph(S_private_overwritten), HOBJECT n_object) = 1
$heap_owners($heap_graph(S_private_overwritten), HCELL n_next_payload) = 3
S_parent_retired = $mof_seek(S_private_overwritten, 7, 7000)[.COMPLETION = NORMAL]
$mof_ready(S_parent_retired, 7)
~((HOBJECT n_object) <- S_parent_retired.ALLOCATIONS) /\ ~((HARRAY n_current_array) <- S_parent_retired.ALLOCATIONS) /\ ~((HOBJECT n_next_node) <- S_parent_retired.ALLOCATIONS)
$weakref_get(S_parent_retired, n_root_weak) = PNULL /\ $weakref_get(S_parent_retired, n_next_node_weak) = PNULL
$weakref_get(S_parent_retired, n_next_leaf_weak) = POBJECT n_next_leaf /\ $weakref_get(S_parent_retired, n_old_node_weak) = POBJECT n_old_node
H_parent_retired = $heap_graph(S_parent_retired)
$heap_owners(H_parent_retired, HCELL n_next_payload) = 2 /\ $heap_owners(H_parent_retired, HOBJECT n_next_leaf) = 1
$heap_owners(H_parent_retired, HARRAY n_outside_array) = 1 /\ $heap_owners(H_parent_retired, HOBJECT n_old_node) = 2
$heap_owners(H_parent_retired, HCELL n_payload) = 3 /\ $heap_owners(H_parent_retired, HOBJECT n_old_leaf) = 1
$heap_valid(H_parent_retired) /\ $call_descriptors_valid(S_parent_retired)
S_old_node_retired = $mof_seek(S_parent_retired, 8, 7000)[.COMPLETION = NORMAL]
$mof_ready(S_old_node_retired, 8)
~((HARRAY n_outside_array) <- S_old_node_retired.ALLOCATIONS) /\ ~((HOBJECT n_old_node) <- S_old_node_retired.ALLOCATIONS)
$weakref_get(S_old_node_retired, n_old_node_weak) = PNULL /\ $weakref_get(S_old_node_retired, n_old_leaf_weak) = POBJECT n_old_leaf
H_old_node_retired = $heap_graph(S_old_node_retired)
$heap_owners(H_old_node_retired, HCELL n_payload) = 2 /\ $heap_owners(H_old_node_retired, HOBJECT n_old_leaf) = 1
$heap_valid(H_old_node_retired) /\ $call_descriptors_valid(S_old_node_retired)
S_old_leaf_retired = $mof_seek(S_old_node_retired, 9, 7000)[.COMPLETION = NORMAL]
$mof_ready(S_old_leaf_retired, 9)
S_old_leaf_retired.STORE[n_payload] = DEFINED (PINT 41)
~((HOBJECT n_old_leaf) <- S_old_leaf_retired.ALLOCATIONS) /\ (HCELL n_payload) <- S_old_leaf_retired.ALLOCATIONS
$weakref_get(S_old_leaf_retired, n_old_leaf_weak) = PNULL
$heap_owners($heap_graph(S_old_leaf_retired), HCELL n_payload) = 1
S_new_cv_retired = $mof_seek(S_old_leaf_retired, 10, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_new_cv_retired, 10)
$lookup(S_new_cv_retired.ENV, $ptascii("nextPayload")) = eps
$lookup(S_new_cv_retired.ENV, $ptascii("out")) = (n_next_payload)
$heap_owners($heap_graph(S_new_cv_retired), HCELL n_next_payload) = 1 /\ $heap_owners($heap_graph(S_new_cv_retired), HOBJECT n_next_leaf) = 1
S_new_leaf_retired = $mof_seek(S_new_cv_retired, 11, 6000)[.COMPLETION = NORMAL]
$mof_ready(S_new_leaf_retired, 11)
S_new_leaf_retired.STORE[n_next_payload] = DEFINED (PINT 43)
~((HOBJECT n_next_leaf) <- S_new_leaf_retired.ALLOCATIONS) /\ (HCELL n_next_payload) <- S_new_leaf_retired.ALLOCATIONS
$weakref_get(S_new_leaf_retired, n_next_leaf_weak) = PNULL
$heap_owners($heap_graph(S_new_leaf_retired), HCELL n_next_payload) = 1
S_full = $drive(S_new_leaf_retired, 15000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
~((HCELL n_payload) <- S_full.ALLOCATIONS) /\ ~((HCELL n_next_payload) <- S_full.ALLOCATIONS)
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source] = DEFINED (PINT 7)
S_full.STORE[n_snapshot] = DEFINED pvalue_original
$string_carrier_valid(S_full, pvalue_original)
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
S_throw_pending = $mof_seek(S_throw_notice, 20, 7000)[.COMPLETION = NORMAL]
$mof_ready(S_throw_pending, 20)
S_throw_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw_pending*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw_pending, perrorcall_entered) /\ $throwable_live(S_throw_pending, n_exception)
H_throw_pending = $heap_graph(S_throw_pending)
$heap_owners(H_throw_pending, HCELL n_throw_private) = 1 /\ $heap_owners(H_throw_pending, HOBJECT n_throw_object) = 1
$heap_owners(H_throw_pending, HARRAY n_throw_array) = 1 /\ $heap_owners(H_throw_pending, HOBJECT n_throw_node) = 2
$heap_owners(H_throw_pending, HCELL n_throw_payload) = 2 /\ $heap_owners(H_throw_pending, HOBJECT n_throw_leaf) = 1
$node_children(S_throw_pending, HARRAY n_throw_array) = [HOBJECT n_throw_node, HOBJECT n_throw_node]
$property_release_nodes(pobjectprops_throw_node.SLOTS) = [HCELL n_throw_payload, HCELL n_throw_payload]
$node_children(S_throw_pending, HCELL n_throw_payload) = [HOBJECT n_throw_leaf]
$heap_valid(H_throw_pending)
S_cancel = $drive(S_throw_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS) /\ ~((HOBJECT n_throw_object) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_array) <- S_cancel.ALLOCATIONS) /\ ~((HOBJECT n_throw_node) <- S_cancel.ALLOCATIONS)
~((HCELL n_throw_payload) <- S_cancel.ALLOCATIONS) /\ ~((HOBJECT n_throw_leaf) <- S_cancel.ALLOCATIONS)
$weakref_get(S_cancel, n_throw_root_weak) = PNULL /\ $weakref_get(S_cancel, n_throw_node_weak) = PNULL /\ $weakref_get(S_cancel, n_throw_leaf_weak) = PNULL
$heap_owners($heap_graph(S_cancel), HARRAY n_throw_array) = 0 /\ $heap_owners($heap_graph(S_cancel), HOBJECT n_throw_node) = 0 /\ $heap_owners($heap_graph(S_cancel), HCELL n_throw_payload) = 0
S_cancel.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
S_throw_full = $drive(S_cancel, 15000)
S_throw_full.COMPLETION = NORMAL /\ S_throw_full.TODO = eps /\ S_throw_full.CURRENT = eps /\ S_throw_full.FRAMES = eps
S_throw_full.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full.STORE[n_throw_source] = DEFINED (PINT 7) /\ S_throw_full.STORE[n_throw_snapshot] = DEFINED pvalue_throw
$string_carrier_valid(S_throw_full, pvalue_throw)
$heap_valid($heap_graph(S_throw_full)) /\ $call_descriptors_valid(S_throw_full)
""".strip().splitlines()

CONTROLS = r"""
$named_reference_notice_graph_object(S_notice, POBJECT n_object, eps)
$named_reference_notice_graph_object_slots(S_notice, pobjectprops_root.SLOTS, [n_object])
$named_reference_notice_heap_object(S_notice, POBJECT n_old_leaf, [n_old_array], [n_object, n_old_node])
n_old_array = n_old_leaf
~$named_reference_notice_heap_object(S_notice, POBJECT n_object, eps, [n_object])
~$named_reference_notice_heap_array(S_notice, PARRAY n_old_array, [n_old_array], eps)
~$named_reference_notice_object(S_notice[.LITERALARRAYRETAINED = [n_old_array]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.LITERALARRAYDEBTS = [n_old_array]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HARRAY n_old_array]], POBJECT n_object)
S_notice.POOLS = ppool :: ppool_tail*
S_pooled = S_notice[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_old_array)]] :: ppool_tail*]
(HARRAY n_old_array) <- $heap_reach($pools_nodes(S_pooled.POOLS), eps, $allocation_edges(S_pooled, S_pooled.ALLOCATIONS))
~$named_reference_notice_object(S_pooled, POBJECT n_object)
S_immutable = S_notice[.ARRAYS[n_old_array] = $array_empty()][.GC.IMMUTABLE = [n_old_array]]
$array_immutable(S_immutable, n_old_array)
~$named_reference_notice_object(S_immutable, POBJECT n_object)
~$named_reference_notice_object(S_notice[.REFCELLS = eps], POBJECT n_object)
~$named_reference_notice_object(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_payload)], POBJECT n_object)
~$named_reference_notice_object(S_notice[.STORE[n_payload] = UNDEFINED], POBJECT n_object)
~$named_reference_notice_object(S_notice[.PROPREFS = [{CELL n_payload, SOURCES eps}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.REFCOERCIONS = [{CELL n_payload, SITE porigin_call, LINE 0, VALUE eps}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_payload, LINE 0, VALUE eps}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.CONTAINERINITS = [{CELL n_payload, ARRAY n_old_array, SITE porigin_call, LINE 0}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.LITERALREFRETAINED = [n_payload]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.LITERALREFDEBTS = [n_payload]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HCELL n_payload]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HOBJECT n_old_leaf)], POBJECT n_object)
~$named_reference_notice_object(S_notice[.OBJECTS[n_old_leaf] = S_notice.OBJECTS[n_root_weak]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.OBJECTTABLES = [{OBJECT n_old_leaf, TABLE 0}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.DESTRUCTION.CALLED = [n_old_leaf]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.GC.WORKER = (0)], POBJECT n_object)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HOBJECT n_old_leaf]], POBJECT n_object)
S_object_cycle = S_notice[.ARRAYS[n_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("back"))) (DIRECT (POBJECT n_object))]]
~$named_reference_notice_object(S_object_cycle, POBJECT n_object)
S_array_cycle = S_notice[.STORE[n_payload] = DEFINED (PARRAY n_old_array)]
~$named_reference_notice_object(S_array_cycle, POBJECT n_object)
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
S_bad_id = S_notice[.OBJECTPROPS = $objectprops_set(S_notice.OBJECTPROPS, n_old_leaf, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_bad_id))}])]
S_bad_bytes = S_notice[.OBJECTPROPS = $objectprops_set(S_notice.OBJECTPROPS, n_old_leaf, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_bad_bytes))}])]
~$named_reference_notice_object(S_bad_id, POBJECT n_object) /\ ~$named_reference_notice_object(S_bad_bytes, POBJECT n_object)
S_raw = S_notice[.OBJECTPROPS = $objectprops_set(S_notice.OBJECTPROPS, n_old_leaf, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("17")))))}])]
~$named_reference_notice_object(S_raw, POBJECT n_object)
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
S_nul_child = S_nul[.OBJECTPROPS = $objectprops_set(S_nul.OBJECTPROPS, n_old_leaf, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_nul))}])]
~$named_reference_notice_object(S_nul_child, POBJECT n_object)
~$named_reference_notice_object(S_written, POBJECT n_object)
~$positional_reference_notice_source(S_pre, pcalltarget, 0, eps)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_parent_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_parent_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_parent_retired, 2)
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
    reached = [initial('S_initial', 0)] + RETURN + COMMON
    if args.front:
        reached += [initial('S_throw_initial', 1)] + THROW
        derived = FRONT
    else:
        reached += PRIVATE + [initial('S_throw_initial', 1)] + THROW + CANCEL
        reached += ['$mof_output(S_full.EVENTS) = $ptascii(' + json.dumps(cases[0]['native_stdout']) + ')', '$mof_output(S_throw_full.EVENTS) = $ptascii(' + json.dumps(cases[1]['native_stdout']) + ')']
        derived = CONTROLS
    reached += [initial('S_quiet_initial', 2)] + QUIET
    reached.append('$mof_output(S_quiet_full.EVENTS) = $ptascii(' + json.dumps(cases[2]['native_stdout']) + ')')
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'mixed-object-array-field-front' if args.front else 'mixed-object-array-field-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
