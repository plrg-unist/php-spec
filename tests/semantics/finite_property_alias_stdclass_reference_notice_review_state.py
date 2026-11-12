#!/usr/bin/env python3
"""Isolate the genuine finite rooted-property Notice admission fence."""
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
dec $fpn_output(pevent*) : ptbytes
def $fpn_output(eps) = eps
def $fpn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $fpn_output(pevent*)
dec $fpn_ready(pstate) : bool
def $fpn_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $fpn_output(S.EVENTS) = $ptascii("A;")
def $fpn_ready(S) = false -- otherwise
dec $fpn_seek(pstate, nat) : pstate
def $fpn_seek(S, n) = S
  -- if $fpn_ready(S) \/ n = 0 \/ S.TODO = eps
def $fpn_seek(S, n) = $fpn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$fpn_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fpn_seek(S, n) = S -- otherwise
'''

REACHED = r'''
S_pre = $fpn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$fpn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("a")) = (n_a_cv)
$lookup(S_pre.ENV, $ptascii("b")) = (n_b_cv)
$lookup(S_pre.ENV, $ptascii("c")) = (n_c_cv)
$lookup(S_pre.ENV, $ptascii("d")) = (n_d_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.STORE[n_a_cv] = DEFINED (POBJECT n_a)
S_pre.STORE[n_b_cv] = DEFINED (POBJECT n_b)
S_pre.STORE[n_c_cv] = DEFINED (POBJECT n_c)
S_pre.STORE[n_d_cv] = DEFINED (POBJECT n_d)
S_pre.OBJECTS[n_a] = INSTANCE porigin_holder
S_pre.OBJECTS[n_b] = INSTANCE porigin_holder
S_pre.OBJECTS[n_c] = INSTANCE porigin_holder
S_pre.OBJECTS[n_d] = INSTANCE porigin_holder
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_holder
pclassdesc.PROPERTIES = [ppropertydesc]
ppropertydesc.ORIGIN = ppropertyid
ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_d ($ptascii("p")) ppropertyid, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid]
$propref_unique_sources(ppropref.SOURCES)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_a ($ptascii("p")) ppropertyid)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_d ($ptascii("p")) ppropertyid)
$objectprops_record_at(S_pre.OBJECTPROPS, n_a) = (pobjectprops_a)
$objectprops_record_at(S_pre.OBJECTPROPS, n_b) = (pobjectprops_b)
$objectprops_record_at(S_pre.OBJECTPROPS, n_c) = (pobjectprops_c)
$objectprops_record_at(S_pre.OBJECTPROPS, n_d) = (pobjectprops_d)
pobjectprops_a.SLOTS = [{DECL (ppropertyid), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}]
pobjectprops_b.SLOTS = pobjectprops_a.SLOTS /\ pobjectprops_c.SLOTS = pobjectprops_a.SLOTS /\ pobjectprops_d.SLOTS = pobjectprops_a.SLOTS
$node_children(S_pre, HOBJECT n_a) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_b) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_c) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_d) = [HCELL n_leaf]
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
$heap_owners(H_pre, HCELL n_leaf) = 6 /\ $heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_a) = 1 /\ $heap_owners(H_pre, HOBJECT n_b) = 1
$heap_owners(H_pre, HOBJECT n_c) = 1 /\ $heap_owners(H_pre, HOBJECT n_d) = 1
$heap_owners(H_pre, HOBJECT n_old) = 2 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_a) <- $heap_prune(H_pre).NODES /\ (HOBJECT n_b) <- $heap_prune(H_pre).NODES
(HOBJECT n_c) <- $heap_prune(H_pre).NODES /\ (HOBJECT n_d) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

PROTOCOL = r'''
~$named_reference_notice_object_property_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_single_b = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_b ($ptascii("p")) ppropertyid])}]]
$named_reference_notice_object_property_source(S_single_b, n_leaf)
$named_reference_notice_array(S_single_b, PARRAY n_root)
S_single_c = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid])}]]
$named_reference_notice_object_property_source(S_single_c, n_leaf)
$named_reference_notice_array(S_single_c, PARRAY n_root)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
S_unroot_c = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("c"))]
$propref_source_valid(S_unroot_c, n_leaf, OBJECT_PROP_SOURCE n_c ($ptascii("p")) ppropertyid)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_unroot_c)).NODES
~((HOBJECT n_c) <- $heap_prune($heap_graph(S_unroot_c)).NODES)
~$named_reference_notice_array(S_unroot_c, PARRAY n_root)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('finite_property_alias_stdclass_reference_notice_review_cases.json')
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
    checks = [initial] + REACHED + PROTOCOL
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    fixture_sha = digest(fixture)
    print(directory, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 540)
    stable = before == fingerprints() and digest(fixture) == fixture_sha
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'source': str(source), 'source_sha256': digest(source),
        'fixture_sha256': fixture_sha, 'conditions': len(checks), 'reached_conditions': len(REACHED) + 1,
        'derived_conditions': len(PROTOCOL), 'heap_bindings': 1, 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('property ingress', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
