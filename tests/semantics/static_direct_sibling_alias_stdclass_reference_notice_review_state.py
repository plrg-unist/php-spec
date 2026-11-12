#!/usr/bin/env python3
"""Ground actual quiet DIRECT static roots at the selected reference Notice boundary."""
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




dec $sopn_stage(pstate, nat) : bool
def $sopn_stage(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;")
def $sopn_stage(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;")
def $sopn_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;E;H;F;")
def $sopn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1:5;1;T:Cannot assign int to reference held by property ReviewStaticDirect27::$s of type stdClass;P;")
def $sopn_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1:5;1;T:Cannot assign int to reference held by property ReviewStaticDirect27::$s of type stdClass;P;41:41;N;Q;K;1:1:47:7:5;W:1:")
def $sopn_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if $sopn_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1:5;1;T:Cannot assign int to reference held by property ReviewStaticDirect27::$s of type stdClass;P;41:41;N;Q;K;1:1:47:7:5;W:1:1;")
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
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("old")) = eps
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_class
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_r, ppropertydesc_s, ppropertydesc_q]
ppropertydesc_r.ORIGIN = ppropertyid_r
ppropertydesc_s.ORIGIN = ppropertyid_s
ppropertydesc_q.ORIGIN = ppropertyid_q
ppropertydesc_r.STATIC /\ ppropertydesc_s.STATIC /\ ppropertydesc_q.STATIC
ppropertydesc_r.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
ppropertydesc_s.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
ppropertydesc_q.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
~((INSTANCE porigin_class) <- S_pre.OBJECTS)
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_s]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_r) = (ppropertydesc_r)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_s) = (ppropertydesc_s)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_q) = (ppropertydesc_q)
S_pre.CLASSSTATICS = [{DECL ppropertyid_r, STATE PROP_VALUE (DIRECT (POBJECT n_old))}, {DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)}, {DECL ppropertyid_q, STATE PROP_VALUE (DIRECT (POBJECT n_old))}]
$class_static_roots(S_pre.CLASSSTATICS) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object(S_pre, POBJECT n_new)
$named_reference_notice_object_ancestors(S_pre, [n_root])
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
$reference_coercion_at(S_pre.REFCOERCIONS, n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf) /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HCELL n_leaf) = 3 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_old) = 3 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $class_statics_valid(S_pre) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
$named_reference_notice_object_static_slot(S_pre, n_leaf, ppropertyid_s, PROP_VALUE (ALIAS n_leaf))
$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_s])
'''.strip().splitlines()

PROTOCOL = r'''
~$named_reference_notice_object_static_slot(S_pre, n_leaf, ppropertyid_r, PROP_VALUE (DIRECT (POBJECT n_old)))
~$named_reference_notice_object_static_slot(S_pre, n_leaf, ppropertyid_q, PROP_VALUE (DIRECT (POBJECT n_old)))
~$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_object_static_sources(S_pre, n_leaf, ppropref.SOURCES)
~$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

