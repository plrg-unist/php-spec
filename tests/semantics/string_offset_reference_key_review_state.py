#!/usr/bin/env python3
"""Independent aliased-key states and the affected legacy REQUEST prefix only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_reference_key_cases as cases
import string_offset_read_warning_cases as legacy

ROOT = Path(__file__).resolve().parents[2]
LEGACY_SOURCE = 'string-offset-read-warning-runtime-carriers'
LEGACY_NAME = 'legacy-request-marked-key-entry-resume'
LEGACY_HASH = '72127c53c781fb09dc7382cba7a3d3714d13e662089d1c7a20a4237609fea5cb'
OUTPUTS = (b'2|String offset cast occurred|5;c|2|2',
           b'2|String offset cast occurred|5;1|1|99|2|2')
HELPERS = r'''
dec $refkey_review_front(pstate, nat) : bool
def $refkey_review_front(S, 0) = ($string_read_plan(S) =/= eps)
def $refkey_review_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_CAST
def $refkey_review_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.PHASE = STRING_CAST
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $refkey_review_front(S, n) = false -- otherwise
dec $refkey_review_seek(pstate, nat, nat) : pstate
def $refkey_review_seek(S, n_stage, n) = S -- if $refkey_review_front(S, n_stage)
def $refkey_review_seek(S, n_stage, n) = S
  -- if ~$refkey_review_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $refkey_review_seek(S, n_stage, 0) = S
  -- if ~$refkey_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $refkey_review_seek(S, n_stage, n) = $refkey_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$refkey_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def seek(start, stage, result):
    return [f'{result}_found = $refkey_review_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def initialize(program, source):
    encoded = json.dumps(base64.b64encode(bytes(source)).decode())
    return ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
            'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_entry')


def source_conditions(program, source, thrown):
    checks = initialize(program, source) + lines(r'''
$string_read_plan(S_entry) = (pstringread)
pstringread.KEYREF
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 5
pstringread.READ.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pstringread.READ.VALUE = PFLOAT 4609434218613702656
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S_entry.ENV, $ptascii("text")) = (n_text)
$lookup(S_entry.ENV, $ptascii("key")) = (n_key)
$lookup(S_entry.ENV, $ptascii("alias")) = (n_key)
$lookup(S_entry.ENV, $ptascii("got")) = (n_got)
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_key <- S_entry.REFCELLS /\ ~(n_text <- S_entry.REFCELLS)
S_entry.STORE[n_key] = DEFINED pstringread.READ.VALUE
S_entry.STORE[n_text] = DEFINED pstringread.READ.BASE
S_entry.STORE[n_got] = DEFINED (PINT 99)
$string_read_capture(S_entry, VARIABLE ($ptascii("key")) 5) = eps
$string_read_key_capture(S_entry, VARIABLE ($ptascii("key")) 5, pstringread.READ.BASE) = ((pstringread.READ.VALUE, pstringread.KEYCELL))
$heap_owners($heap_graph(S_entry), HCELL n_key) = 2
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_entry.STRINGDATA = eps /\ S_entry.EVENTS = eps
$string_read_source(S_entry, pstringread) /\ $string_read_ready(S_entry, pstringread)
''')
    if thrown:
        checks += lines(r'''
$lookup(S_entry.ENV, $ptascii("saved")) = (n_saved_cell)
S_entry.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_entry', 2 if thrown else 1, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
$lookup(S_after.ENV, $ptascii("key")) = (n_key)
$lookup(S_after.ENV, $ptascii("alias")) = (n_key)
S_after.STORE[n_key] = DEFINED (PINT 2)
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STORE[n_text] = S_entry.STORE[n_text]
n_key <- S_after.REFCELLS
$string_read_capture(S_after, VARIABLE ($ptascii("key")) 5) = eps
$string_read_key_current(S_after, pstringread) = (PINT 2)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$heap_owners($heap_graph(S_after), HCELL n_key) = 2
S_after.STRINGDATA = eps
S_after.EVENTS = [OUTPUT ($ptascii("2")), OUTPUT ($ptascii("|")), OUTPUT ($ptascii("String offset cast occurred")), OUTPUT ($ptascii("|")), OUTPUT ($ptascii("5")), OUTPUT ($ptascii(";"))]
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
''')
    if thrown:
        checks += lines(r'''
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
S_after.ERRORHANDLER.CALLBACK = eps
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_tail*][.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)][.ERRORFATALTRACE = eps]
S_raw.STORE[n_got] = DEFINED (PINT 99)
$throwable_previous_id(S_raw, n_saved) = eps
''')
    else:
        checks += lines(r'''
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))][.BASE = BASE_VALUE (KNOWN PNULL)]
''')
    checks += lines(r'''
$drive_steps(S_after, 0) = S_after[.COMPLETION = BUDGET]
S_one = $drive_steps(S_after, 1)
S_one.COMPLETION = BUDGET
S_one.STORE = S_raw.STORE /\ S_one.TODO = S_raw.TODO /\ S_one.EVENTS = S_raw.EVENTS
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_text] = S_entry.STORE[n_text] /\ S_done.STORE[n_key] = DEFINED (PINT 2)
S_done.CODE = S_entry.CODE /\ S_done.POOLS = S_entry.POOLS
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_after, 2000) = S_done
''')
    chunks = ('2', '|', 'String offset cast occurred', '|', '5', ';')
    chunks += ('1', '|', '1', '|', '99', '|', '2', '|', '2') if thrown else ('c', '|', '2', '|', '2')
    checks.append('S_done.EVENTS = [' + ', '.join('OUTPUT ($ptascii(' + json.dumps(x) + '))' for x in chunks) + ']')
    checks.append('S_done.STRINGDATA = [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = eps')
    if thrown:
        checks += lines(r'''
S_done.STORE[n_got] = DEFINED (PINT 99)
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    else:
        checks.append('S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))')
    reached = len(checks)
    if not thrown:
        checks += lines(r'''
$string_read_plan(S_entry[.REFCELLS = n_text :: S_entry.REFCELLS]) = (pstringread)
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("key"))]
$string_read_key_current(S_lost, pstringread) = eps
~$string_read_ready(S_lost, pstringread)
S_range = S_after[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]
$string_read_key_current(S_range, pstringread) = eps
~$string_read_ready(S_range, pstringread)
$string_read_key_current(S_range[.REFCELLS = eps], pstringread) = (PFLOAT 9218868437227405312)
$string_read_key_capture(S_entry, VARIABLE ($ptascii("key")) 5, PSTRING_CARRIER INTERNED_STRING ([97,0])) = eps
''')
    return checks, len(checks) - reached


def legacy_conditions(program, source):
    checks = initialize(program, source) + lines(r'''
$string_read_plan(S_entry) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 11
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abcd"))
pstringread.READ.VALUE = PFLOAT 4609434218613702656
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("s")) 11)
$lookup(S_entry.ENV, $ptascii("s")) = (n_s)
$lookup(S_entry.ENV, $ptascii("key")) = (n_key)
pstringread.BASECELL = (n_s) /\ pstringread.KEYCELL = (n_key)
~(n_s <- S_entry.REFCELLS) /\ ~(n_key <- S_entry.REFCELLS)
S_entry.STRINGDATA[0] = $ptascii("abcd")
S_marked_entry = S_entry[.REFCELLS = n_key :: S_entry.REFCELLS]
$string_read_plan(S_marked_entry) = (pstringread)
$string_read_capture(S_marked_entry, VARIABLE ($ptascii("key")) 11) = eps
$string_read_key_capture(S_marked_entry, VARIABLE ($ptascii("key")) 11, pstringread.READ.BASE) = ((pstringread.READ.VALUE, pstringread.KEYCELL))
$string_read_plan(S_entry[.REFCELLS = n_s :: S_entry.REFCELLS]) = (pstringread)
''') + seek('S_entry', 1, 'S_resume') + lines(r'''
S_resume.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S_resume.CURRENT = eps /\ S_resume.FRAMES = eps /\ S_resume.GLOBALTABLE = eps
S_resume.STORE[n_s] = DEFINED pstringread.READ.BASE
S_resume.STORE[n_key] = DEFINED (PFLOAT 13833706975393952563)
S_bad_key = S_resume[.REFCELLS = n_key :: S_resume.REFCELLS]
$heap_valid($heap_graph(S_bad_key)) /\ $call_descriptors_valid(S_bad_key)
$string_read_capture(S_bad_key, VARIABLE ($ptascii("key")) 11) = eps
$string_read_capture(S_bad_key, VARIABLE ($ptascii("s")) 11) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_source(S_bad_key, pstringread) /\ $string_read_ready(S_bad_key, pstringread)
$string_read_provider_ready(S_bad_key, pstringread)
$string_read_key_current(S_bad_key, pstringread) = (PFLOAT 13833706975393952563)
$heap_owners($heap_graph(S_bad_key), HCELL n_key) = 1
$heap_owners($heap_graph(S_bad_key), HCELL n_s) = 1
$task_nodes(STRING_READ_RESULT pstringread) = eps
PhpStep: S_bad_key ~> S_value
S_value = S_bad_key[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("d")))][.BASE = BASE_VALUE (KNOWN PNULL)]
$error_read_discard(S_bad_key, STRING_READ_RESULT pstringread) = S_bad_key[.ERRORFATALTRACE = eps]
$drive_steps(S_bad_key, 0) = S_bad_key[.COMPLETION = BUDGET]
S_one = $drive_steps(S_bad_key, 1)
S_one.COMPLETION = BUDGET
S_one.RESULT = S_value.RESULT /\ S_one.STORE = S_value.STORE /\ S_one.TODO = S_value.TODO
S_one.STRINGDATA = S_resume.STRINGDATA /\ S_one.EVENTS = S_resume.EVENTS
''')
    return checks, len(checks)


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
    legacy_bytes = legacy.CASES[LEGACY_SOURCE]
    assert hashlib.sha256(legacy_bytes).hexdigest() == LEGACY_HASH
    selected = {**cases.CASES, LEGACY_NAME: legacy_bytes}
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    legacy_path = out / 'legacy-request-source.php'
    legacy_path.write_bytes(legacy_bytes)
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()}) for name, source in selected.items()}
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
    fixtures, originals, selections = [], [legacy_path], []
    for index, (name, source_bytes) in enumerate(selected.items()):
        if name == LEGACY_NAME:
            source = legacy_path
            checks, derived = legacy_conditions(programs[name]['fixture'], source)
            scope = 'affected legacy REQUEST prefix: marked entry plan checked separately, unmarked callback prefix driven, historical late S_bad_key resume/discard checked; derived only, no native or production source gate'
        else:
            row = rows[name]
            native = row['native']
            assert row['passed'] and native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
            source = Path(native['argv'][-1])
            assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
            assert source.with_name('native.stdout').read_bytes() == OUTPUTS[index] and not source.with_name('native.stderr').read_bytes()
            checks, derived = source_conditions(programs[name]['fixture'], source, index == 1)
            originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
            scope = 'new source-reached interned aliased-key state fixture'
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'scope': scope, 'source_sha256': digest(source), 'conditions': len(checks),
            'derived_conditions': derived, 'raw_steps': sum(check.startswith('PhpStep:') for check in checks), 'source_credit': 0})
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
               Path(__file__), Path(cases.__file__), Path(legacy.__file__), report_path, *originals, *fixtures,
               *[ROOT / path for path in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
                 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
                 'tests/semantics/profile.json', 'tests/semantics/static_types.py',
                 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
                 'tests/semantics/string_offset_read_warning_protocol.py')]]
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
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': list(selected),
        'rows': selections, 'conditions': sum(row['conditions'] for row in selections),
        'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before,
        'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'native_reused_from': str(report_path), 'legacy_source_scope': 'maintained original bytes, first read only, no second TMP/bounds/tail or native/CLI source campaign',
        'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
