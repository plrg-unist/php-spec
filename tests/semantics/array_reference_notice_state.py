#!/usr/bin/env python3
"""Reach owning-array Notice transfer and supplied-throw cell/table retirement."""
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
syntax pnrefstage = NR_PRE | NR_HANDLER | NR_THROW
dec $nr_output(pevent*) : ptbytes
def $nr_output(eps) = eps
def $nr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nr_output(pevent*)
dec $nr_stage(pstate, pnrefstage) : bool
def $nr_stage(S, NR_PRE) = $positional_reference_notice_pending(S)
def $nr_stage(S, NR_HANDLER) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $nr_output(S.EVENTS) = $ptascii("P;H;")
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
S_pre_found = $nr_seek(S_initial, NR_PRE, 1000)
S_pre = S_pre_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_array)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
S_pre.STORE[n_source] = DEFINED (PARRAY n_array)
S_pre.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 7))]
$heap_owners($heap_graph(S_pre), HARRAY n_array) = 2
S_pre.HELD = eps /\ S_pre.BASE = BASE_VALUE (KNOWN PNULL)
$call_descriptors_valid(S_pre) /\ $heap_valid($heap_graph(S_pre))
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
S_pre.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
n_private = |S_pre.STORE|
n_private =/= n_source
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) poperand_next* porigin? z
poperand_next* = poperand* ++ [REFERENCE n_private]
S_notice.STORE[n_private] = DEFINED (PARRAY n_array)
$call_reference_operand_valid(S_notice, REFERENCE n_private)
$named_reference_notice_operand(S_notice, REFERENCE n_private)
$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_array]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_array) = 2
(HCELL n_private) <- S_notice.ALLOCATIONS /\ (HARRAY n_array) <- S_notice.ALLOCATIONS
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = eps
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_handler_found = $nr_seek(S_notice, NR_HANDLER, 1000)
S_handler = S_handler_found[.COMPLETION = NORMAL]
$nr_stage(S_handler, NR_HANDLER)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("source")) = eps
~((HCELL n_source) <- S_handler.ALLOCATIONS)
S_handler.STORE[n_private] = DEFINED (PARRAY n_array)
S_handler.ARRAYS[n_array].ITEMS = S_pre.ARRAYS[n_array].ITEMS
$heap_owners($heap_graph(S_handler), HCELL n_private) = 1
$heap_owners($heap_graph(S_handler), HARRAY n_array) = 1
$call_descriptors_valid(S_handler) /\ $heap_valid($heap_graph(S_handler))
S_throw_found = $nr_seek(S_handler, NR_THROW, 1000)
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
perrorcall_entered.RESUME = perrorcall.RESUME
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps
$error_entered_call_valid(S_throw, perrorcall_entered)
$throwable_live(S_throw, n_saved)
$heap_owners($heap_graph(S_throw), HCELL n_private) = 1
$heap_owners($heap_graph(S_throw), HARRAY n_array) = 1
$nr_output(S_throw.EVENTS) = $ptascii("P;H;")
S_cancel_budget = $drive(S_throw, 1)
S_cancel_budget.COMPLETION = BUDGET
S_cancel = S_cancel_budget[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_saved) :: ptask_tail*
S_cancel.ERRORHANDLER = S_pre.ERRORHANDLER
S_cancel.RESULT = KNOWN PNULL /\ S_cancel.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_cancel), HCELL n_private) = 0
$heap_owners($heap_graph(S_cancel), HARRAY n_array) = 0
~((HCELL n_private) <- S_cancel.ALLOCATIONS)
~((HARRAY n_array) <- S_cancel.ALLOCATIONS)
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
$throwable_live(S_cancel, n_saved)
S_cancel.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
$nr_output(S_cancel.EVENTS) = $ptascii("P;H;")
S_zero = $drive(S_pre, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_pre
S_one = $drive(S_notice, 1)
S_two = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_two = S_direct
'''.strip().splitlines()

PURE = r'''
~$named_reference_notice_value(PARRAY n_array)
S_dead = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HARRAY n_array)]
~$named_reference_notice_operand(S_dead, KNOWN (PARRAY n_array))
~$positional_reference_notice_pending(S_dead)
~$named_reference_notice_operand(S_pre, KNOWN (PARRAY (|S_pre.ARRAYS|)))
$named_reference_notice_entries(S_notice, eps)
$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT PNULL), ENTRY (KINT 1) (DIRECT (PBOOL true)), ENTRY (KINT 2) (DIRECT (PINT 5)), ENTRY (KINT 3) (DIRECT (PFLOAT 0)), ENTRY (KINT 4) (DIRECT (PSTRING_CARRIER INTERNED_STRING eps))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (ALIAS n_private)])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (INDIRECT n_saved ($ptascii("x")))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) UNINITIALIZED])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT (PARRAY n_array))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT (POBJECT n_saved))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT PUNDEFINED)])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("x"))))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("x"))))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([0])))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([256])))])
$target_function(S_notice, pcalltarget) = (pfunction)
S_backed = S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_private, LINE 0, VALUE eps}]]
~$named_reference_notice_operand(S_backed, REFERENCE n_private)
~$error_call_valid(S_backed, perrorcall)
S_scalar_backed = S_backed[.STORE = $set_cell(S_backed.STORE, n_private, DEFINED (PINT 7))]
$named_reference_notice_operand(S_scalar_backed, REFERENCE n_private)
$positional_reference_notice_operands(S_notice, [REFERENCE n_private])
S_propref = S_notice[.PROPREFS = [{CELL n_private, SOURCES eps}]]
~$named_reference_notice_operand(S_propref, REFERENCE n_private)
S_coercion = S_notice[.REFCOERCIONS = [{CELL n_private, SITE pfunction.ORIGIN, LINE 0, VALUE eps}]]
~$named_reference_notice_operand(S_coercion, REFERENCE n_private)
S_retired = S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_private)]
~$named_reference_notice_operand(S_retired, REFERENCE n_private)
S_dead_child = S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HARRAY n_array)]
~$named_reference_notice_operand(S_dead_child, REFERENCE n_private)
~$error_call_valid(S_dead_child, perrorcall)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='array-reference-notice-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/array_reference_notice_cases.json',
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
        rows = [row for row in json.loads((ROOT / 'tests/semantics/array_reference_notice_cases.json').read_bytes())
                if row['id'] == 'positional-leaf-array-throw']
        assert len(rows) == 1
        checks = []
        sources = {}
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
                throw_initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
                    base64.b64encode(os.fsencode(source)).decode()) + ')'

        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        checks += ['S_initial = ' + throw_initial] + CHECKS + PURE
        (directory / 'throw.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'reached_conditions': len(CHECKS) + 1, 'pure_controls': len(PURE), 'sources': sources,
            'fixture_sha256': hashlib.sha256((directory / 'throw.watsup').read_bytes()).hexdigest()}, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'throw.watsup').read_bytes()).hexdigest()
    assert fixture_sha256 == json.loads((directory / 'prepared.json').read_bytes())['fixture_sha256']
    command = [str(runner), *map(str, modules), str(directory / 'throw.watsup')]
    process = recorder.recorded(command, directory / 'run', 360)
    stable = (before == fingerprints()
              and fixture_sha256 == hashlib.sha256((directory / 'throw.watsup').read_bytes()).hexdigest())
    passed = (process['exit'] == 0 and not process['timeout'] and stable
              and (directory / 'run.stdout').read_bytes().strip() == b'true'
              and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable,
              'module_count': len(modules), 'mode': 'AL/cache=false/det=true',
              'conditions': json.loads((directory / 'prepared.json').read_bytes())['conditions'],
              'reached_conditions': len(CHECKS) + 1, 'pure_controls': len(PURE),
              'fixture_sha256': fixture_sha256,
              'process': process, 'passed': passed,
              'scope': 'Actual flat-array positional Notice, RESULT-to-private-cell child ownership, source-unset survival and supplied-Throwable cell/table retirement; derived malformed/live/flat/backing controls carry zero native credit. Generic catch/return tails reuse prior laws.'}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('throw ownership/cancellation', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
