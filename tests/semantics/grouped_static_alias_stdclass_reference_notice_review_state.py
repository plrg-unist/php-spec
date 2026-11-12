#!/usr/bin/env python3
"""Isolate the genuine grouped static-source item origins and the genuine Notice fence."""
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
dec $gsn_output(pevent*) : ptbytes
def $gsn_output(eps) = eps
def $gsn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $gsn_output(pevent*)
dec $gsn_ready(pstate) : bool
def $gsn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $gsn_output(S.EVENTS) = $ptascii("R;")
def $gsn_ready(S) = false -- otherwise
dec $gsn_seek(pstate, nat) : pstate
def $gsn_seek(S, n) = S
  -- if $gsn_ready(S) \/ n = 0 \/ S.TODO = eps
def $gsn_seek(S, n) = $gsn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$gsn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gsn_seek(S, n) = S -- otherwise

dec $gsn_raw_indexed(pstate, ppropertydesc) : bool
def $gsn_raw_indexed(S, ppropertydesc) = true
  -- if ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property
  -- if $(|pcpath_property| >= 2)
  -- if pcpath_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]
  -- if pcpath_property[$nabs($(|pcpath_property| - 1))] = PCINDEX n_item
  -- if pcpath_property = pcpath_group ++ [PCFIELD 3, PCINDEX n_item]
  -- if $origin_node(S.SOURCES, PORIGIN n_source pcpath_group) = (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE phpType57*) (SEQUENCE eps) metadata)
  -- if $origin_node(S.SOURCES, PORIGIN n_source pcpath_property) = (NPropertyItem phpType40 ABSENT metadata_item)
def $gsn_raw_indexed(S, ppropertydesc) = false -- otherwise
dec $gsn_replace(pcoccurrence*, pcpath, pcnode?) : pcoccurrence*
def $gsn_replace(eps, pcpath, pcnode_replacement?) = eps
def $gsn_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, (pcnode_new)) = (PCOCCURRENCE pcpath pcnode_new) :: pcoccurrence*
def $gsn_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, eps) = pcoccurrence*
def $gsn_replace((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath, pcnode_replacement?) = (PCOCCURRENCE pcpath_other pcnode) :: $gsn_replace(pcoccurrence*, pcpath, pcnode_replacement?)
  -- if pcpath_other =/= pcpath
dec $gsn_raw_state(pstate, pcpath, pcnode?) : pstate
def $gsn_raw_state(S, pcpath, pcnode_replacement?) = S[.SOURCES = [pcunit[.OCCURRENCES = $gsn_replace(pcunit.OCCURRENCES, pcpath, pcnode_replacement?)]]]
  -- if S.SOURCES = [pcunit]

'''

REACHED = r'''
S_pre = $gsn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$gsn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.CLASSES = [pclassdesc]
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_idle]
ppropertydesc_a.ORIGIN = ppropertyid_a
ppropertydesc_b.ORIGIN = ppropertyid_b
ppropertydesc_c.ORIGIN = ppropertyid_c
ppropertydesc_idle.ORIGIN = ppropertyid_idle
ppropertyid_a = PORIGIN n_source pcpath_a
pcpath_group = pcpath_a[0:$nabs($(|pcpath_a| - 2))]
pcpath_a = pcpath_group ++ [PCFIELD 3, PCINDEX 0]
ppropertyid_b = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 1])
ppropertyid_c = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 2])
ppropertyid_idle = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 3])
$origin_node(S_pre.SOURCES, PORIGIN n_source pcpath_group) = (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_a ABSENT metadata_a, NPropertyItem phpType40_b ABSENT metadata_b, NPropertyItem phpType40_c ABSENT metadata_c, NPropertyItem phpType40_idle ABSENT metadata_idle])) (SEQUENCE eps) metadata)
$gsn_raw_indexed(S_pre, ppropertydesc_a) /\ $gsn_raw_indexed(S_pre, ppropertydesc_b)
$gsn_raw_indexed(S_pre, ppropertydesc_c) /\ $gsn_raw_indexed(S_pre, ppropertydesc_idle)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_a) = (ppropertydesc_a)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_b) = (ppropertydesc_b)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_c) = (ppropertydesc_c)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_idle) = (ppropertydesc_idle)
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_c, CLASS_PROP_SOURCE ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_a]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_b)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_c)
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_a) = ({DECL ppropertyid_a, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_b) = ({DECL ppropertyid_b, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_c) = ({DECL ppropertyid_c, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_idle) = ({DECL ppropertyid_idle, STATE PROP_INITIAL})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
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
$heap_owners(H_pre, HCELL n_leaf) = 5 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$class_statics_valid(S_pre) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS)
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_a])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_b])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_c])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_idle])
~$named_reference_notice_object_static_source(S_pre, n_leaf)
~$named_reference_notice_object_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_static_source(S_pre, n_leaf)
$named_reference_notice_object_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