POST = r'''
$named_reference_notice_object_static_slot(S_pre, n_leaf, ppropertyid_r, PROP_VALUE (DIRECT (POBJECT n_old)))
$named_reference_notice_object_static_slot(S_pre, n_leaf, ppropertyid_q, PROP_VALUE (DIRECT (POBJECT n_old)))
$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
$named_reference_notice_object_static_sources(S_pre, n_leaf, ppropref.SOURCES)
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
S_swapped.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_swapped.PROPREFS, n_leaf) = (ppropref)
$class_static_roots(S_swapped.CLASSSTATICS) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$node_children(S_swapped, HCELL n_leaf) = [HOBJECT n_new]
H_swapped = $heap_graph(S_swapped)
H_swapped = $heap_graph(S_swapped[.PROPREFS = eps])
$heap_owners(H_swapped, HOBJECT n_old) = 2 /\ $heap_owners(H_swapped, HOBJECT n_new) = 2
$proprefs_valid(S_swapped) /\ $class_statics_valid(S_swapped)
S_failed = $sopn_after(S_swapped, 1, 768)
$sopn_stage(S_failed, 1)
S_failed.PROPREFS = S_swapped.PROPREFS /\ S_failed.CLASSSTATICS = S_pre.CLASSSTATICS
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
S_returned.PROPREFS = S_pre.PROPREFS
$class_static_roots(S_returned.CLASSSTATICS) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
H_returned = $heap_graph(S_returned)
H_returned = $heap_graph(S_returned[.PROPREFS = eps])
$heap_owners(H_returned, HCELL n_leaf) = 3
$heap_owners(H_returned, HARRAY n_root) = 2 /\ $heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2 /\ $heap_owners(H_returned, HOBJECT n_new) = 2
$duplicate_item(S_returned, n_copied, ALIAS n_leaf) = ALIAS n_leaf
S_transfer = $sopn_after(S_returned, 3, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_transfer, 3)
$propref_at(S_transfer.PROPREFS, n_leaf) = eps
$propref_at(S_transfer.PROPREFS, n_new_cv) = ({CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s])})
$class_static_roots(S_transfer.CLASSSTATICS) = [HOBJECT n_old, HCELL n_new_cv, HOBJECT n_old]
H_transfer = $heap_graph(S_transfer)
H_transfer = $heap_graph(S_transfer[.PROPREFS = eps])
$heap_owners(H_transfer, HCELL n_leaf) = 2 /\ $heap_owners(H_transfer, HCELL n_new_cv) = 2
$heap_owners(H_transfer, HOBJECT n_old) = 2 /\ $heap_owners(H_transfer, HOBJECT n_new) = 2
$proprefs_valid(S_transfer) /\ $class_statics_valid(S_transfer)
S_one_root = $sopn_after(S_transfer, 4, 2048)[.COMPLETION = NORMAL]
$sopn_stage(S_one_root, 4)
S_one_root.STORE[n_leaf] = DEFINED PNULL
$class_static_roots(S_one_root.CLASSSTATICS) = [HOBJECT n_new, HCELL n_new_cv, HOBJECT n_old]
H_one_root = $heap_graph(S_one_root)
H_one_root = $heap_graph(S_one_root[.PROPREFS = eps])
$heap_owners(H_one_root, HOBJECT n_old) = 1 /\ $heap_owners(H_one_root, HOBJECT n_new) = 2
S_both_roots = $sopn_after(S_one_root, 5, 768)[.COMPLETION = NORMAL]
$sopn_stage(S_both_roots, 5)
$class_static_roots(S_both_roots.CLASSSTATICS) = [HOBJECT n_new, HCELL n_new_cv, HOBJECT n_new]
~((HOBJECT n_old) <- S_both_roots.ALLOCATIONS)
H_both_roots = $heap_graph(S_both_roots)
H_both_roots = $heap_graph(S_both_roots[.PROPREFS = eps])
$heap_owners(H_both_roots, HOBJECT n_new) = 3
$proprefs_valid(S_both_roots) /\ $class_statics_valid(S_both_roots)
'''.strip().splitlines()

