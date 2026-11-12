#!/usr/bin/env python3
"""Authenticate a genuine indexed unused group and its static-source Notice fence."""
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
dec $somi_output(pevent*) : ptbytes
def $somi_output(eps) = eps
def $somi_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $somi_output(pevent*)
dec $somi_ready(pstate) : bool
def $somi_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $somi_output(S.EVENTS) = $ptascii("R;")
def $somi_ready(S) = false -- otherwise
dec $somi_seek(pstate, nat) : pstate
def $somi_seek(S, n) = S
  -- if $somi_ready(S) \/ n = 0 \/ S.TODO = eps
def $somi_seek(S, n) = $somi_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$somi_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $somi_seek(S, n) = S -- otherwise


dec $somi_replace(pcoccurrence*, pcpath, pcnode?) : pcoccurrence*
def $somi_replace(eps, pcpath, pcnode_replacement?) = eps
def $somi_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, (pcnode_new)) = (PCOCCURRENCE pcpath pcnode_new) :: pcoccurrence*
def $somi_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, eps) = pcoccurrence*
def $somi_replace((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath, pcnode_replacement?) = (PCOCCURRENCE pcpath_other pcnode) :: $somi_replace(pcoccurrence*, pcpath, pcnode_replacement?)
  -- if pcpath_other =/= pcpath
dec $somi_raw_state(pstate, pcpath, pcnode?) : pstate
def $somi_raw_state(S, pcpath, pcnode_replacement?) = S[.SOURCES = [pcunit[.OCCURRENCES = $somi_replace(pcunit.OCCURRENCES, pcpath, pcnode_replacement?)]]]
  -- if S.SOURCES = [pcunit]

'''

REACHED = r'''
S_pre = $somi_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$somi_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.OBJECTS = [STDINSTANCE, STDINSTANCE]
n_old =/= n_new
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_class
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_t, ppropertydesc_r, ppropertydesc_q, ppropertydesc_p, ppropertydesc_s]
ppropertydesc_t.STATIC /\ ~ppropertydesc_r.STATIC /\ ~ppropertydesc_q.STATIC /\ ~ppropertydesc_p.STATIC /\ ppropertydesc_s.STATIC
ppropertydesc_s.ORIGIN = ppropertyid_s
ppropertydesc_t.ORIGIN = ppropertyid_t
ppropertydesc_p.ORIGIN = ppropertyid_p
ppropertydesc_r.ORIGIN = ppropertyid_r
ppropertydesc_q.ORIGIN = ppropertyid_q
ppropertyid_s =/= ppropertyid_t /\ ppropertyid_p =/= ppropertyid_s /\ ppropertyid_p =/= ppropertyid_t
$property_declaring_class(S_pre.CLASSES, ppropertyid_s) = (porigin_class)
$property_declaring_class(S_pre.CLASSES, ppropertyid_t) = (porigin_class)
$property_declaring_class(S_pre.CLASSES, ppropertyid_p) = (porigin_class)
~((INSTANCE porigin_class) <- S_pre.OBJECTS)
ppropertydesc_p.NAME = $ptascii("p") /\ ppropertydesc_p.NAME = ppropertydesc_p.KEY
ppropertydesc_p.VISIBILITY = PROPERTY_PUBLIC /\ ppropertydesc_p.SETVISIBILITY = eps
~ppropertydesc_p.READONLY /\ ~ppropertydesc_p.FINAL
ppropertydesc_p.DEFAULT = PROP_UNINITIALIZED
ppropertydesc_p.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
ppropertyid_p = PORIGIN n_source pcpath_property
$(|pcpath_property| >= 2)
pcpath_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]
pcpath_property = pcpath_group ++ [PCFIELD 3, PCINDEX 2]
ppropertyid_r = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 0])
ppropertyid_q = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 1])
$origin_node(S_pre.SOURCES, PORIGIN n_source pcpath_group) = (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_r ABSENT metadata_r, NPropertyItem phpType40_q ABSENT metadata_q, NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE eps) metadata)
$origin_node(S_pre.SOURCES, PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 0])) = (NPropertyItem phpType40_r ABSENT metadata_r)
$origin_node(S_pre.SOURCES, PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 1])) = (NPropertyItem phpType40_q ABSENT metadata_q)
$origin_node(S_pre.SOURCES, PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 2])) = (NPropertyItem phpType40 ABSENT metadata_item)
ppropertydesc_r.NAME = $ptascii("r") /\ ppropertydesc_q.NAME = $ptascii("q")
$property_declaring_class(S_pre.CLASSES, ppropertyid_r) = (porigin_class)
$property_declaring_class(S_pre.CLASSES, ppropertyid_q) = (porigin_class)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_s) = (ppropertydesc_s)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_t) = (ppropertydesc_t)
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_s) = ({DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_t) = ({DECL ppropertyid_t, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_p) = eps
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_r) = eps /\ $class_static_at(S_pre.CLASSSTATICS, ppropertyid_q) = eps
|S_pre.CLASSSTATICS| = 2
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_s, CLASS_PROP_SOURCE ppropertyid_t]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_t)
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf]
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
$heap_owners(H_pre, HCELL n_leaf) = 4 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$class_statics_valid(S_pre) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS)
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''
$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_t, ppropertydesc_s])
~$named_reference_notice_object_property_owner_source(S_pre, n_leaf, ppropertydesc_p, ppropref.SOURCES)
~$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_t])
~$named_reference_notice_object_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_p])
$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
$named_reference_notice_object_static_sources(S_pre, n_leaf, ppropref.SOURCES)
$named_reference_notice_object_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

