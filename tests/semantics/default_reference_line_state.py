#!/usr/bin/env python3
"""Check a real default SEND line and its unchanged call continuation."""
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
dec $dl_front(pstate) : bool
def $dl_front(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PINT 5)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
def $dl_front(S) = false -- otherwise
dec $dl_seek(pstate, nat) : pstate
def $dl_seek(S, n) = S -- if $dl_front(S) \/ n = 0
def $dl_seek(S, n) = $dl_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$dl_front(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $dl_seek(S, n) = S -- otherwise
dec $dl_diagnostics(pevent*) : pevent*
def $dl_diagnostics(eps) = eps
def $dl_diagnostics((DIAGNOSTIC text ptbytes z) :: pevent*) = (DIAGNOSTIC text ptbytes z) :: $dl_diagnostics(pevent*)
def $dl_diagnostics((OUTPUT ptbytes) :: pevent*) = $dl_diagnostics(pevent*)
'''
CHECKS = r'''
S_found = $dl_seek(S_initial, 1000)
S_pre = S_found[.COMPLETION = NORMAL]
$dl_front(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* (porigin_call) 7) :: ptask_tail*
S_pre.ERRORHANDLER.CALLBACK = eps
S_pre.SOURCEPENDING = eps
S_pre.OUTPUTBUFFERS = eps
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$named_reference_notice_value(PINT 5) /\ $positional_reference_notice_operands(S_pre, poperand*)
$call_argument_origin(S_pre, (porigin_call), 0) = (PORIGIN n_source pcpath_producer)
$call_argument_expression(S_pre, (porigin_call), 0) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE ([NArg ABSENT expression_cv (BOOLEAN false) (BOOLEAN false) metadata_arg])) metadata_call
expression_cv = NExprVariable (BYTES text_cv) metadata_cv
$runtime_line(S_pre[.ORIGIN = (PORIGIN n_source pcpath_producer)], eps, expression_producer) = 8
$runtime_line(S_pre[.ORIGIN = (PORIGIN n_source (pcpath_producer ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]))], eps, expression_cv) = 9
$reference_notice_producer_line(S_pre, (PORIGIN n_source pcpath_producer), expression_producer) = 9
$call_send_line(S_pre, (porigin_call), 0) = 9
$call_descriptors_valid(S_pre) /\ $heap_valid($heap_graph(S_pre))
n_private = |S_pre.STORE|
S_one = $drive(S_pre, 1)
S_one.COMPLETION = BUDGET
S_step = S_one[.COMPLETION = NORMAL]
S_step.TODO = (CALL_ARGS pcalltarget phpType7* 1 ([REFERENCE n_private]) (porigin_call) 7) :: ptask_tail*
S_step.STORE[n_private] = DEFINED (PINT 5)
$call_reference_operand_valid(S_step, REFERENCE n_private)
$heap_owners($heap_graph(S_step), HCELL n_private) = 1
(HCELL n_private) <- S_step.ALLOCATIONS
$dl_diagnostics(S_step.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 9]
$call_descriptors_valid(S_step) /\ $heap_valid($heap_graph(S_step))
S_zero = $drive(S_pre, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_pre
S_two = $drive(S_step, 1)
S_two.COMPLETION = BUDGET
S_direct = $drive(S_pre, 2)
S_two = S_direct
'''.strip().splitlines()
DERIVED = r'''
$call_send_line(S_step, (porigin_call), 0) = 8
S_owning = S_pre[.RESULT = KNOWN (PARRAY 0)]
$call_send_line(S_owning, (porigin_call), 0) = 8
S_wrong_origin = S_pre[.ORIGIN = eps]
$call_send_line(S_wrong_origin, (porigin_call), 0) = 8
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(prefix='default-reference-line-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/default_reference_line_cases.json',
                       ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        rows = json.loads((ROOT / 'tests/semantics/default_reference_line_cases.json').read_bytes())
        assert len(rows) == 1
        source = directory / 'source.php'
        source.write_bytes(rows[0]['source'].encode())
        assert hashlib.sha256(source.read_bytes()).hexdigest() == rows[0]['source_sha256']
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
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
        checks = ['S_initial = ' + initial] + CHECKS + DERIVED
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'reached_conditions': len(CHECKS) + 1, 'derived_controls': len(DERIVED),
            'source_sha256': rows[0]['source_sha256'], 'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}, indent=2) + '\n')
    if args.prepare_only:
        return True
    prepared = json.loads((directory / 'prepared.json').read_bytes())
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    assert fixture_sha256 == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(directory / 'state.watsup')], directory / 'run', 240)
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = process['exit'] == 0 and not process['timeout'] and stable and (directory / 'run.stdout').read_bytes() == b'true\n' and not (directory / 'run.stderr').read_bytes()
    (directory / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'inputs_stable': stable,
        'mode': 'AL/cache=false/det=true', 'module_count': len(modules), 'conditions': prepared['conditions'],
        'reached_conditions': prepared['reached_conditions'], 'derived_controls': prepared['derived_controls'],
        'fixture_sha256': fixture_sha256, 'process': process, 'passed': passed}, indent=2) + '\n')
    print('default source-line/continuation', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
