#!/usr/bin/env python3
"""Check completed producer-CV cleanup and the outer Notice snapshot."""
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
syntax pncvstage = NCV_PRE | NCV_HANDLER | NCV_THROW
dec $ncv_output(pevent*) : ptbytes
def $ncv_output(eps) = eps
def $ncv_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ncv_output(pevent*)
dec $ncv_stage(pstate, pncvstage) : bool
def $ncv_stage(S, NCV_PRE) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
def $ncv_stage(S, NCV_HANDLER) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $ncv_output(S.EVENTS) = $ptascii("P:seed;H;")
def $ncv_stage(S, NCV_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $ncv_stage(S, pncvstage) = false -- otherwise
dec $ncv_seek(pstate, pncvstage, nat) : pstate
def $ncv_seek(S, pncvstage, n) = S
  -- if $ncv_stage(S, pncvstage) \/ n = 0
def $ncv_seek(S, pncvstage, n) = $ncv_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pncvstage, $nabs($(n - 1)))
  -- if ~$ncv_stage(S, pncvstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ncv_seek(S, pncvstage, n) = $ncv_seek($drive_steps(S, 1), pncvstage, $nabs($(n - 1)))
  -- if ~$ncv_stage(S, pncvstage) /\ $(n > 0)
  -- if $throwable_pending(S.COMPLETION)
def $ncv_seek(S, pncvstage, n) = S -- otherwise
'''

CHECKS = r'''
S_normal_found = $ncv_seek(S_normal_initial, NCV_PRE, 1000)
S_normal = S_normal_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_normal)
S_normal.TODO = (CALL_SEND pcalltarget_normal phpType7_normal* 0 poperand_normal* porigin_normal? z_normal) :: ptask_normal*
S_normal.RESULT = KNOWN (PINT 5)
S_normal.CURRENT = eps /\ S_normal.FRAMES = eps
$call_argument_expression(S_normal, porigin_normal?, 0) = NExprFuncCall phpType19_normal (SEQUENCE phpType7_inner_normal*) metadata_call_normal
phpType7_inner_normal* = [NArg ABSENT (NExprVariable (BYTES text_normal) metadata_cv_normal) (BOOLEAN false) (BOOLEAN false) metadata_arg_normal]
$lookup(S_normal.ENV, $ptascii("input")) = (n_input_normal)
$lookup(S_normal.ENV, $ptascii("keep")) = (n_input_normal)
S_normal.STORE[n_input_normal] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_normal), HCELL n_input_normal) = 2
$call_descriptors_valid(S_normal) /\ $heap_valid($heap_graph(S_normal))
S_pre_found = $ncv_seek(S_initial, NCV_PRE, 1000)
S_pre = S_pre_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("made")))
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$call_argument_expression(S_pre, porigin?, 0) = NExprFuncCall phpType19 (SEQUENCE phpType7_inner*) metadata_call
phpType7_inner* = [NArg ABSENT (NExprVariable (BYTES text_cv) metadata_cv) (BOOLEAN false) (BOOLEAN false) metadata_arg]
$lookup(S_pre.ENV, $ptascii("input")) = (n_input)
S_pre.STORE[n_input] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("made")))
$call_reference_operand_valid(S_pre, REFERENCE n_input)
$heap_owners($heap_graph(S_pre), HCELL n_input) = 1
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
S_pre.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
n_private = |S_pre.STORE|
n_private =/= n_input
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* 1 ([REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("made")))
$call_reference_operand_valid(S_notice, REFERENCE n_private)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HCELL n_input) = 1
(HCELL n_private) <- S_notice.ALLOCATIONS
$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_private]
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_handler_found = $ncv_seek(S_notice, NCV_HANDLER, 1000)
S_handler = S_handler_found[.COMPLETION = NORMAL]
$ncv_stage(S_handler, NCV_HANDLER)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("input")) = eps
$heap_owners($heap_graph(S_handler), HCELL n_input) = 0
~((HCELL n_input) <- S_handler.ALLOCATIONS)
S_handler.STORE[n_private] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("made")))
$heap_owners($heap_graph(S_handler), HCELL n_private) = 1
$call_descriptors_valid(S_handler) /\ $heap_valid($heap_graph(S_handler))
S_throw_found = $ncv_seek(S_handler, NCV_THROW, 1000)
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
perrorcall_entered.RESUME = perrorcall.RESUME
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps
$lookup(S_throw.ENV, $ptascii("input")) = eps
$error_entered_call_valid(S_throw, perrorcall_entered)
$throwable_live(S_throw, n_saved)
$heap_owners($heap_graph(S_throw), HCELL n_private) = 1
S_throw.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
S_cancel_budget = $drive(S_throw, 1)
S_cancel_budget.COMPLETION = BUDGET
S_cancel = S_cancel_budget[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_saved) :: ptask_tail*
S_cancel.ERRORHANDLER = S_pre.ERRORHANDLER
$heap_owners($heap_graph(S_cancel), HCELL n_private) = 0
~((HCELL n_private) <- S_cancel.ALLOCATIONS)
~((HCELL n_input) <- S_cancel.ALLOCATIONS)
$throwable_live(S_cancel, n_saved)
S_cancel.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
$call_descriptors_valid(S_cancel) /\ $heap_valid($heap_graph(S_cancel))
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
        prefix='producer-cv-reference-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/producer_cv_reference_notice_cases.json',
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
        rows = json.loads((ROOT / 'tests/semantics/producer_cv_reference_notice_cases.json').read_bytes())
        assert {row['id'] for row in rows} == {'positional-producer-cv-snapshot', 'positional-producer-cv-throw'}
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
        checks = ['S_normal_initial = ' + initials['positional-producer-cv-snapshot'],
                  'S_initial = ' + initials['positional-producer-cv-throw']] + CHECKS
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'sources': sources,
            'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    prepared = json.loads((directory / 'prepared.json').read_bytes())
    assert fixture_sha256 == prepared['fixture_sha256']
    command = [str(runner), *map(str, modules), str(directory / 'state.watsup')]
    process = recorder.recorded(command, directory / 'run', 360)
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = (process['exit'] == 0 and not process['timeout'] and stable
              and (directory / 'run.stdout').read_bytes() == b'true\n'
              and not (directory / 'run.stderr').read_bytes())
    (directory / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before,
        'inputs_stable': stable, 'module_count': len(modules), 'mode': 'AL/cache=false/det=true',
        'conditions': prepared['conditions'], 'fixture_sha256': fixture_sha256,
        'process': process, 'passed': passed,
        'scope': 'Actual literal-CV admission bridge, completed producer-formal ownership, absent input CV and supplied-Throwable snapshot cancellation; generic catch/return tails reuse earlier laws.'}, indent=2) + '\n')
    print('completed producer snapshot/cancellation', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
