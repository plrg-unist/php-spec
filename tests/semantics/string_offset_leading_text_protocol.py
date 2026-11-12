#!/usr/bin/env python3
"""Fixed leading-text read offsets, ensuing bounds and supplied-throw cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_leading_text_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = (b'2|Illegal string offset "1x"|5;b|XYZ|0',
           b'2|Illegal string offset "3x"|5;2|Uninitialized string offset 3|5;|WXYZ|0',
           b'2|Illegal string offset "3x"|5;1|1|99|WXYZ|0')
PREFIX = shared.PREFIX + r'''
dec $leading_other(pevent) : pevent*
def $leading_other(OUTPUT n*) = eps
def $leading_other(pevent) = [pevent] -- otherwise
dec $leading_others(pevent*) : pevent*
def $leading_others(eps) = eps
def $leading_others(pevent :: pevent_tail*) = $leading_other(pevent) ++ $leading_others(pevent_tail*)
'''
lines, seek = shared.lines, shared.seek


def watbytes(value):
    return '[' + ','.join(map(str, value)) + ']'


def conditions(name, program, path):
    thrown = name.endswith('supplied-throw')
    bounds = name.endswith('old-bounds')
    index = 3 if bounds or thrown else 1
    replacement = 'WXYZ' if index == 3 else 'XYZ'
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    prefix = f'2|Illegal string offset "{index}x"|5;'.encode()
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r'''
$string_read_plan(S) = (pstringread)
pstringread.READ.LINE = 5 /\ pstringread.READ.MODE = KEY_R
pstringread.READ.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("key")) = (n_key)
$lookup(S.ENV, $ptascii("got")) = (n_got)
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
S.STORE[n_text] = DEFINED pstringread.READ.BASE
S.STORE[n_key] = DEFINED pstringread.READ.VALUE
S.STORE[n_got] = DEFINED (PINT 99)
S.STRINGDATA = eps /\ S.EVENTS = eps
$string_read_source(S, pstringread) /\ $string_read_ready(S, pstringread)
$task_nodes(STRING_READ_RESULT pstringread) = eps
~$string_read_source(S[.ORIGIN = eps], pstringread)
~$string_read_source(S, pstringread[.READ.LINE = 6])
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 5
$error_call_valid(S_dispatch, perrorcall)
S_dispatch.STORE = S.STORE /\ S_dispatch.STRINGDATA = S.STRINGDATA
$heap_graph(S_dispatch) = $heap_graph(S)
''') + [f'pstringread.PHASE = STRING_LEADING {index}',
          f'pstringread.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("{index}x"))',
          f'$string_read_leading(pstringread.READ.BASE, pstringread.READ.VALUE) = ({index})',
          f'perrorcall.MESSAGE = {watbytes(f"Illegal string offset {chr(34)}{index}x{chr(34)}".encode())}']
    if thrown:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_dispatch', 1, 'S_entered') + lines(r'''
S_entered.FRAMES = pframe :: pframe_tail*
pframe.LOCALS = eps
pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_entered*
perrorcall_entered.RESUME = STRING_READ_RESULT pstringread
S_entered.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("key")) = (n_key)
''') + seek('S_entered', 3 if thrown else 2, 'S_after') + [
        f'S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("{replacement}")))',
        f'$retained_outputs(S_after.EVENTS) = {watbytes(prefix)}',
    ] + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
S_after.STORE[n_got] = DEFINED (PINT 99)
$lookup(S_after.ENV, $ptascii("key")) = eps
~$string_read_cell(S_after, n_key)
$string_read_key_current(S_after, pstringread) = eps
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$leading_others(S_after.EVENTS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
''')
    if bounds:
        checks += lines(r'''
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
PhpStep: S_after ~> S_bounds_dispatch
S_bounds_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*
pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 3]
perrorcall_bounds.RESUME = STRING_READ_RESULT pstringread_bounds
perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 3")
perrorcall_bounds.LINE = 5 /\ perrorcall_bounds.LEVEL = 2
$error_call_valid(S_bounds_dispatch, perrorcall_bounds)
$string_read_source(S_bounds_dispatch, pstringread_bounds)
S_bounds_dispatch.STORE = S_after.STORE /\ S_bounds_dispatch.STRINGDATA = S_after.STRINGDATA
''') + seek('S_bounds_dispatch', 2, 'S_resume') + lines(r'''
S_resume.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_resume*
$lookup(S_resume.ENV, $ptascii("key")) = eps
$string_read_key_current(S_resume, pstringread_bounds) = eps
$string_read_source(S_resume, pstringread_bounds) /\ $string_read_ready(S_resume, pstringread_bounds)
S_resume.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("WXYZ")))
$leading_others(S_resume.EVENTS) = eps
PhpStep: S_resume ~> S_step
S_step = S_resume[.TODO = ptask_resume*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]
''') + [f'$retained_outputs(S_resume.EVENTS) = {watbytes(prefix + b"2|Uninitialized string offset 3|5;")}']
    elif thrown:
        checks += lines(r'''
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*
perrorcall_pending.RESUME = STRING_READ_RESULT pstringread
S_popped = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*]
S_restored = $error_handler_restore(S_popped, perrorcall_pending.CALLBACK)
~$error_handler_eligible(S_restored, 2)
$string_read_key_current(S_restored, pstringread) = eps
$throwable_previous_id(S_restored, n_saved) = eps
PhpStep: S_after ~> S_step
S_step = $error_default(S_restored[.ERRORFATALTRACE = eps], DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 3")) 5, 2)
S_step.EVENTS = S_after.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 3")) 5]
S_step.TODO = S_restored.TODO /\ S_step.STORE = S_restored.STORE
S_step.STORE[n_got] = DEFINED (PINT 99)
S_resume = S_after
''')
    else:
        checks += lines(r'''
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
PhpStep: S_after ~> S_step
S_step = S_after[.TODO = ptask_after*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_resume = S_after
''')
    checks += lines(r'''
$drive_steps(S_resume, 0) = S_resume[.COMPLETION = BUDGET]
S_split = $drive_steps(S_resume, 1)
S_split.COMPLETION = BUDGET
S_split.STORE = S_step.STORE /\ S_split.TODO = S_step.TODO /\ S_split.EVENTS = S_step.EVENTS
S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_text] = S_after.STORE[n_text]
$lookup(S_done.ENV, $ptascii("key")) = eps
S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_resume, 2000) = S_done
''') + [f'$retained_outputs(S_done.EVENTS) = {watbytes(OUTPUTS[2 if thrown else int(bounds)])}',
        '$leading_others(S_done.EVENTS) = [DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 3")) 5]' if thrown else
        '$leading_others(S_done.EVENTS) = eps',
        'S_done.STRINGDATA = [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = eps',
        'S_done.STORE[n_got] = DEFINED (PINT 99)' if thrown else
        'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)' if bounds else
        'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))']
    if thrown:
        checks += lines(r'''
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    reached = len(checks)
    if not bounds and not thrown:
        checks += lines(r'''
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))) = eps
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x"))) = eps
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ($ptascii("bad"))) = eps
$string_read_leading(pstringread.READ.BASE, PSTRING ($ptascii("1x"))) = eps
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ([49,0,120])) = eps
$string_read_leading(PSTRING_CARRIER INTERNED_STRING ([97,0,99]), pstringread.READ.VALUE) = eps
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ([256])) = eps
S_request = S_after[.STRINGDATA = [$ptascii("abc"), $ptascii("1x")]]
pvalue_request_base = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pvalue_request_key = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("1x"))
$string_carrier_valid(S_request, pvalue_request_base) /\ $string_carrier_valid(S_request, pvalue_request_key)
$string_read_leading(pvalue_request_base, pstringread.READ.VALUE) = eps
$string_read_leading(pstringread.READ.BASE, pvalue_request_key) = eps
~$string_read_source(S_request, pstringread[.READ.BASE = pvalue_request_base])
~$string_read_source(S_request, pstringread[.READ.VALUE = pvalue_request_key])
~$string_read_shape(S_after, pstringread[.PHASE = STRING_LEADING 3])
~$string_read_shape(S_after, pstringread[.PHASE = STRING_BOUNDS 3])
~$string_read_source(S_after, pstringread[.PHASE = STRING_BOUNDS 3])
$string_read_shape(S_after, pstringread[.READ.VALUE = PFLOAT 4609434218613702656][.PHASE = STRING_BOUNDS 9])
''')
    if bounds:
        checks += lines(r'''
~$string_read_shape(S_resume, pstringread_bounds[.PHASE = STRING_BOUNDS 9])
~$string_read_source(S_resume, pstringread_bounds[.PHASE = STRING_BOUNDS 9])
S_request = S_resume[.STRINGDATA = [$ptascii("abc"), $ptascii("3x")]]
~$string_read_source(S_request, pstringread_bounds[.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))])
~$string_read_source(S_request, pstringread_bounds[.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("3x"))])
''')
    if thrown:
        checks += lines(r'''
S_eligible = S_restored[.ERRORHANDLER.LEVELS = 2]
$error_handler_eligible(S_eligible, 2)
$string_read_key_current(S_eligible, pstringread) = eps
$error_read_discard(S_eligible, STRING_READ_RESULT pstringread) = S_eligible[.ERRORFATALTRACE = eps]
$error_read_discard(S_restored, STRING_READ_RESULT pstringread) = S_step
$string_read_source(S_restored, pstringread)
''')
    return checks, len(checks) - reached


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    source_report = json.loads(report_path.read_bytes())
    rows = {row['id']: row for row in source_report['rows']}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source_report['profile'] == profile
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()}) for name, source in cases.CASES.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        checked = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in checked.values())
    finally:
        adapter.close()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    originals, counts, fixtures = [], [], []
    for index, (name, source_bytes) in enumerate(cases.CASES.items()):
        row = rows[name]
        native = row['native']
        assert row['passed'] and native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        expected_stderr = b'Warning: Uninitialized string offset 3 in ' + bytes(source) + b' on line 5\n' if index == 2 else b''
        assert source.with_name('native.stdout').read_bytes() == OUTPUTS[index] and source.with_name('native.stderr').read_bytes() == expected_stderr
        checks, derived = conditions(name, checked[name]['fixture'], source)
        fixture = out / (name + '.watsup')
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        counts.append({'id': name, 'conditions': len(checks), 'derived_guard_conditions': derived, 'raw_steps': sum(check.startswith('PhpStep:') for check in checks)})
        originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(shared.__file__), Path(shared.cases.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in source_report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row, fixture in zip(counts, fixtures):
        stem = out / (row['id'] + '-model')
        process = recorded([str(runner), *map(str, modules), str(fixture)], stem, 180)
        row['process'] = process
        row['passed'] = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and stem.with_suffix('.stdout').read_bytes() == b'true\n' and not stem.with_suffix('.stderr').read_bytes()
        print(row['id'], row['conditions'], row['passed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in counts)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': list(cases.CASES), 'rows': counts, 'conditions': sum(row['conditions'] for row in counts), 'derived_guard_conditions': sum(row['derived_guard_conditions'] for row in counts), 'inputs': before, 'native_reused_from': str(report_path), 'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')}, 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
