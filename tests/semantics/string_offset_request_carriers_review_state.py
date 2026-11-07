#!/usr/bin/env python3
"""Independently check ordinary concat carriers and the false final byte."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_carriers_cases as cases

ROOT = Path(__file__).resolve().parents[2]
NAME = 'string-offset-quiet-request-key'
PREFIX = r'''
dec $request_quiet_front(pstate, nat) : bool
def $request_quiet_front(S, 0) = true
  -- if S.TODO = (ISSET_RESULT false z) :: ptask*
def $request_quiet_front(S, 1) = true
  -- if S.TODO = (ISSET_RESULT true z) :: ptask*
def $request_quiet_front(S, 2) = true
  -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask*
def $request_quiet_front(S, n_stage) = false -- otherwise
dec $request_quiet_seek(pstate, nat, nat) : pstate
def $request_quiet_seek(S, n_stage, 0) = S
def $request_quiet_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $request_quiet_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $request_quiet_seek(S, n_stage, n) = $request_quiet_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$request_quiet_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
dec $request_quiet_outputs(pevent*) : nat*
def $request_quiet_outputs(eps) = eps
def $request_quiet_outputs((OUTPUT n*) :: pevent_tail*) = n* ++ $request_quiet_outputs(pevent_tail*)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $request_quiet_seek({start}, {stage}, 512)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$request_quiet_front({state}, {stage})']


def checks(program, path):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + reach('S', 'S_initial', 0)
    values += lines(r'''
S.TODO = (ISSET_RESULT false z) :: ptask_after*
S.BASE = BASE_DIM (BASE_VALUE (VARIABLE ptbytes_s z_s)) (VARIABLE ptbytes_key z_key) z_dim
ptbytes_s = $ptascii("s") /\ ptbytes_key = $ptascii("key")
S.CURRENT = eps /\ S.FRAMES = eps /\ S.GLOBALTABLE = eps
$lookup(S.ENV, ptbytes_s) = (n_s)
$lookup(S.ENV, ptbytes_key) = (n_key)
pvalue_base = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("a0"))
pvalue_key = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("-1"))
S.STORE[n_s] = DEFINED pvalue_base /\ S.STORE[n_key] = DEFINED pvalue_key
S.STRINGDATA = [($ptascii("a0")), ($ptascii("-1"))]
$string_carrier_valid(S, pvalue_base) /\ $string_carrier_valid(S, pvalue_key)
$c_string($ptascii("a0")) = $ptascii("a0") /\ $c_string($ptascii("-1")) = $ptascii("-1")
~(n_s <- S.REFCELLS) /\ ~(n_key <- S.REFCELLS)
$heap_owners($heap_graph(S), HCELL n_s) = 1
$heap_owners($heap_graph(S), HCELL n_key) = 1
$value_nodes(pvalue_base) = eps /\ $value_nodes(pvalue_key) = eps
$base_nodes(S.BASE) = eps
$quiet_dimension_value(S, pvalue_base, pvalue_key, z) = S[.RESULT = KNOWN (PSTRING ($ptascii("0")))]
$isset_dimension_value(S, pvalue_base, pvalue_key, false, z) = S[.RESULT = KNOWN (PBOOL true)]
$isset_dimension_value(S, pvalue_base, pvalue_key, true, z) = S[.RESULT = KNOWN (PBOOL true)]
$quiet_string(S, $ptascii("a0"), pvalue_key, z) = $quiet_string(S, $ptascii("a0"), PSTRING ($ptascii("-1")), z)
$isset_string(S, $ptascii("a0"), pvalue_key, true, z) = $isset_string(S, $ptascii("a0"), PSTRING ($ptascii("-1")), true, z)
PhpStep: S ~> S_step
S_step.COMPLETION = NORMAL /\ S_step.RESULT = KNOWN (PBOOL true)
S_step.TODO = ptask_after* /\ S_step.BASE = BASE_VALUE (KNOWN PNULL)
S_step.STORE = S.STORE /\ S_step.ENV = S.ENV /\ S_step.STRINGDATA = S.STRINGDATA
S_step.ALLOCATIONS = S.ALLOCATIONS /\ S_step.HELD = S.HELD
S_step.EVENTS = S.EVENTS /\ S_step.POOLS = S.POOLS /\ S_step.CODE = S.CODE
$heap_graph(S_step) = $heap_graph(S)
S_pause = $drive(S, 0)
S_pause = S[.COMPLETION = BUDGET]
$drive(S, 1) = S_step[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_step[.COMPLETION = BUDGET]
$call_descriptors_valid(S_step)
''')
    values += reach('S_empty', 'S_step', 1) + lines(r'''
S_empty.TODO = (ISSET_RESULT true z_empty) :: ptask_empty*
PhpStep: S_empty ~> S_empty_out
S_empty_out.COMPLETION = NORMAL /\ S_empty_out.RESULT = KNOWN (PBOOL true)
S_empty_out.TODO = ptask_empty* /\ S_empty_out.STORE = S_empty.STORE
S_empty_out.STRINGDATA = S.STRINGDATA /\ S_empty_out.EVENTS = S_empty.EVENTS
''')
    values += reach('S_coalesce', 'S_empty_out', 2) + lines(r'''
S_coalesce.TODO = (COALESCE_QUIET expression_right z_left z_right) :: ptask_coalesce*
S_selected = $quiet_base(S_coalesce, S_coalesce.BASE, z_left)
S_selected.RESULT = KNOWN (PSTRING ($ptascii("0")))
S_coalesced = $coalesce_result($constant_quiet_capture(S_selected)[.TODO = ptask_coalesce*][.BASE = BASE_VALUE (KNOWN PNULL)], expression_right, z_left, z_right)
PhpStep: S_coalesce ~> S_coalesced
S_coalesced.COMPLETION = NORMAL /\ S_coalesced.RESULT = KNOWN (PSTRING ($ptascii("0")))
S_coalesced.TODO = ptask_coalesce* /\ S_coalesced.STORE = S_coalesce.STORE
S_coalesced.STRINGDATA = S.STRINGDATA /\ S_coalesced.EVENTS = S_coalesce.EVENTS
$drive(S_coalesce, 0) = S_coalesce[.COMPLETION = BUDGET]
$drive(S_coalesce, 1) = S_coalesced[.COMPLETION = BUDGET]
S_done = $drive_steps(S_coalesced, 1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_s] = DEFINED pvalue_base /\ S_done.STORE[n_key] = DEFINED pvalue_key
S_done.STRINGDATA = S.STRINGDATA /\ S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$request_quiet_outputs(S_done.EVENTS) = $ptascii("1|1|0|0")
$drive_steps(S, 1000) = S_done
''')
    for suffix, state, carrier, valid in (
        ('missing', 'S', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))', False),
        ('forged', 'S', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("-1"))', False),
        ('range', 'S[.STRINGDATA = [[256]]]', 'PSTRING_CARRIER (REQUEST_STRING 0) ([256])', False),
        ('nul', 'S[.STRINGDATA = [[97,0]]]', 'PSTRING_CARRIER (REQUEST_STRING 0) ([97,0])', True),
    ):
        values += [f'S_{suffix} = {state}', f'pvalue_{suffix} = {carrier}',
                   ('' if valid else '~') + f'$string_carrier_valid(S_{suffix}, pvalue_{suffix})',
                   f'$quiet_dimension_value(S_{suffix}, pvalue_{suffix}, PINT 0, z) = S_{suffix}[.RESULT = KNOWN PNULL]',
                   f'$isset_dimension_value(S_{suffix}, pvalue_{suffix}, PINT 0, false, z) = S_{suffix}[.RESULT = KNOWN (PBOOL false)]',
                   f'$isset_string(S_{suffix}, $ptascii("a0"), pvalue_{suffix}, false, z) = S_{suffix}[.RESULT = KNOWN (PBOOL false)]']
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    source_report = json.loads(report_path.read_bytes())
    native_row = next(row for row in source_report['rows'] if row['id'] == NAME)
    native = native_row['native']
    assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
    source = Path(native['argv'][-1])
    assert source.is_absolute() and source.read_bytes() == cases.CASES[NAME]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == native_row['source_sha256']
    assert source.with_name('native.stdout').read_bytes() == b'1|1|0|0'
    assert source.with_name('native.stderr').read_bytes() == b''
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source_report['profile'] == profile
    runtime_hashes = [value for path, value in source_report['inputs'].items() if path.endswith('/.tools/php/bin/php')]
    assert runtime_hashes == [hashlib.sha256((ROOT / '.tools/php/bin/php').read_bytes()).hexdigest()]
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
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
    report = {'revision': revision, 'mode': 'AL', 'selection': [NAME], 'conditions': len(conditions), 'raw_steps': sum(x.startswith('PhpStep:') for x in conditions), 'native_reused_from': str(report_path), 'source_sha256': native_row['source_sha256'], 'inputs': before, 'process': process, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(NAME, len(conditions), 'PASS' if passed else 'FAIL', flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