CONTROLS = r'''
S_distinct = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_q, PROP_VALUE (DIRECT (POBJECT n_new)))]
$proprefs_valid(S_distinct) /\ $class_statics_valid(S_distinct)
$class_static_roots(S_distinct.CLASSSTATICS) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_new]
~$propref_source_present(S_distinct.PROPREFS, n_leaf, CLASS_PROP_SOURCE ppropertyid_q)
$named_reference_notice_array(S_distinct, PARRAY n_root)
S_other_cell = $reference_cell(S_pre, n_new_cv)[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_q, PROP_VALUE (ALIAS n_new_cv))][.PROPREFS = S_pre.PROPREFS ++ [{CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_q])}]]
$proprefs_valid(S_other_cell) /\ $class_statics_valid(S_other_cell)
$propref_source_valid(S_other_cell, n_new_cv, CLASS_PROP_SOURCE ppropertyid_q)
~$named_reference_notice_array(S_other_cell, PARRAY n_root)
S_stale = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid_q])}]]
~$propref_source_valid(S_stale, n_leaf, CLASS_PROP_SOURCE ppropertyid_q)
~$named_reference_notice_array(S_stale, PARRAY n_root)
S_selected_direct = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_s, PROP_VALUE (DIRECT (POBJECT n_old)))]
$named_reference_notice_object_static_slot(S_selected_direct, n_leaf, ppropertyid_s, PROP_VALUE (DIRECT (POBJECT n_old)))
~$propref_source_valid(S_selected_direct, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
~$named_reference_notice_array(S_selected_direct, PARRAY n_root)
S_missing = S_pre[.CLASSSTATICS = [{DECL ppropertyid_r, STATE PROP_VALUE (DIRECT (POBJECT n_old))}, {DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)}]]
~$named_reference_notice_array(S_missing, PARRAY n_root)
S_owning = S_distinct[.OBJECTPROPS = $objectprops_set(S_distinct.OBJECTPROPS, n_new, [{DECL eps, NAME ($ptascii("v")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}])]
$named_reference_notice_object(S_owning, POBJECT n_old) /\ ~$named_reference_notice_object(S_owning, POBJECT n_new)
~$named_reference_notice_array(S_owning, PARRAY n_root)
S_unallocated = S_distinct[.ALLOCATIONS = $call_remove_owner(S_distinct.ALLOCATIONS, HOBJECT n_new)]
~$named_reference_notice_array(S_unallocated, PARRAY n_root)
S_cached = S_distinct[.OBJECTTABLES = [{OBJECT n_new, TABLE n_root}]]
~$named_reference_notice_array(S_cached, PARRAY n_root)
S_unit = S_distinct[.NATIVEEXCESS = [HOBJECT n_new]]
~$named_reference_notice_array(S_unit, PARRAY n_root)
S_called = S_distinct[.DESTRUCTION.CALLED = [n_new]]
~$named_reference_notice_array(S_called, PARRAY n_root)
S_materialized_child = $objectprops_mark(S_distinct, n_new)
$objectprops_record_at(S_materialized_child.OBJECTPROPS, n_new) = (pobjectprops_materialized)
pobjectprops_materialized.MATERIALIZED
$objectprops_valid(S_materialized_child, S_materialized_child.OBJECTPROPS)
$named_reference_notice_array(S_materialized_child, PARRAY n_root)
S_scalar = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_q, PROP_VALUE (DIRECT (PINT 7)))]
~$named_reference_notice_array(S_scalar, PARRAY n_root)
S_unset = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_q, PROP_UNSET)]
~$named_reference_notice_array(S_unset, PARRAY n_root)
S_nullable = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_s, ppropertydesc_q[.TYPE = [(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_default = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_s, ppropertydesc_q[.DEFAULT = PROP_LITERAL (POBJECT n_old)]]]]]
~$named_reference_notice_array(S_default, PARRAY n_root)
S_setter = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_s, ppropertydesc_q[.SETVISIBILITY = (PROPERTY_PRIVATE)]]]]]
~$named_reference_notice_array(S_setter, PARRAY n_root)
S_readonly = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_s, ppropertydesc_q[.READONLY = true]]]]]
~$named_reference_notice_array(S_readonly, PARRAY n_root)
S_final = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_r, ppropertydesc_s, ppropertydesc_q[.FINAL = true]]]]]
~$named_reference_notice_array(S_final, PARRAY n_root)
S_foreign_row = S_pre[.CLASSSTATICS = [{DECL ppropertyid_r, STATE PROP_VALUE (DIRECT (POBJECT n_old))}, {DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)}, {DECL ppropertyid_r, STATE PROP_VALUE (DIRECT (POBJECT n_old))}]]
~$named_reference_notice_array(S_foreign_row, PARRAY n_root)
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
    catalogue = Path(__file__).with_name('static_direct_sibling_alias_stdclass_reference_notice_review_cases.json')
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
    reached = REACHED + (POST if args.part == 'checkpoint' else POST[:7] if args.part == 'post' else [])
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