SOURCES = r'''
S_no_source = S_pre[.SOURCES = eps]
$propref_source_valid(S_no_source, n_leaf, CLASS_PROP_SOURCE ppropertyid_c)
~$named_reference_notice_array(S_no_source, PARRAY n_root)
S_no_group = $gsn_raw_state(S_pre, pcpath_group, eps)
~$named_reference_notice_object_static_properties(S_no_group, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_array(S_no_group, PARRAY n_root)
S_no_item = $gsn_raw_state(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 2], eps)
~$named_reference_notice_object_static_properties(S_no_item, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_array(S_no_item, PARRAY n_root)
S_default = $gsn_raw_state(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 2], (NPropertyItem phpType40_c (NScalarInt (INTEGER 0) eps) metadata_c))
~$named_reference_notice_object_static_properties(S_default, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_array(S_default, PARRAY n_root)
S_other_item = $gsn_raw_state(S_pre, pcpath_group ++ [PCFIELD 3, PCINDEX 2], (NStmtNop metadata_c))
~$named_reference_notice_object_static_properties(S_other_item, n_leaf, pclassdesc.PROPERTIES)
S_other_group = $gsn_raw_state(S_pre, pcpath_group, (NStmtNop metadata))
~$named_reference_notice_object_static_properties(S_other_group, n_leaf, pclassdesc.PROPERTIES)
S_hooks = $gsn_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_a ABSENT metadata_a, NPropertyItem phpType40_b ABSENT metadata_b, NPropertyItem phpType40_c ABSENT metadata_c, NPropertyItem phpType40_idle ABSENT metadata_idle])) (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") eps) (SEQUENCE eps) (SEQUENCE eps) eps])) metadata))
~$named_reference_notice_object_static_properties(S_hooks, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_array(S_hooks, PARRAY n_root)
$origin_node(S_pre.SOURCES, PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 4])) = eps
~$gsn_raw_indexed(S_pre, ppropertydesc_c[.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 4])])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_c[.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3, PCINDEX 4])]])
~$gsn_raw_indexed(S_pre, ppropertydesc_c[.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 2, PCINDEX 2])])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_c[.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 2, PCINDEX 2])]])
~$gsn_raw_indexed(S_pre, ppropertydesc_c[.ORIGIN = PORIGIN n_source ([PCFIELD 3])])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_c[.ORIGIN = PORIGIN n_source ([PCFIELD 3])]])
~$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_c[.ORIGIN = ppropertyid_idle]])
S_single_raw = $gsn_raw_state(S_pre, pcpath_group, (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40_a ABSENT metadata_a])) (SEQUENCE eps) metadata))
S_single = S_single_raw[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a]]]][.CLASSSTATICS = [{DECL ppropertyid_a, STATE PROP_VALUE (ALIAS n_leaf)}]][.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a])}]]
$gsn_raw_indexed(S_single, ppropertydesc_a)
$proprefs_valid(S_single) /\ $class_statics_valid(S_single)
$named_reference_notice_object_static_properties(S_single, n_leaf, [ppropertydesc_a])
$named_reference_notice_array(S_single, PARRAY n_root)
$class_static_roots(S_single.CLASSSTATICS) = [HCELL n_leaf]
H_single = $heap_graph(S_single)
H_single = $heap_graph(S_single[.PROPREFS = eps])
$heap_owners(H_single, HCELL n_leaf) = 3
S_missing_source = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_c, CLASS_PROP_SOURCE ppropertyid_b])}]]
$propref_source_valid(S_missing_source, n_leaf, CLASS_PROP_SOURCE ppropertyid_c)
~$named_reference_notice_object_static_properties(S_missing_source, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_array(S_missing_source, PARRAY n_root)
S_direct = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_idle, PROP_VALUE (DIRECT (POBJECT n_old)))]
$proprefs_valid(S_direct) /\ $class_statics_valid(S_direct)
$named_reference_notice_array(S_direct, PARRAY n_root)
S_split = $reference_cell(S_pre, n_new_cv)[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_idle, PROP_VALUE (ALIAS n_new_cv))][.PROPREFS = S_pre.PROPREFS ++ [{CELL n_new_cv, SOURCES ([CLASS_PROP_SOURCE ppropertyid_idle])}]]
$proprefs_valid(S_split) /\ $class_statics_valid(S_split)
~$named_reference_notice_array(S_split, PARRAY n_root)
S_unset = S_pre[.CLASSSTATICS = $class_static_set(S_pre.CLASSSTATICS, ppropertyid_idle, PROP_UNSET)]
$propref_source_valid(S_unset, n_leaf, CLASS_PROP_SOURCE ppropertyid_c)
~$named_reference_notice_array(S_unset, PARRAY n_root)
S_no_row = S_pre[.CLASSSTATICS = [{DECL ppropertyid_a, STATE PROP_VALUE (ALIAS n_leaf)}, {DECL ppropertyid_b, STATE PROP_VALUE (ALIAS n_leaf)}, {DECL ppropertyid_c, STATE PROP_VALUE (ALIAS n_leaf)}]]
$propref_source_valid(S_no_row, n_leaf, CLASS_PROP_SOURCE ppropertyid_c)
~$named_reference_notice_array(S_no_row, PARRAY n_root)
S_nonstatic = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_idle[.STATIC = false]]]]]
~$named_reference_notice_array(S_nonstatic, PARRAY n_root)
S_native = S_pre[.NATIVEEXCESS = [HCELL n_leaf]]
~$named_reference_notice_array(S_native, PARRAY n_root)
S_payload = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_old, [{DECL eps, NAME ($ptascii("v")), STATE PROP_VALUE (DIRECT (POBJECT n_new))}])]
~$named_reference_notice_array(S_payload, PARRAY n_root)
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
    catalogue = Path(__file__).with_name('grouped_static_alias_stdclass_reference_notice_review_cases.json')
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
        reached = REACHED[:26] + [REACHED[32], REACHED[33]]
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
