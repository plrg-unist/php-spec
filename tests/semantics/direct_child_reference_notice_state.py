#!/usr/bin/env python3
"""Check real DIRECT child edges, nested COW and last-owner Notice cleanup."""
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
syntax pnrefstage = NR_PRE | NR_HANDLER | NR_RETURN | NR_THROW
dec $nr_output(pevent*) : ptbytes
def $nr_output(eps) = eps
def $nr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nr_output(pevent*)
dec $nr_stage(pstate, pnrefstage) : bool
def $nr_stage(S, NR_PRE) = $positional_reference_notice_pending(S)
def $nr_stage(S, NR_HANDLER) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $nr_output(S.EVENTS) = $ptascii("P;H;")
def $nr_stage(S, NR_RETURN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $nr_output(S.EVENTS) = $ptascii("P;H;F:5:5;T:15:5;")
def $nr_stage(S, NR_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $nr_stage(S, pnrefstage) = false -- otherwise
dec $nr_seek(pstate, pnrefstage, nat) : pstate
def $nr_seek(S, pnrefstage, n) = S
  -- if $nr_stage(S, pnrefstage) \/ n = 0
def $nr_seek(S, pnrefstage, n) = $nr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pnrefstage, $nabs($(n - 1)))
  -- if ~$nr_stage(S, pnrefstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nr_seek(S, pnrefstage, n) = $nr_seek($drive_steps(S, 1), pnrefstage, $nabs($(n - 1)))
  -- if ~$nr_stage(S, pnrefstage) /\ $(n > 0)
  -- if $throwable_pending(S.COMPLETION)
def $nr_seek(S, pnrefstage, n) = S -- otherwise
'''

CHECKS = r'''

S_pre_found = $nr_seek(S_normal_initial, NR_PRE, 1000)
S_pre = S_pre_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("seed")) = (n_seed)
$lookup(S_pre.ENV, $ptascii("child")) = eps /\ $lookup(S_pre.ENV, $ptascii("leaf")) = eps
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_child)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (PARRAY n_child))]
S_pre.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_leaf))]
S_pre.ARRAYS[n_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$node_children(S_pre, HARRAY n_root) = [HARRAY n_child, HARRAY n_child]
$node_children(S_pre, HARRAY n_child) = [HARRAY n_leaf]
$node_children(S_pre, HARRAY n_leaf) = eps
$heap_owners($heap_graph(S_pre), HARRAY n_root) = 3
$heap_owners($heap_graph(S_pre), HARRAY n_child) = 2
$heap_owners($heap_graph(S_pre), HARRAY n_leaf) = 1
$call_descriptors_valid(S_pre) /\ $heap_valid($heap_graph(S_pre))
n_private = |S_pre.STORE|
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_root) = 3
$heap_owners($heap_graph(S_notice), HARRAY n_child) = 2
$heap_owners($heap_graph(S_notice), HARRAY n_leaf) = 1
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S_pre.HELD
$error_call_valid(S_notice, perrorcall)
$call_descriptors_valid(S_notice) /\ $heap_valid($heap_graph(S_notice))
S_handler_found = $nr_seek(S_notice, NR_HANDLER, 1000)
S_handler = S_handler_found[.COMPLETION = NORMAL]
$nr_stage(S_handler, NR_HANDLER)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("source")) = eps
S_handler.STORE[n_private] = DEFINED (PARRAY n_root)
$heap_owners($heap_graph(S_handler), HCELL n_private) = 1
$heap_owners($heap_graph(S_handler), HARRAY n_root) = 2
$heap_owners($heap_graph(S_handler), HARRAY n_child) = 2
$heap_owners($heap_graph(S_handler), HARRAY n_leaf) = 1
S_handler.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_handler.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
S_handler.ARRAYS[n_leaf].ITEMS = S_pre.ARRAYS[n_leaf].ITEMS
$call_descriptors_valid(S_handler) /\ $heap_valid($heap_graph(S_handler))
S_returned_found = $nr_seek(S_handler, NR_RETURN, 2000)
S_returned = S_returned_found[.COMPLETION = NORMAL]
$nr_stage(S_returned, NR_RETURN)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_new_root)
n_new_root =/= n_root
S_returned.ARRAYS[n_new_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_new_child)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (PARRAY n_child))]
n_new_child =/= n_child
S_returned.ARRAYS[n_new_child].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_new_leaf))]
n_new_leaf =/= n_leaf
S_returned.ARRAYS[n_new_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 15))]
S_returned.STORE[n_copy] = DEFINED (PARRAY n_root)
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_child].ITEMS = S_pre.ARRAYS[n_child].ITEMS
S_returned.ARRAYS[n_leaf].ITEMS = S_pre.ARRAYS[n_leaf].ITEMS
$heap_owners($heap_graph(S_returned), HCELL n_private) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_root) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_new_root) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_child) = 3
$heap_owners($heap_graph(S_returned), HARRAY n_new_child) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_leaf) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_new_leaf) = 1
$call_descriptors_valid(S_returned) /\ $heap_valid($heap_graph(S_returned))
S_full = $drive(S_returned, 3000)
S_full.COMPLETION = NORMAL
$nr_output(S_full.EVENTS) = $ptascii("P;H;F:5:5;T:15:5;R:115:5:5:5:1;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PARRAY n_new_root)
S_full.ARRAYS[n_new_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 115))]
S_full.ARRAYS[n_leaf].ITEMS = S_pre.ARRAYS[n_leaf].ITEMS
$heap_owners($heap_graph(S_full), HARRAY n_root) = 1
$heap_owners($heap_graph(S_full), HARRAY n_new_root) = 1
$heap_owners($heap_graph(S_full), HARRAY n_child) = 3
$heap_owners($heap_graph(S_full), HARRAY n_leaf) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_notice, 1)
S_two = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_two = S_direct
S_throw_pre_found = $nr_seek(S_initial, NR_PRE, 1000)
S_throw_pre = S_throw_pre_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_throw_pre)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw phpType7_throw* n_argument_throw poperand_throw* porigin_throw? z_throw) :: ptask_throw*
S_throw_pre.RESULT = KNOWN (PARRAY n_throw_root)
$lookup(S_throw_pre.ENV, $ptascii("r")) = (n_r)
$lookup(S_throw_pre.ENV, $ptascii("saved")) = (n_saved_cell)
S_throw_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
S_throw_pre.ARRAYS[n_throw_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (DIRECT (PARRAY n_throw_child)), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (PARRAY n_throw_child))]
S_throw_pre.ARRAYS[n_throw_child].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_throw_leaf))]
S_throw_pre.ARRAYS[n_throw_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$heap_owners($heap_graph(S_throw_pre), HARRAY n_throw_root) = 2
$heap_owners($heap_graph(S_throw_pre), HARRAY n_throw_child) = 2
$heap_owners($heap_graph(S_throw_pre), HARRAY n_throw_leaf) = 1
n_throw_private = |S_throw_pre.STORE|
S_throw_notice_step = $drive(S_throw_pre, 1)
S_throw_notice_step.COMPLETION = BUDGET
S_throw_notice = S_throw_notice_step[.COMPLETION = NORMAL]
S_throw_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_throw) :: ptask_throw*
$heap_owners($heap_graph(S_throw_notice), HCELL n_throw_private) = 1
$heap_owners($heap_graph(S_throw_notice), HARRAY n_throw_root) = 2
$heap_owners($heap_graph(S_throw_notice), HARRAY n_throw_child) = 2
$heap_owners($heap_graph(S_throw_notice), HARRAY n_throw_leaf) = 1
S_throw_handler_found = $nr_seek(S_throw_notice, NR_HANDLER, 1000)
S_throw_handler = S_throw_handler_found[.COMPLETION = NORMAL]
$nr_stage(S_throw_handler, NR_HANDLER)
S_throw_handler.GLOBALTABLE = (psymboltable_throw)
$lookup(psymboltable_throw.ENV, $ptascii("source")) = eps
$heap_owners($heap_graph(S_throw_handler), HARRAY n_throw_root) = 1
$heap_owners($heap_graph(S_throw_handler), HARRAY n_throw_child) = 2
$heap_owners($heap_graph(S_throw_handler), HARRAY n_throw_leaf) = 1
$call_descriptors_valid(S_throw_handler) /\ $heap_valid($heap_graph(S_throw_handler))
S_throw_found = $nr_seek(S_throw_handler, NR_THROW, 1000)
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail_throw*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw, perrorcall_entered)
$throwable_live(S_throw, n_saved)
$heap_owners($heap_graph(S_throw), HCELL n_throw_private) = 1
$heap_owners($heap_graph(S_throw), HARRAY n_throw_root) = 1
$heap_owners($heap_graph(S_throw), HARRAY n_throw_child) = 2
$heap_owners($heap_graph(S_throw), HARRAY n_throw_leaf) = 1
S_cancel_step = $drive(S_throw, 1)
S_cancel_step.COMPLETION = BUDGET
S_cancel = S_cancel_step[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_saved) :: ptask_tail_throw*
S_cancel.ERRORHANDLER = S_throw_pre.ERRORHANDLER
S_cancel.RESULT = KNOWN PNULL /\ S_cancel.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_cancel), HCELL n_throw_private) = 0
$heap_owners($heap_graph(S_cancel), HARRAY n_throw_root) = 0
$heap_owners($heap_graph(S_cancel), HARRAY n_throw_child) = 0
$heap_owners($heap_graph(S_cancel), HARRAY n_throw_leaf) = 0
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_root) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_child) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_leaf) <- S_cancel.ALLOCATIONS)
S_cancel.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
$nr_output(S_cancel.EVENTS) = $ptascii("P;H;")
$throwable_live(S_cancel, n_saved)
$call_descriptors_valid(S_cancel) /\ $heap_valid($heap_graph(S_cancel))
'''.strip().splitlines()

PURE = r'''

