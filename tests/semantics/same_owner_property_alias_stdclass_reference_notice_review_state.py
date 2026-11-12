#!/usr/bin/env python3
"""Isolate the genuine finite same-owner property-slot Notice fence."""
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
dec $sopn_output(pevent*) : ptbytes
def $sopn_output(eps) = eps
def $sopn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $sopn_output(pevent*)
dec $sopn_ready(pstate) : bool
def $sopn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $sopn_output(S.EVENTS) = $ptascii("A;")
def $sopn_ready(S) = false -- otherwise
dec $sopn_seek(pstate, nat) : pstate
def $sopn_seek(S, n) = S
  -- if $sopn_ready(S) \/ n = 0 \/ S.TODO = eps
def $sopn_seek(S, n) = $sopn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$sopn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $sopn_seek(S, n) = S -- otherwise

dec $sopn_plain(ppropertydesc) : bool
def $sopn_plain(ppropertydesc) = true
  -- if ppropertydesc.NAME = ppropertydesc.KEY
  -- if ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ppropertydesc.SETVISIBILITY = eps
  -- if ~ppropertydesc.STATIC /\ ~ppropertydesc.READONLY /\ ~ppropertydesc.FINAL
  -- if ppropertydesc.DEFAULT = PROP_UNINITIALIZED
  -- if ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
  -- if $ptlc(ptbytes_type) = $ptascii("stdclass")
def $sopn_plain(ppropertydesc) = false -- otherwise
dec $sopn_stage(pstate, nat) : bool
def $sopn_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;")
def $sopn_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;")
def $sopn_stage(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;")
def $sopn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;")
def $sopn_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;C;")
def $sopn_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;C;U:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;X;")
def $sopn_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;C;U:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;X;V:Cannot assign int to reference held by property ReviewMultiSlot17::$d of type stdClass;Z;")
def $sopn_stage(S, 7) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;C;U:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;X;V:Cannot assign int to reference held by property ReviewMultiSlot17::$d of type stdClass;Z;41:41;N;Q;")
def $sopn_stage(S, 8) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;B;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;C;U:Cannot assign int to reference held by property ReviewMultiSlot17::$a of type stdClass;X;V:Cannot assign int to reference held by property ReviewMultiSlot17::$d of type stdClass;Z;41:41;N;Q;K;")
def $sopn_stage(S, n) = false -- otherwise
dec $sopn_after(pstate, nat, nat) : pstate
def $sopn_after(S, n_stage, n) = S
  -- if $sopn_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $sopn_after(S, n_stage, n) = $sopn_after($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$sopn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $sopn_after(S, n_stage, n) = $sopn_after($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$sopn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $sopn_after(S, n_stage, n) = S -- otherwise
'''

REACHED = r'''
S_pre = $sopn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$sopn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("holder")) = (n_owner_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.STORE[n_owner_cv] = DEFINED (POBJECT n_owner)
S_pre.OBJECTS[n_owner] = INSTANCE porigin_holder
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_holder
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d]
ppropertydesc_a.ORIGIN = ppropertyid_a
ppropertydesc_b.ORIGIN = ppropertyid_b
ppropertydesc_c.ORIGIN = ppropertyid_c
ppropertydesc_d.ORIGIN = ppropertyid_d
$sopn_plain(ppropertydesc_a) /\ $sopn_plain(ppropertydesc_b)
$sopn_plain(ppropertydesc_c) /\ $sopn_plain(ppropertydesc_d)
~$property_hook_declared(S_pre, n_owner, $ptascii("a")) /\ ~$property_hook_declared(S_pre, n_owner, $ptascii("b"))
~$property_hook_declared(S_pre, n_owner, $ptascii("c")) /\ ~$property_hook_declared(S_pre, n_owner, $ptascii("d"))
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d, OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d)
$objectprops_record_at(S_pre.OBJECTPROPS, n_owner) = (pobjectprops_owner)
pobjectprops_owner.SLOTS = [{DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_b), NAME ($ptascii("b")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_c), NAME ($ptascii("c")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_d), NAME ($ptascii("d")), STATE PROP_VALUE (ALIAS n_leaf)}]
~pobjectprops_owner.MATERIALIZED /\ $objectprops_valid(S_pre, [pobjectprops_owner])
$object_table_at(S_pre.OBJECTTABLES, n_owner) = eps
$node_children(S_pre, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
~$instance_storage_freeing(S_pre, n_owner) /\ ~(n_owner <- S_pre.DESTRUCTION.CALLED)
~$propref_source_queued(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a)
~$propref_source_queued(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b)
~$propref_source_queued(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c)
~$propref_source_queued(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d)
$heap_count(HOBJECT n_owner, S_pre.NATIVEEXCESS) = 0 /\ ~$weakmap_key_waiting(S_pre, n_owner)
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
$heap_owners(H_pre, HOBJECT n_owner) = 1
$heap_owners(H_pre, HOBJECT n_old) = 2 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_owner) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

