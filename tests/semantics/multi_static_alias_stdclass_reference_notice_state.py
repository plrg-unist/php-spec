#!/usr/bin/env python3
"""Check finite static-source transfer, failure order and real shared-cell owners."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $msan_output(pevent*) : ptbytes
def $msan_output(eps) = eps
def $msan_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $msan_output(pevent*)
dec $msan_stage(pstate, nat) : bool
def $msan_stage(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $msan_output(S.EVENTS) = $ptascii("A;")
def $msan_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $msan_output(S.EVENTS) = $ptascii("A;P;")
def $msan_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $msan_output(S.EVENTS) = $ptascii("A;P;Cannot assign int to reference held by property Third15::$p of type stdClass;B;J;")
def $msan_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $msan_output(S.EVENTS) = $ptascii("A;P;Cannot assign int to reference held by property Third15::$p of type stdClass;B;J;Q;")
def $msan_stage(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $msan_output(S.EVENTS) = $ptascii("A;P;Cannot assign int to reference held by property Third15::$p of type stdClass;B;J;Q;Cannot assign int to reference held by property Third15::$p of type stdClass;R;")
def $msan_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $msan_output(S.EVENTS) = $ptascii("A;P;Cannot assign int to reference held by property Third15::$p of type stdClass;B;J;Q;Cannot assign int to reference held by property Third15::$p of type stdClass;R;T;F;")
def $msan_stage(S, n) = false -- otherwise
dec $msan_seek(pstate, nat, nat) : pstate
def $msan_seek(S, n_stage, n) = S
  -- if $msan_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $msan_seek(S, n_stage, n) = $msan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$msan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $msan_seek(S, n_stage, n) = $msan_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$msan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $msan_seek(S, n_stage, n) = S -- otherwise
'''

CHECKS = r'''
S_pre = $msan_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]
$msan_stage(S_pre, 0)
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("shared")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("first")) = (n_first)
$lookup(S_pre.ENV, $ptascii("second")) = (n_second)
$lookup(S_pre.ENV, $ptascii("third")) = (n_third)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_first] = DEFINED (POBJECT n_first_object)
S_pre.STORE[n_second] = DEFINED (POBJECT n_second_object)
S_pre.STORE[n_third] = DEFINED (POBJECT n_third_object)
S_pre.STORE[n_bad] = DEFINED (PINT 31)
$propref_at(S_pre.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE p_first, CLASS_PROP_SOURCE p_second, CLASS_PROP_SOURCE p_third])})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf, HCELL n_leaf]
$named_reference_notice_object_static_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root) /\ $positional_reference_notice_pending(S_pre)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_leaf)]
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 6
$heap_owners(H_pre, HOBJECT n_old) = 2
$proprefs_valid(S_pre) /\ $class_statics_valid(S_pre) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_one = $drive(S_pre, 1)
S_one.COMPLETION = BUDGET
S_notice = S_one[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
S_first = $msan_seek(S_notice, 1, 1536)[.COMPLETION = NORMAL]
$msan_stage(S_first, 1)
$propref_at(S_first.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE p_third, CLASS_PROP_SOURCE p_second])})
$propref_at(S_first.PROPREFS, n_first) = ({CELL n_first, SOURCES ([CLASS_PROP_SOURCE p_first])})
$class_static_roots(S_first.CLASSSTATICS) = [HCELL n_first, HCELL n_leaf, HCELL n_leaf]
S_first.STORE[n_leaf] = S_pre.STORE[n_leaf]
$named_reference_notice_array(S_first, PARRAY n_root)
H_first = $heap_graph(S_first)
H_first = $heap_graph(S_first[.PROPREFS = eps])
$heap_owners(H_first, HCELL n_leaf) = 5
$heap_owners(H_first, HOBJECT n_old) = 2
$proprefs_valid(S_first) /\ $class_statics_valid(S_first) /\ $call_descriptors_valid(S_first) /\ $heap_valid(H_first)
S_failed = $msan_seek(S_first, 2, 2048)[.COMPLETION = NORMAL]
$msan_stage(S_failed, 2)
S_failed.CLASSSTATICS = S_first.CLASSSTATICS
$propref_at(S_failed.PROPREFS, n_leaf) = $propref_at(S_first.PROPREFS, n_leaf)
$propref_at(S_failed.PROPREFS, n_bad) = eps
S_failed.STORE[n_leaf] = S_pre.STORE[n_leaf]
S_failed.STORE[n_bad] = S_pre.STORE[n_bad]
$named_reference_notice_array(S_failed, PARRAY n_root)
$proprefs_valid(S_failed) /\ $class_statics_valid(S_failed) /\ $call_descriptors_valid(S_failed)
S_second = $msan_seek(S_failed, 3, 1024)[.COMPLETION = NORMAL]
$msan_stage(S_second, 3)
$propref_at(S_second.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE p_third])})
$propref_at(S_second.PROPREFS, n_second) = ({CELL n_second, SOURCES ([CLASS_PROP_SOURCE p_second])})
$class_static_roots(S_second.CLASSSTATICS) = [HCELL n_first, HCELL n_second, HCELL n_leaf]
S_second.STORE[n_leaf] = S_pre.STORE[n_leaf]
H_second = $heap_graph(S_second)
$heap_owners(H_second, HCELL n_leaf) = 4
$named_reference_notice_array(S_second, PARRAY n_root)
$proprefs_valid(S_second) /\ $class_statics_valid(S_second) /\ $call_descriptors_valid(S_second) /\ $heap_valid(H_second)
S_final = $msan_seek(S_second, 4, 2048)[.COMPLETION = NORMAL]
$msan_stage(S_final, 4)
$propref_at(S_final.PROPREFS, n_leaf) = eps
$propref_at(S_final.PROPREFS, n_third) = ({CELL n_third, SOURCES ([CLASS_PROP_SOURCE p_third])})
$class_static_roots(S_final.CLASSSTATICS) = [HCELL n_first, HCELL n_second, HCELL n_third]
S_final.STORE[n_leaf] = S_pre.STORE[n_leaf]
$node_children(S_final, HCELL n_leaf) = [HOBJECT n_old]
H_final = $heap_graph(S_final)
H_final = $heap_graph(S_final[.PROPREFS = eps])
$heap_owners(H_final, HCELL n_leaf) = 3
$heap_owners(H_final, HOBJECT n_old) = 2
$named_reference_notice_array(S_final, PARRAY n_root)
$proprefs_valid(S_final) /\ $class_statics_valid(S_final) /\ $call_descriptors_valid(S_final) /\ $heap_valid(H_final)
S_returned = $msan_seek(S_final, 5, 2048)[.COMPLETION = NORMAL]
$msan_stage(S_returned, 5)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.STORE[n_leaf] = DEFINED (PINT 17)
$propref_at(S_returned.PROPREFS, n_leaf) = eps
S_returned.STORE[n_first] = S_pre.STORE[n_first]
S_returned.STORE[n_second] = S_pre.STORE[n_second]
S_returned.STORE[n_third] = S_pre.STORE[n_third]
$class_static_roots(S_returned.CLASSSTATICS) = [HCELL n_first, HCELL n_second, HCELL n_third]
$node_children(S_returned, HCELL n_leaf) = eps
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_leaf) = 5
$heap_owners(H_returned, HOBJECT n_old) = 1
$heap_owners(H_returned, HCELL n_private) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$proprefs_valid(S_returned) /\ $class_statics_valid(S_returned) /\ $call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    catalogue = Path(__file__).with_name('multi_static_alias_stdclass_reference_notice_cases.json')
    row = json.loads(catalogue.read_bytes())[0]
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    native_row, = [item for item in native['records'] if item['id'] == row['id']]
    source = Path(native_row['command'][-1])
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['passed'] and native['mode'] == 'native-first' and native_row['passed']
    assert native['profile'] == profile and source.read_bytes() == row['source'].encode()
    assert native['runtime_sha256'] == digest(types.PHP) and native_row['cwd'] == str(ROOT)
    assert digest(source) == row['source_sha256']
    directory = args.output or Path(tempfile.mkdtemp(prefix='multi-static-alias-stdclass-reference-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [ROOT / 'spec/semantics/modules.json', runner, Path(__file__), catalogue, native_path, source,
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php', 'frontend/target.php',
        'frontend/wire.php', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): digest(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], directory / 'frontend')
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
    checks = [initial] + CHECKS
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    prepared = {'revision': revision, 'inputs': before, 'case': row['id'], 'source': str(source),
        'conditions': len(checks), 'reached_conditions': len(checks), 'derived_conditions': 0,
        'heap_bindings': sum(check.startswith('H_') and ' = $heap_graph(S_' in check and '[.PROPREFS' not in check for check in CHECKS),
        'fixture_sha256': digest(fixture)}
    (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 480)
    stable = before == fingerprints() and prepared['fixture_sha256'] == digest(fixture)
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (directory / 'run.stdout').read_bytes() == b'true\n' and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable, module_count=len(modules),
        mode='AL/cache=false/det=true', process=process, source_agreements=0, passed=passed)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(row['id'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
