#!/usr/bin/env python3
"""Check singleton array-cell unwrapping and both real descendant COW edges."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import alias_child_reference_notice_state as notice
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
PREFIX = notice.PREFIX + r'''
dec $singleton_return(pstate) : bool
def $singleton_return(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $acquire_call_valid(S)
def $singleton_return(S) = false -- otherwise
dec $singleton_seek(pstate, nat) : pstate
def $singleton_seek(S, n) = S
  -- if $singleton_return(S) \/ n = 0 \/ S.TODO = eps
def $singleton_seek(S, n) = $singleton_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$singleton_return(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $singleton_seek(S, n) = $singleton_seek($drive_steps(S, 1), $nabs($(n - 1)))
  -- if ~$singleton_return(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $singleton_seek(S, n) = S -- otherwise
'''

CHECKS = r'''

S_pre_found = $nr_seek(S_initial, NR_PRE, 512)
S_pre_found.COMPLETION = BUDGET \/ S_pre_found.COMPLETION = NORMAL
S_pre = S_pre_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("child")) = eps /\ $lookup(S_pre.ENV, $ptascii("leaf")) = eps
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (ALIAS n_single)]
S_pre.STORE[n_single] = DEFINED (PARRAY n_child)
S_pre.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (PARRAY n_leaf))]
S_pre.ARRAYS[n_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$node_children(S_pre, HARRAY n_root) = [HCELL n_single]
$node_children(S_pre, HCELL n_single) = [HARRAY n_child]
$node_children(S_pre, HARRAY n_child) = [HARRAY n_leaf]
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_single) = 1
$heap_owners(H_pre, HARRAY n_child) = 1
$heap_owners(H_pre, HARRAY n_leaf) = 1
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HARRAY n_root) = 3
$heap_owners(H_notice, HCELL n_single) = 1
$heap_owners(H_notice, HARRAY n_child) = 1
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_returned_found = $singleton_seek(S_notice, 512)
S_returned_found.COMPLETION = BUDGET \/ S_returned_found.COMPLETION = NORMAL
S_returned = S_returned_found[.COMPLETION = NORMAL]
$singleton_return(S_returned)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_new_root)
n_new_root =/= n_root
S_returned.ARRAYS[n_new_root].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_new_child))]
n_new_child =/= n_child
S_returned.ARRAYS[n_new_child].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (PARRAY n_new_leaf))]
n_new_leaf =/= n_leaf
S_returned.ARRAYS[n_new_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 9))]
S_returned.STORE[n_copy] = DEFINED (PARRAY n_root)
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.STORE[n_single] = S_pre.STORE[n_single]
n_single <- S_returned.REFCELLS
S_returned.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
S_returned.ARRAYS[n_leaf].ITEMS = S_pre.ARRAYS[n_leaf].ITEMS
$node_children(S_returned, HARRAY n_new_root) = [HARRAY n_new_child]
$node_children(S_returned, HCELL n_single) = [HARRAY n_child]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_new_root) = 1
$heap_owners(H_returned, HCELL n_single) = 1
$heap_owners(H_returned, HARRAY n_child) = 1
$heap_owners(H_returned, HARRAY n_new_child) = 1
$heap_owners(H_returned, HARRAY n_leaf) = 1
$heap_owners(H_returned, HARRAY n_new_leaf) = 1
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_full = $drive(S_returned, 1000)
S_full.COMPLETION = NORMAL
$nr_output(S_full.EVENTS) = $ptascii("9:5;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PARRAY n_new_root)
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
S_eof = $nr_seek(S_full, NR_RETURN, 512)
S_eof = S_full
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_notice, 1)
S_two = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_two = S_direct
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='singleton-array-reference-notice-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(notice.__file__), ROOT / 'tests/semantics/alias_child_reference_notice_cases.json',
                       ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php',
                                     'frontend/target.php', 'frontend/wire.php')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        rows = json.loads((ROOT / 'tests/semantics/alias_child_reference_notice_cases.json').read_bytes())
        rows = [row for row in rows if row['id'] == 'positional-singleton-array-cell-nested-cow']
        assert len(rows) == 1
        initials, sources = {}, {}
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            for row in rows:
                source = directory / (row['id'] + '.php')
                source.write_bytes(row['source'].encode())
                assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
                sources[row['id']] = row['source_sha256']
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                initials[row['id']] = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
                    base64.b64encode(os.fsencode(source)).decode()) + ')'
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        checks = ['S_initial = ' + initials['positional-singleton-array-cell-nested-cow']] + CHECKS
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'reached_conditions': len(CHECKS) + 1, 'derived_controls': 0, 'heap_projections': 3, 'sources': sources,
            'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    prepared = json.loads((directory / 'prepared.json').read_bytes())
    assert fixture_sha256 == prepared['fixture_sha256']
    command = [str(runner), *map(str, modules), str(directory / 'state.watsup')]
    process = recorder.recorded(command, directory / 'run', 480)
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = (process['exit'] == 0 and not process['timeout'] and stable
              and (directory / 'run.stdout').read_bytes() == b'true\n'
              and not (directory / 'run.stderr').read_bytes())
    (directory / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before,
        'inputs_stable': stable, 'module_count': len(modules), 'mode': 'AL/cache=false/det=true',
        'conditions': prepared['conditions'], 'reached_conditions': prepared['reached_conditions'], 'derived_controls': prepared['derived_controls'], 'heap_projections': prepared['heap_projections'], 'fixture_sha256': fixture_sha256,
        'process': process, 'passed': passed,
        'scope': 'Actual singleton CELL unwrap becomes a DIRECT child edge at root COW; both child and leaf separate while the old CELL and graph remain singly owned. Real private SEND identity, completion, EOF seeker stop and zero/adjacent budget equality are checked. No complex-normal timeout or generic ownership/GC renewal.'}, indent=2) + '\n')
    print('singleton nested COW/EOF/budget', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
