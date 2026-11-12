#!/usr/bin/env python3
"""Ground genuine mixed same-class source refusal with actual DIRECT complement edges."""
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


'''

REACHED = r'''
S_pre = $sopn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$sopn_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("owner")) = (n_owner_cv)
$lookup(S_pre.ENV, $ptascii("old")) = eps
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
S_pre.STORE[n_owner_cv] = DEFINED (POBJECT n_owner)
S_pre.OBJECTS[n_owner] = INSTANCE porigin_owner
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_owner
pclassdesc.KIND = "class" /\ ~pclassdesc.ABSTRACT /\ ~pclassdesc.READONLY
pclassdesc.PARENT = eps /\ pclassdesc.INTERFACES = eps
pclassdesc.METHODS = eps /\ pclassdesc.CONSTANTS = eps
pclassdesc.PROPERTIES = [ppropertydesc_r, ppropertydesc_p, ppropertydesc_q, ppropertydesc_s]
ppropertydesc_r.ORIGIN = ppropertyid_r
ppropertydesc_p.ORIGIN = ppropertyid_p
ppropertydesc_q.ORIGIN = ppropertyid_q
ppropertydesc_s.ORIGIN = ppropertyid_s
$property_declaring_class(S_pre.CLASSES, ppropertyid_r) = (porigin_owner)
$property_declaring_class(S_pre.CLASSES, ppropertyid_q) = (porigin_owner)
(INSTANCE porigin_owner) <- S_pre.OBJECTS
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p, CLASS_PROP_SOURCE ppropertyid_s]
$propref_unique_sources(ppropref.SOURCES)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid_s) = (ppropertydesc_s)
S_pre.CLASSSTATICS = [{DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)}]
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_s) = ({DECL ppropertyid_s, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf]
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_s)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$objectprops_record_at(S_pre.OBJECTPROPS, n_owner) = (pobjectprops_owner)
pobjectprops_owner.SLOTS = [{DECL (ppropertyid_r), NAME ($ptascii("r")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}, {DECL (ppropertyid_p), NAME ($ptascii("p")), STATE PROP_VALUE (ALIAS n_leaf)}, {DECL (ppropertyid_q), NAME ($ptascii("q")), STATE PROP_VALUE (DIRECT (POBJECT n_old))}]
~pobjectprops_owner.MATERIALIZED /\ $objectprops_valid(S_pre, [pobjectprops_owner])
$object_table_at(S_pre.OBJECTTABLES, n_owner) = eps
$node_children(S_pre, HOBJECT n_owner) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object(S_pre, POBJECT n_new)
$named_reference_notice_object_ancestors(S_pre, [n_root])
~$instance_storage_freeing(S_pre, n_owner) /\ ~(n_owner <- S_pre.DESTRUCTION.CALLED)
~$propref_source_queued(S_pre, n_leaf, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$heap_count(HOBJECT n_owner, S_pre.NATIVEEXCESS) = 0 /\ ~$weakmap_key_waiting(S_pre, n_owner)
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
$heap_owners(H_pre, HOBJECT n_old) = 3 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_owner) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS)
$objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
$named_reference_notice_object_property_slots(S_pre, n_leaf, n_owner, pclassdesc.PROPERTIES, pobjectprops_owner.SLOTS) = ([HOBJECT n_old, HCELL n_leaf, HOBJECT n_old])
$named_reference_notice_object_property_sources(S_pre, n_leaf, [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])
$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_p, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
$named_reference_notice_object_static_properties(S_pre, n_leaf, [ppropertydesc_s])
$class_statics_valid(S_pre)
'''.strip().splitlines()

PROTOCOL = r'''
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_r, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_property_owner(S_pre, n_leaf, ppropertydesc_q, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p)
~$named_reference_notice_object_static_properties(S_pre, n_leaf, pclassdesc.PROPERTIES)
~$named_reference_notice_object_static_sources(S_pre, n_leaf, [CLASS_PROP_SOURCE ppropertyid_s])
~$named_reference_notice_object_sources(S_pre, n_leaf, ppropref.SOURCES)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--part', choices=('ingress',), default='ingress')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('same_class_mixed_direct_alias_stdclass_reference_notice_review_cases.json')
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
    reached = REACHED
    derived = PROTOCOL
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
