#!/usr/bin/env python3
"""Isolate the genuine fresh instance hole and the exact-declaration owner fence."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $mchn_output(pevent*) : ptbytes
def $mchn_output(eps) = eps
def $mchn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mchn_output(pevent*)
dec $mchn_ready(pstate) : bool
def $mchn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $mchn_output(S.EVENTS) = $ptascii("R;")
def $mchn_ready(S) = false -- otherwise
dec $mchn_seek(pstate, nat) : pstate
def $mchn_seek(S, n) = S
  -- if $mchn_ready(S) \/ n = 0 \/ S.TODO = eps
def $mchn_seek(S, n) = $mchn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$mchn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mchn_seek(S, n) = S -- otherwise

'''

REACHED = r'''
S_pre = $mchn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$mchn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("owner")) = (n_owner_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_owner_cv] = DEFINED (POBJECT n_owner)
S_pre.OBJECTS[n_owner] = INSTANCE porigin_class
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_class
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_s, ppropertydesc_q, ppropertydesc_p]
ppropertydesc_s.STATIC /\ ~ppropertydesc_q.STATIC /\ ~ppropertydesc_p.STATIC
ppropertydesc_s.ORIGIN = ppropertyid_s
ppropertydesc_p.ORIGIN = ppropertyid_p
ppropertydesc_q.ORIGIN = ppropertyid_q
ppropertyid_s =/= ppropertyid_p /\ ppropertyid_q =/= ppropertyid_p /\ ppropertyid_q =/= ppropertyid_s
$property_declaring_class(S_pre.CLASSES, ppropertyid_s) = (porigin_class)
$property_declaring_class(S_pre.CLASSES, ppropertyid_p) = (porigin_class)
$property_declaring_class(S_pre.CLASSES, ppropertyid_q) = (porigin_class)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_s) = (ppropertydesc_s)
$objectprops_record_at(S_pre.OBJECTPROPS, n_owner) = (pobjectprops_owner)
pobjectprops_owner.SLOTS = [{DECL (ppropertyid_q), NAME ($ptascii("q")), STATE PROP_INITIAL}, {DECL (ppropertyid_p), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}]
~pobjectprops_owner.MATERIALIZED /\ $objectprops_valid(S_pre, [pobjectprops_owner])
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_s) = ({DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)})
S_pre.CLASSSTATICS = [{DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)}]
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_s, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$node_children(S_pre, HOBJECT n_owner) = [HCELL n_leaf]
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$object_table_at(S_pre.OBJECTTABLES, n_owner) = eps
~$instance_storage_freeing(S_pre, n_owner) /\ ~(n_owner <- S_pre.DESTRUCTION.CALLED)
$heap_count(HOBJECT n_owner, S_pre.NATIVEEXCESS) = 0
~$weakmap_key_waiting(S_pre, n_owner)
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
$heap_owners(H_pre, HCELL n_leaf) = 4 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_owner) = 1
$heap_owners(H_pre, HOBJECT n_old) = 2 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_owner) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$class_statics_valid(S_pre) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS)
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''
$named_reference_notice_object_property_slots(S_pre, n_leaf, n_owner, pclassdesc.PROPERTIES, pobjectprops_owner.SLOTS) = ([HCELL n_leaf])
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_s, ppropertydesc_p])
$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_p, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner_source(S_pre, n_leaf, ppropertydesc_q, ppropref.SOURCES)
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_q])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
~$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
~$named_reference_notice_object_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_object_property_owner_source(S_pre, n_leaf, ppropertydesc_q, ppropref.SOURCES)
$named_reference_notice_object_property_slots(S_pre, n_leaf, n_owner, pclassdesc.PROPERTIES, pobjectprops_owner.SLOTS) = ([HCELL n_leaf])
$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
$named_reference_notice_object_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

SOURCES = r'''
S_unset = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_UNSET))]
$proprefs_valid(S_unset) /\ $class_statics_valid(S_unset)
$objectprops_valid(S_unset, S_unset.OBJECTPROPS) /\ $propref_slots_covered(S_unset, S_unset.OBJECTPROPS)
$named_reference_notice_object_property_owner(S_unset, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_array(S_unset, PARRAY n_root)
$node_children(S_unset, HOBJECT n_owner) = [HCELL n_leaf]
H_unset = $heap_graph(S_unset)
H_unset = $heap_graph(S_unset[.PROPREFS = eps])
$heap_owners(H_unset, HCELL n_leaf) = 4
S_active = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (ALIAS n_leaf)))][.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q])}]]
$proprefs_valid(S_active) /\ $class_statics_valid(S_active)
$objectprops_valid(S_active, S_active.OBJECTPROPS) /\ $propref_slots_covered(S_active, S_active.OBJECTPROPS)
$named_reference_notice_object_property_owner(S_active, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q)
$named_reference_notice_array(S_active, PARRAY n_root)
$node_children(S_active, HOBJECT n_owner) = [HCELL n_leaf, HCELL n_leaf]
H_active = $heap_graph(S_active)
H_active = $heap_graph(S_active[.PROPREFS = eps])
$heap_owners(H_active, HCELL n_leaf) = 5 /\ $heap_owners(H_active, HOBJECT n_old) = 2
S_missing_q = S_active[.PROPREFS = S_pre.PROPREFS]
$propref_source_valid(S_missing_q, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_missing_q, PARRAY n_root)
S_direct = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (DIRECT (POBJECT n_old))))]
$proprefs_valid(S_direct) /\ $class_statics_valid(S_direct)
$objectprops_valid(S_direct, S_direct.OBJECTPROPS) /\ $propref_slots_covered(S_direct, S_direct.OBJECTPROPS)
$named_reference_notice_object_property_owner(S_direct, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_array(S_direct, PARRAY n_root)
S_different = $reference_cell(S_pre, n_new_cv)[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, $property_slot_set(pobjectprops_owner.SLOTS, $ptascii("q"), PROP_VALUE (ALIAS n_new_cv)))][.PROPREFS = S_pre.PROPREFS ++ [{CELL n_new_cv, SOURCES ([OBJECT_PROP_SOURCE n_owner ($ptascii("q")) ppropertyid_q])}]]
$proprefs_valid(S_different) /\ $class_statics_valid(S_different)
$objectprops_valid(S_different, S_different.OBJECTPROPS) /\ $propref_slots_covered(S_different, S_different.OBJECTPROPS)
~$named_reference_notice_object_property_owner(S_different, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_different, PARRAY n_root)
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q[.READONLY = true], OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q[.ORIGIN = ppropertyid_p], OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q[.KEY = $ptascii("missing")], OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
S_wrong_decl = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, [{DECL (ppropertyid_p), NAME ($ptascii("q")), STATE PROP_INITIAL}, {DECL (ppropertyid_p), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}])]
$propref_source_valid(S_wrong_decl, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_wrong_decl, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_wrong_decl, PARRAY n_root)
S_no_slot = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_owner, [{DECL (ppropertyid_p), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}])]
$propref_source_valid(S_no_slot, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_no_slot, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_no_slot, PARRAY n_root)
porigin_class = PORIGIN n_source pcpath_class
porigin_foreign = PORIGIN n_source (pcpath_class ++ [PCFIELD 999])
ppropertyid_foreign = PORIGIN n_source (pcpath_class ++ [PCFIELD 999, PCINDEX 0])
ppropertydesc_foreign = ppropertydesc_q[.ORIGIN = ppropertyid_foreign]
pclassdesc_foreign = pclassdesc[.ORIGIN = porigin_foreign][.NAME = $ptascii("ForeignHole22")][.PROPERTIES = [ppropertydesc_foreign]]
S_foreign = S_pre[.CLASSES = S_pre.CLASSES ++ [pclassdesc_foreign]]
$property_declaring_class(S_foreign.CLASSES, ppropertyid_foreign) = (porigin_foreign)
$propref_source_valid(S_foreign, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_object_property_sources(S_foreign, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
~$named_reference_notice_object_property_owner(S_foreign, n_leaf, ppropertydesc_foreign, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
S_no_source = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s])}]]
$propref_source_valid(S_no_source, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_no_source, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_no_source, PARRAY n_root)
S_dead = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("owner"))]
$propref_source_valid(S_dead, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
H_dead = $heap_graph(S_dead)
(HCELL n_leaf) <- $heap_prune(H_dead).NODES
~((HOBJECT n_owner) <- $heap_prune(H_dead).NODES)
~$named_reference_notice_object_property_owner(S_dead, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_dead, PARRAY n_root)
S_native_owner = S_pre[.NATIVEEXCESS = [HOBJECT n_owner]]
~$named_reference_notice_object_property_owner(S_native_owner, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_array(S_native_owner, PARRAY n_root)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--part', choices=('ingress', 'post', 'checkpoint', 'controls'), default='post')
    parser.add_argument('--checkpoint-report', type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    if args.part == 'post':
        directory = args.output.resolve()
        directory.mkdir(parents=True)
        common = [sys.executable, str(Path(__file__)), '--native-provenance', str(provenance)]
        subprocess.run(common + ['--part', 'checkpoint', '--output', str(directory / 'checkpoint')], cwd=ROOT, check=True)
        checkpoint = directory / 'checkpoint/report.json'
        subprocess.run(common + ['--part', 'controls', '--checkpoint-report', str(checkpoint),
            '--output', str(directory / 'controls')], cwd=ROOT, check=True)
        reports = [json.loads((directory / part / 'report.json').read_bytes()) for part in ('checkpoint', 'controls')]
        checks = [check for report in reports for check in report['checks']]
        repeated = reports[1]['repeated_context_conditions']
        report = {'part': 'post', 'revision': reports[0]['revision'], 'module_count': reports[0]['module_count'],
            'mode': reports[0]['mode'], 'reports': [str(directory / part / 'report.json') for part in ('checkpoint', 'controls')],
            'conditions': len(checks), 'unique_conditions': len(set(checks)),
            'reached_conditions': reports[0]['reached_conditions'], 'derived_conditions': reports[1]['derived_conditions'],
            'repeated_context_conditions': repeated, 'heap_bindings': sum(row['heap_bindings'] for row in reports),
            'passed': all(row['passed'] for row in reports), 'source_agreements': 0}
        assert report['conditions'] == report['unique_conditions'] + repeated
        (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print('post', report['passed'], flush=True)
        return report['passed']
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('same_class_mixed_hole_alias_stdclass_reference_notice_review_cases.json')
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
    derived = INGRESS if args.part == 'ingress' else SOURCES
    if args.part == 'checkpoint':
        derived = []
    if args.part == 'controls':
        reached = REACHED[:30] + [REACHED[33], REACHED[34]]
    checks = [initial] + reached + derived
    if args.part == 'controls':
        checkpoint_path = args.checkpoint_report.resolve()
        checkpoint = json.loads(checkpoint_path.read_bytes())
        assert checkpoint['passed'] and checkpoint['part'] == 'checkpoint'
        assert checkpoint['revision'] == revision and checkpoint['source_sha256'] == digest(source)
        assert checkpoint['inputs'] == before
        assert all(check in checkpoint['checks'] for check in [initial] + reached)
        paths.append(checkpoint_path)
        before = fingerprints()
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
        'fixture_sha256': fixture_sha, 'part': args.part, 'conditions': len(checks), 'checks': checks,
        'checkpoint_report': str(args.checkpoint_report.resolve()) if args.checkpoint_report else None,
        'repeated_context_conditions': len(reached) + 1 if args.part == 'controls' else 0, 'reached_conditions': len(reached) + 1,
        'derived_conditions': len(derived), 'heap_bindings': len({check.split(' = ', 1)[0] for check in checks if check.startswith('H_') and ' = $heap_graph(' in check}), 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.part, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
