#!/usr/bin/env python3
"""Check real object-valued alias cells, COW unwrapping and throw retirement."""
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
dec $aon_output(pevent*) : ptbytes
def $aon_output(eps) = eps
def $aon_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $aon_output(pevent*)
dec $aon_stage(pstate, nat) : bool
def $aon_stage(S, 0) = $positional_reference_notice_pending(S)
def $aon_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $aon_output(S.EVENTS) = $ptascii("H;")
def $aon_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $aon_output(S.EVENTS) = $ptascii("H;F;")
def $aon_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $aon_stage(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("take")
  -- if $aon_output(S.EVENTS) = $ptascii("U;")
def $aon_stage(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $aon_output(S.EVENTS) = $ptascii("U;")
def $aon_stage(S, n) = false -- otherwise
dec $aon_seek(pstate, nat, nat) : pstate
def $aon_seek(S, n_stage, n) = S
  -- if $aon_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $aon_seek(S, n_stage, n) = $aon_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$aon_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aon_seek(S, n_stage, n) = $aon_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$aon_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $aon_seek(S, n_stage, n) = S -- otherwise
'''

SHARED = r'''
S_pre = $aon_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("shared")) = (n_shared)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cell)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_replacement)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
S_pre.STORE[n_shared] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_pre.STORE[n_replacement] = DEFINED (POBJECT n_new)
n_old =/= n_new
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_shared), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_shared)]
$node_children(S_pre, HARRAY n_root) = [HCELL n_shared, HCELL n_shared]
$node_children(S_pre, HCELL n_shared) = [HOBJECT n_old]
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_shared) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2
$heap_owners(H_pre, HOBJECT n_new) = 1
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HCELL n_shared) = 3
$heap_owners(H_notice, HOBJECT n_old) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_handler = $aon_seek(S_notice, 1, 512)[.COMPLETION = NORMAL]
$aon_stage(S_handler, 1)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("source")) = eps
$lookup(psymboltable.ENV, $ptascii("shared")) = (n_shared)
S_handler.STORE[n_shared] = DEFINED (POBJECT n_new)
$node_children(S_handler, HCELL n_shared) = [HOBJECT n_new]
H_handler = $heap_graph(S_handler)
$heap_owners(H_handler, HARRAY n_root) = 2
$heap_owners(H_handler, HCELL n_shared) = 4
$heap_owners(H_handler, HOBJECT n_old) = 1
$heap_owners(H_handler, HOBJECT n_new) = 2
$call_descriptors_valid(S_handler) /\ $heap_valid(H_handler)
S_returned = $aon_seek(S_handler, 2, 512)[.COMPLETION = NORMAL]
$aon_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.STORE[n_shared] = DEFINED (POBJECT n_new)
$node_children(S_returned, HCELL n_shared) = [HOBJECT n_new]
$node_children(S_returned, HARRAY n_copied) = [HCELL n_shared, HCELL n_shared]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_shared) = 5
$heap_owners(H_returned, HOBJECT n_old) = 1
$heap_owners(H_returned, HOBJECT n_new) = 2
$heap_owners(H_returned, HCELL n_private) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()

