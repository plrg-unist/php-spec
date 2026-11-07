#!/usr/bin/env python3
"""Check named current-object cell edges, shared COW, quiet targets and all ordinary ancestors."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
from alias_stdclass_reference_notice_review_cases import CASES

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $aol_output(pevent*) : ptbytes
def $aol_output(eps) = eps
def $aol_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $aol_output(pevent*)
dec $aol_stage(pstate, nat) : bool
def $aol_stage(S, 0) = $named_reference_notice_pending(S)
def $aol_stage(S, 1) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask*
def $aol_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $aol_output(S.EVENTS) = $ptascii("H;1:7;")
def $aol_stage(S, n) = false -- otherwise
dec $aol_seek(pstate, nat, nat) : pstate
def $aol_seek(S, n_stage, n) = S
  -- if $aol_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $aol_seek(S, n_stage, n) = $aol_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$aol_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aol_seek(S, n_stage, n) = S -- otherwise
'''

PRE = r'''
S_pre = $aol_seek(S_initial, 0, 768)[.COMPLETION = NORMAL]
$aol_stage(S_pre, 0)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("live")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved)
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_saved] = DEFINED (POBJECT n_old)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$node_children(S_pre, HARRAY n_root) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$node_children(S_pre, HOBJECT n_old) = eps
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
pobjectprops_old.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_array(S_pre, PARRAY n_root)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

HANDOFF = r'''
S_pre = $aol_seek(S_initial, 0, 768)[.COMPLETION = NORMAL]
$aol_stage(S_pre, 0)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("live")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved)
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_saved] = DEFINED (POBJECT n_old)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$node_children(S_pre, HARRAY n_root) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$node_children(S_pre, HOBJECT n_old) = eps
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
pobjectprops_old.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_array(S_pre, PARRAY n_root)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after = {SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps}
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HARRAY n_root) = 3
$heap_owners(H_notice, HCELL n_leaf) = 3
$heap_owners(H_notice, HOBJECT n_old) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_resume = $aol_seek(S_notice, 1, 768)[.COMPLETION = NORMAL]
$aol_stage(S_resume, 1)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("leaf")) = eps
$lookup(S_resume.ENV, $ptascii("live")) = (n_leaf)
S_resume.STORE[n_leaf] = DEFINED (POBJECT n_new)
n_new =/= n_old
$objectprops_at(S_resume.OBJECTPROPS, n_new) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 7)))}])
$objectprops_at(S_resume.OBJECTPROPS, n_old) = (pobjectprops_old.SLOTS)
$node_children(S_resume, HCELL n_leaf) = [HOBJECT n_new]
$duplicate_item(S_resume, n_root, ALIAS n_leaf) = ALIAS n_leaf
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1
$heap_owners(H_resume, HARRAY n_root) = 3
$heap_owners(H_resume, HCELL n_leaf) = 2
$heap_owners(H_resume, HOBJECT n_new) = 1
$heap_owners(H_resume, HOBJECT n_old) = 1
$error_call_valid(S_resume, perrorcall) /\ $call_descriptors_valid(S_resume)
$heap_valid(H_resume)
'''.strip().splitlines()

RETURNED = r'''
S_returned = $aol_seek(S_initial, 2, 1024)[.COMPLETION = NORMAL]
$aol_stage(S_returned, 2)
$acquire_call_valid(S_returned)
S_returned.RESULT = REFERENCE n_private
$lookup(S_returned.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_returned.ENV, $ptascii("source")) = (n_source)
$lookup(S_returned.ENV, $ptascii("live")) = (n_leaf)
$lookup(S_returned.ENV, $ptascii("saved")) = (n_saved)
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.STORE[n_copy] = DEFINED (PARRAY n_root)
S_returned.STORE[n_source] = DEFINED (PARRAY n_root)
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
S_returned.STORE[n_leaf] = DEFINED (POBJECT n_new)
S_returned.STORE[n_saved] = DEFINED (POBJECT n_old)
n_root =/= n_copied /\ n_new =/= n_old
S_returned.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
S_returned.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 99))]
$node_children(S_returned, HCELL n_private) = [HARRAY n_copied]
$node_children(S_returned, HARRAY n_root) = [HCELL n_leaf]
$node_children(S_returned, HARRAY n_copied) = [HCELL n_leaf]
$node_children(S_returned, HCELL n_leaf) = [HOBJECT n_new]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HARRAY n_root) = 2
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_leaf) = 3
$heap_owners(H_returned, HOBJECT n_new) = 1
$heap_owners(H_returned, HOBJECT n_old) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_zero = $drive(S_returned, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_returned
S_one = $drive(S_returned, 1)
S_split = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_returned, 2)
S_split = S_direct
S_full = $drive(S_returned, 1024)
S_full.COMPLETION = NORMAL
$aol_output(S_full.EVENTS) = $ptascii("H;1:7;9:1:0:5;13:13:9:99;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_leaf] = DEFINED (PINT 13)
S_full.STORE[n_private] = DEFINED (PARRAY n_copied)
$node_children(S_full, HCELL n_leaf) = eps
$objectprops_at(S_full.OBJECTPROPS, n_new) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 9)))}])
$objectprops_at(S_full.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}])
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_leaf) = 3
$heap_owners(H_full, HOBJECT n_new) = 1
$heap_owners(H_full, HOBJECT n_old) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
'''.strip().splitlines()

CELLS = r'''
~$named_reference_notice_entries(S_pre, S_pre.ARRAYS[n_root].ITEMS)
S_unmarked = S_pre[.REFCELLS = eps]
~$named_reference_notice_array(S_unmarked, PARRAY n_root)
S_cell_dead = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HCELL n_leaf)]
~$named_reference_notice_array(S_cell_dead, PARRAY n_root)
S_undefined = S_pre[.STORE[n_leaf] = UNDEFINED]
~$named_reference_notice_array(S_undefined, PARRAY n_root)
S_propref = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_propref, PARRAY n_root)
S_coercion = S_pre[.REFCOERCIONS = [{CELL n_leaf, SITE porigin_call, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_coercion, PARRAY n_root)
S_backed = S_pre[.PARAMETERBACKINGS = [{FUNCTION porigin_call, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_backed, PARRAY n_root)
S_container = S_pre[.CONTAINERINITS = [{CELL n_leaf, ARRAY n_root, SITE porigin_call, LINE 0}]]
~$named_reference_notice_array(S_container, PARRAY n_root)
S_cell_retained = S_pre[.LITERALREFRETAINED = [n_leaf]]
~$named_reference_notice_array(S_cell_retained, PARRAY n_root)
S_cell_debt = S_pre[.LITERALREFDEBTS = [n_leaf]]
~$named_reference_notice_array(S_cell_debt, PARRAY n_root)
S_cell_unit = S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_unit, PARRAY n_root)
S_bad_cell = S_pre[.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (ALIAS (|S_pre.STORE|))]]
~$named_reference_notice_array(S_bad_cell, PARRAY n_root)
S_bad_object = S_pre[.STORE[n_leaf] = DEFINED (POBJECT (|S_pre.OBJECTS|))]
~$named_reference_notice_array(S_bad_object, PARRAY n_root)
S_repeated = S_pre[.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ S_pre.ARRAYS[n_root].ITEMS]
$named_reference_notice_array(S_repeated, PARRAY n_root)
$node_children(S_repeated, HARRAY n_root) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_repeated, HCELL n_leaf) = [HOBJECT n_old]
$heap_owners($heap_graph(S_repeated), HCELL n_leaf) = 4
$heap_owners($heap_graph(S_repeated), HOBJECT n_old) = 2
S_scalar = S_pre[.STORE[n_leaf] = DEFINED (PINT 5)][.LITERALARRAYRETAINED = [n_root]][.LITERALARRAYDEBTS = [n_root]][.NATIVEEXCESS = [HARRAY n_root]]
$named_reference_notice_array(S_scalar, PARRAY n_root)
S_direct = S_pre[.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]]
$named_reference_notice_array(S_direct, PARRAY n_root)
'''.strip().splitlines()

OBJECTS = r'''
S_object_dead = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HOBJECT n_old)]
~$named_reference_notice_array(S_object_dead, PARRAY n_root)
S_kind = S_pre[.OBJECTS[n_old] = WEAKREFERENCE eps]
~$named_reference_notice_array(S_kind, PARRAY n_root)
S_missing = S_pre[.OBJECTPROPS = eps]
~$named_reference_notice_array(S_missing, PARRAY n_root)
S_unmaterialized = S_pre[.OBJECTPROPS = [pobjectprops_old[.MATERIALIZED = false]]]
~$named_reference_notice_array(S_unmaterialized, PARRAY n_root)
S_table = S_pre[.OBJECTTABLES = [{OBJECT n_old, TABLE n_root}]]
~$named_reference_notice_array(S_table, PARRAY n_root)
S_called = S_pre[.DESTRUCTION.CALLED = [n_old]]
~$named_reference_notice_array(S_called, PARRAY n_root)
pinstancestorage_guard = {OBJECT n_old, HANDLE 0, SLOTS pobjectprops_old.SLOTS, NEXT 0, NOTIFY eps, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, USER false}
S_freeing = S_pre[.TODO = [INSTANCE_STORAGE_STEP pinstancestorage_guard]]
$instance_storage_freeing(S_freeing, n_old)
~$named_reference_notice_array(S_freeing, PARRAY n_root)
S_object_unit = S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HOBJECT n_old]]
~$named_reference_notice_array(S_object_unit, PARRAY n_root)
S_worker = S_pre[.GC.WORKER = (0)]
~$named_reference_notice_array(S_worker, PARRAY n_root)
pgccall_guard = {NONCE 0, CALL {SITE porigin_call, KIND INTRINSIC_SET_ERROR_HANDLER, INDEX 0, SENT eps, NAMED false, OWNER eps, SELECTION eps, LINE 0, PACKS eps}, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, PASS 0, TOTAL 0, PENDING eps, COUNT_SOURCE eps}
S_active = S_pre[.GC.ACTIVE = (pgccall_guard)]
~$named_reference_notice_array(S_active, PARRAY n_root)
pgcplan_guard = {CALL pgccall_guard, GRAPH H_pre, EXCESS eps, TABLES eps, CALLED eps, PROXIES eps, WEAK eps, COUNTED eps, BUFFER eps, CANDIDATES eps, DTORS eps, FREESET eps, SCAN eps, INDEX 0, STEPS eps, DONE eps}
S_plan = S_pre[.GC.PLAN = (pgcplan_guard)]
~$named_reference_notice_array(S_plan, PARRAY n_root)
n_map = |S_pre.OBJECTS|
S_map = S_pre[.OBJECTS = S_pre.OBJECTS ++ [WEAKMAP ({KEY n_old, VALUE (PINT 0), BEFORE eps, ORDER 0})]][.ALLOCATIONS = S_pre.ALLOCATIONS ++ [HOBJECT n_map]]
$node_children(S_map, HOBJECT n_old) = eps
$weakmap_key_waiting(S_map, n_old)
~$named_reference_notice_array(S_map, PARRAY n_root)
S_owning = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}]]]]
~$named_reference_notice_array(S_owning, PARRAY n_root)
S_alias = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (ALIAS n_leaf))}]]]]
~$named_reference_notice_array(S_alias, PARRAY n_root)
S_raw = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("x")))))}]]]]
~$named_reference_notice_array(S_raw, PARRAY n_root)
S_request = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("x")))))}]]]]
~$named_reference_notice_array(S_request, PARRAY n_root)
S_nul = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING ([0]))))}]]]]
~$named_reference_notice_array(S_nul, PARRAY n_root)
S_nul_name = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ([0]), STATE (PROP_VALUE (DIRECT (PINT 5)))}]]]]
~$named_reference_notice_array(S_nul_name, PARRAY n_root)
'''.strip().splitlines()

ANCESTORS = r'''
n_child = |S_pre.ARRAYS|
S_child = $allocate_array(S_pre, $array_insert($array_empty(), KINT 0, ALIAS n_leaf))
n_middle = |S_child.ARRAYS|
S_middle = $allocate_array(S_child, $array_insert($array_empty(), KINT 0, DIRECT (PARRAY n_child)))
S_chain = S_middle[.ARRAYS[n_root] = $array_insert($array_empty(), KINT 0, DIRECT (PARRAY n_middle))][.RESULT = S_pre.RESULT]
$named_reference_notice_array(S_chain, PARRAY n_root)
$named_reference_notice_object_ancestors(S_chain, [n_child, n_middle, n_root])
$node_children(S_chain, HCELL n_leaf) = [HOBJECT n_old]
$heap_owners($heap_graph(S_chain), HOBJECT n_old) = 2
S_dag = S_chain[.ARRAYS[n_root] = $array_insert(S_chain.ARRAYS[n_root], KINT 1, DIRECT (PARRAY n_middle))]
$named_reference_notice_array(S_dag, PARRAY n_root)
$heap_owners($heap_graph(S_dag), HARRAY n_middle) = 2
$heap_owners($heap_graph(S_dag), HARRAY n_child) = 1
$heap_owners($heap_graph(S_dag), HOBJECT n_old) = 2
S_array_alias = $reference_cell(S_chain[.STORE[n_saved] = DEFINED (PARRAY n_middle)][.ARRAYS[n_root] = $array_insert($array_empty(), KINT 0, ALIAS n_saved)], n_saved)
$named_reference_notice_array(S_array_alias, PARRAY n_root)
$node_children(S_array_alias, HCELL n_saved) = [HARRAY n_middle]
S_cycle = S_chain[.ARRAYS[n_child] = $array_insert($array_empty(), KINT 0, DIRECT (PARRAY n_root))]
~$named_reference_notice_array(S_cycle, PARRAY n_root)
S_alias_cycle = S_array_alias[.STORE[n_saved] = DEFINED (PARRAY n_root)]
~$named_reference_notice_array(S_alias_cycle, PARRAY n_root)
S_pre.POOLS = ppool :: ppool_tail*
S_root_retained = S_chain[.LITERALARRAYRETAINED = S_chain.LITERALARRAYRETAINED ++ [n_root]]
~$named_reference_notice_array(S_root_retained, PARRAY n_root)
S_root_debt = S_chain[.LITERALARRAYDEBTS = S_chain.LITERALARRAYDEBTS ++ [n_root]]
~$named_reference_notice_array(S_root_debt, PARRAY n_root)
S_root_unit = S_chain[.NATIVEEXCESS = S_chain.NATIVEEXCESS ++ [HARRAY n_root]]
~$named_reference_notice_array(S_root_unit, PARRAY n_root)
S_root_dead = S_chain[.ALLOCATIONS = $call_remove_owner(S_chain.ALLOCATIONS, HARRAY n_root)]
~$named_reference_notice_array(S_root_dead, PARRAY n_root)
S_root_pool = S_chain[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_root)]] :: ppool_tail*]
~$named_reference_notice_array(S_root_pool, PARRAY n_root)
S_middle_retained = S_chain[.LITERALARRAYRETAINED = S_chain.LITERALARRAYRETAINED ++ [n_middle]]
~$named_reference_notice_array(S_middle_retained, PARRAY n_root)
S_middle_debt = S_chain[.LITERALARRAYDEBTS = S_chain.LITERALARRAYDEBTS ++ [n_middle]]
~$named_reference_notice_array(S_middle_debt, PARRAY n_root)
S_middle_unit = S_chain[.NATIVEEXCESS = S_chain.NATIVEEXCESS ++ [HARRAY n_middle]]
~$named_reference_notice_array(S_middle_unit, PARRAY n_root)
S_middle_dead = S_chain[.ALLOCATIONS = $call_remove_owner(S_chain.ALLOCATIONS, HARRAY n_middle)]
~$named_reference_notice_array(S_middle_dead, PARRAY n_root)
S_middle_pool = S_chain[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_middle)]] :: ppool_tail*]
~$named_reference_notice_array(S_middle_pool, PARRAY n_root)
S_child_retained = S_chain[.LITERALARRAYRETAINED = S_chain.LITERALARRAYRETAINED ++ [n_child]]
~$named_reference_notice_array(S_child_retained, PARRAY n_root)
S_child_debt = S_chain[.LITERALARRAYDEBTS = S_chain.LITERALARRAYDEBTS ++ [n_child]]
~$named_reference_notice_array(S_child_debt, PARRAY n_root)
S_child_unit = S_chain[.NATIVEEXCESS = S_chain.NATIVEEXCESS ++ [HARRAY n_child]]
~$named_reference_notice_array(S_child_unit, PARRAY n_root)
S_child_dead = S_chain[.ALLOCATIONS = $call_remove_owner(S_chain.ALLOCATIONS, HARRAY n_child)]
~$named_reference_notice_array(S_child_dead, PARRAY n_root)
S_child_pool = S_chain[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_child)]] :: ppool_tail*]
~$named_reference_notice_array(S_child_pool, PARRAY n_root)
S_empty_immutable = S_chain[.ARRAYS[n_middle] = $array_empty()][.GC.IMMUTABLE = S_chain.GC.IMMUTABLE ++ [n_middle]]
~$named_reference_notice_object_ancestors(S_empty_immutable, [n_child, n_middle, n_root])
~$named_reference_notice_object_ancestors(S_chain, [n_child, (|S_chain.ARRAYS|), n_root])
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--capture-steps', type=int)
    selection.add_argument('--part', choices=('handoff', 'returned', 'cells', 'objects', 'ancestors'))
    args = parser.parse_args()
    assert args.capture_steps is None or 0 < args.capture_steps <= 64
    native_path = args.native_provenance.resolve()
    native = json.loads(native_path.read_bytes())
    source = Path(native['command'][-1])
    assert native['passed'] and native['mode'] == 'native-only'
    assert source.read_bytes() == CASES[native['id']]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='alias-stdclass-reference-review-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), native_path, source,
        ROOT / 'tests/semantics/alias_stdclass_reference_notice_review_cases.py',
        ROOT / 'tests/semantics/alias_stdclass_reference_notice_review_cases.json',
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
        assert prepared.get('capture_steps') == args.capture_steps
        assert prepared.get('part') == args.part
    else:
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
        initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
            base64.b64encode(os.fsencode(source)).decode()) + ')'
        reached = {'handoff': HANDOFF, 'returned': RETURNED}.get(args.part, PRE)
        derived = {'cells': CELLS, 'objects': OBJECTS, 'ancestors': ANCESTORS}.get(args.part, [])
        checks = [initial] + reached + derived
        signature = 'dec $main() : bool\ndef $main() = true\n'
        if args.capture_steps is not None:
            checks = [initial, f'S_snapshot = $drive_steps(S_initial[.COMPLETION = NORMAL], {args.capture_steps})']
            signature = 'dec $main() : pstate\ndef $main() = S_snapshot\n'
        fixture = directory / 'state.watsup'
        fixture.write_text(PREFIX + '\n' + signature +
            ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'source': str(source),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'part': args.part, 'conditions': len(checks), 'reached_conditions': len(reached) + 1,
            'derived_conditions': len(derived), 'heap_bindings': sum(check.startswith('H_') for check in reached),
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
        if args.capture_steps is not None:
            prepared.update(capture_steps=args.capture_steps, conditions=0,
                reached_conditions=0, derived_conditions=0, heap_bindings=0,
                scope='Finite typed pstate capture only; no ownership assertions or source agreements.')
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture = directory / 'state.watsup'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run',
        180 if args.capture_steps is not None else 480)
    stable = before == fingerprints() and hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    stdout = (directory / 'run.stdout').read_bytes()
    result_valid = stdout.startswith(b'{\n') if args.capture_steps is not None else stdout == b'true\n'
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and result_valid
        and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable,
        module_count=len(modules), mode='AL/cache=false/det=true',
        process=process, passed=passed, source_agreements=0)
    if args.capture_steps is not None:
        report['snapshot_sha256'] = hashlib.sha256(stdout).hexdigest()
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('finite AL capture' if args.capture_steps is not None else args.part,
        passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
