#!/usr/bin/env python3
"""Isolate the genuine finite rooted-property Notice admission fence."""
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
PREFIX = r'''
dec $fpn_output(pevent*) : ptbytes
def $fpn_output(eps) = eps
def $fpn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $fpn_output(pevent*)
dec $fpn_ready(pstate) : bool
def $fpn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $fpn_output(S.EVENTS) = $ptascii("A;")
def $fpn_ready(S) = false -- otherwise
dec $fpn_seek(pstate, nat) : pstate
def $fpn_seek(S, n) = S
  -- if $fpn_ready(S) \/ n = 0 \/ S.TODO = eps
def $fpn_seek(S, n) = $fpn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$fpn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fpn_seek(S, n) = S -- otherwise
dec $fpn_stage(pstate, nat) : bool
def $fpn_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;")
def $fpn_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;")
def $fpn_stage(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;")
def $fpn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;")
def $fpn_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T;C;")
def $fpn_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T;C;U;D;")
def $fpn_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T;C;U;D;V;Z;")
def $fpn_stage(S, 7) = true
  -- if S.CURRENT = eps
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T;C;U;D;V;Z;41:41;N;Q;")
def $fpn_stage(S, 8) = true
  -- if S.CURRENT = eps
  -- if $fpn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T;C;U;D;V;Z;41:41;N;Q;K;")
def $fpn_stage(S, n) = false -- otherwise
dec $fpn_after(pstate, nat, nat) : pstate
def $fpn_after(S, n_stage, n) = S
  -- if $fpn_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $fpn_after(S, n_stage, n) = $fpn_after($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$fpn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fpn_after(S, n_stage, n) = $fpn_after($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$fpn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $fpn_after(S, n_stage, n) = S -- otherwise
'''

REACHED = r'''
S_pre = $fpn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$fpn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("a")) = (n_a_cv)
$lookup(S_pre.ENV, $ptascii("b")) = (n_b_cv)
$lookup(S_pre.ENV, $ptascii("c")) = (n_c_cv)
$lookup(S_pre.ENV, $ptascii("d")) = (n_d_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.STORE[n_a_cv] = DEFINED (POBJECT n_a)
S_pre.STORE[n_b_cv] = DEFINED (POBJECT n_b)
S_pre.STORE[n_c_cv] = DEFINED (POBJECT n_c)
S_pre.STORE[n_d_cv] = DEFINED (POBJECT n_d)
S_pre.OBJECTS[n_a] = INSTANCE porigin_holder
S_pre.OBJECTS[n_b] = INSTANCE porigin_holder
S_pre.OBJECTS[n_c] = INSTANCE porigin_holder
S_pre.OBJECTS[n_d] = INSTANCE porigin_holder
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_holder
pclassdesc.PROPERTIES = [ppropertydesc]
ppropertydesc.ORIGIN = ppropertyid
ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_d ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_d ($ptascii("p")) ppropertyid)
$objectprops_record_at(S_pre.OBJECTPROPS, n_a) = (pobjectprops_a)
$objectprops_record_at(S_pre.OBJECTPROPS, n_b) = (pobjectprops_b)
$objectprops_record_at(S_pre.OBJECTPROPS, n_c) = (pobjectprops_c)
$objectprops_record_at(S_pre.OBJECTPROPS, n_d) = (pobjectprops_d)
pobjectprops_a.SLOTS = [{DECL (ppropertyid), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}]
pobjectprops_b.SLOTS = pobjectprops_a.SLOTS /\ pobjectprops_c.SLOTS = pobjectprops_a.SLOTS /\ pobjectprops_d.SLOTS = pobjectprops_a.SLOTS
$node_children(S_pre, HOBJECT n_a) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_b) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_c) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_d) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object_ancestors(S_pre, [n_root])
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
$reference_coercion_at(S_pre.REFCOERCIONS, n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf) /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HCELL n_leaf) = 6 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_a) = 1 /\ $heap_owners(H_pre, HOBJECT n_b) = 1
$heap_owners(H_pre, HOBJECT n_c) = 1 /\ $heap_owners(H_pre, HOBJECT n_d) = 1
$heap_owners(H_pre, HOBJECT n_old) = 2 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_a) <- $heap_prune(H_pre).NODES /\ (HOBJECT n_b) <- $heap_prune(H_pre).NODES
(HOBJECT n_c) <- $heap_prune(H_pre).NODES /\ (HOBJECT n_d) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

PROTOCOL = r'''
~$named_reference_notice_object_property_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_single_b = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid])}]]
$named_reference_notice_object_property_source(S_single_b, n_leaf)
$named_reference_notice_array(S_single_b, PARRAY n_root)
S_single_c = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid])}]]
$named_reference_notice_object_property_source(S_single_c, n_leaf)
$named_reference_notice_array(S_single_c, PARRAY n_root)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
S_unroot_c = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("c"))]
$propref_source_valid(S_unroot_c, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_unroot_c)).NODES
~((HOBJECT n_c) <- $heap_prune($heap_graph(S_unroot_c)).NODES)
~$named_reference_notice_array(S_unroot_c, PARRAY n_root)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_property_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

