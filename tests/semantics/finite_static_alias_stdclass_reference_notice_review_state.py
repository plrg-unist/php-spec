#!/usr/bin/env python3
"""Check four genuine static roots at the reference-Notice admission boundary."""
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
from finite_static_alias_stdclass_reference_notice_review_cases import CASES

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $fsn_output(pevent*) : ptbytes
def $fsn_output(eps) = eps
def $fsn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $fsn_output(pevent*)
dec $fsn_ingress(pstate) : bool
def $fsn_ingress(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $fsn_output(S.EVENTS) = $ptascii("A;")
def $fsn_ingress(S) = false -- otherwise
dec $fsn_seek(pstate, nat) : pstate
def $fsn_seek(S, n) = S
  -- if $fsn_ingress(S) \/ n = 0 \/ S.TODO = eps
def $fsn_seek(S, n) = $fsn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$fsn_ingress(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fsn_seek(S, n) = S -- otherwise
dec $fsn_stage(pstate, nat) : bool
def $fsn_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;")
def $fsn_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;")
def $fsn_stage(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;")
def $fsn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;E;H;F;")
def $fsn_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;E;H;F;1:1:1:1:1;T;B;")
def $fsn_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;E;H;F;1:1:1:1:1;T;B;U;D;")
def $fsn_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;E;H;F;1:1:1:1:1;T;B;U;D;V;Z;")
def $fsn_stage(S, 7) = true
  -- if S.CURRENT = eps
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;E;H;F;1:1:1:1:1;T;B;U;D;V;Z;41:41;N;Q;")
def $fsn_stage(S, 8) = true
  -- if S.CURRENT = eps
  -- if $fsn_output(S.EVENTS) = $ptascii("A;S;G;E;H;F;1:1:1:1:1;T;B;U;D;V;Z;41:41;N;Q;C;")
def $fsn_stage(S, n) = false -- otherwise
dec $fsn_after(pstate, nat, nat) : pstate
def $fsn_after(S, n_stage, n) = S
  -- if $fsn_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $fsn_after(S, n_stage, n) = $fsn_after($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$fsn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fsn_after(S, n_stage, n) = $fsn_after($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$fsn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $fsn_after(S, n_stage, n) = S -- otherwise
'''

PRE = r'''
S_pre = $fsn_seek(S_initial, 1024)[.COMPLETION = NORMAL]
$fsn_ingress(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("third")) = (n_third_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_third_cv] = DEFINED (POBJECT n_third)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
n_leaf =/= n_bad_cv /\ n_old =/= n_new /\ n_new =/= n_third
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$class_named(S_pre.CLASSNAMES, $ptascii("reviewalpha15")) = (porigin_alpha)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewbeta15")) = (porigin_beta)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewgamma15")) = (porigin_gamma)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewdelta15")) = (porigin_delta)
$class_at(S_pre.CLASSES, porigin_alpha) = (pclassdesc_alpha)
$class_at(S_pre.CLASSES, porigin_beta) = (pclassdesc_beta)
$class_at(S_pre.CLASSES, porigin_gamma) = (pclassdesc_gamma)
$class_at(S_pre.CLASSES, porigin_delta) = (pclassdesc_delta)
pclassdesc_alpha.PROPERTIES = [ppropertydesc_alpha]
pclassdesc_beta.PROPERTIES = [ppropertydesc_beta]
pclassdesc_gamma.PROPERTIES = [ppropertydesc_gamma]
pclassdesc_delta.PROPERTIES = [ppropertydesc_delta]
ppropertyid_alpha = ppropertydesc_alpha.ORIGIN
ppropertyid_beta = ppropertydesc_beta.ORIGIN
ppropertyid_gamma = ppropertydesc_gamma.ORIGIN
ppropertyid_delta = ppropertydesc_delta.ORIGIN
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_gamma, CLASS_PROP_SOURCE ppropertyid_alpha, CLASS_PROP_SOURCE ppropertyid_delta, CLASS_PROP_SOURCE ppropertyid_beta]
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_alpha)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_gamma)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_delta)
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_alpha) = ({DECL ppropertyid_alpha, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_beta) = ({DECL ppropertyid_beta, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_gamma) = ({DECL ppropertyid_gamma, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_delta) = ({DECL ppropertyid_delta, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object_ancestors(S_pre, [n_root])
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
$reference_coercion_at(S_pre.REFCOERCIONS, n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf)
$heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 6
$heap_owners(H_pre, HOBJECT n_old) = 2
$heap_owners(H_pre, HOBJECT n_new) = 1
$heap_owners(H_pre, HOBJECT n_third) = 1
(HCELL n_leaf) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $class_statics_valid(S_pre) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''
~$named_reference_notice_object_static_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_singleton = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_alpha])}]]
$named_reference_notice_object_static_source(S_singleton, n_leaf)
$named_reference_notice_array(S_singleton, PARRAY n_root)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_static_source(S_pre, n_leaf)
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
S_same = $fsn_after(S_notice, 0, 1024)[.COMPLETION = NORMAL]
$fsn_stage(S_same, 0)
S_same.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_same.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_gamma, CLASS_PROP_SOURCE ppropertyid_beta, CLASS_PROP_SOURCE ppropertyid_delta, CLASS_PROP_SOURCE ppropertyid_alpha])})
$named_reference_notice_array(S_same, PARRAY n_root)
S_partial = $fsn_after(S_same, 1, 512)[.COMPLETION = NORMAL]
$fsn_stage(S_partial, 1)
$propref_at(S_partial.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_alpha, CLASS_PROP_SOURCE ppropertyid_beta, CLASS_PROP_SOURCE ppropertyid_delta])})
$propref_at(S_partial.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_gamma])})
$class_static_roots(S_partial.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf, HCELL n_new_cv, HCELL n_leaf]
$named_reference_notice_array(S_partial, PARRAY n_root)
S_failed = $fsn_after(S_partial, 2, 512)
$fsn_stage(S_failed, 2)
S_failed.CLASSSTATICS = S_partial.CLASSSTATICS
S_failed.PROPREFS = S_partial.PROPREFS
S_failed.STORE[n_leaf] = S_pre.STORE[n_leaf]
S_failed.STORE[n_bad_cv] = S_pre.STORE[n_bad_cv]
$propref_at(S_failed.PROPREFS, n_bad_cv) = eps
$proprefs_valid(S_failed) /\ $class_statics_valid(S_failed)
S_returned = $fsn_after(S_failed, 3, 1536)[.COMPLETION = NORMAL]
$fsn_stage(S_returned, 3)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.CLASSSTATICS = S_partial.CLASSSTATICS
S_returned.PROPREFS = S_partial.PROPREFS
$duplicate_item(S_returned, n_copied, ALIAS n_leaf) = ALIAS n_leaf
H_returned = $heap_graph(S_returned)
H_returned = $heap_graph(S_returned[.PROPREFS = eps])
$heap_owners(H_returned, HCELL n_leaf) = 5
$heap_owners(H_returned, HOBJECT n_old) = 2
$heap_owners(H_returned, HCELL n_new_cv) = 2
$heap_owners(H_returned, HARRAY n_root) = 2
$heap_owners(H_returned, HARRAY n_copied) = 1
$proprefs_valid(S_returned) /\ $class_statics_valid(S_returned) /\ $call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_second = $fsn_after(S_returned, 4, 1536)[.COMPLETION = NORMAL]
$fsn_stage(S_second, 4)
$propref_at(S_second.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_alpha, CLASS_PROP_SOURCE ppropertyid_delta])})
$propref_at(S_second.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_gamma, CLASS_PROP_SOURCE ppropertyid_beta])})
$class_static_roots(S_second.CLASSSTATICS) = [HCELL n_leaf, HCELL n_new_cv, HCELL n_new_cv, HCELL n_leaf]
$named_reference_notice_array(S_second, PARRAY n_copied)
S_last = $fsn_after(S_second, 5, 1024)[.COMPLETION = NORMAL]
$fsn_stage(S_last, 5)
$propref_at(S_last.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_alpha])})
$propref_at(S_last.PROPREFS, n_third_cv) = ({CELL n_third_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_delta])})
$class_static_roots(S_last.CLASSSTATICS) = [HCELL n_leaf, HCELL n_new_cv, HCELL n_new_cv, HCELL n_third_cv]
$named_reference_notice_array(S_last, PARRAY n_copied)
S_final = $fsn_after(S_last, 6, 1024)[.COMPLETION = NORMAL]
$fsn_stage(S_final, 6)
$propref_at(S_final.PROPREFS, n_leaf) = eps
$propref_at(S_final.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_gamma, CLASS_PROP_SOURCE ppropertyid_beta, CLASS_PROP_SOURCE ppropertyid_alpha])})
$class_static_roots(S_final.CLASSSTATICS) = [HCELL n_new_cv, HCELL n_new_cv, HCELL n_new_cv, HCELL n_third_cv]
S_final.STORE[n_leaf] = S_pre.STORE[n_leaf]
$named_reference_notice_array(S_final, PARRAY n_copied)
H_final = $heap_graph(S_final)
$heap_owners(H_final, HCELL n_leaf) = 2
$heap_owners(H_final, HCELL n_new_cv) = 4
$heap_owners(H_final, HCELL n_third_cv) = 2
$proprefs_valid(S_final) /\ $class_statics_valid(S_final) /\ $heap_valid(H_final)
S_singleton = $fsn_after(S_final, 7, 1536)[.COMPLETION = NORMAL]
$fsn_stage(S_singleton, 7)
S_singleton.STORE[n_leaf] = DEFINED (POBJECT n_old)
$propref_at(S_singleton.PROPREFS, n_leaf) = eps
~((HARRAY n_root) <- S_singleton.ALLOCATIONS)
H_singleton = $heap_graph(S_singleton)
$heap_owners(H_singleton, HCELL n_leaf) = 1
$heap_owners(H_singleton, HOBJECT n_old) = 2
$duplicate_item(S_singleton, n_copied, ALIAS n_leaf) = DIRECT (POBJECT n_old)
S_copied = $fsn_after(S_singleton, 8, 1024)[.COMPLETION = NORMAL]
$fsn_stage(S_copied, 8)
$lookup(S_copied.ENV, $ptascii("snapshot")) = (n_snapshot_cv)
S_copied.STORE[n_snapshot_cv] = DEFINED (PARRAY n_snapshot)
n_snapshot =/= n_copied
S_copied.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_copied.ARRAYS[n_snapshot].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 13))]
$node_children(S_copied, HARRAY n_copied) = [HCELL n_leaf]
$node_children(S_copied, HARRAY n_snapshot) = [HOBJECT n_old]
H_copied = $heap_graph(S_copied)
$heap_owners(H_copied, HCELL n_leaf) = 1
$heap_owners(H_copied, HOBJECT n_old) = 3
$proprefs_valid(S_copied) /\ $class_statics_valid(S_copied) /\ $call_descriptors_valid(S_copied) /\ $heap_valid(H_copied)
S_zero = $drive(S_copied, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_copied
$drive($drive(S_copied, 1)[.COMPLETION = NORMAL], 1) = $drive(S_copied, 2)
'''.strip().splitlines()

SOURCES = r'''
S_reverse = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_beta, CLASS_PROP_SOURCE ppropertyid_delta, CLASS_PROP_SOURCE ppropertyid_alpha, CLASS_PROP_SOURCE ppropertyid_gamma])}]]
$named_reference_notice_object_static_source(S_reverse, n_leaf)
$named_reference_notice_array(S_reverse, PARRAY n_root)
$proprefs_valid(S_reverse) /\ $class_statics_valid(S_reverse)
S_duplicate = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid_beta])}]]
~$named_reference_notice_object_static_source(S_duplicate, n_leaf)
~$named_reference_notice_array(S_duplicate, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_object_static_source(S_empty, n_leaf)
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_mixed = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [OBJECT_PROP_SOURCE n_old ($ptascii("v")) ppropertyid_beta])}]]
~$named_reference_notice_object_static_source(S_mixed, n_leaf)
~$named_reference_notice_array(S_mixed, PARRAY n_root)
ppropertyid_beta = PORIGIN n_beta_source pcpath_beta
S_retired = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [RETIRED_CLASS_PROP_SOURCE (PORIGIN n_beta_source pcpath_beta) 0])}]]
~$named_reference_notice_object_static_source(S_retired, n_leaf)
~$named_reference_notice_array(S_retired, PARRAY n_root)
S_wrong_cell = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_beta, PROP_VALUE (ALIAS n_new_cv))]
~$propref_source_valid(S_wrong_cell, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_wrong_cell, PARRAY n_root)
S_direct = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_beta, PROP_VALUE (DIRECT (POBJECT n_old)))]
~$named_reference_notice_array(S_direct, PARRAY n_root)
S_initial_row = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_beta, PROP_INITIAL)]
~$named_reference_notice_array(S_initial_row, PARRAY n_root)
S_no_rows = S_pre[.CLASSSTATICS = eps]
~$named_reference_notice_array(S_no_rows, PARRAY n_root)
S_no_beta = S_pre[.CLASSSTATICS = [{DECL ppropertyid_alpha, STATE PROP_VALUE (ALIAS n_leaf)}, {DECL ppropertyid_gamma, STATE PROP_VALUE (ALIAS n_leaf)}, {DECL ppropertyid_delta, STATE PROP_VALUE (ALIAS n_leaf)}]]
~$propref_source_valid(S_no_beta, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_no_beta, PARRAY n_root)
S_no_metadata = S_pre[.PROPREFS = eps]
$heap_graph(S_no_metadata) = H_pre
~$class_statics_valid(S_no_metadata)
S_no_active = S_pre[.CLASSNAMES = eps]
~$named_reference_notice_array(S_no_active, PARRAY n_root)
S_no_source = S_pre[.SOURCES = eps]
$propref_source_valid(S_no_source, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_no_source, PARRAY n_root)
S_pre.CLASSES = [pclassdesc_alpha, pclassdesc_beta, pclassdesc_gamma, pclassdesc_delta]
S_nullable = S_pre[.CLASSES = [pclassdesc_alpha, pclassdesc_beta[.PROPERTIES = [ppropertydesc_beta[.TYPE = [(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "null"]))]]]], pclassdesc_gamma, pclassdesc_delta]]
$propref_source_valid(S_nullable, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_protected = S_pre[.CLASSES = [pclassdesc_alpha, pclassdesc_beta[.PROPERTIES = [ppropertydesc_beta[.VISIBILITY = PROPERTY_PROTECTED]]], pclassdesc_gamma, pclassdesc_delta]]
$propref_source_valid(S_protected, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_parent = S_pre[.CLASSES = [pclassdesc_alpha, pclassdesc_beta[.PARENT = ($ptascii("Unknown"))], pclassdesc_gamma, pclassdesc_delta]]
~$named_reference_notice_array(S_parent, PARRAY n_root)
S_deferred = S_pre[.CLASSES = [pclassdesc_alpha, pclassdesc_beta[.PROPERTIES = [ppropertydesc_beta[.DEFAULT = PROP_DEFERRED pclassdesc_beta.ORIGIN]]], pclassdesc_gamma, pclassdesc_delta]]
$propref_source_valid(S_deferred, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_deferred, PARRAY n_root)
S_cell_unit = S_pre[.NATIVEEXCESS = [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_unit, PARRAY n_root)
S_root_unit = S_pre[.NATIVEEXCESS = [HARRAY n_root]]
~$named_reference_notice_array(S_root_unit, PARRAY n_root)
S_cell_debt = S_pre[.LITERALREFDEBTS = [n_leaf]]
~$named_reference_notice_array(S_cell_debt, PARRAY n_root)
S_owned = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (POBJECT n_new)))}])]
$propref_source_valid(S_owned, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
~$named_reference_notice_array(S_owned, PARRAY n_root)
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
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed']
    assert source.read_bytes() == CASES[native['id']]
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == digest(types.PHP)
    assert native['source_sha256'] == digest(source)
    directory = args.output.resolve()
    directory.mkdir(parents=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), provenance, source, types.PHP,
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py',
        'tests/semantics/finite_static_alias_stdclass_reference_notice_review_cases.py',
        'tests/semantics/finite_static_alias_stdclass_reference_notice_review_cases.json')]
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
    reached = PRE + ([] if args.part == 'ingress' else ADMITTED)
    derived = INGRESS if args.part == 'ingress' else SOURCES if args.part == 'sources' else []
    if args.part == 'ownership':
        reached += OWNERSHIP
    checks = [initial] + reached + derived
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    fixture_sha = digest(fixture)
    print(directory, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 720)
    stable = before == fingerprints() and digest(fixture) == fixture_sha
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'source': str(source), 'source_sha256': digest(source),
        'fixture_sha256': fixture_sha, 'part': args.part, 'conditions': len(checks), 'reached_conditions': len(reached) + 1,
        'derived_conditions': len(derived), 'heap_bindings': 1 + sum(check.startswith('H_') and ' = $heap_graph(' in check and '[.PROPREFS' not in check for check in reached[len(PRE):]), 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.part, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