$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_value(PARRAY n_root)
S_self = S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]]
~$named_reference_notice_array(S_self, PARRAY n_root)
S_cycle = S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_root))]]
~$named_reference_notice_array(S_cycle, PARRAY n_root)
S_retired = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HARRAY n_child)]
~$named_reference_notice_array(S_retired, PARRAY n_root)
S_outside = S_pre[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY |S_pre.ARRAYS|))]]
~$named_reference_notice_array(S_outside, PARRAY n_root)
S_raw = S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("x"))))]]
~$named_reference_notice_array(S_raw, PARRAY n_root)
S_request = S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("x"))))]]
~$named_reference_notice_array(S_request, PARRAY n_root)
S_nul = S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([0])))]]
~$named_reference_notice_array(S_nul, PARRAY n_root)
S_object = S_throw_pre[.ARRAYS[n_throw_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_saved))]]
~$named_reference_notice_array(S_object, PARRAY n_throw_root)
S_alias = $reference_cell(S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed)]], n_seed)
$named_reference_notice_array(S_alias, PARRAY n_root)
S_alias_array = S_alias[.STORE = $set_cell(S_alias.STORE, n_seed, DEFINED (PARRAY n_root))]
~$named_reference_notice_array(S_alias_array, PARRAY n_root)
S_alias_unit = S_alias[.NATIVEEXCESS = S_alias.NATIVEEXCESS ++ [HCELL n_seed]]
~$named_reference_notice_array(S_alias_unit, PARRAY n_root)
S_alias_prop = S_alias[.PROPREFS = [{CELL n_seed, SOURCES eps}]]
~$named_reference_notice_array(S_alias_prop, PARRAY n_root)
S_uninitialized = S_pre[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]]
~$named_reference_notice_array(S_uninitialized, PARRAY n_root)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='direct-child-reference-notice-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/direct_child_reference_notice_cases.json',
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
        rows = json.loads((ROOT / 'tests/semantics/direct_child_reference_notice_cases.json').read_bytes())
        assert {row['id'] for row in rows} == {'positional-shared-direct-subtree-cow', 'positional-direct-subtree-throw'}
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
        checks = ['S_normal_initial = ' + initials['positional-shared-direct-subtree-cow'],
                  'S_initial = ' + initials['positional-direct-subtree-throw']] + CHECKS + PURE
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'reached_conditions': len(CHECKS) + 2, 'derived_controls': len(PURE), 'sources': sources,
            'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    prepared = json.loads((directory / 'prepared.json').read_bytes())
    assert fixture_sha256 == prepared['fixture_sha256']
    command = [str(runner), *map(str, modules), str(directory / 'state.watsup')]
    process = recorder.recorded(command, directory / 'run', 600)
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = (process['exit'] == 0 and not process['timeout'] and stable
              and (directory / 'run.stdout').read_bytes() == b'true\n'
              and not (directory / 'run.stderr').read_bytes())
    (directory / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before,
        'inputs_stable': stable, 'module_count': len(modules), 'mode': 'AL/cache=false/det=true',
        'conditions': prepared['conditions'], 'reached_conditions': prepared['reached_conditions'], 'derived_controls': prepared['derived_controls'], 'fixture_sha256': fixture_sha256,
        'process': process, 'passed': passed,
        'scope': 'Actual shared DIRECT child2 and grandchild1 edges survive SEND transfer; selected nested COW preserves outside copies, and throw retires the last private cell/root/child/leaf. Derived graph/refusal controls carry zero native credit. No generic ownership or GC observer renewal.'}, indent=2) + '\n')
    print('direct child ownership/COW/cancellation', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
