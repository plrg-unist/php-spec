#!/usr/bin/env python3
"""Check genuine mixed instance/static property-source Notice composition."""
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
dec $mpn_output(pevent*) : ptbytes
def $mpn_output(eps) = eps
def $mpn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mpn_output(pevent*)
dec $mpn_ready(pstate) : bool
def $mpn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $mpn_output(S.EVENTS) = $ptascii("P;")
def $mpn_ready(S) = false -- otherwise
dec $mpn_seek(pstate, nat) : pstate
def $mpn_seek(S, n) = S
  -- if $mpn_ready(S) \/ n = 0 \/ S.TODO = eps
def $mpn_seek(S, n) = $mpn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$mpn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mpn_seek(S, n) = S -- otherwise

dec $mpn_stage(pstate, nat) : bool
def $mpn_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;")
def $mpn_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;")
def $mpn_stage(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;")
def $mpn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;E;H;F;")
def $mpn_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewStaticOne18::$p of type stdClass;X;")
def $mpn_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewStaticOne18::$p of type stdClass;X;U:Cannot assign int to reference held by property ReviewOwner18::$b of type stdClass;B;")
def $mpn_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewStaticOne18::$p of type stdClass;X;U:Cannot assign int to reference held by property ReviewOwner18::$b of type stdClass;B;V:Cannot assign int to reference held by property ReviewStaticTwo18::$p of type stdClass;Z;")
def $mpn_stage(S, 7) = true
  -- if S.CURRENT = eps
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewStaticOne18::$p of type stdClass;X;U:Cannot assign int to reference held by property ReviewOwner18::$b of type stdClass;B;V:Cannot assign int to reference held by property ReviewStaticTwo18::$p of type stdClass;Z;41:41;N;Q;")
def $mpn_stage(S, 8) = true
  -- if S.CURRENT = eps
  -- if $mpn_output(S.EVENTS) = $ptascii("P;S;A;E;H;F;1:1:1:1:1;T:Cannot assign int to reference held by property ReviewStaticOne18::$p of type stdClass;X;U:Cannot assign int to reference held by property ReviewOwner18::$b of type stdClass;B;V:Cannot assign int to reference held by property ReviewStaticTwo18::$p of type stdClass;Z;41:41;N;Q;K;")
def $mpn_stage(S, n) = false -- otherwise
dec $mpn_after(pstate, nat, nat) : pstate
def $mpn_after(S, n_stage, n) = S
  -- if $mpn_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mpn_after(S, n_stage, n) = $mpn_after($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mpn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mpn_after(S, n_stage, n) = $mpn_after($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$mpn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $mpn_after(S, n_stage, n) = S -- otherwise
'''

REACHED = r'''

S_pre = $mpn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$mpn_ready(S_pre)
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
S_pre.OBJECTS[n_owner] = INSTANCE porigin_owner
$class_at(S_pre.CLASSES, porigin_owner) = (pclassdesc_owner)
pclassdesc_owner.PROPERTIES = [ppropertydesc_a, ppropertydesc_b]
ppropertydesc_a.ORIGIN = ppropertyid_a
ppropertydesc_b.ORIGIN = ppropertyid_b
$class_named(S_pre.CLASSNAMES, $ptascii("reviewstaticone18")) = (porigin_one)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewstatictwo18")) = (porigin_two)
$class_at(S_pre.CLASSES, porigin_one) = (pclassdesc_one)
$class_at(S_pre.CLASSES, porigin_two) = (pclassdesc_two)
pclassdesc_one.PROPERTIES = [ppropertydesc_one]
pclassdesc_two.PROPERTIES = [ppropertydesc_two]
ppropertydesc_one.ORIGIN = ppropertyid_one
ppropertydesc_two.ORIGIN = ppropertyid_two
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, CLASS_PROP_SOURCE ppropertyid_one, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_two]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_one)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_two)
$objectprops_record_at(S_pre.OBJECTPROPS, n_owner) = (pobjectprops_owner)
pobjectprops_owner.SLOTS = [{DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_b), NAME ($ptascii("b")), STATE PROP_VALUE (ALIAS n_leaf)}]
~pobjectprops_owner.MATERIALIZED /\ $objectprops_valid(S_pre, [pobjectprops_owner])
$node_children(S_pre, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf]
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_one) = ({DECL ppropertyid_one, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_two) = ({DECL ppropertyid_two, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf]
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a])
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b])
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b])
$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_one])
$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_two])
$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_two, CLASS_PROP_SOURCE ppropertyid_one])
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
$class_statics_valid(S_pre) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS)
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''

