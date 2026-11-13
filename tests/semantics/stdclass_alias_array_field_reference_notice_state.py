#!/usr/bin/env python3
"""Ground physical array-field edges, finite child tables and independent quiet COW before Notices."""
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
CATALOGUE = Path(__file__).with_name('stdclass_alias_array_field_reference_notice_cases.json')

PREFIX = r"""
dec $aaf_output(pevent*) : ptbytes
def $aaf_output(eps) = eps
def $aaf_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $aaf_output(pevent*)
dec $aaf_ready(pstate, nat) : bool
def $aaf_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("StdClassAliasArrayNotice44\\make") \/ pcallcontext.NAME = $ptascii("StdClassAliasArrayThrow44\\make")
def $aaf_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("StdClassAliasArrayNotice44\\take") \/ pfunction.NAME = $ptascii("StdClassAliasArrayThrow44\\take")
def $aaf_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("K;M:1;F:1:1;R:Y7:Y7:Y7:17:18:1:1;")
def $aaf_ready(S, 3) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;")
def $aaf_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;")
def $aaf_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;D;")
def $aaf_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;D;P;")
def $aaf_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;D;P;K;")
def $aaf_ready(S, 8) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;D;P;K;L;")
def $aaf_ready(S, 9) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $aaf_ready(S, 10) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;D;P;K;L;O;")
def $aaf_ready(S, 11) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $aaf_output(S.EVENTS) = $ptascii("A;M:1;H:1;F:1:1;R:X3:X3:X3:17:28:1:1;D;P;K;L;O;S;")
def $aaf_ready(S, n_stage) = false -- otherwise
dec $aaf_seek(pstate, nat, nat) : pstate
def $aaf_seek(S, n_stage, n) = S
  -- if $aaf_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $aaf_seek(S, n_stage, n) = $aaf_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$aaf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aaf_seek(S, n_stage, n) = $aaf_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$aaf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $aaf_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $aaf_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_return, 0)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("StdClassAliasArrayNotice44\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
$lookup(S_return.ENV, $ptascii("input")) = (n_source)
S_return.STORE[n_source] = DEFINED (POBJECT n_object)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("outside")) = (n_outside)
$lookup(psymboltable_caller.ENV, $ptascii("shared")) = (n_shared)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("seed")) = eps
S_return.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_return.STORE[n_leaf] = DEFINED (PARRAY n_array)
S_return.STORE[n_outside] = DEFINED (PARRAY n_array)
S_return.STORE[n_shared] = DEFINED pvalue_shared
pvalue_shared = PSTRING_CARRIER (REQUEST_STRING n_shared_string) ($ptascii("19"))
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original) /\ $string_carrier_valid(S_return, pvalue_shared)
S_return.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_child)), ENTRY (KSTRING ($ptascii("shared"))) (ALIAS n_shared)]
S_return.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_original)]
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops)
pobjectprops.SLOTS = [ppropertyslot_items, ppropertyslot_again]
ppropertyslot_items = {DECL eps, NAME ($ptascii("items")), STATE (PROP_VALUE (ALIAS n_leaf))}
ppropertyslot_again = {DECL eps, NAME ($ptascii("again")), STATE (PROP_VALUE (ALIAS n_leaf))}
$node_children(S_return, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_return, HCELL n_leaf) = [HARRAY n_array]
$node_children(S_return, HARRAY n_array) = [HARRAY n_child, HCELL n_shared]
$node_children(S_return, HARRAY n_child) = eps /\ $node_children(S_return, HCELL n_shared) = eps
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source) = 3 /\ $heap_owners(H_return, HOBJECT n_object) = 3
$heap_owners(H_return, HCELL n_leaf) = 3 /\ $heap_owners(H_return, HARRAY n_array) = 2
$heap_owners(H_return, HARRAY n_child) = 1 /\ $heap_owners(H_return, HCELL n_shared) = 2
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $aaf_seek(S_after_return, 1, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("source")) = (n_source) /\ $lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf) /\ $lookup(S_pre.ENV, $ptascii("outside")) = (n_outside)
S_pre.STORE[n_leaf] = DEFINED (PARRAY n_array) /\ S_pre.STORE[n_outside] = DEFINED (PARRAY n_array)
S_pre.STORE[n_shared] = DEFINED pvalue_shared /\ S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops)
$objectprops_valid(S_pre, [pobjectprops])
$call_reference_operand_valid(S_pre, REFERENCE n_leaf) /\ $call_reference_operand_valid(S_pre, REFERENCE n_shared)
$named_reference_notice_array(S_pre, PARRAY n_array)
$property_release_nodes(pobjectprops.SLOTS) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HARRAY n_array]
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf) /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
~$array_immutable(S_pre, n_array) /\ ~$array_immutable(S_pre, n_child)
~((HARRAY n_array) <- $heap_reach($pools_nodes(S_pre.POOLS), eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
~((HARRAY n_child) <- $heap_reach($pools_nodes(S_pre.POOLS), eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
~$weakmap_key_waiting(S_pre, n_object)
$aaf_output(S_pre.EVENTS) = $ptascii("A;M:1;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source) = 2 /\ $heap_owners(H_pre, HOBJECT n_object) = 3
$heap_owners(H_pre, HCELL n_leaf) = 3 /\ $heap_owners(H_pre, HARRAY n_array) = 2
$heap_owners(H_pre, HARRAY n_child) = 1 /\ $heap_owners(H_pre, HCELL n_shared) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

THROW = r"""
S_throw_return = $aaf_seek(S_throw_initial, 0, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("StdClassAliasArrayThrow44\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (POBJECT n_throw_object)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
pobjectprops_throw.SLOTS = [{DECL eps, NAME ($ptascii("items")), STATE (PROP_VALUE (ALIAS n_throw_leaf))}]
S_throw_return.STORE[n_throw_leaf] = DEFINED (PARRAY n_throw_array)
S_throw_return.ARRAYS[n_throw_array].ITEMS = [ENTRY (KSTRING ($ptascii("branch"))) (DIRECT (PARRAY n_throw_child))]
S_throw_return.ARRAYS[n_throw_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_throw)]
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_return, pvalue_throw)
S_throw_return.GLOBALTABLE = (psymboltable_throw)
$lookup(psymboltable_throw.ENV, $ptascii("leaf")) = eps /\ $lookup(psymboltable_throw.ENV, $ptascii("seed")) = eps
$lookup(psymboltable_throw.ENV, $ptascii("snapshot")) = (n_throw_snapshot)
$lookup(psymboltable_throw.ENV, $ptascii("watch")) = (n_throw_watch)
S_throw_return.STORE[n_throw_snapshot] = DEFINED pvalue_throw
S_throw_return.STORE[n_throw_watch] = DEFINED (POBJECT n_throw_weak)
S_throw_return.OBJECTS[n_throw_weak] = WEAKREFERENCE (n_throw_object)
$node_children(S_throw_return, HOBJECT n_throw_weak) = eps
S_throw_after_return = $drive(S_throw_return, 1)[.COMPLETION = NORMAL]
H_throw_return = $heap_graph(S_throw_after_return)
$heap_owners(H_throw_return, HOBJECT n_throw_object) = 2 /\ $heap_owners(H_throw_return, HCELL n_throw_leaf) = 1
$heap_owners(H_throw_return, HARRAY n_throw_array) = 1 /\ $heap_owners(H_throw_return, HARRAY n_throw_child) = 1
$heap_valid(H_throw_return)
S_throw_pre = $aaf_seek(S_throw_after_return, 1, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (POBJECT n_throw_object)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps /\ $lookup(S_throw_pre.ENV, $ptascii("leaf")) = eps
$call_reference_operand_valid(S_throw_pre, REFERENCE n_throw_leaf)
$objectprops_record_at(S_throw_pre.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
$objectprops_valid(S_throw_pre, [pobjectprops_throw])
$node_children(S_throw_pre, HOBJECT n_throw_object) = [HCELL n_throw_leaf]
$node_children(S_throw_pre, HCELL n_throw_leaf) = [HARRAY n_throw_array]
$node_children(S_throw_pre, HARRAY n_throw_array) = [HARRAY n_throw_child] /\ $node_children(S_throw_pre, HARRAY n_throw_child) = eps
$named_reference_notice_array(S_throw_pre, PARRAY n_throw_array)
S_throw_pre.PARAMETERBACKINGS = eps /\ S_throw_pre.PROPREFS = eps /\ S_throw_pre.REFCOERCIONS = eps /\ S_throw_pre.CONTAINERINITS = eps
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$aaf_output(S_throw_pre.EVENTS) = $ptascii("T;M;")
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pre, HCELL n_throw_leaf) = 1
$heap_owners(H_throw_pre, HARRAY n_throw_array) = 1 /\ $heap_owners(H_throw_pre, HARRAY n_throw_child) = 1
$heap_valid(H_throw_pre) /\ $call_descriptors_valid(S_throw_pre)
""".strip().splitlines()

QUIET = r"""
S_quiet_cow = $aaf_seek(S_quiet_initial, 2, 6000)[.COMPLETION = NORMAL]
$aaf_ready(S_quiet_cow, 2)
~$error_handler_eligible(S_quiet_cow, 8)
$lookup(S_quiet_cow.ENV, $ptascii("r")) = (n_quiet_private)
$lookup(S_quiet_cow.ENV, $ptascii("source")) = (n_quiet_source)
$lookup(S_quiet_cow.ENV, $ptascii("sourceAlias")) = (n_quiet_source)
$lookup(S_quiet_cow.ENV, $ptascii("keeper")) = (n_quiet_keeper)
$lookup(S_quiet_cow.ENV, $ptascii("leaf")) = (n_quiet_leaf)
$lookup(S_quiet_cow.ENV, $ptascii("outside")) = (n_quiet_outside)
$lookup(S_quiet_cow.ENV, $ptascii("shared")) = (n_quiet_shared)
$lookup(S_quiet_cow.ENV, $ptascii("snapshot")) = (n_quiet_snapshot)
S_quiet_cow.STORE[n_quiet_private] = DEFINED (POBJECT n_quiet_object)
S_quiet_cow.STORE[n_quiet_source] = DEFINED (POBJECT n_quiet_object) /\ S_quiet_cow.STORE[n_quiet_keeper] = DEFINED (POBJECT n_quiet_object)
S_quiet_cow.STORE[n_quiet_leaf] = DEFINED (PARRAY n_quiet_array)
S_quiet_cow.STORE[n_quiet_outside] = DEFINED (PARRAY n_quiet_old_array)
n_quiet_array =/= n_quiet_old_array
S_quiet_cow.ARRAYS[n_quiet_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_quiet_child)), ENTRY (KSTRING ($ptascii("shared"))) (ALIAS n_quiet_shared)]
S_quiet_cow.ARRAYS[n_quiet_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_quiet_old_child)), ENTRY (KSTRING ($ptascii("shared"))) (ALIAS n_quiet_shared)]
n_quiet_child =/= n_quiet_old_child
S_quiet_cow.ARRAYS[n_quiet_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT (PSTRING ($ptascii("Y7"))))]
S_quiet_cow.ARRAYS[n_quiet_old_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_quiet_original)]
pvalue_quiet_original = PSTRING_CARRIER (REQUEST_STRING n_quiet_string) ($ptascii("17"))
S_quiet_cow.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet_original
$string_carrier_valid(S_quiet_cow, pvalue_quiet_original)
S_quiet_cow.STORE[n_quiet_shared] = DEFINED (PSTRING ($ptascii("18")))
$objectprops_record_at(S_quiet_cow.OBJECTPROPS, n_quiet_object) = (pobjectprops_quiet)
pobjectprops_quiet.SLOTS = [{DECL eps, NAME ($ptascii("items")), STATE (PROP_VALUE (ALIAS n_quiet_leaf))}, {DECL eps, NAME ($ptascii("again")), STATE (PROP_VALUE (ALIAS n_quiet_leaf))}]
$node_children(S_quiet_cow, HOBJECT n_quiet_object) = [HCELL n_quiet_leaf, HCELL n_quiet_leaf]
$node_children(S_quiet_cow, HCELL n_quiet_leaf) = [HARRAY n_quiet_array]
H_quiet = $heap_graph(S_quiet_cow)
$heap_owners(H_quiet, HOBJECT n_quiet_object) = 3 /\ $heap_owners(H_quiet, HCELL n_quiet_leaf) = 3
$heap_owners(H_quiet, HARRAY n_quiet_array) = 1 /\ $heap_owners(H_quiet, HARRAY n_quiet_old_array) = 1
$heap_owners(H_quiet, HARRAY n_quiet_child) = 1 /\ $heap_owners(H_quiet, HARRAY n_quiet_old_child) = 1
$heap_owners(H_quiet, HCELL n_quiet_shared) = 3
$heap_valid(H_quiet) /\ $call_descriptors_valid(S_quiet_cow)
S_quiet_full = $drive(S_quiet_cow, 12000)
S_quiet_full.COMPLETION = NORMAL /\ S_quiet_full.TODO = eps /\ S_quiet_full.CURRENT = eps /\ S_quiet_full.FRAMES = eps
~((HOBJECT n_quiet_object) <- S_quiet_full.ALLOCATIONS) /\ ~((HCELL n_quiet_leaf) <- S_quiet_full.ALLOCATIONS) /\ ~((HCELL n_quiet_shared) <- S_quiet_full.ALLOCATIONS)
~((HARRAY n_quiet_array) <- S_quiet_full.ALLOCATIONS) /\ ~((HARRAY n_quiet_old_array) <- S_quiet_full.ALLOCATIONS)
~((HARRAY n_quiet_child) <- S_quiet_full.ALLOCATIONS) /\ ~((HARRAY n_quiet_old_child) <- S_quiet_full.ALLOCATIONS)
S_quiet_full.STORE[n_quiet_private] = DEFINED (PINT 37) /\ S_quiet_full.STORE[n_quiet_source] = DEFINED (PINT 7)
S_quiet_full.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet_original
$string_carrier_valid(S_quiet_full, pvalue_quiet_original)
$heap_valid($heap_graph(S_quiet_full)) /\ $call_descriptors_valid(S_quiet_full)
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
$named_reference_notice_object(S_pre, POBJECT n_object) /\ $positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source /\ n_private =/= n_keeper /\ n_private =/= n_leaf
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]
$named_reference_notice_operand(S_notice, REFERENCE n_private) /\ $error_call_valid(S_notice, perrorcall)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HOBJECT n_object) = 3
$heap_owners(H_notice, HCELL n_leaf) = 3 /\ $heap_owners(H_notice, HARRAY n_array) = 2
$heap_valid(H_notice) /\ $call_descriptors_valid(S_notice)
S_resume = $aaf_seek(S_notice, 3, 6000)[.COMPLETION = NORMAL]
$aaf_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED (POBJECT n_object) /\ S_resume.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_resume.STORE[n_source] = DEFINED (PINT 7) /\ S_resume.STORE[n_snapshot] = DEFINED pvalue_original
S_resume.STORE[n_leaf] = DEFINED (PARRAY n_current_array)
S_resume.STORE[n_outside] = DEFINED (PARRAY n_array)
n_current_array =/= n_array
S_resume.ARRAYS[n_current_array].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_current_child)), ENTRY (KSTRING ($ptascii("shared"))) (ALIAS n_shared)]
S_resume.ARRAYS[n_current_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_current)]
pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_current_string) ($ptascii("23"))
n_current_child =/= n_child /\ n_current_string =/= n_string
S_resume.ARRAYS[n_array].ITEMS = S_pre.ARRAYS[n_array].ITEMS /\ S_resume.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
S_resume.STORE[n_shared] = DEFINED pvalue_current_shared
pvalue_current_shared = PSTRING_CARRIER (REQUEST_STRING n_current_shared_string) ($ptascii("29"))
$string_carrier_valid(S_resume, pvalue_current) /\ $string_carrier_valid(S_resume, pvalue_current_shared) /\ $string_carrier_valid(S_resume, pvalue_original)
$objectprops_record_at(S_resume.OBJECTPROPS, n_object) = (pobjectprops)
$node_children(S_resume, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_resume, HCELL n_leaf) = [HARRAY n_current_array]
$named_reference_notice_object(S_resume, POBJECT n_object) /\ $error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HOBJECT n_object) = 2 /\ $heap_owners(H_resume, HCELL n_private) = 1 /\ $heap_owners(H_resume, HCELL n_leaf) = 3
$heap_owners(H_resume, HARRAY n_current_array) = 1 /\ $heap_owners(H_resume, HARRAY n_array) = 1
$heap_owners(H_resume, HARRAY n_current_child) = 1 /\ $heap_owners(H_resume, HARRAY n_child) = 1 /\ $heap_owners(H_resume, HCELL n_shared) = 3
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_written = $aaf_seek(S_resume, 4, 7000)[.COMPLETION = NORMAL]
$aaf_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_leaf] = DEFINED (PARRAY n_current_array) /\ S_written.STORE[n_outside] = DEFINED (PARRAY n_array)
S_written.ARRAYS[n_current_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT (PSTRING ($ptascii("X3"))))]
S_written.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_original)]
S_written.STORE[n_shared] = DEFINED (PSTRING ($ptascii("28")))
S_written.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_written.OBJECTPROPS, n_object) = (pobjectprops)
$string_carrier_valid(S_written, pvalue_current) /\ $string_carrier_valid(S_written, pvalue_current_shared) /\ $string_carrier_valid(S_written, pvalue_original)
H_written = $heap_graph(S_written)
$heap_owners(H_written, HOBJECT n_object) = 2 /\ $heap_owners(H_written, HCELL n_leaf) = 3
$heap_owners(H_written, HARRAY n_current_array) = 1 /\ $heap_owners(H_written, HARRAY n_array) = 1 /\ $heap_owners(H_written, HCELL n_shared) = 3
$heap_valid(H_written) /\ $call_descriptors_valid(S_written)
S_deleted = $aaf_seek(S_written, 5, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_deleted, 5)
$objectprops_record_at(S_deleted.OBJECTPROPS, n_object) = (pobjectprops_deleted)
pobjectprops_deleted.SLOTS = [ppropertyslot_items[.STATE = PROP_UNSET], ppropertyslot_again]
$node_children(S_deleted, HOBJECT n_object) = [HCELL n_leaf]
H_deleted = $heap_graph(S_deleted)
$heap_owners(H_deleted, HOBJECT n_object) = 2 /\ $heap_owners(H_deleted, HCELL n_leaf) = 2
$heap_valid(H_deleted) /\ $call_descriptors_valid(S_deleted)
S_one_object = $aaf_seek(S_deleted, 6, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_one_object, 6)
S_one_object.STORE[n_private] = DEFINED (PINT 37) /\ S_one_object.STORE[n_keeper] = DEFINED (POBJECT n_object)
H_one_object = $heap_graph(S_one_object)
$heap_owners(H_one_object, HOBJECT n_object) = 1 /\ $heap_owners(H_one_object, HCELL n_leaf) = 2
$heap_valid(H_one_object) /\ $call_descriptors_valid(S_one_object)
S_object_retired = $aaf_seek(S_one_object, 7, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_object_retired, 7)
~((HOBJECT n_object) <- S_object_retired.ALLOCATIONS) /\ ~((HCELL n_keeper) <- S_object_retired.ALLOCATIONS)
H_object_retired = $heap_graph(S_object_retired)
$heap_owners(H_object_retired, HOBJECT n_object) = 0 /\ $heap_owners(H_object_retired, HCELL n_leaf) = 1
$heap_owners(H_object_retired, HARRAY n_current_array) = 1 /\ $heap_owners(H_object_retired, HARRAY n_array) = 1
$heap_valid(H_object_retired) /\ $call_descriptors_valid(S_object_retired)
S_leaf_retired = $aaf_seek(S_object_retired, 8, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_leaf_retired, 8)
~((HCELL n_leaf) <- S_leaf_retired.ALLOCATIONS) /\ ~((HARRAY n_current_array) <- S_leaf_retired.ALLOCATIONS) /\ ~((HARRAY n_current_child) <- S_leaf_retired.ALLOCATIONS)
H_leaf_retired = $heap_graph(S_leaf_retired)
$heap_owners(H_leaf_retired, HARRAY n_current_array) = 0 /\ $heap_owners(H_leaf_retired, HARRAY n_current_child) = 0
$heap_owners(H_leaf_retired, HARRAY n_array) = 1 /\ $heap_owners(H_leaf_retired, HARRAY n_child) = 1 /\ $heap_owners(H_leaf_retired, HCELL n_shared) = 2
$heap_valid(H_leaf_retired) /\ $call_descriptors_valid(S_leaf_retired)
S_outside_retired = $aaf_seek(S_leaf_retired, 10, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_outside_retired, 10)
~((HARRAY n_array) <- S_outside_retired.ALLOCATIONS) /\ ~((HARRAY n_child) <- S_outside_retired.ALLOCATIONS)
H_outside_retired = $heap_graph(S_outside_retired)
$heap_owners(H_outside_retired, HARRAY n_array) = 0 /\ $heap_owners(H_outside_retired, HARRAY n_child) = 0 /\ $heap_owners(H_outside_retired, HCELL n_shared) = 1
$heap_valid(H_outside_retired) /\ $call_descriptors_valid(S_outside_retired)
S_scalar_retired = $aaf_seek(S_outside_retired, 11, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_scalar_retired, 11)
~((HCELL n_shared) <- S_scalar_retired.ALLOCATIONS)
S_full = $drive(S_scalar_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.STORE[n_private] = DEFINED (PINT 37) /\ S_full.STORE[n_source] = DEFINED (PINT 7) /\ S_full.STORE[n_snapshot] = DEFINED pvalue_original
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
S_throw_pending = $aaf_seek(S_throw_notice, 9, 4000)[.COMPLETION = NORMAL]
$aaf_ready(S_throw_pending, 9)
S_throw_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw_pending*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw_pending, perrorcall_entered) /\ $throwable_live(S_throw_pending, n_exception)
H_throw_pending = $heap_graph(S_throw_pending)
$heap_owners(H_throw_pending, HCELL n_throw_private) = 1 /\ $heap_owners(H_throw_pending, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pending, HCELL n_throw_leaf) = 1
$heap_valid(H_throw_pending)
S_cancel = $drive(S_throw_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS) /\ ~((HOBJECT n_throw_object) <- S_cancel.ALLOCATIONS) /\ ~((HCELL n_throw_leaf) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_array) <- S_cancel.ALLOCATIONS) /\ ~((HARRAY n_throw_child) <- S_cancel.ALLOCATIONS)
$heap_owners($heap_graph(S_cancel), HARRAY n_throw_array) = 0 /\ $heap_owners($heap_graph(S_cancel), HARRAY n_throw_child) = 0
$weakref_get(S_cancel, n_throw_weak) = PNULL
$heap_owners($heap_graph(S_cancel), HOBJECT n_throw_object) = 0 /\ $heap_owners($heap_graph(S_cancel), HCELL n_throw_leaf) = 0
S_cancel.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
S_throw_full = $drive(S_cancel, 10000)
S_throw_full.COMPLETION = NORMAL /\ S_throw_full.TODO = eps /\ S_throw_full.CURRENT = eps /\ S_throw_full.FRAMES = eps
S_throw_full.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full.STORE[n_throw_source] = DEFINED (PINT 7) /\ S_throw_full.STORE[n_throw_snapshot] = DEFINED pvalue_throw
$string_carrier_valid(S_throw_full, pvalue_throw) /\ $weakref_get(S_throw_full, n_throw_weak) = PNULL
$heap_valid($heap_graph(S_throw_full)) /\ $call_descriptors_valid(S_throw_full)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object) /\ ~$positional_reference_notice_pending(S_pre)
S_direct = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_object, [ppropertyslot_items[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_again[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_direct, POBJECT n_object) /\ $positional_reference_notice_pending(S_direct)
H_direct = $heap_graph(S_direct)
$heap_owners(H_direct, HCELL n_leaf) = 1 /\ $heap_owners(H_direct, HARRAY n_array) = 2
$heap_valid(H_direct) /\ $call_descriptors_valid(S_direct)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (POBJECT n_object)]
S_fenced.ARRAYS = S_pre.ARRAYS /\ S_fenced.OBJECTPROPS = S_pre.OBJECTPROPS
~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ ~$positional_reference_notice_pending(S_throw_pre)
S_throw_direct = S_throw_pre[.OBJECTPROPS = $objectprops_set(S_throw_pre.OBJECTPROPS, n_throw_object, [{DECL eps, NAME ($ptascii("items")), STATE (PROP_VALUE (DIRECT pvalue_throw))}])]
$named_reference_notice_object(S_throw_direct, POBJECT n_throw_object) /\ $positional_reference_notice_pending(S_throw_direct)
""".strip().splitlines()

CONTROLS = r"""
$update_warning_no_objects($heap_reach([HARRAY n_array], eps, $allocation_edges(S_notice, S_notice.ALLOCATIONS)))
~$named_reference_notice_object_slots(S_notice[.REFCELLS = eps], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_leaf)], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = UNDEFINED], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.PROPREFS = [{CELL n_leaf, SOURCES eps}]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.REFCOERCIONS = [{CELL n_leaf, SITE porigin_call, LINE 0, VALUE eps}]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.CONTAINERINITS = [{CELL n_leaf, ARRAY n_array, SITE porigin_call, LINE 0}]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.LITERALREFRETAINED = [n_leaf]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.LITERALREFDEBTS = [n_leaf]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.NATIVEEXCESS = [HCELL n_leaf]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.LITERALARRAYRETAINED = [n_array]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.LITERALARRAYDEBTS = [n_array]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.NATIVEEXCESS = [HARRAY n_array]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.LITERALARRAYRETAINED = [n_child]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.NATIVEEXCESS = [HCELL n_shared]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.PROPREFS = [{CELL n_shared, SOURCES eps}]], [ppropertyslot_items])
S_pooled = S_notice[.POOLS = S_notice.POOLS ++ [{UNIT 0, CONSTANTS [PCONSTANT eps (PARRAY n_array)]}]]
(HARRAY n_array) <- $heap_reach($pools_nodes(S_pooled.POOLS), eps, $allocation_edges(S_pooled, S_pooled.ALLOCATIONS))
~$named_reference_notice_object_slots(S_pooled, [ppropertyslot_items])
S_pooled_child = S_notice[.POOLS = S_notice.POOLS ++ [{UNIT 0, CONSTANTS [PCONSTANT eps (PARRAY n_child)]}]]
~$named_reference_notice_object_slots(S_pooled_child, [ppropertyslot_items])
S_immutable = S_notice[.ARRAYS[n_array] = $array_empty()][.GC.IMMUTABLE = [n_array]]
$array_immutable(S_immutable, n_array)
~$named_reference_notice_object_slots(S_immutable, [ppropertyslot_items])
S_object_cycle = S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("back"))) (DIRECT (POBJECT n_object))]]
~$update_warning_no_objects($heap_reach([HARRAY n_array], eps, $allocation_edges(S_object_cycle, S_object_cycle.ALLOCATIONS)))
~$named_reference_notice_object_slots(S_object_cycle, [ppropertyslot_items])
S_array_cycle = S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("back"))) (DIRECT (PARRAY n_array))]]
$update_warning_no_objects($heap_reach([HARRAY n_array], eps, $allocation_edges(S_array_cycle, S_array_cycle.ALLOCATIONS)))
~$named_reference_notice_object_slots(S_array_cycle, [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.STORE[n_leaf] = DEFINED (POBJECT n_object)], [ppropertyslot_items])
pvalue_bad_id = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ($ptascii("17"))
pvalue_bad_bytes = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("18"))
~$named_reference_notice_object_slots(S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_bad_id)]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_bad_bytes)]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice[.STORE[n_shared] = DEFINED (PSTRING ($ptascii("19")))], [ppropertyslot_items])
S_nul = S_notice[.STRINGDATA = S_notice.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S_notice.STRINGDATA|)) ([0])
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_object_slots(S_nul[.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_nul)]], [ppropertyslot_items])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_items[.NAME = [0]]])
~$named_reference_notice_object_slots(S_notice, [ppropertyslot_items[.DECL = (INTERNAL_PROPERTY "stdClass" ($ptascii("items")))]])
~$named_reference_notice_object(S_notice[.OBJECTTABLES = [{OBJECT n_object, TABLE 0}]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.NATIVEEXCESS = [HOBJECT n_object]], POBJECT n_object)
~$named_reference_notice_object(S_notice[.GC.WORKER = (0)], POBJECT n_object)
~$named_reference_notice_object(S_written, POBJECT n_object)
~$positional_reference_notice_source(S_pre, pcalltarget, 0, eps)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_retired = $drive(S_leaf_retired, 0)
S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_leaf_retired
$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_leaf_retired, 2)
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
        reached += ['$aaf_output(S_full.EVENTS) = $ptascii(' + json.dumps(cases[0]['native_stdout']) + ')', '$aaf_output(S_throw_full.EVENTS) = $ptascii(' + json.dumps(cases[1]['native_stdout']) + ')']
        derived = CONTROLS
    reached += [initial('S_quiet_initial', 2)] + QUIET
    reached.append('$aaf_output(S_quiet_full.EVENTS) = $ptascii(' + json.dumps(cases[2]['native_stdout']) + ')')
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'stdclass-alias-array-field-front' if args.front else 'stdclass-alias-array-field-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
