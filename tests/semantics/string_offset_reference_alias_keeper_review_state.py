#!/usr/bin/env python3
"""Independent same-cell alias retention and exact affected helper projections."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_reference_alias_keeper_cases as cases
import string_offset_reference_request_base_cases as requests
import string_offset_retained_carrier_cases as retained

ROOT = Path(__file__).resolve().parents[2]
ENTRIES = {
    'prior-request-alias-front': (requests.CASES['string-offset-reference-request-base-live-header'],
        'cfe99543af886933c79cfe587df52a109ccc0d1daeb84f063fa1063b38b97e43'),
    'prior-ordinary-same-cell-projection': (retained.CASES['string-offset-retained-request-carrier'],
        '368d6a8b53fa476925951796c1ff32089538af77ff347aaff0777ee74fef45b6'),
}
OUTPUTS = (b'2|String offset cast occurred|5;c|0|abc|2',
           b'2|String offset cast occurred|5;1|1|99|0|abc|2')
HELPERS = r'''
dec $alias_review_front(pstate, nat) : bool
def $alias_review_front(S, 0) = ($string_read_plan(S) =/= eps)
def $alias_review_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_CAST
def $alias_review_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.PHASE = STRING_CAST
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $alias_review_front(S, n) = false -- otherwise
dec $alias_review_seek(pstate, nat, nat) : pstate
def $alias_review_seek(S, n_stage, n) = S -- if $alias_review_front(S, n_stage)
def $alias_review_seek(S, n_stage, n) = S
  -- if ~$alias_review_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $alias_review_seek(S, n_stage, 0) = S
  -- if ~$alias_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $alias_review_seek(S, n_stage, n) = $alias_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$alias_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def seek(start, stage, result):
    return [f'{result}_found = $alias_review_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def initialize(program, source):
    return ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
            'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_entry')


def source_conditions(program, source, thrown):
    checks = initialize(program, source) + lines(r'''
$string_read_plan(S_entry) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 5
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pstringread.READ.VALUE = PFLOAT 4609434218613702656
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S_entry.ENV, $ptascii("text")) = (n_text)
$lookup(S_entry.ENV, $ptascii("base_alias")) = (n_text)
$lookup(S_entry.ENV, $ptascii("key")) = (n_key)
$lookup(S_entry.ENV, $ptascii("got")) = (n_got)
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_text <- S_entry.REFCELLS /\ ~(n_key <- S_entry.REFCELLS)
S_entry.STORE[n_text] = DEFINED pstringread.READ.BASE
S_entry.STORE[n_key] = DEFINED pstringread.READ.VALUE
S_entry.STORE[n_got] = DEFINED (PINT 99)
$string_read_capture(S_entry, S_entry.RESULT) = eps
$string_read_base_capture(S_entry, S_entry.RESULT) = ((pstringread.READ.BASE, pstringread.BASECELL))
$heap_owners($heap_graph(S_entry), HCELL n_text) = 2
$heap_owners($heap_graph(S_entry), HCELL n_key) = 1
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_entry.STRINGDATA = [$ptascii("abc")] /\ S_entry.EVENTS = eps
''')
    if thrown:
        checks += lines(r'''
$lookup(S_entry.ENV, $ptascii("saved")) = (n_saved_cell)
S_entry.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_entry', 2 if thrown else 1, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
$lookup(S_after.ENV, $ptascii("text")) = eps
$lookup(S_after.ENV, $ptascii("base_alias")) = (n_text)
S_after.STORE[n_text] = DEFINED pstringread.READ.BASE
S_after.STORE[n_key] = DEFINED (PINT 2)
S_after.STORE[n_got] = DEFINED (PINT 99)
n_text <- S_after.REFCELLS
$string_read_capture(S_after, VARIABLE ($ptascii("text")) 5) = eps
$string_read_base_capture(S_after, VARIABLE ($ptascii("text")) 5) = eps
$string_read_capture(S_after, VARIABLE ($ptascii("base_alias")) 5) = eps
$string_read_base_capture(S_after, VARIABLE ($ptascii("base_alias")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_retainer(S_after, pstringread, BIND ($ptascii("base_alias")) n_text)
$string_read_retained(S_after, pstringread, S_after.ENV)
$string_read_provider_ready(S_after, pstringread)
$string_read_key_current(S_after, pstringread) = (PINT 2)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$heap_owners($heap_graph(S_after), HCELL n_text) = 1
(HCELL n_text) <- $heap_prune($heap_graph(S_after)).NODES
S_after.STRINGDATA = S_entry.STRINGDATA
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
$lookup(S_done.ENV, $ptascii("text")) = eps
$lookup(S_done.ENV, $ptascii("base_alias")) = (n_text)
S_done.STORE[n_text] = S_after.STORE[n_text] /\ S_done.STORE[n_key] = DEFINED (PINT 2)
S_done.CODE = S_entry.CODE /\ S_done.POOLS = S_entry.POOLS
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_after, 2000) = S_done
''')
    chunks = ('2', '|', 'String offset cast occurred', '|', '5', ';')
    chunks += ('1', '|', '1', '|', '99', '|', '0', '|', 'abc', '|', '2') if thrown else ('c', '|', '0', '|', 'abc', '|', '2')
    checks.append('S_done.EVENTS = [' + ', '.join('OUTPUT ($ptascii(' + json.dumps(x) + '))' for x in chunks) + ']')
    checks.append('S_done.STRINGDATA = S_entry.STRINGDATA ++ [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = S_entry.STRINGDATA')
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
$lookup(S_after.ENV, $ptascii("right")) = (n_right)
$lookup(S_after.ENV, $ptascii("left")) = (n_left)
n_left =/= n_text /\ n_right =/= n_text
S_shadow = S_after[.ENV = (BIND ($ptascii("base_alias")) n_right) :: S_after.ENV]
$lookup(S_shadow.ENV, $ptascii("base_alias")) = (n_right)
~$string_read_retainer(S_shadow, pstringread, BIND ($ptascii("base_alias")) n_text)
~$string_read_retained(S_shadow, pstringread, S_shadow.ENV)
~$string_read_provider_ready(S_shadow, pstringread)
S_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_text] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))]
$string_carrier_valid(S_equal, PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))
~$string_read_retained(S_equal, pstringread, S_equal.ENV)
~$string_read_provider_ready(S_equal, pstringread)
S_dead = S_after[.ENV = $unbind(S_after.ENV, $ptascii("base_alias"))]
S_dead.STORE[n_text] = DEFINED pstringread.READ.BASE
~((HCELL n_text) <- $heap_prune($heap_graph(S_dead)).NODES)
$string_read_base_capture(S_dead, VARIABLE ($ptascii("base_alias")) 5) = eps
~$string_read_retained(S_dead, pstringread, S_dead.ENV)
~$string_read_provider_ready(S_dead, pstringread)
$string_read_source(S_dead, pstringread)
$string_read_resume(S_dead, pstringread) = S_dead[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$error_read_discard(S_dead, STRING_READ_RESULT pstringread) = S_dead[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_other = S_dead[.STORE[n_left] = DEFINED pstringread.READ.BASE][.REFCELLS = n_left :: S_dead.REFCELLS]
n_other_cell? = (n_left)
$string_read_base_capture(S_other, VARIABLE ($ptascii("left")) 5) = ((pstringread.READ.BASE, n_other_cell?))
~$string_read_retainer(S_other, pstringread, BIND ($ptascii("left")) n_left)
~$string_read_provider_ready(S_other, pstringread)
S_original = S_dead[.ENV = (BIND ($ptascii("text")) n_text) :: S_dead.ENV]
$string_read_base_capture(S_original, VARIABLE ($ptascii("text")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
~$string_read_retained(S_original, pstringread, S_original.ENV)
$string_read_provider_ready(S_original, pstringread)
''')
    return checks, len(checks) - reached


def entry_conditions(name, program, source):
    checks = initialize(program, source) + lines(r'''
$string_read_plan(S_entry) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 5
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
$lookup(S_entry.ENV, $ptascii("text")) = (n_text)
pstringread.BASECELL = (n_text)
''') + seek('S_entry', 1, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
$lookup(S_after.ENV, $ptascii("text")) = (n_text)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
''')
    if name == 'prior-request-alias-front':
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("base_alias")) = (n_text)
n_text <- S_after.REFCELLS
S_after.STORE[n_text] = DEFINED pstringread.READ.BASE
$heap_owners($heap_graph(S_after), HCELL n_text) = 2
$string_read_capture(S_after, VARIABLE ($ptascii("base_alias")) 5) = eps
$string_read_base_capture(S_after, VARIABLE ($ptascii("text")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_retainer(S_after, pstringread, BIND ($ptascii("base_alias")) n_text)
$string_read_retained(S_after, pstringread, S_after.ENV)
$string_read_provider_ready(S_after, pstringread)
''')
    else:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("keeper")) = (n_keeper)
n_keeper =/= n_text
~(n_text <- S_after.REFCELLS)
S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_after.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("keeper"))]
~$string_read_provider_ready(S_lost, pstringread)
S_same = S_lost[.STORE[n_text] = DEFINED pstringread.READ.BASE][.ENV = (BIND ($ptascii("keeper")) n_text) :: S_lost.ENV]
$lookup(S_same.ENV, $ptascii("keeper")) = (n_text)
$string_read_capture(S_same, VARIABLE ($ptascii("keeper")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_retainer(S_same, pstringread, BIND ($ptascii("keeper")) n_text)
$string_read_retained(S_same, pstringread, S_same.ENV)
$string_read_base_capture(S_same, VARIABLE ($ptascii("text")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_provider_ready(S_same, pstringread)
''')
    return checks


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
    for source, expected_hash in ENTRIES.values():
        assert hashlib.sha256(source).hexdigest() == expected_hash
    selected = {**cases.CASES, **{name: row[0] for name, row in ENTRIES.items()}}
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
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
    fixtures, originals, selections = [], [], []
    for index, (name, source_bytes) in enumerate(cases.CASES.items()):
        row = rows[name]
        native = row['native']
        assert row['passed'] and native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert source.with_name('native.stdout').read_bytes() == OUTPUTS[index] and not source.with_name('native.stderr').read_bytes()
        checks, derived = source_conditions(programs[name]['fixture'], source, index == 1)
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived,
            'raw_steps': sum(check.startswith('PhpStep:') for check in checks), 'source_credit': 0})
        originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    entry_text, entry_rows = HELPERS, []
    for index, (name, row) in enumerate(ENTRIES.items()):
        source = out / (name + '.php')
        source.write_bytes(row[0])
        originals.append(source)
        checks = entry_conditions(name, programs[name]['fixture'], source)
        entry_text += f'\ndec $alias_affected_{index}() : bool\ndef $alias_affected_{index}() = true\n'
        entry_text += ''.join('  -- if ' + check + '\n' for check in checks)
        entry_rows.append({'id': name, 'conditions': len(checks), 'source_sha256': digest(source)})
    fixture = out / 'affected-alias-keeper-projections.watsup'
    fixture.write_text(entry_text + '\ndec $main() : bool\ndef $main() = ($alias_affected_0() /\\ $alias_affected_1())\n')
    fixtures.append(fixture)
    selections.append({'id': 'affected-alias-keeper-projections', 'scope': 'two maintained normal-source prefixes through the first restored caller; all projection conditions derived, no old tails/native/source campaign',
        'conditions': sum(row['conditions'] for row in entry_rows), 'derived_conditions': sum(row['conditions'] for row in entry_rows),
        'entries': entry_rows, 'raw_steps': 0, 'source_credit': 0})
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
               Path(__file__), Path(cases.__file__), Path(requests.__file__), Path(retained.__file__), report_path, *originals, *fixtures,
               *[ROOT / path for path in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
                 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
                 'tests/semantics/profile.json', 'tests/semantics/static_types.py',
                 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
                 'tests/semantics/string_offset_reference_request_base_protocol.py', 'tests/semantics/string_offset_retained_carrier_protocol.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if (path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php'))] == [digest(ROOT / '.tools/php/bin/php')]
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
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': [row['id'] for row in selections],
        'rows': selections, 'conditions': sum(row['conditions'] for row in selections),
        'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before,
        'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