OWNERSHIP = r'''
n_private = |S_pre.STORE|
S_one = $drive(S_pre, 1)
S_one.COMPLETION = BUDGET
S_notice = S_one[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after = {SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps}
$error_call_valid(S_notice, perrorcall)
S_same = $fpn_after(S_notice, 0, 1024)[.COMPLETION = NORMAL]
$fpn_stage(S_same, 0)
S_same.OBJECTPROPS = S_pre.OBJECTPROPS
$propref_at(S_same.PROPREFS, n_leaf) = (ppropref_same)
|ppropref_same.SOURCES| = 4 /\ $propref_unique_sources(ppropref_same.SOURCES)
$proprefs_valid(S_same) /\ $propref_slots_covered(S_same, S_same.OBJECTPROPS)
S_partial = $fpn_after(S_same, 1, 768)[.COMPLETION = NORMAL]
$fpn_stage(S_partial, 1)
$propref_at(S_partial.PROPREFS, n_leaf) = (ppropref_partial)
|ppropref_partial.SOURCES| = 3
$propref_source_present(S_partial.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid)
$propref_source_present(S_partial.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
$propref_source_present(S_partial.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_d ($ptascii("p")) ppropertyid)
~$propref_source_present(S_partial.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid)
$propref_at(S_partial.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid])})
$node_children(S_partial, HOBJECT n_b) = [HCELL n_new_cv]
$named_reference_notice_array(S_partial, PARRAY n_root)
$proprefs_valid(S_partial) /\ $propref_slots_covered(S_partial, S_partial.OBJECTPROPS)
S_failed = $fpn_after(S_partial, 2, 768)
$fpn_stage(S_failed, 2)
S_failed.PROPREFS = S_partial.PROPREFS
S_failed.STORE[n_leaf] = S_pre.STORE[n_leaf] /\ S_failed.STORE[n_bad_cv] = S_pre.STORE[n_bad_cv]
$propref_at(S_failed.PROPREFS, n_bad_cv) = eps
$proprefs_valid(S_failed) /\ $propref_slots_covered(S_failed, S_failed.OBJECTPROPS)
S_returned = $fpn_after(S_failed, 3, 1536)[.COMPLETION = NORMAL]
$fpn_stage(S_returned, 3)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.PROPREFS = S_partial.PROPREFS
$node_children(S_returned, HOBJECT n_a) = [HCELL n_leaf]
$node_children(S_returned, HOBJECT n_b) = [HCELL n_new_cv]
$node_children(S_returned, HOBJECT n_c) = [HCELL n_leaf]
$node_children(S_returned, HOBJECT n_d) = [HCELL n_leaf]
H_returned = $heap_graph(S_returned)
H_returned = $heap_graph(S_returned[.PROPREFS = eps])
$heap_owners(H_returned, HCELL n_leaf) = 5 /\ $heap_owners(H_returned, HCELL n_new_cv) = 2
$heap_owners(H_returned, HARRAY n_root) = 2 /\ $heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HOBJECT n_a) = 1 /\ $heap_owners(H_returned, HOBJECT n_b) = 1
$heap_owners(H_returned, HOBJECT n_c) = 1 /\ $heap_owners(H_returned, HOBJECT n_d) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2 /\ $heap_owners(H_returned, HOBJECT n_new) = 1
$duplicate_item(S_returned, n_copied, ALIAS n_leaf) = ALIAS n_leaf
$proprefs_valid(S_returned) /\ $propref_slots_covered(S_returned, S_returned.OBJECTPROPS) /\ $objectprops_valid(S_returned, S_returned.OBJECTPROPS) /\ $heap_valid(H_returned)
S_c_unset = $fpn_after(S_returned, 4, 1536)[.COMPLETION = NORMAL]
$fpn_stage(S_c_unset, 4)
$propref_at(S_c_unset.PROPREFS, n_leaf) = (ppropref_c_unset)
|ppropref_c_unset.SOURCES| = 2
$propref_source_valid(S_c_unset, n_leaf, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid)
$propref_source_valid(S_c_unset, n_leaf, OBJECT_PROP_SOURCE n_d ($ptascii("p")) ppropertyid)
~$propref_source_present(S_c_unset.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
$node_children(S_c_unset, HOBJECT n_c) = eps
(HOBJECT n_c) <- $heap_prune($heap_graph(S_c_unset)).NODES
$named_reference_notice_array(S_c_unset, PARRAY n_copied)
H_c_unset = $heap_graph(S_c_unset)
$heap_owners(H_c_unset, HCELL n_leaf) = 4
$proprefs_valid(S_c_unset) /\ $propref_slots_covered(S_c_unset, S_c_unset.OBJECTPROPS) /\ $heap_valid(H_c_unset)
S_d_unset = $fpn_after(S_c_unset, 5, 1024)[.COMPLETION = NORMAL]
$fpn_stage(S_d_unset, 5)
$propref_at(S_d_unset.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid])})
$node_children(S_d_unset, HOBJECT n_d) = eps
(HOBJECT n_d) <- $heap_prune($heap_graph(S_d_unset)).NODES
$named_reference_notice_array(S_d_unset, PARRAY n_copied)
H_d_unset = $heap_graph(S_d_unset)
$heap_owners(H_d_unset, HCELL n_leaf) = 3
$proprefs_valid(S_d_unset) /\ $propref_slots_covered(S_d_unset, S_d_unset.OBJECTPROPS) /\ $heap_valid(H_d_unset)
S_final = $fpn_after(S_d_unset, 6, 1024)[.COMPLETION = NORMAL]
$fpn_stage(S_final, 6)
$propref_at(S_final.PROPREFS, n_leaf) = eps
$propref_at(S_final.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid])})
$node_children(S_final, HOBJECT n_a) = [HCELL n_new_cv]
S_final.STORE[n_leaf] = S_pre.STORE[n_leaf]
$named_reference_notice_array(S_final, PARRAY n_copied)
H_final = $heap_graph(S_final)
$heap_owners(H_final, HCELL n_leaf) = 2 /\ $heap_owners(H_final, HCELL n_new_cv) = 3
$proprefs_valid(S_final) /\ $propref_slots_covered(S_final, S_final.OBJECTPROPS) /\ $heap_valid(H_final)
S_singleton = $fpn_after(S_final, 7, 1536)[.COMPLETION = NORMAL]
$fpn_stage(S_singleton, 7)
S_singleton.STORE[n_leaf] = DEFINED (POBJECT n_old)
$propref_at(S_singleton.PROPREFS, n_leaf) = eps
~((HARRAY n_root) <- S_singleton.ALLOCATIONS)
H_singleton = $heap_graph(S_singleton)
$heap_owners(H_singleton, HCELL n_leaf) = 1 /\ $heap_owners(H_singleton, HOBJECT n_old) = 2
$duplicate_item(S_singleton, n_copied, ALIAS n_leaf) = DIRECT (POBJECT n_old)
S_copied = $fpn_after(S_singleton, 8, 1024)[.COMPLETION = NORMAL]
$fpn_stage(S_copied, 8)
$lookup(S_copied.ENV, $ptascii("snapshot")) = (n_snapshot_cv)
S_copied.STORE[n_snapshot_cv] = DEFINED (PARRAY n_snapshot)
n_snapshot =/= n_copied
S_copied.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_copied.ARRAYS[n_snapshot].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 13))]
$node_children(S_copied, HARRAY n_copied) = [HCELL n_leaf]
$node_children(S_copied, HARRAY n_snapshot) = [HOBJECT n_old]
H_copied = $heap_graph(S_copied)
$heap_owners(H_copied, HCELL n_leaf) = 1 /\ $heap_owners(H_copied, HOBJECT n_old) = 3
$proprefs_valid(S_copied) /\ $propref_slots_covered(S_copied, S_copied.OBJECTPROPS) /\ $objectprops_valid(S_copied, S_copied.OBJECTPROPS) /\ $heap_valid(H_copied)
S_zero = $drive(S_copied, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_copied
$drive($drive(S_copied, 1)[.COMPLETION = NORMAL], 1) = $drive(S_copied, 2)
'''.strip().splitlines()

