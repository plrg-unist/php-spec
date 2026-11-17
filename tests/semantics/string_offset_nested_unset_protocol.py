#!/usr/bin/env python3
"""Source-reached nested string unset error, driver and guard checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_nested_unset_cases as cases

ROOT = Path(__file__).resolve().parents[2]
NAME = 'nested-unset-leading-numeric-final-assignment'
OUTPUT = b'Cannot use string offset as an array|3|7|ab'
PREFIX = r'''
dec $nested_unset_front(pstate) : bool
def $nested_unset_front(S) = true -- if S.TODO = UNSET_ARRAY :: ptask*
def $nested_unset_front(S) = false -- otherwise
dec $nested_unset_seek(pstate, nat) : pstate
def $nested_unset_seek(S, 0) = S
def $nested_unset_seek(S, n) = S
  -- if $(n > 0)
  -- if $nested_unset_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $nested_unset_seek(S, n) = $nested_unset_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$nested_unset_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
dec $nested_unset_output(pevent) : bool
def $nested_unset_output(OUTPUT n*) = true
def $nested_unset_output(pevent) = false -- otherwise
dec $nested_unset_outputs(pevent*) : nat*
def $nested_unset_outputs(eps) = eps
def $nested_unset_outputs((OUTPUT n*) :: pevent_tail*) = n* ++ $nested_unset_outputs(pevent_tail*)
def $nested_unset_outputs(pevent :: pevent_tail*) = $nested_unset_outputs(pevent_tail*) -- if ~$nested_unset_output(pevent)
dec $nested_unset_diagnostics(pevent*) : pevent*
def $nested_unset_diagnostics(eps) = eps
def $nested_unset_diagnostics((OUTPUT n*) :: pevent_tail*) = $nested_unset_diagnostics(pevent_tail*)
def $nested_unset_diagnostics(pevent :: pevent_tail*) = pevent :: $nested_unset_diagnostics(pevent_tail*) -- if ~$nested_unset_output(pevent)
'''


def lines(value):
    return [line.strip() for line in value.splitlines() if line.strip()]


def conditions(program, path):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')'] + lines(r'''
S_initial.COMPLETION = BUDGET
S_found = $nested_unset_seek(S_initial, 512)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
S.TODO = UNSET_ARRAY :: ptask_tail*
S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ptbytes_s z_s)) poperand_inner z_inner) poperand_final z_final
ptbytes_s = $ptascii("s") /\ z_inner = 3 /\ z_final = 3
poperand_inner = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")))
S.REQUEST = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
S.ERRORHANDLER.CALLBACK = eps /\ S.EVENTS = eps
S.ORIGIN = (PORIGIN 0 pcpath)
$lookup(S.ENV, ptbytes_s) = (n_s)
S.STORE[n_s] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))
$lookup(S.ENV, $ptascii("last")) = (n_last)
S.STORE[n_last] = DEFINED (PINT 7)
~(n_s <- S.REFCELLS) /\ ~(n_last <- S.REFCELLS)
ptbytes_message = $ptascii("Cannot use string offset as an array")
ptbytes_first = $ptascii("Cannot unset string offsets")
PhpStep: S ~> S_raw
S_raw = S[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_s][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message 3]
$heap_graph(S_raw) = $heap_graph(S)
$drive(S, 0) = S[.COMPLETION = BUDGET]
S_one = $drive(S, 1)
S_one.COMPLETION = BUDGET
S_one.TODO = (THROW_SEARCH n_error) :: ptask_throw*
n_error = |S.OBJECTS|
S_one.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "Error" /\ pthrowable.ORIGIN = S.ORIGIN
S_one.STORE = S.STORE /\ S_one.EVENTS = eps
S_one.BASE = BASE_VALUE (KNOWN PNULL)
$heap_valid($heap_graph(S_one)) /\ $call_descriptors_valid(S_one)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_s] = S.STORE[n_s] /\ S_done.STORE[n_last] = S.STORE[n_last]
S_done.STRINGDATA = S.STRINGDATA /\ S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
$nested_unset_outputs(S_done.EVENTS) = $ptascii("Cannot use string offset as an array|3|7|ab")
$nested_unset_diagnostics(S_done.EVENTS) = eps
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S, 1000) = S_done
''')
    reached_count = len(checks)
    checks += lines(r'''
S_base = S[.LOCATION = ROOT n_s][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))]
$unset_intermediate(S_base, PSTRING ($ptascii("ab")), ROOT n_s, KNOWN (PINT (-999)), 9) = S_base[.RESULT = KNOWN (PINT (-999))][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_string_key(S_base, PSTRING ($ptascii("0x")), 9) = S_base
$unset_string_key(S_base, PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")), 9) = S_base
$unset_string_key(S_base, PSTRING ($ptascii("bad")), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_first 9]
$unset_string_key(S_base, PFLOAT 9218868437227405312, 9) = S_base[.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 9]]
$unset_string_key(S_base, PNULL, 9) = S_base[.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 9]]
$unset_string_key(S_base, PBOOL true, 9) = S_base[.EVENTS = [DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 9]]
$unset_string_key(S_base, PFLOAT 18446744073709551616, 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_string_key(S_base, PSTRING ([48,0]), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_string_key(S_base, PSTRING ([256]), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_string_key(S_base, PSTRING_CARRIER INTERNED_STRING ([48,0]), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_string_key(S_base, PSTRING_CARRIER (REQUEST_STRING 0) ([48]), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_string_key(S_base, POBJECT 0, 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_string_key(S_base, PUNDEFINED, 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
S_empty = S_base[.ARRAYS = [$array_empty()]]
$unset_string_key(S_empty, PARRAY 0, 9) = S_empty[.COMPLETION = THROWN "Error" ptbytes_first 9]
$unset_string_key(S_empty, PARRAY 1, 9) = S_empty[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
S_nonempty = S_base[.ARRAYS = [$array_insert($array_empty(), KINT 0, DIRECT (PINT 1))]]
$unset_string_key(S_nonempty, PARRAY 0, 9) = S_nonempty[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_intermediate(S_base, PSTRING ([97,0]), ROOT n_s, KNOWN (PINT 0), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_intermediate(S_base, PSTRING ([256]), ROOT n_s, KNOWN (PINT 0), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
S_callback = S_base[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("heldHandler")))][.ERRORHANDLER.LEVELS = 2]
$unset_intermediate(S_callback, PSTRING ($ptascii("ab")), ROOT n_s, KNOWN (PINT 0), 9) = S_callback[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_intermediate(S_callback, PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")), ROOT n_s, KNOWN (PINT 0), 9) = S_callback[.RESULT = KNOWN (PINT 0)][.COMPLETION = THROWN "Error" ptbytes_message 9]
S_request = S_base[.STRINGDATA = [$ptascii("ab")]]
$unset_intermediate(S_request, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("ab")), ROOT n_s, KNOWN (PINT 0), 9) = S_request[.RESULT = KNOWN (PINT 0)][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_request, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("zz")), ROOT n_s, KNOWN (PINT 0), 9) = S_request[.COMPLETION = THROWN "Error" ($ptascii("Cannot unset offset in a non-array variable")) 9]
$unset_intermediate(S_base, PSTRING_CARRIER INTERNED_STRING ([97,0]), ROOT n_s, KNOWN (PINT 0), 9) = S_base[.COMPLETION = THROWN "Error" ($ptascii("Cannot unset offset in a non-array variable")) 9]
$unset_nonarray(S_base, PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")), 9) = S_base[.COMPLETION = THROWN "Error" ($ptascii("Cannot unset offset in a non-array variable")) 9]
$unset_nonarray(S_base, PSTRING ($ptascii("ab")), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_first 9]
''')
    return checks, len(checks) - reached_count


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
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest(source) == row['source_sha256']
    assert source.with_name('native.stdout').read_bytes() == OUTPUT and not source.with_name('native.stderr').read_bytes()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source_report['profile'] == profile
    hashes = [value for path, value in source_report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')]
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
    checks, derived = conditions(checked['fixture'], source)
    fixture = out / 'test.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), report_path, source, source.with_name('native.stdout'), source.with_name('native.stderr'), fixture, ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n' and not (out / 'model.stderr').read_bytes()
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': [NAME], 'conditions': len(checks), 'derived_guard_conditions': derived, 'raw_query_steps': 1, 'inputs': before, 'native_reused_from': str(report_path), 'source_sha256': row['source_sha256'], 'process': process, 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    print(NAME, len(checks), 'derived', derived, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
