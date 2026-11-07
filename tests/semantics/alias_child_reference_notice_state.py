#!/usr/bin/env python3
"""Check real array-valued cells, singleton/shared COW and Notice cleanup."""
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
  -- if $nr_output(S.EVENTS) = $ptascii("P;H;F:5:7:7;T:15:27:27:7;")
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

S_pre = $nr_seek(S_normal_initial, NR_PRE, 1000)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("shared")) = (n_shared)
$lookup(S_pre.ENV, $ptascii("single")) = eps
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("single"))) (ALIAS n_single), ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_shared), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_shared)]
S_pre.STORE[n_single] = DEFINED (PARRAY n_single_array)
S_pre.STORE[n_shared] = DEFINED (PARRAY n_shared_old)
S_pre.ARRAYS[n_single_array].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_single_leaf))]
S_pre.ARRAYS[n_single_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
S_pre.ARRAYS[n_shared_old].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_shared_old_leaf))]
S_pre.ARRAYS[n_shared_old_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$node_children(S_pre, HARRAY n_root) = [HCELL n_single, HCELL n_shared, HCELL n_shared]
$node_children(S_pre, HCELL n_single) = [HARRAY n_single_array]
$node_children(S_pre, HCELL n_shared) = [HARRAY n_shared_old]
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_single) = 1
$heap_owners(H_pre, HCELL n_shared) = 3
$heap_owners(H_pre, HARRAY n_single_array) = 1
$heap_owners(H_pre, HARRAY n_shared_old) = 1
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
$heap_owners(H_notice, HCELL n_shared) = 3
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S_pre.HELD
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_handler = $nr_seek(S_notice, NR_HANDLER, 1000)[.COMPLETION = NORMAL]
$nr_stage(S_handler, NR_HANDLER)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("source")) = eps
$lookup(psymboltable.ENV, $ptascii("shared")) = (n_shared)
S_handler.STORE[n_private] = DEFINED (PARRAY n_root)
S_handler.STORE[n_shared] = DEFINED (PARRAY n_shared_handler)
n_shared_handler =/= n_shared_old
S_handler.ARRAYS[n_shared_handler].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_handler_leaf))]
S_handler.ARRAYS[n_handler_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 7))]
$node_children(S_handler, HCELL n_shared) = [HARRAY n_shared_handler]
H_handler = $heap_graph(S_handler)
$heap_owners(H_handler, HARRAY n_root) = 2
$heap_owners(H_handler, HCELL n_single) = 1
$heap_owners(H_handler, HCELL n_shared) = 3
$heap_owners(H_handler, HARRAY n_shared_handler) = 1
~((HARRAY n_shared_old) <- S_handler.ALLOCATIONS)
~((HARRAY n_shared_old_leaf) <- S_handler.ALLOCATIONS)
$duplicate_item(S_handler, n_root, ALIAS n_single) = DIRECT (PARRAY n_single_array)
$duplicate_item(S_handler, n_root, ALIAS n_shared) = ALIAS n_shared
$call_descriptors_valid(S_handler) /\ $heap_valid(H_handler)
S_returned = $nr_seek(S_handler, NR_RETURN, 2000)[.COMPLETION = NORMAL]
$nr_stage(S_returned, NR_RETURN)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_new_root)
n_new_root =/= n_root
S_returned.ARRAYS[n_new_root].ITEMS = [ENTRY (KSTRING ($ptascii("single"))) (DIRECT (PARRAY n_single_new)), ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_shared), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_shared)]
n_single_new =/= n_single_array
S_returned.ARRAYS[n_single_new].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_single_new_leaf))]
n_single_new_leaf =/= n_single_leaf
S_returned.ARRAYS[n_single_new_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 15))]
S_returned.STORE[n_single] = S_pre.STORE[n_single]
S_returned.ARRAYS[n_single_array].ITEMS = S_pre.ARRAYS[n_single_array].ITEMS
S_returned.ARRAYS[n_single_leaf].ITEMS = S_pre.ARRAYS[n_single_leaf].ITEMS
S_returned.STORE[n_shared] = DEFINED (PARRAY n_shared_new)
n_shared_new =/= n_shared_handler
S_returned.ARRAYS[n_shared_new].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_shared_new_leaf))]
S_returned.ARRAYS[n_shared_new_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 27))]
$node_children(S_returned, HCELL n_shared) = [HARRAY n_shared_new]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_new_root) = 1
$heap_owners(H_returned, HCELL n_single) = 1
$heap_owners(H_returned, HCELL n_shared) = 5
$heap_owners(H_returned, HARRAY n_single_array) = 1
$heap_owners(H_returned, HARRAY n_single_new) = 1
$heap_owners(H_returned, HARRAY n_shared_new) = 1
~((HARRAY n_shared_handler) <- S_returned.ALLOCATIONS)
~((HARRAY n_handler_leaf) <- S_returned.ALLOCATIONS)
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_full = $drive(S_returned, 3000)
S_full.COMPLETION = NORMAL
$nr_output(S_full.EVENTS) = $ptascii("P;H;F:5:7:7;T:15:27:27:7;R:15:127:127:5:127:127:127:1;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PARRAY n_new_root)
S_full.STORE[n_shared] = DEFINED (PARRAY n_shared_new)
S_full.ARRAYS[n_shared_new_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 127))]
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_shared) = 5
$heap_owners(H_full, HARRAY n_shared_new) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_notice, 1)
S_two = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_two = S_direct
S_throw_pre = $nr_seek(S_initial, NR_PRE, 1000)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_throw_pre)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw phpType7_throw* n_argument_throw poperand_throw* porigin_throw? z_throw) :: ptask_throw*
S_throw_pre.RESULT = KNOWN (PARRAY n_throw_root)
$lookup(S_throw_pre.ENV, $ptascii("saved")) = (n_saved_cell)
S_throw_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
$lookup(S_throw_pre.ENV, $ptascii("r")) = (n_r)
S_throw_pre.ARRAYS[n_throw_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_throw_cell), ENTRY (KSTRING ($ptascii("right"))) (DIRECT (PARRAY n_throw_child))]
S_throw_pre.STORE[n_throw_cell] = DEFINED (PARRAY n_throw_child)
S_throw_pre.ARRAYS[n_throw_child].ITEMS = [ENTRY (KSTRING ($ptascii("node"))) (DIRECT (PARRAY n_throw_leaf))]
S_throw_pre.ARRAYS[n_throw_leaf].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$node_children(S_throw_pre, HARRAY n_throw_root) = [HCELL n_throw_cell, HARRAY n_throw_child]
$node_children(S_throw_pre, HCELL n_throw_cell) = [HARRAY n_throw_child]
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HARRAY n_throw_root) = 2
$heap_owners(H_throw_pre, HCELL n_throw_cell) = 1
$heap_owners(H_throw_pre, HARRAY n_throw_child) = 2
$heap_owners(H_throw_pre, HARRAY n_throw_leaf) = 1
n_throw_private = |S_throw_pre.STORE|
S_throw_step = $drive(S_throw_pre, 1)
S_throw_step.COMPLETION = BUDGET
S_throw_notice = S_throw_step[.COMPLETION = NORMAL]
S_throw_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_throw) :: ptask_throw*
H_throw_notice = $heap_graph(S_throw_notice)
$heap_owners(H_throw_notice, HCELL n_throw_private) = 1
$heap_owners(H_throw_notice, HCELL n_throw_cell) = 1
$heap_owners(H_throw_notice, HARRAY n_throw_child) = 2
S_throw_handler = $nr_seek(S_throw_notice, NR_HANDLER, 1000)[.COMPLETION = NORMAL]
$nr_stage(S_throw_handler, NR_HANDLER)
H_throw_handler = $heap_graph(S_throw_handler)
$heap_owners(H_throw_handler, HARRAY n_throw_root) = 1
$heap_owners(H_throw_handler, HARRAY n_throw_child) = 2
S_throw = $nr_seek(S_throw_handler, NR_THROW, 1000)[.COMPLETION = NORMAL]
$nr_stage(S_throw, NR_THROW)
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail_throw*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw, perrorcall_entered)
S_cancel_step = $drive(S_throw, 1)
S_cancel_step.COMPLETION = BUDGET
S_cancel = S_cancel_step[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_saved) :: ptask_tail_throw*
S_cancel.RESULT = KNOWN PNULL /\ S_cancel.BASE = BASE_VALUE (KNOWN PNULL)
H_cancel = $heap_graph(S_cancel)
$heap_owners(H_cancel, HCELL n_throw_private) = 0
$heap_owners(H_cancel, HARRAY n_throw_root) = 0
$heap_owners(H_cancel, HCELL n_throw_cell) = 0
$heap_owners(H_cancel, HARRAY n_throw_child) = 0
$heap_owners(H_cancel, HARRAY n_throw_leaf) = 0
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_root) <- S_cancel.ALLOCATIONS)
~((HCELL n_throw_cell) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_child) <- S_cancel.ALLOCATIONS)
~((HARRAY n_throw_leaf) <- S_cancel.ALLOCATIONS)
S_cancel.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
$nr_output(S_cancel.EVENTS) = $ptascii("P;H;")
$throwable_live(S_cancel, n_saved)
$call_descriptors_valid(S_cancel) /\ $heap_valid(H_cancel)
S_throw_full = $drive(S_cancel, 1000)
S_throw_full.COMPLETION = NORMAL
$nr_output(S_throw_full.EVENTS) = $ptascii("P;H;C:1:1:1:1;E:recovered;")
'''.strip().splitlines()

PURE = r'''

