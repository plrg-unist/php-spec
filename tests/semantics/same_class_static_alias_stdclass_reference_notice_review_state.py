#!/usr/bin/env python3
"""Isolate the genuine same-class static-source reference Notice fence."""
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
dec $scsn_output(pevent*) : ptbytes
def $scsn_output(eps) = eps
def $scsn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $scsn_output(pevent*)
dec $scsn_ready(pstate) : bool
def $scsn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $scsn_output(S.EVENTS) = $ptascii("R;")
def $scsn_ready(S) = false -- otherwise
dec $scsn_seek(pstate, nat) : pstate
def $scsn_seek(S, n) = S
  -- if $scsn_ready(S) \/ n = 0 \/ S.TODO = eps
def $scsn_seek(S, n) = $scsn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$scsn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scsn_seek(S, n) = S -- otherwise


dec $scsn_plain(pstate, ppropertydesc) : bool
def $scsn_plain(S, ppropertydesc) = true
  -- if ppropertydesc.NAME = ppropertydesc.KEY
  -- if ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ppropertydesc.SETVISIBILITY = eps
  -- if ppropertydesc.STATIC /\ ~ppropertydesc.READONLY /\ ~ppropertydesc.FINAL
  -- if ppropertydesc.DEFAULT = PROP_UNINITIALIZED
  -- if ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
  -- if $ptlc(ptbytes_type) = $ptascii("stdclass")
  -- if ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property
  -- if $(|pcpath_property| >= 2)
  -- if pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]
  -- if pcpath_property = pcpath_group ++ [PCFIELD 3, PCINDEX 0]
  -- if $origin_node(S.SOURCES, PORIGIN n_source pcpath_group) = (NStmtProperty phpType14 phpType24 phpType18 (SEQUENCE ([NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE eps) metadata)
def $scsn_plain(S, ppropertydesc) = false -- otherwise
'''

REACHED = r'''
S_pre = $scsn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$scsn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.CLASSES = [pclassdesc]
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_a, ppropertydesc_b]
ppropertydesc_a.ORIGIN = ppropertyid_a
ppropertydesc_b.ORIGIN = ppropertyid_b
ppropertyid_a =/= ppropertyid_b
$scsn_plain(S_pre, ppropertydesc_a) /\ $scsn_plain(S_pre, ppropertydesc_b)
$property_declaring_class(S_pre.CLASSES, ppropertyid_a) = (pclassdesc.ORIGIN)
$property_declaring_class(S_pre.CLASSES, ppropertyid_b) = (pclassdesc.ORIGIN)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_a) = (ppropertydesc_a)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_b) = (ppropertydesc_b)
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_a]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_b)
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_a) = ({DECL ppropertyid_a, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_b) = ({DECL ppropertyid_b, STATE PROP_VALUE (ALIAS n_leaf)})
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
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_a])
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_b])
~$named_reference_notice_object_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_one_a = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a]]]][.CLASSSTATICS = [{DECL ppropertyid_a, STATE PROP_VALUE (ALIAS n_leaf)}]][.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a])}]]
$proprefs_valid(S_one_a) /\ $class_statics_valid(S_one_a)
$named_reference_notice_object_static_source(S_one_a, n_leaf)
$named_reference_notice_array(S_one_a, PARRAY n_root) /\ $named_reference_notice_pending(S_one_a)
S_one_b = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_b]]]][.CLASSSTATICS = [{DECL ppropertyid_b, STATE PROP_VALUE (ALIAS n_leaf)}]][.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_b])}]]
$proprefs_valid(S_one_b) /\ $class_statics_valid(S_one_b)
$named_reference_notice_object_static_source(S_one_b, n_leaf)
$named_reference_notice_array(S_one_b, PARRAY n_root) /\ $named_reference_notice_pending(S_one_b)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_object_static_source(S_pre, n_leaf)
$named_reference_notice_object_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
'''.strip().splitlines()
SOURCES = r'''
S_permuted = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a, CLASS_PROP_SOURCE ppropertyid_b])}]]
$proprefs_valid(S_permuted) /\ $class_statics_valid(S_permuted)
$named_reference_notice_array(S_permuted, PARRAY n_root)
S_missing = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a])}]]
$propref_source_valid(S_missing, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_object_static_sources(S_missing, n_leaf, [CLASS_PROP_SOURCE ppropertyid_a])
~$named_reference_notice_array(S_missing, PARRAY n_root)
S_hole = S_missing[.CLASSSTATICS = $class_static_set(S_missing.CLASSSTATICS, ppropertyid_b, PROP_INITIAL)]
$proprefs_valid(S_hole) /\ $class_statics_valid(S_hole)
$class_static_roots(S_hole.CLASSSTATICS) = [HCELL n_leaf]
$named_reference_notice_object_static_source(S_hole, n_leaf)
$named_reference_notice_array(S_hole, PARRAY n_root)
H_initial = $heap_graph(S_hole)
H_initial = $heap_graph(S_hole[.PROPREFS = eps])
$heap_owners(H_initial, HCELL n_leaf) = 3 /\ $heap_owners(H_initial, HOBJECT n_old) = 2
S_direct = S_missing[.CLASSSTATICS = $class_static_set(S_missing.CLASSSTATICS, ppropertyid_b, PROP_VALUE (DIRECT (POBJECT n_old)))]
$proprefs_valid(S_direct) /\ $class_statics_valid(S_direct)
$propref_source_valid(S_direct, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_direct, PARRAY n_root)
S_different = S_missing[.CLASSSTATICS = $class_static_set(S_missing.CLASSSTATICS, ppropertyid_b, PROP_VALUE (ALIAS n_new_cv))]
$propref_source_valid(S_different, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_different, PARRAY n_root)
S_unset = S_missing[.CLASSSTATICS = $class_static_set(S_missing.CLASSSTATICS, ppropertyid_b, PROP_UNSET)]
$propref_source_valid(S_unset, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_unset, PARRAY n_root)
S_no_b = S_missing[.CLASSSTATICS = [{DECL ppropertyid_a, STATE PROP_VALUE (ALIAS n_leaf)}]]
$propref_source_valid(S_no_b, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_no_b, PARRAY n_root)
S_duplicate = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid_a])}]]
~$named_reference_notice_array(S_duplicate, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_no_active = S_pre[.CLASSNAMES = eps]
~$named_reference_notice_array(S_no_active, PARRAY n_root)
S_no_source = S_pre[.SOURCES = eps]
$propref_source_valid(S_no_source, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_no_source, PARRAY n_root)
S_nullable = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b[.TYPE = [(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
$propref_source_valid(S_nullable, n_leaf, CLASS_PROP_SOURCE ppropertyid_a) /\ $propref_source_valid(S_nullable, n_leaf, CLASS_PROP_SOURCE ppropertyid_b)
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_protected = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b[.VISIBILITY = PROPERTY_PROTECTED]]]]]
$propref_source_valid(S_protected, n_leaf, CLASS_PROP_SOURCE ppropertyid_a) /\ $propref_source_valid(S_protected, n_leaf, CLASS_PROP_SOURCE ppropertyid_b)
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_nonstatic = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc_a, ppropertydesc_b[.STATIC = false]]]]]
$propref_source_valid(S_nonstatic, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_nonstatic, PARRAY n_root)
S_readonly = S_pre[.CLASSES = [pclassdesc[.READONLY = true]]]
$propref_source_valid(S_readonly, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_readonly, PARRAY n_root)
S_parent = S_pre[.CLASSES = [pclassdesc[.PARENT = ($ptascii("Unknown"))]]]
$propref_source_valid(S_parent, n_leaf, CLASS_PROP_SOURCE ppropertyid_a)
~$named_reference_notice_array(S_parent, PARRAY n_root)
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
    parser.add_argument('--part', choices=('ingress', 'post', 'checkpoint', 'controls'), default='post')
    parser.add_argument('--checkpoint-report', type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('same_class_static_alias_stdclass_reference_notice_review_cases.json')
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
        reached = REACHED[:20] + [REACHED[25]]
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
