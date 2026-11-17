#!/usr/bin/env python3
"""Source-reached terminal string unset carriers, quiet keys and guard checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_terminal_unset_cases as cases
import string_offset_nested_unset_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
NAME = 'terminal-unset-authenticated-carriers'
OUTPUT = b'Cannot unset string offsets|3|ab;Cannot unset string offsets|4|ab'
PREFIX = shared.PREFIX
lines = shared.lines


def conditions(program, path):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')'] + lines(r"""
S_initial.COMPLETION = BUDGET
S_found = $nested_unset_seek(S_initial, 512)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S_a = S_found[.COMPLETION = NORMAL]
S_a.TODO = UNSET_ARRAY :: ptask_a*
S_a.BASE = BASE_DIM (BASE_VALUE (VARIABLE ptbytes_a 3)) (KNOWN (PFLOAT 9218868437227405312)) 3
ptbytes_a = $ptascii("a")
S_a.ORIGIN = (PORIGIN 0 pcpath_a)
S_a.REQUEST = eps /\ S_a.CURRENT = eps /\ S_a.FRAMES = eps
S_a.ERRORHANDLER.CALLBACK = eps /\ S_a.EVENTS = eps
$lookup(S_a.ENV, ptbytes_a) = (n_a)
$lookup(S_a.ENV, $ptascii("b")) = (n_b)
pvalue_a = PSTRING_CARRIER INTERNED_STRING ($ptascii("ab"))
pvalue_b = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("ab"))
S_a.STORE[n_a] = DEFINED pvalue_a /\ S_a.STORE[n_b] = DEFINED pvalue_b
S_a.STRINGDATA = [$ptascii("ab")]
$string_carrier_valid(S_a, pvalue_a) /\ $string_carrier_valid(S_a, pvalue_b)
ptbytes_message = $ptascii("Cannot unset string offsets")
ptbytes_old = $ptascii("Cannot unset offset in a non-array variable")
PhpStep: S_a ~> S_a_raw
S_a_raw = S_a[.TODO = ptask_a*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_a][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message 3]
$heap_graph(S_a_raw) = $heap_graph(S_a)
$drive(S_a, 0) = S_a[.COMPLETION = BUDGET]
S_a_public = $drive(S_a, 1)
S_a_public.COMPLETION = BUDGET /\ S_a_public.EVENTS = eps
S_a_public.TODO = (THROW_SEARCH n_error_a) :: ptask_throw_a*
S_a_public.OBJECTS[n_error_a] = THROWABLE pthrowable_a
pthrowable_a.KIND = "Error"
S_b_found = $nested_unset_seek(S_a_public[.COMPLETION = NORMAL], 512)
S_b_found.COMPLETION = NORMAL \/ S_b_found.COMPLETION = BUDGET
S_b = S_b_found[.COMPLETION = NORMAL]
S_b.TODO = UNSET_ARRAY :: ptask_b*
S_b.BASE = BASE_DIM (BASE_VALUE (VARIABLE ptbytes_b 4)) (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad")))) 4
ptbytes_b = $ptascii("b")
S_b.ORIGIN = (PORIGIN 0 pcpath_b)
S_b.ERRORHANDLER.CALLBACK = eps
S_b.STORE[n_a] = S_a.STORE[n_a] /\ S_b.STORE[n_b] = S_a.STORE[n_b]
S_b.STRINGDATA = S_a.STRINGDATA
$nested_unset_outputs(S_b.EVENTS) = $ptascii("Cannot unset string offsets|3|ab;")
$nested_unset_diagnostics(S_b.EVENTS) = eps
PhpStep: S_b ~> S_b_raw
S_b_raw = S_b[.TODO = ptask_b*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_b][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message 4]
$heap_graph(S_b_raw) = $heap_graph(S_b)
$drive(S_b, 0) = S_b[.COMPLETION = BUDGET]
S_b_public = $drive(S_b, 1)
S_b_public.COMPLETION = BUDGET /\ S_b_public.EVENTS = S_b.EVENTS
S_b_public.TODO = (THROW_SEARCH n_error_b) :: ptask_throw_b*
S_b_public.OBJECTS[n_error_b] = THROWABLE pthrowable_b
pthrowable_b.KIND = "Error" /\ n_error_b =/= n_error_a
S_done = $drive_steps(S_b_public[.COMPLETION = NORMAL], 1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_a] = S_a.STORE[n_a] /\ S_done.STORE[n_b] = S_a.STORE[n_b]
S_done.STRINGDATA = S_a.STRINGDATA /\ S_done.POOLS = S_a.POOLS /\ S_done.CODE = S_a.CODE
$nested_unset_outputs(S_done.EVENTS) = $ptascii("Cannot unset string offsets|3|ab;Cannot unset string offsets|4|ab")
$nested_unset_diagnostics(S_done.EVENTS) = eps
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_a, 2000) = S_done
""")
    reached_count = len(checks)
    checks += lines(r"""
