#!/usr/bin/env python3
"""Ground deep shared object fields, repeated child edges and quiet WeakReference cleanup before Notices."""
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
CATALOGUE = Path(__file__).with_name('stdclass_direct_object_field_reference_notice_cases.json')

PREFIX = r"""
dec $dof_output(pevent*) : ptbytes
def $dof_output(eps) = eps
def $dof_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dof_output(pevent*)
dec $dof_ready(pstate, nat) : bool
def $dof_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("StdClassDirectObjectNotice46\\make") \/ pcallcontext.NAME = $ptascii("StdClassDirectObjectThrow46\\make")
def $dof_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("StdClassDirectObjectNotice46\\take") \/ pfunction.NAME = $ptascii("StdClassDirectObjectThrow46\\take")
def $dof_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $dof_output(S.EVENTS) = $ptascii("K;M:1:1;F:1:1;R:Y8:Y8:Y8:Y8:1:1;")
def $dof_ready(S, n_stage) = false -- otherwise
dec $dof_seek(pstate, nat, nat) : pstate
def $dof_seek(S, n_stage, n) = S
  -- if $dof_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $dof_seek(S, n_stage, n) = $dof_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$dof_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $dof_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $dof_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$dof_ready(S_return, 0)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("StdClassDirectObjectNotice46\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
$lookup(S_return.ENV, $ptascii("input")) = (n_source)
S_return.STORE[n_source] = DEFINED (POBJECT n_object)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(psymboltable_caller.ENV, $ptascii("mid")) = (n_mid_cv)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_old_cv)
$lookup(psymboltable_caller.ENV, $ptascii("next")) = (n_next_cv)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
S_return.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_return.STORE[n_mid_cv] = DEFINED (POBJECT n_middle)
S_return.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_return.STORE[n_next_cv] = DEFINED (POBJECT n_next)
n_object =/= n_middle /\ n_middle =/= n_old /\ n_next =/= n_old /\ n_next =/= n_middle /\ n_next =/= n_object
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops_root)
pobjectprops_root.SLOTS = [ppropertyslot_first, ppropertyslot_second]
ppropertyslot_first = {DECL eps, NAME ($ptascii("first")), STATE (PROP_VALUE (DIRECT (POBJECT n_middle)))}
ppropertyslot_second = {DECL eps, NAME ($ptascii("second")), STATE (PROP_VALUE (DIRECT (POBJECT n_middle)))}
$objectprops_record_at(S_return.OBJECTPROPS, n_middle) = (pobjectprops_middle)
pobjectprops_middle.SLOTS = [ppropertyslot_left, ppropertyslot_right]
ppropertyslot_left = {DECL eps, NAME ($ptascii("left")), STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}
ppropertyslot_right = {DECL eps, NAME ($ptascii("right")), STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}
$objectprops_record_at(S_return.OBJECTPROPS, n_old) = (pobjectprops_old)
pobjectprops_old.SLOTS = [ppropertyslot_old_value]
ppropertyslot_old_value = {DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}
$objectprops_record_at(S_return.OBJECTPROPS, n_next) = (pobjectprops_next)
pobjectprops_next.SLOTS = [ppropertyslot_next_value]
ppropertyslot_next_value.STATE = PROP_VALUE (DIRECT pvalue_next)
pvalue_next = PSTRING_CARRIER (REQUEST_STRING n_next_string) ($ptascii("31"))
$string_carrier_valid(S_return, pvalue_next)
$objectprops_valid(S_return, [pobjectprops_root, pobjectprops_middle, pobjectprops_old, pobjectprops_next])
$node_children(S_return, HOBJECT n_object) = [HOBJECT n_middle, HOBJECT n_middle]
$node_children(S_return, HOBJECT n_middle) = [HOBJECT n_old, HOBJECT n_old]
$node_children(S_return, HOBJECT n_old) = eps /\ $node_children(S_return, HOBJECT n_next) = eps
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source) = 3 /\ $heap_owners(H_return, HOBJECT n_object) = 3
$heap_owners(H_return, HOBJECT n_middle) = 3 /\ $heap_owners(H_return, HOBJECT n_old) = 3 /\ $heap_owners(H_return, HOBJECT n_next) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $dof_seek(S_after_return, 1, 5000)[.COMPLETION = NORMAL]
$dof_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
S_pre.STORE[n_mid_cv] = DEFINED (POBJECT n_middle) /\ S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old) /\ S_pre.STORE[n_next_cv] = DEFINED (POBJECT n_next)
S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_root)
$objectprops_record_at(S_pre.OBJECTPROPS, n_middle) = (pobjectprops_middle)
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
$objectprops_record_at(S_pre.OBJECTPROPS, n_next) = (pobjectprops_next)
S_pre.OBJECTS[n_object] = STDINSTANCE /\ S_pre.OBJECTS[n_middle] = STDINSTANCE /\ S_pre.OBJECTS[n_old] = STDINSTANCE /\ S_pre.OBJECTS[n_next] = STDINSTANCE
$named_reference_notice_object(S_pre, POBJECT n_old) /\ $named_reference_notice_object(S_pre, POBJECT n_next)
$node_children(S_pre, HOBJECT n_object) = [HOBJECT n_middle, HOBJECT n_middle]
$node_children(S_pre, HOBJECT n_middle) = [HOBJECT n_old, HOBJECT n_old]
$property_release_nodes(pobjectprops_root.SLOTS) = [HOBJECT n_middle, HOBJECT n_middle]
$property_release_nodes(pobjectprops_middle.SLOTS) = [HOBJECT n_old, HOBJECT n_old]
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps /\ S_pre.CONTAINERINITS = eps
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps /\ $object_table_at(S_pre.OBJECTTABLES, n_middle) = eps
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
~$weakmap_key_waiting(S_pre, n_object) /\ ~$weakmap_key_waiting(S_pre, n_middle)
$heap_count(HOBJECT n_object, S_pre.NATIVEEXCESS) = 0 /\ $heap_count(HOBJECT n_middle, S_pre.NATIVEEXCESS) = 0
$dof_output(S_pre.EVENTS) = $ptascii("A;M:1:1;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source) = 2 /\ $heap_owners(H_pre, HOBJECT n_object) = 3
$heap_owners(H_pre, HOBJECT n_middle) = 3 /\ $heap_owners(H_pre, HOBJECT n_old) = 3 /\ $heap_owners(H_pre, HOBJECT n_next) = 1
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

THROW = r"""
S_throw_return = $dof_seek(S_throw_initial, 0, 5000)[.COMPLETION = NORMAL]
$dof_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("StdClassDirectObjectThrow46\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (POBJECT n_throw_object)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_object) = (pobjectprops_throw_root)
pobjectprops_throw_root.SLOTS = [ppropertyslot_throw_first, ppropertyslot_throw_second]
ppropertyslot_throw_first.STATE = PROP_VALUE (DIRECT (POBJECT n_throw_middle))
ppropertyslot_throw_second.STATE = PROP_VALUE (DIRECT (POBJECT n_throw_middle))
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_middle) = (pobjectprops_throw_middle)
pobjectprops_throw_middle.SLOTS = [ppropertyslot_throw_left, ppropertyslot_throw_right]
ppropertyslot_throw_left.STATE = PROP_VALUE (DIRECT (POBJECT n_throw_leaf))
ppropertyslot_throw_right.STATE = PROP_VALUE (DIRECT (POBJECT n_throw_leaf))
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_leaf) = (pobjectprops_throw_leaf)
pobjectprops_throw_leaf.SLOTS = [ppropertyslot_throw_value]
ppropertyslot_throw_value.STATE = PROP_VALUE (DIRECT pvalue_throw)
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_return, pvalue_throw)
S_throw_return.GLOBALTABLE = (psymboltable_throw)
$lookup(psymboltable_throw.ENV, $ptascii("mid")) = eps /\ $lookup(psymboltable_throw.ENV, $ptascii("leaf")) = eps
$lookup(psymboltable_throw.ENV, $ptascii("snapshot")) = (n_throw_snapshot)
S_throw_return.STORE[n_throw_snapshot] = DEFINED pvalue_throw
$lookup(psymboltable_throw.ENV, $ptascii("wRoot")) = (n_throw_root_cv)
$lookup(psymboltable_throw.ENV, $ptascii("wMid")) = (n_throw_mid_cv)
$lookup(psymboltable_throw.ENV, $ptascii("wLeaf")) = (n_throw_leaf_cv)
S_throw_return.STORE[n_throw_root_cv] = DEFINED (POBJECT n_throw_root_weak)
S_throw_return.STORE[n_throw_mid_cv] = DEFINED (POBJECT n_throw_mid_weak)
S_throw_return.STORE[n_throw_leaf_cv] = DEFINED (POBJECT n_throw_leaf_weak)
S_throw_return.OBJECTS[n_throw_root_weak] = WEAKREFERENCE (n_throw_object)
S_throw_return.OBJECTS[n_throw_mid_weak] = WEAKREFERENCE (n_throw_middle)
S_throw_return.OBJECTS[n_throw_leaf_weak] = WEAKREFERENCE (n_throw_leaf)
S_throw_after_return = $drive(S_throw_return, 1)[.COMPLETION = NORMAL]
H_throw_return = $heap_graph(S_throw_after_return)
$heap_owners(H_throw_return, HOBJECT n_throw_object) = 2 /\ $heap_owners(H_throw_return, HOBJECT n_throw_middle) = 2 /\ $heap_owners(H_throw_return, HOBJECT n_throw_leaf) = 2
$heap_valid(H_throw_return)
S_throw_pre = $dof_seek(S_throw_after_return, 1, 5000)[.COMPLETION = NORMAL]
$dof_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (POBJECT n_throw_object)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps
$node_children(S_throw_pre, HOBJECT n_throw_object) = [HOBJECT n_throw_middle, HOBJECT n_throw_middle]
$node_children(S_throw_pre, HOBJECT n_throw_middle) = [HOBJECT n_throw_leaf, HOBJECT n_throw_leaf]
$node_children(S_throw_pre, HOBJECT n_throw_leaf) = eps
$named_reference_notice_object(S_throw_pre, POBJECT n_throw_leaf)
$objectprops_valid(S_throw_pre, [pobjectprops_throw_root, pobjectprops_throw_middle, pobjectprops_throw_leaf])
S_throw_pre.PARAMETERBACKINGS = eps /\ S_throw_pre.PROPREFS = eps /\ S_throw_pre.REFCOERCIONS = eps /\ S_throw_pre.CONTAINERINITS = eps
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$dof_output(S_throw_pre.EVENTS) = $ptascii("T;M;")
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pre, HOBJECT n_throw_middle) = 2 /\ $heap_owners(H_throw_pre, HOBJECT n_throw_leaf) = 2
$heap_valid(H_throw_pre) /\ $call_descriptors_valid(S_throw_pre)
""".strip().splitlines()

QUIET = r"""
S_quiet_shared = $dof_seek(S_quiet_initial, 2, 10000)[.COMPLETION = NORMAL]
$dof_ready(S_quiet_shared, 2)
~$error_handler_eligible(S_quiet_shared, 8)
$lookup(S_quiet_shared.ENV, $ptascii("r")) = (n_quiet_private)
$lookup(S_quiet_shared.ENV, $ptascii("source")) = (n_quiet_source)
$lookup(S_quiet_shared.ENV, $ptascii("sourceAlias")) = (n_quiet_source)
$lookup(S_quiet_shared.ENV, $ptascii("keeper")) = (n_quiet_keeper)
$lookup(S_quiet_shared.ENV, $ptascii("mid")) = (n_quiet_mid_cv)
$lookup(S_quiet_shared.ENV, $ptascii("leaf")) = (n_quiet_old_cv)
$lookup(S_quiet_shared.ENV, $ptascii("next")) = (n_quiet_next_cv)
$lookup(S_quiet_shared.ENV, $ptascii("snapshot")) = (n_quiet_snapshot)
S_quiet_shared.STORE[n_quiet_private] = DEFINED (POBJECT n_quiet_object)
S_quiet_shared.STORE[n_quiet_source] = DEFINED (POBJECT n_quiet_object) /\ S_quiet_shared.STORE[n_quiet_keeper] = DEFINED (POBJECT n_quiet_object)
S_quiet_shared.STORE[n_quiet_mid_cv] = DEFINED (POBJECT n_quiet_middle)
S_quiet_shared.STORE[n_quiet_old_cv] = DEFINED (POBJECT n_quiet_old)
S_quiet_shared.STORE[n_quiet_next_cv] = DEFINED (POBJECT n_quiet_next)
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_object) = (pobjectprops_quiet_root)
pobjectprops_quiet_root.SLOTS = [{DECL eps, NAME ($ptascii("first")), STATE (PROP_VALUE (DIRECT (POBJECT n_quiet_middle)))}, {DECL eps, NAME ($ptascii("second")), STATE (PROP_VALUE (DIRECT (POBJECT n_quiet_middle)))}]
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_middle) = (pobjectprops_quiet_middle)
pobjectprops_quiet_middle.SLOTS = [{DECL eps, NAME ($ptascii("left")), STATE (PROP_VALUE (DIRECT (POBJECT n_quiet_old)))}, {DECL eps, NAME ($ptascii("right")), STATE (PROP_VALUE (DIRECT (POBJECT n_quiet_old)))}]
$objectprops_record_at(S_quiet_shared.OBJECTPROPS, n_quiet_old) = (pobjectprops_quiet_old)
pobjectprops_quiet_old.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("Y8")))))}]
S_quiet_shared.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet_original
pvalue_quiet_original = PSTRING_CARRIER (REQUEST_STRING n_quiet_string) ($ptascii("17"))
$string_carrier_valid(S_quiet_shared, pvalue_quiet_original)
$node_children(S_quiet_shared, HOBJECT n_quiet_object) = [HOBJECT n_quiet_middle, HOBJECT n_quiet_middle]
$node_children(S_quiet_shared, HOBJECT n_quiet_middle) = [HOBJECT n_quiet_old, HOBJECT n_quiet_old]
$node_children(S_quiet_shared, HOBJECT n_quiet_old) = eps
$lookup(S_quiet_shared.ENV, $ptascii("wRoot")) = (n_quiet_root_cv)
$lookup(S_quiet_shared.ENV, $ptascii("wMid")) = (n_quiet_mid_weak_cv)
$lookup(S_quiet_shared.ENV, $ptascii("wOld")) = (n_quiet_old_weak_cv)
$lookup(S_quiet_shared.ENV, $ptascii("wNext")) = (n_quiet_next_weak_cv)
S_quiet_shared.STORE[n_quiet_root_cv] = DEFINED (POBJECT n_quiet_root_weak)
S_quiet_shared.STORE[n_quiet_mid_weak_cv] = DEFINED (POBJECT n_quiet_mid_weak)
S_quiet_shared.STORE[n_quiet_old_weak_cv] = DEFINED (POBJECT n_quiet_old_weak)
S_quiet_shared.STORE[n_quiet_next_weak_cv] = DEFINED (POBJECT n_quiet_next_weak)
$weakref_get(S_quiet_shared, n_quiet_root_weak) = POBJECT n_quiet_object
$weakref_get(S_quiet_shared, n_quiet_mid_weak) = POBJECT n_quiet_middle
$weakref_get(S_quiet_shared, n_quiet_old_weak) = POBJECT n_quiet_old
$weakref_get(S_quiet_shared, n_quiet_next_weak) = POBJECT n_quiet_next
H_quiet = $heap_graph(S_quiet_shared)
$heap_owners(H_quiet, HOBJECT n_quiet_object) = 3 /\ $heap_owners(H_quiet, HOBJECT n_quiet_middle) = 3
$heap_owners(H_quiet, HOBJECT n_quiet_old) = 3 /\ $heap_owners(H_quiet, HOBJECT n_quiet_next) = 1
$heap_valid(H_quiet) /\ $call_descriptors_valid(S_quiet_shared)
S_quiet_full = $drive(S_quiet_shared, 15000)
S_quiet_full.COMPLETION = NORMAL /\ S_quiet_full.TODO = eps /\ S_quiet_full.CURRENT = eps /\ S_quiet_full.FRAMES = eps
~((HOBJECT n_quiet_object) <- S_quiet_full.ALLOCATIONS) /\ ~((HOBJECT n_quiet_middle) <- S_quiet_full.ALLOCATIONS)
~((HOBJECT n_quiet_old) <- S_quiet_full.ALLOCATIONS) /\ ~((HOBJECT n_quiet_next) <- S_quiet_full.ALLOCATIONS)
$weakref_get(S_quiet_full, n_quiet_root_weak) = PNULL /\ $weakref_get(S_quiet_full, n_quiet_mid_weak) = PNULL
$weakref_get(S_quiet_full, n_quiet_old_weak) = PNULL /\ $weakref_get(S_quiet_full, n_quiet_next_weak) = PNULL
S_quiet_full.STORE[n_quiet_private] = DEFINED (PINT 37) /\ S_quiet_full.STORE[n_quiet_source] = DEFINED (PINT 7)
S_quiet_full.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet_original
$string_carrier_valid(S_quiet_full, pvalue_quiet_original)
$heap_valid($heap_graph(S_quiet_full)) /\ $call_descriptors_valid(S_quiet_full)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops_root.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object) /\ ~$named_reference_notice_object(S_pre, POBJECT n_middle)
~$positional_reference_notice_pending(S_pre)
S_flat_middle = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_middle, [ppropertyslot_left[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_right[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_flat_middle, POBJECT n_middle)
~$named_reference_notice_object(S_flat_middle, POBJECT n_object)
S_flat_root = S_flat_middle[.OBJECTPROPS = $objectprops_set(S_flat_middle.OBJECTPROPS, n_object, [ppropertyslot_first[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_second[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_flat_root, POBJECT n_object) /\ $positional_reference_notice_pending(S_flat_root)
H_flat = $heap_graph(S_flat_root)
$heap_owners(H_flat, HOBJECT n_middle) = 1 /\ $heap_owners(H_flat, HOBJECT n_old) = 1
$heap_owners(H_flat, HOBJECT n_object) = 3 /\ $heap_owners(H_flat, HOBJECT n_next) = 1
$heap_valid(H_flat) /\ $call_descriptors_valid(S_flat_root)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (POBJECT n_object)]
S_fenced.OBJECTPROPS = S_pre.OBJECTPROPS
~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ ~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_middle)
~$positional_reference_notice_pending(S_throw_pre)
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    assert args.front
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
    reached = [initial('S_initial', 0)] + RETURN + COMMON + [initial('S_throw_initial', 1)] + THROW + [initial('S_quiet_initial', 2)] + QUIET
    reached.append('$dof_output(S_quiet_full.EVENTS) = $ptascii(' + json.dumps(cases[2]['native_stdout']) + ')')
    derived = FRONT
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'stdclass-direct-object-field-front', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