UNWRAP = r'''
S_pre = $aon_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("held")) = (n_held)
$lookup(S_pre.ENV, $ptascii("single")) = eps
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_held] = DEFINED (POBJECT n_object)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_single)]
S_pre.STORE[n_single] = DEFINED (POBJECT n_object)
$node_children(S_pre, HCELL n_single) = [HOBJECT n_object]
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_single) = 1
$heap_owners(H_pre, HOBJECT n_object) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
S_unwrapped = $aon_seek(S_pre, 4, 512)[.COMPLETION = NORMAL]
$aon_stage(S_unwrapped, 4)
$lookup(S_unwrapped.ENV, $ptascii("v")) = (n_private)
S_unwrapped.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_unwrapped.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_object)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_unwrapped.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_unwrapped.STORE[n_single] = DEFINED (POBJECT n_object)
$node_children(S_unwrapped, HARRAY n_root) = [HCELL n_single]
$node_children(S_unwrapped, HARRAY n_copied) = [HOBJECT n_object]
$node_children(S_unwrapped, HCELL n_single) = [HOBJECT n_object]
H_unwrapped = $heap_graph(S_unwrapped)
$heap_owners(H_unwrapped, HARRAY n_root) = 1
$heap_owners(H_unwrapped, HARRAY n_copied) = 1
$heap_owners(H_unwrapped, HCELL n_single) = 1
$heap_owners(H_unwrapped, HOBJECT n_object) = 3
$call_descriptors_valid(S_unwrapped) /\ $heap_valid(H_unwrapped)
S_returned = $aon_seek(S_unwrapped, 5, 512)[.COMPLETION = NORMAL]
$aon_stage(S_returned, 5)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
S_returned.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (PINT 17)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.STORE[n_single] = DEFINED (POBJECT n_object)
$objectprops_at(S_returned.OBJECTPROPS, n_object) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 9)))}])
$node_children(S_returned, HARRAY n_copied) = eps
$node_children(S_returned, HCELL n_single) = [HOBJECT n_object]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HCELL n_single) = 1
$heap_owners(H_returned, HOBJECT n_object) = 2
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()

THROW = r'''
S_pre = $aon_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
$lookup(S_pre.ENV, $ptascii("weak")) = (n_weak_cell)
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
$lookup(S_pre.ENV, $ptascii("seed")) = eps
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
S_pre.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("direct"))) (DIRECT (POBJECT n_object))]
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_object)
$node_children(S_pre, HARRAY n_root) = [HCELL n_leaf, HCELL n_leaf, HOBJECT n_object]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_object]
S_pre.OBJECTS[n_weak] = WEAKREFERENCE (n_object)
$weakref_get(S_pre, n_weak) = POBJECT n_object
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 2
$heap_owners(H_pre, HCELL n_leaf) = 2
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
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HCELL n_leaf) = 2
$heap_owners(H_notice, HOBJECT n_object) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_throw = $aon_seek(S_notice, 3, 512)[.COMPLETION = NORMAL]
$aon_stage(S_throw, 3)
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail_throw*
perrorcall_entered.RESUME = perrorcall.RESUME
$error_entered_call_valid(S_throw, perrorcall_entered)
S_throw.STORE[n_private] = DEFINED (PARRAY n_root)
$weakref_get(S_throw, n_weak) = POBJECT n_object
H_throw = $heap_graph(S_throw)
$heap_owners(H_throw, HCELL n_private) = 1
$heap_owners(H_throw, HARRAY n_root) = 1
$heap_owners(H_throw, HCELL n_leaf) = 2
$heap_owners(H_throw, HOBJECT n_object) = 2
$call_descriptors_valid(S_throw) /\ $heap_valid(H_throw)
S_full = $drive(S_throw, 1000)
S_full.COMPLETION = NORMAL
$aon_output(S_full.EVENTS) = $ptascii("P;H;C:1:1:1:1:1;E;")
S_full.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
$weakref_get(S_full, n_weak) = PNULL
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_private) = 0
$heap_owners(H_full, HARRAY n_root) = 0
$heap_owners(H_full, HCELL n_leaf) = 0
$heap_owners(H_full, HOBJECT n_object) = 0
~((HCELL n_private) <- S_full.ALLOCATIONS)
~((HARRAY n_root) <- S_full.ALLOCATIONS)
~((HCELL n_leaf) <- S_full.ALLOCATIONS)
~((HOBJECT n_object) <- S_full.ALLOCATIONS)
$throwable_live(S_full, n_saved)
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
'''.strip().splitlines()

GROUPS = {
    'shared': ('positional-shared-object-cell-retarget-cow', SHARED),
    'unwrap': ('positional-singleton-object-cell-unwrap', UNWRAP),
    'throw': ('positional-mixed-object-cell-last-owner-throw', THROW),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS, required=True)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    case, reached = GROUPS[args.group]
    catalogue = Path(__file__).with_name('alias_stdclass_reference_notice_cases.json')
    row, = [row for row in json.loads(catalogue.read_bytes()) if row['id'] == case]
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    native_row, = [item for item in native['rows'] if item['id'] == case]
    source = Path(native_row['process']['command'][-1])
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['passed'] and native['mode'] == 'native-only' and native_row['passed']
    assert native['profile'] == profile and source.read_bytes() == row['source'].encode()
    assert native['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    assert native_row['process']['cwd'] == str(ROOT)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    directory = args.output or Path(tempfile.mkdtemp(prefix='alias-stdclass-reference-state-' + args.group + '-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [ROOT / 'spec/semantics/modules.json', runner, Path(__file__), catalogue, native_path, source,
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php', 'frontend/target.php',
        'frontend/wire.php', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
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
    checks = [initial] + reached
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    prepared = {'revision': revision, 'inputs': before, 'group': args.group, 'case': case, 'source': str(source),
        'conditions': len(checks), 'reached_conditions': len(checks), 'derived_conditions': 0,
        'heap_bindings': sum(check.startswith('H_') for check in reached),
        'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
    (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 480)
    stable = before == fingerprints() and prepared['fixture_sha256'] == hashlib.sha256(fixture.read_bytes()).hexdigest()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (directory / 'run.stdout').read_bytes() == b'true\n' and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable, module_count=len(modules),
        mode='AL/cache=false/det=true', process=process, source_agreements=0, passed=passed)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.group, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
