#!/usr/bin/env python3
"""Independent reached-state checks of terminal string unset carrier dispatch."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_terminal_unset_cases as cases

ROOT = Path(__file__).resolve().parents[2]
NAME = 'terminal-unset-authenticated-carriers'
OUTPUT = b'Cannot unset string offsets|3|ab;Cannot unset string offsets|4|ab'
HELPERS = r'''
dec $terminal_unset_front(pstate) : bool
def $terminal_unset_front(S) = true -- if S.TODO = UNSET_ARRAY :: ptask*
def $terminal_unset_front(S) = false -- otherwise
dec $terminal_unset_seek(pstate, nat) : pstate
def $terminal_unset_seek(S, 0) = S
def $terminal_unset_seek(S, n) = S
  -- if $(n > 0)
  -- if $terminal_unset_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $terminal_unset_seek(S, n) = $terminal_unset_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$terminal_unset_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def conditions(program, source):
    encoded = json.dumps(base64.b64encode(bytes(source)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')']
    checks += [line.strip() for line in r'''
S_initial.COMPLETION = BUDGET
S_first_found = $terminal_unset_seek(S_initial, 512)
S_first_found.COMPLETION = NORMAL \/ S_first_found.COMPLETION = BUDGET
S_first = S_first_found[.COMPLETION = NORMAL]
S_first.TODO = UNSET_ARRAY :: ptask_first*
S_first.BASE = BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("a")) 3)) (KNOWN (PFLOAT 9218868437227405312)) 3
S_first.REQUEST = eps /\ S_first.CURRENT = eps /\ S_first.EVENTS = eps
S_first.ERRORHANDLER.CALLBACK = eps /\ S_first.ERRORFATALTRACE = eps
S_first.ORIGIN = (PORIGIN 0 pcpath_first)
$lookup(S_first.ENV, $ptascii("a")) = (n_a)
$lookup(S_first.ENV, $ptascii("b")) = (n_b)
S_first.STORE[n_a] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))
S_first.STORE[n_b] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("ab")))
S_first.STRINGDATA = [$ptascii("ab")]
$string_carrier_valid(S_first, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("ab")))
~(n_a <- S_first.REFCELLS) /\ ~(n_b <- S_first.REFCELLS)
$heap_owners($heap_graph(S_first), HCELL n_a) = 1
$heap_owners($heap_graph(S_first), HCELL n_b) = 1
ptbytes_message = $ptascii("Cannot unset string offsets")
PhpStep: S_first ~> S_first_raw
S_first_raw = S_first[.TODO = ptask_first*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_a][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message 3]
$heap_graph(S_first_raw) = $heap_graph(S_first[.TODO = ptask_first*][.BASE = BASE_VALUE (KNOWN PNULL)][.RESULT = KNOWN PNULL])
$drive(S_first, 0) = S_first[.COMPLETION = BUDGET]
S_first_public = $drive(S_first, 1)
S_first_public.COMPLETION = BUDGET /\ S_first_public.EVENTS = eps
S_second_found = $terminal_unset_seek(S_first_public, 512)
S_second_found.COMPLETION = NORMAL \/ S_second_found.COMPLETION = BUDGET
S_second = S_second_found[.COMPLETION = NORMAL]
S_second.TODO = UNSET_ARRAY :: ptask_second*
S_second.BASE = BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("b")) 4)) (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad")))) 4
S_second.ORIGIN = (PORIGIN 0 pcpath_second)
pcpath_first =/= pcpath_second
S_second.CURRENT = eps /\ S_second.ERRORHANDLER.CALLBACK = eps
S_second.STORE[n_a] = S_first.STORE[n_a] /\ S_second.STORE[n_b] = S_first.STORE[n_b]
S_second.STRINGDATA = S_first.STRINGDATA
S_second.EVENTS = [OUTPUT ptbytes_message, OUTPUT ($ptascii("|")), OUTPUT ($ptascii("3")), OUTPUT ($ptascii("|")), OUTPUT ($ptascii("ab")), OUTPUT ($ptascii(";"))]
$heap_valid($heap_graph(S_second)) /\ $call_descriptors_valid(S_second)
PhpStep: S_second ~> S_second_raw
S_second_raw = S_second[.TODO = ptask_second*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_b][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message 4]
$heap_graph(S_second_raw) = $heap_graph(S_second[.TODO = ptask_second*][.BASE = BASE_VALUE (KNOWN PNULL)][.RESULT = KNOWN PNULL])
$drive(S_second, 0) = S_second[.COMPLETION = BUDGET]
S_second_public = $drive(S_second, 1)
S_second_public.COMPLETION = BUDGET /\ S_second_public.EVENTS = S_second.EVENTS
S_done = $drive_steps(S_second_public[.COMPLETION = NORMAL], 1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_a] = S_first.STORE[n_a] /\ S_done.STORE[n_b] = S_first.STORE[n_b]
S_done.STRINGDATA = S_first.STRINGDATA /\ S_done.POOLS = S_first.POOLS /\ S_done.CODE = S_first.CODE
S_done.EVENTS = S_second.EVENTS ++ [OUTPUT ptbytes_message, OUTPUT ($ptascii("|")), OUTPUT ($ptascii("4")), OUTPUT ($ptascii("|")), OUTPUT ($ptascii("ab"))]
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_first, 1000) = S_done
$drive_steps(S_second, 1000) = S_done
'''.splitlines() if line.strip()]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    report = json.loads(report_path.read_bytes())
    row = next(row for row in report['rows'] if row['id'] == NAME)
    native = row['native']
    assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
    source = Path(native['argv'][-1])
    assert source.is_absolute() and source.read_bytes() == cases.CASES[NAME]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest(source) == row['source_sha256']
    assert source.with_name('native.stdout').read_bytes() == OUTPUT and not source.with_name('native.stderr').read_bytes()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert report['profile'] == profile
    hashes = [value for path, value in report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')]
    assert hashes == [digest(ROOT / '.tools/php/bin/php')]
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
    checks = conditions(checked['fixture'], source)
    fixture = out / 'test.watsup'
    fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
               Path(__file__), Path(cases.__file__), report_path, source,
               source.with_name('native.stdout'), source.with_name('native.stderr'), fixture,
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n' and not (out / 'model.stderr').read_bytes()
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': [NAME],
        'conditions': len(checks), 'raw_unset_steps': 2, 'native_reused_from': str(report_path),
        'inputs': before, 'process': process, 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    print('terminal-unset-review', len(checks), passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