S_key = S_b[.RESULT = KNOWN (PFLOAT 9218868437227405312)]
$unset_terminal_nonarray(S_key, pvalue_a, 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_terminal_nonarray(S_key, pvalue_b, 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_message 9]
S_interned_key = S_b[.RESULT = KNOWN pvalue_a]
$unset_terminal_nonarray(S_interned_key, pvalue_a, 9) = S_interned_key[.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_nonarray(S_interned_key, pvalue_a, 9) = S_interned_key[.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_nonarray(S_key, pvalue_b, 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_nonarray(S_b[.RESULT = KNOWN PNULL], pvalue_b, 9) = S_b[.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_b[.RESULT = KNOWN PNULL], pvalue_b, 9) = S_b[.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_terminal_key(S_key, PNULL) /\ $unset_terminal_key(S_key, PBOOL false)
$unset_terminal_key(S_key, PINT (-9223372036854775808))
~$unset_terminal_key(S_key, PINT 9223372036854775808)
~$unset_terminal_key(S_key, PFLOAT 18446744073709551616)
~$unset_terminal_key(S_key, PUNDEFINED)
~$unset_terminal_key(S_key, PARRAY 0) /\ ~$unset_terminal_key(S_key, POBJECT 0)
~$unset_terminal_key(S_key, PSTRING ([0]))
~$unset_terminal_key(S_key, PSTRING ([256]))
~$unset_terminal_key(S_key, PSTRING_CARRIER INTERNED_STRING ([0]))
~$unset_terminal_key(S_key, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("forged")))
$unset_terminal_key(S_key, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("ab")))
$unset_terminal_nonarray(S_key, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("forged")), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("ab")), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER INTERNED_STRING ([97,0]), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER INTERNED_STRING ([256]), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_b[.RESULT = KNOWN (PARRAY 0)], pvalue_b, 9) = S_b[.RESULT = KNOWN (PARRAY 0)][.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_b[.RESULT = KNOWN (POBJECT 0)], pvalue_a, 9) = S_b[.RESULT = KNOWN (POBJECT 0)][.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_b[.RESULT = KNOWN (PSTRING ([0]))], pvalue_a, 9) = S_b[.RESULT = KNOWN (PSTRING ([0]))][.COMPLETION = THROWN "Error" ptbytes_old 9]
$unset_terminal_nonarray(S_b[.RESULT = REFERENCE n_b], pvalue_b, 9) = S_b[.RESULT = REFERENCE n_b][.COMPLETION = THROWN "Error" ptbytes_old 9]
S_callback = S_key[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("heldHandler")))][.ERRORHANDLER.LEVELS = 2]
$unset_terminal_nonarray(S_callback, pvalue_a, 9) = S_callback[.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_terminal_nonarray(S_callback, pvalue_b, 9) = S_callback[.COMPLETION = THROWN "Error" ptbytes_message 9]
$lookup(S_b.ENV, $ptascii("missing")) = eps
$unset_final(S_b, pvalue_b, ROOT n_b, VARIABLE ($ptascii("missing")) 9, 9) = S_b[.RESULT = KNOWN PNULL][.EVENTS = S_b.EVENTS ++ [WARNING ($ptascii("missing")) 9]][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_terminal_nonarray(S_b[.RESULT = KNOWN (PARRAY 0)], PSTRING ($ptascii("ab")), 9) = S_b[.RESULT = KNOWN (PARRAY 0)][.COMPLETION = THROWN "Error" ptbytes_message 9]
""")
    return checks, len(checks) - reached_count


def main(expected_stderr=None):
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
    assert source.with_name('native.stdout').read_bytes() == OUTPUT
    assert source.with_name('native.stderr').read_bytes() == (expected_stderr(source) if expected_stderr else b'')
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
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(shared.__file__), report_path, source, source.with_name('native.stdout'), source.with_name('native.stderr'), fixture, ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n' and not (out / 'model.stderr').read_bytes()
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': [NAME], 'conditions': len(checks), 'derived_guard_conditions': derived, 'raw_unset_steps': 2, 'inputs': before, 'native_reused_from': str(report_path), 'source_sha256': row['source_sha256'], 'process': process, 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    print(NAME, len(checks), 'derived', derived, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