PROTOCOL = r'''
~$named_reference_notice_object_property_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
S_one = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a]]]][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, [{DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_VALUE (ALIAS n_leaf)}])][.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a])}]]
$propref_source_valid(S_one, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a)
$named_reference_notice_object_property_source(S_one, n_leaf)
$named_reference_notice_array(S_one, PARRAY n_root)
S_dead = S_one[.ENV = $unbind(S_one.ENV, $ptascii("holder"))]
$propref_source_valid(S_dead, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a)
$($heap_owners($heap_graph(S_dead), HCELL n_leaf) > 0)
~((HOBJECT n_owner) <- $heap_prune($heap_graph(S_dead)).NODES)
~$named_reference_notice_object_property_source(S_dead, n_leaf)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_property_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

OWNERSHIP = r'''
n_private = |S_pre.STORE|
S_one_step = $drive(S_pre, 1)
S_one_step.COMPLETION = BUDGET
S_notice = S_one_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after = {SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps}
$error_call_valid(S_notice, perrorcall)
S_same = $sopn_after(S_notice, 0, 1024)[.COMPLETION = NORMAL]
$sopn_stage(S_same, 0)
S_same.OBJECTPROPS = S_pre.OBJECTPROPS
$propref_at(S_same.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a])})
$proprefs_valid(S_same) /\ $propref_slots_covered(S_same, S_same.OBJECTPROPS)
S_partial = $sopn_after(S_same, 1, 768)[.COMPLETION = NORMAL]
$sopn_stage(S_partial, 1)
$propref_at(S_partial.PROPREFS, n_leaf) = (ppropref_partial)
ppropref_partial.SOURCES = [OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d]
$objectprops_record_at(S_partial.OBJECTPROPS, n_owner) = (pobjectprops_partial)
pobjectprops_partial.SLOTS = [{DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_b), NAME ($ptascii("b")), STATE PROP_UNSET}, {DECL (ppropertyid_c), NAME ($ptascii("c")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_d), NAME ($ptascii("d")), STATE PROP_VALUE (ALIAS n_leaf)}]
$node_children(S_partial, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
$named_reference_notice_array(S_partial, PARRAY n_root)
$proprefs_valid(S_partial) /\ $propref_slots_covered(S_partial, S_partial.OBJECTPROPS)
S_failed = $sopn_after(S_partial, 2, 768)
$sopn_stage(S_failed, 2)
S_failed.PROPREFS = S_partial.PROPREFS
$objectprops_record_at(S_failed.OBJECTPROPS, n_owner) = (pobjectprops_partial)
S_failed.STORE[n_leaf] = S_pre.STORE[n_leaf] /\ S_failed.STORE[n_bad_cv] = S_pre.STORE[n_bad_cv]
$propref_at(S_failed.PROPREFS, n_bad_cv) = eps
$proprefs_valid(S_failed) /\ $propref_slots_covered(S_failed, S_failed.OBJECTPROPS)
S_returned = $sopn_after(S_failed, 3, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_returned, 3)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.PROPREFS = S_partial.PROPREFS
$node_children(S_returned, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
H_returned = $heap_graph(S_returned)
H_returned = $heap_graph(S_returned[.PROPREFS = eps])
$heap_owners(H_returned, HCELL n_leaf) = 5
$heap_owners(H_returned, HARRAY n_root) = 2 /\ $heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HOBJECT n_owner) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2 /\ $heap_owners(H_returned, HOBJECT n_new) = 1
$duplicate_item(S_returned, n_copied, ALIAS n_leaf) = ALIAS n_leaf
$proprefs_valid(S_returned) /\ $propref_slots_covered(S_returned, S_returned.OBJECTPROPS) /\ $objectprops_valid(S_returned, S_returned.OBJECTPROPS) /\ $heap_valid(H_returned)
S_c_unset = $sopn_after(S_returned, 4, 2048)[.COMPLETION = NORMAL]
$sopn_stage(S_c_unset, 4)
$propref_at(S_c_unset.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d])})
$objectprops_record_at(S_c_unset.OBJECTPROPS, n_owner) = (pobjectprops_c_unset)
$property_slot_at(pobjectprops_c_unset.SLOTS, $ptascii("c")) = ({DECL (ppropertyid_c), NAME ($ptascii("c")), STATE PROP_UNSET})
$node_children(S_c_unset, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf]
(HOBJECT n_owner) <- $heap_prune($heap_graph(S_c_unset)).NODES
$named_reference_notice_array(S_c_unset, PARRAY n_copied)
H_c_unset = $heap_graph(S_c_unset)
$heap_owners(H_c_unset, HCELL n_leaf) = 4
$proprefs_valid(S_c_unset) /\ $propref_slots_covered(S_c_unset, S_c_unset.OBJECTPROPS) /\ $heap_valid(H_c_unset)
S_a_unset = $sopn_after(S_c_unset, 5, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_a_unset, 5)
$propref_at(S_a_unset.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d])})
$objectprops_record_at(S_a_unset.OBJECTPROPS, n_owner) = (pobjectprops_a_unset)
$property_slot_at(pobjectprops_a_unset.SLOTS, $ptascii("a")) = ({DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_UNSET})
$node_children(S_a_unset, HOBJECT n_owner) = [HCELL n_leaf]
(HOBJECT n_owner) <- $heap_prune($heap_graph(S_a_unset)).NODES
$named_reference_notice_array(S_a_unset, PARRAY n_copied)
H_a_unset = $heap_graph(S_a_unset)
$heap_owners(H_a_unset, HCELL n_leaf) = 3
$proprefs_valid(S_a_unset) /\ $propref_slots_covered(S_a_unset, S_a_unset.OBJECTPROPS) /\ $heap_valid(H_a_unset)
S_final = $sopn_after(S_a_unset, 6, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_final, 6)
$propref_at(S_final.PROPREFS, n_leaf) = eps
$propref_at(S_final.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d])})
$node_children(S_final, HOBJECT n_owner) = [HCELL n_new_cv]
S_final.STORE[n_leaf] = S_pre.STORE[n_leaf]
$named_reference_notice_array(S_final, PARRAY n_copied)
$named_reference_notice_object_property_source(S_final, n_new_cv)
H_final = $heap_graph(S_final)
$heap_owners(H_final, HCELL n_leaf) = 2 /\ $heap_owners(H_final, HCELL n_new_cv) = 2
$proprefs_valid(S_final) /\ $propref_slots_covered(S_final, S_final.OBJECTPROPS) /\ $heap_valid(H_final)
S_singleton = $sopn_after(S_final, 7, 2048)[.COMPLETION = NORMAL]
$sopn_stage(S_singleton, 7)
S_singleton.STORE[n_leaf] = DEFINED (POBJECT n_old)
$propref_at(S_singleton.PROPREFS, n_leaf) = eps
~((HARRAY n_root) <- S_singleton.ALLOCATIONS)
H_singleton = $heap_graph(S_singleton)
$heap_owners(H_singleton, HCELL n_leaf) = 1 /\ $heap_owners(H_singleton, HOBJECT n_old) = 2
$duplicate_item(S_singleton, n_copied, ALIAS n_leaf) = DIRECT (POBJECT n_old)
S_copied = $sopn_after(S_singleton, 8, 1024)[.COMPLETION = NORMAL]
$sopn_stage(S_copied, 8)
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
S_dead_owner = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("holder"))]
$propref_source_valid(S_dead_owner, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_dead_owner)).NODES
~((HOBJECT n_owner) <- $heap_prune($heap_graph(S_dead_owner)).NODES)
~$named_reference_notice_array(S_dead_owner, PARRAY n_root)
S_duplicate = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c])}]]
~$named_reference_notice_array(S_duplicate, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_mixed = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid_c])}]]
~$named_reference_notice_array(S_mixed, PARRAY n_root)
S_missing = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d])}]]
$proprefs_valid(S_missing) /\ ~$propref_slots_covered(S_missing, S_missing.OBJECTPROPS)
~$named_reference_notice_array(S_missing, PARRAY n_root)
S_extra_slot = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, pobjectprops_owner.SLOTS ++ [{DECL (ppropertyid_c), NAME ($ptascii("c")), STATE PROP_VALUE (ALIAS n_leaf)}])]
~$named_reference_notice_array(S_extra_slot, PARRAY n_root)
S_short = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, [pobjectprops_owner.SLOTS[0], pobjectprops_owner.SLOTS[1], pobjectprops_owner.SLOTS[2]])]
~$named_reference_notice_array(S_short, PARRAY n_root)
S_inactive = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, OBJECT_PROP_SOURCE n_owner ($ptascii("c")) ppropertyid_c])}]][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("d"), PROP_INITIAL))]
$proprefs_valid(S_inactive) /\ $propref_slots_covered(S_inactive, S_inactive.OBJECTPROPS)
$node_children(S_inactive, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
$named_reference_notice_array(S_inactive, PARRAY n_root)
S_unset = S_inactive[.OBJECTPROPS = $objectprops_set(S_inactive.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("d"), PROP_UNSET))]
$named_reference_notice_array(S_unset, PARRAY n_root)
S_direct = S_inactive[.OBJECTPROPS = $objectprops_set(S_inactive.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("d"), PROP_VALUE (DIRECT (POBJECT n_new))))]
$proprefs_valid(S_direct) /\ $propref_slots_covered(S_direct, S_direct.OBJECTPROPS)
$named_reference_notice_array(S_direct, PARRAY n_root)
S_other_cell = S_inactive[.PROPREFS = S_inactive.PROPREFS ++ [{CELL n_new_cv, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d])}]][.REFCELLS = S_inactive.REFCELLS ++ [n_new_cv]][.OBJECTPROPS = $objectprops_set(S_inactive.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("d"), PROP_VALUE (ALIAS n_new_cv)))]
$propref_source_valid(S_other_cell, n_new_cv, OBJECT_PROP_SOURCE n_owner ($ptascii("d")) ppropertyid_d)
$proprefs_valid(S_other_cell) /\ $propref_slots_covered(S_other_cell, S_other_cell.OBJECTPROPS)
~$named_reference_notice_array(S_other_cell, PARRAY n_root)
S_nullable = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.TYPE = [(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
$proprefs_valid(S_nullable) /\ $propref_slots_covered(S_nullable, S_nullable.OBJECTPROPS)
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_protected = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.VISIBILITY = PROPERTY_PROTECTED]]]]]
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_default = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.DEFAULT = PROP_LITERAL (POBJECT n_old)]]]]]
~$named_reference_notice_array(S_default, PARRAY n_root)
S_setter = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.SETVISIBILITY = (PROPERTY_PRIVATE)]]]]]
~$named_reference_notice_array(S_setter, PARRAY n_root)
S_readonly = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.READONLY = true]]]]]
~$named_reference_notice_array(S_readonly, PARRAY n_root)
S_final_property = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.FINAL = true]]]]]
~$named_reference_notice_array(S_final_property, PARRAY n_root)
S_static = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.STATIC = true]]]]]
~$named_reference_notice_array(S_static, PARRAY n_root)
S_wrong_key = S_inactive[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d[.NAME = ($ptascii("other"))]]]]]
~$named_reference_notice_array(S_wrong_key, PARRAY n_root)
S_source_unit = S_pre[.NATIVEEXCESS = [HOBJECT n_owner]]
~$named_reference_notice_array(S_source_unit, PARRAY n_root)
S_called = S_pre[.DESTRUCTION.CALLED = [n_owner]]
~$named_reference_notice_array(S_called, PARRAY n_root)
pinstancestorage_source = {OBJECT n_owner, HANDLE 0, SLOTS pobjectprops_owner.SLOTS, NEXT 0, NOTIFY eps, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, USER false}
S_freeing = S_pre[.TODO = [INSTANCE_STORAGE_STEP pinstancestorage_source]]
$instance_storage_freeing(S_freeing, n_owner)
~$named_reference_notice_array(S_freeing, PARRAY n_root)
S_table = S_pre[.OBJECTTABLES = [{OBJECT n_owner, TABLE n_root}]]
~$named_reference_notice_array(S_table, PARRAY n_root)
S_materialized = $objectprops_mark(S_pre, n_owner)
~$named_reference_notice_array(S_materialized, PARRAY n_root)
S_parent = S_pre[.CLASSES = [pclassdesc[.PARENT = ($ptascii("Unknown"))]]]
~$named_reference_notice_array(S_parent, PARRAY n_root)
S_owning = S_pre[.STORE[n_leaf] = DEFINED (POBJECT n_new)][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_new, [{DECL eps, NAME ($ptascii("v")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}])]
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
    catalogue = Path(__file__).with_name('same_owner_property_alias_stdclass_reference_notice_review_cases.json')
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
