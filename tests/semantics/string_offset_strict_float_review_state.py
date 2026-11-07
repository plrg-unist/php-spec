#!/usr/bin/env python3
"""Check strict float-index diagnostics separately from silent quiet reads."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_strict_float_cases as cases

ROOT = Path(__file__).resolve().parents[2]
NAME = 'string-offset-strict-float-infinite'
DIGEST = 'bba1b4c28d64826954cb47a70e0d8ac9e579246bb7d8b79ebe1e08d6bda85bb0'
RANGE = b'The float INF is not representable as an int, cast occurred'
PRECISION = b'Implicit conversion from float INF to int loses precision'
PREFIX = r'''
dec $strict_float_front(pstate, nat) : bool
def $strict_float_front(S, 0) = true -- if S.TODO = (ISSET_RESULT false z) :: ptask*
def $strict_float_front(S, 1) = true -- if S.TODO = (ISSET_RESULT true z) :: ptask*
def $strict_float_front(S, 2) = true -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask*
def $strict_float_front(S, n_stage) = false -- otherwise
dec $strict_float_seek(pstate, nat, nat) : pstate
def $strict_float_seek(S, n_stage, 0) = S
def $strict_float_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $strict_float_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $strict_float_seek(S, n_stage, n) = $strict_float_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$strict_float_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
dec $strict_float_output(pevent) : bool
def $strict_float_output(OUTPUT n*) = true
def $strict_float_output(pevent) = false -- otherwise
dec $strict_float_outputs(pevent*) : nat*
def $strict_float_outputs(eps) = eps
def $strict_float_outputs((OUTPUT n*) :: pevent_tail*) = n* ++ $strict_float_outputs(pevent_tail*)
def $strict_float_outputs(pevent :: pevent_tail*) = $strict_float_outputs(pevent_tail*) -- if ~$strict_float_output(pevent)
dec $strict_float_diagnostics(pevent*) : pevent*
def $strict_float_diagnostics(eps) = eps
def $strict_float_diagnostics((OUTPUT n*) :: pevent_tail*) = $strict_float_diagnostics(pevent_tail*)
def $strict_float_diagnostics(pevent :: pevent_tail*) = pevent :: $strict_float_diagnostics(pevent_tail*) -- if ~$strict_float_output(pevent)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $strict_float_seek({start}, {stage}, 512)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$strict_float_front({state}, {stage})']


def checks(program, path):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + reach('S', 'S_initial', 0)
    values += lines(r'''
S.TODO = (ISSET_RESULT false 2) :: ptask_after*
S.BASE = BASE_DIM (BASE_VALUE (VARIABLE ptbytes_s z_s)) (VARIABLE ptbytes_k z_k) 2
ptbytes_s = $ptascii("s") /\ ptbytes_k = $ptascii("k")
S.REQUEST = eps /\ S.CURRENT = eps /\ S.FRAMES = eps /\ S.EVENTS = eps
$lookup(S.ENV, ptbytes_s) = (n_s)
$lookup(S.ENV, ptbytes_k) = (n_k)
S.STORE[n_s] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))
S.STORE[n_k] = DEFINED (PFLOAT 9218868437227405312)
S.ERRORFATALTRACE = eps /\ S.CONSTCONTEXT = eps
$display_mode(S.DISPLAYINI) = 2
~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192)
$float_long(9218868437227405312, true) = (0, [RANGEWARNING])
ptbytes_range = $ptascii("The float INF is not representable as an int, cast occurred")
ptbytes_precision = $ptascii("Implicit conversion from float INF to int loses precision")
pevent_range = $event_source(S, DIAGNOSTIC "Warning" ptbytes_range 2)
pevent_precision = $event_source(S, DIAGNOSTIC "Deprecated" ptbytes_precision 2)
PhpStep: S ~> S_step
S_step = S[.RESULT = KNOWN (PBOOL true)][.TODO = ptask_after*][.BASE = BASE_VALUE (KNOWN PNULL)][.EVENTS = [pevent_range, pevent_precision]]
$heap_graph(S_step) = $heap_graph(S)
S_pause = $drive(S, 0)
S_pause = S[.COMPLETION = BUDGET]
$drive(S, 1) = S_step[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_step[.COMPLETION = BUDGET]
''')
    values += reach('S_empty', 'S_step', 1) + lines(r'''
S_empty.TODO = (ISSET_RESULT true 2) :: ptask_empty*
pevent_range_empty = $event_source(S_empty, DIAGNOSTIC "Warning" ptbytes_range 2)
pevent_precision_empty = $event_source(S_empty, DIAGNOSTIC "Deprecated" ptbytes_precision 2)
$strict_float_diagnostics(S_empty.EVENTS) = [pevent_range, pevent_precision]
$strict_float_outputs(S_empty.EVENTS) = $ptascii("1|")
PhpStep: S_empty ~> S_emptied
S_emptied = S_empty[.RESULT = KNOWN (PBOOL false)][.TODO = ptask_empty*][.BASE = BASE_VALUE (KNOWN PNULL)][.EVENTS = S_empty.EVENTS ++ [pevent_range_empty, pevent_precision_empty]]
$drive(S_empty, 0) = S_empty[.COMPLETION = BUDGET]
$drive(S_empty, 1) = S_emptied[.COMPLETION = BUDGET]
''')
    values += reach('S_coalesce', 'S_emptied', 2) + lines(r'''
S_coalesce.TODO = (COALESCE_QUIET expression_right 2 2) :: ptask_coalesce*
S_coalesce.CONSTCONTEXT = eps
$strict_float_outputs(S_coalesce.EVENTS) = $ptascii("1|0|")
PhpStep: S_coalesce ~> S_coalesced
S_coalesced = S_coalesce[.RESULT = KNOWN (PSTRING ($ptascii("a")))][.TODO = ptask_coalesce*][.BASE = BASE_VALUE (KNOWN PNULL)]
$drive(S_coalesce, 1) = S_coalesced[.COMPLETION = BUDGET]
S_done = $drive_steps(S_coalesced, 1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE = S.STORE /\ S_done.STRINGDATA = S.STRINGDATA
S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
$strict_float_outputs(S_done.EVENTS) = $ptascii("1|0|a")
$strict_float_diagnostics(S_done.EVENTS) = [pevent_range, pevent_precision, pevent_range_empty, pevent_precision_empty]
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''')
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    source_report = json.loads(report_path.read_bytes())
    row = next(row for row in source_report['rows'] if row['id'] == NAME)
    native = row['native']
    assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
    source = Path(native['argv'][-1])
    assert source.is_absolute() and source.read_bytes() == cases.CASES[NAME]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256'] == DIGEST
    assert source.with_name('native.stdout').read_bytes() == b'1|0|a'
    stderr = b'Warning: ' + RANGE + b' in ' + bytes(source) + b' on line 2\nDeprecated: ' + PRECISION + b' in ' + bytes(source) + b' on line 2\n'
    assert source.with_name('native.stderr').read_bytes() == stderr * 2
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source_report['profile'] == profile
    runtime_hashes = [value for path, value in source_report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')]
    assert runtime_hashes == [hashlib.sha256((ROOT / '.tools/php/bin/php').read_bytes()).hexdigest()]
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(cases.CASES[NAME]).decode()})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        adapter.close()
    conditions = checks(checked['fixture'], source)
    fixture = out / 'test.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (x if x.startswith('PhpStep:') else 'if ' + x) + '\n' for x in conditions))
    (out / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), report_path,
               source, source.with_name('native.stdout'), source.with_name('native.stderr'), fixture,
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py']
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n' and (out / 'model.stderr').read_bytes() == b''
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': revision, 'mode': 'AL', 'selection': [NAME], 'conditions': len(conditions), 'raw_steps': sum(x.startswith('PhpStep:') for x in conditions), 'native_reused_from': str(report_path), 'source_sha256': DIGEST, 'inputs': before, 'process': process, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(NAME, len(conditions), 'PASS' if passed else 'FAIL', flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
