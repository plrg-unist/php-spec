#!/usr/bin/env python3
"""Independent fixed leading-text offsets through return, bounds and throw."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_leading_text_cases as cases

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = {
    'string-offset-leading-text-key-unset': b'2|Illegal string offset "1x"|5;b|XYZ|0',
    'string-offset-leading-text-old-bounds': b'2|Illegal string offset "3x"|5;2|Uninitialized string offset 3|5;|WXYZ|0',
    'string-offset-leading-text-supplied-throw': b'2|Illegal string offset "3x"|5;1|1|99|WXYZ|0',
}
HELPERS = r'''
dec $leading_review_front(pstate, nat) : bool
def $leading_review_front(S, 0) = ($string_read_plan(S) =/= eps)
def $leading_review_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING i
def $leading_review_front(S, 2) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_BOUNDS i
def $leading_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.PHASE = STRING_LEADING i
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $leading_review_front(S, n) = false -- otherwise
dec $leading_review_seek(pstate, nat, nat) : pstate
def $leading_review_seek(S, n_stage, n) = S -- if $leading_review_front(S, n_stage)
def $leading_review_seek(S, n_stage, n) = S
  -- if ~$leading_review_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $leading_review_seek(S, n_stage, 0) = S
  -- if ~$leading_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $leading_review_seek(S, n_stage, n) = $leading_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$leading_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def seek(start, stage, result):
    return [f'{result}_found = $leading_review_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def output_events(chunks):
    return ', '.join('OUTPUT ($ptascii(' + json.dumps(chunk) + '))' for chunk in chunks)


def conditions(name, program, source):
    bounds = name.endswith('old-bounds')
    thrown = name.endswith('supplied-throw')
    index = 3 if bounds or thrown else 1
    replacement = 'WXYZ' if bounds or thrown else 'XYZ'
    first = output_events(('2', '|', f'Illegal string offset "{index}x"', '|', '5', ';'))
    encoded = json.dumps(base64.b64encode(bytes(source)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_entry') + [
        '$string_read_plan(S_entry) = (pstringread)',
        f'pstringread.PHASE = STRING_LEADING {index}',
        'pstringread.READ.LINE = 5',
        'pstringread.READ.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        f'pstringread.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("{index}x"))',
    ] + lines(r'''
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S_entry.ENV, $ptascii("text")) = (n_text)
$lookup(S_entry.ENV, $ptascii("key")) = (n_key)
$lookup(S_entry.ENV, $ptascii("got")) = (n_got)
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
S_entry.STORE[n_text] = DEFINED pstringread.READ.BASE
S_entry.STORE[n_key] = DEFINED pstringread.READ.VALUE
S_entry.STORE[n_got] = DEFINED (PINT 99)
S_entry.STRINGDATA = eps /\ S_entry.EVENTS = eps
$string_read_source(S_entry, pstringread) /\ $error_handler_eligible(S_entry, 2)
$task_nodes(STRING_READ_RESULT pstringread) = eps
''')
    if thrown:
        checks += lines(r'''
$lookup(S_entry.ENV, $ptascii("saved")) = (n_saved_cell)
S_entry.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_entry', 3 if thrown else 1, 'S_after') + [
        r'S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps',
        f'S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("{replacement}")))',
        '$lookup(S_after.ENV, $ptascii("key")) = eps',
        'S_after.STORE[n_key] = S_entry.STORE[n_key]',
        '~$string_read_cell(S_after, n_key)',
        '$string_read_key_current(S_after, pstringread) = eps',
        r'$string_read_ready(S_after, pstringread) /\ $string_read_source(S_after, pstringread)',
        'S_after.STORE[n_got] = DEFINED (PINT 99)',
        'S_after.STRINGDATA = eps',
        'S_after.EVENTS = [' + first + ']',
        r'$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)',
    ]
    start = 'S_after'
    events = first
    if thrown:
        checks += lines(r'''
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
S_after.ERRORHANDLER.CALLBACK = eps /\ S_after.ERRORHANDLER.LEVELS = 0
$throwable_previous_id(S_after, n_saved) = eps
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_tail*][.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)][.ERRORFATALTRACE = eps][.EVENTS = S_after.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 3")) 5]]
S_raw.STORE[n_got] = DEFINED (PINT 99)
''')
        events += ', DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 3")) 5'
    elif bounds:
        checks += lines(r'''
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S_after.ERRORHANDLER = S_entry.ERRORHANDLER
PhpStep: S_after ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_tail*
pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 3]
perrorcall_bounds.RESUME = STRING_READ_RESULT pstringread_bounds
perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 3") /\ perrorcall_bounds.LINE = 5
$error_call_valid(S_dispatch, perrorcall_bounds)
S_dispatch.STORE = S_after.STORE /\ S_dispatch.STRINGDATA = eps
S_dispatch.EVENTS = S_after.EVENTS
''') + seek('S_dispatch', 2, 'S_bounds') + lines(r'''
S_bounds.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_bounds*
$lookup(S_bounds.ENV, $ptascii("key")) = eps
$string_read_key_current(S_bounds, pstringread_bounds) = eps
$string_read_source(S_bounds, pstringread_bounds) /\ $string_read_ready(S_bounds, pstringread_bounds)
S_bounds.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("WXYZ")))
PhpStep: S_bounds ~> S_raw
S_raw = S_bounds[.TODO = ptask_bounds*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]
''')
        events += ', ' + output_events(('2', '|', 'Uninitialized string offset 3', '|', '5', ';'))
        checks.append('S_bounds.EVENTS = [' + events + ']')
        start = 'S_bounds'
    else:
        checks += lines(r'''
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S_after.ERRORHANDLER = S_entry.ERRORHANDLER
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))][.BASE = BASE_VALUE (KNOWN PNULL)]
''')
    checks += [
        f'$drive_steps({start}, 0) = {start}[.COMPLETION = BUDGET]',
        f'S_one = $drive_steps({start}, 1)',
        'S_one.COMPLETION = BUDGET',
        r'S_one.STORE = S_raw.STORE /\ S_one.TODO = S_raw.TODO /\ S_one.EVENTS = S_raw.EVENTS',
    ] + lines(r'''
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_text] = S_after.STORE[n_text]
$lookup(S_done.ENV, $ptascii("key")) = eps
S_done.CODE = S_entry.CODE /\ S_done.POOLS = S_entry.POOLS
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''') + [f'$drive_steps({start}, 2000) = S_done']
    tail = ('1', '|', '1', '|', '99', '|', 'WXYZ', '|', '0') if thrown else ('', '|', 'WXYZ', '|', '0') if bounds else ('b', '|', 'XYZ', '|', '0')
    checks.append('S_done.EVENTS = [' + events + ', ' + output_events(tail) + ']')
    checks.append('S_done.STRINGDATA = [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = eps')
    if thrown:
        checks += lines(r'''
S_done.STORE[n_got] = DEFINED (PINT 99)
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    else:
        checks.append('S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)' if bounds else 'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))')
    reached = len(checks)
    if thrown:
        checks += lines(r'''
S_suppressed = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_tail*][.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)][.ERRORHANDLER.LEVELS = 2]
$error_handler_eligible(S_suppressed, 2)
$string_read_discard(S_suppressed, pstringread) = S_suppressed[.ERRORFATALTRACE = eps]
''')
    if bounds:
        checks += lines(r'''
~$string_read_source(S_bounds, pstringread_bounds[.PHASE = STRING_BOUNDS 4])
~$string_read_shape(S_bounds, pstringread_bounds[.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))])
''')
    if not bounds and not thrown:
        checks += lines(r'''
~$string_read_source(S_after, pstringread[.PHASE = STRING_LEADING 2])
~$string_read_ready(S_after, pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S_after, pstringread[.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))])
~$string_read_source(S_after, pstringread[.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))])
S_request_base = S_after[.STRINGDATA = [$ptascii("abc")]]
$string_carrier_valid(S_request_base, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
$string_read_source(S_request_base, pstringread[.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))])
~$string_read_ready(S_request_base, pstringread[.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))])
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ([49,0,120])) = eps
$string_read_leading(pstringread.READ.BASE, PSTRING_CARRIER INTERNED_STRING ([256])) = eps
$string_read_plan(S_entry[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))]) = eps
''')
    return checks, len(checks) - reached


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    report = json.loads(report_path.read_bytes())
    rows = {row['id']: row for row in report['rows']}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert report['profile'] == profile
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
        programs = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in programs.values())
    finally:
        adapter.close()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    fixtures, originals, selections = [], [], []
    for name, source_bytes in cases.CASES.items():
        row = rows[name]
        native = row['native']
        assert row['passed'] and native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        expected_stderr = b'Warning: Uninitialized string offset 3 in ' + bytes(source) + b' on line 5\n' if name.endswith('supplied-throw') else b''
        assert source.with_name('native.stdout').read_bytes() == OUTPUTS[name] and source.with_name('native.stderr').read_bytes() == expected_stderr
        checks, derived = conditions(name, programs[name]['fixture'], source)
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived, 'raw_steps': sum(check.startswith('PhpStep:') for check in checks)})
        originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
               Path(__file__), Path(cases.__file__), report_path, *originals, *fixtures,
               *[ROOT / path for path in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
                 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
                 'tests/semantics/profile.json', 'tests/semantics/static_types.py',
                 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row, fixture in zip(selections, fixtures):
        prefix = out / (row['id'] + '-model')
        process = recorded([str(runner), *map(str, modules), str(fixture)], prefix, 180)
        row['model'] = process
        row['passed'] = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and prefix.with_suffix('.stdout').read_bytes() == b'true\n' and not prefix.with_suffix('.stderr').read_bytes()
        print(row['id'], row['conditions'], row['passed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in selections)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': list(cases.CASES),
        'rows': selections, 'conditions': sum(row['conditions'] for row in selections),
        'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before,
        'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    print('leading-text-review', sum(row['conditions'] for row in selections), passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