~$named_reference_notice_object_property_source(S_pre, n_leaf)
~$named_reference_notice_object_static_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
'''.strip().splitlines()

ADMITTED = r'''

S_pre.CLASSES = [pclassdesc_owner, pclassdesc_one, pclassdesc_two]
~$named_reference_notice_object_property_source(S_pre, n_leaf)
~$named_reference_notice_object_static_source(S_pre, n_leaf)
$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
$named_reference_notice_object_source(S_pre, n_leaf)
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
S_same = $mpn_after(S_notice, 0, 1024)[.COMPLETION = NORMAL]
$mpn_stage(S_same, 0)
S_same.OBJECTPROPS = S_pre.OBJECTPROPS /\ S_same.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_same.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, CLASS_PROP_SOURCE ppropertyid_two, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_one])})
$proprefs_valid(S_same) /\ $propref_slots_covered(S_same, S_same.OBJECTPROPS) /\ $class_statics_valid(S_same)
S_partial = $mpn_after(S_same, 1, 768)[.COMPLETION = NORMAL]
$mpn_stage(S_partial, 1)
$propref_at(S_partial.PROPREFS, n_leaf) = (ppropref_partial)
ppropref_partial.SOURCES = [CLASS_PROP_SOURCE ppropertyid_one, CLASS_PROP_SOURCE ppropertyid_two, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b]
$objectprops_record_at(S_partial.OBJECTPROPS, n_owner) = (pobjectprops_partial)
pobjectprops_partial.SLOTS = [{DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_UNSET}, {DECL (ppropertyid_b), NAME ($ptascii("b")), STATE PROP_VALUE (ALIAS n_leaf)}]
$node_children(S_partial, HOBJECT n_owner) = [HCELL n_leaf]
S_partial.CLASSSTATICS = S_pre.CLASSSTATICS
$named_reference_notice_array(S_partial, PARRAY n_root)
$proprefs_valid(S_partial) /\ $propref_slots_covered(S_partial, S_partial.OBJECTPROPS) /\ $class_statics_valid(S_partial)
S_failed = $mpn_after(S_partial, 2, 768)
$mpn_stage(S_failed, 2)
S_failed.PROPREFS = S_partial.PROPREFS /\ S_failed.CLASSSTATICS = S_partial.CLASSSTATICS
$objectprops_record_at(S_failed.OBJECTPROPS, n_owner) = (pobjectprops_partial)
S_failed.STORE[n_leaf] = S_pre.STORE[n_leaf] /\ S_failed.STORE[n_bad_cv] = S_pre.STORE[n_bad_cv]
$propref_at(S_failed.PROPREFS, n_bad_cv) = eps
$proprefs_valid(S_failed) /\ $class_statics_valid(S_failed)
S_returned = $mpn_after(S_failed, 3, 1536)[.COMPLETION = NORMAL]
$mpn_stage(S_returned, 3)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.PROPREFS = S_partial.PROPREFS /\ S_returned.CLASSSTATICS = S_partial.CLASSSTATICS
$node_children(S_returned, HOBJECT n_owner) = [HCELL n_leaf]
H_returned = $heap_graph(S_returned)
H_returned = $heap_graph(S_returned[.PROPREFS = eps])
$heap_owners(H_returned, HCELL n_leaf) = 5
$heap_owners(H_returned, HARRAY n_root) = 2 /\ $heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HOBJECT n_owner) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2 /\ $heap_owners(H_returned, HOBJECT n_new) = 1
$duplicate_item(S_returned, n_copied, ALIAS n_leaf) = ALIAS n_leaf
$proprefs_valid(S_returned) /\ $propref_slots_covered(S_returned, S_returned.OBJECTPROPS) /\ $class_statics_valid(S_returned) /\ $heap_valid(H_returned)
S_first = $mpn_after(S_returned, 4, 2048)[.COMPLETION = NORMAL]
$mpn_stage(S_first, 4)
$propref_at(S_first.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_two])})
$propref_at(S_first.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_one])})
$class_static_roots(S_first.CLASSSTATICS) = [HCELL n_new_cv, HCELL n_leaf]
S_first.STORE[n_leaf] = DEFINED (POBJECT n_old) /\ S_first.STORE[n_new_cv] = DEFINED (POBJECT n_new)
H_first = $heap_graph(S_first)
$heap_owners(H_first, HCELL n_leaf) = 4 /\ $heap_owners(H_first, HCELL n_new_cv) = 2
$named_reference_notice_array(S_first, PARRAY n_copied)
$proprefs_valid(S_first) /\ $class_statics_valid(S_first) /\ $heap_valid(H_first)
S_b_unset = $mpn_after(S_first, 5, 2048)[.COMPLETION = NORMAL]
$mpn_stage(S_b_unset, 5)
$propref_at(S_b_unset.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_two])})
$objectprops_record_at(S_b_unset.OBJECTPROPS, n_owner) = (pobjectprops_unset)
pobjectprops_unset.SLOTS = [{DECL (ppropertyid_a), NAME ($ptascii("a")), STATE PROP_UNSET}, {DECL (ppropertyid_b), NAME ($ptascii("b")), STATE PROP_UNSET}]
$node_children(S_b_unset, HOBJECT n_owner) = eps
$class_static_roots(S_b_unset.CLASSSTATICS) = [HCELL n_new_cv, HCELL n_leaf]
H_b_unset = $heap_graph(S_b_unset)
$heap_owners(H_b_unset, HCELL n_leaf) = 3 /\ $heap_owners(H_b_unset, HCELL n_new_cv) = 2
$named_reference_notice_object_static_source(S_b_unset, n_leaf) /\ $named_reference_notice_array(S_b_unset, PARRAY n_copied)
$proprefs_valid(S_b_unset) /\ $propref_slots_covered(S_b_unset, S_b_unset.OBJECTPROPS) /\ $class_statics_valid(S_b_unset) /\ $heap_valid(H_b_unset)
S_final = $mpn_after(S_b_unset, 6, 2048)[.COMPLETION = NORMAL]
$mpn_stage(S_final, 6)
$propref_at(S_final.PROPREFS, n_leaf) = eps
$propref_at(S_final.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_one, CLASS_PROP_SOURCE ppropertyid_two])})
$class_static_roots(S_final.CLASSSTATICS) = [HCELL n_new_cv, HCELL n_new_cv]
$node_children(S_final, HOBJECT n_owner) = eps
$named_reference_notice_array(S_final, PARRAY n_copied) /\ $named_reference_notice_object_source(S_final, n_new_cv)
H_final = $heap_graph(S_final)
H_final = $heap_graph(S_final[.PROPREFS = eps])
$heap_owners(H_final, HCELL n_leaf) = 2 /\ $heap_owners(H_final, HCELL n_new_cv) = 3
$heap_owners(H_final, HOBJECT n_owner) = 1
$proprefs_valid(S_final) /\ $class_statics_valid(S_final) /\ $heap_valid(H_final)
S_singleton = $mpn_after(S_final, 7, 2048)[.COMPLETION = NORMAL]
$mpn_stage(S_singleton, 7)
S_singleton.STORE[n_leaf] = DEFINED (POBJECT n_old)
$propref_at(S_singleton.PROPREFS, n_leaf) = eps
~((HARRAY n_root) <- S_singleton.ALLOCATIONS)
H_singleton = $heap_graph(S_singleton)
$heap_owners(H_singleton, HCELL n_leaf) = 1 /\ $heap_owners(H_singleton, HOBJECT n_old) = 2
$duplicate_item(S_singleton, n_copied, ALIAS n_leaf) = DIRECT (POBJECT n_old)
S_copied = $mpn_after(S_singleton, 8, 1024)[.COMPLETION = NORMAL]
$mpn_stage(S_copied, 8)
$lookup(S_copied.ENV, $ptascii("snapshot")) = (n_snapshot_cv)
S_copied.STORE[n_snapshot_cv] = DEFINED (PARRAY n_snapshot)
n_snapshot =/= n_copied
S_copied.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_copied.ARRAYS[n_snapshot].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 13))]
$node_children(S_copied, HARRAY n_copied) = [HCELL n_leaf]
$node_children(S_copied, HARRAY n_snapshot) = [HOBJECT n_old]
H_copied = $heap_graph(S_copied)
$heap_owners(H_copied, HCELL n_leaf) = 1 /\ $heap_owners(H_copied, HOBJECT n_old) = 3
$proprefs_valid(S_copied) /\ $propref_slots_covered(S_copied, S_copied.OBJECTPROPS) /\ $class_statics_valid(S_copied) /\ $heap_valid(H_copied)
S_zero = $drive(S_copied, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_copied
$drive($drive(S_copied, 1)[.COMPLETION = NORMAL], 1) = $drive(S_copied, 2)
'''.strip().splitlines()

SOURCES = r'''

S_permuted = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_two, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_one, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a])}]]
$proprefs_valid(S_permuted) /\ $propref_slots_covered(S_permuted, S_permuted.OBJECTPROPS) /\ $class_statics_valid(S_permuted)
$named_reference_notice_object_source(S_permuted, n_leaf) /\ $named_reference_notice_array(S_permuted, PARRAY n_root)
S_duplicate_object = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a])}]]
~$named_reference_notice_array(S_duplicate_object, PARRAY n_root)
S_duplicate_static = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid_two])}]]
~$named_reference_notice_array(S_duplicate_static, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_retired = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [RETIRED_CLASS_PROP_SOURCE ppropertyid_one 0])}]]
~$named_reference_notice_array(S_retired, PARRAY n_root)
S_dead = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("holder"))]
$propref_source_valid(S_dead, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_dead)).NODES
~((HOBJECT n_owner) <- $heap_prune($heap_graph(S_dead)).NODES)
~$named_reference_notice_array(S_dead, PARRAY n_root)
S_missing_object = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("a")) ppropertyid_a, CLASS_PROP_SOURCE ppropertyid_one, CLASS_PROP_SOURCE ppropertyid_two])}]]
$proprefs_valid(S_missing_object) /\ ~$propref_slots_covered(S_missing_object, S_missing_object.OBJECTPROPS)
~$named_reference_notice_array(S_missing_object, PARRAY n_root)
S_direct_object = S_missing_object[.OBJECTPROPS = $objectprops_set(S_missing_object.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("b"), PROP_VALUE (DIRECT (POBJECT n_old))))]
$proprefs_valid(S_direct_object) /\ $propref_slots_covered(S_direct_object, S_direct_object.OBJECTPROPS)
~$named_reference_notice_array(S_direct_object, PARRAY n_root)
S_wrong_static = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_two, PROP_VALUE (ALIAS n_new_cv))]
~$named_reference_notice_array(S_wrong_static, PARRAY n_root)
S_direct_static = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_two, PROP_VALUE (DIRECT (POBJECT n_old)))]
~$named_reference_notice_array(S_direct_static, PARRAY n_root)
S_initial_static = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_two, PROP_INITIAL)]
~$named_reference_notice_array(S_initial_static, PARRAY n_root)
S_no_rows = S_pre[.CLASSSTATICS = eps]
~$named_reference_notice_array(S_no_rows, PARRAY n_root)
S_nullable_static = S_pre[.CLASSES = [pclassdesc_owner, pclassdesc_one, pclassdesc_two[.PROPERTIES = [ppropertydesc_two[.TYPE = [(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
$propref_source_valid(S_nullable_static, n_leaf, CLASS_PROP_SOURCE ppropertyid_two)
~$named_reference_notice_array(S_nullable_static, PARRAY n_root)
S_protected_static = S_pre[.CLASSES = [pclassdesc_owner, pclassdesc_one, pclassdesc_two[.PROPERTIES = [ppropertydesc_two[.VISIBILITY = PROPERTY_PROTECTED]]]]]
$propref_source_valid(S_protected_static, n_leaf, CLASS_PROP_SOURCE ppropertyid_two)
~$named_reference_notice_array(S_protected_static, PARRAY n_root)
S_nullable_object = S_pre[.CLASSES = [pclassdesc_owner[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b[.TYPE = [(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "null"]))]]]], pclassdesc_one, pclassdesc_two]]
$propref_source_valid(S_nullable_object, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("b")) ppropertyid_b)
~$named_reference_notice_array(S_nullable_object, PARRAY n_root)
S_cell_unit = S_pre[.NATIVEEXCESS = [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_unit, PARRAY n_root)
S_root_unit = S_pre[.NATIVEEXCESS = [HARRAY n_root]]
~$named_reference_notice_array(S_root_unit, PARRAY n_root)
S_payload = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("v")), STATE PROP_VALUE (DIRECT (POBJECT n_new))}])]
~$named_reference_notice_array(S_payload, PARRAY n_root)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--part', choices=('ingress', 'post'), default='post')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('mixed_property_alias_stdclass_reference_notice_review_cases.json')
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
    reached = REACHED + ([] if args.part == 'ingress' else ADMITTED + OWNERSHIP)
    derived = INGRESS if args.part == 'ingress' else SOURCES
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
