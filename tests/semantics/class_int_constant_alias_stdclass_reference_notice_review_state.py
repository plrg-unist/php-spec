#!/usr/bin/env python3
"""Ground own grouped integer constants at a genuine mixed-source Notice fence."""
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
  -- if $sopn_output(S.EVENTS) = $ptascii("A:13:19;")
def $sopn_ready(S) = false -- otherwise
dec $sopn_seek(pstate, nat) : pstate
def $sopn_seek(S, n) = S
  -- if $sopn_ready(S) \/ n = 0 \/ S.TODO = eps
def $sopn_seek(S, n) = $sopn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$sopn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $sopn_seek(S, n) = S -- otherwise



dec $sopn_stage(pstate, nat) : bool
def $sopn_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $sopn_output(S.EVENTS) = $ptascii("A:13:19;S;")
def $sopn_stage(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $sopn_output(S.EVENTS) = $ptascii("A:13:19;S;")
def $sopn_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $sopn_output(S.EVENTS) = $ptascii("A:13:19;S;E;H;F;")
def $sopn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A:13:19;S;E;H;F;1:1:1:1:5;1;T:Cannot assign int to reference held by property ReviewMixedConstant28::$s of type stdClass;C;")
def $sopn_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A:13:19;S;E;H;F;1:1:1:1:5;1;T:Cannot assign int to reference held by property ReviewMixedConstant28::$s of type stdClass;C;U:Cannot assign int to reference held by property ReviewMixedConstant28::$p of type stdClass;P;")
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

;; Forged occurrence controls remain helper-only and grant no source credit.
dec $cint_replace(pcoccurrence*, pcpath, pcnode?) : pcoccurrence*
def $cint_replace(eps, pcpath, pcnode_replacement?) = eps
def $cint_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, (pcnode_new)) = (PCOCCURRENCE pcpath pcnode_new) :: pcoccurrence*
def $cint_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, eps) = pcoccurrence*
def $cint_replace((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath, pcnode_replacement?) = (PCOCCURRENCE pcpath_other pcnode) :: $cint_replace(pcoccurrence*, pcpath, pcnode_replacement?)
  -- if pcpath_other =/= pcpath
dec $cint_raw(pstate, pcpath, pcnode?) : pstate
def $cint_raw(S, pcpath, pcnode_replacement?) = S[.SOURCES = [pcunit[.OCCURRENCES = $cint_replace(pcunit.OCCURRENCES, pcpath, pcnode_replacement?)]]]
  -- if S.SOURCES = [pcunit]

'''

REACHED = r'''
S_pre = $sopn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$sopn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("owner")) = (n_owner_cv)
$lookup(S_pre.ENV, $ptascii("old")) = eps
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.STORE[n_owner_cv] = DEFINED (POBJECT n_owner)
S_pre.OBJECTS[n_owner] = INSTANCE porigin_owner
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_owner
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps
pclassdesc.CONSTANTS = [pclassconstantdesc_k, pclassconstantdesc_l]
porigin_owner = PORIGIN n_source pcpath_owner
$origin_node(S_pre.SOURCES, porigin_owner) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_class) metadata_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_constants, statement_properties, statement_static])) metadata_class)
$base64(text_class) = pclassdesc.NAME
statement_constants = NStmtClassConst (SEQUENCE eps) (INTEGER 1) ABSENT (SEQUENCE ([phpType46_k, phpType46_l])) metadata_group
pcpath_group = pcpath_owner ++ [PCFIELD 5, PCINDEX 0]
$origin_node(S_pre.SOURCES, PORIGIN n_source pcpath_group) = (statement_constants)
phpType46_k = NConst (NIdentifier (BYTES text_k) metadata_k_name) (NScalarInt (INTEGER 13) metadata_k_value) metadata_k
$base64(text_k) = $ptascii("K")
pclassconstantdesc_k.OWNER = porigin_owner /\ pclassconstantdesc_k.OWNERNAME = pclassdesc.NAME
pclassconstantdesc_k.NAME = $ptascii("K") /\ pclassconstantdesc_k.VISIBILITY = PROPERTY_PUBLIC
~pclassconstantdesc_k.FINAL /\ pclassconstantdesc_k.TYPE = eps /\ pclassconstantdesc_k.FOLDED
pclassconstantdesc_k.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 0])
$origin_node(S_pre.SOURCES, pclassconstantdesc_k.ORIGIN) = (phpType46_k)
pclassconstantdesc_k.INITIALIZER = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 0, PCFIELD 1])
$origin_node(S_pre.SOURCES, pclassconstantdesc_k.INITIALIZER) = (NScalarInt (INTEGER 13) metadata_k_value)
$pool_value(S_pre.POOLS, pclassconstantdesc_k.INITIALIZER) = (PINT 13)
$pool_class(S_pre.POOLS, pclassconstantdesc_k.INITIALIZER) = (PVSCALAR)
phpType46_l = NConst (NIdentifier (BYTES text_l) metadata_l_name) (NScalarInt (INTEGER 19) metadata_l_value) metadata_l
$base64(text_l) = $ptascii("L")
pclassconstantdesc_l.OWNER = porigin_owner /\ pclassconstantdesc_l.OWNERNAME = pclassdesc.NAME
pclassconstantdesc_l.NAME = $ptascii("L") /\ pclassconstantdesc_l.VISIBILITY = PROPERTY_PUBLIC
~pclassconstantdesc_l.FINAL /\ pclassconstantdesc_l.TYPE = eps /\ pclassconstantdesc_l.FOLDED
pclassconstantdesc_l.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 1])
$origin_node(S_pre.SOURCES, pclassconstantdesc_l.ORIGIN) = (phpType46_l)
pclassconstantdesc_l.INITIALIZER = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 1, PCFIELD 1])
$origin_node(S_pre.SOURCES, pclassconstantdesc_l.INITIALIZER) = (NScalarInt (INTEGER 19) metadata_l_value)
$pool_value(S_pre.POOLS, pclassconstantdesc_l.INITIALIZER) = (PINT 19)
$pool_class(S_pre.POOLS, pclassconstantdesc_l.INITIALIZER) = (PVSCALAR)
pclassdesc.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q, ppropertydesc_s]
ppropertydesc_r.ORIGIN = ppropertyid_r
ppropertydesc_p.ORIGIN = ppropertyid_p
ppropertydesc_q.ORIGIN = ppropertyid_q
ppropertydesc_s.ORIGIN = ppropertyid_s
$property_declaring_class(S_pre.CLASSES, ppropertyid_r) = (porigin_owner)
$property_declaring_class(S_pre.CLASSES, ppropertyid_q) = (porigin_owner)
(INSTANCE porigin_owner) <- S_pre.OBJECTS
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p, CLASS_PROP_SOURCE ppropertyid_s]
$propref_unique_sources(ppropref.SOURCES)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_s) = (ppropertydesc_s)
S_pre.CLASSSTATICS = [{DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)}]
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_s) = ({DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf]
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$objectprops_record_at(S_pre.OBJECTPROPS, n_owner) = (pobjectprops_owner)
pobjectprops_owner.SLOTS = [{DECL (ppropertyid_r), NAME ($ptascii("r")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}, {DECL (ppropertyid_p), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_q), NAME ($ptascii("q")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}]
~pobjectprops_owner.MATERIALIZED /\ $objectprops_valid(S_pre, [pobjectprops_owner])
$object_table_at(S_pre.OBJECTTABLES, n_owner) = eps
$node_children(S_pre, HOBJECT n_owner) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object(S_pre, POBJECT n_new)
$named_reference_notice_object_ancestors(S_pre, [n_root])
~$instance_storage_freeing(S_pre, n_owner) /\ ~(n_owner <- S_pre.DESTRUCTION.CALLED)
~$propref_source_queued(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$heap_count(HOBJECT n_owner, S_pre.NATIVEEXCESS) = 0 /\ ~$weakmap_key_waiting(S_pre, n_owner)
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
$reference_coercion_at(S_pre.REFCOERCIONS, n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf) /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HCELL n_leaf) = 4 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_owner) = 1
$heap_owners(H_pre, HOBJECT n_old) = 3 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_owner) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
$named_reference_notice_object_property_slots(S_pre, n_leaf, n_owner, pclassdesc.PROPERTIES, pobjectprops_owner.SLOTS) = ([HOBJECT n_old, HCELL n_leaf, HOBJECT n_old])
$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_s])
$class_statics_valid(S_pre)
'''.strip().splitlines()

PROTOCOL = r'''
~$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_p, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_without_constants = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = eps]]]
H_pre = $heap_graph(S_without_constants)
$named_reference_notice_object_property_sources(S_without_constants, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
$named_reference_notice_object_static_sources(S_without_constants, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
$named_reference_notice_array(S_without_constants, PARRAY n_root)
'''.strip().splitlines()

POST = r'''
$named_reference_notice_class_constants(S_pre, pclassdesc, pclassdesc.CONSTANTS)
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_p, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_r, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
S_one_step = $drive(S_pre, 1)
S_one_step.COMPLETION = BUDGET
S_notice = S_one_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_private)]
$error_call_valid(S_notice, perrorcall)
S_swapped = $sopn_after(S_notice, 0, 768)[.COMPLETION = NORMAL]
$sopn_stage(S_swapped, 0)
S_swapped.STORE[n_leaf] = DEFINED (POBJECT n_new)
S_swapped.OBJECTPROPS = S_pre.OBJECTPROPS
$propref_at(S_swapped.PROPREFS, n_leaf) = (ppropref_swapped)
ppropref_swapped.SOURCES = [CLASS_PROP_SOURCE ppropertyid_s, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p]
$node_children(S_swapped, HOBJECT n_owner) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$node_children(S_swapped, HCELL n_leaf) = [HOBJECT n_new]
$class_static_roots(S_swapped.CLASSSTATICS) = [HCELL n_leaf]
H_swapped = $heap_graph(S_swapped)
H_swapped = $heap_graph(S_swapped[.PROPREFS = eps])
$heap_owners(H_swapped, HOBJECT n_old) = 2 /\ $heap_owners(H_swapped, HOBJECT n_new) = 2
$proprefs_valid(S_swapped) /\ $propref_slots_covered(S_swapped, S_swapped.OBJECTPROPS) /\ $class_statics_valid(S_swapped)
S_failed = $sopn_after(S_swapped, 1, 768)
$sopn_stage(S_failed, 1)
S_failed.PROPREFS = S_swapped.PROPREFS
$objectprops_record_at(S_failed.OBJECTPROPS, n_owner) = (pobjectprops_owner)
S_failed.CLASSSTATICS = S_pre.CLASSSTATICS
S_failed.STORE[n_leaf] = DEFINED (POBJECT n_new) /\ S_failed.STORE[n_bad_cv] = DEFINED (PINT 17)
$propref_at(S_failed.PROPREFS, n_bad_cv) = eps
S_returned = $sopn_after(S_failed, 2, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.PROPREFS = S_swapped.PROPREFS
$node_children(S_returned, HOBJECT n_owner) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$class_static_roots(S_returned.CLASSSTATICS) = [HCELL n_leaf]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_leaf) = 4
$heap_owners(H_returned, HARRAY n_root) = 2 /\ $heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2 /\ $heap_owners(H_returned, HOBJECT n_new) = 2
$duplicate_item(S_returned, n_copied, ALIAS n_leaf) = ALIAS n_leaf
$named_reference_notice_array(S_returned, PARRAY n_copied)
S_partial = $sopn_after(S_returned, 3, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_partial, 3)
$propref_at(S_partial.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])})
$propref_at(S_partial.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s])})
$class_static_at(S_partial.CLASSSTATICS, ppropertyid_s) = ({DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_new_cv)})
$class_static_roots(S_partial.CLASSSTATICS) = [HCELL n_new_cv]
$objectprops_record_at(S_partial.OBJECTPROPS, n_owner) = (pobjectprops_owner)
H_partial = $heap_graph(S_partial)
H_partial = $heap_graph(S_partial[.PROPREFS = eps])
$heap_owners(H_partial, HCELL n_leaf) = 3 /\ $heap_owners(H_partial, HCELL n_new_cv) = 2
$heap_owners(H_partial, HOBJECT n_old) = 2 /\ $heap_owners(H_partial, HOBJECT n_new) = 2
$proprefs_valid(S_partial) /\ $propref_slots_covered(S_partial, S_partial.OBJECTPROPS) /\ $class_statics_valid(S_partial)
S_final_transfer = $sopn_after(S_partial, 4, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_final_transfer, 4)
$propref_at(S_final_transfer.PROPREFS, n_leaf) = eps
$propref_at(S_final_transfer.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])})
$node_children(S_final_transfer, HOBJECT n_owner) = [HOBJECT n_old, HCELL n_new_cv, HOBJECT n_old]
$class_static_roots(S_final_transfer.CLASSSTATICS) = [HCELL n_new_cv]
H_final_transfer = $heap_graph(S_final_transfer)
H_final_transfer = $heap_graph(S_final_transfer[.PROPREFS = eps])
$heap_owners(H_final_transfer, HCELL n_leaf) = 2 /\ $heap_owners(H_final_transfer, HCELL n_new_cv) = 3
$heap_owners(H_final_transfer, HOBJECT n_old) = 2 /\ $heap_owners(H_final_transfer, HOBJECT n_new) = 2
$proprefs_valid(S_final_transfer) /\ $propref_slots_covered(S_final_transfer, S_final_transfer.OBJECTPROPS) /\ $class_statics_valid(S_final_transfer)
'''.strip().splitlines()

CONTROLS = r'''
S_distinct = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (DIRECT (POBJECT n_new))))]
$proprefs_valid(S_distinct) /\ $propref_slots_covered(S_distinct, S_distinct.OBJECTPROPS)
$named_reference_notice_object_property_slots(S_distinct, n_leaf, n_owner, pclassdesc.PROPERTIES, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (DIRECT (POBJECT n_new)))) = ([HOBJECT n_old, HCELL n_leaf, HOBJECT n_new])
$named_reference_notice_array(S_distinct, PARRAY n_root)
S_other_cell = S_pre[.PROPREFS = S_pre.PROPREFS ++ [{CELL n_new_cv, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q])}]][.REFCELLS = S_pre.REFCELLS ++ [n_new_cv]][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (ALIAS n_new_cv)))]
$propref_source_valid(S_other_cell, n_new_cv, OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q)
$proprefs_valid(S_other_cell) /\ $propref_slots_covered(S_other_cell, S_other_cell.OBJECTPROPS)
~$named_reference_notice_array(S_other_cell, PARRAY n_root)
S_stale = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q])}]]
~$propref_source_valid(S_stale, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q)
~$named_reference_notice_array(S_stale, PARRAY n_root)
S_dead = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("owner"))]
$propref_source_valid(S_dead, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~((HOBJECT n_owner) <- $heap_prune($heap_graph(S_dead)).NODES)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_dead)).NODES
~$named_reference_notice_array(S_dead, PARRAY n_root)
S_extra = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, pobjectprops_owner.SLOTS ++ [pobjectprops_owner.SLOTS[0]])]
~$named_reference_notice_array(S_extra, PARRAY n_root)
S_missing = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, [pobjectprops_owner.SLOTS[1], pobjectprops_owner.SLOTS[2]])]
~$named_reference_notice_array(S_missing, PARRAY n_root)
S_wrong_decl = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, [pobjectprops_owner.SLOTS[0][.DECL = (ppropertyid_q)], pobjectprops_owner.SLOTS[1], pobjectprops_owner.SLOTS[2]])]
~$named_reference_notice_array(S_wrong_decl, PARRAY n_root)
S_owning = S_distinct[.OBJECTPROPS = $objectprops_set(S_distinct.OBJECTPROPS, n_new, [{DECL eps, NAME ($ptascii("v")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}])]
$named_reference_notice_object(S_owning, POBJECT n_old) /\ ~$named_reference_notice_object(S_owning, POBJECT n_new)
~$named_reference_notice_array(S_owning, PARRAY n_root)
S_scalar = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (DIRECT (PINT 7))))]
~$named_reference_notice_array(S_scalar, PARRAY n_root)
S_user = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (DIRECT (POBJECT n_owner))))]
~$named_reference_notice_array(S_user, PARRAY n_root)
S_leaf_unit = S_distinct[.NATIVEEXCESS = [HOBJECT n_new]]
~$named_reference_notice_array(S_leaf_unit, PARRAY n_root)
S_owner_unit = S_pre[.NATIVEEXCESS = [HOBJECT n_owner]]
~$named_reference_notice_array(S_owner_unit, PARRAY n_root)
S_called = S_distinct[.DESTRUCTION.CALLED = [n_new]]
~$named_reference_notice_array(S_called, PARRAY n_root)
S_materialized = $objectprops_mark(S_pre, n_owner)
~$named_reference_notice_array(S_materialized, PARRAY n_root)
S_table = S_pre[.OBJECTTABLES = [{OBJECT n_owner, TABLE n_root}]]
~$named_reference_notice_array(S_table, PARRAY n_root)
S_default = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q[.DEFAULT = PROP_LITERAL (POBJECT n_old)], ppropertydesc_s]]]]
~$named_reference_notice_array(S_default, PARRAY n_root)
S_setter = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q[.SETVISIBILITY = (PROPERTY_PRIVATE)], ppropertydesc_s]]]]
~$named_reference_notice_array(S_setter, PARRAY n_root)
S_readonly = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q[.READONLY = true], ppropertydesc_s]]]]
~$named_reference_notice_array(S_readonly, PARRAY n_root)
S_final = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q[.FINAL = true], ppropertydesc_s]]]]
~$named_reference_notice_array(S_final, PARRAY n_root)
S_protected = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q[.VISIBILITY = PROPERTY_PROTECTED], ppropertydesc_s]]]]
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_no_source = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s])}]]
$propref_source_valid(S_no_source, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$propref_source_present(S_no_source.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_no_source, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_no_source, PARRAY n_root)
S_static_only = S_no_source[.OBJECTPROPS = $objectprops_set(S_no_source.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("p"), PROP_INITIAL))]
$proprefs_valid(S_static_only) /\ $propref_slots_covered(S_static_only, S_static_only.OBJECTPROPS) /\ $class_statics_valid(S_static_only)
$propref_source_valid(S_static_only, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
(INSTANCE porigin_owner) <- S_static_only.OBJECTS
~$named_reference_notice_object_property_owner_source(S_static_only, n_leaf, ppropertydesc_q, [CLASS_PROP_SOURCE ppropertyid_s])
~$named_reference_notice_array(S_static_only, PARRAY n_root)
S_static_direct = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])}]][.CLASSSTATICS = [{DECL ppropertyid_s, STATE PROP_VALUE (DIRECT (POBJECT n_old))}]]
$proprefs_valid(S_static_direct) /\ $propref_slots_covered(S_static_direct, S_static_direct.OBJECTPROPS) /\ $class_statics_valid(S_static_direct)
$class_static_roots(S_static_direct.CLASSSTATICS) = [HOBJECT n_old]
$named_reference_notice_object_static_properties(S_static_direct, n_leaf, [ppropertydesc_s])
$named_reference_notice_array(S_static_direct, PARRAY n_root)
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q[.KEY = $ptascii("missing")], OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q[.ORIGIN = ppropertyid_p], OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
S_owner = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.OWNER = pclassconstantdesc_l.INITIALIZER], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_owner, PARRAY n_root)
S_owner_name = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.OWNERNAME = $ptascii("Wrong")], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_owner_name, PARRAY n_root)
S_name = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.NAME = $ptascii("Wrong")], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_name, PARRAY n_root)
S_visibility = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.VISIBILITY = PROPERTY_PROTECTED], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_visibility, PARRAY n_root)
S_final_constant = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.FINAL = true], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_final_constant, PARRAY n_root)
S_typed_constant = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.TYPE = [(PTBRANCH ([PTINT]))]], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_typed_constant, PARRAY n_root)
S_unfolded = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.FOLDED = false], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_unfolded, PARRAY n_root)
S_initializer = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.INITIALIZER = pclassconstantdesc_l.INITIALIZER], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_initializer, PARRAY n_root)
S_wrong_index = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 2])], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_wrong_index, PARRAY n_root)
S_wrong_group = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k[.ORIGIN = PORIGIN n_source (pcpath_owner ++ [PCFIELD 5, PCINDEX 1, PCFIELD 3, PCINDEX 0])], pclassconstantdesc_l]]]]
~$named_reference_notice_array(S_wrong_group, PARRAY n_root)
S_missing_descriptor = S_pre[.CLASSES = [pclassdesc[.CONSTANTS = [pclassconstantdesc_k]]]]
~$named_reference_notice_class_constants(S_missing_descriptor, pclassdesc[.CONSTANTS = [pclassconstantdesc_k]], [pclassconstantdesc_k])
~$named_reference_notice_array(S_missing_descriptor, PARRAY n_root)
S_missing_group = $cint_raw(S_pre, pcpath_group, eps)
~$named_reference_notice_array(S_missing_group, PARRAY n_root)
S_missing_item = $cint_raw(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 1], eps)
~$named_reference_notice_array(S_missing_item, PARRAY n_root)
S_wrong_item = $cint_raw(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 1], (phpType46_k))
~$named_reference_notice_array(S_wrong_item, PARRAY n_root)
S_wrong_raw_initializer = $cint_raw(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 1, PCFIELD 1], (NScalarInt (INTEGER 23) metadata_l_value))
~$named_reference_notice_array(S_wrong_raw_initializer, PARRAY n_root)
S_wrong_raw_owner = $cint_raw(S_pre, pcpath_owner, (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "V3Jvbmc=") metadata_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_constants, statement_properties, statement_static])) metadata_class))
~$named_reference_notice_array(S_wrong_raw_owner, PARRAY n_root)
$pool_at(S_pre.POOLS, n_source) = (ppool)
S_no_pool = S_pre[.POOLS = eps]
~$named_reference_notice_array(S_no_pool, PARRAY n_root)
S_wrong_pool_value = S_pre[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_group ++ [PCFIELD 3, PCINDEX 0, PCFIELD 1]) (PINT 99)) :: ppool.CONSTANTS]]]
~$named_reference_notice_array(S_wrong_pool_value, PARRAY n_root)
S_wrong_pool_class = S_pre[.POOLS = [ppool[.CONSTANTS = (PCCLASS (pcpath_group ++ [PCFIELD 3, PCINDEX 0, PCFIELD 1]) PVOBJECT) :: ppool.CONSTANTS]]]
~$named_reference_notice_array(S_wrong_pool_class, PARRAY n_root)
$named_reference_notice_class_constants(S_pre, pclassdesc, eps)
statement_default_public = NStmtClassConst (SEQUENCE eps) (INTEGER 0) ABSENT (SEQUENCE ([phpType46_k, phpType46_l])) metadata_group
S_default_public = $cint_raw($cint_raw(S_pre, pcpath_owner, (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_class) metadata_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_default_public, statement_properties, statement_static])) metadata_class)), pcpath_group, (statement_default_public))
$named_reference_notice_array(S_default_public, PARRAY n_root)
statement_raw_protected = NStmtClassConst (SEQUENCE eps) (INTEGER 2) ABSENT (SEQUENCE ([phpType46_k, phpType46_l])) metadata_group
S_raw_protected = $cint_raw($cint_raw(S_pre, pcpath_owner, (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_class) metadata_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_raw_protected, statement_properties, statement_static])) metadata_class)), pcpath_group, (statement_raw_protected))
~$named_reference_notice_array(S_raw_protected, PARRAY n_root)
statement_raw_typed = NStmtClassConst (SEQUENCE eps) (INTEGER 1) (NIdentifier (BYTES "aW50") eps) (SEQUENCE ([phpType46_k, phpType46_l])) metadata_group
S_raw_typed = $cint_raw($cint_raw(S_pre, pcpath_owner, (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_class) metadata_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_raw_typed, statement_properties, statement_static])) metadata_class)), pcpath_group, (statement_raw_typed))
~$named_reference_notice_array(S_raw_typed, PARRAY n_root)
statement_raw_attributes = NStmtClassConst (SEQUENCE ([(NAttributeGroup (SEQUENCE eps) eps)])) (INTEGER 1) ABSENT (SEQUENCE ([phpType46_k, phpType46_l])) metadata_group
S_raw_attributes = $cint_raw($cint_raw(S_pre, pcpath_owner, (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_class) metadata_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_raw_attributes, statement_properties, statement_static])) metadata_class)), pcpath_group, (statement_raw_attributes))
~$named_reference_notice_array(S_raw_attributes, PARRAY n_root)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--part', choices=('ingress', 'checkpoint', 'post'), default='post')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('class_int_constant_alias_stdclass_reference_notice_review_cases.json')
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
    reached = REACHED + (POST if args.part == 'checkpoint' else POST[:10] if args.part == 'post' else [])
    derived = CONTROLS if args.part == 'post' else PROTOCOL if args.part == 'ingress' else []
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