SOURCES = r'''
S_missing_q = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_t, ppropertydesc_r, ppropertydesc_p, ppropertydesc_s]]]]
$propref_source_valid(S_missing_q, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
~$named_reference_notice_object_static_properties(S_missing_q, n_leaf, [ppropertydesc_p])
~$named_reference_notice_array(S_missing_q, PARRAY n_root)
S_missing_r = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_t, ppropertydesc_q, ppropertydesc_p, ppropertydesc_s]]]]
~$named_reference_notice_object_static_properties(S_missing_r, n_leaf, [ppropertydesc_p])
~$named_reference_notice_array(S_missing_r, PARRAY n_root)
S_missing_p = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_t, ppropertydesc_r, ppropertydesc_q, ppropertydesc_s]]]]
~$named_reference_notice_object_static_properties(S_missing_p, n_leaf, [ppropertydesc_q])
~$named_reference_notice_array(S_missing_p, PARRAY n_root)
S_missing_raw_q = $somi_raw_state(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 1], eps)
~$named_reference_notice_array(S_missing_raw_q, PARRAY n_root)
S_wrong_raw_q = $somi_raw_state(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 1], (NPropertyItem phpType40_r ABSENT metadata_r))
~$named_reference_notice_array(S_wrong_raw_q, PARRAY n_root)
S_extra_raw = $somi_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_r ABSENT metadata_r, NPropertyItem phpType40_q ABSENT metadata_q, NPropertyItem phpType40 ABSENT metadata_item, NPropertyItem (NVarLikeIdentifier (BYTES "eg==") eps) ABSENT metadata_item])) (SEQUENCE eps) metadata))
~$named_reference_notice_array(S_extra_raw, PARRAY n_root)
S_empty_group = $somi_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE eps) (SEQUENCE eps) metadata))
~$named_reference_notice_array(S_empty_group, PARRAY n_root)
S_reordered_group = $somi_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40 ABSENT metadata_item, NPropertyItem phpType40_q ABSENT metadata_q, NPropertyItem phpType40_r ABSENT metadata_r])) (SEQUENCE eps) metadata))
~$named_reference_notice_array(S_reordered_group, PARRAY n_root)
S_default_q = $somi_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_r ABSENT metadata_r, NPropertyItem phpType40_q (NScalarInt (INTEGER 0) eps) metadata_q, NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE eps) metadata))
~$named_reference_notice_array(S_default_q, PARRAY n_root)
S_hooks = $somi_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_r ABSENT metadata_r, NPropertyItem phpType40_q ABSENT metadata_q, NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") eps) (SEQUENCE eps) (SEQUENCE eps) eps])) metadata))
~$named_reference_notice_array(S_hooks, PARRAY n_root)
S_wrong_q_origin = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_t, ppropertydesc_r, ppropertydesc_q[.ORIGIN = ppropertyid_p], ppropertydesc_p, ppropertydesc_s]]]]
~$named_reference_notice_array(S_wrong_q_origin, PARRAY n_root)
S_q_static = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_t, ppropertydesc_r, ppropertydesc_q[.STATIC = true], ppropertydesc_p, ppropertydesc_s]]]]
~$named_reference_notice_array(S_q_static, PARRAY n_root)
S_q_type = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_t, ppropertydesc_r, ppropertydesc_q[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]], ppropertydesc_p, ppropertydesc_s]]]]
~$named_reference_notice_array(S_q_type, PARRAY n_root)
S_exact_instance = S_pre[.OBJECTS = S_pre.OBJECTS ++ [INSTANCE porigin_class]]
$propref_source_valid(S_exact_instance, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
~$named_reference_notice_array(S_exact_instance, PARRAY n_root)
S_static_initial = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s])}]][.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_t, PROP_INITIAL)]
$proprefs_valid(S_static_initial) /\ $class_statics_valid(S_static_initial)
$named_reference_notice_array(S_static_initial, PARRAY n_root)
$class_static_roots(S_static_initial.CLASSSTATICS) = [HCELL n_leaf]
H_initial = $heap_graph(S_static_initial)
H_initial = $heap_graph(S_static_initial[.PROPREFS = eps])
$heap_owners(H_initial, HCELL n_leaf) = 3
S_cell_unit = S_pre[.NATIVEEXCESS = [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_unit, PARRAY n_root)
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
    catalogue = Path(__file__).with_name('grouped_unused_mixed_alias_stdclass_reference_notice_review_cases.json')
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
        reached = REACHED
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