SOURCES = r'''
S_unroot_c = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("c"))]
$propref_source_valid(S_unroot_c, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_unroot_c)).NODES
~((HOBJECT n_c) <- $heap_prune($heap_graph(S_unroot_c)).NODES)
~$named_reference_notice_array(S_unroot_c, PARRAY n_root)
S_duplicate = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid])}]]
~$named_reference_notice_array(S_duplicate, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_mixed = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid])}]]
~$named_reference_notice_array(S_mixed, PARRAY n_root)
S_wrong_slot = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_c, [{DECL (ppropertyid), NAME ($ptascii("p")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}])]
~$propref_source_valid(S_wrong_slot, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
~$named_reference_notice_array(S_wrong_slot, PARRAY n_root)
S_source_unit = S_pre[.NATIVEEXCESS = [HOBJECT n_c]]
~$named_reference_notice_array(S_source_unit, PARRAY n_root)
S_called = S_pre[.DESTRUCTION.CALLED = [n_c]]
~$named_reference_notice_array(S_called, PARRAY n_root)
pinstancestorage_source = {OBJECT n_c, HANDLE 0, SLOTS pobjectprops_c.SLOTS, NEXT 0, NOTIFY eps, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, USER false}
S_freeing = S_pre[.TODO = [INSTANCE_STORAGE_STEP pinstancestorage_source]]
$instance_storage_freeing(S_freeing, n_c)
~$named_reference_notice_array(S_freeing, PARRAY n_root)
S_table = S_pre[.OBJECTTABLES = [{OBJECT n_c, TABLE n_root}]]
~$named_reference_notice_array(S_table, PARRAY n_root)
S_materialized = $objectprops_mark(S_pre, n_c)
~$named_reference_notice_array(S_materialized, PARRAY n_root)
S_parent = S_pre[.CLASSES = [pclassdesc[.PARENT = ($ptascii("Unknown"))]]]
~$named_reference_notice_array(S_parent, PARRAY n_root)
S_nullable = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
$propref_source_valid(S_nullable, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_protected = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.VISIBILITY = PROPERTY_PROTECTED]]]]]
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_extra = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_c, pobjectprops_c.SLOTS ++ [{DECL eps, NAME ($ptascii("extra")), STATE PROP_VALUE (DIRECT (PINT 0))}])]
$propref_source_valid(S_extra, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
~$named_reference_notice_array(S_extra, PARRAY n_root)
S_owning = S_pre[.STORE[n_leaf] = DEFINED (POBJECT n_new)][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_new, [{DECL eps, NAME ($ptascii("v")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}])]
$propref_source_valid(S_owning, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
$named_reference_notice_object(S_owning, POBJECT n_old)
~$named_reference_notice_array(S_owning, PARRAY n_root)
S_root_unit = S_pre[.NATIVEEXCESS = [HARRAY n_root]]
~$named_reference_notice_array(S_root_unit, PARRAY n_root)
S_cell_unit = S_pre[.NATIVEEXCESS = [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_unit, PARRAY n_root)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--part', choices=('ingress', 'ownership', 'sources'), default='ingress')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('finite_property_alias_stdclass_reference_notice_review_cases.json')
    row, = json.loads(catalogue.read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == digest(types.PHP)
    assert native['source_sha256'] == digest(source) == row['source_sha256']
    directory = args.output.resolve()
    directory.mkdir(parents=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), catalogue, provenance, source, types.PHP,
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): digest(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
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
    reached = REACHED + ([] if args.part == 'ingress' else ADMITTED)
    derived = PROTOCOL if args.part == 'ingress' else SOURCES if args.part == 'sources' else []
    if args.part == 'ownership':
        reached += OWNERSHIP
    checks = [initial] + reached + derived
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    fixture_sha = digest(fixture)
    print(directory, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 1200)
    stable = before == fingerprints() and digest(fixture) == fixture_sha
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'source': str(source), 'source_sha256': digest(source),
        'fixture_sha256': fixture_sha, 'part': args.part, 'conditions': len(checks), 'reached_conditions': len(reached) + 1,
        'derived_conditions': len(derived), 'heap_bindings': len({check.split(' = ', 1)[0] for check in reached if check.startswith('H_') and ' = $heap_graph(' in check}), 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.part, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