$named_reference_notice_array(S_pre, PARRAY n_root)
S_self = S_pre[.STORE = $set_cell(S_pre.STORE, n_single, DEFINED (PARRAY n_root))]
~$named_reference_notice_array(S_self, PARRAY n_root)
S_direct_cycle = S_pre[.ARRAYS[n_single_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_root))]]
~$named_reference_notice_array(S_direct_cycle, PARRAY n_root)
S_alias_cycle = S_pre[.ARRAYS[n_single_leaf].ITEMS = [ENTRY (KINT 0) (ALIAS n_single)]]
~$named_reference_notice_array(S_alias_cycle, PARRAY n_root)
S_unmarked = S_pre[.REFCELLS = eps]
~$named_reference_notice_array(S_unmarked, PARRAY n_root)
S_retired = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HCELL n_single)]
~$named_reference_notice_array(S_retired, PARRAY n_root)
$target_function(S_pre, pcalltarget) = (pfunction)
S_backed = S_pre[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_single, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_backed, PARRAY n_root)
S_container = S_pre[.CONTAINERINITS = [{CELL n_single, ARRAY n_single_array, SITE pfunction.ORIGIN, LINE 0}]]
~$named_reference_notice_array(S_container, PARRAY n_root)
S_propref = S_pre[.PROPREFS = [{CELL n_single, SOURCES eps}]]
~$named_reference_notice_array(S_propref, PARRAY n_root)
S_coercion = S_pre[.REFCOERCIONS = [{CELL n_single, SITE pfunction.ORIGIN, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_coercion, PARRAY n_root)
S_ref_retained = S_pre[.LITERALREFRETAINED = [n_single]]
~$named_reference_notice_array(S_ref_retained, PARRAY n_root)
S_ref_debt = S_pre[.LITERALREFDEBTS = [n_single]]
~$named_reference_notice_array(S_ref_debt, PARRAY n_root)
S_ref_unit = S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HCELL n_single]]
~$named_reference_notice_array(S_ref_unit, PARRAY n_root)
S_array_retired = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HARRAY n_single_array)]
~$named_reference_notice_array(S_array_retired, PARRAY n_root)
S_array_retained = S_pre[.LITERALARRAYRETAINED = [n_single_array]]
~$named_reference_notice_array(S_array_retained, PARRAY n_root)
S_array_debt = S_pre[.LITERALARRAYDEBTS = [n_single_array]]
~$named_reference_notice_array(S_array_debt, PARRAY n_root)
S_array_unit = S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HARRAY n_single_array]]
~$named_reference_notice_array(S_array_unit, PARRAY n_root)
S_immutable = S_pre[.ARRAYS[n_single_array] = $array_empty()][.GC.IMMUTABLE = S_pre.GC.IMMUTABLE ++ [n_single_array]]
~$named_reference_notice_array(S_immutable, PARRAY n_root)
S_pre.POOLS = ppool :: ppool_tail*
S_pool = S_pre[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_single_array)]] :: ppool_tail*]
~$named_reference_notice_array(S_pool, PARRAY n_root)
S_pool_root = S_pre[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_root)]] :: ppool_tail*]
~$named_reference_notice_array(S_pool_root, PARRAY n_root)
S_nul = S_pre[.ARRAYS[n_single_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([0])))]]
~$named_reference_notice_array(S_nul, PARRAY n_root)
S_object = S_throw_pre[.STORE = $set_cell(S_throw_pre.STORE, n_throw_cell, DEFINED (POBJECT n_saved))]
~$named_reference_notice_array(S_object, PARRAY n_throw_root)
'''.strip().splitlines()

NORMAL_END = CHECKS.index('S_throw_pre = $nr_seek(S_initial, NR_PRE, 1000)[.COMPLETION = NORMAL]')
NORMAL = CHECKS[:NORMAL_END]
THROW = CHECKS[NORMAL_END:]
GUARD_SETUP = (NORMAL[:NORMAL.index('n_private = |S_pre.STORE|')]
               + THROW[:THROW.index('n_throw_private = |S_throw_pre.STORE|')])
GROUPS = {
    'normal': ([('S_normal_initial', 'positional-singleton-shared-array-cell-cow')], NORMAL, []),
    'throw': ([('S_initial', 'positional-array-cell-throw')], THROW, []),
    'guards': ([('S_normal_initial', 'positional-singleton-shared-array-cell-cow'),
                ('S_initial', 'positional-array-cell-throw')], GUARD_SETUP, PURE),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    parser.add_argument('--group', choices=GROUPS, required=True)
    args = parser.parse_args()
    initial_rows, reached, derived = GROUPS[args.group]
    scope = {
        'normal': 'Actual private CELL transfer, singleton unwrap, repeated shared CELL identity, handler payload retargeting and nested COW preserve real owners and budget replay.',
        'throw': 'Actual ALIAS and DIRECT edges to one child retire with the last private root on supplied throw, preserving the old assignment target and skipping later sends.',
        'guards': 'Source-reached pre-SEND prefixes plus derived ordinary-cell, header and alternating-cycle refusals; no COW, cleanup or source agreement credit.',
    }[args.group]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='alias-child-reference-notice-' + args.group + '-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/alias_child_reference_notice_cases.json',
                       ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php',
                                     'frontend/target.php', 'frontend/wire.php')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
        assert prepared['group'] == args.group
    else:
        rows = json.loads((ROOT / 'tests/semantics/alias_child_reference_notice_cases.json').read_bytes())
        assert {row['id'] for row in rows} == {'positional-singleton-shared-array-cell-cow', 'positional-array-cell-throw'}
        rows = [row for row in rows if row['id'] in {case for _, case in initial_rows}]
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
        checks = [name + ' = ' + initials[case] for name, case in initial_rows] + reached + derived
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'group': args.group, 'conditions': len(checks), 'reached_conditions': len(initial_rows) + len(reached),
            'derived_controls': len(derived), 'heap_projections': sum(check.startswith('H_') for check in reached),
            'sources': sources,
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
        'group': args.group, 'conditions': prepared['conditions'], 'reached_conditions': prepared['reached_conditions'], 'derived_controls': prepared['derived_controls'],
        'heap_projections': prepared['heap_projections'], 'fixture_sha256': fixture_sha256,
        'process': process, 'passed': passed,
        'scope': scope}, indent=2) + '\n')
    print('array-cell', args.group, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
