#!/usr/bin/env python3
"""Check actual private-array/object last-owner cleanup and the new path boundary."""
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
import stdclass_reference_notice_state as notice

ROOT = Path(__file__).resolve().parents[2]
CASE = 'positional-direct-object-leaf-last-owner-throw'

REACHED = r'''
S_pre = $stdn_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_object))]
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("target")) = (n_target)
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
$lookup(S_pre.ENV, $ptascii("weak")) = (n_weak_cell)
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_target] = DEFINED (POBJECT n_object)
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
S_pre.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S_pre.OBJECTS[n_object] = STDINSTANCE
S_pre.OBJECTS[n_weak] = WEAKREFERENCE (n_object)
$node_children(S_pre, HARRAY n_root) = [HOBJECT n_object]
$node_children(S_pre, HOBJECT n_object) = eps
$node_children(S_pre, HOBJECT n_weak) = eps
$weakref_get(S_pre, n_weak) = POBJECT n_object
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 2
$heap_owners(H_pre, HOBJECT n_object) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$node_children(S_notice, HARRAY n_root) = [HOBJECT n_object]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HARRAY n_root) = 2
$heap_owners(H_notice, HOBJECT n_object) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_throw = $stdn_seek(S_notice, 3, 512)[.COMPLETION = NORMAL]
$stdn_stage(S_throw, 3)
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail_throw*
perrorcall_entered.RESUME = perrorcall.RESUME
$error_entered_call_valid(S_throw, perrorcall_entered)
S_throw.STORE[n_private] = DEFINED (PARRAY n_root)
$weakref_get(S_throw, n_weak) = POBJECT n_object
H_throw = $heap_graph(S_throw)
$heap_owners(H_throw, HCELL n_private) = 1
$heap_owners(H_throw, HARRAY n_root) = 1
$heap_owners(H_throw, HOBJECT n_object) = 1
$call_descriptors_valid(S_throw) /\ $heap_valid(H_throw)
S_full = $drive(S_throw, 1000)
S_full.COMPLETION = NORMAL
$stdn_output(S_full.EVENTS) = $ptascii("P;C:1:1:1;E;")
S_full.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
S_full.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S_full, n_weak) = PNULL
$node_children(S_full, HOBJECT n_weak) = eps
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_private) = 0
$heap_owners(H_full, HARRAY n_root) = 0
$heap_owners(H_full, HOBJECT n_object) = 0
~((HCELL n_private) <- S_full.ALLOCATIONS)
~((HARRAY n_root) <- S_full.ALLOCATIONS)
~((HOBJECT n_object) <- S_full.ALLOCATIONS)
$throwable_live(S_full, n_saved)
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_notice, 1)
S_split = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_split = S_direct
'''.strip().splitlines()

DERIVED = r'''
~$named_reference_notice_entries(S_pre, [ENTRY (KINT 0) (DIRECT (POBJECT n_object))])
$named_reference_notice_graph_entries(S_pre, [ENTRY (KINT 0) (DIRECT (POBJECT n_object))], [n_root])
~$named_reference_notice_object_ancestors(S_pre, [|S_pre.ARRAYS|])
S_immutable = S_pre[.ARRAYS[n_root] = $array_empty()][.GC.IMMUTABLE = S_pre.GC.IMMUTABLE ++ [n_root]]
~$named_reference_notice_object_ancestors(S_immutable, [n_root])
$named_reference_notice_array(S_immutable, PARRAY n_root)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='object-leaf-reference-notice-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    catalogue = ROOT / 'tests/semantics/object_leaf_reference_notice_cases.json'
    row, = [row for row in json.loads(catalogue.read_bytes()) if row['id'] == CASE]
    source = directory / (CASE + '.php')
    native_path = args.native_report.resolve() if args.native_report else None
    if native_path:
        native = json.loads(native_path.read_bytes())
        native_row, = [item for item in native['rows'] if item['id'] == CASE]
        source = Path(native_row['process']['command'][-1])
        assert native['passed'] and native_row['passed']
        assert source.read_bytes() == row['source'].encode()
    elif not args.prepared:
        source.write_bytes(row['source'].encode())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [ROOT / 'spec/semantics/modules.json', runner, Path(__file__),
        Path(notice.__file__), catalogue, source, ROOT / '_build/default/adapter/main.exe',
        types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php',
        'frontend/target.php', 'frontend/wire.php', 'tests/semantics/error_handler_run.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    if native_path:
        paths.append(native_path)
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        checks = ['S_initial = ' + initial] + REACHED + DERIVED
        (directory / 'state.watsup').write_text(notice.PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'conditions': len(checks),
            'reached_conditions': len(REACHED) + 1, 'derived_controls': len(DERIVED),
            'heap_projections': 4, 'source_sha256': row['source_sha256'], 'source_file': str(source),
            'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    assert fixture_sha256 == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(directory / 'state.watsup')], directory / 'run', 480)
    head_after = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_after == revision and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    (directory / 'report.json').write_text(json.dumps({**prepared, 'inputs_stable': stable,
        'head_stable': head_after == revision, 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'process': process, 'passed': passed,
        'scope': 'Actual sole private CELL-to-array-to-object retirement on supplied throw; complementary derived path/empty-immutable controls have no source agreement credit.'}, indent=2) + '\n')
    print('object-leaf', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
