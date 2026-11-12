#!/usr/bin/env python3
"""Check four genuine static roots at the reference-Notice admission boundary."""
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
from finite_static_alias_stdclass_reference_notice_review_cases import CASES

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $fsn_output(pevent*) : ptbytes
def $fsn_output(eps) = eps
def $fsn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $fsn_output(pevent*)
dec $fsn_ingress(pstate) : bool
def $fsn_ingress(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $fsn_output(S.EVENTS) = $ptascii("A;")
def $fsn_ingress(S) = false -- otherwise
dec $fsn_seek(pstate, nat) : pstate
def $fsn_seek(S, n) = S
  -- if $fsn_ingress(S) \/ n = 0 \/ S.TODO = eps
def $fsn_seek(S, n) = $fsn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$fsn_ingress(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $fsn_seek(S, n) = S -- otherwise
'''

PRE = r'''
S_pre = $fsn_seek(S_initial, 1024)[.COMPLETION = NORMAL]
$fsn_ingress(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
$lookup(S_pre.ENV, $ptascii("third")) = (n_third_cv)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cv)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.STORE[n_third_cv] = DEFINED (POBJECT n_third)
S_pre.STORE[n_bad_cv] = DEFINED (PINT 17)
n_leaf =/= n_bad_cv /\ n_old =/= n_new /\ n_new =/= n_third
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$class_named(S_pre.CLASSNAMES, $ptascii("reviewalpha15")) = (porigin_alpha)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewbeta15")) = (porigin_beta)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewgamma15")) = (porigin_gamma)
$class_named(S_pre.CLASSNAMES, $ptascii("reviewdelta15")) = (porigin_delta)
$class_at(S_pre.CLASSES, porigin_alpha) = (pclassdesc_alpha)
$class_at(S_pre.CLASSES, porigin_beta) = (pclassdesc_beta)
$class_at(S_pre.CLASSES, porigin_gamma) = (pclassdesc_gamma)
$class_at(S_pre.CLASSES, porigin_delta) = (pclassdesc_delta)
pclassdesc_alpha.PROPERTIES = [ppropertydesc_alpha]
pclassdesc_beta.PROPERTIES = [ppropertydesc_beta]
pclassdesc_gamma.PROPERTIES = [ppropertydesc_gamma]
pclassdesc_delta.PROPERTIES = [ppropertydesc_delta]
ppropertyid_alpha = ppropertydesc_alpha.ORIGIN
ppropertyid_beta = ppropertydesc_beta.ORIGIN
ppropertyid_gamma = ppropertydesc_gamma.ORIGIN
ppropertyid_delta = ppropertydesc_delta.ORIGIN
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid_gamma, CLASS_PROP_SOURCE ppropertyid_alpha, CLASS_PROP_SOURCE ppropertyid_delta, CLASS_PROP_SOURCE ppropertyid_beta]
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_alpha)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_beta)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_gamma)
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid_delta)
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_alpha) = ({DECL ppropertyid_alpha, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_beta) = ({DECL ppropertyid_beta, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_gamma) = ({DECL ppropertyid_gamma, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_at(S_pre.CLASSSTATICS, ppropertyid_delta) = ({DECL ppropertyid_delta, STATE PROP_VALUE (ALIAS n_leaf)})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object_ancestors(S_pre, [n_root])
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
$reference_coercion_at(S_pre.REFCOERCIONS, n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf)
$heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 6
$heap_owners(H_pre, HOBJECT n_old) = 2
$heap_owners(H_pre, HOBJECT n_new) = 1
$heap_owners(H_pre, HOBJECT n_third) = 1
(HCELL n_leaf) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $class_statics_valid(S_pre) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''
~$named_reference_notice_object_static_source(S_pre, n_leaf)
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_singleton = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_alpha])}]]
$named_reference_notice_object_static_source(S_singleton, n_leaf)
$named_reference_notice_array(S_singleton, PARRAY n_root)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed']
    assert source.read_bytes() == CASES[native['id']]
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == digest(types.PHP)
    assert native['source_sha256'] == digest(source)
    directory = args.output.resolve()
    directory.mkdir(parents=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), provenance, source, types.PHP,
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py',
        'tests/semantics/finite_static_alias_stdclass_reference_notice_review_cases.py',
        'tests/semantics/finite_static_alias_stdclass_reference_notice_review_cases.json')]
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
    checks = [initial] + PRE + INGRESS
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    fixture_sha = digest(fixture)
    print(directory, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 480)
    stable = before == fingerprints() and digest(fixture) == fixture_sha
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'source': str(source), 'source_sha256': digest(source),
        'fixture_sha256': fixture_sha, 'conditions': len(checks), 'reached_conditions': len(PRE) + 1,
        'derived_conditions': len(INGRESS), 'heap_bindings': 1, 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('ingress', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
