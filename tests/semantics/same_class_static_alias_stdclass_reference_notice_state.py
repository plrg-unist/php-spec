#!/usr/bin/env python3
"""Check same-class static sources, partial transfer and singleton COW."""
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
dec $ssan_output(pevent*) : ptbytes
def $ssan_output(eps) = eps
def $ssan_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ssan_output(pevent*)
dec $ssan_stage(pstate, nat) : bool
def $ssan_stage(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $ssan_output(S.EVENTS) = $ptascii("A;")
def $ssan_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;")
def $ssan_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;E;H;")
def $ssan_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;E;H;F;")
def $ssan_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1;T:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;P;")
def $ssan_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1;T:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;P;U:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;B;")
def $ssan_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1;T:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;P;U:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;B;41:41;N;Q;")
def $ssan_stage(S, 7) = true
  -- if S.CURRENT = eps
  -- if $ssan_output(S.EVENTS) = $ptascii("A;S;E;H;F;1:1:1;T:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;P;U:Cannot assign int to reference held by property StaticSlots19::$b of type stdClass;B;41:41;N;Q;K;")
def $ssan_stage(S, n) = false -- otherwise
dec $ssan_seek(pstate, nat, nat) : pstate
def $ssan_seek(S, n_stage, n) = S
  -- if $ssan_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $ssan_seek(S, n_stage, n) = $ssan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ssan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ssan_seek(S, n_stage, n) = $ssan_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$ssan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $ssan_seek(S, n_stage, n) = S -- otherwise
'''

CHECKS = r'''
S_pre = $ssan_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]
$ssan_stage(S_pre, 0)
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new] = DEFINED (POBJECT n_replacement)
S_pre.STORE[n_bad] = DEFINED (PINT 17)
$propref_at(S_pre.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a, CLASS_PROP_SOURCE ppropertyid_b])})
$property_declaring_class(S_pre.CLASSES, ppropertyid_a) = $property_declaring_class(S_pre.CLASSES, ppropertyid_b)
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf, HCELL n_leaf]
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$named_reference_notice_object_static_source(S_pre, n_leaf)
$named_reference_notice_array(S_pre, PARRAY n_root) /\ $positional_reference_notice_pending(S_pre)
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 4
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
S_self = $ssan_seek(S_notice, 1, 1536)[.COMPLETION = NORMAL]
$ssan_stage(S_self, 1)
S_self.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_self.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_b, CLASS_PROP_SOURCE ppropertyid_a])})
S_self.STORE[n_leaf] = S_pre.STORE[n_leaf]
$proprefs_valid(S_self) /\ $class_statics_valid(S_self) /\ $call_descriptors_valid(S_self)
S_handler = $ssan_seek(S_self, 2, 2048)[.COMPLETION = NORMAL]
$ssan_stage(S_handler, 2)
S_handler.CLASSSTATICS = S_self.CLASSSTATICS
$propref_at(S_handler.PROPREFS, n_leaf) = $propref_at(S_self.PROPREFS, n_leaf)
$propref_at(S_handler.PROPREFS, n_bad) = eps
S_handler.STORE[n_leaf] = S_pre.STORE[n_leaf]
S_handler.STORE[n_bad] = S_pre.STORE[n_bad]
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("leaf")) = eps
$named_reference_notice_array(S_handler, PARRAY n_root)
$proprefs_valid(S_handler) /\ $class_statics_valid(S_handler) /\ $call_descriptors_valid(S_handler)
S_returned = $ssan_seek(S_handler, 3, 1536)[.COMPLETION = NORMAL]
$ssan_stage(S_returned, 3)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$propref_at(S_returned.PROPREFS, n_leaf) = $propref_at(S_self.PROPREFS, n_leaf)
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 2
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_leaf) = 4
$heap_owners(H_returned, HOBJECT n_old) = 2
$proprefs_valid(S_returned) /\ $class_statics_valid(S_returned) /\ $call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_partial = $ssan_seek(S_returned, 4, 2048)[.COMPLETION = NORMAL]
$ssan_stage(S_partial, 4)
$class_static_roots(S_partial.CLASSSTATICS) = [HCELL n_new, HCELL n_leaf]
$propref_at(S_partial.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_b])})
$propref_at(S_partial.PROPREFS, n_new) = ({CELL n_new, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a])})
S_partial.STORE[n_leaf] = S_pre.STORE[n_leaf]
~$named_reference_notice_array(S_partial, PARRAY n_copied)
$proprefs_valid(S_partial) /\ $class_statics_valid(S_partial) /\ $call_descriptors_valid(S_partial)
S_final = $ssan_seek(S_partial, 5, 2048)[.COMPLETION = NORMAL]
$ssan_stage(S_final, 5)
$class_static_roots(S_final.CLASSSTATICS) = [HCELL n_new, HCELL n_new]
$propref_at(S_final.PROPREFS, n_leaf) = eps
$propref_at(S_final.PROPREFS, n_new) = ({CELL n_new, SOURCES ([CLASS_PROP_SOURCE ppropertyid_a, CLASS_PROP_SOURCE ppropertyid_b])})
S_final.STORE[n_leaf] = S_pre.STORE[n_leaf]
$named_reference_notice_object_static_source(S_final, n_new)
$named_reference_notice_array(S_final, PARRAY n_copied)
H_final = $heap_graph(S_final)
H_final = $heap_graph(S_final[.PROPREFS = eps])
$heap_owners(H_final, HCELL n_leaf) = 2
$heap_owners(H_final, HCELL n_new) = 3
$heap_owners(H_final, HOBJECT n_old) = 2
$proprefs_valid(S_final) /\ $class_statics_valid(S_final) /\ $call_descriptors_valid(S_final) /\ $heap_valid(H_final)
S_single = $ssan_seek(S_final, 6, 2048)[.COMPLETION = NORMAL]
$ssan_stage(S_single, 6)
~((HARRAY n_root) <- S_single.ALLOCATIONS)
S_single.STORE[n_leaf] = DEFINED (POBJECT n_old)
$propref_at(S_single.PROPREFS, n_leaf) = eps
$duplicate_item(S_single, n_copied, ALIAS n_leaf) = DIRECT (POBJECT n_old)
H_single = $heap_graph(S_single)
$heap_owners(H_single, HCELL n_leaf) = 1
$heap_owners(H_single, HCELL n_new) = 3
$heap_owners(H_single, HOBJECT n_old) = 2
$proprefs_valid(S_single) /\ $class_statics_valid(S_single) /\ $call_descriptors_valid(S_single) /\ $heap_valid(H_single)
S_snapshot = $ssan_seek(S_single, 7, 1536)[.COMPLETION = NORMAL]
$ssan_stage(S_snapshot, 7)
$lookup(S_snapshot.ENV, $ptascii("snapshot")) = (n_snapshot_cell)
S_snapshot.STORE[n_snapshot_cell] = DEFINED (PARRAY n_snapshot)
n_snapshot =/= n_copied
S_snapshot.ARRAYS[n_copied].ITEMS = S_returned.ARRAYS[n_copied].ITEMS
S_snapshot.ARRAYS[n_snapshot].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 13))]
H_snapshot = $heap_graph(S_snapshot)
$heap_owners(H_snapshot, HCELL n_leaf) = 1
$heap_owners(H_snapshot, HOBJECT n_old) = 3
$proprefs_valid(S_snapshot) /\ $class_statics_valid(S_snapshot) /\ $call_descriptors_valid(S_snapshot) /\ $heap_valid(H_snapshot)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    catalogue = Path(__file__).with_name('same_class_static_alias_stdclass_reference_notice_cases.json')
    row, = json.loads(catalogue.read_bytes())
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    native_row, = [item for item in native['records'] if item['id'] == row['id']]
    source = Path(native_row['command'][-1])
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['mode'] == 'native-first' and native_row['passed']
    assert native['profile'] == profile and source.read_bytes() == row['source'].encode()
    assert native['runtime_sha256'] == digest(types.PHP) and native_row['cwd'] == str(ROOT)
    assert digest(source) == row['source_sha256']
    directory = args.output or Path(tempfile.mkdtemp(prefix='same-class-static-reference-state-', dir=ROOT / '.tools'))
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
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 1200)
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
