#!/usr/bin/env python3
"""Reach a genuine named reference-send Notice and supplied-throw cancellation."""
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
syntax pnrefstage = NR_PRE | NR_NOTICE | NR_HANDLER | NR_THROW
dec $nr_output(pevent*) : ptbytes
def $nr_output(eps) = eps
def $nr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nr_output(pevent*)
def $nr_output(pevent :: pevent_tail*) = $nr_output(pevent_tail*) -- otherwise
dec $nr_stage(pstate, pnrefstage) : bool
def $nr_stage(S, NR_PRE) = $named_reference_notice_pending(S)
def $nr_stage(S, NR_NOTICE) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = NAMED_ARGS pcalltarget phpType7* n pnamedargs porigin? z
def $nr_stage(S, NR_HANDLER) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $nr_output(S.EVENTS) = $ptascii("P;H:8:7:1;")
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
$named_reference_notice_pending(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget phpType7* n_argument pnamedargs porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PINT 7)
n_private = |S_pre.STORE|
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
$lookup(S_pre.ENV, $ptascii("v")) = (n_v)
S_pre.STORE[n_v] = DEFINED (PINT 55)
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget phpType7* $(n_argument + 1) pnamedargs_next porigin? z
$named_slot_at(pnamedargs_next.SLOTS, 0) = NAMED_SENT (REFERENCE n_private)
S_notice.STORE[n_private] = DEFINED (PINT 7)
$call_reference_operand_valid(S_notice, REFERENCE n_private)
$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_private]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S_pre.HELD
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
S_handler_found = $nr_seek(S_notice, NR_HANDLER, 1000)
S_handler = S_handler_found[.COMPLETION = NORMAL]
$nr_stage(S_handler, NR_HANDLER)
$heap_owners($heap_graph(S_handler), HCELL n_private) = 1
$call_descriptors_valid(S_handler)
S_throw_found = $nr_seek(S_handler, NR_THROW, 1000)
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
perrorcall_entered.RESUME = perrorcall.RESUME
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps
$error_entered_call_valid(S_throw, perrorcall_entered)
$throwable_live(S_throw, n_saved)
$heap_owners($heap_graph(S_throw), HCELL n_private) = 1
$nr_output(S_throw.EVENTS) = $ptascii("P;H:8:7:1;")
S_throw.STORE[n_v] = DEFINED (PINT 55)
S_cancel_budget = $drive(S_throw, 1)
S_cancel_budget.COMPLETION = BUDGET
S_cancel = S_cancel_budget[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_saved) :: ptask_tail*
S_cancel.ERRORHANDLER = S_pre.ERRORHANDLER
S_cancel.RESULT = KNOWN PNULL /\ S_cancel.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_cancel), HCELL n_private) = 0
$throwable_live(S_cancel, n_saved)
S_cancel.STORE[n_v] = DEFINED (PINT 55)
$call_descriptors_valid(S_cancel)
S_full = $drive(S_pre, 10000)
S_full.COMPLETION = NORMAL
$nr_output(S_full.EVENTS) = $ptascii("P;H:8:7:1;C:1:1:1;E:56;")
S_full.STORE[n_v] = DEFINED (PINT 56)
$lookup(S_full.ENV, $ptascii("e")) = (n_e)
S_full.STORE[n_e] = DEFINED (POBJECT n_saved)
$heap_owners($heap_graph(S_full), HCELL n_private) = 0
$call_descriptors_valid(S_full) /\ $heap_valid($heap_prune($heap_graph(S_full)))
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
$drive(S_notice, 10000) = S_full
$drive(S_cancel, 10000) = S_full
$drive($drive(S_throw, 0)[.COMPLETION = NORMAL], 10000) = S_full
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='named-reference-send-notice-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/named_reference_send_notice_cases.json',
                       ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        rows = json.loads(paths[-4].read_bytes())
        checks = []
        sources = {}
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            for index, row in enumerate(rows):
                source = directory / (row['id'] + '.php')
                source.write_bytes(row['source'].encode())
                assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
                sources[row['id']] = row['source_sha256']
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
                    base64.b64encode(os.fsencode(source)).decode()) + ')'
                if row['id'] == 'named-reference-return-throw':
                    throw_initial = initial
                    continue
                state = 'S_positive' + str(index)
                expected = 'NAMED_POSITION 0' if index == 0 else 'NAMED_EXTRA $ptascii("tail")'
                value = '7' if index == 0 else '9'
                checks += [state + '_initial = ' + initial,
                           state + '_found = $nr_seek(' + state + '_initial, NR_PRE, 1000)',
                           state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
                           '$named_reference_notice_pending(' + state + ')',
                           state + '.RESULT = KNOWN (PINT ' + value + ')',
                           state + '.TODO = (NAMED_SEND pcalltarget_positive' + str(index)
                           + ' phpType7_positive' + str(index) + '* n_positive' + str(index)
                           + ' pnamedargs_positive' + str(index) + ' porigin_positive' + str(index)
                           + '? z_positive' + str(index) + ') :: ptask_positive' + str(index) + '*',
                           '$named_can_store(pnamedargs_positive' + str(index) + ', ' + expected + ')']
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        checks += ['S_initial = ' + throw_initial] + CHECKS
        (directory / 'throw.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'sources': sources}, indent=2) + '\n')
    if args.prepare_only:
        return True
    command = [str(runner), *map(str, modules), str(directory / 'throw.watsup')]
    process = recorder.recorded(command, directory / 'run', 120)
    stable = before == fingerprints()
    passed = (process['exit'] == 0 and not process['timeout'] and stable
              and (directory / 'run.stdout').read_bytes().strip() == b'true'
              and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable,
              'module_count': len(modules), 'mode': 'AL/cache=false/det=true',
              'conditions': json.loads((directory / 'prepared.json').read_bytes())['conditions'],
              'process': process, 'passed': passed,
              'scope': 'Actual named scalar reference-send Notice with supplied saved-Throwable cancellation; zero native reexecutions.'}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('throw ownership/cancellation', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
