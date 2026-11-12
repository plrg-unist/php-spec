#!/usr/bin/env python3
"""Independent live REQUEST keeper checks at ordinary return and throw fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_retained_carrier_cases as cases

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = (b'H;c|XYZ|abc|2', b'H;1|1|99|XYZ|abc|2')
HELPERS = r'''
dec $retained_review_front(pstate, nat) : bool
def $retained_review_front(S, 0) = ($string_read_plan(S) =/= eps)
def $retained_review_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
def $retained_review_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $retained_review_front(S, n) = false -- otherwise
dec $retained_review_seek(pstate, nat, nat) : pstate
def $retained_review_seek(S, n_stage, n) = S -- if $retained_review_front(S, n_stage)
def $retained_review_seek(S, n_stage, n) = S
  -- if ~$retained_review_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $retained_review_seek(S, n_stage, 0) = S
  -- if ~$retained_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $retained_review_seek(S, n_stage, n) = $retained_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$retained_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def seek(start, stage, result):
    return [f'{result}_found = $retained_review_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def conditions(program, source, thrown):
    encoded = json.dumps(base64.b64encode(bytes(source)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_entry') + lines(r'''
$string_read_plan(S_entry) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 5
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pstringread.READ.VALUE = PFLOAT 4609434218613702656
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S_entry.ENV, $ptascii("text")) = (n_text)
$lookup(S_entry.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S_entry.ENV, $ptascii("key")) = (n_key)
$lookup(S_entry.ENV, $ptascii("got")) = (n_got)
n_text =/= n_keeper /\ n_text =/= n_key /\ n_got =/= n_keeper
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_keeper_cell? = (n_keeper)
S_entry.STORE[n_text] = DEFINED pstringread.READ.BASE
S_entry.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_entry.STORE[n_got] = DEFINED (PINT 99)
S_entry.STRINGDATA = [$ptascii("abc")]
$string_carrier_valid(S_entry, pstringread.READ.BASE)
$string_read_source(S_entry, pstringread) /\ $error_handler_eligible(S_entry, 2)
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_entry.EVENTS = eps /\ S_entry.CURRENT = eps /\ S_entry.FRAMES = eps
''')
    if thrown:
        checks += lines(r'''
$lookup(S_entry.ENV, $ptascii("saved")) = (n_saved_cell)
S_entry.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_entry', 2 if thrown else 1, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_after.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_after.STORE[n_key] = DEFINED (PINT 2) /\ S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S_entry.STRINGDATA
$string_read_capture(S_after, VARIABLE ($ptascii("text")) 5) = ((PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")), pstringread.BASECELL))
$string_read_capture(S_after, VARIABLE ($ptascii("keeper")) 5) = ((pstringread.READ.BASE, n_keeper_cell?))
$string_read_source(S_after, pstringread) /\ $string_read_provider_ready(S_after, pstringread)
$string_read_key_current(S_after, pstringread) = (PINT 2)
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_after.EVENTS = [OUTPUT ($ptascii("H;"))]
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
''')
    if thrown:
        checks += lines(r'''
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
S_after.ERRORHANDLER.CALLBACK = eps
$task_nodes(THROW_SEARCH n_saved) = [HOBJECT n_saved]
$throwable_previous_id(S_after, n_saved) = eps
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_tail*][.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)][.ERRORFATALTRACE = eps]
S_raw.STORE[n_got] = DEFINED (PINT 99)
S_raw.ERRORHANDLER = S_entry.ERRORHANDLER
''')
    else:
        checks += lines(r'''
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S_after.ERRORHANDLER = S_entry.ERRORHANDLER
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))][.BASE = BASE_VALUE (KNOWN PNULL)]
$heap_graph(S_raw) = $heap_graph(S_after)
''')
    checks += lines(r'''
$drive_steps(S_after, 0) = S_after[.COMPLETION = BUDGET]
S_one = $drive_steps(S_after, 1)
S_one.COMPLETION = BUDGET
S_one.STORE = S_raw.STORE /\ S_one.TODO = S_raw.TODO /\ S_one.EVENTS = S_raw.EVENTS
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_text] = S_after.STORE[n_text] /\ S_done.STORE[n_keeper] = S_after.STORE[n_keeper]
S_done.STORE[n_key] = DEFINED (PINT 2)
S_done.STRINGDATA = S_entry.STRINGDATA /\ S_done.CODE = S_entry.CODE /\ S_done.POOLS = S_entry.POOLS
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_after, 2000) = S_done
''')
    chunks = ('1', '|', '1', '|', '99', '|', 'XYZ', '|', 'abc', '|', '2') if thrown else ('c', '|', 'XYZ', '|', 'abc', '|', '2')
    events = ', '.join('OUTPUT ($ptascii(' + json.dumps(chunk) + '))' for chunk in ('H;', *chunks))
    checks.append('S_done.EVENTS = [' + events + ']')
    if thrown:
        checks += lines(r'''
S_done.STORE[n_got] = DEFINED (PINT 99)
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    else:
        checks += ['S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))']
    reached = len(checks)
    if not thrown:
        checks += lines(r'''
S_no_keeper = S_after[.ENV = $unbind(S_after.ENV, $ptascii("keeper"))]
S_no_keeper.STORE[n_keeper] = DEFINED pstringread.READ.BASE
$string_carrier_valid(S_no_keeper, pstringread.READ.BASE)
~$string_read_provider_ready(S_no_keeper, pstringread)
$string_read_resume(S_no_keeper, pstringread).COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"
$string_read_discard(S_no_keeper, pstringread).COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"
S_interned_equal = S_after[.STORE[n_keeper] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))]
~$string_read_provider_ready(S_interned_equal, pstringread)
S_request_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))]
$string_carrier_valid(S_request_equal, PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))
~$string_read_provider_ready(S_request_equal, pstringread)
S_shadow = S_after[.ENV = (BIND ($ptascii("keeper")) n_got) :: S_after.ENV]
$lookup(S_shadow.ENV, $ptascii("keeper")) = (n_got)
~$string_read_provider_ready(S_shadow, pstringread)
~$string_read_provider_ready(S_after[.REFCELLS = n_keeper :: S_after.REFCELLS], pstringread)
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
    fixture_text, originals, selections = HELPERS, [], []
    for index, (name, source_bytes) in enumerate(cases.CASES.items()):
        row = rows[name]
        native = row['native']
        assert row['passed'] and native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert source.with_name('native.stdout').read_bytes() == OUTPUTS[index] and not source.with_name('native.stderr').read_bytes()
        checks, derived = conditions(programs[name]['fixture'], source, index == 1)
        fixture_text += f'\ndec $retained_review_{index}() : bool\ndef $retained_review_{index}() = true\n'
        fixture_text += ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived, 'raw_steps': sum(check.startswith('PhpStep:') for check in checks)})
        originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    fixture = out / 'test.watsup'
    fixture.write_text(fixture_text + '\ndec $main() : bool\ndef $main() = ($retained_review_0() /\\ $retained_review_1())\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
               Path(__file__), Path(cases.__file__), report_path, *originals, fixture,
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n' and not (out / 'model.stderr').read_bytes()
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': list(cases.CASES),
        'rows': selections, 'conditions': sum(row['conditions'] for row in selections),
        'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before,
        'process': process, 'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    print('retained-carrier-review', sum(row['conditions'] for row in selections), passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
